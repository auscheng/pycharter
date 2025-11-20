#!/usr/bin/env python3
"""
Complete Developer Journey Example

This example demonstrates the complete data contract journey from a developer's perspective:

1. Start with a Pydantic model (developer-defined)
2. Convert it to JSON Schema
3. Parse a (partial) data contract to acquire metadata, coercion rules, validation rules, governance rules
4. Store these into the metadata store
5. Retrieve from metadata store and rebuild a consolidated data contract
6. Convert this data contract into a more comprehensive Pydantic model
7. Perform runtime validation with this data contract via Pydantic
8. Database initialization/upgrade example

This is the recommended workflow for developers working with PyCharter.
"""

import json
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field

from pycharter import (
    InMemoryMetadataStore,
    PostgresMetadataStore,
    build_contract_from_store,
    from_dict,
    get_model_from_contract,
    parse_contract,
    to_dict,
    validate,
    ValidationResult,
)

# ============================================================================
# Step 1: Start with a Pydantic Model (Developer-Defined)
# ============================================================================

print("=" * 70)
print("Step 1: Start with a Pydantic Model")
print("=" * 70)
print("\nAs a developer, you start by defining your data model using Pydantic.\n")


class User(BaseModel):
    """User model - your initial Pydantic definition."""
    
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=20, description="Username")
    email: str = Field(..., description="User email address")
    age: int = Field(..., ge=0, le=150, description="User age")


print("✓ Defined User Pydantic model")
print(f"  Fields: {list(User.model_fields.keys())}")
print(f"  Required: {[name for name, field in User.model_fields.items() if field.is_required()]}")

# ============================================================================
# Step 2: Convert Pydantic Model to JSON Schema
# ============================================================================

print("\n" + "=" * 70)
print("Step 2: Convert Pydantic Model to JSON Schema")
print("=" * 70)
print("\nConvert your Pydantic model to JSON Schema format.\n")

from pycharter import to_dict

# Convert the Pydantic model to JSON Schema
base_schema = to_dict(User, title="User", version="1.0.0")

print("✓ Converted User model to JSON Schema")
print(f"  Schema type: {base_schema.get('type')}")
print(f"  Properties: {list(base_schema.get('properties', {}).keys())}")
print(f"  Version: {base_schema.get('version')}")

# ============================================================================
# Step 3: Parse a (Partial) Data Contract
# ============================================================================

print("\n" + "=" * 70)
print("Step 3: Parse a (Partial) Data Contract")
print("=" * 70)
print("\nParse a data contract file to acquire metadata, coercion rules,")
print("validation rules, and governance rules.\n")

# Example: A partial contract file (YAML or JSON) that contains additional rules
# This might come from business stakeholders, data governance team, etc.
partial_contract = {
    "metadata": {
        "version": "1.0.0",
        "description": "User data contract for authentication system",
        "domain": "authentication",
        "tags": ["user", "auth", "profile"],
    },
    "ownership": {
        "owner": "data-team",
        "team": "engineering",
        "contact": "data-team@example.com",
    },
    "governance_rules": {
        "data_retention": {"days": 365},
        "privacy": {"pii": True, "encryption_required": True},
        "access_control": {"level": "restricted"},
    },
    "coercion_rules": {
        "version": "1.0.0",
        "rules": {
            "age": "coerce_to_integer",  # Convert string "30" to integer 30
            "user_id": "coerce_to_string",  # Ensure user_id is always string
        },
    },
    "validation_rules": {
        "version": "1.0.0",
        "rules": {
            "email": {
                "format": {"type": "email"},  # Additional email validation
            },
            "username": {
                "pattern": {"regex": "^[a-zA-Z0-9_]+$"},  # Alphanumeric + underscore only
            },
            "age": {
                "is_positive": {},  # Custom validation: age must be positive
            },
        },
    },
}

from pycharter import parse_contract

# Parse the partial contract
# Note: parse_contract extracts coercion_rules and validation_rules but doesn't store
# them in ContractMetadata. We'll access them from the original dict for storage.
contract_metadata = parse_contract(partial_contract)

# Extract coercion and validation rules from the original contract dict
# These will be stored separately in the metadata store
coercion_rules = partial_contract.get("coercion_rules", {})
validation_rules = partial_contract.get("validation_rules", {})

print("✓ Parsed partial data contract")
print(f"  Metadata: {contract_metadata.metadata.get('description')}")
print(f"  Owner: {contract_metadata.ownership.get('owner')}")
print(f"  Governance rules: {list(contract_metadata.governance_rules.keys())}")
print(f"  Coercion rules: {list(coercion_rules.get('rules', {}).keys()) if coercion_rules else 'None'}")
print(f"  Validation rules: {list(validation_rules.get('rules', {}).keys()) if validation_rules else 'None'}")

# ============================================================================
# Step 4: Store into Metadata Store
# ============================================================================

