"""
Tests for reverse conversion (Pydantic → JSON Schema).
"""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from pydantic import BaseModel, Field

from pycharter import to_dict, to_file, to_json


class TestReverseConversion:
    """Test Pydantic model to JSON Schema conversion."""

    def test_simple_model_to_schema(self):
        """Test converting a simple model to schema."""
        class Person(BaseModel):
            name: str
            age: int
        
        schema = to_dict(Person)
        
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["type"] == "integer"
        assert "name" in schema["required"]
        assert "age" in schema["required"]

    def test_model_with_defaults(self):
        """Test model with default values."""
        class User(BaseModel):
            username: str
            active: bool = True
            role: str = "user"
        
        schema = to_dict(User)
        
        assert "username" in schema["required"]
        assert "active" not in schema["required"]
        assert "role" not in schema["required"]
        assert schema["properties"]["active"]["default"] is True
        assert schema["properties"]["role"]["default"] == "user"

    def test_model_with_field_constraints(self):
        """Test model with Field constraints."""
        class Person(BaseModel):
            name: str = Field(..., min_length=3, max_length=50)
            age: int = Field(ge=0, le=120)
            email: str = Field(default="")
        
        schema = to_dict(Person)
        
        assert schema["properties"]["name"]["minLength"] == 3
        assert schema["properties"]["name"]["maxLength"] == 50
        assert schema["properties"]["age"]["minimum"] == 0
        assert schema["properties"]["age"]["maximum"] == 120
        assert schema["properties"]["email"]["default"] == ""

    def test_nested_model_to_schema(self):
        """Test nested model conversion."""
        class Address(BaseModel):
            street: str
            city: str
        
        class Person(BaseModel):
            name: str
            address: Address
        
        schema = to_dict(Person)
        
        assert schema["properties"]["address"]["type"] == "object"
        assert "street" in schema["properties"]["address"]["properties"]
        assert "city" in schema["properties"]["address"]["properties"]

    def test_array_fields(self):
        """Test array fields in model."""
        class Product(BaseModel):
            name: str
            tags: list[str]
        
        schema = to_dict(Product)
        
        assert schema["properties"]["tags"]["type"] == "array"
        assert schema["properties"]["tags"]["items"]["type"] == "string"

    def test_enum_field(self):
        """Test enum/Literal field."""
        from typing import Literal
        
        class Status(BaseModel):
            status: Literal["active", "inactive", "pending"]
        
        schema = to_dict(Status)
        
        # Enum should be converted
        assert "enum" in schema["properties"]["status"] or "const" in schema["properties"]["status"]

    def test_to_json(self):
        """Test converting to JSON string."""
        class Person(BaseModel):
            name: str
            age: int
        
        schema_json = to_json(Person)
        schema = json.loads(schema_json)
        
        assert schema["type"] == "object"
        assert "name" in schema["properties"]

    def test_to_file(self):
        """Test converting to file."""
        class Person(BaseModel):
            name: str
            age: int
        
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
        
        try:
            to_file(Person, temp_path)
            
            with open(temp_path) as f:
                schema = json.load(f)
            
            assert schema["type"] == "object"
            assert "name" in schema["properties"]
        finally:
            Path(temp_path).unlink()

    def test_model_with_description(self):
        """Test model with description."""
        class Person(BaseModel):
            """A person model."""
            name: str
        
        schema = to_dict(Person)
        
        assert "description" in schema
        assert "A person model" in schema["description"]

    def test_complex_nested_model(self):
        """Test complex nested model."""
        class Address(BaseModel):
            street: str
            city: str
        
        class OrderItem(BaseModel):
            product_id: int
            quantity: int
        
        class Order(BaseModel):
            order_id: str
            customer: Address
            items: list[OrderItem]
        
        schema = to_dict(Order)
        
        assert schema["properties"]["customer"]["type"] == "object"
        assert schema["properties"]["items"]["type"] == "array"
        assert schema["properties"]["items"]["items"]["type"] == "object"

