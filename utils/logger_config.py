import logging
import sys
import os

# Ensure the logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Create a logger
logger = logging.getLogger("dash_app")
logger.setLevel(logging.DEBUG)  # Set minimum logging level

# Console Handler (logs to terminal)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# File Handler (logs to a file)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # Logs everything

# Formatter (adds timestamps and log level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Attach handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Optional: Disable logging from external libraries (optional)
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # Flask internal logs
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Requests library logs
