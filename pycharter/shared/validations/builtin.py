"""
Built-in validation functions for common validation rules.
"""

import re
from typing import Any, List

from pydantic import ValidationInfo


def min_length(threshold: int):
    """
    Factory function to create a min_length validator.
    
    Args:
        threshold: Minimum length required
        
    Returns:
        Validation function
    """
    def _min_length(value: Any, info: ValidationInfo) -> Any:
        if value is None:
            return value
        if isinstance(value, str):
            if len(value) < threshold:
                raise ValueError(
                    f"String must be at least {threshold} characters long, got {len(value)}"
                )
        elif isinstance(value, (list, dict)):
            if len(value) < threshold:
                raise ValueError(
                    f"Value must have at least {threshold} items, got {len(value)}"
                )
        return value
    return _min_length


def max_length(threshold: int):
    """
    Factory function to create a max_length validator.
    
    Args:
        threshold: Maximum length allowed
        
    Returns:
        Validation function
    """
    def _max_length(value: Any, info: ValidationInfo) -> Any:
        if value is None:
            return value
        if isinstance(value, str):
            if len(value) > threshold:
                raise ValueError(
                    f"String must be at most {threshold} characters long, got {len(value)}"
                )
        elif isinstance(value, (list, dict)):
            if len(value) > threshold:
                raise ValueError(
                    f"Value must have at most {threshold} items, got {len(value)}"
                )
        return value
    return _max_length


def only_allow(allowed_values: List[Any]):
    """
    Factory function to create an only_allow validator.
    
    Args:
        allowed_values: List of allowed values
        
    Returns:
        Validation function
    """
    def _only_allow(value: Any, info: ValidationInfo) -> Any:
        if value not in allowed_values:
            raise ValueError(
                f"Value must be one of {allowed_values}, got {value}"
            )
        return value
    return _only_allow


def only_allow_if(condition: dict):
    """
    Factory function to create a conditional only_allow validator.
    
    Args:
        condition: Dict with 'field' and 'value' keys for conditional check
        
    Returns:
        Validation function
    """
    def _only_allow_if(value: Any, info: ValidationInfo) -> Any:
        # This is a simplified version - full implementation would check other fields
        # For now, just return the value
        return value
    return _only_allow_if


def greater_than_or_equal_to(threshold: float):
    """
    Factory function to create a greater_than_or_equal_to validator.
    
    Args:
        threshold: Minimum value allowed
        
    Returns:
        Validation function
    """
    def _gte(value: Any, info: ValidationInfo) -> Any:
        if value is None:
            return value
        if isinstance(value, (int, float)):
            if value < threshold:
                raise ValueError(
                    f"Value must be >= {threshold}, got {value}"
                )
        return value
    return _gte


def less_than_or_equal_to(threshold: float):
    """
    Factory function to create a less_than_or_equal_to validator.
    
    Args:
        threshold: Maximum value allowed
        
    Returns:
        Validation function
    """
    def _lte(value: Any, info: ValidationInfo) -> Any:
        if value is None:
            return value
        if isinstance(value, (int, float)):
            if value > threshold:
                raise ValueError(
                    f"Value must be <= {threshold}, got {value}"
                )
        return value
    return _lte


def no_capital_characters():
    """
    Factory function to create a no_capital_characters validator.
    
    Returns:
        Validation function
    """
    def _no_capital_characters(value: Any, info: ValidationInfo) -> Any:
        """
        Validate that string contains no capital characters.
        
        Returns:
            Validated value
            
        Raises:
            ValidationError: If string contains capital characters
        """
        if value is None:
            return value
        if isinstance(value, str):
            if any(c.isupper() for c in value):
                raise ValueError(
                    "String must not contain capital characters"
                )
        return value
    return _no_capital_characters


def is_positive(threshold: int = 0):
    """
    Factory function to create an is_positive validator.
    
    Args:
        threshold: Minimum value (default 0, meaning must be > 0)
        
    Returns:
        Validation function
    """
    def _is_positive(value: Any, info: ValidationInfo) -> Any:
        if value is None:
            return value
        if isinstance(value, (int, float)):
            if value <= threshold:
                raise ValueError(
                    f"Value must be greater than {threshold}, got {value}"
                )
        return value
    return _is_positive


def non_empty_string(value: Any, info: ValidationInfo) -> Any:
    """
    Validator to ensure string is not empty.
    
    Args:
        value: The value to validate
        info: Validation info
        
    Returns:
        Validated value
        
    Raises:
        ValidationError: If string is empty
    """
    if value is None:
        return value
    if isinstance(value, str):
        if len(value.strip()) == 0:
            raise ValueError("String must not be empty")
    return value


def no_special_characters():
    """
    Factory function to create a no_special_characters validator.
    
    Returns:
        Validation function
    """
    def _no_special_characters(value: Any, info: ValidationInfo) -> Any:
        """
        Validate that string contains no special characters (only alphanumeric).
        
        Returns:
            Validated value
            
        Raises:
            ValidationError: If string contains special characters
        """
        if value is None:
            return value
        if isinstance(value, str):
            if not re.match(r'^[a-zA-Z0-9\s]*$', value):
                raise ValueError(
                    "String must contain only alphanumeric characters and spaces"
                )
        return value
    return _no_special_characters

