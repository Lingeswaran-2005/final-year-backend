from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schema.document import DocumentResponse

from src.service.document_service import (
    delete_document,
    get_document,
    get_documents,
    upload_document,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentResponse,
)
async def upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await upload_document(
        db=db,
        file=file,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
async def get_all(
    db: AsyncSession = Depends(get_db),
):
    return await get_documents(
        db=db,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_one(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_document(
        db=db,
        document_id=document_id,
    )


@router.get(
    "/{document_id}/download",
)
async def download(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    document = await get_document(
        db=db,
        document_id=document_id,
    )

    path = Path(
        document.storage_path
    )

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="Stored file not found.",
        )

    return FileResponse(
        path=path,
        media_type=document.content_type,
        filename=document.filename,
    )


@router.delete(
    "/{document_id}",
)
async def delete(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    await delete_document(
        db=db,
        document_id=document_id,
    )

    return {
        "message": "Document deleted successfully."
    }