from langchain_core.messages import ToolMessage
from langgraph.types import interrupt
from src.agent.agent import AgentState


def requires_approval(tool) -> bool:
    """
    Return True when human approval is required.

    Tools must explicitly declare themselves read-only
    to bypass approval.
    """

    metadata = getattr(tool, "metadata", {}) or {}

    read_only = metadata.get("readOnlyHint")

    # Fail closed.
    return read_only is not True


def human_approval(state: AgentState, tools) -> AgentState:
    messages = state.get("messages", [])

    if not messages:
        return {
            "approval_granted": True,
        }

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        return {
            "approval_granted": True,
        }

    for tool_call in tool_calls:
        tool_name = tool_call["name"]

        registered_tool = next(
            (
                tool
                for tool in tools
                if tool.name == tool_name
            ),
            None,
        )

        # Unknown tools must fail closed.
        if registered_tool is None:
            approval = interrupt({
                "type": "approval_required",
                "tool_name": tool_name,
                "tool_args": tool_call.get("args", {}),
                "message": (
                    "This tool could not be identified. "
                    "Approval is required."
                ),
            })

            if not approval.get("approved", False):
                return {
                    "approval_granted": False,
                }

            continue

        if not requires_approval(registered_tool):
            continue

        approval = interrupt({
            "type": "approval_required",
            "tool_name": tool_name,
            "tool_args": tool_call.get("args", {}),
            "message": f"The agent wants to execute '{tool_name}'.",
        })

        if not approval.get("approved", False):
            return {
                "approval_granted": False,
            }

    return {
        "approval_granted": True,
    }