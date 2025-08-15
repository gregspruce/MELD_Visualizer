"""
File service for handling file operations and format detection.
"""

import base64
import logging
from pathlib import Path
from typing import Optional, Tuple

from constants import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_MB

logger = logging.getLogger(__name__)


class FileService:
    """Service for file handling operations."""
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def is_csv_file(filename: str) -> bool:
        """Check if file is a CSV file."""
        return FileService.get_file_extension(filename) == '.csv'
    
    @staticmethod
    def is_gcode_file(filename: str) -> bool:
        """Check if file is a G-code file."""
        ext = FileService.get_file_extension(filename)
        return ext in ['.nc', '.gcode', '.txt']
    
    @staticmethod
    def decode_file_contents(contents: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Decode base64 file contents.
        
        Args:
            contents: Base64 encoded string with data URL prefix
            
        Returns:
            Tuple of (decoded_bytes, error_message)
        """
        try:
            # Split data URL to get base64 content
            if ',' not in contents:
                return None, "Invalid file format"
            
            _, content_string = contents.split(',', 1)
            decoded = base64.b64decode(content_string)
            return decoded, None
            
        except Exception as e:
            logger.error(f"Failed to decode file contents: {e}")
            return None, f"Failed to decode file: {str(e)}"
    
    @staticmethod
    def validate_file_size(contents: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that file size is within limits.
        
        Args:
            contents: Base64 encoded file contents
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        decoded, error = FileService.decode_file_contents(contents)
        
        if error:
            return False, error
        
        size_mb = len(decoded) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return False, f"File too large: {size_mb:.1f} MB (max: {MAX_FILE_SIZE_MB} MB)"
        
        return True, None
    
    @staticmethod
    def detect_delimiter(content: str, sample_lines: int = 5) -> str:
        """
        Detect CSV delimiter from file content.
        
        Args:
            content: File content as string
            sample_lines: Number of lines to sample
            
        Returns:
            Detected delimiter character
        """
        lines = content.split('\n')[:sample_lines]
        
        # Count occurrences of common delimiters
        delimiters = [',', '\t', ';', '|']
        delimiter_counts = {d: 0 for d in delimiters}
        
        for line in lines:
            for delimiter in delimiters:
                delimiter_counts[delimiter] += line.count(delimiter)
        
        # Return most frequent delimiter
        return max(delimiter_counts, key=delimiter_counts.get)
    
    @staticmethod
    def get_file_info(contents: str, filename: str) -> dict:
        """
        Get information about an uploaded file.
        
        Args:
            contents: Base64 encoded file contents
            filename: Original filename
            
        Returns:
            Dictionary with file information
        """
        decoded, error = FileService.decode_file_contents(contents)
        
        if error:
            return {'error': error}
        
        size_bytes = len(decoded)
        size_mb = size_bytes / (1024 * 1024)
        
        return {
            'filename': filename,
            'extension': FileService.get_file_extension(filename),
            'size_bytes': size_bytes,
            'size_mb': round(size_mb, 2),
            'is_csv': FileService.is_csv_file(filename),
            'is_gcode': FileService.is_gcode_file(filename)
        }