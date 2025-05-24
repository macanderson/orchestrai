from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class JobStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    requirements: List[str]
    keywords: List[str]
    location: Optional[str] = None
    type: Optional[str] = None
    salary_range: Optional[str] = None
    department: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: str
    status: JobStatus
    tenant_id: str
    created_at: int
    updated_at: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
