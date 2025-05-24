from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Request,
)
from typing import List, Dict, Any
from api.schemas.document import DocumentResponse, DocumentURLUpload
from api.services.document_processor import DocumentProcessor
from api.services.auth import AuthService
from api.services.auth import get_current_user
import tempfile
import csv
import io


router = APIRouter()
document_processor = DocumentProcessor()
auth_service = AuthService()


@router.post("/upload-url", response_model=Dict[str, Any])
async def upload_url(
    data: DocumentURLUpload,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Upload a document from a URL"""
    tenant_id = request.state.tenant_id

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={
            "id": data.project_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        },
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Process the URL
    result = await document_processor.process_url(
        url=str(data.url), project_id=data.project_id, user_id=current_user.id
    )

    return result


@router.post("/upload-file", response_model=Dict[str, Any])
async def upload_file(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Upload a document file"""
    tenant_id = request.state.tenant_id

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={"id": project_id, "tenant_id": tenant_id, "deleted_at": None},
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Save file to temp location
    file_content = await file.read()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    # Process the file
    result = await document_processor.process_file(
        file_path=temp_file_path,
        file_type=file.content_type,
        project_id=project_id,
        user_id=current_user.id,
    )

    return result


@router.post("/upload-csv-data", response_model=Dict[str, Any])
async def upload_csv_data(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    request: Request = None,
):
    """Upload and process raw CSV data for RAG"""
    tenant_id = request.state.tenant_id

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={"id": project_id, "tenant_id": tenant_id, "deleted_at": None},
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Read and parse CSV data
    file_content = await file.read()
    csv_content = file_content.decode("utf-8")

    csv_reader = csv.DictReader(io.StringIO(csv_content))
    csv_data = list(csv_reader)

    # Process the CSV data
    result = await document_processor.process_csv_data(
        csv_data=csv_data, project_id=project_id, user_id=current_user.id
    )

    return result


@router.get("/{project_id}", response_model=List[DocumentResponse])
async def get_documents(
    project_id: str,
    current_user=Depends(get_current_user),
    request: Request = None,  # noqa: F821
):
    """Get all documents for a project"""
    tenant_id = request.state.tenant_id

    # Check if user has access to the project
    project = await request.state.prisma.project.find_first(
        where={"id": project_id, "tenant_id": tenant_id, "deleted_at": None},
        include={"users": {"where": {"user_id": current_user.id}}},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get all documents for the project
    documents = await request.state.prisma.document.find_many(
        where={"project_id": project_id, "deleted_at": None},
        order_by={"created_at": "desc"},
    )

    return documents
