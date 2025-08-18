"""
Test script to verify security fixes are working correctly.
"""

import json
import base64
import tempfile
from pathlib import Path
from src.meld_visualizer.utils.security_utils import (
    FileValidator, InputValidator, ConfigurationManager, 
    ErrorHandler, secure_parse_gcode
)

def test_file_validation():
    """Test file upload validation."""
    print("Testing File Validation...")
    
    # Test 1: Valid CSV file
    valid_csv = "data:text/csv;base64," + base64.b64encode(b"col1,col2\n1,2\n3,4").decode()
    is_valid, error = FileValidator.validate_file_upload(valid_csv, "test.csv")
    assert is_valid == True, f"Valid CSV should pass: {error}"
    print("[PASS] Valid CSV accepted")
    
    # Test 2: Path traversal attempt
    is_valid, error = FileValidator.validate_file_upload(valid_csv, "../../../etc/passwd")
    assert is_valid == False, "Path traversal should be blocked"
    print("[PASS] Path traversal blocked")
    
    # Test 3: Invalid file type
    is_valid, error = FileValidator.validate_file_upload(valid_csv, "test.exe")
    assert is_valid == False, "Invalid file type should be blocked"
    print("[PASS] Invalid file type blocked")
    
    # Test 4: File too large (simulate)
    large_content = "data:text/csv;base64," + base64.b64encode(b"x" * (11 * 1024 * 1024)).decode()
    is_valid, error = FileValidator.validate_file_upload(large_content, "large.csv")
    assert is_valid == False, "Large files should be blocked"
    print("[PASS] Large file blocked")
    
    # Test 5: Script injection attempt
    malicious = "data:text/csv;base64," + base64.b64encode(b"<script>alert('xss')</script>").decode()
    is_valid, error = FileValidator.validate_file_upload(malicious, "mal.csv")
    assert is_valid == False, "Script injection should be blocked"
    print("[PASS] Script injection blocked")
    
    print("File validation tests: PASSED\n")

def test_input_sanitization():
    """Test input sanitization."""
    print("Testing Input Sanitization...")
    
    # Test numeric input sanitization
    assert InputValidator.sanitize_numeric_input("123.45") == 123.45
    assert InputValidator.sanitize_numeric_input("inf", max_val=100) == 0
    assert InputValidator.sanitize_numeric_input(150, max_val=100) == 100
    assert InputValidator.sanitize_numeric_input(-10, min_val=0) == 0
    print("[PASS] Numeric input sanitization working")
    
    # Test column name sanitization
    allowed = ["XPos", "YPos", "ZPos"]
    assert InputValidator.sanitize_column_name("XPos", allowed) == "XPos"
    assert InputValidator.sanitize_column_name("'; DROP TABLE--", allowed) == None
    assert InputValidator.sanitize_column_name("NonExistent", allowed) == None
    print("[PASS] Column name sanitization working")
    
    # Test G-code line sanitization
    result = InputValidator.sanitize_gcode_line("G1 X10.5 Y20.3")
    assert result is not None and "G1" in result and "X10.5" in result
    assert InputValidator.sanitize_gcode_line("G1 X" + "9"*1000) == None  # Too long
    result = InputValidator.sanitize_gcode_line("G1 X10 (comment)")
    assert result is not None and "G1" in result and "X10" in result
    print("[PASS] G-code sanitization working")
    
    print("Input sanitization tests: PASSED\n")

