#!/usr/bin/env python3
"""
Example 6: Separated Workflow - Schema, Metadata, and Rules Stored Separately

Demonstrates the new workflow where:
1. Metadata (from business unit) is collected separately
2. Schemas (from developers as Pydantic models) are converted to JSON Schema and stored separately
3. Coercion and validation rules (from developer + business) are stored separately
4. At runtime, all 3 are retrieved and combined for validation
"""

from pydantic import BaseModel, Field

from pycharter import (
    MetadataStoreClient,
    from_dict,
    get_model_from_store,
    to_dict,
    validate_with_store,
)

from pycharter.metadata_store.in_memory import InMemoryMetadataStore


def separated_workflow_example():
    """Demonstrate the separated workflow."""
    print("=" * 70)
    print("Separated Workflow: Schema, Metadata, and Rules Stored Separately")
    print("=" * 70)
    print("\nThis example demonstrates the new workflow where components are stored separately.\n")
    
    # ========================================================================
    # Step 1: Business Unit Provides Metadata
    # ========================================================================
    print("-" * 70)
    print("Step 1: Business Unit Provides Metadata")
    print("-" * 70)
    
    business_metadata = {
        "owner": "data-team",
        "team": "engineering",
        "contact": "data-team@example.com",
        "description": "User data contract for authentication",
        "governance_rules": {
            "data_retention": {"days": 365},
            "pii_fields": {"fields": ["email", "user_id"]},
            "access_control": {"level": "restricted"},
        },
        "version": "1.0.0",
        "created": "2024-01-01",
        "last_updated": "2024-01-15",
    }
    
    print("✓ Business metadata collected:")
    print(f"  Owner: {business_metadata['owner']}")
    print(f"  Version: {business_metadata['version']}")
    print(f"  Governance rules: {len(business_metadata['governance_rules'])} rules")
    
    # ========================================================================
    # Step 2: Developer Writes Pydantic Model and Converts to JSON Schema
    # ========================================================================
    print("\n" + "-" * 70)
    print("Step 2: Developer Writes Pydantic Model and Converts to JSON Schema")
    print("-" * 70)
    
    # Developer writes Pydantic model
    class User(BaseModel):
        """User model defined by developer."""
        user_id: str = Field(..., description="Unique identifier for the user")
        username: str = Field(..., min_length=3, max_length=20, description="Username")
        email: str = Field(..., description="User's email address")
        age: int = Field(..., ge=0, le=150, description="User's age in years")
        created_at: str = Field(..., description="Account creation timestamp")
    
    # Convert to JSON Schema
    schema = to_dict(User)
    
    print("✓ Developer created Pydantic model and converted to JSON Schema")
    print(f"  Model: {User.__name__}")
    print(f"  Properties: {list(schema.get('properties', {}).keys())}")
    print(f"  Required: {schema.get('required', [])}")
    
    # ========================================================================
    # Step 3: Developer + Business Define Coercion and Validation Rules
    # ========================================================================
    print("\n" + "-" * 70)
    print("Step 3: Developer + Business Define Coercion and Validation Rules")
    print("-" * 70)
    
    # Coercion rules (developer + business collaboration)
    coercion_rules = {
        "user_id": "coerce_to_string",  # Ensure user_id is always a string
        "age": "coerce_to_integer",     # Convert string numbers to integers
    }
    
    # Validation rules (developer + business collaboration)
    validation_rules = {
        "username": {
            "no_capital_characters": None,  # Business requirement: usernames must be lowercase
            "min_length": {"threshold": 3},  # Developer: technical constraint
        },
        "email": {
            "non_empty_string": None,  # Business requirement: email cannot be empty
        },
        "age": {
            "is_positive": {"threshold": 0},  # Business requirement: age must be positive
        },
    }
    
    print("✓ Coercion and validation rules defined:")
    print(f"  Coercion rules: {list(coercion_rules.keys())}")
    print(f"  Validation rules: {list(validation_rules.keys())}")
    
    # ========================================================================
    # Step 4: Store All Components Separately in Database
    # ========================================================================
    print("\n" + "-" * 70)
    print("Step 4: Store All Components Separately in Database")
    print("-" * 70)
    
    store = InMemoryMetadataStore()
    store.connect()
    
    try:
        # Store schema (from developer)
        schema_id = store.store_schema(
            schema_name="user",
            schema=schema,
            version=business_metadata["version"],
        )
        print(f"  ✓ Stored schema (ID: {schema_id})")
        
        # Store metadata (from business)
        store.store_metadata(
            resource_id=schema_id,
            metadata=business_metadata,
            resource_type="schema",
        )
        print(f"  ✓ Stored business metadata")
        
        # Store ownership (from business)
        store.store_ownership(
            resource_id=schema_id,
            owner=business_metadata["owner"],
            team=business_metadata["team"],
            additional_info={"contact": business_metadata["contact"]},
        )
        print(f"  ✓ Stored ownership information")
        
        # Store coercion rules (from developer + business)
        store.store_coercion_rules(
            schema_id=schema_id,
            coercion_rules=coercion_rules,
            version=business_metadata["version"],
        )
        print(f"  ✓ Stored coercion rules")
        
        # Store validation rules (from developer + business)
        store.store_validation_rules(
            schema_id=schema_id,
            validation_rules=validation_rules,
            version=business_metadata["version"],
        )
        print(f"  ✓ Stored validation rules")
        
        # ========================================================================
        # Step 5: Runtime Validation - Retrieve All Components and Validate
        # ========================================================================
        print("\n" + "-" * 70)
        print("Step 5: Runtime Validation - Retrieve All Components and Validate")
        print("-" * 70)
        
        # Simulate incoming data
        incoming_data = {
            "user_id": "12345",  # String (coercion will ensure it stays string)
            "username": "alice",  # Already lowercase
            "email": "alice@example.com",
            "age": 30,  # Integer (coercion will ensure it stays integer)
            "created_at": "2024-01-15T10:30:00Z",
        }
        
        print(f"\n  Incoming data: {incoming_data}")
        
        # Option 1: Use convenience function (retrieves all and validates)
        result = validate_with_store(
            store=store,
            schema_id=schema_id,
            data=incoming_data,
            strict=False,
        )
        
        if result.is_valid:
            print(f"\n  ✓ Validation passed!")
            print(f"    user_id: {result.data.user_id} (type: {type(result.data.user_id).__name__})")
            print(f"    username: {result.data.username}")
            print(f"    email: {result.data.email}")
            print(f"    age: {result.data.age} (type: {type(result.data.age).__name__})")
        else:
            print(f"\n  ✗ Validation failed: {result.errors}")
        
        # Option 2: Get model once and use multiple times
        print("\n  Alternative: Get model once and reuse")
        UserModel = get_model_from_store(store, schema_id, "User")
        
        # Validate multiple records
        batch_data = [
            {"user_id": "user1", "username": "alice", "email": "alice@example.com", "age": 30, "created_at": "2024-01-15T10:30:00Z"},
            {"user_id": "user2", "username": "BOB", "email": "bob@example.com", "age": "25", "created_at": "2024-01-15T10:30:00Z"},
        ]
        
        from pycharter import validate_batch
        results = validate_batch(UserModel, batch_data)
        valid_count = sum(1 for r in results if r.is_valid)
        print(f"  ✓ Validated batch: {valid_count}/{len(batch_data)} valid")
        
        # ========================================================================
        # Summary
        # ========================================================================
        print("\n" + "=" * 70)
        print("Workflow Summary")
        print("=" * 70)
        print("""
✓ Separated workflow demonstrated:

  1. Business Metadata    → Collected separately (ownership, governance, versioning)
  2. Developer Schema     → Pydantic model → JSON Schema, stored separately
  3. Coercion/Validation → Defined by developer + business, stored separately
  4. Storage             → All 3 components stored independently in database
  5. Runtime Validation  → All components retrieved and combined automatically

Benefits:
  - Clear separation of concerns
  - Independent versioning of each component
  - Business and developer can work independently
  - Runtime flexibility: retrieve and combine on-demand
        """)
    
    finally:
        store.disconnect()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Separated Workflow Example")
    print("=" * 70 + "\n")
    
    separated_workflow_example()
    
    print("\n" + "=" * 70)
    print("✓ Separated workflow example completed!")
    print("=" * 70 + "\n")

