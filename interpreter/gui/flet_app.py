import flet as ft
import asyncio
import threading
import datetime
import os
import sys
from pathlib import Path

# Add the parent directory to the path to allow importing the interpreter module
# This is only needed when running the file directly
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

from interpreter import Interpreter
from interpreter.profiles import Profile

class InterpreterMessage:
    def __init__(self, content, role="user"):
        self.content = content
        self.role = role
        self.timestamp = ft.Text(value=datetime.datetime.now().strftime("%H:%M"))

    def to_message_row(self, theme_mode):
        # Theme-aware colors
        bg_color = "#f0f0f0" if self.role == "user" else "#e1f5fe"
        if theme_mode == ft.ThemeMode.DARK:
            bg_color = "#424242" if self.role == "user" else "#263238"
            
        text_align = ft.TextAlign.RIGHT if self.role == "user" else ft.TextAlign.LEFT
        alignment = ft.MainAxisAlignment.END if self.role == "user" else ft.MainAxisAlignment.START
        
        return ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Markdown(
                                value=self.content,
                                selectable=True,
                                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                code_theme="atom-one-dark" if theme_mode == ft.ThemeMode.DARK else "atom-one-light",
                            ),
                            padding=ft.padding.all(10),
                            border_radius=ft.border_radius.all(10),
                            bgcolor=bg_color,
                            width=500,
                        )
                    ],
                    alignment=alignment,
                ),
                ft.Row(
                    [
                        self.timestamp,
                        ft.Text(" • " + self.role.capitalize()),
                    ],
                    alignment=alignment,
                    tight=True,
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            width=800,
        )

