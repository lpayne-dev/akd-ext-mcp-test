"""FastMCP Server for akd-ext tools."""

from fastmcp import FastMCP

from akd_ext import tools
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

if __name__ == "__main__":
    mcp.run()
