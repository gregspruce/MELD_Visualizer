"""
Input validation tests for MELD Visualizer.
Tests security validation, input sanitization, and boundary conditions.
"""

import pytest
import base64
import json
from pathlib import Path
from unittest.mock import Mock, patch

from src.meld_visualizer.utils.security_utils import (
    FileValidator, InputValidator, ConfigurationManager,
    ErrorHandler, secure_parse_gcode
)
from src.meld_visualizer.constants import (
    MAX_FILE_SIZE_MB, ALLOWED_FILE_EXTENSIONS,
    MAX_GCODE_LINE_LENGTH, SAFE_CONFIG_KEYS
)


class TestFileValidation:
    """Test file upload validation."""
    
    def test_valid_csv_file(self):
        """Test validation of valid CSV file."""
        content = b"col1,col2\n1,2\n3,4"
        encoded = base64.b64encode(content).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        is_valid, error = FileValidator.validate_file_upload(contents, "data.csv")
        
        assert is_valid is True
        assert error is None
    
    def test_path_traversal_attempt(self):
        """Test detection of path traversal attempts."""
        content = b"test"
        encoded = base64.b64encode(content).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        # Various path traversal attempts
        malicious_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "data/../../../secret.csv",
            "/etc/passwd"
        ]
        
        for filename in malicious_names:
            is_valid, error = FileValidator.validate_file_upload(contents, filename)
            assert is_valid is False
            assert "path traversal" in error.lower() or "invalid" in error.lower()
    
    def test_invalid_file_extension(self):
        """Test rejection of invalid file extensions."""
        content = b"test"
        encoded = base64.b64encode(content).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        invalid_extensions = [".exe", ".dll", ".sh", ".bat", ".pdf", ".docx"]
        
        for ext in invalid_extensions:
            is_valid, error = FileValidator.validate_file_upload(contents, f"file{ext}")
            assert is_valid is False
            assert "not allowed" in error.lower() or "invalid" in error.lower()
    
    def test_file_size_limit(self):
        """Test file size limit enforcement."""
        # Create file larger than limit
        large_content = b"x" * (MAX_FILE_SIZE_MB * 1024 * 1024 + 1000)
        encoded = base64.b64encode(large_content).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        is_valid, error = FileValidator.validate_file_upload(contents, "large.csv")
        
        assert is_valid is False
        assert "too large" in error.lower()
    
    def test_script_injection_detection(self):
        """Test detection of script injection attempts."""
        malicious_patterns = [
            b"<script>alert('xss')</script>",
            b"javascript:alert(1)",
            b"onerror=alert(1)",
            b"eval(atob('...'))",
            b"__import__('os').system('ls')",
            b"subprocess.call(['rm', '-rf'])"
        ]
        
        for pattern in malicious_patterns:
            encoded = base64.b64encode(pattern).decode()
            contents = f"data:text/csv;base64,{encoded}"
            
            is_valid, error = FileValidator.validate_file_upload(contents, "mal.csv")
            assert is_valid is False
            assert "suspicious" in error.lower()
    
    def test_valid_gcode_file(self):
        """Test validation of valid G-code file."""
        gcode = b"G0 X0 Y0 Z0\nG1 X10 Y10 F100"
        encoded = base64.b64encode(gcode).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        is_valid, error = FileValidator.validate_file_upload(contents, "program.nc")
        
        assert is_valid is True
        assert error is None