class InterpreterApp:
    def __init__(self):
        """Initialize the Interpreter App."""
        self.interpreter = Interpreter()
        self.messages = []
        self.lock = threading.Lock()
        self.active_thread = None
        self.theme_mode = ft.ThemeMode.LIGHT
        self.settings_dialog = None
        self.page = None  # Store reference to the page for later use
        
    def main(self, page: ft.Page):
        # Store reference to the page
        self.page = page
        
        # Set up the page
        self.page.title = "Open Interpreter"
        self.page.theme_mode = self.theme_mode
        self.page.padding = 0
        self.page.bgcolor = None  # Let theme handle background color
        self.page.window_width = 1000
        self.page.window_height = 800
        self.page.window_min_width = 600
        self.page.window_min_height = 400
        
        # Add window resize event handler
        def on_resize(e):
            if hasattr(self, 'settings_container'):
                self.settings_container.width = self.page.width
                self.settings_container.height = self.page.height
                self.page.update()
        
        self.page.on_resize = on_resize
        
        # Chat messages list
        self.messages_view = ft.ListView(
            expand=True,
            auto_scroll=True,
            spacing=10,
            padding=ft.padding.all(10),
        )
        
        # Message input field
        self.message_input = ft.TextField(
            hint_text="Ask Open Interpreter...",
            border_radius=ft.border_radius.all(30),
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            text_size=14,
            shift_enter=True,
            on_submit=self.send_message,
        )

        # Send button
        send_button = ft.IconButton(
            icon=ft.icons.SEND_ROUNDED,
            tooltip="Send message",
            on_click=self.send_message,
        )
        
        # Create model dropdown and other settings fields
        self.model_dropdown = ft.Dropdown(
            label="Model",
            hint_text="Select LLM model",
            options=[
                ft.dropdown.Option("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet"),
                ft.dropdown.Option("gpt-4o", "GPT-4o"),
                ft.dropdown.Option("gpt-4-turbo", "GPT-4 Turbo"),
                ft.dropdown.Option("gpt-3.5-turbo", "GPT-3.5 Turbo"),
                ft.dropdown.Option("claude-3-haiku-20240307", "Claude 3 Haiku"),
                ft.dropdown.Option("claude-3-opus-20240229", "Claude 3 Opus"),
                ft.dropdown.Option("custom", "Custom..."),
            ],
            autofocus=True,
            value="claude-3-5-sonnet-20241022",
            width=300,
            on_change=self.on_model_change,
        )
        
        # Custom model TextField (initially hidden)
        self.custom_model_field = ft.TextField(
            label="Custom Model",
            hint_text="Enter custom model name",
            width=300,
            visible=False,
        )
        
        # Temperature slider with value label in a row
        self.temperature_slider = ft.Slider(
            min=0,
            max=1,
            divisions=10,  # Back to 10 steps
            value=0,
            on_change=self.update_temperature_label,
            expand=True,  # Take available space in the row
        )
        
        # Temperature display label
        self.temperature_label = ft.Text(
            value="0.0",
            style=ft.TextThemeStyle.BODY_MEDIUM,
            width=50,  # Fixed width to avoid layout shifts
            text_align=ft.TextAlign.RIGHT,
        )
        
        # Temperature row to contain slider and label side by side
        self.temperature_row = ft.Row(
            [
                self.temperature_slider,
                self.temperature_label,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            width=300,
        )
        
        # Auto-run switch
        self.auto_run_switch = ft.Switch(
            label="Auto-run code",
            value=True,
        )
        
        # API Base TextField
        self.api_base_field = ft.TextField(
            label="API Base URL",
            hint_text="Leave empty for default",
            width=300,
        )
        
        # API Key TextField with password protection
        self.api_key_field = ft.TextField(
            label="API Key",
            hint_text="Your API key",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        # Provider dropdown
        self.provider_dropdown = ft.Dropdown(
            label="Provider",
            hint_text="Select provider (optional)",
            options=[
                ft.dropdown.Option("", "Auto-detect"),
                ft.dropdown.Option("anthropic", "Anthropic"),
                ft.dropdown.Option("openai", "OpenAI"),
                ft.dropdown.Option("azure", "Azure OpenAI"),
                ft.dropdown.Option("ollama", "Ollama"),
                ft.dropdown.Option("custom", "Custom..."),
            ],
            width=300,
            on_change=self.on_provider_change,
        )
        
        # Custom provider TextField (initially hidden)
        self.custom_provider_field = ft.TextField(
            label="Custom Provider",
            hint_text="Enter custom provider name",
            width=300,
            visible=False,
        )

        # Load profile from default location
        profile = Profile()
        if os.path.exists(os.path.expanduser(Profile.DEFAULT_PROFILE_PATH)):
            profile.load(Profile.DEFAULT_PROFILE_PATH)
            
        # Set initial values for settings based on profile
        model_value = profile.model if profile.model else "claude-3-5-sonnet-20241022"
        provider_value = profile.provider if profile.provider else ""
        
        # Check if model is in the dropdown options
        model_exists = any(option.key == model_value for option in self.model_dropdown.options)
        if not model_exists:
            # Set to custom and populate custom field
            self.model_dropdown.value = "custom"
            self.custom_model_field.value = model_value
            self.custom_model_field.visible = True
        else:
            self.model_dropdown.value = model_value
            
        # Check if provider is in the dropdown options
        provider_exists = any(option.key == provider_value for option in self.provider_dropdown.options)
        if provider_value and not provider_exists:
            # Set to custom and populate custom field
            self.provider_dropdown.value = "custom"
            self.custom_provider_field.value = provider_value
            self.custom_provider_field.visible = True
        else:
            self.provider_dropdown.value = provider_value
        
        # Set other values
        self.temperature_slider.value = profile.temperature
        self.temperature_label.value = f"{profile.temperature:.1f}"
        self.auto_run_switch.value = profile.auto_run
        self.api_base_field.value = profile.api_base or ""
        self.api_key_field.value = profile.api_key or ""
        
        # Settings dialog content
        settings_header = ft.Row(
            [
                ft.Text("Settings", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    tooltip="Close",
                    on_click=self.close_settings,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        settings_content = ft.Column(
            [
                settings_header,
                ft.Divider(),
                
                ft.Text("Model Settings", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.model_dropdown,
                self.custom_model_field,
                self.provider_dropdown,
                self.custom_provider_field,
                
                ft.Container(height=10),
                
                ft.Text("API Configuration", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.api_base_field,
                self.api_key_field,
                
                ft.Container(height=10),
                
                ft.Text("Generation Settings", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text("Temperature: Controls randomness of outputs", style=ft.TextThemeStyle.BODY_MEDIUM),
                self.temperature_row,
                
                ft.Container(height=10),
                
                ft.Text("Code Execution", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.auto_run_switch,
                
                ft.Container(height=20),
                
                ft.Row(
                    [
                        ft.OutlinedButton("Cancel", on_click=self.close_settings),
                        ft.FilledButton("Save", on_click=self.save_settings),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10,
                ),
            ],
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            width=450,
            height=600,
        )
        
        # Dark mode toggle
        self.dark_mode_switch = ft.Switch(
            label="Dark Mode",
            value=self.theme_mode == ft.ThemeMode.DARK,
            on_change=self.toggle_dark_mode,
        )
        
        # Settings button
        settings_button = ft.IconButton(
            icon=ft.icons.SETTINGS,
            tooltip="Settings",
            on_click=self.show_settings,
        )

        # Stop button (initially disabled)
        self.stop_button = ft.IconButton(
            icon=ft.icons.STOP,
            tooltip="Stop generation",
            on_click=self.stop_generation,
            disabled=True,
        )
        
        # Create settings container (hidden initially)
        self.settings_container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=settings_content,
                    padding=20,
                ),
                elevation=15,
                surface_tint_color=ft.colors.SURFACE_VARIANT,
                color=ft.colors.SURFACE,
                shadow_color=ft.colors.with_opacity(0.5, ft.colors.BLACK),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            alignment=ft.alignment.center,
            visible=False,
            # Make it take the full size of the screen
            width=page.width,
            height=page.height,
            # Semi-transparent background
            bgcolor=ft.colors.with_opacity(0.6, ft.colors.BLACK),
            # Position it in the center
            left=0,
            top=0,
            right=0,
            bottom=0,
        )

        # Set up the main layout
        page.overlay.append(self.settings_container)
        
        page.add(
            # Top app bar
            ft.AppBar(
                leading=ft.Icon(ft.icons.INTERPRETER_MODE),
                leading_width=40,
                title=ft.Text("Open Interpreter"),
                center_title=False,
                bgcolor=ft.colors.SURFACE_VARIANT,
                actions=[
                    self.dark_mode_switch,
                    settings_button,
                ],
            ),
            
            # Chat area
            ft.Container(
                content=self.messages_view,
                expand=True,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
                margin=ft.margin.all(10),
                padding=ft.padding.all(0),
            ),
            
            # Bottom input area
            ft.Container(
                content=ft.Row(
                    [
                        self.message_input,
                        self.stop_button,
                        send_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(10),
            ),
        )
        
        # Add welcome message
        self.add_assistant_message("👋 Welcome to Open Interpreter! How can I help you today?")
        page.update()
    
    def toggle_dark_mode(self, e):
        # Update theme mode
        self.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        self.page.theme_mode = self.theme_mode
        
        # Refresh all messages to update their appearance
        self.refresh_messages()
        self.page.update()
    
    def refresh_messages(self):
        # Rebuild all message rows with the current theme
        if hasattr(self, 'messages_view') and hasattr(self, 'messages'):
            self.messages_view.controls.clear()
            for message in self.messages:
                self.messages_view.controls.append(message.to_message_row(self.theme_mode))
            self.messages_view.update()
    
    def show_settings(self, e):
        """Show the settings container."""
        # Show the settings container
        self.settings_container.visible = True
        self.page.update()
    
    def close_settings(self, e):
        """Close the settings dialog without saving changes."""
        # Hide the settings container
        self.settings_container.visible = False
        
        # Reset custom fields visibility based on current saved values
        if self.model_dropdown.value == "custom":
            self.custom_model_field.visible = True
        else:
            self.custom_model_field.visible = False
            
        if self.provider_dropdown.value == "custom":
            self.custom_provider_field.visible = True
        else:
            self.custom_provider_field.visible = False
        
        self.page.update()
    
    def on_model_change(self, e):
        """Handle model dropdown changes."""
        if e.control.value == "custom":
            self.custom_model_field.visible = True
        else:
            self.custom_model_field.visible = False
        self.page.update()
    
    def on_provider_change(self, e):
        """Handle provider dropdown changes."""
        if e.control.value == "custom":
            self.custom_provider_field.visible = True
        else:
            self.custom_provider_field.visible = False
        self.page.update()
    
    def save_settings(self, e):
        """Save the settings and close the dialog."""
        # Handle custom model
        if self.model_dropdown.value == "custom" and self.custom_model_field.value:
            model_value = self.custom_model_field.value
        else:
            model_value = self.model_dropdown.value
            
        # Handle custom provider
        if self.provider_dropdown.value == "custom" and self.custom_provider_field.value:
            provider_value = self.custom_provider_field.value
        else:
            provider_value = self.provider_dropdown.value
        
        # Update the interpreter with new settings
        self.interpreter.model = model_value
        self.interpreter.temperature = self.temperature_slider.value
        self.interpreter.auto_run = self.auto_run_switch.value
        self.interpreter.api_base = self.api_base_field.value if self.api_base_field.value else None
        self.interpreter.api_key = self.api_key_field.value if self.api_key_field.value else None
        self.interpreter.provider = provider_value
        
        # Hide the settings container
        self.settings_container.visible = False
        
        # Show a confirmation snackbar
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved"),
            action="OK",
            duration=2000,
        )
        self.page.snack_bar.open = True
        
        self.page.update()
    
    def add_user_message(self, content):
        message = InterpreterMessage(content, role="user")
        self.messages.append(message)
        self.messages_view.controls.append(message.to_message_row(self.theme_mode))
        self.message_input.value = ""
        self.message_input.update()
        self.messages_view.update()
    
    def add_assistant_message(self, content):
        message = InterpreterMessage(content, role="assistant")
        self.messages.append(message)
        self.messages_view.controls.append(message.to_message_row(self.theme_mode))
        self.messages_view.update()
    
    def send_message(self, e=None):
        if not self.message_input.value or self.message_input.value.isspace():
            return
        
        # Get the message content
        message_content = self.message_input.value
        
        # Add the message to the chat
        self.add_user_message(message_content)
        
        # Disable the input and enable the stop button
        self.message_input.disabled = True
        self.stop_button.disabled = False
        self.message_input.update()
        self.stop_button.update()
        
        # Create a new thread for the response
        self.active_thread = threading.Thread(
            target=self.get_interpreter_response,
            args=(message_content,),
        )
        self.active_thread.daemon = True
        self.active_thread.start()
    
    def get_interpreter_response(self, message_content):
        # Create a temporary list for capturing the response chunks
        response_chunks = []
        
        try:
            # Set the input message
            self.interpreter.messages = [{"role": "user", "content": message_content}]
            
            # Create an empty response in the UI
            current_response = ""
            with self.lock:
                self.add_assistant_message(current_response)
                response_index = len(self.messages_view.controls) - 1
            
            # Use standard non-async approach
            for chunk in self.interpreter.respond(stream=True):
                # Check if we have delta content in choices
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content') and choice.delta.content:
                        # Append the new content
                        response_chunks.append(choice.delta.content)
                        current_response = "".join(response_chunks)
                        
                        # Update the UI with the new chunk
                        with self.lock:
                            if response_index < len(self.messages_view.controls):
                                self.messages[-1].content = current_response
                                self.messages_view.controls[response_index] = self.messages[-1].to_message_row(self.theme_mode)
                                self.messages_view.update()
        
        except Exception as e:
            # Add error message
            error_message = f"⚠️ Error: {str(e)}"
            with self.lock:
                if response_index < len(self.messages_view.controls):
                    self.messages[-1].content = error_message
                    self.messages_view.controls[response_index] = self.messages[-1].to_message_row(self.theme_mode)
                else:
                    self.add_assistant_message(error_message)
                self.messages_view.update()
        
        finally:
            # Re-enable the input and disable the stop button
            self.message_input.disabled = False
            self.stop_button.disabled = True
            self.message_input.update()
            self.stop_button.update()
    
    def stop_generation(self, e=None):
        # Add a way to stop the generation
        if self.active_thread and self.active_thread.is_alive():
            self.interpreter._interrupt = True
            self.add_assistant_message("_Generation stopped by user._")

    def update_temperature_label(self, e):
        # Update the temperature label with the current slider value
        self.temperature_label.value = f"{self.temperature_slider.value:.1f}"
        self.page.update()

def main():
    app = InterpreterApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main() 