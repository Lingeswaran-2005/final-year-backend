from src.tools.internal_tools.ssh_tools import connect , disconnect , execute
from src.tools.internal_tools.network_tools import ping , curl , traceroute , dig
from src.tools.internal_tools.firewall_tools import firewall_allow_port , firewall_deny_port , firewall_status ,firewall_allow_icmp , firewall_block_icmp , firewall_delete_rule , firewall_flush , firewall_set_default_policy

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

INTERNAL_TOOLS = SSH_TOOLS + NETWORK_TOOLS + FIREWALL_TOOLS