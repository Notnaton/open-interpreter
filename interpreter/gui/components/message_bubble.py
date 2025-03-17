"""
Message bubble component for the Open Interpreter GUI.

This module provides a custom widget for displaying chat messages
with different styling based on the role (user, assistant, etc.).
"""
from typing import Dict, Any, List, Union
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, DictProperty

from ..utils.styling import get_color, COLORS

class MessageBubble(BoxLayout):
    """A custom widget for displaying chat messages with appropriate styling"""
    
    role = StringProperty("")
    content_text = StringProperty("")
    message = DictProperty({})
    
    def __init__(self, message: Dict[str, Any], **kwargs):
        """
        Initialize a message bubble with the provided message data.
        
        Args:
            message: Dict containing message data with role and content
            **kwargs: Additional keyword arguments for BoxLayout
        """
        super(MessageBubble, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(10)
        self.spacing = dp(5)
        self.message = message
        self.content_text = ""
        
        # Extract role from message
        self.role = message.get("role", "")
        
        # Create the UI
        self._create_ui()
        
        # Update height based on children
        self.bind(minimum_height=self.setter('height'))
        self.height = self.minimum_height
    
    def _create_ui(self) -> None:
        """Create the UI components for displaying the message"""
        # Add role label
        role_label = Label(
            text=self.role.upper(),
            size_hint_y=None,
            height=dp(20),
            color=get_color(COLORS["text_light"]),
            halign='left',
            valign='top',
            font_size=dp(12),
            bold=True
        )
        role_label.bind(size=role_label.setter('text_size'))
        self.add_widget(role_label)
        
        # Process content
        content = self._process_content()
        self.content_text = content
        
        # Create content label
        content_label = Label(
            text=content,
            size_hint_y=None,
            color=get_color(COLORS["text"]),
            halign='left',
            valign='top',
            padding_x=dp(10),
            padding_y=dp(10),
            text_size=(self.width - dp(40), None)  # Constrain width for text wrapping
        )
        
        # Make label size adapt to text content
        content_label.bind(
            texture_size=lambda instance, size: setattr(instance, 'height', size[1])
        )
        content_label.bind(
            width=lambda instance, width: setattr(instance, 'text_size', (width - dp(20), None))
        )
        
        # Create background for message
        content_layout = BoxLayout(
            size_hint_y=None,
            padding=dp(10)
        )
        
        # Set background color based on role
        bg_color = COLORS["user_msg"] if self.role == "user" else COLORS["ai_msg"]
        
        # Create proper canvas instructions for the background
        with content_layout.canvas.before:
            Color(*get_color(bg_color))
            self.rect = RoundedRectangle(
                pos=content_layout.pos, 
                size=content_layout.size,
                radius=[10, 10, 10, 10]
            )
            
        # Update the rectangle position and size when the layout changes
        content_layout.bind(pos=self._update_rect, size=self._update_rect)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Add the content label to the layout
        content_layout.add_widget(content_label)
        self.add_widget(content_layout)
    
    def _process_content(self) -> str:
        """
        Process the message content into a displayable string.
        
        Returns:
            Processed content string
        """
        content = self.message.get("content", "")
        
        # Handle content list (e.g., for multimodal messages)
        if isinstance(content, list):
            text_content = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_content.append(item.get("text", ""))
            content = "\n".join(text_content) if text_content else str(content)
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = str(content)
            
        return content
    
    def _update_rect(self, instance, value):
        """Update the background rectangle when the layout changes"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def update_message(self, message: Dict[str, Any]) -> None:
        """
        Update the message bubble with new content.
        
        Args:
            message: Dict containing updated message data
        """
        self.message = message
        self.role = message.get("role", self.role)
        
        # Recreate UI with updated content
        self.clear_widgets()
        self._create_ui() 