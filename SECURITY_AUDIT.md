# Security Audit Report - MELD Visualizer Dash Application

**Audit Date:** 2025-08-15  
**Application:** MELD Visualizer  
**Framework:** Dash (Flask-based) with Plotly  
**Auditor:** Security Specialist

## Executive Summary

The MELD Visualizer is a Dash web application designed for visualizing 3D process data from MELD manufacturing. While the application correctly implements local-only binding for network security, several critical and high-severity vulnerabilities have been identified that require immediate attention.

## Severity Ratings
- **CRITICAL**: Immediate exploitation risk, requires urgent fix
- **HIGH**: Significant security risk, should be fixed promptly  
- **MEDIUM**: Moderate risk, should be addressed in regular updates
- **LOW**: Minor risk, best practice improvements

---

## 1. CRITICAL VULNERABILITIES

### 1.1 Arbitrary File Write via Configuration (CRITICAL)
**Location:** `callbacks.py:199-206`  
**OWASP:** A01:2021 - Broken Access Control

**Issue:**
The `save_config_and_advise_restart()` function writes user-controlled data directly to `config.json` without path validation or sanitization.

```python
with open('config.json', 'w') as f:
    json.dump(new_config, f, indent=2)
```

**Risk:** 
- Potential for path traversal if filename can be manipulated
- No validation of configuration values before writing
- Could overwrite critical system files if path manipulation is possible

**Recommendation:**
```python
import os
from pathlib import Path

def save_config_and_advise_restart(...):
    # Validate configuration values
    ALLOWED_THEMES = list(THEMES.keys())
    ALLOWED_TEMPLATES = ["plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
    
    if theme not in ALLOWED_THEMES:
        return True, "Error: Invalid theme selected", no_update
    if template not in ALLOWED_TEMPLATES:
        return True, "Error: Invalid template selected", no_update
    
    # Ensure safe file path
    config_path = Path(__file__).parent / 'config.json'
    config_path = config_path.resolve()
    
    # Verify path is within application directory
    app_dir = Path(__file__).parent.resolve()
    if not str(config_path).startswith(str(app_dir)):
        return True, "Error: Invalid configuration path", no_update
    
    # Write with restricted permissions
    with open(config_path, 'w') as f:
        json.dump(new_config, f, indent=2)
```

### 1.2 Command Injection Risk in G-code Processing (CRITICAL)
**Location:** `data_processing.py:73-104`  
**OWASP:** A03:2021 - Injection

**Issue:**
The G-code parser uses regex without proper input sanitization, potentially allowing malicious code execution through crafted G-code files.

**Risk:**
- Malicious G-code files could cause denial of service
- Resource exhaustion through infinite loops
- Potential for regex DoS (ReDoS) attacks

**Recommendation:**
```python
import re
from typing import Optional

# Compile regex once for performance and security
GCODE_WORD_RE = re.compile(r'^([A-Z])([-+]?\d{1,10}\.?\d{0,6})$')
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit
MAX_LINES = 1000000  # Maximum lines to process

def parse_gcode_file(contents, filename):
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        return None, "Error: File too large (max 100MB)", False
    
    # Validate filename extension
    allowed_extensions = ['.nc', '.gcode', '.g']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return None, "Error: Invalid file type", False
    
    # Add timeout for parsing
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("G-code parsing timeout")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        # Parse with limits
        lines = io.StringIO(gcode_text).readlines()[:MAX_LINES]
        # ... rest of parsing logic
    finally:
        signal.alarm(0)  # Cancel alarm
```

---

## 2. HIGH SEVERITY VULNERABILITIES

### 2.1 Unrestricted File Upload (HIGH)
**Location:** `callbacks.py:45-79`, `data_processing.py:12-47`  
**OWASP:** A01:2021 - Broken Access Control

**Issue:**
No file size limits, type validation, or malware scanning for uploaded files.

**Current Issues:**
- No maximum file size enforcement
- Basic file extension check only ('.csv' in filename)
- No content-type validation
- No virus/malware scanning
- Files processed directly from memory without sandboxing

**Recommendation:**
```python
import magic
import hashlib

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_MIME_TYPES = ['text/csv', 'text/plain', 'application/csv']

def validate_upload(contents, filename):
    # Check file size
    file_size = len(base64.b64decode(contents.split(',')[1]))
    if file_size > MAX_UPLOAD_SIZE:
        return False, "File too large (max 50MB)"
    
    # Validate MIME type
    decoded = base64.b64decode(contents.split(',')[1])
    mime_type = magic.from_buffer(decoded, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid file type: {mime_type}"
    
    # Check file extension
    if not filename.lower().endswith('.csv'):
        return False, "Only CSV files are allowed"
    
    # Generate file hash for logging
    file_hash = hashlib.sha256(decoded).hexdigest()
    print(f"File uploaded: {filename}, Hash: {file_hash}, Size: {file_size}")
    
    return True, None
```

