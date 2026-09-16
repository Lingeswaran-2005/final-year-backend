from datetime import datetime, timezone
from langgraph.graph import StateGraph

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_core.messages import HumanMessage

from src.db.model import Conversation, Message
from src.schema.chat import ChatRequest, ChatResponse
from src.core.exceptions import AppException
from src.utils.helper_functions import extract_text
from src.service.rag_service import search_similar_chunks , build_rag_context , build_augmented_prompt


async def create_conversation(
    db: AsyncSession,
) -> Conversation:

    conversation = Conversation()

    db.add(conversation)

    await db.commit()
    await db.refresh(conversation)

    return conversation


async def get_conversations(
    db: AsyncSession,
) -> list[Conversation]:

    result = await db.execute(
        select(Conversation)
        .order_by(Conversation.updated_at.desc())
    )

    return list(result.scalars().all())


async def get_conversation(
    db: AsyncSession,
    conversation_id: int,
) -> Conversation:

    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
    )

    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise AppException(
            message="Conversation not found.",
            status_code=404,
        )

    return conversation


async def get_messages(
    db: AsyncSession,
    conversation_id: int,
) -> list[Message]:

    # Make sure conversation exists
    await get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )

    return list(result.scalars().all())


async def chat(
    db: AsyncSession,
    graph,
    conversation_id: int,
    request: ChatRequest,
) -> ChatResponse:

    if graph is None:
        raise AppException(
            message="Application graph service is not initialized.",
            status_code=503,
        )

    if not request.message or not request.message.strip():
        raise AppException(
            message="Message cannot be empty.",
            status_code=400,
        )

    # Make sure the conversation exists
    conversation = await get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    # Save the original user message.
    # The augmented prompt is not stored in the application chat history.
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    db.add(user_message)
    await db.commit()

    try:
        # Retrieve the top three relevant document chunks.
        chunks = await search_similar_chunks(
            db=db,
            query=request.message,
            limit=3,
        )

        # Build context from the retrieved chunks.
        rag_context = build_rag_context(chunks)

        # Add the context to the user's question.
        augmented_prompt = build_augmented_prompt(
            user_question=request.message,
            context=rag_context,
        )

        # Use the existing graph and its existing SYSTEM_PROMPT.
        config = {
            "configurable": {
                "thread_id": str(conversation_id),
            }
        }

        result = await graph.ainvoke(
            {
                "messages": [
                    HumanMessage(content=augmented_prompt)
                ]
            },
            config=config,
        )

        messages = result.get("messages", [])

        if not messages:
            raise AppException(
                message="No response messages returned from graph invocation.",
                status_code=500,
            )

        response_message = messages[-1]

        response_content = response_message.content

        if isinstance(response_content, list):
            response_content = "\n".join(
                item.get("text", "")
                for item in response_content
                if isinstance(item, dict)
                and item.get("type") == "text"
            )

        if not isinstance(response_content, str):
            response_content = str(response_content)

        response_content = response_content.strip()

        if not response_content:
            raise AppException(
                message="The AI service returned an empty response.",
                status_code=500,
            )

        # Save only the normal assistant answer.
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_content,
        )

        db.add(assistant_message)

        conversation.updated_at = datetime.now(timezone.utc)

        await db.commit()

        return ChatResponse(
            response=response_content,
        )

    except AppException:
        raise

    except Exception as error:
        await db.rollback()

        raise AppException(
            message="Failed to process chat request.",
            status_code=500,
        ) from error