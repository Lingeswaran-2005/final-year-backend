from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.model import DocumentChunk


async def create_document_chunks(
    db: AsyncSession,
    document_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
) -> list[DocumentChunk]:

    document_chunks = []

    for index, (content, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        document_chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=content,
            embedding=embedding,
        )

        db.add(document_chunk)

        document_chunks.append(document_chunk)

    await db.flush()

    return document_chunks


async def get_document_chunks(
    db: AsyncSession,
    document_id: int,
) -> list[DocumentChunk]:

    result = await db.execute(
        select(DocumentChunk)
        .where(
            DocumentChunk.document_id == document_id
        )
        .order_by(DocumentChunk.chunk_index)
    )

    return list(result.scalars().all())


async def delete_document_chunks(
    db: AsyncSession,
    document_id: int,
) -> None:

    chunks = await get_document_chunks(
        db=db,
        document_id=document_id,
    )

    for chunk in chunks:
        await db.delete(chunk)

    await db.flush()