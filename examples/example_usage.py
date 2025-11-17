#!/usr/bin/env python3
"""
Comprehensive examples demonstrating pycharter features.

This script shows:
- Basic schema conversion
- x-validators format (pre and post validation)
- $ref and definitions
- Format fields (uuid, email)
- Standard JSON Schema keywords
- Reverse conversion (Pydantic → JSON Schema)
"""

import json
from pathlib import Path

from pycharter import from_file, from_dict, to_dict, to_json

# Get data directory (schemas and sample data are now in data/)
DATA_DIR = Path(__file__).parent.parent / "data"
EXAMPLES_DIR = Path(__file__).parent


def example_1_basic_usage():
    """Example 1: Basic schema conversion from file."""
    print("=" * 70)
    print("Example 1: Basic User Schema with Standard JSON Schema Keywords")
    print("=" * 70)
    
    User = from_file(str(DATA_DIR / "schemas" / "user_schema.json"), "User")
    
    # Load sample data
    with open(DATA_DIR / "sample_data" / "user_sample_data.json") as f:
        user_data = json.load(f)
    
    user = User(**user_data)
    
    print(f"✓ Username: {user.username}")
    print(f"✓ Email: {user.email}")
    print(f"✓ Name: {user.profile.firstName} {user.profile.lastName}")
    print(f"✓ Address: {user.address.city}, {user.address.state}")
    print(f"✓ Tags: {user.tags}")
    print(f"✓ Active: {user.active}")
    print(f"\nFull user data:\n{user.model_dump_json(indent=2)}")
    print()


def example_2_x_validators_and_refs():
    """Example 2: x-validators, $ref, and definitions."""
    print("=" * 70)
    print("Example 2: Order Schema with x-validators, $ref, and definitions")
    print("=" * 70)
    
    Order = from_file(str(DATA_DIR / "schemas" / "order_schema.json"), "Order")
    
    # Load sample data
    with open(DATA_DIR / "sample_data" / "order_sample_data.json") as f:
        order_data = json.load(f)
    
    order = Order(**order_data)
    
    print(f"✓ Order ID: {order.order_id}")
    print(f"✓ Customer: {order.customer.name} (ID: {order.customer.customer_id})")
    print(f"✓ Customer Email: {order.customer.email}")
    print(f"✓ Status: {order.status}")
    print(f"✓ Notes (coerced to lowercase): '{order.notes}'")
    print(f"✓ Items: {len(order.items)}")
    for item in order.items:
        print(f"  - {item.sku}: {item.quantity}x ${item.price}")
    print(f"✓ Total: ${order.total}")
    print()


def example_3_product_with_validations():
    """Example 3: Product schema with various validations."""
    print("=" * 70)
    print("Example 3: Product Schema with Multiple Validation Types")
    print("=" * 70)
    
    Product = from_file(str(DATA_DIR / "schemas" / "product_schema.json"), "Product")
    
    # Load sample data
    with open(DATA_DIR / "sample_data" / "product_sample_data.json") as f:
        product_data = json.load(f)
    
    product = Product(**product_data)
    
    print(f"✓ Product: {product.name} (ID: {product.id})")
    print(f"✓ Category: {product.category.name}")
    if product.category.parent:
        print(f"✓ Parent Category: {product.category.parent.name}")
    print(f"✓ Variants: {len(product.variants)}")
    for variant in product.variants:
        print(f"  - SKU: {variant.sku}, Size: {variant.size}, Price: ${variant.price}")
        print(f"    Inventory: {variant.inventory.quantity} at {variant.inventory.location}")
    print(f"✓ Active: {product.active}")
    print()


def example_4_activity_with_coercion():
    """Example 4: Activity schema with coercion."""
    print("=" * 70)
    print("Example 4: Activity Schema with Pre-validation Coercion")
    print("=" * 70)
    
    Activity = from_file(str(DATA_DIR / "schemas" / "activity_schema.json"), "Activity")
    
    # Load sample data
    with open(DATA_DIR / "sample_data" / "activity_sample_data.json") as f:
        activity_data = json.load(f)
    
    activity = Activity(**activity_data)
    
    print(f"✓ Activity ID: {activity.activity_id}")
    print(f"✓ User: {activity.user.username} (ID: {activity.user.user_id})")
    print(f"✓ Action: {activity.action}")
    print(f"✓ Resource (coerced to lowercase): '{activity.resource}'")
    print(f"✓ Timestamp: {activity.timestamp}")
    print(f"✓ IP Address: {activity.ip_address}")
    if activity.metadata:
        metadata_dict = activity.metadata.model_dump() if hasattr(activity.metadata, 'model_dump') else dict(activity.metadata)
        print(f"✓ Metadata: {json.dumps(metadata_dict, indent=2)}")
    print()


