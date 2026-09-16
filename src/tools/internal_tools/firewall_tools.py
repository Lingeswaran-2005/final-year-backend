from langchain.tools import tool

from src.tools.internal_tools import execute


def run_iptables(
    args: list[str],
    session_id: str | None = None,
) -> str:
    """Execute an iptables command locally or on a remote SSH server."""

    try:
        command = "iptables " + " ".join(args)
        result = execute(command, session_id)

        if not isinstance(result, dict):
            return "iptables error: Invalid response format from execution handler."

        if result.get("error"):
            return f"iptables error: {result['error']}"

        exit_code = result.get("exit_code", -1)
        stderr = result.get("stderr", "").strip()
        stdout = result.get("stdout", "").strip()

        if exit_code != 0:
            return f"iptables error: {stderr if stderr else 'Unknown execution error'}"

        return stdout or "iptables command executed successfully."

    except Exception as e:
        return f"iptables execution error: {str(e)}"


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

@tool
def firewall_status(
    session_id: str | None = None,
) -> str:
    """Show the current iptables INPUT firewall rules."""

    return run_iptables(
        [
            "-L",
            "INPUT",
            "-n",
            "-v",
            "--line-numbers",
        ],
        session_id,
    )

firewall_status.metadata = {
    "readOnlyHint": True,
}

# ---------------------------------------------------------
# PORT RULES
# ---------------------------------------------------------

@tool
def firewall_allow_port(
    port: int,
    protocol: str = "tcp",
    session_id: str | None = None,
) -> str:
    """Allow incoming traffic on a TCP or UDP port."""

    if not 1 <= port <= 65535:
        return "Invalid port. Port must be between 1 and 65535."

    if protocol not in {"tcp", "udp"}:
        return "Invalid protocol. Use 'tcp' or 'udp'."

    return run_iptables(
        [
            "-I",
            "INPUT",
            "-p",
            protocol,
            "--dport",
            str(port),
            "-j",
            "ACCEPT",
        ],
        session_id,
    )

firewall_allow_port.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

@tool
def firewall_deny_port(
    port: int,
    protocol: str = "tcp",
    session_id: str | None = None,
) -> str:
    """Block incoming traffic on a TCP or UDP port."""

    if not 1 <= port <= 65535:
        return "Invalid port. Port must be between 1 and 65535."

    if protocol not in {"tcp", "udp"}:
        return "Invalid protocol. Use 'tcp' or 'udp'."

    return run_iptables(
        [
            "-I",
            "INPUT",
            "-p",
            protocol,
            "--dport",
            str(port),
            "-j",
            "DROP",
        ],
        session_id,
    )

firewall_deny_port.metadata = {
    "readOnlyHint": False,
    "destructiveHint": True,
}

# ---------------------------------------------------------
# DELETE RULE
# ---------------------------------------------------------

@tool
def firewall_delete_rule(
    rule_number: int,
    session_id: str | None = None,
) -> str:
    """Delete an INPUT firewall rule using its rule number."""

    if rule_number < 1:
        return "Invalid rule number. Rule number must be greater than 0."

    return run_iptables(
        [
            "-D",
            "INPUT",
            str(rule_number),
        ],
        session_id,
    )

firewall_delete_rule.metadata = {
    "readOnlyHint": False,
    "destructiveHint": True,
}

# ---------------------------------------------------------
# ICMP
# ---------------------------------------------------------

@tool
def firewall_block_icmp(
    session_id: str | None = None,
) -> str:
    """Block incoming ICMP echo requests, preventing other machines from pinging this server."""

    return run_iptables(
        [
            "-I",
            "INPUT",
            "-p",
            "icmp",
            "--icmp-type",
            "echo-request",
            "-j",
            "DROP",
        ],
        session_id,
    )

firewall_block_icmp.metadata = {
    "readOnlyHint": False,
    "destructiveHint": True,
}

@tool
def firewall_allow_icmp(
    session_id: str | None = None,
) -> str:
    """Remove the first matching ICMP echo-request blocking rule."""

    return run_iptables(
        [
            "-D",
            "INPUT",
            "-p",
            "icmp",
            "--icmp-type",
            "echo-request",
            "-j",
            "DROP",
        ],
        session_id,
    )

firewall_allow_icmp.metadata = {
    "readOnlyHint": False,
    "destructiveHint": True,
}

# ---------------------------------------------------------
# FLUSH
# ---------------------------------------------------------

@tool
def firewall_flush(
    session_id: str | None = None,
) -> str:
    """Remove all rules from the INPUT chain."""

    return run_iptables(
        [
            "-F",
            "INPUT",
        ],
        session_id,
    )

firewall_flush.metadata = {
    "readOnlyHint": False,
    "destructiveHint": True,
}

# ---------------------------------------------------------
# DEFAULT POLICY
# ---------------------------------------------------------

@tool
def firewall_set_default_policy(
    policy: str,
    session_id: str | None = None,
) -> str:
    """Set the default INPUT policy to ACCEPT or DROP."""

    if policy not in {"ACCEPT", "DROP"}:
        return "Invalid policy. Use 'ACCEPT' or 'DROP'."

    return run_iptables(
        [
            "-P",
            "INPUT",
            policy,
        ],
        session_id,
    )

firewall_set_default_policy.metadata = {
    "readOnlyHint": False,
    "destructiveHint": True,
}