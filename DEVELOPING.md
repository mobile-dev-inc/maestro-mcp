## Development

This project uses `uv` for dependency management.

### Using UV

Install `uv` globally:

```bash
brew install uv
```

To install dependencies, run:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
uv pip install -e ".[dev]"
```

To run the application, use:

```bash
uv run --with "mcp[cli]" --with "requests" mcp run src/maestro_mcp/cli.py
```

## Configuring the MCP on Claude, Windsurf, etc

Include the following on Claude's config file:

```
{
  "mcpServers": {
    "maestro": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "uv",
        "--with",
        "requests",
        "mcp",
        "run",
        "<full path to mcp.py>"
      ],
      "env": {
        "MAESTRO_BINARY_PATH": "<path to the maestro executable - usually ~/.maestro/bin/maestro>",
        "MAESTRO_API_KEY": "<your maestro api key - you can get this from your maestro.dev account. It'll be automatically looked up after you run `maestro login`>"
      }
    }
  }
}
```

Install locally with:

```
 uv run --with "mcp[cli]" mcp install -v MAESTRO_API_KEY="<your api key>" -v MAESTRO_BINARY_PATH="~/.maestro/bin/maestro" mcp.py
```

### Building locally

To build the MCP, run:

```bash
rf -rf dist/
uv build
```

Install the local build with:

```bash
pip uninstall -y maestro-mcp
pip install dist/*.whl
```

