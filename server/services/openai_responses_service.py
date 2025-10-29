from typing import List, Optional, Dict
from openai import OpenAI
from openai.types.responses import Response
from openai.types.responses.response_output_item import ResponseOutputItem
from openai.types.responses.response_input_item import Message
from openai.types.responses.response_output_message import ResponseOutputMessage
from openai.types.responses.response_function_call_output_item import ResponseFunctionCallOutputItem
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall

class ResponsesAPIService:
    """Service for interacting with OpenAI's Responses API"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def create_response(
        self,
        input_data: List[Message | ResponseOutputMessage],
        tools: Optional[List[Dict]],
        model: str,
        instructions: str,
        previous_response_id: Optional[str] = None,
    ) -> Response:
        """
        Create a response using OpenAI's Responses API.
        
        Args:
            input_data: List of messages in Responses API format
            tools: List of tool definitions
            model: Model to use (e.g., 'gpt-4o-mini')
            instructions: System instructions
            previous_response_id: ID of previous response for continuation
            
        Returns:
            Response object containing outputs and metadata
        """
        create_kwargs = {
            "model": model,
            "input": input_data,
            "instructions": instructions,
        }
        
        if tools:
            create_kwargs["tools"] = tools
            
        if previous_response_id:
            create_kwargs["previous_response_id"] = previous_response_id
        
        response = self.client.responses.create(**create_kwargs)
        return response
    
    def extract_text_from_output(self, output: ResponseOutputItem) -> Optional[str]:
        """Extract text content from a response output item"""
        if hasattr(output, 'content') and output.content:
            for item in output.content:
                if hasattr(item, 'text'):
                    return item.text
        return None
    
    def extract_function_calls(self, output: ResponseOutputItem) -> List[ResponseFunctionCallOutputItem]:
        """Extract function calls from a response output item"""
        if isinstance(output, ResponseFunctionCallOutputItem):
            return [output]
        return []
    
    def is_message_output(self, output: ResponseOutputItem) -> bool:
        """Check if output is a message output"""
        return hasattr(output, 'role') and hasattr(output, 'content')
    
    def is_function_call_output(self, output: ResponseOutputItem) -> bool:
        """Check if output is a function call output"""
        return isinstance(output, ResponseFunctionToolCall)
