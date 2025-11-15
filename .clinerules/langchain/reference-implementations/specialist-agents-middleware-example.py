"""
Specialist agents middleware for manager-worker delegation patterns.

This middleware handles:
- Creating assignment tools for each specialist agent
- Injecting specialist descriptions into system prompt
- Extending state with specialist_histories tracking
- Formatting specialist responses via optional formatter functions
"""

import json
import logging
from typing import List, Dict, Any, Optional, Callable, Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langchain.tools import ToolRuntime
from langchain.agents.middleware import AgentMiddleware
from langgraph.types import Command
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from .models import SpecialistHistoriesState

logger = logging.getLogger(__name__)


class SpecialistAgentsMiddleware(AgentMiddleware):
    """
    Middleware to enable manager agents to delegate to specialist agents.
    
    This middleware:
    1. Creates `assign_to_{name}` tools for each specialist
    2. Injects specialist descriptions into the manager's system prompt
    3. Extends state schema to track specialist conversation histories
    4. Formats specialist responses using optional formatter functions
    
    Example:
        ```python
        from rapid_ai.agents.middleware.custom.specialist_agents import SpecialistAgentsMiddleware
        
        def format_specialist_response(structured_response, specialist_name):
            return f"# {specialist_name} Report\\n{structured_response.executive_summary}"
        
        specialists = [
            {
                "agent": risk_agent,
                "name": "risk_assessment",
                "description": "Identifies and evaluates entity-specific risks...",
                "formatter": format_specialist_response
            },
            {
                "agent": supply_chain_agent,
                "name": "supply_chain",
                "description": "Examines supply chain relationships...",
                "formatter": None  # Will use default formatting
            }
        ]
        
        specialist_middleware = SpecialistAgentsMiddleware(specialists=specialists)
        
        manager = create_agent(
            model=llm,
            middleware=[specialist_middleware, ...],
            ...
        )
        ```
    
    Args:
        specialists: List of specialist configurations, each with:
            - agent: CompiledStateGraph - The specialist agent to invoke
            - name: str - Specialist name (e.g., "risk_assessment")
            - description: str - Description for tool prompting
            - formatter: Optional[Callable] - Function to format structured response.
                Signature: (structured_response: BaseModel, specialist_name: str) -> str
                If None, returns raw structured response if present, else last message.
    """
    
    state_schema = SpecialistHistoriesState
    
    def __init__(self, specialists: List[Dict[str, Any]]):
        super().__init__()
        self.specialists = specialists
        self._tools = []
        
        # Create assignment tools for each specialist
        for specialist_config in specialists:
            agent = specialist_config["agent"]
            name = specialist_config["name"]
            description = specialist_config["description"]
            formatter = specialist_config.get("formatter", None)
            
            # Create the assignment tool
            assignment_tool = self._create_assignment_tool(
                specialist_agent=agent,
                specialist_name=name,
                description=description,
                formatter=formatter
            )
            self._tools.append(assignment_tool)
        
        logger.debug(f"SpecialistAgentsMiddleware initialized with {len(self._tools)} specialists")
    
    @property
    def tools(self):
        """Return the assignment tools to be added to the manager agent."""
        return self._tools
    
    def wrap_model_call(self, request, handler):
        """Inject specialist descriptions into system prompt."""
        # Build specialist descriptions section
        specialist_section = "\n\n=== Available Specialists ===\n\n"
        specialist_section += "You can delegate tasks to specialized team members:\n\n"
        
        specialists_list = []
        for specialist_config in self.specialists:
            name = specialist_config["name"]
            description = specialist_config["description"]
            agent = specialist_config["agent"]
            
            # Format specialist name for display
            display_name = name.replace('_', ' ').title()
            
            # Get tool names from the specialist agent if possible
            tool_names = []
            if hasattr(agent, 'nodes') and 'agent' in agent.nodes:
                # Try to extract tools from the compiled agent
                agent_node = agent.nodes['agent']
                if hasattr(agent_node, 'tools'):
                    tool_names = [t.name for t in agent_node.tools]
            
            # Build specialist entry
            specialist_entry = (
                f"**{display_name}** (`assign_to_{name}`)\n"
                f"{description}"
            )
            
            if tool_names:
                specialist_entry += f"\nTools: {', '.join(tool_names)}"
            
            specialists_list.append(specialist_entry)
        
        specialist_section += "\n\n".join(specialists_list)
        
        specialist_section += """\n\n**IMPORTANT: Tool Usage**:
⚠️ Be cautious about calling more than 2 specialists at once. Too many simultaneous calls can overwhelm processing and lead to timeouts or errors. Call tools strategically and wait for results before proceeding."""
        
        # Append to existing system prompt
        if request.system_prompt:
            request.system_prompt = request.system_prompt + specialist_section
        else:
            request.system_prompt = specialist_section
        
        return handler(request)
    
    async def awrap_model_call(self, request, handler):
        """Async version of wrap_model_call."""
        # Build specialist descriptions section
        specialist_section = "\n\n=== Available Specialists ===\n\n"
        specialist_section += "You can delegate tasks to specialized team members:\n\n"
        
        specialists_list = []
        for specialist_config in self.specialists:
            name = specialist_config["name"]
            description = specialist_config["description"]
            agent = specialist_config["agent"]
            
            # Format specialist name for display
            display_name = name.replace('_', ' ').title()
            
            # Get tool names from the specialist agent if possible
            tool_names = []
            if hasattr(agent, 'nodes') and 'agent' in agent.nodes:
                # Try to extract tools from the compiled agent
                agent_node = agent.nodes['agent']
                if hasattr(agent_node, 'tools'):
                    tool_names = [t.name for t in agent_node.tools]
            
            # Build specialist entry
            specialist_entry = (
                f"**{display_name}** (`assign_to_{name}`)\n"
                f"{description}"
            )
            
            if tool_names:
                specialist_entry += f"\nTools: {', '.join(tool_names)}"
            
            specialists_list.append(specialist_entry)
        
        specialist_section += "\n\n".join(specialists_list)
        
        specialist_section += """\n\n**IMPORTANT: Tool Usage**:
⚠️ Be cautious about calling more than 2 specialists at once. Too many simultaneous calls can overwhelm processing and lead to timeouts or errors. Call tools strategically and wait for results before proceeding."""
        
        # Append to existing system prompt
        if request.system_prompt:
            request.system_prompt = request.system_prompt + specialist_section
        else:
            request.system_prompt = specialist_section
        
        return await handler(request)
    
    def _create_assignment_tool(
        self,
        specialist_agent: CompiledStateGraph,
        specialist_name: str,
        description: str,
        formatter: Optional[Callable[[BaseModel, str], str]] = None
    ):
        """
        Create an assignment tool for a specialist agent.
        
        This is based on the agent_assignment_tool pattern but integrated
        into middleware for better composability.
        """
        
        @tool(
            f"assign_to_{specialist_name}",
            description=description
        )
        async def assign_task(
            task: Annotated[str, "The specific task or question for the specialist"],
            runtime: ToolRuntime,
            tool_call_id: Annotated[str, InjectedToolCallId]
        ):
            """Assign a task to a specialist agent."""
            try:
                # Get manager context from runtime
                manager_context = runtime.context
                
                # Create a simple namespace object with all manager fields plus specialist_name
                # This works with any context schema as long as specialist expects specialist_name
                from types import SimpleNamespace
                from dataclasses import fields
                
                # Copy all fields from manager context
                context_dict = {
                    f.name: getattr(manager_context, f.name)
                    for f in fields(manager_context)
                }
                
                # Add specialist_name
                context_dict["specialist_name"] = specialist_name
                
                # Create context object
                specialist_context = SimpleNamespace(**context_dict)
                
                # Get current state to count specialist calls
                state = runtime.state
                specialist_histories = state.get("specialist_histories", {})
                
                # Count previous calls to this specialist
                call_count = sum(1 for key in specialist_histories if key.startswith(f"{specialist_name}_"))
                call_number = call_count + 1
                history_key = f"{specialist_name}_{call_number}"
                
                # Invoke specialist with task only (no conversation history)
                result = await specialist_agent.ainvoke(
                    input={
                        "messages": [{"role": "user", "content": task}]
                    },
                    context=specialist_context,
                    config={"recursion_limit": 100}
                )
                
                # Get specialist messages for history
                specialist_messages = result["messages"]
                
                # Format the response
                if formatter:
                    # Use custom formatter if provided
                    structured_response = result.get("structured_response")
                    if structured_response:
                        formatted_content = formatter(structured_response, specialist_name)
                    else:
                        # Fallback to last message if no structured response
                        formatted_content = specialist_messages[-1].content
                else:
                    # Default formatting
                    structured_response = result.get("structured_response")
                    if structured_response:
                        # Return structured response as JSON
                        formatted_content = json.dumps(
                            structured_response.dict() if hasattr(structured_response, 'dict') else structured_response,
                            indent=2
                        )
                    else:
                        # Return last message content
                        formatted_content = specialist_messages[-1].content
                
                # Create success tool message
                tool_message = ToolMessage(
                    content=formatted_content,
                    name=f"assign_to_{specialist_name}",
                    tool_call_id=tool_call_id
                )
                
                # Return Command updating both messages and specialist_histories
                return Command(update={
                    "messages": [tool_message],
                    "specialist_histories": {
                        history_key: specialist_messages
                    }
                })
                
            except Exception as e:
                # Error handling: return error message with retry suggestion
                logger.error(f"Error executing {specialist_name} specialist: {e}", exc_info=True)
                error_message = (
                    f"Error executing {specialist_name} specialist: {str(e)}\n\n"
                    f"Suggestion: You may want to retry with a more specific task or try a different specialist."
                )
                
                return ToolMessage(
                    content=error_message,
                    name=f"assign_to_{specialist_name}",
                    tool_call_id=tool_call_id
                )
        
        return assign_task
