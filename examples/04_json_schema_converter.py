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


def example_nested_models():
    """Convert model with nested Pydantic models."""
    print("\n" + "=" * 70)
    print("Example 4f: Nested Models")
    print("=" * 70)
    
    # Define nested models
    class Address(BaseModel):
        """Address information."""
        street: str = Field(..., min_length=1)
        city: str = Field(..., min_length=1)
        state: str = Field(..., min_length=2, max_length=2)
        zipcode: str = Field(..., pattern="^\\d{5}(-\\d{4})?$")
    
    class Contact(BaseModel):
        """Contact information."""
        email: str = Field(..., description="Email address")
        phone: str = Field(default="", description="Phone number")
    
    class Person(BaseModel):
        """Person with nested address and contact."""
        name: str = Field(..., min_length=1)
        age: int = Field(..., ge=0, le=150)
        address: Address  # Nested model
        contact: Contact  # Nested model
    
    # Convert to schema
    schema = to_dict(Person)
    
    print(f"\n✓ Converted Person model with nested Address and Contact")
    print(f"  Top-level properties: {list(schema.get('properties', {}).keys())}")
    
    # Check nested address schema
    address_prop = schema.get('properties', {}).get('address', {})
    print(f"\n  Address (nested) schema:")
    print(f"    Type: {address_prop.get('type')}")
    print(f"    Properties: {list(address_prop.get('properties', {}).keys())}")
    print(f"    Required: {address_prop.get('required', [])}")
    
    # Check nested contact schema
    contact_prop = schema.get('properties', {}).get('contact', {})
    print(f"\n  Contact (nested) schema:")
    print(f"    Type: {contact_prop.get('type')}")
    print(f"    Properties: {list(contact_prop.get('properties', {}).keys())}")
    
    # Verify nested constraints are preserved
    address_street = address_prop.get('properties', {}).get('street', {})
    address_zipcode = address_prop.get('properties', {}).get('zipcode', {})
    print(f"\n  Nested constraints preserved:")
    print(f"    Address.street minLength: {address_street.get('minLength')}")
    print(f"    Address.zipcode pattern: {address_zipcode.get('pattern')}")


def example_nested_arrays():
    """Convert model with arrays of nested models."""
    print("\n" + "=" * 70)
    print("Example 4g: Arrays of Nested Models")
    print("=" * 70)
    
    # Define nested model
    class OrderItem(BaseModel):
        """Order item with product details."""
        product_id: str = Field(..., description="Product identifier")
        quantity: int = Field(..., ge=1, description="Quantity ordered")
        price: float = Field(..., ge=0, description="Unit price")
    
    class Order(BaseModel):
        """Order with array of items."""
        order_id: str = Field(..., description="Order identifier")
        customer_id: str = Field(..., description="Customer identifier")
        items: list[OrderItem] = Field(..., min_length=1, description="Order items")
        total: float = Field(..., ge=0, description="Total order amount")
    
    # Convert to schema
    schema = to_dict(Order)
    
    print(f"\n✓ Converted Order model with array of OrderItem")
    print(f"  Properties: {list(schema.get('properties', {}).keys())}")
    
    # Check array of nested models
    items_prop = schema.get('properties', {}).get('items', {})
    print(f"\n  Items (array) schema:")
    print(f"    Type: {items_prop.get('type')}")
    print(f"    Min items: {items_prop.get('minItems')}")
    
    # Check nested item schema
    item_schema = items_prop.get('items', {})
    print(f"\n  OrderItem (nested in array) schema:")
    print(f"    Type: {item_schema.get('type')}")
    print(f"    Properties: {list(item_schema.get('properties', {}).keys())}")
    print(f"    Required: {item_schema.get('required', [])}")
    
    # Verify nested constraints
    item_quantity = item_schema.get('properties', {}).get('quantity', {})
    print(f"\n  Nested array item constraints preserved:")
    print(f"    OrderItem.quantity minimum: {item_quantity.get('minimum')}")


def example_deeply_nested():
    """Convert model with deeply nested structures."""
    print("\n" + "=" * 70)
    print("Example 4h: Deeply Nested Structures")
    print("=" * 70)
    
    # Deeply nested models
    class Coordinates(BaseModel):
        """Geographic coordinates."""
        latitude: float = Field(..., ge=-90, le=90)
        longitude: float = Field(..., ge=-180, le=180)
    
    class Location(BaseModel):
        """Location with coordinates."""
        name: str = Field(..., description="Location name")
        coordinates: Coordinates  # Nested model
    
    class Warehouse(BaseModel):
        """Warehouse information."""
        warehouse_id: str = Field(..., description="Warehouse identifier")
        location: Location  # Nested model containing another nested model
        capacity: int = Field(..., ge=0)
    
    class Product(BaseModel):
        """Product with warehouse information."""
        product_id: str = Field(..., description="Product identifier")
        name: str = Field(..., min_length=1)
        warehouses: list[Warehouse] = Field(default_factory=list)  # Array of nested models
    
    # Convert to schema
    schema = to_dict(Product)
    
    print(f"\n✓ Converted Product model with deeply nested structures")
    print(f"  Top-level properties: {list(schema.get('properties', {}).keys())}")
    
    # Navigate through nested structure
    warehouses_prop = schema.get('properties', {}).get('warehouses', {})
    warehouse_item = warehouses_prop.get('items', {})
    warehouse_location = warehouse_item.get('properties', {}).get('location', {})
    location_coords = warehouse_location.get('properties', {}).get('coordinates', {})
    
    print(f"\n  Deep nesting structure:")
    print(f"    Product.warehouses (array)")
    print(f"      → Warehouse.location (nested)")
    print(f"        → Location.coordinates (nested)")
    print(f"          → Coordinates.latitude/longitude")
    
    print(f"\n  Deeply nested constraints preserved:")
    print(f"    Coordinates.latitude range: [{location_coords.get('properties', {}).get('latitude', {}).get('minimum')}, {location_coords.get('properties', {}).get('latitude', {}).get('maximum')}]")
    print(f"    Coordinates.longitude range: [{location_coords.get('properties', {}).get('longitude', {}).get('minimum')}, {location_coords.get('properties', {}).get('longitude', {}).get('maximum')}]")


