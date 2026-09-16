from sqlalchemy.ext.asyncio import AsyncSession

from src.db.model import Document

from src.service.chunking_service import create_chunks
from src.service.document_chunk_service import (
    create_document_chunks,
)
from src.service.embedding_service import generate_embeddings
from src.service.text_extraction_service import extract_text


async def process_document(
    db: AsyncSession,
    document: Document,
) -> None:

    text = extract_text(
        file_path=document.storage_path,
        content_type=document.content_type,
    )

    if not text.strip():
        raise ValueError(
            "Could not extract any text from the document."
        )

    chunks = create_chunks(text)

    if not chunks:
        raise ValueError(
            "Document did not produce any chunks."
        )

    embeddings = generate_embeddings(chunks)

    await create_document_chunks(
        db=db,
        document_id=document.id,
        chunks=chunks,
        embeddings=embeddings,
    )