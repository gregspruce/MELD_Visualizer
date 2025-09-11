"""
Test suite for standardized error handling utilities.
Tests the error handling framework, custom exceptions, and logging patterns.
"""

import logging
from unittest.mock import Mock, patch

import pytest

from src.meld_visualizer.utils.error_handling import (
    DataProcessingError,
    ErrorCode,
    ErrorContext,
    ErrorLogger,
    MELDVisualizerError,
    SecurityError,
    ServiceError,
    ValidationError,
    VisualizationError,
    handle_errors,
    safe_execute,
    validate_file_path,
    validate_numeric_range,
    validate_required_fields,
)


class TestErrorCode:
    """Test error code enumeration."""

    def test_error_code_values(self):
        """Test error code values are properly defined."""
        assert ErrorCode.UNKNOWN_ERROR.value == "E1000"
        assert ErrorCode.DATA_PARSING_ERROR.value == "E1100"
        assert ErrorCode.MESH_GENERATION_ERROR.value == "E1200"
        assert ErrorCode.FILE_VALIDATION_ERROR.value == "E1300"
        assert ErrorCode.CACHE_ERROR.value == "E1400"

    def test_error_code_coverage(self):
        """Test that all major error categories are covered."""
        codes = [code.value for code in ErrorCode]

        # Check coverage of major categories
        assert any(code.startswith("E10") for code in codes)  # General errors
        assert any(code.startswith("E11") for code in codes)  # Data processing
        assert any(code.startswith("E12") for code in codes)  # Visualization
        assert any(code.startswith("E13") for code in codes)  # Security
        assert any(code.startswith("E14") for code in codes)  # Service


class TestMELDVisualizerError:
    """Test base MELD visualizer error class."""

    def test_basic_error_creation(self):
        """Test basic error creation with minimal parameters."""
        error = MELDVisualizerError("Test error message")

        assert str(error) == "Test error message"
        assert error.error_code == ErrorCode.UNKNOWN_ERROR
        assert error.user_message == "An unexpected error occurred. Please try again."
        assert error.context == {}
        assert error.cause is None

    def test_error_with_all_parameters(self):
        """Test error creation with all parameters."""
        cause = ValueError("Original cause")
        context = {"file": "test.csv", "line": 42}

        error = MELDVisualizerError(
            "Technical error message",
            error_code=ErrorCode.DATA_PARSING_ERROR,
            user_message="Custom user message",
            context=context,
            cause=cause,
        )

        assert str(error) == "Technical error message"
        assert error.error_code == ErrorCode.DATA_PARSING_ERROR
        assert error.user_message == "Custom user message"
        assert error.context == context
        assert error.cause == cause

    def test_error_to_dict(self):
        """Test error serialization to dictionary."""
        cause = ValueError("Original cause")
        context = {"test": "value"}

        error = MELDVisualizerError(
            "Test message", error_code=ErrorCode.INVALID_INPUT, context=context, cause=cause
        )

        error_dict = error.to_dict()

        assert error_dict["error_code"] == "E1001"
        assert error_dict["technical_message"] == "Test message"
        assert error_dict["context"] == context
        assert error_dict["cause"] == "Original cause"

    def test_default_user_messages(self):
        """Test default user message generation."""
        test_cases = [
            (ErrorCode.INVALID_INPUT, "The provided input is invalid"),
            (ErrorCode.FILE_FORMAT_ERROR, "The uploaded file format is not supported"),
            (ErrorCode.DATA_PARSING_ERROR, "Unable to parse the data file"),
            (ErrorCode.MESH_GENERATION_ERROR, "Failed to generate 3D visualization"),
            (ErrorCode.FILE_VALIDATION_ERROR, "The uploaded file failed security validation"),
            (ErrorCode.CONFIGURATION_ERROR, "Configuration error detected"),
        ]

        for error_code, expected_fragment in test_cases:
            error = MELDVisualizerError("Technical message", error_code=error_code)
            assert expected_fragment in error.user_message


class TestSpecificErrors:
    """Test specific error subclasses."""

    def test_data_processing_error(self):
        """Test DataProcessingError defaults."""
        error = DataProcessingError("Data error")
        assert error.error_code == ErrorCode.DATA_PARSING_ERROR
        assert isinstance(error, MELDVisualizerError)

    def test_validation_error(self):
        """Test ValidationError defaults."""
        error = ValidationError("Validation failed")
        assert error.error_code == ErrorCode.DATA_VALIDATION_ERROR
        assert isinstance(error, MELDVisualizerError)

    def test_visualization_error(self):
        """Test VisualizationError defaults."""
        error = VisualizationError("Visualization failed")
        assert error.error_code == ErrorCode.MESH_GENERATION_ERROR
        assert isinstance(error, MELDVisualizerError)

    def test_security_error(self):
        """Test SecurityError defaults."""
        error = SecurityError("Security violation")
        assert error.error_code == ErrorCode.FILE_VALIDATION_ERROR
        assert isinstance(error, MELDVisualizerError)

    def test_service_error(self):
        """Test ServiceError defaults."""
        error = ServiceError("Service unavailable")
        assert error.error_code == ErrorCode.CACHE_ERROR
        assert isinstance(error, MELDVisualizerError)


