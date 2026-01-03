"""
Utility functions for EST Config Verification Tool.
Common helper functions used across modules.
"""
import re
from pathlib import Path
from typing import Optional


def extract_serial_digits(serial_number: str) -> str:
    """
    Extract only numeric digits from serial number.
    
    Args:
        serial_number: Serial number string (e.g., "EDW12345678" or "SN12345678").
        
    Returns:
        String containing only digits (e.g., "12345678").
    """
    return ''.join(re.findall(r'\d+', str(serial_number)))


def truncate_serial_number(serial_number: str, max_length: int = 20) -> str:
    """
    Truncate serial number to maximum length for filename safety.
    
    Args:
        serial_number: Serial number string.
        max_length: Maximum length (default: 20).
        
    Returns:
        Truncated serial number string.
    """
    return serial_number[:max_length] if len(serial_number) > max_length else serial_number


def safe_path_join(base_path: Path, *parts: str) -> Path:
    """
    Safely join path parts, ensuring total length doesn't exceed Windows limits.
    
    Args:
        base_path: Base path.
        *parts: Path parts to join.
        
    Returns:
        Path object.
    """
    result = base_path
    for part in parts:
        result = result / part
    return result


def ensure_directory(path: Path) -> bool:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

