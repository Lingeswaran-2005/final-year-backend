from src.tools.internal_tools.ssh_tools import connect , disconnect , execute
from src.tools.internal_tools.network_tools import ping , curl , traceroute , dig
from src.tools.internal_tools.firewall_tools import firewall_allow_port , firewall_deny_port , firewall_status ,firewall_allow_icmp , firewall_block_icmp , firewall_delete_rule , firewall_flush , firewall_set_default_policy
from src.tools.internal_tools.router_tools import (
    router_links,
    router_enable_interface,
    router_disable_interface,
    show_ip_addresses,
    add_ip_address,
    delete_ip_address,
    router_neighbors,
    router_routes,
    router_route_to_destination,
    router_add_route_via_gateway,
    router_add_route_via_interface,
    router_delete_route,
    router_add_default_route,
    router_delete_default_route,
)
SSH_TOOLS = [connect , disconnect]

NETWORK_TOOLS = [ping , curl , traceroute , dig]

FIREWALL_TOOLS = [
    firewall_status , 
    firewall_allow_port , 
    firewall_deny_port,
    firewall_allow_icmp,
    firewall_block_icmp,
    firewall_delete_rule,
    firewall_flush,
    firewall_set_default_policy
    ]

ROUTER_TOOLS = [
    router_links,
    router_enable_interface,
    router_disable_interface,
    show_ip_addresses,
    add_ip_address,
    delete_ip_address,
    router_neighbors,
    router_routes,
    router_route_to_destination,
    router_add_route_via_gateway,
    router_add_route_via_interface,
    router_delete_route,
    router_add_default_route,
    router_delete_default_route,
]

INTERNAL_TOOLS = SSH_TOOLS + NETWORK_TOOLS + FIREWALL_TOOLS + ROUTER_TOOLS