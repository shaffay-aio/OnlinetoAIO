import os
import logging

from dotenv import load_dotenv
load_dotenv()

class CustomFormatter(logging.Formatter):
    GREEN = "\033[92m"
    RESET = "\033[0m"
    FORMAT = f"{GREEN}%(asctime)s - %(name)s - %(levelname)s - %(message)s{RESET}"

    def format(self, record):
        formatter = logging.Formatter(self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    
    # Check if logger already has handlers to prevent duplicate logs
    if not logger.hasHandlers():
        # Central control for turning DEBUG and INFO logging on/off
        debug_enabled = os.getenv("DEBUG_LOGGING_ENABLED", "true").lower() == "true"
        info_enabled = os.getenv("INFO_LOGGING_ENABLED", "true").lower() == "true"
        
        if debug_enabled or info_enabled:
            logger.setLevel(level)
            
            # Create a console handler
            console_handler = logging.StreamHandler()
            
            # Set handler level based on environment variables
            if debug_enabled:
                console_handler.setLevel(logging.DEBUG)
            elif info_enabled:
                console_handler.setLevel(logging.INFO)
            else:
                # Disable the handler if neither is enabled
                console_handler.setLevel(logging.CRITICAL)
            
            # Apply the custom formatter
            console_handler.setFormatter(CustomFormatter())
            
            # Add the handler to the logger
            logger.addHandler(console_handler)
        else:
            # Disable logging if neither is enabled
            logger.disabled = True
    
    return logger