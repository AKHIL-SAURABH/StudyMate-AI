"""
StudyMate AI — MCP Client.

Connects to the MCP server via stdio transport, dynamically discovers
available tools, and provides tool invocation capabilities.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from backend.config import get_settings
from backend.exceptions import MCPConnectionError, MCPToolNotFoundError, ToolExecutionError
from utils.logger import get_logger

logger = get_logger("mcp_client")


class MCPClient:
    """Client for interacting with the MCP server."""

    def __init__(self) -> None:
        self._tools: list[dict[str, Any]] = []
        self._tools_discovered: bool = False

    def _get_server_params(self) -> StdioServerParameters:
        """Get MCP server connection parameters."""
        settings = get_settings()
        server_path = settings.mcp_server_path

        return StdioServerParameters(
            command=sys.executable,
            args=[server_path],
            env=None,
        )

    async def discover_tools(self) -> list[dict[str, Any]]:
        """
        Discover all available tools from the MCP server.

        Connects to the MCP server, lists tools, and caches the result.

        Returns:
            List of tool descriptors with name, description, and input schema.

        Raises:
            MCPConnectionError: If connection to MCP server fails.
        """
        try:
            server_params = self._get_server_params()

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    tools_result = await session.list_tools()

                    self._tools = []
                    for tool in tools_result.tools:
                        tool_info = {
                            "name": tool.name,
                            "description": tool.description or "",
                            "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                        }
                        self._tools.append(tool_info)

                    self._tools_discovered = True
                    logger.info(
                        "Discovered %d MCP tools: %s",
                        len(self._tools),
                        [t["name"] for t in self._tools],
                    )

            return self._tools

        except Exception as exc:
            logger.error("Failed to discover MCP tools: %s", exc)
            raise MCPConnectionError(f"Tool discovery failed: {exc}") from exc

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        Call an MCP tool by name with the given arguments.

        Args:
            tool_name: Name of the tool to invoke.
            arguments: Dictionary of arguments matching the tool's input schema.

        Returns:
            Tool output as a string.

        Raises:
            MCPToolNotFoundError: If the tool doesn't exist.
            ToolExecutionError: If tool execution fails.
        """
        try:
            server_params = self._get_server_params()

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    logger.info("Calling MCP tool: %s with args: %s", tool_name, json.dumps(arguments)[:200])

                    result = await session.call_tool(tool_name, arguments)

                    # Extract text content from result
                    output_text = ""
                    if result.content:
                        for content_block in result.content:
                            if hasattr(content_block, "text"):
                                output_text += content_block.text

                    if hasattr(result, "isError") and result.isError:
                        raise ToolExecutionError(tool_name, f"Tool returned error: {output_text}")

                    logger.info("Tool %s returned %d chars", tool_name, len(output_text))
                    return output_text

        except (MCPToolNotFoundError, ToolExecutionError):
            raise
        except Exception as exc:
            logger.error("MCP tool call failed (%s): %s", tool_name, exc)
            raise ToolExecutionError(tool_name, str(exc)) from exc

    def get_tools_description(self) -> str:
        """
        Format discovered tools as a readable description for the LLM.

        Returns:
            Formatted string listing all tools with descriptions and parameters.
        """
        if not self._tools:
            return "No tools available."

        lines = []
        for tool in self._tools:
            name = tool["name"]
            desc = tool["description"]
            schema = tool.get("input_schema", {})
            params = schema.get("properties", {})
            required = schema.get("required", [])

            param_strs = []
            for param_name, param_info in params.items():
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                req_marker = " (required)" if param_name in required else " (optional)"
                param_strs.append(f"    - {param_name} ({param_type}){req_marker}: {param_desc}")

            params_text = "\n".join(param_strs) if param_strs else "    No parameters"
            lines.append(f"### {name}\n{desc}\n  Parameters:\n{params_text}\n")

        return "\n".join(lines)

    def get_tools_list_for_prompt(self) -> str:
        """
        Get a concise tool list for the tool calling prompt.

        Returns:
            Simple formatted list of tool names and descriptions.
        """
        if not self._tools:
            return "No tools available."

        lines = []
        for tool in self._tools:
            schema = tool.get("input_schema", {})
            params = list(schema.get("properties", {}).keys())
            params_str = ", ".join(params) if params else "none"
            lines.append(f"- **{tool['name']}**({params_str}): {tool['description']}")

        return "\n".join(lines)

    @property
    def tools(self) -> list[dict[str, Any]]:
        """Get the cached list of discovered tools."""
        return self._tools


# Singleton instance
mcp_client = MCPClient()
