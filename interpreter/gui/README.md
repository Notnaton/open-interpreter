# Open Interpreter GUI

A graphical user interface for Open Interpreter built with [Flet](https://flet.dev/).

## Features

- Modern and intuitive chat interface
- Interactive messaging with Open Interpreter
- Code execution within the chat interface
- Live response streaming
- Dark/light mode toggle
- Settings configuration:
  - Model selection
  - Provider choice
  - API key and base URL configuration
  - Temperature and streaming options
  - Auto-run code toggle
- Markdown rendering with syntax highlighting for code blocks

## Requirements

- Python 3.8+
- Flet (`pip install flet[all]` or `uv add flet[all]`)

## Running the GUI

There are several ways to run the Open Interpreter GUI:

### 1. Using the launcher script

```bash
# Run with Python
python scripts/gui.py

# Or make it executable and run directly
chmod +x scripts/gui.py
./scripts/gui.py
```

### 2. Using Python's module syntax

```bash
python -m interpreter.gui.flet_app
```

### 3. After installation with pip

```bash
oi-gui
```

## Usage

1. **Sending Messages**: Type your query in the input field and press Enter or click the send button
2. **Configuring Settings**: Click the settings icon in the top right to adjust model, API, and execution settings
3. **Toggling Dark Mode**: Use the Dark Mode switch in the top bar to change the theme
4. **Stopping Generation**: If needed, click the stop button to halt the current response generation

## Implementation Details

The GUI is built using Flet, a framework for building interactive multi-platform applications using Flutter. It communicates with Open Interpreter's core functionality through its Python API.

Key components:

- `InterpreterApp`: Main application class managing the UI and interpreter interactions
- `InterpreterMessage`: Message representation for the chat interface
- Thread-based response handling to keep the UI responsive during long-running operations

## Contributing

Contributions to improve the GUI are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.

## License

Same as Open Interpreter's license. 