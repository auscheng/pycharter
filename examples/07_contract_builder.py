#!/usr/bin/env python3
"""
Example 7: Contract Builder Service

Demonstrates how to construct consolidated data contracts from separate artifacts
(schema, coercion rules, validation rules, metadata). The built contract tracks
all component versions and can be used for runtime validation.
"""

from pycharter import (
    build_contract,
    build_contract_from_store,
    ContractArtifacts,
    InMemoryMetadataStore,
    validate_with_contract,
)


def example_build_from_artifacts():
    """Build contract from separate artifacts."""
    print("=" * 70)
    print("Example 7a: Building Contract from Separate Artifacts")
    print("=" * 70)
    
    # Define separate artifacts (as they would be stored in database)
    artifacts = ContractArtifacts(
        schema={
            "type": "object",
            "version": "1.0.0",
            "title": "Product",
            "properties": {
                "product_id": {"type": "string"},
                "name": {"type": "string", "minLength": 1, "maxLength": 200},
                "price": {"type": "number", "minimum": 0},
                "stock": {"type": "integer", "minimum": 0},
            },
            "required": ["product_id", "name", "price"],
        },
        coercion_rules={
            "version": "1.0.0",
            "description": "Coercion rules for Product",
            "rules": {
                "price": "coerce_to_float",
                "stock": "coerce_to_integer",
            },
        },
        validation_rules={
            "version": "1.0.0",
            "description": "Validation rules for Product",
            "rules": {
                "price": {"greater_than_or_equal_to": {"threshold": 0}},
                "stock": {"is_positive": {"threshold": 0}},
            },
        },
        metadata={
            "version": "1.0.0",
            "description": "Product data contract for e-commerce",
            "created": "2024-01-01",
            "last_updated": "2024-01-15",
        },
        ownership={
            "owner": "product-team",
            "team": "data-engineering",
            "contact": "product-team@example.com",
        },
        governance_rules={
            "data_retention": {
                "days": 2555,
                "description": "Product data retained for 7 years",
            },
            "access_control": {
                "level": "public",
                "description": "Product data is publicly accessible",
            },
        },
    )
    
    # Build consolidated contract
    contract = build_contract(artifacts)
    
    print("\n✓ Contract built successfully")
    print(f"  Schema title: {contract['schema'].get('title')}")
    print(f"  Versions tracked: {contract.get('versions', {})}")
    print(f"  Has metadata: {'metadata' in contract}")
    print(f"  Has ownership: {'ownership' in contract}")
    print(f"  Has governance_rules: {'governance_rules' in contract}")
    
    # Verify coercion and validation rules are merged into schema
    price_prop = contract["schema"]["properties"]["price"]
    print(f"\n✓ Rules merged into schema:")
    print(f"  price.coercion: {price_prop.get('coercion')}")
    print(f"  price.validations: {price_prop.get('validations', {})}")
    
    # Use contract for validation
    print("\n✓ Using contract for validation:")
    result = validate_with_contract(
        contract,
        {
            "product_id": "prod-123",
            "name": "Widget",
            "price": "29.99",  # String (will be coerced to float)
            "stock": "100",  # String (will be coerced to integer)
        },
    )
    
    if result.is_valid:
        print(f"  ✓ Validation successful")
        print(f"    Name: {result.data.name}")
        print(f"    Price: {result.data.price} (type: {type(result.data.price).__name__})")
        print(f"    Stock: {result.data.stock} (type: {type(result.data.stock).__name__})")
    else:
        print(f"  ✗ Validation failed: {result.errors}")


def example_build_from_store():
    """Build contract from metadata store."""
    print("\n" + "=" * 70)
    print("Example 7b: Building Contract from Metadata Store")
    print("=" * 70)
    
    # Create store and store artifacts separately
    store = InMemoryMetadataStore()
    store.connect()
    
    # Store schema
    schema = {
        "type": "object",
        "version": "1.0.0",
        "title": "User",
        "properties": {
            "user_id": {"type": "string"},
            "username": {"type": "string", "minLength": 3},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0},
        },
        "required": ["user_id", "username", "email"],
    }
    
    schema_id = store.store_schema("user", schema, version="1.0.0")
    print(f"  ✓ Stored schema (ID: {schema_id})")
    
    # Store coercion rules
    coercion_rules = {"user_id": "coerce_to_string", "age": "coerce_to_integer"}
    store.store_coercion_rules(schema_id, coercion_rules, version="1.0.0")
    print(f"  ✓ Stored coercion rules")
    
    # Store validation rules
    validation_rules = {
        "username": {"min_length": {"threshold": 3}},
        "age": {"is_positive": {"threshold": 0}},
    }
    store.store_validation_rules(schema_id, validation_rules, version="1.0.0")
    print(f"  ✓ Stored validation rules")
    
    # Store metadata
    metadata = {
        "version": "1.0.0",
        "description": "User data contract",
        "created": "2024-01-01",
        "governance_rules": {
            "data_retention": {"days": 365},
            "pii_fields": {"fields": ["email", "user_id"]},
        },
    }
    store.store_metadata(schema_id, metadata)
    print(f"  ✓ Stored metadata")
    
    # Store ownership
    store.store_ownership(schema_id, owner="data-team", team="engineering")
    print(f"  ✓ Stored ownership")
    
    # Build contract from store
    contract = build_contract_from_store(store, schema_id)
    
    print(f"\n✓ Contract built from store")
    print(f"  Versions tracked: {contract.get('versions', {})}")
    print(f"  Schema properties: {list(contract['schema']['properties'].keys())}")
    
    # Use contract for validation
    print("\n✓ Using contract for validation:")
    result = validate_with_contract(
        contract,
        {
            "user_id": 12345,  # Integer (will be coerced to string)
            "username": "alice",
            "email": "alice@example.com",
            "age": "30",  # String (will be coerced to integer)
        },
    )
    
    if result.is_valid:
        print(f"  ✓ Validation successful")
        print(f"    User ID: {result.data.user_id} (type: {type(result.data.user_id).__name__})")
        print(f"    Username: {result.data.username}")
        print(f"    Age: {result.data.age} (type: {type(result.data.age).__name__})")
    else:
        print(f"  ✗ Validation failed: {result.errors}")
    
    store.disconnect()


def example_version_tracking():
    """Demonstrate version tracking in consolidated contract."""
    print("\n" + "=" * 70)
    print("Example 7c: Version Tracking in Consolidated Contract")
    print("=" * 70)
    
    # Create artifacts with different versions
    artifacts = ContractArtifacts(
        schema={"type": "object", "version": "2.0.0", "properties": {"name": {"type": "string"}}},
        coercion_rules={"version": "1.5.0", "rules": {"name": "coerce_to_string"}},
        validation_rules={"version": "1.0.0", "rules": {"name": {"min_length": {"threshold": 1}}}},
        metadata={"version": "1.2.0", "description": "Test contract"},
    )
    
    contract = build_contract(artifacts)
    
    print("\n✓ Contract versions tracked:")
    for component, version in contract.get("versions", {}).items():
        print(f"  {component}: {version}")
    
    print("\n✓ This allows you to:")
    print("  - Track which versions of each component were used")
    print("  - Reproduce the exact contract configuration")
    print("  - Audit contract changes over time")
    print("  - Ensure consistency across environments")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Contract Builder Service Examples")
    print("=" * 70 + "\n")
    
    example_build_from_artifacts()
    example_build_from_store()
    example_version_tracking()
    
    print("\n" + "=" * 70)
    print("✓ All Contract Builder examples completed!")
    print("=" * 70 + "\n")