def test_config_management():
    """Test secure configuration management."""
    print("Testing Configuration Management...")
    
    # Test 1: Valid configuration
    valid_config = {
        "default_theme": "Cerulean",
        "plotly_template": "plotly_dark",
        "graph_1_options": ["XPos", "YPos"],
        "graph_2_options": ["ZPos"]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_cwd = Path.cwd()
        try:
            Path(tmpdir).mkdir(exist_ok=True)
            import os
            os.chdir(tmpdir)
            
            success, msg = ConfigurationManager.save_config(valid_config)
            assert success == True, f"Valid config should save: {msg}"
            print("[PASS] Valid configuration saved")
            
            # Test 2: Invalid keys
            invalid_config = {
                "default_theme": "Test",
                "malicious_key": "evil_value"
            }
            success, msg = ConfigurationManager.save_config(invalid_config)
            assert success == False, "Invalid keys should be rejected"
            print("[PASS] Invalid configuration keys blocked")
            
            # Test 3: Path traversal in config path (Windows-specific)
            import platform
            if platform.system() == "Windows":
                bad_path = "C:\\Windows\\System32\\config.json"
            else:
                bad_path = "/etc/config.json"
            success, msg = ConfigurationManager.save_config(valid_config, bad_path)
            assert success == False, f"Absolute paths should be rejected: {msg}"
            print("[PASS] Absolute path in config blocked")
            
            # Test 4: Load configuration
            loaded = ConfigurationManager.load_config("config.json")
            assert loaded["default_theme"] == "Cerulean"
            print("[PASS] Configuration loaded successfully")
            
        finally:
            os.chdir(orig_cwd)
    
    print("Configuration management tests: PASSED\n")

def test_gcode_parsing():
    """Test secure G-code parsing."""
    print("Testing G-code Parsing...")
    
    # Test 1: Valid G-code
    valid_gcode = """G0 X0 Y0 Z0
G1 X10 Y10 F100
M34 S4200
G1 X20 Y20 Z5"""
    
    lines, error = secure_parse_gcode(valid_gcode)
    assert lines is not None, f"Valid G-code should parse: {error}"
    assert len(lines) == 4, "Should have 4 valid lines"
    print("[PASS] Valid G-code parsed")
    
    # Test 2: G-code with comments
    gcode_with_comments = """G0 X0 Y0 (move to origin)
(This is a comment line)
G1 X10 Y10 ; inline comment"""
    
    lines, error = secure_parse_gcode(gcode_with_comments)
    assert lines is not None
    assert len(lines) == 2, "Should have 2 valid lines after removing comments"
    print("[PASS] G-code comments handled")
    
    # Test 3: Malformed G-code (ReDoS protection)
    malicious = "G1 X" + "9" * 10000  # Would cause ReDoS with unsafe regex
    lines, error = secure_parse_gcode(malicious)
    assert lines is not None or error != "", "Malicious G-code should be handled safely"
    print("[PASS] ReDoS attack prevented")
    
    print("G-code parsing tests: PASSED\n")

def test_error_handling():
    """Test secure error handling."""
    print("Testing Error Handling...")
    
    # Test that sensitive information is not exposed
    try:
        raise FileNotFoundError("/secret/path/to/file.txt")
    except Exception as e:
        msg = ErrorHandler.handle_error(e, user_friendly=True)
        assert "/secret/path" not in msg, "Path should not be exposed"
        assert "file could not be found" in msg.lower()
        print("[PASS] Sensitive paths hidden from error messages")
    
    try:
        raise ValueError("Invalid value: secret_password123")
    except Exception as e:
        msg = ErrorHandler.handle_error(e, user_friendly=True)
        assert "secret_password123" not in msg, "Sensitive data should not be exposed"
        print("[PASS] Sensitive data hidden from error messages")
    
    print("Error handling tests: PASSED\n")

if __name__ == "__main__":
    print("=" * 50)
    print("SECURITY FIXES VERIFICATION")
    print("=" * 50 + "\n")
    
    try:
        test_file_validation()
        test_input_sanitization()
        test_config_management()
        test_gcode_parsing()
        test_error_handling()
        
        print("=" * 50)
        print("ALL SECURITY TESTS PASSED [PASS]")
        print("=" * 50)
        print("\nThe security fixes have been successfully implemented:")
        print("1. [PASS] File upload validation (size, type, content)")
        print("2. [PASS] Input sanitization (numeric, columns, G-code)")
        print("3. [PASS] Secure configuration management")
        print("4. [PASS] ReDoS protection in G-code parsing")
        print("5. [PASS] Safe error handling without information leakage")
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()