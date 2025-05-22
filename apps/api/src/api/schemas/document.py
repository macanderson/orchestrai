from pydantic import BaseModel, HttpUrl
from typing import Optional, Any, Dict


class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str


class DocumentCreate(DocumentBase):
    source_url: Optional[HttpUrl] = None
    content_type: str


class DocumentResponse(DocumentBase):
    id: str
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    content_type: str
    created_at: int
    updated_at: int
    created_by: Optional[str] = None


class DocumentURLUpload(BaseModel):
    url: HttpUrl
    project_id: str


class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    created_at: int
