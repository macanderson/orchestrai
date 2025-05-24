# __init__.py
from api.routes.v1.auth import router as auth_router
from api.routes.v1.documents import router as documents_router
from api.routes.v1.projects import router as projects_router
from api.routes.v1.users import router as users_router
from api.routes.v1.tenants import router as tenants_router
from api.routes.v1.agents import router as agents_router


__all__ = [
    "auth_router",
    "documents_router",
    "projects_router",
    "users_router",
    "tenants_router",
    "agents_router",
]