print("\n" + "=" * 70)
print("Step 4: Store into Metadata Store")
print("=" * 70)
print("\nStore the schema, metadata, ownership, coercion rules, and")
print("validation rules into the metadata store.\n")

# Use InMemoryMetadataStore for this example (or PostgresMetadataStore for production)
store = InMemoryMetadataStore()
store.connect()

try:
    # Store the schema (from Step 2)
    schema_id = store.store_schema(
        schema_name="user",
        schema=base_schema,
        version=base_schema.get("version", "1.0.0"),
    )
    print(f"✓ Stored schema (ID: {schema_id})")
    
    # Store ownership information
    store.store_ownership(
        resource_id=schema_id,
        owner=contract_metadata.ownership.get("owner", "unknown"),
        team=contract_metadata.ownership.get("team"),
        additional_info=contract_metadata.ownership,
    )
    print(f"✓ Stored ownership information")
    
    # Store metadata
    store.store_metadata(
        resource_id=schema_id,
        metadata=contract_metadata.metadata,
        resource_type="schema",
    )
    print(f"✓ Stored metadata")
    
    # Store coercion rules (from the original partial_contract)
    if coercion_rules:
        coercion_version = coercion_rules.get("version", "1.0.0")
        store.store_coercion_rules(
            schema_id=schema_id,
            coercion_rules=coercion_rules.get("rules", {}),
            version=coercion_version,
        )
        print(f"✓ Stored coercion rules (version: {coercion_version})")
    
    # Store validation rules (from the original partial_contract)
    if validation_rules:
        validation_version = validation_rules.get("version", "1.0.0")
        store.store_validation_rules(
            schema_id=schema_id,
            validation_rules=validation_rules.get("rules", {}),
            version=validation_version,
        )
        print(f"✓ Stored validation rules (version: {validation_version})")
    
    # Store governance rules
    if contract_metadata.governance_rules:
        store.store_governance_rule(
            rule_name="user_governance",
            rule_definition=contract_metadata.governance_rules,
            schema_id=schema_id,
        )
        print(f"✓ Stored governance rules")
    
    print(f"\n✓ All components stored in metadata store (Schema ID: {schema_id})")
    
    # ============================================================================
    # Step 5: Retrieve and Rebuild Consolidated Data Contract
    # ============================================================================
    
    print("\n" + "=" * 70)
    print("Step 5: Retrieve and Rebuild Consolidated Data Contract")
    print("=" * 70)
    print("\nRetrieve all components from the metadata store and rebuild")
    print("a consolidated data contract.\n")
    
    from pycharter import build_contract_from_store
    
    # Rebuild the complete contract from the metadata store
    consolidated_contract = build_contract_from_store(
        store=store,
        schema_id=schema_id,
        version=None,  # Use latest version
        include_metadata=True,
        include_ownership=True,
        include_governance=True,
    )
    
    print("✓ Rebuilt consolidated data contract from metadata store")
    print(f"  Schema properties: {list(consolidated_contract.get('schema', {}).get('properties', {}).keys())}")
    print(f"  Metadata: {consolidated_contract.get('metadata', {}).get('description')}")
    print(f"  Ownership: {consolidated_contract.get('ownership', {}).get('owner')}")
    print(f"  Versions tracked: {list(consolidated_contract.get('versions', {}).keys())}")
    
    # ============================================================================
    # Step 6: Convert to Comprehensive Pydantic Model
    # ============================================================================
    
    print("\n" + "=" * 70)
    print("Step 6: Convert to Comprehensive Pydantic Model")
    print("=" * 70)
    print("\nConvert the consolidated data contract (with all rules merged)")
    print("into a comprehensive Pydantic model that includes coercion and")
    print("validation rules.\n")
    
    from pycharter import get_model_from_contract
    
    # Generate a comprehensive Pydantic model from the consolidated contract
    # This model includes all coercion and validation rules
    ComprehensiveUserModel = get_model_from_contract(
        contract=consolidated_contract,
        model_name="ComprehensiveUser",
    )
    
    print("✓ Generated comprehensive Pydantic model from consolidated contract")
    print(f"  Model name: {ComprehensiveUserModel.__name__}")
    print(f"  Fields: {list(ComprehensiveUserModel.model_fields.keys())}")
    
    # Compare with original model
    print(f"\n  Comparison with original User model:")
    print(f"    Original fields: {list(User.model_fields.keys())}")
    print(f"    Comprehensive fields: {list(ComprehensiveUserModel.model_fields.keys())}")
    print(f"    ✓ Comprehensive model includes all rules from the contract")
    
    # Optional: Demonstrate round-trip conversion (model → schema → model)
    print(f"\n  Round-trip conversion demonstration:")
    print(f"    Converting comprehensive model back to JSON Schema...")
    comprehensive_schema = to_dict(ComprehensiveUserModel, title="ComprehensiveUser", version="1.0.0")
    print(f"    ✓ Converted back to schema (round-trip complete)")
    print(f"    Schema properties: {list(comprehensive_schema.get('properties', {}).keys())}")
    print(f"    This demonstrates the round-trip: Pydantic → JSON Schema → Pydantic → JSON Schema")
    
    # ============================================================================
    # Step 7: Perform Runtime Validation
    # ============================================================================
    
    print("\n" + "=" * 70)
    print("Step 7: Perform Runtime Validation")
    print("=" * 70)
    print("\nUse the comprehensive Pydantic model to validate data at runtime.\n")
    
    # Test data - some valid, some invalid
    test_data = [
        {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "alice_smith",
            "email": "alice@example.com",
            "age": "30",  # String - will be coerced to integer
        },
        {
            "user_id": "223e4567-e89b-12d3-a456-426614174001",
            "username": "bob",
            "email": "bob@example.com",
            "age": 25,
        },
        {
            "user_id": "invalid",
            "username": "ab",  # Too short (min_length=3)
            "email": "not-an-email",
            "age": -5,  # Invalid (must be >= 0)
        },
    ]
    
    print(f"Validating {len(test_data)} records...\n")
    
    valid_count = 0
    invalid_count = 0
    
    for i, data in enumerate(test_data, 1):
        result: ValidationResult = validate(
            ComprehensiveUserModel,
            data,
            strict=False,  # Lenient mode allows coercion
        )
        
        if result.is_valid:
            valid_count += 1
            print(f"  ✓ Record {i}: Valid")
            print(f"    Username: {result.data.username}")
            print(f"    Email: {result.data.email}")
            print(f"    Age: {result.data.age} (type: {type(result.data.age).__name__})")
        else:
            invalid_count += 1
            print(f"  ✗ Record {i}: Invalid")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"    - {error}")
    
    print(f"\n✓ Validation Summary:")
    print(f"  Valid: {valid_count}/{len(test_data)}")
    print(f"  Invalid: {invalid_count}/{len(test_data)}")
    
    # ============================================================================
    # Step 8: Database Initialization Example
    # ============================================================================
    
    print("\n" + "=" * 70)
    print("Step 8: Database Initialization")
    print("=" * 70)
    print("\nExample of how to initialize/upgrade the database schema.\n")
    
    print("For PostgreSQL metadata store, you need to initialize the database first:")
    print("\n  Option 1: Using CLI command (Recommended)")
    print("  " + "-" * 66)
    print("  pycharter db init postgresql://user:pass@localhost/pycharter")
    print("\n  Option 2: Using environment variable")
    print("  " + "-" * 66)
    print("  export PYCHARTER_DATABASE_URL=postgresql://user:pass@localhost/pycharter")
    print("  pycharter db init")
    print("\n  Option 3: Upgrade existing database")
    print("  " + "-" * 66)
    print("  pycharter db upgrade postgresql://user:pass@localhost/pycharter")
    print("\n  Then in Python:")
    print("  " + "-" * 66)
    print("  from pycharter import PostgresMetadataStore")
    print("  store = PostgresMetadataStore('postgresql://user:pass@localhost/pycharter')")
    print("  store.connect()  # Validates schema exists")
    
    # Example with PostgreSQL (if available)
    try:
        # This is just a demonstration - don't actually connect unless configured
        print("\n  Example PostgreSQL usage (commented out):")
        print("  " + "-" * 66)
        print("  # store = PostgresMetadataStore('postgresql://user:pass@localhost/pycharter')")
        print("  # store.connect()  # Requires: pycharter db init first")
        print("  # schema_id = store.store_schema('user', base_schema, version='1.0.0')")
    except Exception:
        pass
    
    # ============================================================================
    # Summary
    # ============================================================================
    
    print("\n" + "=" * 70)
    print("Complete Journey Summary")
    print("=" * 70)
    print("""
✓ Complete developer journey demonstrated:

  1. Started with Pydantic model (User)
  2. Converted to JSON Schema (base_schema)
  3. Parsed partial contract (metadata, rules, governance)
  4. Stored all components in metadata store
  5. Retrieved and rebuilt consolidated contract
  6. Generated comprehensive Pydantic model (with all rules)
  7. Performed runtime validation with comprehensive model
  8. Database initialization instructions provided

The journey shows how:
- Developer models (Pydantic) can be enhanced with business rules
- Metadata store acts as a central repository for all contract components
- Consolidated contracts combine schema + rules for comprehensive validation
- Runtime validation uses the enhanced model with all rules applied
    """)
    
finally:
    store.disconnect()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Complete Developer Journey Example")
    print("=" * 70)
    print("\nThis example demonstrates the complete workflow from Pydantic model")
    print("to runtime validation, including metadata store integration.\n")
    
    print("=" * 70 + "\n")

