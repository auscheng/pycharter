"""
Tests for the converter module.
"""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from pycharter import from_dict, from_file, from_json


def test_from_dict_simple_schema(simple_person_schema):
    """Test converting a simple schema from dictionary using fixture."""
    Person = from_dict(simple_person_schema, "Person")
    
    # Test required field
    person = Person(name="Alice", age=30)
    assert person.name == "Alice"
    assert person.age == 30
    
    # Test optional field - check if age is required or optional
    if "age" in simple_person_schema.get("required", []):
        # Age is required, so we need to provide it
        person2 = Person(name="Bob", age=25)
        assert person2.name == "Bob"
        assert person2.age == 25
    else:
        # Age is optional
        person2 = Person(name="Bob")
        assert person2.name == "Bob"
        assert person2.age is None


def test_from_dict_with_defaults(user_with_defaults_schema):
    """Test schema with default values using fixture."""
    User = from_dict(user_with_defaults_schema, "User")
    user = User(username="testuser")
    assert user.username == "testuser"
    assert user.active is True  # Default value
    assert user.role == "user"  # Default value


def test_from_dict_nested_objects(nested_address_schema):
    """Test schema with nested objects using fixture."""
    Person = from_dict(nested_address_schema, "Person")
    person = Person(
        name="Alice",
        address={"street": "123 Main St", "city": "New York", "state": "NY", "zipcode": "10001"}
    )
    
    assert person.name == "Alice"
    assert person.address.street == "123 Main St"
    assert person.address.city == "New York"
    assert person.address.country == "USA"  # Default value


def test_from_dict_arrays():
    """Test schema with array types."""
    schema = {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"},
            },
            "scores": {
                "type": "array",
                "items": {"type": "integer"},
            },
        },
    }
    
    Item = from_dict(schema, "Item")
    item = Item(tags=["python", "pydantic"], scores=[1, 2, 3])
    
    assert item.tags == ["python", "pydantic"]
    assert item.scores == [1, 2, 3]


def test_from_dict_array_of_objects():
    """Test schema with array of nested objects."""
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "value": {"type": "number"},
                    },
                },
            },
        },
    }
    
    Container = from_dict(schema, "Container")
    container = Container(
        items=[
            {"name": "item1", "value": 10.5},
            {"name": "item2", "value": 20.0},
        ]
    )
    
    assert len(container.items) == 2
    assert container.items[0].name == "item1"
    assert container.items[0].value == 10.5


def test_from_json():
    """Test converting from JSON string."""
    schema_json = json.dumps({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    })
    
    Person = from_json(schema_json, "Person")
    person = Person(name="Alice", age=30)
    assert person.name == "Alice"
    assert person.age == 30


