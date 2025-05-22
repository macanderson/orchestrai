from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from prisma import Prisma
from .core.config import settings
from .routes.v1.auth import router as auth_router
from .routes.v1.documents import router as documents_router
from .routes.v1.agents import router as agents_router
from .routes.v1.chat import router as chat_router
from .routes.v1.projects import router as projects_router
from .core.auth import get_current_user
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Prisma client
prisma = Prisma()

# Tenant middleware
class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-Id")
        
        # Skip tenant check for auth endpoints and public routes
        if request.url.path.startswith("/api/v1/auth") or request.url.path.startswith("/docs"):
            return await call_next(request)
        
        # For protected routes, ensure tenant ID is provided
        if not tenant_id:
            return Response(
                status_code=400,
                content="X-Tenant-Id header is required",
                media_type="text/plain"
            )
        
        # Store tenant ID in request state for later use
        request.state.tenant_id = tenant_id
        
        # Continue processing the request
        return await call_next(request)


app = FastAPI(
    title="DocuChat API",
    description="API for RAG-based documentation chat system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware
app.add_middleware(TenantMiddleware)


@app.on_event("startup")
async def startup():
    await prisma.connect()
    logger.info("Connected to database")


@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()
    logger.info("Disconnected from database")


# Register routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"], dependencies=[Depends(get_current_user)])
app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"], dependencies=[Depends(get_current_user)])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"], dependencies=[Depends(get_current_user)])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["Projects"], dependencies=[Depends(get_current_user)])


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}
