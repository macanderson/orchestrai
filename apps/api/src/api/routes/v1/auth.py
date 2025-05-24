import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from api.services.auth import AuthService, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize auth service
auth_service = AuthService()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    reset_token: str
    new_password: str


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tenant_id: str


@router.post("/register", response_model=Token)
async def register(data: UserRegister, request: Request):
    """Register a new user"""
    tenant_id = request.headers.get("X-Tenant-Id")

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required"
        )

    # Connect Prisma
    await auth_service.prisma.connect()

    try:
        # Check if tenant exists
        tenant = await auth_service.prisma.tenant.find_unique(
            where={"id": tenant_id}
        )

        if not tenant or tenant.deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        # Get default role for new users (optional)
        default_role = await auth_service.prisma.userrole.find_first(
            where={"type": "CUSTOMER_USER"}
        )

        # Register user
        result = await auth_service.register_user(
            email=data.email,
            password=data.password,
            tenant_id=tenant_id,
            first_name=data.first_name,
            last_name=data.last_name,
            role_id=default_role.id if default_role else None
        )

        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    finally:
        await auth_service.prisma.disconnect()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    """Login a user"""
    tenant_id = request.headers.get("X-Tenant-Id")

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required"
        )

    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")

    # Connect Prisma
    await auth_service.prisma.connect()

    try:
        # Authenticate user
        result = await auth_service.login(
            email=form_data.username,
            password=form_data.password,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
    finally:
        await auth_service.prisma.disconnect()


@router.post("/logout")
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Logout a user"""
    # Connect Prisma
    await auth_service.prisma.connect()

    try:
        success = await auth_service.logout(token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )

        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
    finally:
        await auth_service.prisma.disconnect()


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: str = Depends(oauth2_scheme)
):
    """Refresh an access token"""
    # Connect Prisma
    await auth_service.prisma.connect()

    try:
        result = await auth_service.refresh_token(token)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
    finally:
        await auth_service.prisma.disconnect()


@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    current_user=Depends(get_current_user)
):
    """Change user password"""
    # Connect Prisma
    await auth_service.prisma.connect()

    try:
        success = await auth_service.change_password(
            user_id=current_user.id,
            current_password=data.current_password,
            new_password=data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password"
            )

        return {"message": "Password changed successfully"}

    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )
    finally:
        await auth_service.prisma.disconnect()


@router.post("/request-password-reset")
async def request_password_reset(
    data: PasswordResetRequest,
    request: Request
):
    """Request a password reset"""
    tenant_id = request.headers.get("X-Tenant-Id")

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required"
        )

    # Connect Prisma
    await auth_service.prisma.connect()

    try:
        reset_token = await auth_service.request_password_reset(
            email=data.email,
            tenant_id=tenant_id
        )

        # In a real application, you would send this token via email
        # For now, we'll return it in the response (NOT for production!)
        if reset_token:
            # TODO: Send email with reset token
            logger.info(
                f"Password reset token for {data.email}: {reset_token}"
            )
            return {
                "message": "Password reset instructions sent to your email",
                # Remove this in production!
                "reset_token": reset_token
            }
        else:
            # Don't reveal whether the email exists
            return {
                "message": "Password reset instructions sent to your email"
            }

    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        # Don't reveal errors for security
        return {"message": "Password reset instructions sent to your email"}
    finally:
        await auth_service.prisma.disconnect()


@router.post("/reset-password")
async def reset_password(data: PasswordReset):
    """Reset password with reset token"""
    # Connect Prisma
    await auth_service.prisma.connect()

    try:
        success = await auth_service.reset_password(
            reset_token=data.reset_token,
            new_password=data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        return {"message": "Password reset successfully"}

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )
    finally:
        await auth_service.prisma.disconnect()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user=Depends(get_current_user)
):
    """Get current user info"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.firstName,
        last_name=current_user.lastName,
        tenant_id=current_user.tenantId
    )