def example_nested_round_trip():
    """Demonstrate round-trip with nested models."""
    print("\n" + "=" * 70)
    print("Example 4i: Round-Trip with Nested Models")
    print("=" * 70)
    
    from pycharter import from_dict
    
    # Create a model with nested structure
    class Category(BaseModel):
        name: str = Field(..., min_length=1)
        description: str = Field(default="")
    
    class Product(BaseModel):
        product_id: str
        name: str = Field(..., min_length=1)
        category: Category
        tags: list[str] = Field(default_factory=list)
    
    # Step 1: Convert model to schema
    print("\n1. Pydantic model → JSON Schema")
    original_schema = to_dict(Product)
    print(f"   ✓ Converted Product model to schema")
    print(f"     Properties: {list(original_schema.get('properties', {}).keys())}")
    
    # Check nested category
    category_prop = original_schema.get('properties', {}).get('category', {})
    print(f"     Category (nested) properties: {list(category_prop.get('properties', {}).keys())}")
    
    # Step 2: Convert schema back to model
    print("\n2. JSON Schema → Pydantic model")
    ProductModel2 = from_dict(original_schema, "Product2")
    print(f"   ✓ Generated ProductModel2 from schema")
    
    # Step 3: Create instance and verify
    print("\n3. Create instance with nested data")
    product = ProductModel2(
        product_id="prod-123",
        name="Widget",
        category={"name": "Electronics", "description": "Electronic items"},
        tags=["popular", "new"]
    )
    print(f"   ✓ Created product: {product.name}")
    print(f"   ✓ Category: {product.category.name} - {product.category.description}")
    print(f"   ✓ Tags: {product.tags}")
    
    # Step 4: Convert back to schema
    print("\n4. Pydantic model → JSON Schema (round-trip)")
    round_trip_schema = to_dict(ProductModel2)
    print(f"   ✓ Round-trip conversion successful")
    print(f"     Original has {len(original_schema.get('properties', {}))} properties")
    print(f"     Round-trip has {len(round_trip_schema.get('properties', {}))} properties")
    
    # Verify nested structure preserved
    rt_category = round_trip_schema.get('properties', {}).get('category', {})
    print(f"     Nested category preserved: {rt_category.get('type') == 'object'}")


def example_nested_from_separate_modules():
    """Demonstrate nested models from separate files/modules."""
    print("\n" + "=" * 70)
    print("Example 4j: Nested Models from Separate Modules")
    print("=" * 70)
    
    import tempfile
    import os
    import importlib.util
    
    # Create a temporary module file with a nested model
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''from pydantic import BaseModel, Field

class Address(BaseModel):
    """Address model from separate module."""
    street: str = Field(..., min_length=1, description="Street address")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=2, max_length=2, description="State code")
    zipcode: str = Field(..., pattern="^\\\\d{5}(-\\\\d{4})?$", description="ZIP code")
''')
        temp_module_path = f.name
    
    try:
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("temp_address_module", temp_module_path)
        address_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(address_module)
        Address = address_module.Address
        
        # Create a model in this file that uses the imported model
        class Person(BaseModel):
            """Person model using Address from separate module."""
            name: str = Field(..., min_length=1)
            age: int = Field(..., ge=0, le=150)
            address: Address  # Nested model from separate module
        
        # Convert to schema
        schema = to_dict(Person)
        
        print(f"\n✓ Converted Person model with Address from separate module")
        print(f"  Top-level properties: {list(schema.get('properties', {}).keys())}")
        
        # Check nested address schema
        address_prop = schema.get('properties', {}).get('address', {})
        print(f"\n  Address (from separate module) schema:")
        print(f"    Type: {address_prop.get('type')}")
        print(f"    Properties: {list(address_prop.get('properties', {}).keys())}")
        print(f"    Required: {address_prop.get('required', [])}")
        
        # Verify constraints from separate module are preserved
        address_street = address_prop.get('properties', {}).get('street', {})
        address_zipcode = address_prop.get('properties', {}).get('zipcode', {})
        print(f"\n  Constraints from separate module preserved:")
        print(f"    Address.street minLength: {address_street.get('minLength')}")
        print(f"    Address.zipcode pattern: {address_zipcode.get('pattern')}")
        
        print(f"\n✓ Key Point: Nested models can be defined in separate files/modules!")
        print(f"  The converter works with any BaseModel class accessible in Python runtime.")
        print(f"  It doesn't matter where the model is defined - same file, different file,")
        print(f"  or even dynamically imported modules.")
        
    except Exception as e:
        print(f"\n✗ Error testing separate modules: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if os.path.exists(temp_module_path):
            os.unlink(temp_module_path)


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
    example_nested_models()
    example_nested_arrays()
    example_deeply_nested()
    example_nested_round_trip()
    example_nested_from_separate_modules()
    
    print("\n" + "=" * 70)
    print("✓ All JSON Schema Converter examples completed!")
    print("=" * 70 + "\n")
