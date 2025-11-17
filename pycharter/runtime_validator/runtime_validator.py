"""
Runtime validator with support for retrieving schemas, metadata, and rules from store.

This module provides high-level functions for runtime validation that retrieve
all necessary components (schema, metadata, coercion rules, validation rules)
from the metadata store and perform validation.
"""

from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from pycharter.metadata_store import MetadataStoreClient
from pycharter.pydantic_generator import from_dict
from pycharter.runtime_validator.validator import ValidationResult, validate, validate_batch


def validate_with_store(
    store: MetadataStoreClient,
    schema_id: str,
    data: Dict[str, Any],
    version: Optional[str] = None,
    strict: bool = False,
) -> ValidationResult:
    """
    Validate data using schema, coercion rules, and validation rules from store.
    
    This function:
    1. Retrieves schema from metadata store
    2. Retrieves coercion rules and merges them into schema
    3. Retrieves validation rules and merges them into schema
    4. Generates Pydantic model from complete schema
    5. Validates data against the model
    
    Args:
        store: MetadataStoreClient instance
        schema_id: Schema identifier
        data: Data dictionary to validate
        version: Optional version string (if None, uses latest)
        strict: If True, raise exceptions on validation errors
        
    Returns:
        ValidationResult object
        
    Example:
        >>> store = MyMetadataStore(...)
        >>> store.connect()
        >>> result = validate_with_store(store, "user_schema_v1", {"name": "Alice"})
        >>> if result.is_valid:
        ...     print(f"Valid: {result.data.name}")
    """
    # Get complete schema (with coercion and validation rules merged)
    complete_schema = store.get_complete_schema(schema_id, version)
    
    if not complete_schema:
        raise ValueError(f"Schema not found: {schema_id}")
    
    # Generate model from complete schema
    model_name = complete_schema.get("title", "DynamicModel")
    Model = from_dict(complete_schema, model_name)
    
    # Validate data
    return validate(Model, data, strict=strict)


def validate_batch_with_store(
    store: MetadataStoreClient,
    schema_id: str,
    data_list: List[Dict[str, Any]],
    version: Optional[str] = None,
    strict: bool = False,
) -> List[ValidationResult]:
    """
    Validate a batch of data using schema and rules from store.
    
    Args:
        store: MetadataStoreClient instance
        schema_id: Schema identifier
        data_list: List of data dictionaries to validate
        version: Optional version string (if None, uses latest)
        strict: If True, stop on first validation error
        
    Returns:
        List of ValidationResult objects
        
    Example:
        >>> store = MyMetadataStore(...)
        >>> store.connect()
        >>> results = validate_batch_with_store(
        ...     store, "user_schema_v1", [{"name": "Alice"}, {"name": "Bob"}]
        ... )
        >>> valid_count = sum(1 for r in results if r.is_valid)
    """
    # Get complete schema once
    complete_schema = store.get_complete_schema(schema_id, version)
    
    if not complete_schema:
        raise ValueError(f"Schema not found: {schema_id}")
    
    # Generate model once
    model_name = complete_schema.get("title", "DynamicModel")
    Model = from_dict(complete_schema, model_name)
    
    # Validate batch
    return validate_batch(Model, data_list, strict=strict)


def get_model_from_store(
    store: MetadataStoreClient,
    schema_id: str,
    model_name: Optional[str] = None,
    version: Optional[str] = None,
) -> Type[BaseModel]:
    """
    Get a Pydantic model from store with all rules applied.
    
    This is useful when you need the model for multiple validations
    and want to avoid retrieving the schema multiple times.
    
    Args:
        store: MetadataStoreClient instance
        schema_id: Schema identifier
        model_name: Optional model name (defaults to schema title)
        version: Optional version string (if None, uses latest)
        
    Returns:
        Pydantic model class
        
    Example:
        >>> store = MyMetadataStore(...)
        >>> store.connect()
        >>> UserModel = get_model_from_store(store, "user_schema_v1", "User")
        >>> # Use model multiple times
        >>> result1 = validate(UserModel, data1)
        >>> result2 = validate(UserModel, data2)
    """
    complete_schema = store.get_complete_schema(schema_id, version)
    
    if not complete_schema:
        raise ValueError(f"Schema not found: {schema_id}")
    
    model_name = model_name or complete_schema.get("title", "DynamicModel")
    return from_dict(complete_schema, model_name)

