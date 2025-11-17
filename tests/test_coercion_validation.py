"""
Tests for coercion and validation functionality.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from pycharter import from_dict


def test_coercion_to_string():
    """Test coercion to string."""
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "coercion": "coerce_to_string"
            }
        }
    }
    
    Person = from_dict(schema, "Person")
    
    # Test int coercion
    person1 = Person(name=123)
    assert person1.name == "123"
    assert isinstance(person1.name, str)
    
    # Test float coercion
    person2 = Person(name=3.14)
    assert person2.name == "3.14"
    
    # Test bool coercion
    person3 = Person(name=True)
    assert person3.name == "True"


def test_coercion_to_integer():
    """Test coercion to integer."""
    schema = {
        "type": "object",
        "properties": {
            "age": {
                "type": "integer",
                "coercion": "coerce_to_integer"
            }
        }
    }
    
    Person = from_dict(schema, "Person")
    
    # Test float coercion
    person1 = Person(age=3.14)
    assert person1.age == 3
    assert isinstance(person1.age, int)
    
    # Test string coercion
    person2 = Person(age="42")
    assert person2.age == 42
    
    # Test bool coercion
    person3 = Person(age=True)
    assert person3.age == 1


def test_validation_min_length():
    """Test min_length validation."""
    schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "validations": {
                    "min_length": {"threshold": 3}
                }
            }
        }
    }
    
    Item = from_dict(schema, "Item")
    
    # Valid - meets minimum
    item1 = Item(code="ABC")
    assert item1.code == "ABC"
    
    # Invalid - too short
    with pytest.raises(PydanticValidationError):
        Item(code="AB")


def test_validation_max_length():
    """Test max_length validation."""
    schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "validations": {
                    "max_length": {"threshold": 3}
                }
            }
        }
    }
    
    Item = from_dict(schema, "Item")
    
    # Valid - meets maximum
    item1 = Item(code="ABC")
    assert item1.code == "ABC"
    
    # Invalid - too long
    with pytest.raises(PydanticValidationError):
        Item(code="ABCD")


def test_validation_only_allow():
    """Test only_allow validation."""
    schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "validations": {
                    "only_allow": {"allowed_values": ["active", "inactive", "pending"]}
                }
            }
        }
    }
    
    Item = from_dict(schema, "Item")
    
    # Valid values
    item1 = Item(status="active")
    assert item1.status == "active"
    
    item2 = Item(status="pending")
    assert item2.status == "pending"
    
    # Invalid value
    with pytest.raises(PydanticValidationError):
        Item(status="invalid")


def test_validation_no_capital_characters():
    """Test no_capital_characters validation."""
    schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "validations": {
                    "no_capital_characters": None
                }
            }
        }
    }
    
    Item = from_dict(schema, "Item")
    
    # Valid - no capitals
    item1 = Item(code="abc123")
    assert item1.code == "abc123"
    
    # Invalid - has capitals
    with pytest.raises(PydanticValidationError):
        Item(code="Abc123")


def test_coercion_and_validation_together():
    """Test coercion followed by validation."""
    schema = {
        "type": "object",
        "properties": {
            "destination": {
                "type": "string",
                "coercion": "coerce_to_string",
                "validations": {
                    "min_length": {"threshold": 3},
                    "max_length": {"threshold": 3},
                    "no_capital_characters": None,
                    "only_allow": {"allowed_values": ["abc", "def", "ghi"]}
                }
            }
        }
    }
    
    Flight = from_dict(schema, "Flight")
    
    # Coerce int to string, then validate
    # "123" is 3 chars, so it passes length but fails only_allow
    with pytest.raises(PydanticValidationError):
        Flight(destination=123)  # Coerces to "123", but "123" not in allowed values
    
    # Valid example
    flight2 = Flight(destination="abc")
    assert flight2.destination == "abc"


def test_multiple_validations():
    """Test multiple validations on same field."""
    schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "validations": {
                    "min_length": {"threshold": 2},
                    "max_length": {"threshold": 5},
                    "no_special_characters": None
                }
            }
        }
    }
    
    Item = from_dict(schema, "Item")
    
    # Valid
    item1 = Item(code="ABC12")
    assert item1.code == "ABC12"
    
    # Invalid - too short
    with pytest.raises(PydanticValidationError):
        Item(code="A")
    
    # Invalid - too long
    with pytest.raises(PydanticValidationError):
        Item(code="ABCDEF")
    
    # Invalid - special characters
    with pytest.raises(PydanticValidationError):
        Item(code="ABC@12")


def test_nested_with_coercion():
    """Test coercion in nested objects."""
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "coercion": "coerce_to_string"
                    }
                }
            }
        }
    }
    
    Account = from_dict(schema, "Account")
    account = Account(user={"id": 12345})
    assert account.user.id == "12345"
    assert isinstance(account.user.id, str)

