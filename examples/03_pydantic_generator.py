#!/usr/bin/env python3
"""
Example 3: Pydantic Generator Service

Demonstrates how to generate Pydantic models from JSON Schema definitions.
Supports loading from dictionaries, JSON strings, files, and URLs.
"""

import json
from pathlib import Path

from pycharter import from_dict, from_file, from_json, generate_model_file

# Get data directory
DATA_DIR = Path(__file__).parent.parent / "data"


def example_from_dict():
    """Generate model from a dictionary schema."""
    print("=" * 70)
    print("Example 3a: Generate Model from Dictionary")
    print("=" * 70)
    
    schema = {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "age", "email"],
    }
    
    # Generate Pydantic model
    Person = from_dict(schema, "Person")
    
    # Use the model
    person = Person(name="Alice", age=30, email="alice@example.com")
    
    print(f"\n✓ Generated Person model")
    print(f"  Name: {person.name}")
    print(f"  Age: {person.age}")
    print(f"  Email: {person.email}")
    
    # Validation works automatically
    try:
        invalid = Person(name="", age=-5, email="not-an-email")
    except Exception as e:
        print(f"\n✓ Validation caught invalid data: {type(e).__name__}")


def example_from_file():
    """Generate model from a JSON schema file."""
    print("\n" + "=" * 70)
    print("Example 3b: Generate Model from JSON Schema File")
    print("=" * 70)
    
    # Use the book schema from examples (which has version)
    schema_path = DATA_DIR / "examples" / "book_schema.json"
    
    if not schema_path.exists():
        print(f"\n⚠ Schema file not found: {schema_path}")
        print("  Creating example schema with version...")
        # Create a simple example schema with version
        import json
        example_schema = {
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
            },
            "required": ["name", "email"],
        }
        schema_path.parent.mkdir(parents=True, exist_ok=True)
        with open(schema_path, "w") as f:
            json.dump(example_schema, f, indent=2)
    
    # Generate model from file
    User = from_file(str(schema_path), "User")
    
    # Create instance with sample data
    user_data = {"name": "Alice", "email": "alice@example.com"}
    user = User(**user_data)
    
    print(f"\n✓ Generated User model from: {schema_path.name}")
    print(f"  Name: {user.name}")
    print(f"  Email: {user.email}")


def example_from_json_string():
    """Generate model from a JSON string."""
    print("\n" + "=" * 70)
    print("Example 3c: Generate Model from JSON String")
    print("=" * 70)
    
    schema_json = """
    {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "product_id": {"type": "string"},
            "name": {"type": "string"},
            "price": {"type": "number", "minimum": 0},
            "in_stock": {"type": "boolean", "default": true}
        },
        "required": ["product_id", "name", "price"]
    }
    """
    
    # Generate model from JSON string
    Product = from_json(schema_json, "Product")
    
    # Use the model
    product = Product(product_id="prod-123", name="Widget", price=19.99)
    
    print(f"\n✓ Generated Product model from JSON string")
    print(f"  Product ID: {product.product_id}")
    print(f"  Name: {product.name}")
    print(f"  Price: ${product.price}")
    print(f"  In Stock: {product.in_stock}")  # Uses default value


def example_generate_model_file():
    """Generate a Python file with the model definition."""
    print("\n" + "=" * 70)
    print("Example 3d: Generate Model File")
    print("=" * 70)
    
    schema = {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "order_id": {"type": "string", "format": "uuid"},
            "customer_name": {"type": "string"},
            "total": {"type": "number", "minimum": 0},
        },
        "required": ["order_id", "customer_name", "total"],
    }
    
    output_path = Path(__file__).parent / "generated_order_model.py"
    
    # Generate Python file with model
    generate_model_file(schema, str(output_path), "Order")
    
    print(f"\n✓ Generated model file: {output_path.name}")
    print(f"  You can now import: from examples.generated_order_model import Order")
    
    # Clean up (optional)
    # output_path.unlink()


def example_nested_objects():
    """Generate model with nested objects."""
    print("\n" + "=" * 70)
    print("Example 3e: Nested Objects and Arrays")
    print("=" * 70)
    
    schema = {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                },
                "required": ["name", "email"],
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
        },
        "required": ["user", "tags"],
    }
    
    # Generate model
    UserProfile = from_dict(schema, "UserProfile")
    
    # Use nested model
    profile = UserProfile(
        user={"name": "Alice", "email": "alice@example.com"},
        tags=["python", "data", "validation"],
    )
    
    print(f"\n✓ Generated UserProfile model with nested objects")
    print(f"  User name: {profile.user.name}")
    print(f"  User email: {profile.user.email}")
    print(f"  Tags: {profile.tags}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Pydantic Generator Service Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    example_from_dict()
    example_from_file()
    example_from_json_string()
    example_generate_model_file()
    example_nested_objects()
    
    print("\n" + "=" * 70)
    print("✓ All Pydantic Generator examples completed!")
    print("=" * 70 + "\n")

