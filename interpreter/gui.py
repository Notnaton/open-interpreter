"""
GUI entry point for Open Interpreter.

This is a compatibility wrapper that uses the modular GUI implementation.
For new applications, use the modular GUI directly via:
    from interpreter.gui import launch_gui
"""
from .gui.app import launch_gui

if __name__ == "__main__":
    launch_gui()
