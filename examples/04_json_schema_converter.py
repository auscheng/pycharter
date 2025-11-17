#!/usr/bin/env python3
"""
Example 4: JSON Schema Converter Service

Demonstrates how to convert Pydantic models back to JSON Schema format.
This enables round-trip conversion and schema documentation.
"""

import json
from pathlib import Path

from pydantic import BaseModel, Field

from pycharter import to_dict, to_file, to_json

# Get data directory
DATA_DIR = Path(__file__).parent.parent / "data"


def example_to_dict():
    """Convert Pydantic model to JSON Schema dictionary."""
    print("=" * 70)
    print("Example 4a: Convert Model to JSON Schema Dictionary")
    print("=" * 70)
    
    # Define a Pydantic model
    class Product(BaseModel):
        """Product model with validation."""
        product_id: str = Field(..., description="Unique product identifier")
        name: str = Field(..., min_length=1, description="Product name")
        price: float = Field(..., ge=0, description="Product price")
        in_stock: bool = Field(default=True, description="Stock availability")
    
    # Convert to JSON Schema
    schema = to_dict(Product)
    
    print(f"\n✓ Converted Product model to JSON Schema")
    print(f"  Type: {schema.get('type')}")
    print(f"  Properties: {list(schema.get('properties', {}).keys())}")
    print(f"  Required: {schema.get('required', [])}")
    
    # Show a property detail
    price_prop = schema.get('properties', {}).get('price', {})
    print(f"  Price type: {price_prop.get('type')}")
    print(f"  Price minimum: {price_prop.get('minimum')}")


def example_to_json():
    """Convert Pydantic model to JSON Schema string."""
    print("\n" + "=" * 70)
    print("Example 4b: Convert Model to JSON Schema String")
    print("=" * 70)
    
    class User(BaseModel):
        username: str = Field(..., min_length=3, max_length=20)
        email: str = Field(..., description="User email address")
        age: int = Field(..., ge=0, le=150)
    
    # Convert to JSON string
    schema_json = to_json(User, indent=2)
    
    print(f"\n✓ Converted User model to JSON Schema string")
    print(f"\nSchema (first 200 chars):")
    print(schema_json[:200] + "...")


def example_to_file():
    """Convert Pydantic model to JSON Schema file."""
    print("\n" + "=" * 70)
    print("Example 4c: Convert Model to JSON Schema File")
    print("=" * 70)
    
    class Order(BaseModel):
        order_id: str
        customer_name: str
        total: float = Field(..., ge=0)
        items: list[str] = Field(default_factory=list)
    
    # Convert to file
    output_path = DATA_DIR / "schemas" / "generated_order_schema.json"
    to_file(Order, str(output_path))
    
    print(f"\n✓ Converted Order model to file: {output_path.name}")
    
    # Verify the file
    with open(output_path) as f:
        saved_schema = json.load(f)
    
    print(f"  Saved schema has {len(saved_schema.get('properties', {}))} properties")


def example_round_trip():
    """Demonstrate round-trip conversion: schema → model → schema."""
    print("\n" + "=" * 70)
    print("Example 4d: Round-Trip Conversion")
    print("=" * 70)
    
    from pycharter import from_dict
    
    # Start with a schema
    original_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "value": {"type": "number", "minimum": 0},
        },
        "required": ["name", "value"],
    }
    
    print("\n1. Original schema → Pydantic model")
    Item = from_dict(original_schema, "Item")
    item = Item(name="Test Item", value=42.5)
    print(f"   ✓ Created model instance: {item.name} = {item.value}")
    
    print("\n2. Pydantic model → JSON Schema")
    converted_schema = to_dict(Item)
    print(f"   ✓ Converted back to schema")
    print(f"   Properties: {list(converted_schema.get('properties', {}).keys())}")
    print(f"   Required: {converted_schema.get('required', [])}")
    
    print("\n✓ Round-trip conversion successful!")


def example_with_validations():
    """Convert model with custom validations."""
    print("\n" + "=" * 70)
    print("Example 4e: Model with Field Constraints")
    print("=" * 70)
    
    class ValidatedProduct(BaseModel):
        sku: str = Field(..., pattern="^[A-Z0-9-]+$", description="SKU format")
        name: str = Field(..., min_length=1, max_length=100)
        price: float = Field(..., gt=0, description="Must be positive")
        category: str = Field(..., description="Product category")
    
    # Convert to schema
    schema = to_dict(ValidatedProduct)
    
    print(f"\n✓ Converted ValidatedProduct model")
    
    # Check constraints are preserved
    sku_prop = schema.get('properties', {}).get('sku', {})
    price_prop = schema.get('properties', {}).get('price', {})
    
    print(f"  SKU pattern: {sku_prop.get('pattern')}")
    print(f"  Price exclusive minimum: {price_prop.get('exclusiveMinimum')}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - JSON Schema Converter Service Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    example_to_dict()
    example_to_json()
    example_to_file()
    example_round_trip()
    example_with_validations()
    
    print("\n" + "=" * 70)
    print("✓ All JSON Schema Converter examples completed!")
    print("=" * 70 + "\n")

