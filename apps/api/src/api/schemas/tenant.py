from pydantic import BaseModel
from typing import Optional, Literal


class TenantCreate(BaseModel):
    name: str
    slug: str
    license_type: Literal["TRIAL", "PRO", "ENTERPRISE"] = "TRIAL"


class TenantResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    role_id: str
    tenant_id: str
    created_at: int
    updated_at: int
    created_by: Optional[str] = None 