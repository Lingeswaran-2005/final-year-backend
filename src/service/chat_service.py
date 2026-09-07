from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_core.messages import HumanMessage

from src.db.model import Conversation, Message
from src.schema.chat import ChatRequest, ChatResponse
from src.core.exceptions import AppException
from src.utils.helper_functions import extract_text


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

    # Make sure conversation exists
    conversation = await get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    db.add(user_message)

    await db.commit()

    # LangGraph thread ID
    config = {
        "configurable": {
            "thread_id": str(conversation_id),
        }
    }

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=request.message)
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

    content = extract_text(
        getattr(response_message, "content", "")
    )

    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=content,
    )

    db.add(assistant_message)

    # Update conversation activity
    conversation.updated_at = datetime.now(timezone.utc)

    await db.commit()

    return ChatResponse(
        response=content,
    )