import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
from api.core.auth import create_access_token, get_current_user
from api.core.config import settings
from supabase import create_client, Client
import time

logger = logging.getLogger(__name__)
router = APIRouter()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", response_model=Token)
async def register(data: UserCreate, request: Request):
    """Register a new user"""
    tenant_id = request.headers.get("X-Tenant-Id")

    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-Id header is required",
        )

    # Check if tenant exists
    tenant = await request.state.prisma.tenant.find_unique(
        where={
            "id": tenant_id,
        },
    )

    if not tenant or tenant.deleted_at:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Check if user already exists
    existing_user = await request.state.prisma.user.find_first(
        where={"email": data.email, "tenant_id": tenant_id}
    )

    if existing_user and not existing_user.deleted_at:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        # Create user in Supabase
        supabase_response = supabase.auth.sign_up(
            {"email": data.email, "password": data.password}
        )

        supabase_user = supabase_response.user

        # Create user in our database
        current_time = int(time.time())
        user = await request.state.prisma.user.create(
            {
                "data": {
                    "id": supabase_user.id,
                    "email": data.email,
                    "name": data.name,
                    "tenant_id": tenant_id,
                    "created_at": current_time,
                    "updated_at": current_time,
                }
            }
        )

        # Generate access token
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None
):
    """Login a user"""
    tenant_id = request.headers.get("X-Tenant-Id")

    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-Id header is required",
        )

    try:
        # Login with Supabase
        supabase_response = supabase.auth.sign_in_with_password(
            {"email": form_data.username, "password": form_data.password}
        )

        supabase_user = supabase_response.user

        # Find user in our database
        user = await request.state.prisma.user.find_first(
            where={
                "id": supabase_user.id,
                "tenant_id": tenant_id,
                "deleted_at": None,
            },
        )

        if not user:
            raise HTTPException(
                status_code=404, detail="User not found for this tenant"  # noqa: E501
            )

        # Generate access token
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )


@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    """Logout a user"""
    try:
        # We don't need to invalidate JWT tokens since they're stateless
        # Instead, implement token refreshing and a blacklist
        # in a production system
        return {"message": "Successfully logged out"}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Logout failed: {str(e)}",
        )


@router.post("/reset-password")
async def reset_password(email: EmailStr):
    """Request password reset"""
    try:
        # Send password reset email with Supabase
        supabase.auth.reset_password_email(email)
        return {"message": "Password reset email sent"}

    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        # For security reasons, always return the same message
        return {"message": "Password reset email sent if user exists"}


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "tenant_id": current_user.tenant_id,
    }
