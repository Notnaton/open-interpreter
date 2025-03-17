#!/usr/bin/env python3
"""
Open Interpreter GUI

A simple launcher script for the GUI in the scripts folder.
This allows running the GUI without installation:

    python scripts/gui.py
    ./scripts/gui.py (if executable)
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
current_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(current_dir))

# Import and run the GUI
from interpreter.gui.flet_app import main

if __name__ == "__main__":
    print("Starting Open Interpreter GUI...")
    main() 