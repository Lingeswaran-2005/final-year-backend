from datetime import datetime, timezone
from langgraph.graph import StateGraph 
from langgraph.types import Command

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
        
## moduled format

def validate_chat_request(request: ChatRequest) -> None:
    if not request.message or not request.message.strip():
        raise AppException(
            message="Message cannot be empty.",
            status_code=400,
        )
        
async def save_user_message(
    db: AsyncSession,
    conversation_id: int,
    content: str,
) -> None:

    message = Message(
        conversation_id=conversation_id,
        role="user",
        content=content,
    )

    db.add(message)
    await db.commit()

async def build_chat_prompt(
    db: AsyncSession,
    user_message: str,
) -> str:

    chunks = await search_similar_chunks(
        db=db,
        query=user_message,
        limit=3,
    )

    rag_context = build_rag_context(chunks)

    return build_augmented_prompt(
        user_question=user_message,
        context=rag_context,
    )

def get_graph_config(conversation_id: int) -> dict:
    return {
        "configurable": {
            "thread_id": str(conversation_id),
        }
    }

async def invoke_chat_graph(
    graph,
    conversation_id: int,
    prompt: str,
):

    config = get_graph_config(conversation_id)

    return await graph.ainvoke(
        {
            "messages": [
                HumanMessage(content=prompt)
            ]
        },
        config=config,
    )

async def resume_chat_graph(
    graph,
    conversation_id: int,
    approved: bool,
):
    config = get_graph_config(conversation_id)

    return await graph.ainvoke(
        Command(
            resume={
                "approved": approved
            }
        ),
        config=config,
    )
    
def get_interrupt(result):

    interrupts = result.get("__interrupt__", [])

    if not interrupts:
        return None

    return interrupts[0].value
    
def extract_graph_response(result) -> str:

    messages = result.get("messages", [])

    if not messages:
        raise AppException(
            message="No response messages returned from graph invocation.",
            status_code=500,
        )

    response_message = messages[-1]

    response_content = extract_text(
        response_message.content
    ).strip()

    if not response_content:
        raise AppException(
            message="The AI service returned an empty response.",
            status_code=500,
        )

    return response_content

async def save_assistant_message(
    db: AsyncSession,
    conversation_id: int,
    content: str,
) -> None:

    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=content,
    )

    db.add(assistant_message)

    conversation = await get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    conversation.updated_at = datetime.now(timezone.utc)

    await db.commit()
    
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

    try:

        # --------------------------------
        # Resume an interrupted graph
        # --------------------------------

        if request.approved is not None:

            result = await resume_chat_graph(
                graph=graph,
                conversation_id=conversation_id,
                approved=request.approved,
            )

        # --------------------------------
        # Start a new chat
        # --------------------------------

        else:

            validate_chat_request(request)

            await get_conversation(
                db=db,
                conversation_id=conversation_id,
            )

            await save_user_message(
                db=db,
                conversation_id=conversation_id,
                content=request.message,
            )

            prompt = await build_chat_prompt(
                db=db,
                user_message=request.message,
            )

            result = await invoke_chat_graph(
                graph=graph,
                conversation_id=conversation_id,
                prompt=prompt,
            )

        # --------------------------------
        # Check whether graph is paused
        # --------------------------------

        interrupt = get_interrupt(result)

        if interrupt is not None:
            return ChatResponse(
                response=None,
                approval_required=True,
                approval_request=interrupt,
            )

        # --------------------------------
        # Normal AI response
        # --------------------------------

        response_content = extract_graph_response(result)

        await save_assistant_message(
            db=db,
            conversation_id=conversation_id,
            content=response_content,
        )

        return ChatResponse(
            response=response_content,
            approval_required=False,
            approval_request=None,
        )

    except AppException:
        raise

    except Exception as error:
        await db.rollback()

        raise AppException(
            message="Failed to process chat request.",
            status_code=500,
        ) from error