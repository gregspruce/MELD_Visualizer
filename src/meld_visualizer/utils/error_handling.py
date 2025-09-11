"""
Standardized error handling utilities for MELD Visualizer.
Provides consistent error patterns, logging, and user feedback across all modules.
"""

import logging
from contextlib import AbstractContextManager
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast

from typing_extensions import Literal, ParamSpec

# Type variables for generic typing
P = ParamSpec("P")  # For preserving function parameter types
T = TypeVar("T")  # For generic return types
F = TypeVar("F", bound=Callable[..., Any])  # For decorator function types


class ErrorCode(Enum):
    """Standardized error codes for programmatic error handling."""

    # General errors (1000-1099)
    UNKNOWN_ERROR = "E1000"
    INVALID_INPUT = "E1001"
    MISSING_DEPENDENCY = "E1002"
    CONFIGURATION_ERROR = "E1003"

    # Data processing errors (1100-1199)
    DATA_PARSING_ERROR = "E1100"
    DATA_VALIDATION_ERROR = "E1101"
    FILE_FORMAT_ERROR = "E1102"
    DATA_CONVERSION_ERROR = "E1103"
    GCODE_PARSING_ERROR = "E1104"

    # Visualization errors (1200-1299)
    MESH_GENERATION_ERROR = "E1200"
    PLOT_CREATION_ERROR = "E1201"
    VOLUME_CALCULATION_ERROR = "E1202"

    # Security errors (1300-1399)
    FILE_VALIDATION_ERROR = "E1300"
    PATH_TRAVERSAL_ERROR = "E1301"
    FILE_SIZE_ERROR = "E1302"
    PERMISSION_ERROR = "E1303"

    # Service errors (1400-1499)
    CACHE_ERROR = "E1400"
    NETWORK_ERROR = "E1401"
    STORAGE_ERROR = "E1402"


