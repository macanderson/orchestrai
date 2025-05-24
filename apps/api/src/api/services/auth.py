from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from db.client import Prisma
from api.core.config import settings
import secrets
import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication and user management"""

    def __init__(self):
        self.prisma = Prisma()
        self.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    async def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    async def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.JWT_SECRET_KEY, algorithm=self.algorithm
        )
        return encoded_jwt

    async def decode_access_token(self, token: str) -> Optional[dict]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(
                token, self.JWT_SECRET_KEY,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            return payload
        except JWTError:
            return None

    async def register_user(
        self,
        email: str,
        password: str,
        tenant_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role_id: Optional[str] = None
    ) -> dict:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.prisma.user.find_first(
            where={"email": email, "tenantId": tenant_id}
        )

        if existing_user and not existing_user.deleted:
            raise ValueError("User with this email already exists")

        # Hash the password
        password_hash = await self.hash_password(password)

        # Create the user
        user = await self.prisma.user.create({
            "data": {
                "email": email,
                "passwordHash": password_hash,
                "firstName": first_name,
                "lastName": last_name,
                "tenantId": tenant_id,
                "roleId": role_id,
            }
        })

        # Create access token
        access_token = await self.create_access_token(
            data={"sub": user.id, "email": user.email, "tenant_id": tenant_id}
        )
        # Create session
        await self.create_user_session(
            user_id=user.id,
            token=access_token,
            ip_address=None,
            user_agent=None
        )

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "tenantId": user.tenantId,
            },
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def login(
        self,
        email: str,
        password: str,
        tenant_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """Authenticate a user and return tokens"""
        # Find user
        user = await self.prisma.user.find_first(
            where={
                "email": email,
                "tenantId": tenant_id,
                "deleted": False
            }
        )

        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not user.passwordHash or not await self.verify_password(
            password, user.passwordHash
        ):
            raise ValueError("Invalid email or password")

        # Create access token
        access_token = await self.create_access_token(
            data={"sub": user.id, "email": user.email, "tenant_id": tenant_id}
        )

        # Create session
        await self.create_user_session(
            user_id=user.id,
            token=access_token,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "tenantId": user.tenantId,
            },
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def create_user_session(
        self,
        user_id: str,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Create a user session"""
        expires_at = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )

        session = await self.prisma.usersession.create({
            "data": {
                "userId": user_id,
                "token": token,
                "expiresAt": expires_at,
                "ipAddress": ip_address,
                "userAgent": user_agent,
            }
        })

        return session

    async def get_current_user(self, token: str):
        """Get the current user from a token"""
        # Decode token
        payload = await self.decode_access_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Check if session exists and is valid
        session = await self.prisma.usersession.find_first(
            where={
                "token": token,
                "deleted": False,
                "expiresAt": {"gt": datetime.utcnow()}
            }
        )

        if not session:
            return None

        # Get user
        user = await self.prisma.user.find_unique(
            where={"id": user_id},
            include={"tenant": True, "role": True}
        )

        if not user or user.deleted:
            return None

        return user

    async def logout(self, token: str) -> bool:
        """Logout a user by invalidating their session"""
        session = await self.prisma.usersession.find_first(
            where={"token": token}
        )

        if session:
            await self.prisma.usersession.update(
                where={"id": session.id},
                data={
                    "deleted": True,
                    "deletedAt": datetime.utcnow()
                }
            )
            return True

        return False

    async def refresh_token(self, token: str) -> Optional[dict]:
        """Refresh an access token"""
        user = await self.get_current_user(token)
        if not user:
            return None

        # Invalidate old session
        await self.logout(token)

        # Create new token
        new_token = await self.create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "tenant_id": user.tenantId
            }
        )

        # Create new session
        await self.create_user_session(
            user_id=user.id,
            token=new_token
        )

        return {
            "access_token": new_token,
            "token_type": "bearer",
        }

    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change a user's password"""
        user = await self.prisma.user.find_unique(
            where={"id": user_id}
        )

        if not user or not user.passwordHash:
            return False

        # Verify current password
        if not await self.verify_password(current_password, user.passwordHash):
            return False

        # Hash new password
        new_password_hash = await self.hash_password(new_password)

        # Update user
        await self.prisma.user.update(
            where={"id": user_id},
            data={"passwordHash": new_password_hash}
        )

        # Invalidate all sessions for this user
        await self.prisma.usersession.update_many(
            where={"userId": user_id, "deleted": False},
            data={
                "deleted": True,
                "deletedAt": datetime.utcnow()
            }
        )

        return True

    async def request_password_reset(
        self,
        email: str,
        tenant_id: str
    ) -> Optional[str]:
        """Request a password reset token"""
        user = await self.prisma.user.find_first(
            where={
                "email": email,
                "tenantId": tenant_id,
                "deleted": False
            }
        )

        if not user:
            return None

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        # Store reset token (you might want to create a
        # separate table for this)
        # TODO: Create a separate table for this
        # For now, we'll create a special session
        expires_at = datetime.utcnow() + timedelta(hours=24)

        await self.prisma.usersession.create({
            "data": {
                "userId": user.id,
                "token": f"reset_{reset_token}",
                "expiresAt": expires_at,
            }
        })

        return reset_token

    async def reset_password(
        self,
        reset_token: str,
        new_password: str
    ) -> bool:
        """Reset a user's password with a reset token"""
        # Find reset session
        session = await self.prisma.usersession.find_first(
            where={
                "token": f"reset_{reset_token}",
                "deleted": False,
                "expiresAt": {"gt": datetime.utcnow()}
            }
        )

        if not session:
            return False

        # Hash new password
        new_password_hash = await self.hash_password(new_password)

        # Update user password
        await self.prisma.user.update(
            where={"id": session.userId},
            data={"passwordHash": new_password_hash}
        )

        # Invalidate all sessions for this user
        await self.prisma.usersession.update_many(
            where={"userId": session.userId},
            data={
                "deleted": True,
                "deletedAt": datetime.utcnow()
            }
        )

        return True


# Dependency injection for FastAPI authentication

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service() -> AuthService:
    return AuthService()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get the current user from the token.
    """
    return await auth_service.get_current_user(token)


async def get_current_tenant(
    user=Depends(get_current_user)
):
    """
    Dependency to get the current tenant from the current user.
    """
    if user and hasattr(user, "tenant"):
        return user.tenant
    return None
