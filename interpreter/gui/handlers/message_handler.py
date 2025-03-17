"""
Message handler for the Open Interpreter GUI.

This module provides the logic for processing user messages and AI responses,
handling streaming, and managing the message state.
"""
import asyncio
import traceback
from typing import Dict, Any, Optional, Callable, List

from ..utils.error_handler import ErrorHandler, gui_exception_handler
from ..utils.async_helpers import AsyncHelper

class MessageHandler:
    """Handler for processing messages and responses in the GUI"""
    
    def __init__(self, interpreter, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the message handler.
        
        Args:
            interpreter: The interpreter instance to use
            status_callback: Optional callback function for status updates
        """
        self.interpreter = interpreter
        self.status_callback = status_callback
        self.chunk_buffer = ""
        self.message_streaming = False
    
    def update_status(self, status: str) -> None:
        """
        Update the status via the provided callback.
        
        Args:
            status: Status message to display
        """
        if self.status_callback:
            self.status_callback(status)
    
    @gui_exception_handler()
    def send_user_message(self, message: str) -> None:
        """
        Send a user message to the interpreter.
        
        Args:
            message: User message text
        """
        if not message.strip():
            return
            
        # Add user message to the interpreter's message history
        self.interpreter.messages.append({"role": "user", "content": message})
        
        # Start response processing in a separate thread
        self.message_streaming = True
        AsyncHelper.run_in_thread(self.process_response)
    
    @gui_exception_handler()
    def process_response(self) -> None:
        """Process the interpreter's response in a separate thread"""
        try:
            # Create event loop for asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Reset the chunk buffer
            self.chunk_buffer = ""
            
            # Prepare for assistant message
            assistant_idx = self._prepare_assistant_message()
            
            # Start streaming response
            try:
                # Get response chunks and process them
                for chunk in loop.run_until_complete(self._get_response()):
                    self._process_chunk(chunk, assistant_idx)
            
            except Exception as e:
                error_msg = f"Error during streaming: {str(e)}"
                ErrorHandler.log_error(e, "Error during response streaming")
                
                # Update message with error
                if assistant_idx >= 0 and assistant_idx < len(self.interpreter.messages):
                    current_content = self.interpreter.messages[assistant_idx].get("content", "")
                    self.interpreter.messages[assistant_idx]["content"] = f"{current_content}\n\n⚠️ {error_msg}"
                
            # Set status to "Ready" when done
            self.update_status("Ready")
            
        except Exception as e:
            # Handle any other errors in the thread
            error_msg = f"Thread error: {str(e)}"
            ErrorHandler.log_error(e, "Error in response processing thread")
            
            # Make sure we have a valid assistant message to update
            if len(self.interpreter.messages) > 0 and self.interpreter.messages[-1].get("role") != "assistant":
                self.interpreter.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})
            elif len(self.interpreter.messages) > 0:
                self.interpreter.messages[-1]["content"] = f"⚠️ {error_msg}"
            
            self.update_status("Error occurred")
        
        finally:
            self.message_streaming = False
    
    def _prepare_assistant_message(self) -> int:
        """
        Find or create an assistant message to update.
        
        Returns:
            The index of the assistant message
        """
        assistant_idx = -1
        
        # Look for an empty assistant message
        for i, msg in enumerate(self.interpreter.messages):
            if msg.get("role") == "assistant" and (not msg.get("content") or msg.get("content") == ""):
                assistant_idx = i
                break
        
        # Create a new assistant message if none exists
        if assistant_idx == -1:
            self.interpreter.messages.append({"role": "assistant", "content": ""})
            assistant_idx = len(self.interpreter.messages) - 1
            
        return assistant_idx
        
    async def _get_response(self):
        """
        Get the streaming response from the interpreter.
        
        Returns:
            An async generator yielding response chunks
        """
        try:
            # Call the interpreter's respond method
            response_generator = self.interpreter._sync_respond_stream()
            
            # Convert to a consistent async generator regardless of input type
            async for chunk in AsyncHelper.ensure_async_generator(response_generator):
                yield chunk
                
        except Exception as e:
            ErrorHandler.log_error(e, "Error getting response stream")
            # Return an empty result to avoid breaking the stream
            return
    
    def _process_chunk(self, chunk: Any, assistant_idx: int) -> None:
        """
        Process a response chunk from the LLM.
        
        Args:
            chunk: The response chunk
            assistant_idx: Index of the assistant message to update
        """
        # Check if choices and delta exist in the chunk
        if not hasattr(chunk, 'choices') or not chunk.choices:
            return
            
        # Handle content delta
        if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            self.chunk_buffer += content
            
            # Update the response content in the appropriate message
            self.interpreter.messages[assistant_idx]["content"] = self.chunk_buffer
    
    def get_message_safe_copy(self) -> List[Dict[str, Any]]:
        """
        Create a safe copy of the messages for UI display.
        
        Returns:
            A list of sanitized message dictionaries
        """
        # Create a safe copy, filtering any invalid messages
        messages_copy = []
        
        for msg in self.interpreter.messages:
            if isinstance(msg, dict) and "role" in msg:
                # Create a sanitized copy
                safe_msg = {"role": msg["role"]}
                
                # Handle content field safely
                if "content" in msg:
                    if msg["content"] is None:
                        safe_msg["content"] = ""
                    elif isinstance(msg["content"], list):
                        # Handle content list (common in OpenAI/Anthropic APIs)
                        safe_content = []
                        for item in msg["content"]:
                            if isinstance(item, dict) and "type" in item:
                                safe_content.append(item)
                        safe_msg["content"] = safe_content or ""
                    else:
                        safe_msg["content"] = str(msg["content"])
                else:
                    safe_msg["content"] = ""
                    
                messages_copy.append(safe_msg)
        
        return messages_copy 