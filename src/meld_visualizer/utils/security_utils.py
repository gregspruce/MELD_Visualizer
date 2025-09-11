"""
Security utilities for the MELD Visualizer application.
Provides secure file handling, input validation, and configuration management.
"""

import base64
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Import security constants from centralized location
from ..constants import (
    ALLOWED_FILE_EXTENSIONS,
    MAX_CONFIG_LIST_LENGTH,
    MAX_CONFIG_SIZE_KB,
    MAX_FILE_SIZE_MB,
    MAX_GCODE_LINE_LENGTH,
    MAX_GCODE_WORD_LENGTH,
    SAFE_CONFIG_KEYS,
)

# Configure logging
logger = logging.getLogger(__name__)

# Regex patterns with timeout protection
SAFE_GCODE_PATTERN = re.compile(r"^([A-Z])([-+]?\d{0,10}(?:\.\d{0,6})?)$")

# Import standardized error handling


class FileValidator:
    """Validates uploaded files for security risks."""

    @staticmethod
    def validate_file_upload(contents: str, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file for security risks.

        Args:
            contents: Base64 encoded file content
            filename: Name of the uploaded file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check filename for path traversal attempts
            if ".." in filename or "/" in filename or "\\" in filename:
                return False, "Invalid filename: Path traversal detected"

            # Check file extension
            ext = Path(filename).suffix.lower()
            if ext not in ALLOWED_FILE_EXTENSIONS:
                return (
                    False,
                    f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_EXTENSIONS)}",
                )

            # Decode and check file size
            try:
                _, content_string = contents.split(",", 1)
                decoded = base64.b64decode(content_string)
            except (ValueError, IndexError):
                return False, "Invalid file format"

            size_mb = len(decoded) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                return False, f"File too large. Maximum size: {MAX_FILE_SIZE_MB} MB"

            # Check for suspicious content patterns
            content_str = decoded.decode("utf-8", errors="ignore")

            # Check for script injection attempts
            suspicious_patterns = [
                r"<script",
                r"javascript:",
                r"onerror=",
                r"onclick=",
                r"eval\(",
                r"exec\(",
                r"__import__",
                r"subprocess",
            ]

            for pattern in suspicious_patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    return False, "File contains suspicious content"

            return True, None

        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False, "File validation failed"


class InputValidator:
    """Validates and sanitizes user inputs."""

    @staticmethod
    def sanitize_numeric_input(
        value: Any, min_val: float = None, max_val: float = None, default: float = 0
    ) -> float:
        """
        Sanitize numeric input values.

        Args:
            value: Input value to sanitize
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            default: Default value if validation fails

        Returns:
            Sanitized float value
        """
        try:
            num_val = float(value)

            # Check for special values
            if not (-1e308 < num_val < 1e308):  # Prevent infinity
                return default

            if min_val is not None and num_val < min_val:
                return min_val
            if max_val is not None and num_val > max_val:
                return max_val

            return num_val

        except (TypeError, ValueError):
            return default

    @staticmethod
    def sanitize_column_name(column_name: str, allowed_columns: list) -> Optional[str]:
        """
        Validate column name against allowed list.

        Args:
            column_name: Column name to validate
            allowed_columns: List of allowed column names

        Returns:
            Sanitized column name or None if invalid
        """
        if not column_name or not isinstance(column_name, str):
            return None

        # Remove any special characters that could cause issues
        clean_name = re.sub(r"[^\w\s-]", "", column_name)

        if clean_name in allowed_columns:
            return clean_name

        return None

    @staticmethod
    def sanitize_gcode_line(line: str) -> Optional[str]:
        """
        Sanitize a G-code line to prevent regex DoS.

        Args:
            line: G-code line to sanitize

        Returns:
            Sanitized line or None if invalid
        """
        if not line or len(line) > MAX_GCODE_LINE_LENGTH:
            return None

        # Remove comments safely - handle both () and ; style comments
        if "(" in line and ")" in line:
            # Remove content between parentheses
            start = line.find("(")
            end = line.find(")", start)
            line = (line[:start] + line[end + 1 :]).strip()
        elif "(" in line:
            # If only opening paren, remove from there to end
            line = line[: line.find("(")].strip()
        if ";" in line:
            line = line[: line.find(";")].strip()

        if not line:  # If nothing left after removing comments
            return None

        # Validate each word separately to prevent ReDoS
        words = line.upper().split()
        sanitized_words = []

        for word in words:
            if len(word) > MAX_GCODE_WORD_LENGTH:  # Reasonable max length for a G-code word
                continue

            # Check if it matches safe pattern
            if SAFE_GCODE_PATTERN.match(word):
                sanitized_words.append(word)

        return " ".join(sanitized_words) if sanitized_words else None


