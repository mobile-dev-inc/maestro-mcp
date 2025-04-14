#!/usr/bin/env python3
"""
Entry point script for running the MCP server during development.
Run with: uv run mcp.py
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Now run the module
from maestro_mcp.cli import mcp

if __name__ == "__main__":
    mcp.run()
