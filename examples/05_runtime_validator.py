#!/usr/bin/env python3
"""
Example 5: Runtime Validator Service

Demonstrates how to validate data against generated Pydantic models in
production data pipelines, ETL scripts, and API endpoints.
"""

import json
from pathlib import Path

from pycharter import ValidationResult, from_dict, from_file, validate, validate_batch

# Get data directory
DATA_DIR = Path(__file__).parent.parent / "data"


def example_validate_single_record():
    """Validate a single data record."""
    print("=" * 70)
    print("Example 5a: Validate Single Record")
    print("=" * 70)
    
    # Generate a model
    schema = {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid"},
            "username": {"type": "string", "minLength": 3},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0},
        },
        "required": ["user_id", "username", "email"],
    }
    
    User = from_dict(schema, "User")
    
    # Valid data
    valid_data = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "alice",
        "email": "alice@example.com",
        "age": 30,
    }
    
    result = validate(User, valid_data)
    
    if result.is_valid:
        print(f"\n✓ Validation passed!")
        print(f"  Username: {result.data.username}")
        print(f"  Email: {result.data.email}")
        print(f"  Age: {result.data.age}")
    else:
        print(f"\n✗ Validation failed: {result.errors}")
    
    # Invalid data
    invalid_data = {
        "user_id": "not-a-uuid",
        "username": "ab",  # Too short
        "email": "not-an-email",
        "age": -5,  # Negative
    }
    
    result = validate(User, invalid_data)
    
    if not result.is_valid:
        print(f"\n✓ Validation correctly caught errors:")
        for error in result.errors:
            print(f"  - {error}")


def example_validate_batch():
    """Validate multiple records in batch."""
    print("\n" + "=" * 70)
    print("Example 5b: Validate Batch of Records")
    print("=" * 70)
    
    # Generate model
    schema = {
        "type": "object",
        "properties": {
            "product_id": {"type": "string"},
            "name": {"type": "string", "minLength": 1},
            "price": {"type": "number", "minimum": 0},
        },
        "required": ["product_id", "name", "price"],
    }
    
    Product = from_dict(schema, "Product")
    
    # Batch of data (e.g., from CSV, API, etc.)
    products_data = [
        {"product_id": "prod-1", "name": "Widget", "price": 19.99},
        {"product_id": "prod-2", "name": "Gadget", "price": 29.99},
        {"product_id": "prod-3", "name": "", "price": -5},  # Invalid
        {"product_id": "prod-4", "name": "Thing", "price": 9.99},
    ]
    
    # Validate batch
    results = validate_batch(Product, products_data)
    
    valid_count = sum(1 for r in results if r.is_valid)
    invalid_count = sum(1 for r in results if not r.is_valid)
    
    print(f"\n✓ Batch validation complete:")
    print(f"  Total records: {len(products_data)}")
    print(f"  Valid: {valid_count}")
    print(f"  Invalid: {invalid_count}")
    
    # Process valid records
    valid_products = [r.data for r in results if r.is_valid]
    print(f"\n✓ Processed {len(valid_products)} valid products")
    for product in valid_products:
        print(f"  - {product.name}: ${product.price}")


def example_strict_mode():
    """Demonstrate strict mode (raises exceptions)."""
    print("\n" + "=" * 70)
    print("Example 5c: Strict Mode (Raises Exceptions)")
    print("=" * 70)
    
    schema = {
        "type": "object",
        "properties": {
            "order_id": {"type": "string"},
            "total": {"type": "number", "minimum": 0},
        },
        "required": ["order_id", "total"],
    }
    
    Order = from_dict(schema, "Order")
    
    invalid_data = {"order_id": "order-1", "total": -10}
    
    # Lenient mode (default) - returns ValidationResult
    result = validate(Order, invalid_data, strict=False)
    print(f"\n✓ Lenient mode: Validation failed but no exception raised")
    print(f"  Errors: {result.errors}")
    
    # Strict mode - raises exception
    try:
        validate(Order, invalid_data, strict=True)
    except Exception as e:
        print(f"\n✓ Strict mode: Exception raised: {type(e).__name__}")


def example_in_etl_pipeline():
    """Example of using validator in an ETL pipeline."""
    print("\n" + "=" * 70)
    print("Example 5d: Using Validator in ETL Pipeline")
    print("=" * 70)
    
    # Load schema from file
    schema_path = DATA_DIR / "schemas" / "user_schema.json"
    User = from_file(str(schema_path), "User")
    
    # Simulate data from source (e.g., CSV, API, database)
    raw_users = [
        {"username": "alice", "email": "alice@example.com", "age": 30},
        {"username": "bob", "email": "bob@example.com", "age": 25},
        {"username": "charlie", "email": "invalid-email", "age": 35},  # Invalid
    ]
    
    print("\n✓ Processing ETL pipeline with validation:")
    
    validated_users = []
    errors = []
    
    for i, raw_user in enumerate(raw_users):
        result = validate(User, raw_user, strict=False)
        
        if result.is_valid:
            validated_users.append(result.data)
            print(f"  ✓ Record {i+1}: Valid - {result.data.username}")
        else:
            errors.append({"record": i+1, "data": raw_user, "errors": result.errors})
            print(f"  ✗ Record {i+1}: Invalid - {result.errors}")
    
    print(f"\n✓ ETL Summary:")
    print(f"  Processed: {len(raw_users)} records")
    print(f"  Valid: {len(validated_users)}")
    print(f"  Invalid: {len(errors)}")
    
    # Continue processing with validated data
    if validated_users:
        print(f"\n✓ Continuing pipeline with {len(validated_users)} valid records")


def example_with_stored_schema():
    """Example using schema from metadata store."""
    print("\n" + "=" * 70)
    print("Example 5e: Validating with Schema from Metadata Store")
    print("=" * 70)
    
    # Simulate getting schema from metadata store
    # (In production, you'd use MetadataStoreClient.get_schema())
    schema = {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["customer_id", "name", "email"],
    }
    
    # Generate model from stored schema
    Customer = from_dict(schema, "Customer")
    
    # Validate incoming data (e.g., from API request)
    api_data = {
        "customer_id": "cust-123",
        "name": "Alice Smith",
        "email": "alice@example.com",
    }
    
    result = validate(Customer, api_data)
    
    if result.is_valid:
        print(f"\n✓ API data validated successfully")
        print(f"  Customer: {result.data.name} ({result.data.email})")
    else:
        print(f"\n✗ API data validation failed: {result.errors}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Runtime Validator Service Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    example_validate_single_record()
    example_validate_batch()
    example_strict_mode()
    example_in_etl_pipeline()
    example_with_stored_schema()
    
    print("\n" + "=" * 70)
    print("✓ All Runtime Validator examples completed!")
    print("=" * 70 + "\n")

