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
    
    # Define schema inline (or load from file)
    schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string", "minLength": 3},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0},
        },
        "required": ["username", "email", "age"],
    }
    
    User = from_dict(schema, "User")
    
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
            print(f"  ✗ Record {i+1}: Invalid - {result.errors[:1]}")
    
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
    
    from pycharter import InMemoryMetadataStore, validate_with_store
    
    # Create store and store schema
    store = InMemoryMetadataStore()
    store.connect()
    
    schema = {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["customer_id", "name", "email"],
    }
    
    schema_id = store.store_schema("customer", schema, version="1.0.0")
    
    # Validate using store (retrieves schema automatically)
    api_data = {
        "customer_id": "cust-123",
        "name": "Alice Smith",
        "email": "alice@example.com",
    }
    
    result = validate_with_store(store, schema_id, api_data)
    
    if result.is_valid:
        print(f"\n✓ API data validated successfully using store")
        print(f"  Customer: {result.data.name} ({result.data.email})")
    else:
        print(f"\n✗ API data validation failed: {result.errors}")
    
    store.disconnect()


def example_contract_based_validation():
    """Example validating directly from contract files (no database)."""
    print("\n" + "=" * 70)
    print("Example 5f: Contract-Based Validation (No Database)")
    print("=" * 70)
    
    from pycharter import (
        validate_with_contract,
        validate_batch_with_contract,
        get_model_from_contract,
    )
    
    contract_path = DATA_DIR / "examples" / "book_contract.yaml"
    
    if not contract_path.exists():
        print(f"\n⚠ Contract file not found: {contract_path}")
        print("  Skipping contract-based validation example")
        return
    
    # Method 1: Validate directly from file (simplest)
    print("\n✓ Method 1: Validate directly from file")
    result = validate_with_contract(
        str(contract_path),
        {
            "isbn": "9780123456789",
            "title": "Python Guide",
            "author": {"name": "John Doe"},
            "price": 39.99,
            "pages": 500,
            "published_date": "2024-01-15T10:00:00Z",
        },
    )
    
    if result.is_valid:
        print(f"  ✓ Validation successful")
        print(f"    Title: {result.data.title}")
        print(f"    Author: {result.data.author.name}")
    else:
        print(f"  ✗ Validation failed: {result.errors[:1]}")
    
    # Method 2: Get model once, validate multiple times (efficient)
    print("\n✓ Method 2: Get model once, validate multiple times")
    BookModel = get_model_from_contract(str(contract_path), "Book")
    
    data1 = {
        "isbn": "1111111111111",
        "title": "Book 1",
        "author": {"name": "Author 1"},
        "price": 10.0,
        "pages": 100,
        "published_date": "2024-01-01T00:00:00Z",
    }
    data2 = {
        "isbn": "2222222222222",
        "title": "Book 2",
        "author": {"name": "Author 2"},
        "price": 20.0,
        "pages": 200,
        "published_date": "2024-01-02T00:00:00Z",
    }
    
    result1 = validate(BookModel, data1)
    result2 = validate(BookModel, data2)
    print(f"  ✓ Validated 2 records: {result1.is_valid}, {result2.is_valid}")
    
    # Method 3: Batch validation
    print("\n✓ Method 3: Batch validation from contract")
    results = validate_batch_with_contract(str(contract_path), [data1, data2])
    valid_count = sum(1 for r in results if r.is_valid)
    print(f"  ✓ Batch validation: {valid_count}/{len(results)} valid")
    
    # Method 4: From dictionary
    print("\n✓ Method 4: Validate from dictionary")
    contract_dict = {
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "integer", "minimum": 0},
            },
            "required": ["name", "age"],
        },
        "coercion_rules": {
            "rules": {"age": "coerce_to_integer"},
        },
    }
    
    result = validate_with_contract(contract_dict, {"name": "Alice", "age": "30"})
    if result.is_valid:
        print(f"  ✓ Validation successful")
        print(f"    Name: {result.data.name}, Age: {result.data.age} (type: {type(result.data.age).__name__})")


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
    example_contract_based_validation()
    
    print("\n" + "=" * 70)
    print("✓ All Runtime Validator examples completed!")
    print("=" * 70 + "\n")

