"""
Settings model for the Open Interpreter GUI.

This module provides a structured representation of the interpreter settings
with validation and persistence capabilities.
"""
import os
import json
from typing import List, Dict, Any, Optional, Union

class Settings:
    """Data model for interpreter settings with validation and persistence"""
    
    def __init__(self, interpreter_instance=None):
        """
        Initialize settings from an interpreter instance or defaults.
        
        Args:
            interpreter_instance: Optional interpreter instance to initialize from
        """
        # Default settings
        self.model: str = ""
        self.provider: Optional[str] = None
        self.api_key: Optional[str] = None
        self.api_base: Optional[str] = None
        self.temperature: float = 0.7
        self.tools: List[str] = ["interpreter"]
        self.auto_run: bool = True
        
        # Load from interpreter if provided
        if interpreter_instance:
            self.load_from_interpreter(interpreter_instance)
    
    def load_from_interpreter(self, interpreter) -> None:
        """
        Load settings from an interpreter instance.
        
        Args:
            interpreter: The interpreter instance to load settings from
        """
        if hasattr(interpreter, 'model') and interpreter.model:
            self.model = interpreter.model
            
        if hasattr(interpreter, 'provider') and interpreter.provider:
            self.provider = interpreter.provider
            
        if hasattr(interpreter, 'api_key') and interpreter.api_key:
            self.api_key = interpreter.api_key
            
        if hasattr(interpreter, 'api_base') and interpreter.api_base:
            self.api_base = interpreter.api_base
            
        if hasattr(interpreter, 'temperature'):
            self.temperature = interpreter.temperature
            
        if hasattr(interpreter, 'tools') and interpreter.tools:
            self.tools = interpreter.tools
            
        if hasattr(interpreter, 'auto_run'):
            self.auto_run = interpreter.auto_run
    
    def apply_to_interpreter(self, interpreter) -> None:
        """
        Apply these settings to an interpreter instance.
        
        Args:
            interpreter: The interpreter instance to apply settings to
        """
        # Only set values that are not None (to avoid overwriting with empty values)
        if self.model:
            interpreter.model = self.model
            
        if self.provider:
            interpreter.provider = self.provider
            
        if self.api_key:
            interpreter.api_key = self.api_key
            
        if self.api_base:
            interpreter.api_base = self.api_base
            
        interpreter.temperature = self.temperature
        interpreter.tools = self.tools
        interpreter.auto_run = self.auto_run
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to a dictionary for serialization.
        
        Returns:
            Dictionary representation of settings
        """
        return {
            "model": self.model,
            "provider": self.provider,
            "temperature": self.temperature,
            "api_base": self.api_base,
            "tools": self.tools,
            "auto_run": self.auto_run,
            # Don't include api_key for security
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load settings from a dictionary.
        
        Args:
            data: Dictionary containing settings values
        """
        if "model" in data and data["model"]:
            self.model = data["model"]
            
        if "provider" in data:
            self.provider = data["provider"]
            
        if "api_key" in data and data["api_key"]:
            self.api_key = data["api_key"]
            
        if "api_base" in data and data["api_base"]:
            self.api_base = data["api_base"]
            
        if "temperature" in data:
            self.temperature = float(data["temperature"])
            
        if "tools" in data and data["tools"]:
            self.tools = data["tools"]
            
        if "auto_run" in data:
            self.auto_run = bool(data["auto_run"])
    
    def load_from_file(self, file_path: Optional[str] = None) -> bool:
        """
        Load settings from a JSON file.
        
        Args:
            file_path: Path to settings file, defaults to ~/.interpreter_gui_settings.json
            
        Returns:
            True if successful, False otherwise
        """
        if file_path is None:
            file_path = os.path.expanduser("~/.interpreter_gui_settings.json")
            
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    self.from_dict(data)
                return True
        except Exception as e:
            print(f"Error loading settings: {e}")
        return False
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        Save settings to a JSON file.
        
        Args:
            file_path: Path to settings file, defaults to ~/.interpreter_gui_settings.json
            
        Returns:
            True if successful, False otherwise
        """
        if file_path is None:
            file_path = os.path.expanduser("~/.interpreter_gui_settings.json")
            
        try:
            # Convert settings to dict, excluding sensitive data
            data = self.to_dict()
            
            # Write to file
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
        return False 