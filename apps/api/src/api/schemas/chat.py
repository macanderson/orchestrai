from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatSessionCreate(BaseModel):
    agent_id: str
    title: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: str
    agent_id: str
    title: Optional[str] = None
    created_at: int
    updated_at: int


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: str
    chat_session_id: str
    role: str
    content: str
    created_at: int


class ChatCompletionRequest(BaseModel):
    chat_session_id: str
    message: str


class ChatCompletionResponse(BaseModel):
    message: ChatMessageResponse
    sources: List[Dict[str, Any]] = []
