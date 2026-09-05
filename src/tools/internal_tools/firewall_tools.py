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
            return f"iptables error: Invalid response format from execution handler."

        if result.get("error"):
            return f"iptables error: {result['error']}"

        exit_code = result.get("exit_code", -1)
        stderr = result.get("stderr", "").strip()
        stdout = result.get("stdout", "").strip()

        if exit_code != 0:
            return f"iptables error: {stderr if stderr else 'Unknown execution error'}"

        return stdout
    except Exception as e:
        return f"iptables execution error: {str(e)}"


@tool
def firewall_status(
    session_id: str | None = None,
) -> str:
    """Show the current iptables INPUT firewall rules."""

    try:
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
    except Exception as e:
        return f"Error retrieving firewall status: {str(e)}"


@tool
def firewall_allow_port(
    port: int,
    protocol: str = "tcp",
    session_id: str | None = None,
) -> str:
    """Allow incoming traffic on a port using iptables."""

    try:
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
    except Exception as e:
        return f"Error allowing firewall port {port}: {str(e)}"


@tool
def firewall_deny_port(
    port: int,
    protocol: str = "tcp",
    session_id: str | None = None,
) -> str:
    """Drop incoming traffic on a port using iptables."""

    try:
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
    except Exception as e:
        return f"Error denying firewall port {port}: {str(e)}"


@tool
def block_icmp(
    session_id: str | None = None,
) -> str:
    """Block incoming ICMP echo requests, preventing other machines from pinging this server."""

    try:
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
    except Exception as e:
        return f"Error blocking ICMP: {str(e)}"


@tool
def allow_icmp(
    session_id: str | None = None,
) -> str:
    """Remove the ICMP blocking rule so incoming ping requests are allowed."""

    try:
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
    except Exception as e:
        return f"Error allowing ICMP: {str(e)}"