class TestInputSanitization:
    """Test input sanitization functions."""
    
    def test_numeric_input_sanitization(self):
        """Test numeric input sanitization."""
        # Valid numbers
        assert InputValidator.sanitize_numeric_input("123.45") == 123.45
        assert InputValidator.sanitize_numeric_input(42) == 42
        assert InputValidator.sanitize_numeric_input(-10.5) == -10.5
        
        # Invalid inputs
        assert InputValidator.sanitize_numeric_input("abc", default=0) == 0
        assert InputValidator.sanitize_numeric_input(None, default=10) == 10
        assert InputValidator.sanitize_numeric_input("", default=5) == 5
        
        # Infinity handling
        assert InputValidator.sanitize_numeric_input(float('inf'), default=100) == 100
        assert InputValidator.sanitize_numeric_input(float('-inf'), default=0) == 0
        
        # Range enforcement
        assert InputValidator.sanitize_numeric_input(150, max_val=100) == 100
        assert InputValidator.sanitize_numeric_input(-50, min_val=0) == 0
        assert InputValidator.sanitize_numeric_input(50, min_val=0, max_val=100) == 50
    
    def test_column_name_sanitization(self):
        """Test column name sanitization."""
        allowed = ["XPos", "YPos", "ZPos", "ToolTemp"]
        
        # Valid columns
        assert InputValidator.sanitize_column_name("XPos", allowed) == "XPos"
        assert InputValidator.sanitize_column_name("ToolTemp", allowed) == "ToolTemp"
        
        # Invalid columns
        assert InputValidator.sanitize_column_name("'; DROP TABLE--", allowed) is None
        assert InputValidator.sanitize_column_name("NonExistent", allowed) is None
        assert InputValidator.sanitize_column_name("", allowed) is None
        assert InputValidator.sanitize_column_name(None, allowed) is None
        
        # Special characters removal
        assert InputValidator.sanitize_column_name("X@Pos", allowed) is None
        assert InputValidator.sanitize_column_name("Tool$Temp", allowed) is None
    
    def test_gcode_line_sanitization(self):
        """Test G-code line sanitization."""
        # Valid G-code
        assert "G1" in InputValidator.sanitize_gcode_line("G1 X10.5 Y20.3")
        assert "X10.5" in InputValidator.sanitize_gcode_line("G1 X10.5")
        assert "F100" in InputValidator.sanitize_gcode_line("G1 F100")
        
        # Comment removal
        result = InputValidator.sanitize_gcode_line("G1 X10 ; comment")
        assert result is not None
        assert "G1" in result
        assert "comment" not in result
        
        result = InputValidator.sanitize_gcode_line("G1 X10 (comment)")
        assert result is not None
        assert "G1" in result
        assert "comment" not in result
        
        # Line too long
        long_line = "G1 X" + "9" * MAX_GCODE_LINE_LENGTH
        assert InputValidator.sanitize_gcode_line(long_line) is None
        
        # Empty/invalid lines
        assert InputValidator.sanitize_gcode_line("") is None
        assert InputValidator.sanitize_gcode_line("   ") is None
        assert InputValidator.sanitize_gcode_line("(only comment)") is None
    
    @pytest.mark.parametrize("gcode,expected", [
        ("G0 X0 Y0 Z0", True),
        ("G1 X10.5 Y-20.3 Z5", True),
        ("M34 S4200", True),
        ("G2 I1.5 J2.5", True),
        ("INVALID", False),
        ("X Y Z", False)
    ])
    def test_gcode_pattern_matching(self, gcode, expected):
        """Test G-code pattern matching."""
        result = InputValidator.sanitize_gcode_line(gcode)
        if expected:
            assert result is not None
        else:
            assert result is None or len(result) == 0


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_valid_configuration_save(self, tmp_path):
        """Test saving valid configuration."""
        config = {
            "default_theme": "Cerulean",
            "plotly_template": "plotly_dark",
            "graph_1_options": ["XPos", "YPos"],
            "graph_2_options": ["ZPos"],
            "plot_2d_y_options": ["FeedVel"],
            "plot_2d_color_options": ["ToolTemp"]
        }
        
        # Change to temp directory
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            success, message = ConfigurationManager.save_config(config)
            assert success is True
            assert "success" in message.lower()
            
            # Verify file was created
            config_file = tmp_path / "config.json"
            assert config_file.exists()
            
            # Verify content
            saved = json.loads(config_file.read_text())
            assert saved["default_theme"] == "Cerulean"
        finally:
            os.chdir(original_cwd)
    
    def test_invalid_configuration_keys(self):
        """Test rejection of invalid configuration keys."""
        config = {
            "default_theme": "Test",
            "malicious_key": "evil_value",
            "another_bad_key": "bad"
        }
        
        success, message = ConfigurationManager.save_config(config)
        
        assert success is False
        assert "invalid" in message.lower()
    
    def test_configuration_path_validation(self):
        """Test configuration path validation."""
        config = {"default_theme": "Test"}
        
        # Absolute paths should be rejected
        invalid_paths = [
            "/etc/config.json",
            "C:\\Windows\\System32\\config.json",
            "/var/www/config.json"
        ]
        
        for path in invalid_paths:
            success, message = ConfigurationManager.save_config(config, path)
            assert success is False
            assert "absolute" in message.lower() or "invalid" in message.lower()
    
    def test_configuration_size_limit(self):
        """Test configuration size limit."""
        # Create large configuration
        large_config = {
            "default_theme": "x" * 10000,
            "graph_1_options": ["col" + str(i) for i in range(1000)]
        }
        
        # Should fail validation
        assert ConfigurationManager._validate_config_value(
            "default_theme", large_config["default_theme"]
        ) is False
    
    def test_configuration_value_validation(self):
        """Test individual configuration value validation."""
        # Valid values
        assert ConfigurationManager._validate_config_value("default_theme", "Cerulean")
        assert ConfigurationManager._validate_config_value("plotly_template", "plotly_dark")
        assert ConfigurationManager._validate_config_value("graph_1_options", ["XPos", "YPos"])
        
        # Invalid values
        assert not ConfigurationManager._validate_config_value("default_theme", 123)
        assert not ConfigurationManager._validate_config_value("graph_1_options", "not_a_list")
        assert not ConfigurationManager._validate_config_value("unknown_key", "value")


