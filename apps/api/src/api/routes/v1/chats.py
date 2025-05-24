from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from api.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from api.services.retriever import DocumentRetriever
from api.services.llm_service import LLMService
from api.services.auth import AuthService
from api.services.auth import get_current_user
import time

router = APIRouter()
retriever = DocumentRetriever()
llm_service = LLMService()
auth_service = AuthService()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    data: ChatSessionCreate,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Create a new chat session"""
    tenant_id = request.state.tenant_id

    # Get the agent with project info
    agent = await request.state.prisma.agent.find_unique(
        where={"id": data.agent_id}, include={"project": True}
    )

    if not agent or agent.deleted_at:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": agent.project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        },
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create the chat session
    current_time = int(time.time())
    session = await request.state.prisma.chat_session.create(
        {
            "data": {
                "user_id": current_user.id,
                "agent_id": data.agent_id,
                "title": data.title or "New chat",
                "created_at": current_time,
                "updated_at": current_time,
                "created_by": current_user.id,
                "updated_by": current_user.id,
            }
        }
    )

    return session


@router.get("/sessions/{agent_id}", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    agent_id: str,
    current_user=Depends(get_current_user),
    request: Request = None,  # noqa: F821
):
    """Get all chat sessions for an agent"""
    tenant_id = request.state.tenant_id

    # Get the agent with project info
    agent = await request.state.prisma.agent.find_unique(
        where={"id": agent_id}, include={"project": True}
    )

    if not agent or agent.deleted_at:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": agent.project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        },
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get all chat sessions for the agent and user
    sessions = await request.state.prisma.chat_session.find_many(
        where={
            "agent_id": agent_id,
            "user_id": current_user.id,
            "deleted_at": None,
        },
        order_by={"created_at": "desc"},
    )

    return sessions


@router.get("/messages/{session_id}", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: str,
    current_user=Depends(get_current_user),
    request: Request = None,  # noqa: F821
):
    """Get all messages for a chat session"""
    tenant_id = request.state.tenant_id

    # Get the chat session with agent and project info
    session = await request.state.prisma.chat_session.find_unique(
        where={
            "id": session_id,
        },
        include={"agent": {"include": {"project": True}}},
    )

    if not session or session.deleted_at:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Check if user owns the session
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": session.agent.project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        },
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get all messages for the chat session
    messages = await request.state.prisma.chat_message.find_many(
        where={"chat_session_id": session_id, "deleted_at": None},
        order_by={"created_at": "asc"},
    )

    return messages


@router.post("/messages/{session_id}", response_model=ChatMessageResponse)
async def create_chat_message(
    session_id: str,
    data: ChatMessageCreate,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Create a new chat message"""
    tenant_id = request.state.tenant_id

    # Get the chat session with agent and project info
    session = await request.state.prisma.chat_session.find_unique(
        where={
            "id": session_id,
        },
        include={"agent": {"include": {"project": True}}},
    )

    if not session or session.deleted_at:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Check if user owns the session
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": session.agent.project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        },
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create the message
    current_time = int(time.time())
    message = await request.state.prisma.chat_message.create(
        {
            "data": {
                "chat_session_id": session_id,
                "role": "user",
                "content": data.content,
                "created_at": current_time,
                "updated_at": current_time,
                "created_by": current_user.id,
                "updated_by": current_user.id,
            }
        }
    )

    return message


@router.post("/completion", response_model=ChatCompletionResponse)
async def chat_completion(
    data: ChatCompletionRequest,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Get a chat completion"""
    tenant_id = request.state.tenant_id

    # Get the chat session with agent and project info
    session = await request.state.prisma.chat_session.find_unique(
        where={"id": data.chat_session_id},
        include={"agent": {"include": {"project": True}}},
    )

    if not session or session.deleted_at:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Check if user owns the session
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": session.agent.project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        },
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get conversation history
    chat_messages = await request.state.prisma.chat_message.find_many(
        where={"chat_session_id": data.chat_session_id, "deleted_at": None},
        order_by={"created_at": "asc"},
        take=10,  # Limit to last 10 messages
    )

    # Format conversation history for the LLM
    conversation_history = [
        {"role": msg.role, "content": msg.content} for msg in chat_messages
    ]

    # Retrieve relevant document chunks
    context_chunks = await retriever.retrieve(
        query=data.message, project_id=project.id, top_k=5
    )

    # Generate response using LLM
    llm_response = await llm_service.generate_response(
        query=data.message,
        context_chunks=context_chunks,
        conversation_history=conversation_history,
    )

    # Create the assistant message
    current_time = int(time.time())
    assistant_message = await request.state.prisma.chat_message.create(
        {
            "data": {
                "chat_session_id": data.chat_session_id,
                "role": "assistant",
                "content": llm_response["answer"],
                "created_at": current_time,
                "updated_at": current_time,
                "created_by": current_user.id,
                "updated_by": current_user.id,
            }
        }
    )

    # Update session timestamp
    await request.state.prisma.chat_session.update(
        where={"id": data.chat_session_id},
        data={"updated_at": current_time, "updated_by": current_user.id},
    )

    # Return the response with sources
    return {"message": assistant_message, "sources": llm_response["sources"]}
