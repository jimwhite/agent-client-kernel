#!/usr/bin/env bash
# Thin shell shim that calls the Python gateway next to this file.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/acp_gateway.py" "$@"
