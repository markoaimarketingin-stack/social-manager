"""
Chat router — supports Ask mode (Q&A only) and Agent mode (can post to platforms).
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
from social_manager.routers.users import get_current_user
from social_manager.db import SessionLocal, SocialConnectionRepository, Post, PublishingJob, SocialStrategyLogRepository
from social_manager.platforms.hub import get_user_platform_hub
from social_manager.approvals import policy_engine, approval_workflow
from social_manager.routers.publishing import execute_publishing_job
import os
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Agent Chat"])


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    agent_name: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    mode: str = "ask"  # 'ask' or 'agent'
    platforms: Optional[List[str]] = []  # platforms to post to in agent mode


ASK_SYSTEM_PROMPT = """You are a helpful social media expert assistant for Social Manager app.
You help users with social media strategy, content ideas, analytics insights, and best practices.
You can answer questions about their brand, audience, and platform strategies.
You are knowledgeable, concise, and actionable.
NEVER claim you posted anything — you are in Ask/Q&A mode only."""

AGENT_SYSTEM_PROMPTS = {
    "linkedin": """You are a LinkedIn content creator agent. Draft a professional LinkedIn post based on the user's request.
Be concise, insightful, and professional. Include 2-3 relevant hashtags.
Output ONLY the post text, nothing else — no preamble, no explanation.""",
    "instagram": """You are an Instagram content creator agent. Draft an engaging Instagram caption based on the user's request.
Be creative, visual-forward, and engaging. Include 5-8 relevant hashtags.
Output ONLY the caption text with hashtags, nothing else.""",
    "facebook": """You are a Facebook content creator agent. Draft an engaging Facebook post based on the user's request.
Be conversational and community-focused. Include 2-3 hashtags.
Output ONLY the post text, nothing else.""",
    "x": """You are an X (Twitter) content creator agent. Draft a punchy tweet based on the user's request.
Be concise, direct, and engaging. Max 280 characters. Include 1-2 hashtags.
Output ONLY the tweet text, nothing else."""
}


async def call_groq_llm(system_prompt: str, user_message: str, history: List[ChatMessage]) -> Optional[str]:
    """Call Groq API for LLM responses."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("gsk_your"):
        return None

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-6:]:  # keep last 6 messages for context
        api_role = "assistant" if h.role in ("assistant", "agent") else "user"
        messages.append({"role": api_role, "content": h.content})
    messages.append({"role": "user", "content": user_message})

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 600
                },
                timeout=20.0
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Groq request failed: {e}")
    return None


