from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from api.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
auth_service = AuthService()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user from the token.
    """
    return await auth_service.get_current_user(token)
