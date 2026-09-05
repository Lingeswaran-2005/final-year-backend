from langchain_core.messages import HumanMessage

from src.core.exceptions import AppException
from src.schema import ChatRequest, ChatResponse
from src.utils.helper_functions import extract_text


def chat(request: ChatRequest , graph) -> ChatResponse:

    if graph is None:
        raise AppException(
            message="Application graph service is not initialized.",
            status_code=503
        )

    config = {
        "configurable": {
            "thread_id": "user_1"
        }
    }

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=request.message)
            ]
        },
        config=config
    )

    messages = result.get("messages", [])

    if not messages:
        raise AppException(
            message="No response messages returned from graph invocation.",
            status_code=500
        )

    response = messages[-1]

    content = extract_text(
        getattr(response, "content", "")
    )

    return ChatResponse(
        response=content
    )