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
    Returns None and other types as-is.
    
    Note: None values are preserved (not converted to "None" string).
    Use coerce_empty_to_null if you want empty strings to become None.
    """
    if data is None:
        return None
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
    Returns None and other types as-is.
    
    Note: None values are preserved (not converted).
    """
    if data is None:
        return None
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
    Returns None and other types as-is.
    
    Note: None values are preserved (not converted).
    """
    if data is None:
        return None
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
    Returns None and other types as-is.
    
    Note: None values are preserved (not converted).
    """
    if data is None:
        return None
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
    Returns None and other types as-is.
    
    Note: None values are preserved (not converted).
    For nullable datetime fields, None will pass through unchanged.
    Use coerce_empty_to_null if you want empty strings to become None.
    """
    if data is None:
        return None
    if isinstance(data, datetime):
        return data
    elif isinstance(data, str):
        # Handle empty strings - return as-is (don't try to parse)
        if len(data.strip()) == 0:
            return data
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
        Lowercase string if input is string, None if None, otherwise original value
        
    Note: None values are preserved (not converted).
    """
    if data is None:
        return None
    if isinstance(data, str):
        return data.lower()
    return data


def coerce_to_uuid(data: Any) -> Any:
    """
    Coerce string to UUID.
    
    Converts: str (UUID format) -> UUID
    Returns None and other types as-is.
    
    Note: None values are preserved (not converted).
    """
    if data is None:
        return None
    if isinstance(data, UUID):
        return data
    elif isinstance(data, str):
        try:
            return UUID(data)
        except (ValueError, AttributeError):
            return data
    return data


def coerce_to_uppercase(data: Any) -> Any:
    """
    Coerce string to uppercase.
    
    Args:
        data: The data to coerce
        
    Returns:
        Uppercase string if input is string, None if None, otherwise original value
        
    Note: None values are preserved (not converted).
    """
    if data is None:
        return None
    if isinstance(data, str):
        return data.upper()
    return data


def coerce_to_stripped_string(data: Any) -> Any:
    """
    Coerce string by stripping leading and trailing whitespace.
    
    Args:
        data: The data to coerce
        
    Returns:
        Stripped string if input is string, None if None, otherwise original value
        
    Note: None values are preserved (not converted).
    """
    if data is None:
        return None
    if isinstance(data, str):
        return data.strip()
    return data


def coerce_to_list(data: Any) -> Any:
    """
    Coerce single value to list.
    
    Converts: single value -> [value]
    Returns lists as-is.
    
    Note: None values are preserved (not converted to []).
    This allows nullable fields to remain None.
    If you want None -> [], use coerce_to_list_allow_none or handle separately.
    """
    if data is None:
        return None
    if isinstance(data, list):
        return data
    else:
        return [data]


def coerce_to_date(data: Any) -> Any:
    """
    Coerce various types to date (date only, no time).
    
    Converts: str (date format), datetime -> date
    Returns None and other types as-is.
    
    Note: None values are preserved (not converted).
    For nullable date fields, None will pass through unchanged.
    Use coerce_empty_to_null if you want empty strings to become None.
    """
    from datetime import date
    
    if data is None:
        return None
    if isinstance(data, date):
        return data
    elif isinstance(data, datetime):
        return data.date()
    elif isinstance(data, str):
        # Handle empty strings - return as-is (don't try to parse)
        if len(data.strip()) == 0:
            return data
        try:
            # Try ISO format first
            return datetime.fromisoformat(data.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(data, fmt).date()
                except ValueError:
                    continue
    return data


def coerce_empty_to_null(data: Any) -> Any:
    """
    Coerce empty values to None (null).
    
    Converts empty strings, empty lists, empty dicts to None.
    Useful for nullable fields where empty values should be treated as null.
    
    Args:
        data: The data to coerce
        
    Returns:
        None if input is empty (empty string, empty list, empty dict),
        otherwise original value
    """
    if data is None:
        return None
    elif isinstance(data, str) and len(data.strip()) == 0:
        return None
    elif isinstance(data, list) and len(data) == 0:
        return None
    elif isinstance(data, dict) and len(data) == 0:
        return None
    return data

