"""FastMCP Server for akd-ext tools."""

from fastmcp import FastMCP

from akd_ext.mcp.registry import MCPToolRegistry
from akd_ext.mcp.converter import tool_converter, register_mcp_tool
from akd.tools._base import BaseTool

# Create MCP server
mcp = FastMCP("akd-ext-tools")


def register_all_tools():
    """
    Auto-discover and register all @mcp_tool decorated classes.

    This function imports the tools module to trigger decorator registration,
    then converts and registers each tool with the FastMCP server.

    Example:
        register_all_tools()
    """
    # Import tools module to trigger @mcp_tool decorator registration
    # This must be done inside the function to avoid circular imports
    import akd_ext.tools  # noqa: F401

    # Get all registered tool classes from singleton registry
    tool_classes = MCPToolRegistry().get_tools()

    for tool_class in tool_classes:
        tool = tool_class()
        # Convert tool to FastMCP compatible function
        mcp_func = tool_converter(tool)
        # Register tool with FastMCP server
        register_mcp_tool(mcp_func, mcp)


def register_tools_manually(tools: list[type[BaseTool]]) -> None:
    """
    Register tools manually without @mcp_tool decorator.

    Args:
        tools: List of BaseTool subclasses to register.

    Example:
        register_tools_manually(tools=[ReverseTool, InternalTool])
    """
    for tool_class in tools:
        tool = tool_class()
        mcp_func = tool_converter(tool)
        register_mcp_tool(mcp_func, mcp)


register_all_tools()
# register_tools_manually(tools=[])  # Add tools here if needed


def main(
    transport: str | None = None,
    host: str | None = None,
    port: int | None = None,
) -> None:
    """Run the MCP server. Callable entrypoint for deploy tools."""
    import os

    resolved_transport = transport or os.getenv("MCP_TRANSPORT", "stdio")
    resolved_host = host or os.getenv("MCP_HOST", "127.0.0.1")
    resolved_port = port if port is not None else int(os.getenv("MCP_PORT", "8000"))

    if resolved_transport == "sse":
        mcp.run(transport="sse", host=resolved_host, port=resolved_port)
    else:
        mcp.run()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run akd-ext MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=None,
        help="Transport type (default: MCP_TRANSPORT env var or stdio)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind to for SSE (default: MCP_HOST env var or 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for SSE transport (default: MCP_PORT env var or 8000)",
    )
    args = parser.parse_args()
    main(transport=args.transport, host=args.host, port=args.port)
