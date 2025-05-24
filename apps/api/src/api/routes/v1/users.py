from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from api.schemas.auth import UserResponse
from api.services.auth import AuthService
from api.services.auth import get_current_user
import time

router = APIRouter()
auth_service = AuthService()


@router.post("/", response_model=UserResponse)
async def create_user(
    data,
    current_user=Depends(get_current_user),
    request: Request = None,  # noqa: E501
):
    """Create a new User"""
    tenant_id = request.state.tenant_id

    # Create the User
    current_time = int(time.time())
    user = await request.state.prisma.User.create(
        {
            "data": {
                "email": data.email,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "password": data.password,
                "role_id": data.role_id if hasattr(data, 'role_id') else None,
                "tenant_id": tenant_id,
                "created_at": current_time,
                "updated_at": current_time,
                "created_by": current_user.id,
                "updated_by": current_user.id,
            }
        }
    )

    return user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    current_user=Depends(get_current_user), request: Request = None
):  # noqa: E501
    """Get all users for the current tenant that the user has access to"""
    tenant_id = request.state.tenant_id

    # Get all users for the tenant where the user is a member
    users = await request.state.prisma.User.find_many(
        where={
            "tenant_id": tenant_id,
            "deleted_at": None,
            "users": {
                "some": {"user_id": current_user.id, "deleted_at": None}
            },  # noqa: E501
        },
        order_by={"created_at": "desc"},
    )

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user=Depends(get_current_user),
    request: Request = None,  # noqa: E501
):
    """Get a specific User"""
    tenant_id = request.state.tenant_id

    # Get the User
    user = await request.state.prisma.User.find_first(
        where={
            "id": user_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
            "users": {
                "some": {"user_id": current_user.id, "deleted_at": None}
            },  # noqa: E501
        }
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
