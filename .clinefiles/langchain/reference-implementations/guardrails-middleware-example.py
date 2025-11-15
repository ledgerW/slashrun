"""Generalizable guardrails middleware for agent safety and content filtering."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, Type

if TYPE_CHECKING:
    from collections.abc import Awaitable

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticToolsParser
from pydantic import BaseModel

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
    hook_config,
)
from langgraph.runtime import Runtime

logger = logging.getLogger(__name__)


class GuardrailsMiddleware(AgentMiddleware):
    """
    Generalizable middleware for agent guardrails and content filtering.
    
    Provides two layers of protection:
    1. System Prompt Injection: Injects static guardrail rules into system prompts
    2. Output Content Filtering: Validates and corrects agent outputs using LLM-based validation
    
    This middleware can be configured for different agents by providing:
    - Static guardrail rules (always injected into system prompts)
    - Optional output filtering with custom validation prompts and schemas
    
    Example:
        ```python
        from rapid_ai.agents.middleware.custom.guardrails import GuardrailsMiddleware
        from langchain.agents import create_agent
        
        # Minimal - just prompt injection
        agent = create_agent(
            model="gpt-4o",
            middleware=[
                GuardrailsMiddleware(
                    system_prompt_rules=my_guardrails_string
                )
            ]
        )
        
        # Full - prompt injection + output filtering
        agent = create_agent(
            model="gpt-4o",
            middleware=[
                GuardrailsMiddleware(
                    system_prompt_rules=my_guardrails_string,
                    output_filter_system_prompt=filter_system_prompt,
                    output_filter_user_prompt=filter_user_prompt,
                    output_schema=MyValidationResultSchema,
                    validation_model=init_chat_model("gpt-4o-mini")
                )
            ],
            response_format=MyOutputSchema
        )
        ```
    
    Args:
        system_prompt_rules: Static guardrail rules to inject into system prompts.
            These rules will be appended to existing system prompts from other middleware.
        output_filter_system_prompt: Optional system prompt for output validation.
            Should describe the validation rules and what to check for.
        output_filter_user_prompt: Optional user prompt template for output validation.
            Should contain a {output_json} placeholder for the output to validate.
        output_schema: Optional Pydantic model for structured validation results.
            Should have a field containing the corrected output.
        validation_model: Optional separate model for validation (e.g., gpt-4o-mini for cost).
            If not provided, uses the agent's main model.
    """

    def __init__(
        self,
        *,
        system_prompt_rules: str,
        output_filter_system_prompt: Optional[str] = None,
        output_filter_user_prompt: Optional[str] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        validation_model: Optional[BaseChatModel] = None,
    ) -> None:
        """
        Initialize the GuardrailsMiddleware.
        
        For output filtering to be enabled, all three filtering parameters must be provided:
        - output_filter_system_prompt
        - output_filter_user_prompt
        - output_schema
        
        The validation_model is optional; if not provided, the agent's main model is used.
        """
        super().__init__()
        self.system_prompt_rules = system_prompt_rules
        
        # Validate output filtering configuration
        filtering_params = [
            output_filter_system_prompt,
            output_filter_user_prompt,
            output_schema,
        ]
        filtering_enabled = any(p is not None for p in filtering_params)
        
        if filtering_enabled and not all(p is not None for p in filtering_params):
            raise ValueError(
                "For output filtering, all three parameters must be provided: "
                "output_filter_system_prompt, output_filter_user_prompt, and output_schema"
            )
        
        self.output_filter_system_prompt = output_filter_system_prompt
        self.output_filter_user_prompt = output_filter_user_prompt
        self.output_schema = output_schema
        self.validation_model = validation_model
        self.filtering_enabled = filtering_enabled

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """
        Inject guardrail rules into system prompt before model invocation.
        
        Appends the guardrail rules to any existing system prompt from previous middleware.
        This ensures guardrails are always present while preserving other middleware prompts.
        """
        request.system_prompt = (
            request.system_prompt + "\n\n" + self.system_prompt_rules
            if request.system_prompt
            else self.system_prompt_rules
        )
        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """
        Inject guardrail rules into system prompt before model invocation (async version).
        
        Appends the guardrail rules to any existing system prompt from previous middleware.
        This ensures guardrails are always present while preserving other middleware prompts.
        """
        request.system_prompt = (
            request.system_prompt + "\n\n" + self.system_prompt_rules
            if request.system_prompt
            else self.system_prompt_rules
        )
        return await handler(request)

    def after_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """
        Validate and filter agent output using LLM-based validation (sync version).
        
        Only runs if output filtering is enabled (all filtering parameters provided).
        Uses the validation_model if provided, otherwise uses the agent's main model.
        
        Validates either:
        - The structured_output key in state (if present and matches output_schema)
        - The last AI message content (fallback)
        
        Returns:
            None if validation passes or filtering disabled
            Dict with updated state if validation fails (corrects or rejects output)
        """
        if not self.filtering_enabled:
            return None
        
        # Try to get structured response from state first
        output_to_validate = None
        using_structured_output = False
        
        if "structured_response" in state and state["structured_response"] is not None:
            # Validate structured response from state
            output_to_validate = state["structured_response"]
            using_structured_output = True
        else:
            # Fallback to last message content
            if not state["messages"]:
                return None

            last_message = state["messages"][-1]
            if not isinstance(last_message, AIMessage):
                return None
            
            # Skip if no content to validate
            if not last_message.content:
                return None
            
            output_to_validate = last_message.content
        
        try:
            # Prepare output for validation
            if hasattr(output_to_validate, 'model_dump_json'):
                # Pydantic model
                output_json = output_to_validate.model_dump_json(indent=2)
            elif isinstance(output_to_validate, str):
                # Already a string
                output_json = output_to_validate
            else:
                # Convert to JSON string
                import json
                output_json = json.dumps(output_to_validate, indent=2)
            
            user_prompt = self.output_filter_user_prompt.format(output_json=output_json)
            
            # Use validation model or agent's model
            model = self.validation_model if self.validation_model else runtime.model
            
            # Set up structured output parsing
            tools = [self.output_schema]
            bound_model = model.bind_tools(tools)
            parser = PydanticToolsParser(tools=tools)
            
            # Invoke validation
            messages = [
                SystemMessage(content=self.output_filter_system_prompt),
                HumanMessage(content=user_prompt),
            ]
            
            result = bound_model.invoke(messages)
            parsed_result = parser.invoke(result)
            
            if not parsed_result:
                logger.warning("Output filter returned no results, allowing original output")
                return None
            
            validation_result = parsed_result[0]
            
            # Check if violations were found and corrected
            # Assumes validation schema has a 'violations_found' or similar field
            violations_found = getattr(validation_result, "violations_found", False)
            
            if violations_found:
                # Get corrected output
                corrected_output = getattr(validation_result, "corrected_output", None)
                corrections_made = getattr(validation_result, "corrections_made", "Unknown corrections")
                
                logger.info(f"Output filter applied corrections: {corrections_made}")
                
                # Return corrected output
                if corrected_output:
                    if using_structured_output:
                        # Update structured_response in state
                        return {
                            "structured_response": corrected_output
                        }
                    else:
                        # Update last message
                        corrected_json = corrected_output.model_dump_json(indent=2)
                        return {
                            "messages": [
                                AIMessage(content=corrected_json)
                            ]
                        }
            else:
                logger.debug("Output filter found no violations")
            
            return None
            
        except Exception as e:
            # Log the error with full details for debugging
            logger.error(f"Error in output filter: {str(e)}", exc_info=True)
            logger.warning("Returning original output due to filter error")
            
            # Explicitly return the original state to ensure the agent continues
            # This prevents the endpoint from hanging on validation errors
            if using_structured_output:
                return {
                    "structured_response": output_to_validate
                }
            else:
                # Return the original last message
                return {
                    "messages": [state["messages"][-1]]
                }

    async def aafter_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """
        Validate and filter agent output using LLM-based validation (async version).
        
        Only runs if output filtering is enabled (all filtering parameters provided).
        Uses the validation_model if provided, otherwise uses the agent's main model.
        
        Validates either:
        - The structured_output key in state (if present and matches output_schema)
        - The last AI message content (fallback)
        
        Returns:
            None if validation passes or filtering disabled
            Dict with updated state if validation fails (corrects or rejects output)
        """
        if not self.filtering_enabled:
            return None
        
        # Try to get structured response from state first
        output_to_validate = None
        using_structured_output = False
        
        if "structured_response" in state and state["structured_response"] is not None:
            # Validate structured response from state
            output_to_validate = state["structured_response"]
            using_structured_output = True
        else:
            # Fallback to last message content
            if not state["messages"]:
                return None

            last_message = state["messages"][-1]
            if not isinstance(last_message, AIMessage):
                return None
            
            # Skip if no content to validate
            if not last_message.content:
                return None
            
            output_to_validate = last_message.content
        
        try:
            # Prepare output for validation
            if hasattr(output_to_validate, 'model_dump_json'):
                # Pydantic model
                output_json = output_to_validate.model_dump_json(indent=2)
            elif isinstance(output_to_validate, str):
                # Already a string
                output_json = output_to_validate
            else:
                # Convert to JSON string
                import json
                output_json = json.dumps(output_to_validate, indent=2)
            
            user_prompt = self.output_filter_user_prompt.format(output_json=output_json)
            
            # Use validation model or agent's model
            model = self.validation_model if self.validation_model else runtime.model
            
            # Set up structured output parsing
            tools = [self.output_schema]
            bound_model = model.bind_tools(tools)
            parser = PydanticToolsParser(tools=tools)
            
            # Invoke validation
            messages = [
                SystemMessage(content=self.output_filter_system_prompt),
                HumanMessage(content=user_prompt),
            ]
            
            result = await bound_model.ainvoke(messages)
            parsed_result = parser.invoke(result)
            
            if not parsed_result:
                logger.warning("Output filter returned no results, allowing original output")
                return None
            
            validation_result = parsed_result[0]
            
            # Check if violations were found and corrected
            # Assumes validation schema has a 'violations_found' or similar field
            violations_found = getattr(validation_result, "violations_found", False)
            
            if violations_found:
                # Get corrected output
                corrected_output = getattr(validation_result, "corrected_output", None)
                corrections_made = getattr(validation_result, "corrections_made", "Unknown corrections")
                
                logger.info(f"Output filter applied corrections: {corrections_made}")
                
                # Return corrected output
                if corrected_output:
                    if using_structured_output:
                        # Update structured_response in state
                        return {
                            "structured_response": corrected_output
                        }
                    else:
                        # Update last message
                        corrected_json = corrected_output.model_dump_json(indent=2)
                        return {
                            "messages": [
                                AIMessage(content=corrected_json)
                            ]
                        }
            else:
                logger.debug("Output filter found no violations")
            
            return None
            
        except Exception as e:
            # Log the error with full details for debugging
            logger.error(f"Error in output filter: {str(e)}", exc_info=True)
            logger.warning("Returning original output due to filter error")
            
            # Explicitly return the original state to ensure the agent continues
            # This prevents the endpoint from hanging on validation errors
            if using_structured_output:
                return {
                    "structured_response": output_to_validate
                }
            else:
                # Return the original last message
                return {
                    "messages": [state["messages"][-1]]
                }