class TestErrorLogger:
    """Test centralized error logging."""

    def test_log_meld_error(self):
        """Test logging of MELD visualizer errors."""
        mock_logger = Mock()

        error = MELDVisualizerError(
            "Test error", error_code=ErrorCode.DATA_PARSING_ERROR, context={"file": "test.csv"}
        )

        ErrorLogger.log_error(mock_logger, error)

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args

        # Check log level
        assert call_args[0][0] == logging.ERROR

        # Check log message format
        assert "[E1100]" in call_args[0][1]
        assert "Test error" in call_args[0][1]

        # Check extra fields
        extra = call_args[1]["extra"]
        assert extra["error_code"] == "E1100"
        assert "file" in extra["context"]

    def test_log_generic_error(self):
        """Test logging of generic Python errors."""
        mock_logger = Mock()

        error = ValueError("Generic error")
        context = {"operation": "test"}

        ErrorLogger.log_error(mock_logger, error, context)

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args

        assert call_args[0][0] == logging.ERROR
        assert "[E1000]" in call_args[0][1]
        assert "Generic error" in call_args[0][1]
        assert call_args[1]["extra"]["context"] == context

    def test_log_warning(self):
        """Test warning logging."""
        mock_logger = Mock()
        context = {"test": "value"}

        ErrorLogger.log_warning(mock_logger, "Warning message", context)

        mock_logger.warning.assert_called_once_with("Warning message", extra={"context": context})

    def test_log_info(self):
        """Test info logging."""
        mock_logger = Mock()
        context = {"operation": "success"}

        ErrorLogger.log_info(mock_logger, "Info message", context)

        mock_logger.info.assert_called_once_with("Info message", extra={"context": context})


class TestErrorDecorator:
    """Test error handling decorator."""

    def test_handle_errors_success(self):
        """Test decorator allows successful execution."""

        @handle_errors()
        def successful_function(x, y):
            return x + y

        result = successful_function(2, 3)
        assert result == 5

    def test_handle_errors_meld_exception_passthrough(self):
        """Test decorator passes through MELD exceptions unchanged."""

        @handle_errors()
        def failing_function():
            raise DataProcessingError("Original MELD error")

        with pytest.raises(DataProcessingError) as exc_info:
            failing_function()

        assert str(exc_info.value) == "Original MELD error"
        assert exc_info.value.error_code == ErrorCode.DATA_PARSING_ERROR

    @patch("src.meld_visualizer.utils.error_handling.logging.getLogger")
    def test_handle_errors_generic_exception_conversion(self, mock_get_logger):
        """Test decorator converts generic exceptions to MELD exceptions."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @handle_errors(
            error_type=ValidationError,
            error_code=ErrorCode.INVALID_INPUT,
            user_message="Custom user message",
        )
        def failing_function():
            raise ValueError("Generic error")

        with pytest.raises(ValidationError) as exc_info:
            failing_function()

        assert exc_info.value.error_code == ErrorCode.INVALID_INPUT
        assert exc_info.value.user_message == "Custom user message"
        assert exc_info.value.cause.__class__ == ValueError
        assert str(exc_info.value.cause) == "Generic error"

    @patch("src.meld_visualizer.utils.error_handling.logging.getLogger")
    def test_handle_errors_logging_disabled(self, mock_get_logger):
        """Test decorator with logging disabled."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @handle_errors(log_errors=False)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(MELDVisualizerError):
            failing_function()

        # Should not have logged the error
        mock_logger.log.assert_not_called()


class TestSafeExecute:
    """Test safe execution utility."""

    def test_safe_execute_success(self):
        """Test successful function execution."""

        def success_func(x, y):
            return x * y

        result, error = safe_execute(success_func, 3, 4)

        assert result == 12
        assert error is None

    def test_safe_execute_meld_error(self):
        """Test safe execution with MELD error."""

        def failing_func():
            raise DataProcessingError("Test error")

        result, error = safe_execute(failing_func, default_return="fallback")

        assert result == "fallback"
        assert isinstance(error, DataProcessingError)
        assert str(error) == "Test error"

    def test_safe_execute_generic_error(self):
        """Test safe execution with generic error."""

        def failing_func():
            raise ValueError("Generic error")

        result, error = safe_execute(failing_func, default_return=None)

        assert result is None
        assert isinstance(error, MELDVisualizerError)
        assert error.cause.__class__ == ValueError

    def test_safe_execute_with_error_handler(self):
        """Test safe execution with custom error handler."""
        error_handler = Mock()

        def failing_func():
            raise ValueError("Test error")

        result, error = safe_execute(
            failing_func, default_return="default", error_handler=error_handler
        )

        error_handler.assert_called_once()
        assert isinstance(error_handler.call_args[0][0], MELDVisualizerError)


