from pydantic import BaseModel
from typing import Any

class ChatRequest(BaseModel):
    message: str | None = None
    approved : bool | None = None


class ChatResponse(BaseModel):
    response: str | None = None
    approval_required: bool = False
    approval_request: dict[str, Any] | None = None