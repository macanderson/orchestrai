from pydantic import BaseModel
from typing import Optional


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: str


class AgentCreate(AgentBase):
    prompt_template: str


class AgentResponse(AgentBase):
    id: str
    prompt_template: str
    created_at: int
    updated_at: int
    created_by: Optional[str] = None
