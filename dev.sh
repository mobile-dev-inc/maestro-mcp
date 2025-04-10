#!/bin/bash
# Script to run the MCP in development mode

# Activate the poetry environment
poetry run mcp dev src/maestro_mcp/cli.py -e . "$@"
