from langgraph.graph import StateGraph , END , START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.postgres import PostgresSaver

import os

from src.agent import AgentState , should_continue, agent
from src.tools import TOOLS

# Tool Node
tool_node = ToolNode(TOOLS)

# Graph Setup
graph = StateGraph(AgentState)

# Graph Node Setup

graph.add_node("agent", agent)
graph.add_node("tools", tool_node)

# Graph Edge Setup

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    ["tools", END]
)
graph.add_edge("tools", "agent")

