"""
Utility functions for music-download-utility.
Provides helpers for validation, formatting, and file management.
"""

import re
import os
import hashlib
from typing import Optional


def sanitize_filename(name: str) -> str:
    """
    Remove or replace characters that are invalid in filenames.

    Args:
        name: Original filename string.

    Returns:
        Sanitized filename string.
    """
    # Replace problematic characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Limit length to 200 characters
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized if sanitized else "untitled"


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid HTTP/HTTPS URL.

    Args:
        url: URL string to validate.

    Returns:
        True if valid, False otherwise.
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def get_file_hash(filepath: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Compute the hash of a file for integrity checking.

    Args:
        filepath: Path to the file.
        algorithm: Hash algorithm (sha256, md5, etc.).

    Returns:
        Hexadecimal hash string, or None if error.
    """
    if not os.path.exists(filepath):
        return None

    hash_func = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception:
        return None


def format_size(bytes_size: int) -> str:
    """
    Convert bytes to human-readable size string.

    Args:
        bytes_size: Size in bytes.

    Returns:
        Formatted string (e.g., "3.45 MB").
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"
