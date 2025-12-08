# logger_config.py
import os
import sys
from datetime import datetime
from loguru import logger

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Get current date for daily folder
current_date = datetime.now().strftime("%Y%m%d")
daily_logs_dir = os.path.join(logs_dir, current_date)
os.makedirs(daily_logs_dir, exist_ok=True)

# Remove default handler
logger.remove()

# Define custom log levels with specific colors
# Add SUCCESS level between INFO and WARNING if not exists
if "SUCCESS" not in logger._core.levels:
    logger.level("SUCCESS", no=25, color="<green>")

# Configure colors for built-in levels
logger.level("TRACE", color="<cyan>")
logger.level("DEBUG", color="<blue>")
logger.level("INFO", color="<light-blue>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<RED><WHITE>")  # Bold red on white background

# Add console handler with custom format
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name:<20}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="TRACE",
    colorize=True
)

# Add file handler with daily rotation (without colors)
# ໃຊ້ enqueue=True ແລະ serialize=True ເພື່ອຮອງຮັບ multiple workers/processes
logger.add(
    os.path.join(daily_logs_dir, "app.log"),
    rotation="500 MB",  # ປ່ຽນເປັນ size-based rotation ເພື່ອຫຼີກລ້ຽງບັນຫາ Windows permission
    retention="30 days",  # Keep logs for 30 days
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name:<20}:{function}:{line} - {message}",
    level="TRACE",
    backtrace=True,
    diagnose=True,
    enqueue=True,  # ເຮັດໃຫ້ thread-safe ແລະ process-safe
    serialize=False  # ບໍ່ serialize ເພື່ອປະສິດທິພາບ
)

# Add separate error log file for errors and above
logger.add(
    os.path.join(daily_logs_dir, "error.log"),
    rotation="100 MB",  # ປ່ຽນເປັນ size-based rotation
    retention="30 days",  # Keep logs for 30 days
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name:<20}:{function}:{line} - {message}",
    level="ERROR",
    backtrace=True,
    diagnose=True,
    enqueue=True,  # ເຮັດໃຫ້ thread-safe ແລະ process-safe
    serialize=False
)