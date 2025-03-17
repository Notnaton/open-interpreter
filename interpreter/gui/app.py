"""
Main application class for the Open Interpreter GUI.

This module provides the main Kivy application that integrates all
the GUI components, handlers, and utilities.
"""
import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from .components.chat_history import ChatHistory
from .components.settings_panel import SettingsPanel
from .handlers.message_handler import MessageHandler
from .handlers.tool_handler import ToolHandler
from .utils.styling import COLORS, UI_DIMENSIONS
from .utils.error_handler import ErrorHandler
from .models.settings import Settings

from ..interpreter import Interpreter  # Import from parent package

# Configure Kivy
kivy.require('2.3.1')
Window.clearcolor = get_color_from_hex(COLORS["background"])
Window.size = (UI_DIMENSIONS["window_width"], UI_DIMENSIONS["window_height"])

class InterpreterGUI(App):
    """Main Kivy application for Open Interpreter"""
    
    def __init__(self, interpreter_instance=None, **kwargs):
        """
        Initialize the GUI application.
        
        Args:
            interpreter_instance: Optional interpreter instance to use
            **kwargs: Additional keyword arguments for App
        """
        super(InterpreterGUI, self).__init__(**kwargs)
        self.title = "Open Interpreter"
        
        # Create or use provided interpreter instance
        self.interpreter = interpreter_instance or Interpreter()
        
        # Create handlers
        self.message_handler = MessageHandler(
            self.interpreter, 
            status_callback=self.update_status
        )
        self.tool_handler = ToolHandler(
            status_callback=self.update_status
        )
        
        # Create settings model
        self.settings = Settings(self.interpreter)
        
        # Initialize UI elements (will be set in build)
        self.chat_history = None
        self.message_input = None
        self.status_label = None
        
        # Install global error handler
        ErrorHandler.install_global_handler()
        
        # Load persistent settings
        self.settings.load_from_file()
        self.settings.apply_to_interpreter(self.interpreter)
    
    def on_stop(self):
        """Save settings when app is closed"""
        self.settings.save_to_file()
        return super().on_stop()
    
    def build(self):
        """Build the application UI"""
        self.root = BoxLayout(orientation='vertical')
        
        # Add top toolbar
        self._build_toolbar()
        
        # Add chat history
        self.chat_history = ChatHistory()
        self.root.add_widget(self.chat_history)
        
        # Add input area
        self._build_input_area()
        
        # Add status bar
        self._build_status_bar()
        
        # Initialize with empty messages if needed
        if not hasattr(self.interpreter, 'messages'):
            self.interpreter.messages = []
        
        # Update chat history
        self.update_chat_history()
        
        return self.root
    
    def _build_toolbar(self):
        """Build the top toolbar with title and buttons"""
        toolbar = BoxLayout(
            size_hint_y=None,
            height=dp(UI_DIMENSIONS["toolbar_height"]),
            padding=dp(5),
            spacing=dp(10)
        )
        
        # Add background to toolbar
        with toolbar.canvas.before:
            Color(*get_color_from_hex(COLORS["secondary"]))
            Rectangle(pos=(0, 0), size=(Window.width, dp(UI_DIMENSIONS["toolbar_height"])))
        
        # Title
        title = Label(
            text="Open Interpreter",
            color=get_color_from_hex("#FFFFFF"),
            bold=True,
            size_hint_x=0.7
        )
        toolbar.add_widget(title)
        
        # Settings button
        settings_btn = Button(
            text="Settings",
            size_hint_x=0.15,
            background_color=get_color_from_hex(COLORS["primary"])
        )
        settings_btn.bind(on_release=self.open_settings)
        toolbar.add_widget(settings_btn)
        
        # Clear chat button
        clear_btn = Button(
            text="Clear Chat",
            size_hint_x=0.15,
            background_color=get_color_from_hex(COLORS["text_light"])
        )
        clear_btn.bind(on_release=self.clear_chat)
        toolbar.add_widget(clear_btn)
        
        self.root.add_widget(toolbar)
    
    def _build_input_area(self):
        """Build the message input area with text input and send button"""
        input_area = BoxLayout(
            size_hint_y=None,
            height=dp(UI_DIMENSIONS["input_area_height"]),
            padding=dp(10),
            spacing=dp(10)
        )
        
        self.message_input = TextInput(
            multiline=True,
            hint_text="Type your message here...",
            font_size=dp(14),
            padding=dp(10),
            cursor_color=get_color_from_hex(COLORS["text"]),
            background_color=get_color_from_hex("#FFFFFF")
        )
        # Bind Enter key to send message
        self.message_input.bind(on_key_down=self.on_key_down)
        input_area.add_widget(self.message_input)
        
        # Send button
        send_btn = Button(
            text="Send",
            size_hint_x=0.2,
            background_color=get_color_from_hex(COLORS["primary"]),
            color=get_color_from_hex("#FFFFFF")
        )
        send_btn.bind(on_release=self.send_message)
        input_area.add_widget(send_btn)
        
        self.root.add_widget(input_area)
    
    def _build_status_bar(self):
        """Build the status bar at the bottom of the window"""
        status_bar = BoxLayout(
            size_hint_y=None,
            height=dp(UI_DIMENSIONS["status_bar_height"]),
            padding=[dp(10), dp(5)]
        )
        
        # Add background to status bar
        with status_bar.canvas.before:
            Color(*get_color_from_hex(COLORS["secondary"]))
            Rectangle(
                pos=(0, 0), 
                size=(Window.width, dp(UI_DIMENSIONS["status_bar_height"]))
            )
        
        # Status indicator
        self.status_label = Label(
            text="Ready",
            color=get_color_from_hex("#FFFFFF"),
            size_hint_x=1
        )
        status_bar.add_widget(self.status_label)
        
        self.root.add_widget(status_bar)
    
    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        """
        Handle keypress events.
        
        Send message when Ctrl+Enter is pressed.
        """
        # keycode 40 is Enter key
        if keycode == 40 and 'ctrl' in modifiers:
            self.send_message(None)
            return True
    
    def open_settings(self, instance):
        """Open the settings modal dialog"""
        settings_panel = SettingsPanel(
            self.interpreter,
            callback=self.update_status
        )
        settings_panel.open()
    
    def clear_chat(self, instance):
        """Clear the chat history"""
        self.interpreter.messages = []
        self.update_chat_history()
        self.update_status("Chat cleared")
    
    def update_chat_history(self):
        """Update the chat history UI with current messages"""
        # Get safe copy of messages
        messages_copy = self.message_handler.get_message_safe_copy()
        
        # Update the UI
        self.chat_history.update_messages(messages_copy)
    
    def update_status(self, status):
        """
        Update the status bar text.
        
        This method is used as a callback for various components.
        """
        def _update(dt):
            if self.status_label:
                self.status_label.text = status
        
        # Use Clock to ensure UI updates happen in the main thread
        Clock.schedule_once(_update, 0)
    
    def send_message(self, instance):
        """Send the user message to the interpreter and handle the response"""
        # Get message text
        message = self.message_input.text.strip()
        if not message:
            return
        
        # Clear input
        self.message_input.text = ""
        
        # Send message
        self.message_handler.send_user_message(message)
        
        # Update UI
        self.update_chat_history()
        
        # Set status to "Thinking..."
        self.update_status("Thinking...")


def launch_gui(interpreter_instance=None):
    """
    Launch the GUI with an optional interpreter instance.
    
    Args:
        interpreter_instance: Optional interpreter instance to use
    """
    try:
        app = InterpreterGUI(interpreter_instance=interpreter_instance)
        app.run()
    except Exception as e:
        ErrorHandler.log_error(e, "Error launching GUI")
        
        # Try to display a simple error dialog
        try:
            from kivy.uix.label import Label
            from kivy.uix.floatlayout import FloatLayout
            
            class ErrorApp(App):
                def build(self):
                    layout = FloatLayout()
                    error_label = Label(
                        text=f"Failed to launch Open Interpreter GUI:\n{str(e)}",
                        color=(1, 0, 0, 1)
                    )
                    layout.add_widget(error_label)
                    return layout
            
            error_app = ErrorApp()
            error_app.run()
        except:
            # If all else fails, print to console
            print("FATAL ERROR: Could not launch recovery GUI") 