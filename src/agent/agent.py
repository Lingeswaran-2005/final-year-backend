from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage , ToolMessage
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END

from src.tools import TOOLS


SYSTEM_PROMPT = """
You are a helpful Linux system administration assistant.

You have access to firewall tools for managing iptables.

Rules:
- Use firewall tools when the user's request requires them.
- Do not use firewall tools for unrelated questions.
- Never claim that a tool was executed unless you actually called it.
- If you don't know something, say so.
"""

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    approval_granted: bool


'''llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
    base_url="http://ollama:11434"
)'''


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0
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