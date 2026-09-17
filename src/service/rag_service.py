from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.model import DocumentChunk
from src.service.embedding_service import generate_embedding


async def search_similar_chunks(
    db: AsyncSession,
    query: str,
    limit: int = 3,
    similarity_threshold: float = 0.75,
) -> list[DocumentChunk]:

    query_embedding = generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )
    
    similarity = 1 - distance

    result = await db.execute(
        select(DocumentChunk)
        .where(similarity >= similarity_threshold)
        .order_by(distance.asc())
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
Use the following document context as additional information that may help answer the user's question.

Document context:

{context}

User question:
{user_question}

Instructions:

* Use the document context when it is relevant to the user's question.
* Treat the document context as supplementary information, not as the only source of truth.
* You may use your existing knowledge when the document context does not contain the required information.
* When the user asks you to perform an action or obtain current information, use the appropriate available tools rather than relying only on the document context.
* Prefer tool results over document context when determining the current state of a system.
* Do not mention embeddings, vector search, chunks, or retrieval.
* Do not invent facts or claim that an action was performed unless you actually performed it.

""".strip()