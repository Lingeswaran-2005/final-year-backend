import ipaddress
import re

from langchain_core.tools import tool
from src.tools.internal_tools.ssh_tools import execute

# Reuse your existing execute function.


def run_ip(
    args: list[str],
    session_id: str | None = None,
) -> str:
    """Execute an ip command locally or on a remote SSH server."""

    try:
        command = "ip " + " ".join(args)
        result = execute(command, session_id)

        if not isinstance(result, dict):
            return "ip error: Invalid response format from execution handler."

        if result.get("error"):
            return f"ip error: {result['error']}"

        exit_code = result.get("exit_code", -1)
        stderr = result.get("stderr", "").strip()
        stdout = result.get("stdout", "").strip()

        if exit_code != 0:
            return f"ip error: {stderr if stderr else 'Unknown execution error'}"

        return stdout or "ip command executed successfully."

    except Exception as e:
        return f"ip execution error: {str(e)}"


def validate_interface(interface: str) -> bool:
    """Validate a Linux network interface name."""
    return bool(
        interface
        and len(interface) <= 15
        and re.fullmatch(r"[a-zA-Z0-9_.:-]+", interface)
    )


def validate_ip(value: str) -> bool:
    """Validate an IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def validate_network(value: str) -> bool:
    """Validate an IP network with its prefix."""
    try:
        ipaddress.ip_network(value, strict=False)
        return "/" in value
    except ValueError:
        return False


def validate_address_prefix(value: str) -> bool:
    """Validate an IP address with a prefix."""
    try:
        ipaddress.ip_interface(value)
        return "/" in value
    except ValueError:
        return False


# ---------------------------------------------------------
# LINK
# ---------------------------------------------------------

@tool
def router_links(
    session_id: str | None = None,
) -> str:
    """Show all router interfaces and their link states."""

    return run_ip(["link", "show"], session_id)


router_links.metadata = {"readOnlyHint": True}


@tool
def router_enable_interface(
    interface: str,
    session_id: str | None = None,
) -> str:
    """Bring a router network interface up."""

    if not validate_interface(interface):
        return "ip error: Invalid interface name."

    return run_ip(["link", "set", interface, "up"], session_id)

router_enable_interface.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

@tool
def router_disable_interface(
    interface: str,
    session_id: str | None = None,
) -> str:
    """Bring a router network interface down."""

    if not validate_interface(interface):
        return "ip error: Invalid interface name."

    return run_ip(["link", "set", interface, "down"], session_id)

router_disable_interface.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

# ---------------------------------------------------------
# IP ADDRESSES
# ---------------------------------------------------------

@tool
def show_ip_addresses(
    session_id: str | None = None,
) -> str:
    """Show IP addresses configured on all router interfaces."""

    return run_ip(["addr", "show"], session_id)


show_ip_addresses.metadata = {"readOnlyHint": True}


@tool
def add_ip_address(
    address_prefix: str,
    interface: str,
    session_id: str | None = None,
) -> str:
    """Add an IP address and prefix to a router interface."""

    if not validate_address_prefix(address_prefix):
        return "ip error: Invalid IP address or prefix."

    if not validate_interface(interface):
        return "ip error: Invalid interface name."

    return run_ip(
        ["addr", "add", address_prefix, "dev", interface],
        session_id,
    )

add_ip_address.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

@tool
def delete_ip_address(
    address_prefix: str,
    interface: str,
    session_id: str | None = None,
) -> str:
    """Delete an IP address and prefix from a router interface."""

    if not validate_address_prefix(address_prefix):
        return "ip error: Invalid IP address or prefix."

    if not validate_interface(interface):
        return "ip error: Invalid interface name."

    return run_ip(
        ["addr", "del", address_prefix, "dev", interface],
        session_id,
    )

delete_ip_address.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

# ---------------------------------------------------------
# NEIGHBORS
# ---------------------------------------------------------

@tool
def router_neighbors(
    session_id: str | None = None,
) -> str:
    """Show the router's neighbor table."""

    return run_ip(["neigh", "show"], session_id)


router_neighbors.metadata = {"readOnlyHint": True}


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

@tool
def router_routes(
    session_id: str | None = None,
) -> str:
    """Show the router's IPv4 routing table."""

    return run_ip(["route", "show"], session_id)


router_routes.metadata = {"readOnlyHint": True}


@tool
def router_route_to_destination(
    destination_ip: str,
    session_id: str | None = None,
) -> str:
    """Show which route the router would use to reach an IP address."""

    if not validate_ip(destination_ip):
        return "ip error: Invalid destination IP address."

    return run_ip(["route", "get", destination_ip], session_id)


router_route_to_destination.metadata = {"readOnlyHint": True}


@tool
def router_add_route_via_gateway(
    network: str,
    gateway_ip: str,
    session_id: str | None = None,
) -> str:
    """Add a route to a network through a gateway."""

    if not validate_network(network):
        return "ip error: Invalid destination network or prefix."

    if not validate_ip(gateway_ip):
        return "ip error: Invalid gateway IP address."

    return run_ip(
        ["route", "add", network, "via", gateway_ip],
        session_id,
    )

router_add_route_via_gateway.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

@tool
def router_add_route_via_interface(
    network: str,
    interface: str,
    session_id: str | None = None,
) -> str:
    """Add a route to a network through a specified interface."""

    if not validate_network(network):
        return "ip error: Invalid destination network or prefix."

    if not validate_interface(interface):
        return "ip error: Invalid interface name."

    return run_ip(
        ["route", "add", network, "dev", interface],
        session_id,
    )
    
router_add_route_via_interface.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}


@tool
def router_delete_route(
    network: str,
    session_id: str | None = None,
) -> str:
    """Delete a route matching a destination network and prefix."""

    if not validate_network(network):
        return "ip error: Invalid destination network or prefix."

    return run_ip(["route", "del", network], session_id)

router_delete_route.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

@tool
def router_add_default_route(
    gateway_ip: str,
    session_id: str | None = None,
) -> str:
    """Add a default route through a gateway."""

    if not validate_ip(gateway_ip):
        return "ip error: Invalid gateway IP address."

    return run_ip(
        ["route", "add", "default", "via", gateway_ip],
        session_id,
    )
router_add_default_route.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}


@tool
def router_delete_default_route(
    session_id: str | None = None,
) -> str:
    """Delete the router's default route."""

    return run_ip(["route", "del", "default"], session_id)

router_delete_default_route.metadata = {
    "readOnlyHint": False,
    "destructiveHint": False,
}

# Tools marked read-only:
# router_links
# router_addresses
# router_interface_address
# router_neighbors
# router_interface_neighbors
# router_routes
# router_route_to_destination
