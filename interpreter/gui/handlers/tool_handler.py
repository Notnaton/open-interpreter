"""
Tool handler for the Open Interpreter GUI.

This module provides functionality for handling tool calls from the
LLM, including parsing arguments, displaying status updates, and
managing tool execution.
"""
import json
from typing import Dict, Any, Optional, Callable

from ..utils.error_handler import ErrorHandler, gui_exception_handler

class ToolHandler:
    """Handler for tool calls in the GUI"""
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the tool handler.
        
        Args:
            status_callback: Optional callback function for status updates
        """
        self.status_callback = status_callback
        self.tool_call_in_progress = False
    
    def update_status(self, status: str) -> None:
        """
        Update the status via the provided callback.
        
        Args:
            status: Status message to display
        """
        if self.status_callback:
            self.status_callback(status)
    
    @gui_exception_handler()
    def handle_tool_call(self, tool_call: Any) -> None:
        """
        Handle a tool call from the LLM response.
        
        Args:
            tool_call: The tool call object from the LLM
        """
        if not tool_call or not hasattr(tool_call, "function") or not hasattr(tool_call.function, "name"):
            return
            
        try:
            self.tool_call_in_progress = True
            
            # Extract tool name
            tool_name = tool_call.function.name
            
            # Parse arguments
            tool_args = self._parse_tool_arguments(tool_call)
            
            # Update status with tool info
            tool_description = self._get_tool_description(tool_name, tool_args)
            self.update_status(tool_description)
            
        except Exception as e:
            ErrorHandler.log_error(e, "Error handling tool call")
        finally:
            self.tool_call_in_progress = False
    
    def _parse_tool_arguments(self, tool_call: Any) -> Dict[str, Any]:
        """
        Parse the arguments from a tool call.
        
        Args:
            tool_call: The tool call object
            
        Returns:
            Dictionary of parsed arguments
        """
        tool_args = {}
        
        if hasattr(tool_call.function, "arguments") and tool_call.function.arguments:
            try:
                # Parse arguments JSON
                args_str = tool_call.function.arguments
                if isinstance(args_str, str):
                    tool_args = json.loads(args_str)
            except Exception as e:
                ErrorHandler.log_error(e, f"Error parsing tool arguments: {tool_call.function.arguments}")
                
        return tool_args
    
    def _get_tool_description(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """
        Generate a user-friendly description of the tool being executed.
        
        Args:
            tool_name: Name of the tool
            tool_args: Tool arguments
            
        Returns:
            Human-readable description of the tool execution
        """
        # Format specific tools nicely
        if tool_name == "bash" and "command" in tool_args:
            return f"Running: {tool_args['command']}"
        elif tool_name == "python" and "code" in tool_args:
            return f"Running Python code"
        elif tool_name == "write_file" and "filename" in tool_args:
            return f"Writing to file: {tool_args['filename']}"
        elif tool_name == "read_file" and "filename" in tool_args:
            return f"Reading file: {tool_args['filename']}"
        
        # Generic fallback
        return f"Running: {tool_name}" 