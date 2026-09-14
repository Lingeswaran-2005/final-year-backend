from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.db.model import Document


UPLOAD_DIRECTORY = Path("/app/storage/documents")


async def upload_document(
    db: AsyncSession,
    file: UploadFile,
) -> Document:

    if not file.filename:
        raise AppException(
            message="Filename is missing.",
            status_code=400,
        )

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    original_filename = Path(
        file.filename
    ).name

    stored_filename = (
        f"{uuid4()}_{original_filename}"
    )

    storage_path = (
        UPLOAD_DIRECTORY / stored_filename
    )

    file_size = 0

    try:

        with storage_path.open("wb") as output_file:

            while chunk := await file.read(1024 * 1024):

                output_file.write(chunk)

                file_size += len(chunk)

    except Exception:

        if storage_path.exists():
            storage_path.unlink()

        raise AppException(
            message="Failed to store document.",
            status_code=500,
        )

    document = Document(
        filename=original_filename,
        content_type=(
            file.content_type
            or "application/octet-stream"
        ),
        file_size=file_size,
        storage_path=str(storage_path)
    )

    db.add(document)

    try:

        await db.commit()
        await db.refresh(document)

    except Exception:

        await db.rollback()

        if storage_path.exists():
            storage_path.unlink()

        raise AppException(
            message="Failed to save document metadata.",
            status_code=500,
        )

    return document


async def get_documents(
    db: AsyncSession,
) -> list[Document]:

    result = await db.execute(
        select(Document)
        .order_by(Document.created_at.desc())
    )

    return list(
        result.scalars().all()
    )


async def get_document(
    db: AsyncSession,
    document_id: int,
) -> Document:

    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise AppException(
            message="Document not found.",
            status_code=404,
        )

    return document


async def delete_document(
    db: AsyncSession,
    document_id: int,
) -> None:

    document = await get_document(
        db=db,
        document_id=document_id,
    )

    storage_path = Path(
        document.storage_path
    )

    try:

        await db.delete(document)

        await db.commit()

    except Exception:

        await db.rollback()

        raise AppException(
            message="Failed to delete document.",
            status_code=500,
        )

    if storage_path.exists():

        try:
            storage_path.unlink()

        except OSError:
            pass