def example_5_validation_errors():
    """Example 5: Demonstrating validation errors."""
    print("=" * 70)
    print("Example 5: Validation Error Examples")
    print("=" * 70)
    
    from pydantic import ValidationError
    
    Order = from_file(str(DATA_DIR / "schemas" / "order_schema.json"), "Order")
    
    # Test invalid data
    test_cases = [
        {
            "name": "Invalid UUID format",
            "data": {
                "order_id": "not-a-uuid",
                "customer": {"customer_id": 1, "email": "test@example.com"},
                "items": [{"sku": "ABC-123456", "quantity": 1}],
                "status": "pending"
            }
        },
        {
            "name": "Invalid SKU format (regex validation)",
            "data": {
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer": {"customer_id": 1, "email": "test@example.com"},
                "items": [{"sku": "invalid-sku", "quantity": 1}],
                "status": "pending"
            }
        },
        {
            "name": "Negative customer_id (is_positive validation)",
            "data": {
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer": {"customer_id": -1, "email": "test@example.com"},
                "items": [{"sku": "ABC-123456", "quantity": 1}],
                "status": "pending"
            }
        },
        {
            "name": "Invalid enum value",
            "data": {
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer": {"customer_id": 1, "email": "test@example.com"},
                "items": [{"sku": "ABC-123456", "quantity": 1}],
                "status": "invalid_status"
            }
        }
    ]
    
    for test_case in test_cases:
        try:
            Order(**test_case["data"])
            print(f"✗ {test_case['name']}: Should have failed but didn't")
        except ValidationError as e:
            print(f"✓ {test_case['name']}: Validation error caught")
            print(f"  Error: {str(e).split('(')[0]}")
    print()


def example_6_reverse_conversion():
    """Example 6: Reverse conversion (Pydantic → JSON Schema)."""
    print("=" * 70)
    print("Example 6: Reverse Conversion (Pydantic Model → JSON Schema)")
    print("=" * 70)
    
    from pydantic import BaseModel, Field
    from typing import Optional
    
    # Create a Pydantic model
    class Product(BaseModel):
        """A product model."""
        id: int = Field(..., description="Product ID", ge=1)
        name: str = Field(..., min_length=1, max_length=200)
        price: float = Field(..., ge=0, description="Product price")
        active: bool = Field(default=True)
        tags: Optional[list[str]] = Field(default=None, max_length=10)
    
    # Convert to JSON Schema
    schema = to_dict(Product)
    
    print("Generated JSON Schema:")
    print(json.dumps(schema, indent=2))
    print()
    
    # Convert to JSON string
    schema_json = to_json(Product)
    print("As JSON string (first 200 chars):")
    print(schema_json[:200] + "...")
    print()


def example_7_dynamic_schema():
    """Example 7: Creating models dynamically from inline schemas."""
    print("=" * 70)
    print("Example 7: Dynamic Model Creation from Inline Schema")
    print("=" * 70)
    
    # Define schema inline
    blog_post_schema = {
        "type": "object",
        "version": "1.0.0",
        "required": ["title", "content", "author"],
        "properties": {
            "title": {
                "type": "string",
                "minLength": 5,
                "maxLength": 100,
                "x-validators": [
                    { "name": "non_empty_string" }
                ]
            },
            "content": {
                "type": "string",
                "minLength": 10
            },
            "author": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["name", "email"]
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 0,
                "maxItems": 5,
                "uniqueItems": True
            },
            "published": {
                "type": "boolean",
                "default": False
            }
        }
    }
    
    BlogPost = from_dict(blog_post_schema, "BlogPost")
    
    post = BlogPost(
        title="Getting Started with Charter",
        content="Charter is a powerful tool for converting JSON schemas to Pydantic models...",
        author={
            "name": "Alice Smith",
            "email": "alice@example.com"
        },
        tags=["python", "pydantic", "json-schema"],
        published=True
    )
    
    print(f"✓ Title: {post.title}")
    print(f"✓ Author: {post.author.name} ({post.author.email})")
    print(f"✓ Tags: {post.tags}")
    print(f"✓ Published: {post.published}")
    print(f"✓ Content length: {len(post.content)} characters")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("CHARTER EXAMPLES - Comprehensive Feature Demonstration")
    print("=" * 70 + "\n")
    
    try:
        example_1_basic_usage()
        example_2_x_validators_and_refs()
        example_3_product_with_validations()
        example_4_activity_with_coercion()
        example_5_validation_errors()
        example_6_reverse_conversion()
        example_7_dynamic_schema()
        
        print("=" * 70)
        print("All examples completed successfully! ✓")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file: {e}")
        print("Make sure you're running this from the project root directory")
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
