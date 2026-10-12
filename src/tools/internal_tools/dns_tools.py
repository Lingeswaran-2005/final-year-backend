import re

from langchain_core.tools import tool
from src.tools.internal_tools.ssh_tools import execute


def run_dns_command(
    command: str,
    session_id: str | None = None,
) -> str:
    """Execute a DNS command locally or on a remote SSH server."""
    try:
        result = execute(command, session_id)

        if not isinstance(result, dict):
            return "DNS error: Invalid response format from execution handler."

        if result.get("error"):
            return f"DNS error: {result['error']}"

        exit_code = result.get("exit_code", -1)
        stderr = result.get("stderr", "").strip()
        stdout = result.get("stdout", "").strip()

        if exit_code != 0:
            return f"DNS error: {stderr or 'Unknown execution error'}"

        return stdout or "DNS command executed successfully."

    except Exception as e:
        return f"DNS execution error: {str(e)}"


# 1. BIND status

@tool
def dns_status(session_id: str | None = None) -> str:
    """Check BIND status and whether the DNS server process is running."""
    result = run_dns_command("rndc status", session_id)

    if not result.startswith("DNS error:"):
        return result

    # RNDC may be unavailable even when BIND is running.
    process_result = run_dns_command(
        "pgrep -a named",
        session_id,
    )

    if not process_result.startswith("DNS error:"):
        return (
            "BIND process is running, but RNDC status could not be obtained.\n"
            f"Process information:\n{process_result}\n"
            f"RNDC result: {result}"
        )

    return (
        f"Unable to verify BIND status.\n"
        f"RNDC result: {result}\n"
        f"Process check: {process_result}"
    )


dns_status.metadata = {"readOnlyHint": True}


# 2. BIND options

@tool
def dns_options(session_id: str | None = None) -> str:
    """Read BIND options, including recursion and query access settings."""
    return run_dns_command(
        "cat /etc/bind/named.conf.options",
        session_id,
    )


dns_options.metadata = {"readOnlyHint": True}


# 3. Local configuration and configured zones

@tool
def dns_local_config(session_id: str | None = None) -> str:
    """Read BIND local configuration containing configured zone declarations."""
    return run_dns_command(
        "cat /etc/bind/named.conf.local",
        session_id,
    )


dns_local_config.metadata = {"readOnlyHint": True}


# 4. Zone data

@tool
def dns_zone_data(
    zone_name: str,
    session_id: str | None = None,
) -> str:
    """Read the records in a DNS zone file."""
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", zone_name):
        return "DNS error: Invalid zone name."

    return run_dns_command(
        f"cat /etc/bind/zones/db.{zone_name}",
        session_id,
    )


dns_zone_data.metadata = {"readOnlyHint": True}