class MELDVisualizerError(Exception):
    """Base exception class for MELD Visualizer applications."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.error_code: ErrorCode = error_code
        self.user_message: str = user_message or self._get_default_user_message()
        self.context: Dict[str, Any] = context or {}
        self.cause: Optional[Exception] = cause

    def _get_default_user_message(self) -> str:
        """Get a user-friendly error message based on error code."""
        user_messages: Dict[ErrorCode, str] = {
            ErrorCode.UNKNOWN_ERROR: "An unexpected error occurred. Please try again.",
            ErrorCode.INVALID_INPUT: "The provided input is invalid. Please check your data.",
            ErrorCode.FILE_FORMAT_ERROR: "The uploaded file format is not supported.",
            ErrorCode.DATA_PARSING_ERROR: "Unable to parse the data file. Please check the format.",
            ErrorCode.MESH_GENERATION_ERROR: "Failed to generate 3D visualization. Please try with different data.",
            ErrorCode.FILE_VALIDATION_ERROR: "The uploaded file failed security validation.",
            ErrorCode.CONFIGURATION_ERROR: "Configuration error detected. Please check your settings.",
        }
        return user_messages.get(
            self.error_code, "An error occurred while processing your request."
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error_code": self.error_code.value,
            "technical_message": str(self),
            "user_message": self.user_message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class DataProcessingError(MELDVisualizerError):
    """Exception for data processing and parsing errors."""

    def __init__(
        self, message: str, error_code: ErrorCode = ErrorCode.DATA_PARSING_ERROR, **kwargs: Any
    ) -> None:
        super().__init__(message, error_code, **kwargs)


class ValidationError(MELDVisualizerError):
    """Exception for data validation errors."""

    def __init__(
        self, message: str, error_code: ErrorCode = ErrorCode.DATA_VALIDATION_ERROR, **kwargs: Any
    ) -> None:
        super().__init__(message, error_code, **kwargs)


class VisualizationError(MELDVisualizerError):
    """Exception for visualization and mesh generation errors."""

    def __init__(
        self, message: str, error_code: ErrorCode = ErrorCode.MESH_GENERATION_ERROR, **kwargs: Any
    ) -> None:
        super().__init__(message, error_code, **kwargs)


class SecurityError(MELDVisualizerError):
    """Exception for security-related issues."""

    def __init__(
        self, message: str, error_code: ErrorCode = ErrorCode.FILE_VALIDATION_ERROR, **kwargs: Any
    ) -> None:
        super().__init__(message, error_code, **kwargs)


class ServiceError(MELDVisualizerError):
    """Exception for service layer errors (cache, network, storage)."""

    def __init__(
        self, message: str, error_code: ErrorCode = ErrorCode.CACHE_ERROR, **kwargs: Any
    ) -> None:
        super().__init__(message, error_code, **kwargs)


class ErrorLogger:
    """Centralized error logging with consistent formatting."""

    @staticmethod
    def log_error(
        logger: logging.Logger,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: int = logging.ERROR,
    ) -> None:
        """Log an error with consistent formatting and context."""

        if isinstance(error, MELDVisualizerError):
            error_dict = error.to_dict()
            log_message = f"[{error.error_code.value}] {error_dict['technical_message']}"

            if context:
                error_dict["context"].update(context)

            logger.log(
                level,
                log_message,
                extra={
                    "error_code": error.error_code.value,
                    "user_message": error.user_message,
                    "context": error_dict["context"],
                    "cause": error_dict["cause"],
                },
                exc_info=True if error.cause else False,
            )
        else:
            # Handle non-MELD errors
            logger.log(
                level,
                f"[{ErrorCode.UNKNOWN_ERROR.value}] {str(error)}",
                extra={"context": context or {}},
                exc_info=True,
            )

    @staticmethod
    def log_warning(
        logger: logging.Logger, message: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a warning with consistent formatting."""
        logger.warning(message, extra={"context": context or {}})

    @staticmethod
    def log_info(
        logger: logging.Logger, message: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an info message with consistent formatting."""
        logger.info(message, extra={"context": context or {}})


def handle_errors(
    error_type: Type[MELDVisualizerError] = MELDVisualizerError,
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    user_message: Optional[str] = None,
    log_errors: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for standardized error handling."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            logger: logging.Logger = logging.getLogger(func.__module__)

            try:
                return func(*args, **kwargs)
            except MELDVisualizerError:
                # Re-raise MELD errors without modification
                raise
            except Exception as e:
                # Convert generic exceptions to MELD exceptions
                context: Dict[str, Any] = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args": str(args)[:200],  # Truncate for logging
                    "kwargs": str(kwargs)[:200],
                }

                meld_error: MELDVisualizerError = error_type(
                    message=f"Error in {func.__name__}: {str(e)}",
                    error_code=error_code,
                    user_message=user_message,
                    context=context,
                    cause=e,
                )

                if log_errors:
                    ErrorLogger.log_error(logger, meld_error)

                raise meld_error

        return cast(Callable[P, T], wrapper)

    return decorator


def safe_execute(
    func: Callable[..., T],
    *args: Any,
    default_return: Optional[T] = None,
    error_handler: Optional[Callable[[MELDVisualizerError], None]] = None,
    log_errors: bool = True,
    **kwargs: Any,
) -> Tuple[Optional[T], Optional[MELDVisualizerError]]:
    """
    Safely execute a function and return (result, error) tuple.

    Args:
        func: Function to execute
        *args: Arguments for function
        default_return: Value to return if function fails
        error_handler: Optional custom error handler
        log_errors: Whether to log errors
        **kwargs: Keyword arguments for function

    Returns:
        Tuple of (result, error). If successful, error is None.
        If failed, result is default_return and error contains the exception.
    """
    logger: logging.Logger = logging.getLogger(
        func.__module__ if hasattr(func, "__module__") else __name__
    )

    try:
        result: T = func(*args, **kwargs)
        return result, None
    except MELDVisualizerError as e:
        if log_errors:
            ErrorLogger.log_error(logger, e)
        if error_handler:
            error_handler(e)
        return default_return, e
    except Exception as e:
        # Convert to MELD error
        meld_error: MELDVisualizerError = MELDVisualizerError(
            message=f"Unexpected error in {getattr(func, '__name__', 'unknown')}: {str(e)}",
            cause=e,
            context={
                "function": getattr(func, "__name__", "unknown"),
                "args": str(args)[:200],
                "kwargs": str(kwargs)[:200],
            },
        )

        if log_errors:
            ErrorLogger.log_error(logger, meld_error)
        if error_handler:
            error_handler(meld_error)

        return default_return, meld_error


class ErrorContext(AbstractContextManager["ErrorContext"]):
    """Context manager for error handling with resource cleanup."""

    def __init__(
        self,
        operation_name: str,
        logger: logging.Logger,
        cleanup_func: Optional[Callable[[], None]] = None,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    ) -> None:
        self.operation_name: str = operation_name
        self.logger: logging.Logger = logger
        self.cleanup_func: Optional[Callable[[], None]] = cleanup_func
        self.error_code: ErrorCode = error_code

    def __enter__(self) -> "ErrorContext":
        ErrorLogger.log_info(self.logger, f"Starting operation: {self.operation_name}")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> Literal[False]:
        if exc_type is not None:
            if not isinstance(exc_val, MELDVisualizerError):
                # Convert to MELD error
                meld_error: MELDVisualizerError = MELDVisualizerError(
                    message=f"Error in {self.operation_name}: {str(exc_val)}",
                    error_code=self.error_code,
                    context={"operation": self.operation_name},
                    cause=exc_val if isinstance(exc_val, Exception) else None,
                )
                ErrorLogger.log_error(self.logger, meld_error)
            else:
                ErrorLogger.log_error(self.logger, exc_val)

        # Always run cleanup
        if self.cleanup_func:
            try:
                self.cleanup_func()
            except Exception as cleanup_error:
                ErrorLogger.log_warning(
                    self.logger, f"Cleanup failed for {self.operation_name}: {str(cleanup_error)}"
                )

        ErrorLogger.log_info(self.logger, f"Completed operation: {self.operation_name}")

        return False  # Don't suppress exceptions


# Utility functions for common error patterns
def validate_file_path(path: str) -> None:
    """Validate file path for security issues."""
    # Check for path traversal attempts - allow normal forward slashes but block traversal
    if ".." in path or path.startswith("/") or "\\" in path:
        raise SecurityError(
            f"Invalid file path detected: {path}",
            error_code=ErrorCode.PATH_TRAVERSAL_ERROR,
            context={"path": path},
        )


def validate_numeric_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    name: str = "value",
) -> None:
    """Validate numeric value is within specified range."""
    if min_val is not None and value < min_val:
        raise ValidationError(
            f"{name} ({value}) is below minimum allowed value ({min_val})",
            context={"value": value, "min_val": min_val, "field_name": name},
        )

    if max_val is not None and value > max_val:
        raise ValidationError(
            f"{name} ({value}) exceeds maximum allowed value ({max_val})",
            context={"value": value, "max_val": max_val, "field_name": name},
        )


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that all required fields are present in data."""
    missing_fields: List[str] = [
        field for field in required_fields if field not in data or data[field] is None
    ]

    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            context={"missing_fields": missing_fields, "provided_fields": list(data.keys())},
        )
