#!/usr/bin/env python3
"""
Complete Workflow Example

Demonstrates the full data production journey using all five PyCharter services:
1. Contract Parser - Parse data contract files
2. Metadata Store - Store metadata in database
3. Pydantic Generator - Generate models from schemas
4. JSON Schema Converter - Convert models back to schemas
5. Runtime Validator - Validate data in production
"""

import json
from pathlib import Path

from pycharter import (
    ContractMetadata,
    MetadataStoreClient,
    ValidationResult,
    from_dict,
    parse_contract_file,
    to_dict,
    validate,
)

# Get data directory
DATA_DIR = Path(__file__).parent.parent / "data"


class ExampleMetadataStore(MetadataStoreClient):
    """Simple in-memory metadata store for demonstration."""
    
    def __init__(self):
        super().__init__()
        self._schemas = {}
        self._next_id = 1
    
    def connect(self):
        self._connection = "connected"
        print("  ✓ Connected to metadata store")
    
    def disconnect(self):
        self._connection = None
    
    def store_schema(self, schema_name: str, schema: dict, version: str = None):
        schema_id = self._next_id
        self._next_id += 1
        self._schemas[schema_id] = {
            "id": schema_id,
            "name": schema_name,
            "version": version,
            "schema": schema,
        }
        print(f"  ✓ Stored schema '{schema_name}' v{version} (ID: {schema_id})")
        return schema_id
    
    def get_schema(self, schema_id: int):
        if schema_id in self._schemas:
            return self._schemas[schema_id]["schema"]
        return None


def complete_workflow():
    """Demonstrate the complete data production journey."""
    print("=" * 70)
    print("Complete Data Production Journey")
    print("=" * 70)
    print("\nThis example demonstrates all five PyCharter services working together.")
    print("\nJourney: Contract → Parse → Store → Generate → Validate\n")
    
    # ========================================================================
    # Step 1: Parse Contract Specification
    # ========================================================================
    print("\n" + "-" * 70)
    print("Step 1: Parse Contract Specification")
    print("-" * 70)
    
    contract_path = DATA_DIR / "contracts" / "user_contract.yaml"
    
    if not contract_path.exists():
        print(f"  ⚠ Contract file not found: {contract_path}")
        print("  Creating a simple contract for demonstration...")
        
        # Create a simple contract dictionary
        contract_dict = {
            "schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "username": {"type": "string", "minLength": 3, "maxLength": 20},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer", "minimum": 0, "maximum": 150},
                },
                "required": ["user_id", "username", "email"],
            },
            "governance_rules": {
                "data_retention": {"days": 365},
            },
            "ownership": {
                "owner": "data-team",
                "team": "engineering",
            },
            "metadata": {
                "version": "1.0.0",
                "description": "User data contract",
            },
        }
        
        from pycharter import parse_contract
        metadata = parse_contract(contract_dict)
    else:
        metadata = parse_contract_file(str(contract_path))
    
    print(f"  ✓ Parsed contract")
    print(f"    Schema properties: {len(metadata.schema.get('properties', {}))}")
    print(f"    Owner: {metadata.ownership.get('owner')}")
    print(f"    Version: {metadata.metadata.get('version')}")
    
    # ========================================================================
    # Step 2: Store Metadata in Database
    # ========================================================================
    print("\n" + "-" * 70)
    print("Step 2: Store Metadata in Database")
    print("-" * 70)
    
    store = ExampleMetadataStore()
    store.connect()
    
    try:
        schema_id = store.store_schema(
            schema_name="user",
            schema=metadata.schema,
            version=metadata.metadata.get("version", "1.0.0"),
        )
        
        store.store_ownership(
            schema_id=schema_id,
            owner=metadata.ownership.get("owner"),
            team=metadata.ownership.get("team"),
        )
        
        print(f"  ✓ Metadata stored (Schema ID: {schema_id})")
        
        # ========================================================================
        # Step 3: Generate Pydantic Model from Stored Schema
        # ========================================================================
        print("\n" + "-" * 70)
        print("Step 3: Generate Pydantic Model from Stored Schema")
        print("-" * 70)
        
        # Retrieve schema from store
        stored_schema = store.get_schema(schema_id)
        
        # Generate Pydantic model
        UserModel = from_dict(stored_schema, "User")
        
        print(f"  ✓ Generated UserModel from stored schema")
        print(f"    Model name: {UserModel.__name__}")
        print(f"    Fields: {list(UserModel.model_fields.keys())}")
        
        # ========================================================================
        # Step 4: (Optional) Convert Model Back to Schema for Documentation
        # ========================================================================
        print("\n" + "-" * 70)
        print("Step 4: Convert Model Back to Schema (Round-Trip)")
        print("-" * 70)
        
        # Convert model back to schema
        converted_schema = to_dict(UserModel)
        
        print(f"  ✓ Converted model back to JSON Schema")
        print(f"    Properties: {list(converted_schema.get('properties', {}).keys())}")
        
        # ========================================================================
        # Step 5: Validate Data in Production Pipeline
        # ========================================================================
        print("\n" + "-" * 70)
        print("Step 5: Validate Data in Production Pipeline")
        print("-" * 70)
        
        # Simulate incoming data (e.g., from API, ETL, etc.)
        production_data = [
            {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "alice",
                "email": "alice@example.com",
                "age": 30,
            },
            {
                "user_id": "223e4567-e89b-12d3-a456-426614174001",
                "username": "bob",
                "email": "bob@example.com",
                "age": 25,
            },
            {
                "user_id": "invalid-uuid",
                "username": "ab",  # Too short
                "email": "not-an-email",
                "age": -5,  # Invalid
            },
        ]
        
        print(f"\n  Validating {len(production_data)} records...")
        
        valid_count = 0
        invalid_count = 0
        
        for i, data in enumerate(production_data, 1):
            result: ValidationResult = validate(UserModel, data, strict=False)
            
            if result.is_valid:
                valid_count += 1
                print(f"    ✓ Record {i}: Valid - {result.data.username} ({result.data.email})")
            else:
                invalid_count += 1
                print(f"    ✗ Record {i}: Invalid - {', '.join(result.errors[:2])}")
        
        print(f"\n  ✓ Validation Summary:")
        print(f"    Valid: {valid_count}")
        print(f"    Invalid: {invalid_count}")
        
        # ========================================================================
        # Summary
        # ========================================================================
        print("\n" + "=" * 70)
        print("Workflow Summary")
        print("=" * 70)
        print("""
✓ Complete data production journey demonstrated:

  1. Contract Parser    → Parsed contract file into structured metadata
  2. Metadata Store    → Stored schema and ownership in database
  3. Pydantic Generator → Generated Pydantic model from stored schema
  4. Schema Converter  → Converted model back to schema (round-trip)
  5. Runtime Validator  → Validated production data against model

All five services worked together seamlessly!
        """)
    
    finally:
        store.disconnect()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Complete Workflow Example")
    print("=" * 70 + "\n")
    
    complete_workflow()
    
    print("\n" + "=" * 70)
    print("✓ Complete workflow example finished!")
    print("=" * 70 + "\n")

