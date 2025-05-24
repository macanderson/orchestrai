from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from api.schemas.agent import AgentCreate, AgentResponse
from api.services.auth import get_current_user
import time

router = APIRouter()


@router.post("/", response_model=AgentResponse)
async def create_agent(
    data: AgentCreate,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Create a new chat agent"""
    tenant_id = request.state.tenant_id

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": data.project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        },
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create the agent
    current_time = int(time.time())
    agent = await request.state.prisma.agent.create(
        {
            "data": {
                "name": data.name,
                "description": data.description,
                "project_id": data.project_id,
                "prompt_template": data.prompt_template,
                "created_at": current_time,
                "updated_at": current_time,
                "created_by": current_user.id,
                "updated_by": current_user.id,
            }
        }
    )

    return agent


@router.get("/{project_id}", response_model=List[AgentResponse])
async def get_agents(
    project_id: str,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Get all agents for a project"""
    tenant_id = request.state.tenant_id

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={"id": project_id, "tenant_id": tenant_id, "deleted_at": None},
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get all agents for the project
    agents = await request.state.prisma.agent.find_many(
        where={"project_id": project_id, "deleted_at": None},
        order_by={"created_at": "desc"},
    )

    return agents


@router.get("/detail/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Get a specific agent"""
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

    return agent
