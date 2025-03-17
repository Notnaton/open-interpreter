"""
Chat history component for the Open Interpreter GUI.

This module provides a scrollable view for displaying the message history
with efficient update mechanisms to avoid unnecessary redraws.
"""
from typing import List, Dict, Any, Optional
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.clock import Clock

from .message_bubble import MessageBubble
from ..utils.error_handler import gui_exception_handler

class ChatHistory(ScrollView):
    """ScrollView that displays the message history with efficient updating"""
    
    def __init__(self, **kwargs):
        """
        Initialize the chat history view.
        
        Args:
            **kwargs: Additional keyword arguments for ScrollView
        """
        super(ChatHistory, self).__init__(**kwargs)
        
        # Create the main layout for messages
        self.layout = GridLayout(
            cols=1, 
            spacing=dp(10), 
            padding=dp(10), 
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        
        # Keep track of the last message state to avoid unnecessary updates
        self.last_message_count = 0
        self.last_message_content = ""
    
    @gui_exception_handler()
    def update_messages(self, messages: List[Dict[str, Any]]) -> None:
        """
        Update the chat history with the latest messages.
        
        This method efficiently updates the chat history by only redrawing
        when necessary, such as when there are new messages or when the 
        content of existing messages has changed.
        
        Args:
            messages: List of message dictionaries to display
        """
        # Only redraw if there are new messages or content has changed
        current_count = len(messages)
        
        # Check if we need to redraw (new messages or content changed)
        need_redraw = current_count != self.last_message_count
        
        # If no new messages, check if content of last message changed
        if not need_redraw and current_count > 0 and self.last_message_count > 0:
            # Get the content of the last message for comparison
            last_content = self._get_message_content(messages[-1])
            need_redraw = last_content != self.last_message_content
        
        if need_redraw:
            # Clear existing widgets
            self.layout.clear_widgets()
            
            # Add message bubbles for each valid message
            for message in messages:
                if message.get("role") in ["user", "assistant", "system", "tool"]:
                    bubble = MessageBubble(message)
                    self.layout.add_widget(bubble)
            
            # Update tracking state
            self.last_message_count = current_count
            if current_count > 0:
                self.last_message_content = self._get_message_content(messages[-1])
            else:
                self.last_message_content = ""
                
            # Scroll to bottom after update
            self.scroll_to_bottom()
    
    def _get_message_content(self, message: Dict[str, Any]) -> str:
        """
        Extract a normalized string representation of message content for comparison.
        
        Args:
            message: The message dictionary
            
        Returns:
            String representation of the message content
        """
        content = message.get("content", "")
        
        # Handle content list
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return "\n".join(text_parts)
        
        # Convert to string if not already
        return str(content) if content is not None else ""
    
    def scroll_to_bottom(self, delay: float = 0.1) -> None:
        """
        Scroll to the bottom of the chat history.
        
        Args:
            delay: Optional delay before scrolling (in seconds)
        """
        if delay > 0:
            Clock.schedule_once(lambda dt: self._scroll_now(), delay)
        else:
            self._scroll_now()
    
    def _scroll_now(self) -> None:
        """Immediately scroll to the bottom of the chat history"""
        self.scroll_y = 0 