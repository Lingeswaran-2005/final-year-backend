from langgraph.graph import StateGraph , END , START
from langgraph.prebuilt import ToolNode


from src.agent.agent import AgentState , should_continue, agent , route_after_approval , approval_denied
from src.tools import TOOLS
from src.agent.approval import human_approval

# Tool Node
tool_node = ToolNode(TOOLS)

# Graph Setup
graph = StateGraph(AgentState)

# Graph Node Setup

graph.add_node("agent", agent)

graph.add_node(
    "approval",
    lambda state: human_approval(
        state,
        TOOLS,
    ),
)

graph.add_node(
    "approval_denied",
    approval_denied,
)

graph.add_node("tools", tool_node)

# Graph Edge Setup

graph.add_edge(START, "agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "approval": "approval",
        END: END,
    },
)

graph.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "tools": "tools",
        "approval_denied": "approval_denied",
    },
)

graph.add_edge("approval_denied", "agent")

graph.add_edge("tools", "agent")