### 2.2 Missing Input Validation (HIGH)
**Location:** Multiple locations in `callbacks.py`  
**OWASP:** A03:2021 - Injection

**Issue:**
User inputs from dropdowns, sliders, and text inputs are not validated before use.

**Examples:**
- Line 263-276: Slider values used without bounds checking
- Line 349-360: Column names from dropdowns used directly in DataFrame operations
- Line 439: Z-stretch factor used without validation

**Recommendation:**
```python
def validate_numeric_input(value, min_val, max_val, default):
    """Validate and sanitize numeric inputs"""
    try:
        val = float(value)
        if min_val <= val <= max_val:
            return val
    except (TypeError, ValueError):
        pass
    return default

def validate_column_name(col_name, allowed_columns):
    """Validate column names against whitelist"""
    if col_name in allowed_columns:
        return col_name
    return None

# Example usage in callbacks
z_stretch_factor = validate_numeric_input(z_stretch_factor, 0.1, 10.0, 1.0)
selected_column = validate_column_name(col_chosen, df.columns.tolist())
```

### 2.3 Sensitive Data Exposure in Error Messages (HIGH)
**Location:** Throughout `callbacks.py` and `data_processing.py`  
**OWASP:** A01:2021 - Broken Access Control

**Issue:**
Detailed error messages expose internal application structure and file paths.

**Examples:**
- Line 46: `f"An unexpected error occurred: {e}"`
- Line 158: `f"An error occurred while parsing G-code on line {line_num}: {e}"`

**Recommendation:**
```python
import logging
import uuid

# Configure secure logging
logger = logging.getLogger(__name__)

def safe_error_response(error, user_message=None):
    """Log detailed error internally, return safe message to user"""
    error_id = str(uuid.uuid4())
    logger.error(f"Error ID {error_id}: {error}")
    
    if user_message:
        return f"{user_message} (Error ID: {error_id})"
    return f"An error occurred. Please contact support with Error ID: {error_id}"

# Usage
except Exception as e:
    return None, safe_error_response(e, "Failed to process file"), False
```

---

## 3. MEDIUM SEVERITY VULNERABILITIES

### 3.1 Insufficient Session Management (MEDIUM)
**Location:** Application-wide  
**OWASP:** A07:2021 - Identification and Authentication Failures

**Issue:**
No authentication or session management implemented. Any user accessing the local port can modify configuration.

**Recommendation:**
- Implement basic authentication for configuration changes
- Add session tokens for multi-user scenarios
- Consider JWT tokens for API-style access

### 3.2 Missing Security Headers (MEDIUM)
**Location:** `app.py`  
**OWASP:** A05:2021 - Security Misconfiguration

**Issue:**
No security headers configured (CSP, X-Frame-Options, etc.)

**Recommendation:**
```python
from flask import Flask
from flask_talisman import Talisman

def create_app(testing: bool = False) -> Dash:
    app = Dash(...)
    
    # Configure security headers
    csp = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
    }
    
    Talisman(
        app.server,
        force_https=False,  # Since local only
        strict_transport_security=False,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src']
    )
    
    return app
```

### 3.3 Uncontrolled Resource Consumption (MEDIUM)
**Location:** `data_processing.py:177-301`  
**OWASP:** A06:2021 - Vulnerable and Outdated Components

**Issue:**
Mesh generation can consume excessive memory with large datasets.

**Recommendation:**
```python
import resource

def generate_volume_mesh(df_active, color_col):
    # Set memory limit (2GB)
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, -1))
    
    # Limit number of points
    MAX_POINTS = 100000
    if len(df_active) > MAX_POINTS:
        # Sample the data
        df_active = df_active.sample(n=MAX_POINTS)
        print(f"Data sampled to {MAX_POINTS} points for performance")
    
    # ... rest of function
```

---

## 4. LOW SEVERITY VULNERABILITIES

### 4.1 Debug Mode Information Disclosure (LOW)
**Location:** `app.py:78-83`  
**OWASP:** A05:2021 - Security Misconfiguration

**Issue:**
Debug mode can expose sensitive information if accidentally enabled in production.

**Recommendation:**
```python
import sys

# Ensure debug is disabled in production
def is_production():
    return not (sys.argv[0].endswith('pytest') or 
                os.environ.get('TESTING') == '1')

if __name__ == "__main__":
    debug = False
    if not is_production():
        debug = os.environ.get("DEBUG", "0") in ("1", "true", "True")
    
    app.run(host=host, port=port, debug=debug)
```

### 4.2 Missing CORS Configuration (LOW)
**Location:** `app.py`  
**OWASP:** A05:2021 - Security Misconfiguration

**Issue:**
No explicit CORS configuration (though mitigated by local-only binding).

**Recommendation:**
```python
from flask_cors import CORS

def create_app(testing: bool = False) -> Dash:
    app = Dash(...)
    
    # Restrict CORS to local origin only
    CORS(app.server, origins=['http://127.0.0.1:8050', 'http://localhost:8050'])
    
    return app
```

