from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from api.schemas.project import ProjectCreate, ProjectResponse
from api.services.auth import AuthService
from api.services.auth import get_current_user
import time

router = APIRouter()

auth_service = AuthService()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    current_user=Depends(get_current_user),
    request: Request = None,  # noqa: E501
):
    """Create a new project"""
    tenant_id = request.state.tenant_id

    # Create the project
    current_time = int(time.time())
    project = await request.state.prisma.project.create(
        {
            "data": {
                "name": data.name,
                "description": data.description,
                "tenant_id": tenant_id,
                "created_at": current_time,
                "updated_at": current_time,
                "created_by": current_user.id,
                "updated_by": current_user.id,
                "users": {
                    "create": {
                        "user_id": current_user.id,
                        "role": "OWNER",
                        "created_at": current_time,
                        "updated_at": current_time,
                        "created_by": current_user.id,
                        "updated_by": current_user.id,
                    }
                },
            }
        }
    )

    return project


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    current_user=Depends(get_current_user), request: Request = None
):  # noqa: E501
    """Get all projects for the current tenant that the user has access to"""
    tenant_id = request.state.tenant_id

    # Get all projects for the tenant where the user is a member
    projects = await request.state.prisma.project.find_many(
        where={
            "tenant_id": tenant_id,
            "deleted_at": None,
            "users": {
                "some": {"user_id": current_user.id, "deleted_at": None}
            },  # noqa: E501
        },
        order_by={"created_at": "desc"},
    )

    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user=Depends(get_current_user),
    request: Request = None,  # noqa: E501
):
    """Get a specific project"""
    tenant_id = request.state.tenant_id

    # Get the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
            "users": {
                "some": {"user_id": current_user.id, "deleted_at": None}
            },  # noqa: E501
        }
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project
