from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schema.chat import ChatRequest

from src.service.chat_service import (
    create_conversation,
    get_conversations,
    get_conversation,
    get_messages,
    chat,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("")
async def create_chat(
    db: AsyncSession = Depends(get_db),
):
    return await create_conversation(db)


@router.get("")
async def list_chats(
    db: AsyncSession = Depends(get_db),
):
    return await get_conversations(db)


@router.get("/{conversation_id}")
async def get_chat(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_conversation(
        db=db,
        conversation_id=conversation_id,
    )


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_messages(
        db=db,
        conversation_id=conversation_id,
    )


@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    request: ChatRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    return await chat(
        db=db,
        graph=req.app.state.graph,
        conversation_id=conversation_id,
        request=request,
    )