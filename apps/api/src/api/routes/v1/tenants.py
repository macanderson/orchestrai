from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from api.schemas.tenant import TenantResponse
from api.services.auth import get_current_tenant

router = APIRouter()


@router.get("/", response_model=List[TenantResponse])
async def get_tenants(
    current_tenant=Depends(get_current_tenant), request: Request = None
):  # noqa: E501
    """Get all tenants for the current tenant that the tenant has access to"""
    tenant_id = request.state.tenant_id

    # Get all tenants for the tenant where the tenant is a member
    tenants = await request.state.prisma.Tenant.find_many(
        where={
            "tenant_id": tenant_id,
            "deleted_at": None,
            "tenants": {
                "some": {"tenant_id": current_tenant.id, "deleted_at": None}
            },  # noqa: E501
        },
        order_by={"created_at": "desc"},
    )

    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    current_tenant=Depends(get_current_tenant),
    request: Request = None,  # noqa: E501
):
    """Get a specific Tenant"""
    tenant_id = request.state.tenant_id

    # Get the Tenant
    tenant = await request.state.prisma.Tenant.find_first(
        where={
            "id": tenant_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
            "tenants": {
                "some": {"tenant_id": current_tenant.id, "deleted_at": None}
            },  # noqa: E501
        }
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant
