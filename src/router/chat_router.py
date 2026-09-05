from fastapi import APIRouter , Depends

from src.schema import ChatRequest, ChatResponse
from src.service.chat_service import chat
from src.core.dependencies import get_graph


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("", response_model=ChatResponse)
def chat_route(request: ChatRequest , graph = Depends(get_graph)):

    return chat(request , graph)