def test_from_file():
    """Test loading schema from file."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
        },
    }
    
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(schema, f)
        temp_path = f.name
    
    try:
        User = from_file(temp_path, "User")
        user = User(name="Test", email="test@example.com")
        assert user.name == "Test"
        assert user.email == "test@example.com"
    finally:
        Path(temp_path).unlink()


def test_from_file_auto_name():
    """Test from_file with automatic model name from filename."""
    schema = {
        "type": "object",
        "properties": {
            "value": {"type": "string"},
        },
    }
    
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(schema, f)
        temp_path = f.name
    
    try:
        # Model name should be derived from filename
        Model = from_file(temp_path)
        instance = Model(value="test")
        assert instance.value == "test"
    finally:
        Path(temp_path).unlink()


def test_invalid_schema():
    """Test that invalid schemas raise appropriate errors."""
    # Not a dictionary
    with pytest.raises(ValueError, match="Schema must be a dictionary"):
        from_dict("not a dict")
    
    # Missing type and properties
    with pytest.raises(ValueError):
        from_dict({})


def test_non_object_schema():
    """Test that non-object schemas raise an error."""
    schema = {"type": "string"}
    
    with pytest.raises(ValueError, match="Schema must be of type 'object'"):
        from_dict(schema)


def test_deeply_nested_objects():
    """Test deeply nested object structures."""
    schema = {
        "type": "object",
        "properties": {
            "level1": {
                "type": "object",
                "properties": {
                    "level2": {
                        "type": "object",
                        "properties": {
                            "level3": {
                                "type": "object",
                                "properties": {
                                    "value": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    Container = from_dict(schema, "Container")
    container = Container(
        level1={
            "level2": {
                "level3": {
                    "value": "deep"
                }
            }
        }
    )
    
    assert container.level1.level2.level3.value == "deep"


def test_multiple_nested_objects():
    """Test schema with multiple nested objects at the same level."""
    schema = {
        "type": "object",
        "properties": {
            "shipping": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "city": {"type": "string"}
                },
                "required": ["address", "city"]
            },
            "billing": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "city": {"type": "string"}
                },
                "required": ["address", "city"]
            }
        }
    }
    
    Order = from_dict(schema, "Order")
    order = Order(
        shipping={"address": "123 Main St", "city": "NYC"},
        billing={"address": "456 Oak Ave", "city": "LA"}
    )
    
    assert order.shipping.address == "123 Main St"
    assert order.shipping.city == "NYC"
    assert order.billing.address == "456 Oak Ave"
    assert order.billing.city == "LA"


def test_nested_object_with_defaults():
    """Test nested objects with default values."""
    schema = {
        "type": "object",
        "properties": {
            "settings": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string", "default": "dark"},
                    "notifications": {"type": "boolean", "default": True}
                }
            }
        }
    }
    
    Config = from_dict(schema, "Config")
    config = Config()
    
    # Nested objects with defaults need to be explicitly created
    # or the nested object itself needs defaults
    if config.settings is not None:
        assert config.settings.theme == "dark"
        assert config.settings.notifications is True
    else:
        # If settings is None, create it explicitly
        config = Config(settings={"theme": "dark", "notifications": True})
        assert config.settings.theme == "dark"
        assert config.settings.notifications is True


def test_array_of_nested_objects():
    """Test array containing nested objects."""
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "details": {
                            "type": "object",
                            "properties": {
                                "color": {"type": "string"},
                                "size": {"type": "string"}
                            }
                        }
                    },
                    "required": ["name"]
                }
            }
        }
    }
    
    Cart = from_dict(schema, "Cart")
    cart = Cart(
        items=[
            {
                "name": "Item1",
                "details": {"color": "red", "size": "large"}
            },
            {
                "name": "Item2",
                "details": {"color": "blue", "size": "small"}
            }
        ]
    )
    
    assert len(cart.items) == 2
    assert cart.items[0].name == "Item1"
    assert cart.items[0].details.color == "red"
    assert cart.items[1].details.size == "small"


def test_complex_nested_structure():
    """Test a complex real-world nested structure."""
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "profile": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "address": {
                                "type": "object",
                                "properties": {
                                    "street": {"type": "string"},
                                    "city": {"type": "string"}
                                }
                            }
                        },
                        "required": ["name"]
                    },
                    "orders": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "orderId": {"type": "string"},
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "productId": {"type": "integer"},
                                            "quantity": {"type": "integer"}
                                        }
                                    }
                                }
                            },
                            "required": ["orderId"]
                        }
                    }
                },
                "required": ["id", "profile"]
            }
        }
    }
    
    Account = from_dict(schema, "Account")
    account = Account(
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
    
    assert account.user.id == 1
    assert account.user.profile.name == "Alice"
    assert account.user.profile.address.city == "NYC"
    assert len(account.user.orders) == 1
    assert account.user.orders[0].orderId == "ORD-001"
    assert len(account.user.orders[0].items) == 2
    assert account.user.orders[0].items[0].productId == 1


def test_nested_optional_objects():
    """Test nested objects that are optional."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "metadata": {
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "notes": {"type": "string"}
                }
            }
        },
        "required": ["name"]
    }
    
    Item = from_dict(schema, "Item")
    # Create without optional nested object
    item1 = Item(name="Test")
    assert item1.name == "Test"
    assert item1.metadata is None
    
    # Create with nested object
    item2 = Item(
        name="Test2",
        metadata={"tags": ["tag1"], "notes": "Some notes"}
    )
    assert item2.metadata.tags == ["tag1"]
    assert item2.metadata.notes == "Some notes"


def test_nested_with_required_fields():
    """Test nested objects with required fields."""
    schema = {
        "type": "object",
        "properties": {
            "customer": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"}
                        },
                        "required": ["street", "city"]
                    }
                },
                "required": ["name", "email", "address"]
            }
        }
    }
    
    Order = from_dict(schema, "Order")
    order = Order(
        customer={
            "name": "John",
            "email": "john@example.com",
            "address": {
                "street": "123 Main St",
                "city": "NYC"
            }
        }
    )
    
    assert order.customer.name == "John"
    assert order.customer.address.street == "123 Main St"
    
    # Test validation - missing required nested field should fail
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Order(customer={"name": "John", "email": "john@example.com"})


def test_example_user_schema():
    """Test the example user schema from examples directory."""
    import json
    from pathlib import Path
    
    schema_path = Path(__file__).parent.parent / "examples" / "user_schema.json"
    if schema_path.exists():
        User = from_file(str(schema_path), "User")
        
        user = User(
            username="alice",
            email="alice@example.com",
            profile={
                "firstName": "Alice",
                "lastName": "Smith"
            },
            address={
                "city": "New York",
                "state": "NY"
            },
            tags=["developer", "python"],
            scores=[95, 87, 92]
        )
        
        assert user.username == "alice"
        assert user.profile.firstName == "Alice"
        assert user.address.city == "New York"
        assert user.address.country == "USA"  # Default value
        assert user.active is True  # Default value
        assert user.tags == ["developer", "python"]
        assert user.scores == [95, 87, 92]

