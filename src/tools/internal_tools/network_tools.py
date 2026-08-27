from langchain.tools import tool

from src.tools.internal_tools.ssh_tools import execute


@tool
def ping(
    host: str,
    session_id: str | None = None,
) -> dict:
    """
    Ping a host.

    If session_id is provided, ping is executed from
    the remote SSH server. Otherwise it runs locally.
    """

    return execute(
        f"ping -c 4 {host}",
        session_id,
    )


@tool
def dig(
    domain: str,
    session_id: str | None = None,
) -> dict:
    """
    Perform a DNS lookup.

    If session_id is provided, dig is executed from
    the remote SSH server. Otherwise it runs locally.
    """

    return execute(
        f"dig {domain}",
        session_id,
    )


@tool
def curl(
    url: str,
    session_id: str | None = None,
) -> dict:
    """
    Make an HTTP request.

    If session_id is provided, curl is executed from
    the remote SSH server. Otherwise it runs locally.
    """

    return execute(
        f"curl -I {url}",
        session_id,
    )


@tool
def traceroute(
    host: str,
    session_id: str | None = None,
) -> dict:
    """
    Trace the network route to a host.

    If session_id is provided, traceroute is executed
    from the remote SSH server. Otherwise it runs locally.
    """

    return execute(
        f"traceroute {host}",
        session_id,
    )