"""
Tests demonstrating the use of fixtures and mock data.

These tests show how to use the fixtures directory for testing
and serve as examples for users.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from pycharter import from_dict, from_file


class TestUsingFixtures:
    """Tests using fixtures from conftest.py."""

    def test_simple_person_with_fixture(self, simple_person_schema, valid_person_data):
        """Test simple person schema using fixtures."""
        Person = from_dict(simple_person_schema, "Person")
        person = Person(**valid_person_data)
        
        assert person.name == "Alice Smith"
        assert person.age == 30
        assert person.email == "alice@example.com"

    def test_user_with_defaults_fixture(self, user_with_defaults_schema, valid_user_data):
        """Test user schema with defaults using fixtures."""
        User = from_dict(user_with_defaults_schema, "User")
        user = User(**valid_user_data)
        
        assert user.username == "alice"
        assert user.active is True  # Default value
        assert user.role == "user"  # Default value

    def test_nested_address_fixture(self, nested_address_schema, valid_nested_address_data):
        """Test nested address schema using fixtures."""
        Person = from_dict(nested_address_schema, "Person")
        person = Person(**valid_nested_address_data)
        
        assert person.name == "Bob Johnson"
        assert person.address.street == "123 Main Street"
        assert person.address.city == "New York"
        assert person.address.country == "USA"  # Default value

    def test_coercion_with_fixture(self, coercion_schema, valid_coercion_data):
        """Test coercion using fixtures."""
        Model = from_dict(coercion_schema, "CoercionModel")
        instance = Model(**valid_coercion_data)
        
        # Verify coercion happened
        assert isinstance(instance.id, str)  # 12345 -> "12345"
        assert isinstance(instance.count, int)  # "42" -> 42
        assert isinstance(instance.price, float)  # "99.99" -> 99.99
        assert isinstance(instance.is_active, bool)  # "true" -> True

    def test_validation_with_fixture(self, validation_schema):
        """Test validation using fixtures."""
        Model = from_dict(validation_schema, "ValidationModel")
        
        # Valid data
        valid = Model(code="abc123", status="active", score=50)
        assert valid.code == "abc123"
        assert valid.status == "active"
        assert valid.score == 50
        
        # Invalid: code too short
        with pytest.raises(PydanticValidationError):
            Model(code="ab", status="active", score=50)
        
        # Invalid: status not allowed
        with pytest.raises(PydanticValidationError):
            Model(code="abc123", status="invalid", score=50)
        
        # Invalid: score out of range
        with pytest.raises(PydanticValidationError):
            Model(code="abc123", status="active", score=150)

    def test_array_simple_fixture(self, array_simple_schema):
        """Test simple arrays using fixtures."""
        Model = from_dict(array_simple_schema, "ArrayModel")
        
        instance = Model(
            tags=["python", "pydantic"],
            scores=[1, 2, 3],
            prices=[10.5, 20.0, 30.5]
        )
        
        assert instance.tags == ["python", "pydantic"]
        assert instance.scores == [1, 2, 3]
        assert instance.prices == [10.5, 20.0, 30.5]

    def test_array_of_objects_fixture(self, array_of_objects_schema):
        """Test array of objects using fixtures."""
        Model = from_dict(array_of_objects_schema, "CartModel")
        
        instance = Model(
            items=[
                {"name": "Apple", "price": 1.50, "quantity": 5},
                {"name": "Banana", "price": 0.75, "quantity": 10}
            ]
        )
        
        assert len(instance.items) == 2
        assert instance.items[0].name == "Apple"
        assert instance.items[0].price == 1.50
        assert instance.items[1].quantity == 10

    def test_complex_nested_fixture(self, complex_nested_schema):
        """Test complex nested structure using fixtures."""
        Model = from_dict(complex_nested_schema, "AccountModel")
        
        instance = Model(
            user={
                "id": 1,
                "profile": {
                    "name": "Alice",
                    "address": {
                        "street": "123 Main St",
                        "city": "NYC"
                    }
                },
                "orders": [
                    {
                        "orderId": "ORD-001",
                        "items": [
                            {"productId": 1, "quantity": 2},
                            {"productId": 2, "quantity": 1}
                        ]
                    }
                ]
            }
        )
        
        assert instance.user.id == 1
        assert instance.user.profile.name == "Alice"
        assert instance.user.profile.address.city == "NYC"
        assert len(instance.user.orders) == 1
        assert instance.user.orders[0].orderId == "ORD-001"
        assert len(instance.user.orders[0].items) == 2


class TestLoadingFromFixtureFiles:
    """Tests loading schemas directly from fixture files."""

    def test_load_schema_from_file(self, schemas_dir):
        """Test loading a schema from fixture file."""
        schema_path = schemas_dir / "simple_person.json"
        Model = from_file(str(schema_path), "Person")
        
        person = Model(name="Test", age=25)
        assert person.name == "Test"
        assert person.age == 25

    def test_all_schema_fixtures_are_valid(self, schemas_dir):
        """Test that all schema fixtures are valid and can be loaded."""
        schema_files = list(schemas_dir.glob("*.json"))
        
        assert len(schema_files) > 0, "No schema fixtures found"
        
        for schema_file in schema_files:
            # Should not raise any errors
            Model = from_file(str(schema_file), "TestModel")
            assert Model is not None
            # Verify it's a Pydantic model
            assert hasattr(Model, "model_fields")