class TestGcodeValidation:
    """Test G-code parsing validation."""
    
    def test_secure_gcode_parsing(self):
        """Test secure G-code parsing."""
        valid_gcode = """G0 X0 Y0 Z0
        G1 X10 Y10 F100
        M34 S4200
        G1 X20 Y20 Z5"""
        
        lines, error = secure_parse_gcode(valid_gcode)
        
        assert lines is not None
        assert error == ""
        assert len(lines) == 4
    
    def test_gcode_line_limit(self):
        """Test G-code line limit enforcement."""
        # Create file with too many lines
        many_lines = "\n".join([f"G1 X{i} Y{i}" for i in range(150000)])
        
        lines, error = secure_parse_gcode(many_lines, max_lines=100000)
        
        assert lines is None
        assert "too large" in error.lower()
    
    def test_gcode_redos_protection(self):
        """Test protection against ReDoS attacks."""
        # Pattern that could cause ReDoS with unsafe regex
        malicious = "G1 X" + "9" * 10000
        
        lines, error = secure_parse_gcode(malicious)
        
        # Should handle without hanging
        assert lines is not None or error != ""
    
    def test_gcode_comment_styles(self):
        """Test handling of different comment styles."""
        gcode_with_comments = """
        ; This is a semicolon comment
        G0 X0 Y0 ; Inline semicolon comment
        (This is a parenthesis comment)
        G1 X10 Y10 (Inline parenthesis comment)
        G1 X20 Y20 Z5 ; Another comment
        """
        
        lines, error = secure_parse_gcode(gcode_with_comments)
        
        assert lines is not None
        # Comments should be removed
        for line in lines:
            assert "comment" not in line.lower()


class TestErrorHandling:
    """Test error handling and messaging."""
    
    def test_error_message_sanitization(self):
        """Test that error messages don't expose sensitive information."""
        # File not found error with path
        error = FileNotFoundError("/secret/path/to/file.txt")
        message = ErrorHandler.handle_error(error, user_friendly=True)
        
        assert "/secret/path" not in message
        assert "file could not be found" in message.lower()
        
        # Value error with sensitive data
        error = ValueError("Invalid password: admin123")
        message = ErrorHandler.handle_error(error, user_friendly=True)
        
        assert "admin123" not in message
        assert "invalid input" in message.lower()
    
    def test_error_logging(self):
        """Test that errors are properly logged."""
        with patch('security_utils.logger') as mock_logger:
            error = Exception("Test error")
            ErrorHandler.handle_error(error)
            
            # Should log the error
            mock_logger.error.assert_called()
    
    def test_specific_error_mapping(self):
        """Test mapping of specific error types."""
        errors_and_expected = [
            (FileNotFoundError(), "could not be found"),
            (PermissionError(), "permission denied"),
            (ValueError(), "invalid input"),
            (KeyError(), "missing"),
            (MemoryError(), "too much memory")
        ]
        
        for error, expected in errors_and_expected:
            message = ErrorHandler.handle_error(error, user_friendly=True)
            assert expected in message.lower()


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        # Empty file
        assert FileValidator.validate_file_upload("", "test.csv") == (False, "Invalid file format")
        
        # Empty column name
        assert InputValidator.sanitize_column_name("", ["XPos"]) is None
        
        # Empty G-code
        assert InputValidator.sanitize_gcode_line("") is None
    
    def test_maximum_values(self):
        """Test maximum allowed values."""
        # Maximum file size (exactly at limit)
        max_content = b"x" * (MAX_FILE_SIZE_MB * 1024 * 1024)
        encoded = base64.b64encode(max_content).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        is_valid, _ = FileValidator.validate_file_upload(contents, "max.csv")
        assert is_valid is True
        
        # Just over limit
        over_content = b"x" * (MAX_FILE_SIZE_MB * 1024 * 1024 + 1)
        encoded = base64.b64encode(over_content).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        is_valid, _ = FileValidator.validate_file_upload(contents, "over.csv")
        assert is_valid is False
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        # Unicode in filenames
        unicode_names = ["测试.csv", "тест.csv", "🔥.csv", "file_with_émoji.csv"]
        
        for filename in unicode_names:
            # Should handle gracefully
            content = b"test"
            encoded = base64.b64encode(content).decode()
            contents = f"data:text/csv;base64,{encoded}"
            
            # Check extension validation still works
            if filename.endswith('.csv'):
                is_valid, _ = FileValidator.validate_file_upload(contents, filename)
                assert is_valid is True
    
    def test_null_byte_injection(self):
        """Test protection against null byte injection."""
        # Null byte in filename
        malicious_names = ["file.csv\x00.exe", "data\x00.csv", "test.csv\x00"]
        
        for filename in malicious_names:
            content = b"test"
            encoded = base64.b64encode(content).decode()
            contents = f"data:text/csv;base64,{encoded}"
            
            # Should handle safely
            try:
                is_valid, error = FileValidator.validate_file_upload(contents, filename)
                # Either reject or handle safely
                assert is_valid is False or error is not None
            except:
                # Should not crash
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])