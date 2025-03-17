"""
Centralized styling module for the Open Interpreter GUI.

This module contains all the styling constants used throughout the UI.
"""
from typing import Dict, Tuple, Any
from kivy.utils import get_color_from_hex

# Color scheme
COLORS: Dict[str, str] = {
    "primary": "#3498db",       # Blue
    "secondary": "#2c3e50",     # Dark blue
    "background": "#f9f9f9",    # Light gray
    "text": "#2c3e50",          # Dark blue
    "text_light": "#7f8c8d",    # Gray
    "user_msg": "#e8f4fc",      # Light blue
    "ai_msg": "#f0f0f0",        # Light gray
    "error": "#e74c3c",         # Red
    "success": "#2ecc71",       # Green
}

# Convert hex colors to Kivy color tuples when needed
def get_color(color_name: str) -> Tuple[float, float, float, float]:
    """Get a color tuple from the color name"""
    if color_name in COLORS:
        return get_color_from_hex(COLORS[color_name])
    return get_color_from_hex(color_name)

# UI dimensions
UI_DIMENSIONS: Dict[str, Any] = {
    "window_width": 1000,
    "window_height": 700,
    "padding": 10,
    "spacing": 10,
    "button_height": 40,
    "toolbar_height": 50,
    "status_bar_height": 30,
    "input_area_height": 100,
}

# Font settings
FONTS: Dict[str, Any] = {
    "default_size": 14,
    "title_size": 18,
    "small_size": 12,
}

# Animation durations
ANIMATIONS: Dict[str, float] = {
    "fade_in": 0.3,
    "fade_out": 0.2,
    "scroll_duration": 0.2,
} 