from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.model import DocumentChunk
from src.service.embedding_service import generate_embedding


async def search_similar_chunks(
    db: AsyncSession,
    query: str,
    limit: int = 3,
) -> list[DocumentChunk]:

    query_embedding = generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    result = await db.execute(
        select(DocumentChunk)
        .order_by(distance)
        .limit(limit)
    )

    return list(result.scalars().all())


def build_rag_context(
    chunks: list[DocumentChunk],
) -> str:

    if not chunks:
        return (
            "No relevant document context was found."
        )

    context_parts: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"""
            Context {index}:
            {chunk.content}
            """.strip()
        )

    return "\n\n".join(context_parts)

def build_augmented_prompt(
    user_question: str,
    context: str,
) -> str:

    return f"""
Use the following document context to answer the user's question.

Document context:
-----------------
{context}
-----------------

User question:
{user_question}

Instructions:
- Use the document context when it is relevant.
- Do not mention embeddings, vector search, chunks, or retrieval.
- If the context does not contain the answer, say that the information
  is not available in the provided documents.
- Do not invent facts.
""".strip()