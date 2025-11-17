"""
Built-in coercion functions for common type conversions.
"""

import json
from datetime import datetime
from typing import Any
from uuid import UUID


def coerce_to_string(data: Any) -> Any:
    """
    Coerce various types to string.
    
    Converts: int, float, bool, datetime, dict, list -> str
    Returns other types as-is.
    """
    if isinstance(data, (int, float, bool)):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, (dict, list)):
        return json.dumps(data)
    return data


def coerce_to_integer(data: Any) -> Any:
    """
    Coerce various types to integer.
    
    Converts: float, str (numeric), bool, datetime -> int
    Returns other types as-is.
    """
    if isinstance(data, int):
        return data
    elif isinstance(data, float):
        return int(data)
    elif isinstance(data, bool):
        return int(data)
    elif isinstance(data, str):
        try:
            return int(float(data))  # Handle "3.14" -> 3
        except (ValueError, TypeError):
            return data
    elif isinstance(data, datetime):
        return int(data.timestamp())
    return data


def coerce_to_float(data: Any) -> Any:
    """
    Coerce various types to float.
    
    Converts: int, str (numeric), bool -> float
    Returns other types as-is.
    """
    if isinstance(data, (int, float)):
        return float(data)
    elif isinstance(data, bool):
        return float(data)
    elif isinstance(data, str):
        try:
            return float(data)
        except (ValueError, TypeError):
            return data
    return data


def coerce_to_boolean(data: Any) -> Any:
    """
    Coerce various types to boolean.
    
    Converts: int (0/1), str ("true"/"false"), str ("1"/"0") -> bool
    Returns other types as-is.
    """
    if isinstance(data, bool):
        return data
    elif isinstance(data, int):
        return bool(data)
    elif isinstance(data, str):
        lower = data.lower().strip()
        if lower in ("true", "1", "yes", "on"):
            return True
        elif lower in ("false", "0", "no", "off", ""):
            return False
    return data


def coerce_to_datetime(data: Any) -> Any:
    """
    Coerce various types to datetime.
    
    Converts: str (ISO format), int/float (timestamp) -> datetime
    Returns other types as-is.
    """
    if isinstance(data, datetime):
        return data
    elif isinstance(data, str):
        try:
            # Try ISO format first
            return datetime.fromisoformat(data.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Try common formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(data, fmt)
                except ValueError:
                    continue
    elif isinstance(data, (int, float)):
        try:
            return datetime.fromtimestamp(data)
        except (ValueError, OSError):
            pass
    return data


def coerce_to_lowercase(data: Any) -> Any:
    """
    Coerce string to lowercase.
    
    Args:
        data: The data to coerce
        
    Returns:
        Lowercase string if input is string, otherwise original value
    """
    if isinstance(data, str):
        return data.lower()
    return data


def coerce_to_uuid(data: Any) -> Any:
    """
    Coerce string to UUID.
    
    Converts: str (UUID format) -> UUID
    Returns other types as-is.
    """
    if isinstance(data, UUID):
        return data
    elif isinstance(data, str):
        try:
            return UUID(data)
        except (ValueError, AttributeError):
            return data
    return data