class ConfigurationManager:
    """Secure configuration file management."""

    @staticmethod
    def save_config(
        config_data: Dict[str, Any], config_path: str = "config.json"
    ) -> Tuple[bool, str]:
        """
        Securely save configuration data.

        Args:
            config_data: Configuration dictionary to save
            config_path: Path to configuration file

        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate config path
            config_path = Path(config_path)
            if config_path.is_absolute():
                return False, "Absolute paths not allowed for configuration"

            # Ensure we're writing to the correct directory
            safe_path = Path.cwd() / config_path.name

            # Validate configuration keys
            invalid_keys = set(config_data.keys()) - SAFE_CONFIG_KEYS
            if invalid_keys:
                return False, f"Invalid configuration keys: {invalid_keys}"

            # Validate configuration values
            for key, value in config_data.items():
                if not ConfigurationManager._validate_config_value(key, value):
                    return False, f"Invalid value for configuration key: {key}"

            # Check size limit
            config_json = json.dumps(config_data)
            if len(config_json) > MAX_CONFIG_SIZE_KB * 1024:
                return False, "Configuration file too large"

            # Write atomically using temp file
            temp_path = safe_path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(config_data, f, indent=2)

            # Atomic rename
            temp_path.replace(safe_path)

            return True, "Configuration saved successfully"

        except Exception as e:
            logger.error(f"Configuration save error: {e}")
            return False, "Failed to save configuration"

    @staticmethod
    def _validate_config_value(key: str, value: Any) -> bool:
        """Validate individual configuration values."""
        if key == "default_theme":
            return isinstance(value, str) and len(value) < 100
        elif key == "plotly_template":
            return isinstance(value, str) and len(value) < 100
        elif key in [
            "graph_1_options",
            "graph_2_options",
            "plot_2d_y_options",
            "plot_2d_color_options",
        ]:
            return (
                isinstance(value, list)
                and len(value) < MAX_CONFIG_LIST_LENGTH
                and all(isinstance(item, str) and len(item) < 100 for item in value)
            )
        return False

    @staticmethod
    def load_config(
        config_path: str = "config.json", default_config: Dict = None
    ) -> Dict[str, Any]:
        """
        Securely load configuration file.

        Args:
            config_path: Path to configuration file
            default_config: Default configuration to use if loading fails

        Returns:
            Configuration dictionary
        """
        try:
            # Validate path
            config_path = Path(config_path)
            if config_path.is_absolute() or ".." in str(config_path):
                logger.warning("Invalid config path, using defaults")
                return default_config or {}

            safe_path = Path.cwd() / config_path.name

            if not safe_path.exists():
                return default_config or {}

            # Check file size
            if safe_path.stat().st_size > MAX_CONFIG_SIZE_KB * 1024:
                logger.warning("Config file too large, using defaults")
                return default_config or {}

            with open(safe_path, "r") as f:
                user_config = json.load(f)

            # Validate loaded config
            safe_config = {}
            for key in SAFE_CONFIG_KEYS:
                if key in user_config:
                    if ConfigurationManager._validate_config_value(key, user_config[key]):
                        safe_config[key] = user_config[key]

            # Merge with defaults
            if default_config:
                return {**default_config, **safe_config}
            return safe_config

        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Configuration load error: {e}")
            return default_config or {}


class ErrorHandler:
    """Secure error handling and user messaging."""

    @staticmethod
    def handle_error(error: Exception, user_friendly: bool = True) -> str:
        """
        Handle errors securely without exposing sensitive information.

        Args:
            error: The exception that occurred
            user_friendly: Whether to return user-friendly message

        Returns:
            Error message string
        """
        # Log the full error for debugging
        logger.error(f"Application error: {error}", exc_info=True)

        if not user_friendly:
            return str(error)

        # Map specific errors to user-friendly messages
        error_messages = {
            FileNotFoundError: "The requested file could not be found.",
            PermissionError: "Permission denied. Please check file permissions.",
            ValueError: "Invalid input provided. Please check your data.",
            KeyError: "Required data field is missing.",
            MemoryError: "Operation requires too much memory. Try with smaller data.",
        }

        for error_type, message in error_messages.items():
            if isinstance(error, error_type):
                return f"Error: {message}"

        # Generic message for unknown errors
        return "An error occurred while processing your request. Please try again."


# Utility functions for easy integration


def secure_parse_gcode(content: str, max_lines: int = 100000) -> Tuple[Optional[list], str]:
    """
    Securely parse G-code content with protection against DoS.

    Args:
        content: G-code content as string
        max_lines: Maximum number of lines to process

    Returns:
        Tuple of (parsed_lines, error_message)
    """
    try:
        lines = content.splitlines()

        if len(lines) > max_lines:
            return None, f"File too large. Maximum {max_lines} lines allowed."

        sanitized_lines = []
        for line in lines:
            sanitized = InputValidator.sanitize_gcode_line(line)
            if sanitized:
                sanitized_lines.append(sanitized)

        return sanitized_lines, ""

    except Exception as e:
        logger.error(f"G-code parsing error: {e}")
        return None, "Failed to parse G-code file"
