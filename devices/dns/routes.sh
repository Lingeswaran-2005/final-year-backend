#!/bin/sh
set -e

ip route replace 192.168.10.0/24 via 192.168.20.2

exec "$@"