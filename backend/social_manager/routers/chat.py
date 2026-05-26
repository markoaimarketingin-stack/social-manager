from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from social_manager.routers.users import get_current_user
import os
import httpx # Use httpx for Groq API calls

router = APIRouter(prefix="/api/chat", tags=["Agent Chat"])

class ChatMessage(BaseModel):
    role: str # 'user' or 'agent'
    content: str
    agent_name: Optional[str] = None

class ChatRequest(BaseModel):
    # Support both old and new frontend formats
    message: Optional[str] = None
    history: Optional[List[ChatMessage]] = None
    active_platforms: Optional[List[str]] = None
    
    # New format support
    platform: Optional[str] = None
    messages: Optional[List[ChatMessage]] = None

AGENT_PROMPTS = {
    "facebook": "You are the Facebook Marketing Agent. Focus on community and long-form engagement. Draft a friendly, informative post.",
    "instagram": "You are the Instagram Creative Agent. Focus on aesthetics, storytelling, and hashtags. Draft a visual-first post.",
    "linkedin": "You are the LinkedIn Professional Agent. Focus on B2B networking and leadership. Draft a professional, structured post.",
    "x": "You are the X Real-time Agent. Focus on viral hooks and brevity. Draft a punchy update under 280 chars."
}

async def call_groq(system_prompt: str, user_message: str, history: List[ChatMessage]):
    """Helper to call Groq API as a fallback or primary for agents."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("gsk_your"):
        return None # Not configured
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-3:]:
        # Map internal 'agent' role to 'assistant' for LLM APIs
        api_role = "assistant" if h.role == "agent" else h.role
        messages.append({"role": api_role, "content": h.content})
    messages.append({"role": "user", "content": user_message})
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Groq API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Groq Request Exception: {e}")
    return None

@router.post("/interact")
async def chat_with_agents(
    req: ChatRequest,
    current_user = Depends(get_current_user)
):
    """
    Simulate a conversation between a user and multiple platform agents.
    Uses Groq as primary (faster/generous) and has a mock fallback.
    """
    agent_responses = []
    
    # Normalize inputs
    user_message = req.message or (req.messages[-1].content if req.messages else "")
    chat_history = req.history or (req.messages[:-1] if req.messages else [])
    platforms = req.active_platforms or ([req.platform] if req.platform else [])

    for platform in platforms:
        system_prompt = AGENT_PROMPTS.get(platform, "You are a social media assistant.")
        
        # 1. Try Groq (Primary for agents)
        content = await call_groq(system_prompt, user_message, chat_history)
        
        # 2. Fallback to Mock if LLM fails
        if not content:
            content = f"[MOCK DRAFT FOR {platform.upper()}]\n\nHello! I'm currently in offline mode due to API quota limits, but here is a sample draft based on your request: '{user_message}'\n\n#socialmedia #marketing #brand"

        agent_responses.append({
            "role": "agent",
            "agent_name": f"{platform.capitalize()} Agent",
            "platform": platform,
            "content": content
        })

    return {
        "status": "success",
        "responses": agent_responses
    }
