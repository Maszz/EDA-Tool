import logging
import sys
import os

# ✅ Read Logging Config from Environment Variables
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# ✅ Ensure the logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ✅ Define log file
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# ✅ Create a logger
logger = logging.getLogger("dash_app")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))  # Default to DEBUG

# ✅ Remove existing handlers (to prevent duplicate logs)
if logger.hasHandlers():
    logger.handlers.clear()

if ENABLE_LOGGING:
    # ✅ Console Handler (logs to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # ✅ File Handler (logs to a file)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))  # Logs everything

    # ✅ Formatter (adds timestamps and log level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # ✅ Attach handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"✅ Logging Enabled | Level: {LOG_LEVEL}")

else:
    # ✅ Disable logging if ENABLE_LOGGING is False
    logging.disable(logging.CRITICAL)  # Turns off all logging
    print("⚠️ Logging is disabled.")

# ✅ Optional: Reduce external library logs
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # Flask internal logs
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Requests library logs
