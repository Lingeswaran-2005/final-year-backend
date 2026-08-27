from langchain.tools import tool

from src.tools.internal_tools import execute


def run_iptables(
    args: list[str],
    session_id: str | None = None,
) -> str:
    """Execute an iptables command locally or on a remote SSH server."""

    command = "iptables " + " ".join(args)

    result = execute(command, session_id)

    if result["exit_code"] != 0:
        return f"iptables error: {result['stderr'].strip()}"

    return result["stdout"].strip()


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


@tool
def firewall_allow_port(
    port: int,
    protocol: str = "tcp",
    session_id: str | None = None,
) -> str:
    """Allow incoming traffic on a port using iptables."""

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


@tool
def firewall_deny_port(
    port: int,
    protocol: str = "tcp",
    session_id: str | None = None,
) -> str:
    """Drop incoming traffic on a port using iptables."""

    if not 1 <= port <= 65535:
        return "Invalid port. Port must be between 1 and 65535."

    if protocol not in {"tcp", "udp"}:
        return "Invalid protocol. Use 'tcp' or 'udp'."

    return run_iptables(
        [
            "-A",
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


@tool
def block_icmp(
    session_id: str | None = None,
) -> str:
    """Block incoming ICMP echo requests, preventing other machines from pinging this server."""

    return run_iptables(
        [
            "-A",
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


@tool
def allow_icmp(
    session_id: str | None = None,
) -> str:
    """Remove the ICMP blocking rule so incoming ping requests are allowed."""

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