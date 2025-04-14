import logging
import os
import sys


class Logger:
    """
    A simple logger class that provides the same functionality as the current get_logger.
    """
    def __init__(self, name: str):
        """
        Initialize a logger with the given name.
        
        Args:
            name: The name of the logger
        """
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Configure the logger if it hasn't been configured yet
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            
            # Create file handler
            log_dir = os.path.expanduser("~/.maestro")
            os.makedirs(log_dir, exist_ok=True)  # Ensure directory exists
            log_file = os.path.join(log_dir, "mcp.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            
            # Add handlers to logger
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, *args, **kwargs):
        """
        Log an info message.
        
        Args:
            message: The message to log
            *args: Arguments for string formatting
            **kwargs: Keyword arguments for string formatting
        """
        if args:
            message = message % args
        self.logger.info(message, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """
        Log an error message.
        
        Args:
            message: The message to log
            *args: Arguments for string formatting
            **kwargs: Keyword arguments for string formatting
        """
        if args:
            message = message % args
        self.logger.error(message, **kwargs)


def get_logger(name: str) -> Logger:
    """
    Get a logger instance with the given name.
    This function is provided for backward compatibility.
    
    Args:
        name: The name of the logger
        
    Returns:
        A Logger instance
    """
    return Logger(name)
