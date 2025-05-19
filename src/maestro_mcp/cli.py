# Add lifespan support for startup/shutdown with strong typing
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP
from .logger import get_logger

from .maestro_cli import MaestroCli

logger = get_logger("maestro_mcp")

cli = MaestroCli(
    api_key=os.environ.get("MAESTRO_API_KEY", None),
    maestro_binary_path=os.environ.get("MAESTRO_BINARY_PATH", None),
    api_server=os.environ.get("MAESTRO_API_SERVER", "https://api.copilot.mobile.dev"),
)


@dataclass
class AppContext:
    maestro_cli: MaestroCli


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize on startup
    try:
        logger.info("Starting app")
        yield AppContext(cli)
    finally:
        # Cleanup on shutdown
        pass


# Pass lifespan to server
mcp = FastMCP("Maestro MCP", lifespan=app_lifespan, dependencies=["uv"])


@mcp.resource("https://maestro.dev/cheat-sheet")
def cheat_sheet() -> str:
    """
    A full cheat-sheet of the complete syntax for Maestro flow files.

    :return: a full cheat sheet of Maestro YAML syntax
    """
    try:
        return cli.cheat_sheet()
    except Exception as e:
        logger.error(e.__str__())
        return "Could not retrieve cheat sheet: " + e.__str__()


@mcp.tool()
def get_cheat_sheet(ctx: Context) -> str:
    """
    A full cheat-sheet of the complete syntax for Maestro flow files.

    IMPORTANT: Always call this function to load a summary of Maestro's syntax before using any of the other tools!

    :return: a full cheat sheet of Maestro YAML syntax
    """
    cli: MaestroCli = ctx.request_context.lifespan_context.maestro_cli
    try:
        return cli.cheat_sheet()
    except Exception as e:
        ctx.error(e.__str__())
        raise e


@mcp.tool()
def run_code(ctx: Context, flow_script: str):
    """
    Use this when interacting with a device and running adhoc commands, preferably one at a time.

    Whenever you're exploring an app, testing out commands or debugging, prefer using this tool over creating temp files and using run_flow_files.

    Run a set of Maestro commands (one or more). This can be a full maestro script (including headers), a set of commands (one per line) or simply a single command (eg '- tapOn: 123').

    If this fails due to no device running, please ask the user to start a device!

    If you don't have an up-to-date view hierarchy or screenshot on which to execute the commands, please call get_hierarchy first, instead of blindly guessing.

    *** You don't need to call check_syntax before executing this, as syntax will be checked as part of the execution flow. ***

    Use the `get_hierarchy` tool to retrieve the current view hierarchy and use it to execute commands on the device.
    Use the `cheat_sheet` tool to retrieve a summary of Maestro's syntax before using any of the other tools.

    Examples of valid inputs:
    ```
    - tapOn: 123
    ```

    ```
    appId: any
    ---
    - tapOn: 123
    ```

    ```
    appId: any
    # other headers here
    ---
    - tapOn: 456
    - scroll
    # other commands here
    ```

    :param flow_script: a maestro flow as a string.
    :return:
    """
    cli: MaestroCli = ctx.request_context.lifespan_context.maestro_cli

    try:
        logger.info(f"Executing code:\n\n{flow_script}")
        ctx.info(f"Executing code:\n\n{flow_script}")
        res = cli.run_code(flow_script)
        try:
            curr_hierarchy = cli.get_hierarchy()
            res += f"""

            Current view hierarchy:
            {curr_hierarchy}
            """
        except Exception:
            pass

        return res
    except Exception as e:
        ctx.error(e.__str__())
        raise e


