"""
Centralized error handling for the Open Interpreter GUI.

This module provides error handling utilities for the entire GUI application,
including global exception capturing, logging, and UI recovery mechanisms.
"""
import sys
import traceback
import time
import logging
from typing import Callable, Any, Optional
import os

# Set up logging
LOG_FILE = os.path.expanduser("~/.interpreter_gui_error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("interpreter_gui")

class ErrorHandler:
    """Centralized error handling class for the GUI application"""
    
    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        """Log an error to the error log file with context information"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        stack_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        
        # Log to console
        print(f"ERROR: {error_msg}")
        print(stack_trace)
        
        # Log to file
        logger.error(f"{error_msg}\n{stack_trace}")
    
    @staticmethod
    def install_global_handler() -> None:
        """Install a global exception handler to prevent app crashes"""
        def global_exception_handler(exc_type, exc_value, exc_traceback):
            """Global exception handler that logs errors but doesn't crash the app"""
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.critical(f"Uncaught exception: {error_msg}")
            # Don't crash the app
            return True
        
        # Install the custom exception handler
        sys.excepthook = global_exception_handler
    
    @staticmethod
    def safe_execute(func: Callable, *args: Any, recovery_value: Any = None, 
                    context: str = "", **kwargs: Any) -> Any:
        """
        Execute a function safely, catching and logging any exceptions.
        
        Args:
            func: The function to execute
            *args: Arguments to pass to the function
            recovery_value: Value to return if an exception occurs
            context: Context information for error logging
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The function result or recovery_value if an exception occurs
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return recovery_value

def gui_exception_handler(update_ui_callback: Optional[Callable] = None):
    """
    Decorator to safely execute UI code with exception handling.
    
    Args:
        update_ui_callback: Optional callback to execute for UI recovery
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, f"Error in {func.__name__}")
                
                # Execute UI recovery if provided
                if update_ui_callback:
                    try:
                        update_ui_callback(e)
                    except Exception as recovery_error:
                        ErrorHandler.log_error(recovery_error, "Error in UI recovery")
                
                # Return None to prevent further execution
                return None
        return wrapper
    return decorator 