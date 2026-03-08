from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/api/v1/ai", tags=["ai-chat"])


def _is_ai_configured() -> bool:
    return bool(settings.ANTHROPIC_API_KEY) or bool(
        settings.ANTHROPIC_BASE_URL and settings.ANTHROPIC_AUTH_TOKEN
    )


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    conversation_history: list


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if not _is_ai_configured():
        raise HTTPException(
            status_code=503,
            detail="AI chat is not configured. Set ANTHROPIC_API_KEY (or ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN) in your .env file.",
        )

    from app.services.ai_service import chat_with_ai

    try:
        result = chat_with_ai(request.message, request.conversation_history, db)
        return result
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid API key or auth token.")
        if "rate" in error_msg.lower() and "limit" in error_msg.lower():
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again shortly.")
        raise HTTPException(status_code=500, detail="AI service error. Please try again.")


@router.get("/status")
def ai_status():
    """Check if AI chat is configured and available."""
    from app.services.ai_service import _get_model
    return {
        "configured": _is_ai_configured(),
        "model": _get_model(),
    }