@mcp.tool()
def run_flow_files(ctx: Context, flowFiles: str) -> str:
    """
    Run one or more full Maestro test files.

    If this fails due to no device running, please ask the user to start a device!

    Use the `cheat_sheet` tool to retrieve a summary of Maestro's syntax before writing any code.

    :param flowFiles: a space-delimited list of one or more flow files to test. e.g. "/path/to/flowFile1.yml /path/to/flowFile2.yml". 
    
    **Please provide the full path to the files**. 
    
    If there are spaces in the path, please enclose the path in quotes.
    
    :return: result of the flow execution
    """
    cli: MaestroCli = ctx.request_context.lifespan_context.maestro_cli

    try:
        res = cli.run_test(flowFiles)
        try:
            curr_hierarchy = cli.get_hierarchy()
            res += f"""

            Current view hierarchy:
            {curr_hierarchy}
            """
        except Exception:
            pass

        return res
    except Exception as e:
        logger.error(e.__str__())
        ctx.error(e.__str__())
        try:
            curr_hierarchy = cli.get_hierarchy()
            return f"""
            Execution failed with: {e.__str__()}

            Current view hierarchy:
            {curr_hierarchy}
            """
        except Exception:
            pass

        raise e


# @mcp.tool()
# def start_device(ctx: Context, os: str, platform: str) -> str:
#     """
#     Start a device for testing.

#     DO NOT USE THIS FUNCTION UNLESS THE USER EXPLICITLY REQUESTS IT.

#     :param os: the OS of the device. Supported values for iOS: 16, 17 or 18. Supported values for Android: 28, 29, 30, 31, 33
#     :param platform: the platform of the device. Supported values: android, ios
#     :return:
#     """
#     cli: MaestroCli = ctx.request_context.lifespan_context.maestro_cli
#     logger.info(f"Starting {platform} {os} device...")
#     ctx.info(f"Starting {platform} {os} device...")

#     try:
#         return cli.start_device(os, platform)
#     except Exception as e:
#         logger.error(e.__str__())
#         ctx.error(e.__str__())
#         raise e


@mcp.tool()
def get_hierarchy(ctx: Context) -> str:
    """
    Retrieves the view hierarchy of the currently visible screen.

    Use this to get a full view of what's currently visible on the device.

    You can use this to get names of parameters before writing code, debugging or when you're not sure what to do next.

    :return: a JSON of the full view hierarchy of the current screen on the device
    """
    cli: MaestroCli = ctx.request_context.lifespan_context.maestro_cli
    logger.info("Getting view hierarchy...")
    ctx.info("Getting view hierarchy...")

    try:
        return cli.get_hierarchy()
    except Exception as e:
        logger.error(e.__str__())
        ctx.error(e.__str__())
        raise e


@mcp.tool()
def query_docs(ctx: Context, query: str) -> str:
    """
    Queries the Maestro Documentation for instructions related to CLI, Cloud, Maestro Studio or Maestro language Syntax.

    You can include any free text search as well as relevant code blocks in the query.

    :param query: free text search query
    :return: responses according to the official documentation
    """
    cli: MaestroCli = ctx.request_context.lifespan_context.maestro_cli
    logger.info(f"Querying docs for '{query}'...")
    ctx.info(f"Querying docs for '{query}'...")

    try:
        return cli.query_docs("Search the Maestro documentation to answer the following question: " + query)
    except Exception as e:
        logger.error(e.__str__())
        ctx.error(e.__str__())
        raise e


@mcp.tool()
def check_syntax(ctx: Context, code: str) -> str:
    """
    Validates the syntax of a block of Maestro code.
    Valid maestro code must be well-formatted YAML.
    This tool will return an error message if the code is not valid or OK if it is.

    :param code: The maestro code to be validated
    :return: a syntax validation message or OK if code is valid
    """
    cli: MaestroCli = ctx.request_context.lifespan_context.maestro_cli
    logger.info("Checking syntax for %s", code)
    ctx.info("Checking syntax for %s", code)

    try:
        return cli.check_syntax(code)
    except Exception as e:
        logger.error(e.__str__())
        ctx.error(e.__str__())
        raise e


if __name__ == "__main__":
    mcp.run()