class TestErrorContext:
    """Test error context manager."""

    @patch("src.meld_visualizer.utils.error_handling.ErrorLogger")
    def test_error_context_success(self, mock_error_logger):
        """Test context manager with successful operation."""
        mock_logger = Mock()

        with ErrorContext("test operation", mock_logger):
            1 + 1

        # Should log start and completion
        assert mock_error_logger.log_info.call_count == 2
        start_call = mock_error_logger.log_info.call_args_list[0]
        end_call = mock_error_logger.log_info.call_args_list[1]

        assert "Starting operation: test operation" in start_call[0]
        assert "Completed operation: test operation" in end_call[0]

    @patch("src.meld_visualizer.utils.error_handling.ErrorLogger")
    def test_error_context_with_exception(self, mock_error_logger):
        """Test context manager with exception."""
        mock_logger = Mock()
        cleanup_func = Mock()

        with pytest.raises(ValueError):
            with ErrorContext("test operation", mock_logger, cleanup_func):
                raise ValueError("Test error")

        # Should log error and run cleanup
        mock_error_logger.log_error.assert_called_once()
        cleanup_func.assert_called_once()

    @patch("src.meld_visualizer.utils.error_handling.ErrorLogger")
    def test_error_context_cleanup_failure(self, mock_error_logger):
        """Test context manager handles cleanup failure gracefully."""
        mock_logger = Mock()

        def failing_cleanup():
            raise RuntimeError("Cleanup failed")

        with pytest.raises(ValueError):
            with ErrorContext("test operation", mock_logger, failing_cleanup):
                raise ValueError("Original error")

        # Should log both the original error and cleanup warning
        assert mock_error_logger.log_error.call_count == 1
        assert mock_error_logger.log_warning.call_count == 1


class TestValidationUtilities:
    """Test validation utility functions."""

    def test_validate_file_path_valid(self):
        """Test file path validation with valid paths."""
        # These should not raise exceptions
        validate_file_path("normal_file.txt")
        validate_file_path("folder/file.csv")

    def test_validate_file_path_invalid(self):
        """Test file path validation with invalid paths."""
        invalid_paths = [
            "../../../etc/passwd",
            "folder/../../../secret",
            "C:\\Windows\\System32",
            "/etc/passwd",
        ]

        for path in invalid_paths:
            with pytest.raises(SecurityError) as exc_info:
                validate_file_path(path)
            assert exc_info.value.error_code == ErrorCode.PATH_TRAVERSAL_ERROR

    def test_validate_numeric_range_valid(self):
        """Test numeric range validation with valid values."""
        # These should not raise exceptions
        validate_numeric_range(5, min_val=0, max_val=10)
        validate_numeric_range(0, min_val=0)
        validate_numeric_range(100, max_val=100)
        validate_numeric_range(3.14)

    def test_validate_numeric_range_invalid(self):
        """Test numeric range validation with invalid values."""
        # Test minimum violation
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_range(-1, min_val=0, name="test_value")

        assert "test_value (-1) is below minimum" in str(exc_info.value)

        # Test maximum violation
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_range(11, max_val=10, name="test_value")

        assert "test_value (11) exceeds maximum" in str(exc_info.value)

    def test_validate_required_fields_valid(self):
        """Test required fields validation with valid data."""
        data = {"name": "test", "age": 25, "email": "test@example.com"}
        required = ["name", "age"]

        # Should not raise exception
        validate_required_fields(data, required)

    def test_validate_required_fields_missing(self):
        """Test required fields validation with missing fields."""
        data = {"name": "test"}
        required = ["name", "age", "email"]

        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, required)

        error_message = str(exc_info.value)
        assert "Missing required fields:" in error_message
        assert "age" in error_message
        assert "email" in error_message

    def test_validate_required_fields_none_values(self):
        """Test required fields validation with None values."""
        data = {"name": "test", "age": None}
        required = ["name", "age"]

        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, required)

        assert "age" in str(exc_info.value)


class TestErrorHandlingIntegration:
    """Integration tests for error handling system."""

    def test_end_to_end_error_flow(self):
        """Test complete error handling flow from creation to logging."""

        @handle_errors(error_type=DataProcessingError, error_code=ErrorCode.DATA_PARSING_ERROR)
        def process_data(data):
            if not data:
                raise ValueError("Empty data")
            return data.upper()

        # Test success case
        result = process_data("test")
        assert result == "TEST"

        # Test error case
        with pytest.raises(DataProcessingError) as exc_info:
            process_data("")

        error = exc_info.value
        assert error.error_code == ErrorCode.DATA_PARSING_ERROR
        assert error.cause.__class__ == ValueError
        assert "Empty data" in str(error.cause)

    def test_error_chaining_preservation(self):
        """Test that error chaining preserves original stack traces."""

        def inner_function():
            raise ValueError("Original error")

        def middle_function():
            try:
                inner_function()
            except ValueError as e:
                raise DataProcessingError("Middle error", cause=e)

        with pytest.raises(DataProcessingError) as exc_info:
            middle_function()

        error = exc_info.value
        assert str(error) == "Middle error"
        assert error.cause.__class__ == ValueError
        assert str(error.cause) == "Original error"
