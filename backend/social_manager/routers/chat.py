"""
Chat router — supports Ask mode (Q&A only) and Agent mode (can post to platforms).
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel
from typing import List, Dict, Optional
from social_manager.routers.users import get_current_user
from social_manager.db import (
    SessionLocal,
    SocialConnectionRepository,
    Post,
    PublishingJob,
    SocialStrategyLogRepository,
    ChatSession,
    ChatMessage as DBChatMessage,
    ChatSessionRepository,
)
from social_manager.platforms.hub import get_user_platform_hub
from social_manager.approvals import policy_engine, approval_workflow
from social_manager.routers.publishing import execute_publishing_job
from social_manager.knowledge_base import KnowledgeBaseManager
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
    model: Optional[str] = None
    session_id: Optional[int] = None


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


async def call_llm(
    system_prompt: str,
    user_message: str,
    history: List[ChatMessage],
    model: str = "marko-2.0-mini",
    groq_key: Optional[str] = None,
    openai_key: Optional[str] = None
) -> Optional[str]:
    """Call LLM (Groq or OpenAI) based on keys and model selection."""
    is_openai = (model == "gpt-4o-mini" or (openai_key and not groq_key))
    
    if is_openai:
        api_key = openai_key or os.getenv("OPENAI_API_KEY")
        if not api_key or any(k in api_key.lower() for k in ["your_key", "your_openai", "your-openai", "sk-proj-your"]):
            api_key = None
        
        if not api_key:
            logger.warning("OpenAI API key not provided or placeholder. Cannot call OpenAI.")
            return None
            
        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-6:]:
            api_role = "assistant" if h.role in ("assistant", "agent") else "user"
            messages.append({"role": api_role, "content": h.content})
        messages.append({"role": "user", "content": user_message})
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 600
                    },
                    timeout=20.0
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
        return None
        
    else:
        # Default/fallback to Groq
        api_key = groq_key or os.getenv("GROQ_API_KEY")
        if not api_key or any(k in api_key.lower() for k in ["your_key", "your_groq", "your-groq", "gsk_your"]):
            api_key = None
            
        if not api_key:
            logger.warning("Groq API key not provided or placeholder. Cannot call Groq.")
            return None
            
        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-6:]:
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


async def call_groq_llm(system_prompt: str, user_message: str, history: List[ChatMessage]) -> Optional[str]:
    """Compatibility wrapper for call_groq_llm."""
    return await call_llm(system_prompt, user_message, history)


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


@router.get("/sessions")
async def list_chat_sessions(
    current_user=Depends(get_current_user)
):
    db = SessionLocal()
    try:
        repo = ChatSessionRepository(db)
        sessions = repo.list_sessions(user_id=current_user.id)
        return [
            {
                "id": s.id,
                "title": s.title,
                "mode": s.mode,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None
            }
            for s in sessions
        ]
    finally:
        db.close()


@router.get("/sessions/{session_id}")
async def get_chat_session(
    session_id: int,
    current_user=Depends(get_current_user)
):
    db = SessionLocal()
    try:
        repo = ChatSessionRepository(db)
        session = repo.get_session_with_messages(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Chat session not found")
            
        return {
            "id": session.id,
            "title": session.title,
            "mode": session.mode,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "published": m.published,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                }
                for m in session.messages
            ]
        }
    finally:
        db.close()


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user=Depends(get_current_user)
):
    db = SessionLocal()
    try:
        repo = ChatSessionRepository(db)
        session = repo.get_session_with_messages(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        repo.delete(session_id)
        return {"success": True}
    finally:
        db.close()


@router.post("/interact")
async def chat_interact(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    x_groq_api_key: Optional[str] = Header(None, alias="X-Groq-Api-Key"),
    x_openai_api_key: Optional[str] = Header(None, alias="X-OpenAI-Api-Key"),
):
    """
    Chat endpoint:
    - Ask mode: Q&A with social media AI expert, leveraging Knowledge Base.
    - Agent mode: Drafts content with LLM, returns as draft (does not auto-publish) for Dashboard auto-fill.
    """
    db = SessionLocal()
    try:
        repo = ChatSessionRepository(db)
        
        # 1. Fetch or create ChatSession
        if req.session_id is not None:
            session = repo.get_session_with_messages(req.session_id)
            if not session or session.user_id != current_user.id:
                raise HTTPException(status_code=404, detail="Chat session not found")
        else:
            session = repo.create(
                user_id=current_user.id,
                title=req.message[:60] if req.message else "New Chat",
                mode=req.mode
            )
            
        # 2. Save User Message
        user_msg = DBChatMessage(
            session_id=session.id,
            role="user",
            content=req.message
        )
        db.add(user_msg)
        db.commit()
        db.refresh(session)
        
        # Build history helper from DB session messages (excluding the last one we just added)
        history_list = [
            ChatMessage(role=m.role, content=m.content)
            for m in session.messages[:-1]
        ]

        if req.mode == "ask":
            # Build context from Knowledge Base
            kb_manager = KnowledgeBaseManager(db)
            kb_context = kb_manager.build_context_for_llm(max_chars=4000)
            
            system_prompt = ASK_SYSTEM_PROMPT
            if kb_context and "[No documents" not in kb_context:
                system_prompt = f"{ASK_SYSTEM_PROMPT}\n\nUse the following knowledge base context to answer the user's question if relevant:\n{kb_context}"
                
            content = await call_llm(
                system_prompt=system_prompt,
                user_message=req.message,
                history=history_list,
                model=req.model or "marko-2.0-mini",
                groq_key=x_groq_api_key,
                openai_key=x_openai_api_key
            )
            
            if not content:
                content = (
                    f"I'm your social media assistant! You asked: '{req.message}'\n\n"
                    "I can help you with:\n"
                    "• Content strategy and ideas\n"
                    "• Platform best practices\n"
                    "• Audience insights\n"
                    "• Post timing recommendations\n\n"
                    "(Note: AI service is currently unavailable — please check your API keys)"
                )
                
            # Save Assistant Message
            assistant_msg = DBChatMessage(
                session_id=session.id,
                role="assistant",
                content=content
            )
            db.add(assistant_msg)
            db.commit()
            
            return {
                "session_id": session.id,
                "mode": "ask",
                "response": content,
                "published": []
            }

        elif req.mode == "agent":
            # Agent mode — draft content for the platforms
            target_platform = req.platforms[0] if req.platforms else "social media"
            system_prompt = AGENT_SYSTEM_PROMPTS.get(
                target_platform.lower(),
                "You are a social media expert. Draft a post based on the user's request. Output ONLY the post text."
            )
            
            content = await call_llm(
                system_prompt=system_prompt,
                user_message=req.message,
                history=history_list,
                model=req.model or "marko-2.0-mini",
                groq_key=x_groq_api_key,
                openai_key=x_openai_api_key
            )
            
            if not content:
                content = req.message
                
            platforms_str = ", ".join([p.capitalize() for p in req.platforms]) if req.platforms else "social media"
            response_msg = f"I've prepared your post for {platforms_str} — review it in the Dashboard and click Publish when ready:\n\n{content}"
            
            # Save Assistant Message
            assistant_msg = DBChatMessage(
                session_id=session.id,
                role="assistant",
                content=response_msg
            )
            db.add(assistant_msg)
            db.commit()
            
            return {
                "session_id": session.id,
                "mode": "agent",
                "response": response_msg,
                "draft_content": content,
                "platforms": req.platforms,
                "published": []
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Use 'ask' or 'agent'.")
    finally:
        db.close()
