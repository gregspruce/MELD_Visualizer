"""
Logging configuration for MELD Visualizer.
Provides structured logging with different levels and handlers.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..constants import ERROR_LOG_FILE_MAX_BYTES, LOG_BACKUP_COUNT, LOG_FILE_MAX_BYTES

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
APP_LOG_FILE = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"
PERFORMANCE_LOG_FILE = LOGS_DIR / "performance.log"
SECURITY_LOG_FILE = LOGS_DIR / "security.log"

# Log format configurations
DETAILED_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
)
SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
CONSOLE_FORMAT = "%(levelname)s - %(name)s - %(message)s"

# Color codes for console output
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",  # Reset
}


class ColoredConsoleHandler(logging.StreamHandler):
    """Console handler with colored output."""

    def emit(self, record):
        """Emit a colored log record."""
        try:
            # Add color to the level name
            levelname = record.levelname
            if levelname in COLORS:
                record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"

            super().emit(record)

            # Reset level name
            record.levelname = levelname
        except Exception:
            self.handleError(record)


class PerformanceLogger:
    """Logger for performance metrics."""

    def __init__(self, logger_name: str = "performance"):
        """Initialize performance logger."""
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        # Add file handler for performance logs
        if not self.logger.handlers:
            handler = logging.handlers.RotatingFileHandler(
                PERFORMANCE_LOG_FILE, maxBytes=LOG_FILE_MAX_BYTES, backupCount=5  # 10MB
            )
            handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
            self.logger.addHandler(handler)

    def log_operation(self, operation: str, duration_ms: float, details: Optional[dict] = None):
        """Log a performance metric."""
        message = f"Operation: {operation} - Duration: {duration_ms:.2f}ms"
        if details:
            message += f" - Details: {details}"
        self.logger.info(message)

    def log_memory(self, operation: str, memory_mb: float):
        """Log memory usage."""
        self.logger.info(f"Memory: {operation} - Usage: {memory_mb:.2f}MB")

    def log_cache_hit(self, cache_name: str, hit_rate: float):
        """Log cache performance."""
        self.logger.info(f"Cache: {cache_name} - Hit rate: {hit_rate:.2%}")


class SecurityLogger:
    """Logger for security events."""

    def __init__(self, logger_name: str = "security"):
        """Initialize security logger."""
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        # Add file handler for security logs
        if not self.logger.handlers:
            handler = logging.handlers.RotatingFileHandler(
                SECURITY_LOG_FILE, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_BACKUP_COUNT  # 10MB
            )
            handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
            self.logger.addHandler(handler)

    def log_file_upload(self, filename: str, size_mb: float, user: Optional[str] = None):
        """Log file upload event."""
        self.logger.info(f"File upload: {filename} ({size_mb:.2f}MB) by {user or 'anonymous'}")

    def log_validation_failure(self, reason: str, details: Optional[dict] = None):
        """Log validation failure."""
        message = f"Validation failed: {reason}"
        if details:
            message += f" - Details: {details}"
        self.logger.warning(message)

    def log_config_change(self, changes: dict, user: Optional[str] = None):
        """Log configuration changes."""
        self.logger.info(f"Config changed by {user or 'anonymous'}: {changes}")


def setup_logging(
    level: str = "INFO", console: bool = True, file: bool = True, colored: bool = True
) -> None:
    print(f"DEBUG: setup_logging() called with MELD_LOGGING={os.environ.get('MELD_LOGGING')}")
    print(f"DEBUG: setup_logging() called with MELD_LOGGING={os.environ.get('MELD_LOGGING')}")
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Enable console output
        file: Enable file output
        colored: Use colored console output
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    if console:
        if colored and sys.platform != "win32":  # Colored output may not work on Windows
            console_handler = ColoredConsoleHandler(sys.stdout)
        else:
            console_handler = logging.StreamHandler(sys.stdout)

        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))
        root_logger.addHandler(console_handler)

    # File handler for general logs
    if file:
        file_handler = logging.handlers.RotatingFileHandler(
            APP_LOG_FILE, maxBytes=LOG_FILE_MAX_BYTES, backupCount=5  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
        root_logger.addHandler(file_handler)

        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE, maxBytes=ERROR_LOG_FILE_MAX_BYTES, backupCount=3  # 5MB
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
        root_logger.addHandler(error_handler)

    # Set levels for specific loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)  # Reduce Flask noise
    logging.getLogger("dash").setLevel(logging.WARNING)  # Reduce Dash noise

    root_logger.info(f"Logging initialized - Level: {level}, Console: {console}, File: {file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Performance and security logger instances
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()


# Decorators for logging
def log_execution_time(func):
    """Decorator to log function execution time."""
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000
            performance_logger.log_operation(f"{func.__module__}.{func.__name__}", duration)
            return result
        except Exception as e:
            duration = (time.time() - start) * 1000
            performance_logger.log_operation(
                f"{func.__module__}.{func.__name__} (failed)", duration, {"error": str(e)}
            )
            raise

    return wrapper


def log_errors(logger_name: Optional[str] = None):
    """Decorator to log function errors."""
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise

        return wrapper

    return decorator


# Initialize logging on import
if os.environ.get("MELD_LOGGING", "true").lower() != "false":
    setup_logging(level=os.environ.get("LOG_LEVEL", "INFO"), console=True, file=True, colored=True)