async def publish_post_for_user(user_id: int, content: str, platform: str, db_session):
    """Create and immediately publish a post for the user on the specified platform."""
    try:
        # Create Post record
        post = Post(
            user_id=user_id,
            content=content,
            platform=platform,
            status="pending"
        )
        db_session.add(post)
        db_session.flush()

        # Create PublishingJob
        job = PublishingJob(
            post_id=post.id,
            platform=platform,
            status="pending"
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        db_session.refresh(post)

        # Execute publishing
        job.status = "processing"
        db_session.commit()

        user_hub = get_user_platform_hub(user_id, db_session)
        prepared = await user_hub.prepare_post_for_platform(
            platform=platform,
            content=content,
            assets=[]
        )
        result = await user_hub.publish_to_platform(
            platform=platform,
            prepared_post=prepared
        )

        job.status = "published"
        job.platform_post_id = str(result.get("id", ""))
        db_session.commit()
        return {"success": True, "job_id": job.id, "post_id": post.id, "platform_post_id": job.platform_post_id}

    except Exception as e:
        logger.error(f"Publishing failed for user {user_id} on {platform}: {e}")
        if 'job' in locals():
            job.status = "failed"
            job.error_message = str(e)
            db_session.commit()
        return {"success": False, "error": str(e)}


@router.post("/interact")
async def chat_interact(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    """
    Chat endpoint:
    - Ask mode: Q&A with social media AI expert
    - Agent mode: Drafts content with LLM then posts to selected platforms
    """
    if req.mode == "ask":
        # Q&A mode — just answer, never post
        content = await call_groq_llm(ASK_SYSTEM_PROMPT, req.message, req.history or [])
        if not content:
            content = (
                f"I'm your social media assistant! You asked: '{req.message}'\n\n"
                "I can help you with:\n"
                "• Content strategy and ideas\n"
                "• Platform best practices\n"
                "• Audience insights\n"
                "• Post timing recommendations\n\n"
                "(Note: AI service is currently unavailable — please check your GROQ_API_KEY)"
            )
        return {
            "mode": "ask",
            "response": content,
            "published": []
        }

    elif req.mode == "agent":
        # Agent mode — draft content and post to platforms
        if not req.platforms:
            return {
                "mode": "agent",
                "response": "Please select at least one platform to post to.",
                "published": []
            }

        db = SessionLocal()
        try:
            # Check user has connections for requested platforms
            conn_repo = SocialConnectionRepository(db)
            published_results = []
            errors = []
            status_lines = []

            for platform in req.platforms:
                conn = conn_repo.get_user_connection(current_user.id, platform)
                if not conn:
                    errors.append(f"{platform}: Not connected. Please connect this platform first.")
                    continue

                # Generate platform-specific content
                system_prompt = AGENT_SYSTEM_PROMPTS.get(
                    platform.lower(),
                    "You are a social media expert. Draft a post based on the user's request. Output ONLY the post text."
                )
                content = await call_groq_llm(system_prompt, req.message, req.history or [])

                if not content:
                    # Fallback content
                    content = req.message

                # Run Compliance Policy Checks
                policy_res = policy_engine.check_content(content)
                has_warnings = any(v.severity == "warning" for v in policy_res["violations"])
                
                # Check risk (low-risk educational vs launch/pricing/claims)
                risk_keywords = ["launch", "price", "pricing", "sale", "cost", "dollar", "$", "buy", "discount", "offer", "guarantee", "risk-free"]
                content_lower = content.lower()
                is_low_risk = not any(kw in content_lower for kw in risk_keywords)
                
                if not policy_res["passed"]:
                    status = "draft"
                    approval_status = "rejected"
                elif has_warnings or not is_low_risk:
                    status = "draft"
                    approval_status = "pending"
                else:
                    status = "approved"
                    approval_status = "approved"

                # Create the Post record in DB
                post = Post(
                    user_id=current_user.id,
                    content=content,
                    platform=platform,
                    status=status,
                    approval_status=approval_status
                )
                db.add(post)
                db.flush()

                # Audit logging
                strategy_log_repo = SocialStrategyLogRepository(db)
                strategy_log_repo.log_event(
                    event="agent_compliance_check",
                    details=(
                        f"Post ID {post.id} drafted by agent for {platform}. "
                        f"Passed: {policy_res['passed']}. Low-Risk: {is_low_risk}. "
                        f"Status: {status}. Approval: {approval_status}."
                    )
                )

                # Process based on approval status
                if approval_status == "rejected":
                    violations_str = ", ".join([v.details for v in policy_res["violations"]])
                    errors.append(f"{platform.capitalize()}: Blocked by compliance check - {violations_str}")
                    status_lines.append(f"❌ {platform.capitalize()}: Blocked by compliance check - {violations_str}")
                    
                elif approval_status == "pending":
                    # Register in approval workflow
                    approval_workflow.submit_for_approval(
                        post_id=post.id,
                        content=content,
                        creator_id=str(current_user.id),
                        required_approvers=["manager"]
                    )
                    
                    # Create the pending PublishingJob
                    job = PublishingJob(
                        post_id=post.id,
                        platform=platform,
                        status="pending"
                    )
                    db.add(job)
                    db.flush()
                    
                    reason_str = "flagged content" if has_warnings else "product launch/pricing review required"
                    status_lines.append(f"⏳ {platform.capitalize()}: Sent to approval queue ({reason_str}).")
                    
                elif approval_status == "approved":
                    # Create PublishingJob
                    job = PublishingJob(
                        post_id=post.id,
                        platform=platform,
                        status="pending"
                    )
                    db.add(job)
                    db.flush()
                    
                    # Enqueue in background task
                    background_tasks.add_task(execute_publishing_job, job.id)
                    
                    published_results.append({
                        "platform": platform,
                        "content": content,
                        "job_id": job.id,
                        "post_id": post.id,
                        "platform_post_id": ""
                    })
                    status_lines.append(f"✅ {platform.capitalize()}: Passed policy and queued for publishing!")

            db.commit()

            # Build final response text
            response_msg = ""
            if status_lines:
                response_msg = "\n".join(status_lines)
            else:
                response_msg = "No posts could be created."
                if errors:
                    response_msg += "\n" + "\n".join([f"❌ {e}" for e in errors])

            return {
                "mode": "agent",
                "response": response_msg,
                "published": published_results
            }
        finally:
            db.close()

    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'ask' or 'agent'.")
