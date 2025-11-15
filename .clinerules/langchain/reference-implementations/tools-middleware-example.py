"""
Tools middleware for providing tools to agents.

This middleware handles:
- Injecting tools into the agent
- Optionally injecting tool descriptions/guidance into system prompt
"""

import logging
from typing import List, Optional, Callable
from langchain_core.tools import BaseTool
from langchain.agents.middleware import AgentMiddleware

logger = logging.getLogger(__name__)


class ToolsMiddleware(AgentMiddleware):
    """
    Middleware to provide tools to an agent with optional system prompt guidance.
    
    This middleware:
    1. Makes tools available to the agent via the `tools` property
    2. Optionally injects tool usage guidance into the system prompt
    
    Example:
        ```python
        from rapid_ai.agents.middleware.custom.tools import ToolsMiddleware
        from rapid_ai.agents.tools.trss_tools import get_tool
        
        tools_middleware = ToolsMiddleware(
            tools=[
                get_tool("entity_risks", "langchain"),
                get_tool("events_data", "langchain")
            ],
            system_prompt="Use these tools to analyze entity risks and events..."
        )
        
        agent = create_agent(
            model=llm,
            middleware=[tools_middleware, ...],
            ...
        )
        ```
    
    Args:
        tools: List of tools to provide to the agent
        system_prompt: Optional guidance on how/when to use the tools
    """
    
    def __init__(
        self,
        tools: List[BaseTool],
        system_prompt: Optional[str] = None
    ):
        super().__init__()
        self._tools = tools
        self._system_prompt = system_prompt
        
        logger.debug(f"ToolsMiddleware initialized with {len(tools)} tools")
    
    @property
    def tools(self) -> List[BaseTool]:
        """Return the tools to be added to the agent."""
        return self._tools
    
    def wrap_model_call(self, request, handler):
        """Inject tool guidance into system prompt with {tools_list} variable support."""
        # Always generate the formatted tools list
        tools_list_items = []
        for tool in self._tools:
            tool_name = tool.name
            tool_description = tool.description or "No description available"
            # Remove any "Args:" sections from description if present
            if "Args:" in tool_description:
                tool_description = tool_description.split("Args:")[0].strip()
            tools_list_items.append(f"**{tool_name}**: {tool_description}")
        
        formatted_tools_list = "\n\n".join(tools_list_items)
        
        # Build the tools section
        if self._system_prompt is None:
            # No custom prompt - use default format
            tools_section = f"""=== Available Tools ===

You have access to the following tools:

{formatted_tools_list}"""
        else:
            # Custom prompt provided
            if "{tools_list}" in self._system_prompt:
                # Inject tools list into the placeholder
                tools_section = self._system_prompt.format(tools_list=formatted_tools_list)
            else:
                # No placeholder - append tools list to the bottom
                tools_section = f"""{self._system_prompt}

{formatted_tools_list}"""
        
        # Append to existing system prompt
        if tools_section:
            if request.system_prompt:
                request.system_prompt = (
                    request.system_prompt + "\n\n" + tools_section
                )
            else:
                request.system_prompt = tools_section
        
        return handler(request)
    
    async def awrap_model_call(self, request, handler):
        """Async version of wrap_model_call with {tools_list} variable support."""
        # Always generate the formatted tools list
        tools_list_items = []
        for tool in self._tools:
            tool_name = tool.name
            tool_description = tool.description or "No description available"
            # Remove any "Args:" sections from description if present
            if "Args:" in tool_description:
                tool_description = tool_description.split("Args:")[0].strip()
            tools_list_items.append(f"**{tool_name}**: {tool_description}")
        
        formatted_tools_list = "\n\n".join(tools_list_items)
        
        # Build the tools section
        if self._system_prompt is None:
            # No custom prompt - use default format
            tools_section = f"""=== Available Tools ===

You have access to the following tools:

{formatted_tools_list}"""
        else:
            # Custom prompt provided
            if "{tools_list}" in self._system_prompt:
                # Inject tools list into the placeholder
                tools_section = self._system_prompt.format(tools_list=formatted_tools_list)
            else:
                # No placeholder - append tools list to the bottom
                tools_section = f"""{self._system_prompt}

{formatted_tools_list}"""
        
        # Append to existing system prompt
        if tools_section:
            if request.system_prompt:
                request.system_prompt = (
                    request.system_prompt + "\n\n" + tools_section
                )
            else:
                request.system_prompt = tools_section
        
        return await handler(request)
