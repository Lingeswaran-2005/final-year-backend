from typing import Annotated,TypedDict
from langchain_core.messages import BaseMessage , SystemMessage
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


'''llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
    base_url="http://ollama:11434"
)'''


llm = ChatGoogleGenerativeAI(
    model = "gemini-3.1-flash-lite",
    temperature = 0
)

llm_with_tools = llm.bind_tools(TOOLS)

def should_continue(state : AgentState) -> str:
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "tools"
    return END
    
def agent(state : AgentState) -> AgentState:
    
    message = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state['messages']
    ]
    
    response = llm_with_tools.invoke(message)
    
    return {
        "messages" : [response]
    }