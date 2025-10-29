from typing import List, Dict, Any, Callable, Optional
from pydantic import BaseModel, Field
from openai.types.responses.response_input_item import Message
from openai.types.responses.response_output_message import ResponseOutputMessage
from openai.types.responses import ResponseFunctionToolCall, ResponseFunctionCallOutputItem, ResponseFunctionToolCall


from openai.types.responses.response_input_text import ResponseInputText
import json
import logging

from server.services.openai_responses_service import ResponsesAPIService    

logger = logging.getLogger(__name__)


class AgentTool(BaseModel):
    """Configuration for an agent tool"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


class AgentExecutionResult(BaseModel):
    """Result of agent execution"""
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="All messages processed")
    final_response: str = Field(default="", description="Final response text")
    error: Optional[str] = Field(None, description="Error message if any")
    iterations: int = Field(0, description="Number of iterations executed")


class WorkflowAgent:
    """Agent for executing workflows using OpenAI's Responses API"""
    
    def __init__(
        self,
        openai_service: ResponsesAPIService,
        model: str = "gpt-4o-mini",
        max_iterations: int = 20,
    ):
        self.openai_service = openai_service
        self.model = model
        self.max_iterations = max_iterations
    
    def execute(
        self,
        system_instructions: str,
        user_message: str,
        tools: List[AgentTool],
        tools_fn_map: Dict[str, Callable],
        on_message_callback: Optional[Callable] = None,
    ) -> AgentExecutionResult:
        """
        Execute agent loop with function calling.
        
        Args:
            system_instructions: System prompt for the agent
            user_message: Initial user message
            tools: List of tools available to the agent
            tools_fn_map: Map of tool names to callable functions
            on_message_callback: Optional callback for each message
            
        Returns:
            AgentExecutionResult with execution details
        """
        # Convert tools to OpenAI format
        tools_openai = [tool.to_openai_format() for tool in tools]
        
        # Build initial messages
        messages: List[Message | ResponseOutputMessage] = [
            Message(
                role="user",
                content=[ResponseInputText(text=user_message, type="input_text")]
            )
        ]
        
        all_messages = []
        iteration = 0
        final_response = ""
        
        try:
            while iteration < self.max_iterations:
                iteration += 1
                logger.info(f"Agent iteration {iteration}")
                
                # Get response from OpenAI
                response = self.openai_service.create_response(
                    input_data=messages,
                    tools=tools_openai if tools else None,
                    model=self.model,
                    instructions=system_instructions,
                )
                
                if not response:
                    error_msg = "Error getting response from OpenAI"
                    logger.error(error_msg)
                    return AgentExecutionResult(
                        messages=all_messages,
                        final_response="",
                        error=error_msg,
                        iterations=iteration
                    )
                
                # Process response outputs
                function_calls = []
                
                for output in response.output:
                    messages.append(output)
                    
                    # Handle message outputs
                    if self.openai_service.is_message_output(output):
                        text = self.openai_service.extract_text_from_output(output)
                        if text:
                            final_response = text
                            all_messages.append({
                                "role": "assistant",
                                "content": text
                            })
                            if on_message_callback:
                                on_message_callback(text)
                    
                    # Handle function call outputs
                    elif self.openai_service.is_function_call_output(output):
                        if isinstance(output, ResponseFunctionToolCall):
                            function_calls.append(output)
                
                # Execute function calls if any
                if function_calls:
                    logger.info(f"Processing {len(function_calls)} function calls")
                    
                    for func_call in function_calls:
                        tool_name = func_call.name
                        call_id = func_call.call_id
                        args_str = func_call.arguments if hasattr(func_call, 'arguments') else "{}"
                        
                        try:
                            args = json.loads(args_str) if isinstance(args_str, str) else args_str
                            logger.info(f"Executing function: {tool_name} with args: {args}")
                            
                            # Execute the function
                            if tool_name in tools_fn_map:
                                result = tools_fn_map[tool_name](**args)
                            else:
                                result = f"Function {tool_name} not found"
                                logger.error(f"Function {tool_name} not found in tools_fn_map")
                            
                            # Add function result to messages
                            function_output = ResponseFunctionToolCall(
                                call_id=call_id,
                                output=str(result),
                                type="function_call_output"
                            )
                            messages.append(function_output)
                            
                        except Exception as e:
                            error_msg = f"Error executing function {tool_name}: {str(e)}"
                            logger.error(error_msg, exc_info=True)
                            
                            function_output = ResponseFunctionToolCall(
                                call_id=call_id,
                                output=error_msg,
                                type="function_call_output"
                            )
                            messages.append(function_output)
                    
                    # Continue loop to process next iteration
                    continue
                else:
                    # No function calls, we're done
                    logger.info(f"Final response: {final_response}")
                    return AgentExecutionResult(
                        messages=all_messages,
                        final_response=final_response,
                        error=None,
                        iterations=iteration
                    )
            
            # Max iterations reached
            error_msg = "Maximum iterations reached"
            logger.warning(error_msg)
            return AgentExecutionResult(
                messages=all_messages,
                final_response=final_response,
                error=error_msg,
                iterations=iteration
            )
            
        except Exception as e:
            error_msg = f"Error in agent execution: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return AgentExecutionResult(
                messages=all_messages,
                final_response="",
                error=error_msg,
                iterations=iteration
            )