---

## 5. POSITIVE SECURITY FINDINGS

### 5.1 Network Security
- Application correctly binds to 127.0.0.1 (local only)
- Port 8050 is not exposed to network interfaces

### 5.2 Dependencies
- Using maintained versions of core libraries
- Dash framework provides some built-in XSS protection

---

## 6. SECURITY CHECKLIST

### Immediate Actions Required:
- [ ] Implement file upload validation and size limits
- [ ] Add input validation for all user inputs
- [ ] Sanitize configuration file operations
- [ ] Implement safe error handling
- [ ] Add resource consumption limits

### Short-term Improvements:
- [ ] Add security headers (CSP, X-Frame-Options)
- [ ] Implement logging and monitoring
- [ ] Add rate limiting for file uploads
- [ ] Create security configuration file
- [ ] Implement basic authentication for sensitive operations

### Long-term Enhancements:
- [ ] Implement proper session management
- [ ] Add file scanning capabilities
- [ ] Create security tests
- [ ] Implement audit logging
- [ ] Add encryption for sensitive data

---

## 7. RECOMMENDED SECURITY CONFIGURATION

Create a new file `security_config.py`:

```python
# security_config.py
import os
from pathlib import Path

class SecurityConfig:
    # File Upload Security
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.csv', '.nc', '.gcode'}
    ALLOWED_MIME_TYPES = {'text/csv', 'text/plain', 'application/csv'}
    
    # Input Validation
    MAX_STRING_LENGTH = 1000
    MAX_NUMERIC_VALUE = 1e6
    MIN_NUMERIC_VALUE = -1e6
    
    # Resource Limits
    MAX_DATAFRAME_ROWS = 1000000
    MAX_MESH_POINTS = 100000
    PARSING_TIMEOUT = 30  # seconds
    
    # Paths
    APP_DIR = Path(__file__).parent.resolve()
    CONFIG_FILE = APP_DIR / 'config.json'
    LOG_DIR = APP_DIR / 'logs'
    
    # Security Headers
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        'img-src': "'self' data:",
        'font-src': "'self' https://cdn.jsdelivr.net",
    }
    
    # Rate Limiting
    UPLOAD_RATE_LIMIT = "10 per minute"
    CONFIG_RATE_LIMIT = "5 per minute"
    
    @classmethod
    def validate_path(cls, path):
        """Ensure path is within application directory"""
        path = Path(path).resolve()
        return str(path).startswith(str(cls.APP_DIR))
    
    @classmethod
    def get_secure_path(cls, filename):
        """Get secure path for file operations"""
        safe_name = Path(filename).name  # Remove any directory components
        return cls.APP_DIR / safe_name
```

---

## 8. TESTING RECOMMENDATIONS

### Security Test Cases:
1. **File Upload Tests:**
   - Upload oversized files (>100MB)
   - Upload non-CSV files with .csv extension
   - Upload files with malicious payloads
   - Test concurrent uploads

2. **Input Validation Tests:**
   - SQL injection attempts in text fields
   - XSS payloads in configuration
   - Boundary value testing for numeric inputs
   - Path traversal attempts

3. **Resource Consumption Tests:**
   - Large dataset processing
   - Memory exhaustion scenarios
   - CPU-intensive operations

---

## 9. COMPLIANCE NOTES

### OWASP Top 10 (2021) Coverage:
- **A01 Broken Access Control** - CRITICAL issues found
- **A02 Cryptographic Failures** - Not applicable (no sensitive data storage)
- **A03 Injection** - HIGH risk in G-code processing
- **A04 Insecure Design** - MEDIUM issues in architecture
- **A05 Security Misconfiguration** - MEDIUM issues found
- **A06 Vulnerable Components** - Dependencies appear current
- **A07 Authentication Failures** - No authentication implemented
- **A08 Software and Data Integrity** - File upload integrity not verified
- **A09 Security Logging Failures** - No security logging implemented
- **A10 Server-Side Request Forgery** - Not applicable (no external requests)

---

## 10. CONCLUSION

The MELD Visualizer application has several critical security vulnerabilities that require immediate attention. The most pressing issues are:

1. **Arbitrary file write vulnerability** in configuration management
2. **Unrestricted file upload** without proper validation
3. **Missing input validation** throughout the application
4. **Resource consumption** risks in data processing

### Priority Remediation Plan:
1. **Week 1:** Fix critical vulnerabilities (file write, input validation)
2. **Week 2:** Implement file upload restrictions and validation
3. **Week 3:** Add security headers and error handling
4. **Week 4:** Implement logging and monitoring

The application's local-only network binding provides good isolation, but the identified vulnerabilities could still be exploited by local attackers or through social engineering attacks.

---

**Report Generated:** 2025-08-15  
**Next Review Date:** 2025-09-15  
**Classification:** CONFIDENTIAL