from typing import Annotated, TypedDict
import os
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage , ToolMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import END
from src.tools import TOOLS

SYSTEM_PROMPT = """
You are an enterprise IT operations assistant specializing in Linux
administration and network infrastructure.

Your role is to answer technical questions, diagnose issues, and use
available tools to inspect or manage systems.

Rules:
- Use tools only when the request requires them.
- Prefer read-only tools for diagnostics.
- Execute modifications only when requested and approved.
- Never invent system information or tool results.
- Trust tool results over assumptions when reporting system state.
- If an operation fails, explain the actual error.
- If information is insufficient, ask for clarification.
- Give accurate, concise technical responses.
"""

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    approval_granted: bool


from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="local-model",
    base_url=os.getenv("LLM_BASE_URL"),
    api_key="local-key",
    temperature=0,
    streaming=False,
    timeout=120,
    max_retries=2,
    extra_body={
        "chat_template_kwargs":{
            "enable_thinking" : False
        }
    }
)

llm_with_tools = llm.bind_tools(TOOLS)

def should_continue(state: AgentState) -> str:
    try:
        messages = state.get('messages', [])
        if not messages:
            return END
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "approval"
        return END
    except Exception:
        return END
    
def route_after_approval(state: AgentState) -> str:
    if state.get("approval_granted") is True:
        return "tools"

    return "approval_denied"


def approval_denied(state: AgentState):

    tool_call = state["messages"][-1].tool_calls[0]

    return {
        "messages": [
            ToolMessage(
                content="The user denied permission to execute this tool.",
                tool_call_id=tool_call["id"],
            )
        ]
    }
    
def reset_approval(state: AgentState):
    return {
        "approval_granted": False
    }    


def agent(state: AgentState) -> AgentState:
    try:
        message = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state['messages']
        ]
        
        response = llm_with_tools.invoke(message)
        
        return {
            "messages": [response]
        }
    except Exception as e:
        error_msg = AIMessage(content=f"An error occurred while communicating with the AI service: {str(e)}")
        return {
            "messages": [error_msg]
        }