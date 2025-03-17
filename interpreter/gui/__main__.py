"""
Main entry point for the Open Interpreter GUI package.

This module allows the package to be executed directly with `python -m interpreter.gui`.
"""
from .app import launch_gui

if __name__ == "__main__":
    launch_gui() 