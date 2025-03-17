"""
Settings panel component for the Open Interpreter GUI.

This module provides a modal dialog for configuring interpreter settings
such as model, provider, API keys, and other options.
"""
from typing import List, Dict, Any, Optional, Callable
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.utils import get_color_from_hex

from ..utils.styling import COLORS
from ..utils.error_handler import gui_exception_handler
from ..models.settings import Settings

class CustomModalView(ModalView):
    """A custom ModalView that includes the minimum_height property"""
    minimum_height = NumericProperty(0)
    title = StringProperty('Settings')


class SettingsPanel(CustomModalView):
    """Settings modal that allows configuring the interpreter"""
    
    def __init__(self, interpreter_instance, callback: Optional[Callable] = None, **kwargs):
        """
        Initialize the settings panel.
        
        Args:
            interpreter_instance: The interpreter instance to configure
            callback: Optional callback function to execute when settings are saved
            **kwargs: Additional keyword arguments for ModalView
        """
        super(SettingsPanel, self).__init__(**kwargs)
        self.size_hint = (0.8, 0.8)
        self.interpreter = interpreter_instance
        self.callback = callback
        
        # Create settings model
        self.settings = Settings(interpreter_instance)
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the settings UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Title
        title = Label(
            text="Settings",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            bold=True
        )
        main_layout.add_widget(title)
        
        # Scrollable content
        scroll_view = ScrollView(size_hint=(1, 1))
        
        # Settings container - now inside a scroll view
        content = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Provider selection
        content.add_widget(Label(
            text="Provider:", 
            halign='right', 
            size_hint_y=None, 
            height=dp(40), 
            size_hint_x=0.3
        ))
        
        provider_spinner = Spinner(
            text=self.settings.provider or "Auto",
            values=["Auto", "openai", "anthropic", "ollama", "lm_studio", "local"],
            size_hint_y=None,
            height=dp(40),
            size_hint_x=0.7
        )
        content.add_widget(provider_spinner)
        self.provider_spinner = provider_spinner
        
        # Model selection
        content.add_widget(Label(
            text="Model:", 
            halign='right', 
            size_hint_y=None, 
            height=dp(40), 
            size_hint_x=0.3
        ))
        
        # Model input with model selection
        model_layout = BoxLayout(
            size_hint_x=0.7, 
            size_hint_y=None, 
            height=dp(40), 
            spacing=dp(5)
        )
        
        model_input = TextInput(
            text=self.settings.model or "",
            multiline=False,
            size_hint_x=0.7,
            hint_text="Model name"
        )
        model_layout.add_widget(model_input)
        self.model_input = model_input
        
        # Common models dropdown
        common_models = [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "mistral:latest",
            "llama3:latest"
        ]
        
        model_spinner = Spinner(
            text="Select model",
            values=common_models,
            size_hint_x=0.3
        )
        model_spinner.bind(text=self._on_model_selected)
        model_layout.add_widget(model_spinner)
        
        content.add_widget(model_layout)
        
        # API Base
        content.add_widget(Label(
            text="API Base URL:", 
            halign='right', 
            size_hint_y=None, 
            height=dp(40), 
            size_hint_x=0.3
        ))
        
        api_base_input = TextInput(
            text=self.settings.api_base or "",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            size_hint_x=0.7,
            hint_text="https://api.openai.com/v1/ or leave empty for default"
        )
        content.add_widget(api_base_input)
        self.api_base_input = api_base_input
        
        # API Key
        content.add_widget(Label(
            text="API Key:", 
            halign='right', 
            size_hint_y=None, 
            height=dp(40), 
            size_hint_x=0.3
        ))
        
        api_key_input = TextInput(
            text=self.settings.api_key or "",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            size_hint_x=0.7,
            password=True,
            hint_text="Enter your API key"
        )
        content.add_widget(api_key_input)
        self.api_key_input = api_key_input
        
        # Temperature
        content.add_widget(Label(
            text="Temperature:", 
            halign='right', 
            size_hint_y=None, 
            height=dp(40), 
            size_hint_x=0.3
        ))
        
        temp_input = TextInput(
            text=str(self.settings.temperature),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            size_hint_x=0.7,
            hint_text="0.0 - 1.0"
        )
        content.add_widget(temp_input)
        self.temp_input = temp_input
        
        # Tools
        content.add_widget(Label(
            text="Tools:", 
            halign='right', 
            size_hint_y=None, 
            height=dp(40), 
            size_hint_x=0.3
        ))
        
        tools_layout = BoxLayout(size_hint_x=0.7, size_hint_y=None, height=dp(40))
        
        self.tool_buttons = {}
        available_tools = ["interpreter", "editor", "gui"]
        for tool in available_tools:
            btn = ToggleButton(
                text=tool,
                state='down' if tool in self.settings.tools else 'normal'
            )
            tools_layout.add_widget(btn)
            self.tool_buttons[tool] = btn
            
        content.add_widget(tools_layout)
        
        # Auto-run toggle
        content.add_widget(Label(
            text="Auto-run:", 
            halign='right', 
            size_hint_y=None, 
            height=dp(40), 
            size_hint_x=0.3
        ))
        
        self.auto_run_btn = ToggleButton(
            text="Enabled" if self.settings.auto_run else "Disabled",
            state='down' if self.settings.auto_run else 'normal',
            size_hint_x=0.7,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(self.auto_run_btn)
        
        # Add content to scroll view
        scroll_view.add_widget(content)
        main_layout.add_widget(scroll_view)
        
        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        cancel_btn = Button(
            text="Cancel",
            background_color=get_color_from_hex(COLORS["text_light"])
        )
        cancel_btn.bind(on_release=self.dismiss)
        
        save_btn = Button(
            text="Save",
            background_color=get_color_from_hex(COLORS["primary"])
        )
        save_btn.bind(on_release=self.save_settings)
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)
        
        main_layout.add_widget(button_layout)
        self.add_widget(main_layout)
    
    def _on_model_selected(self, spinner, text):
        """Update model input text when a model is selected from the dropdown"""
        if text != "Select model":
            self.model_input.text = text

    @gui_exception_handler()
    def save_settings(self, *args):
        """Save settings from the UI to the interpreter instance and settings model"""
        # Get values from UI
        self.settings.api_key = self.api_key_input.text.strip() if self.api_key_input.text else None
        self.settings.model = self.model_input.text.strip() if self.model_input.text else None
        self.settings.temperature = float(self.temp_input.text) if self.temp_input.text else 0.7
        self.settings.provider = self.provider_spinner.text.lower() if self.provider_spinner.text and self.provider_spinner.text != "Auto" else None
        self.settings.api_base = self.api_base_input.text.strip() if self.api_base_input.text else None
        
        # Apply model prefix based on provider if not already prefixed
        if self.settings.model and self.settings.provider and self.settings.provider != "auto":
            # Check if model name already has a provider prefix
            has_prefix = False
            provider_prefixes = ["openai/", "anthropic/", "ollama/", "lm_studio/", "local/"]
            for prefix in provider_prefixes:
                if self.settings.model.startswith(prefix):
                    has_prefix = True
                    break
            
            # Add provider prefix if needed
            if not has_prefix:
                if self.settings.provider == "openai":
                    self.settings.model = f"openai/{self.settings.model}"
                elif self.settings.provider == "anthropic":
                    self.settings.model = f"anthropic/{self.settings.model}"
                elif self.settings.provider == "ollama":
                    self.settings.model = f"ollama/{self.settings.model}"
                elif self.settings.provider == "lm_studio":
                    self.settings.model = f"lm_studio/{self.settings.model}"
                elif self.settings.provider == "local":
                    self.settings.model = f"local/{self.settings.model}"
        
        # Update tools from toggle buttons
        self.settings.tools = [
            tool for tool, btn in self.tool_buttons.items() 
            if btn.state == 'down'
        ]
        
        # Update auto-run
        self.settings.auto_run = self.auto_run_btn.state == 'down'
        
        # Apply settings to interpreter
        self.settings.apply_to_interpreter(self.interpreter)
        
        # Save settings to file
        self.settings.save_to_file()
        
        # Close the settings panel
        self.dismiss()
        
        # Execute callback if provided
        if self.callback:
            self.callback("Settings saved") 