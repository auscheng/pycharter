"""
Pytest configuration and shared fixtures.

This module provides reusable fixtures for all tests.
"""

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from pycharter import from_dict


# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCHEMAS_DIR = FIXTURES_DIR / "schemas"
SAMPLE_DATA_DIR = FIXTURES_DIR / "sample_data"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def schemas_dir() -> Path:
    """Return the path to the schemas directory."""
    return SCHEMAS_DIR


@pytest.fixture
def sample_data_dir() -> Path:
    """Return the path to the sample data directory."""
    return SAMPLE_DATA_DIR


def load_schema(filename: str) -> Dict[str, Any]:
    """Helper function to load a schema from fixtures."""
    schema_path = SCHEMAS_DIR / filename
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema fixture not found: {filename}")
    with open(schema_path) as f:
        return json.load(f)


def load_sample_data(filename: str) -> Dict[str, Any]:
    """Helper function to load sample data from fixtures."""
    data_path = SAMPLE_DATA_DIR / filename
    if not data_path.exists():
        raise FileNotFoundError(f"Sample data fixture not found: {filename}")
    with open(data_path) as f:
        return json.load(f)


# Schema fixtures
@pytest.fixture
def simple_person_schema() -> Dict[str, Any]:
    """Load the simple person schema fixture."""
    return load_schema("simple_person.json")


@pytest.fixture
def user_with_defaults_schema() -> Dict[str, Any]:
    """Load the user with defaults schema fixture."""
    return load_schema("user_with_defaults.json")


@pytest.fixture
def nested_address_schema() -> Dict[str, Any]:
    """Load the nested address schema fixture."""
    return load_schema("nested_address.json")


@pytest.fixture
def coercion_schema() -> Dict[str, Any]:
    """Load the coercion schema fixture."""
    return load_schema("with_coercion.json")


@pytest.fixture
def validation_schema() -> Dict[str, Any]:
    """Load the validation schema fixture."""
    return load_schema("with_validations.json")


@pytest.fixture
def coercion_and_validation_schema() -> Dict[str, Any]:
    """Load the coercion and validation schema fixture."""
    return load_schema("with_coercion_and_validation.json")


@pytest.fixture
def array_simple_schema() -> Dict[str, Any]:
    """Load the simple array schema fixture."""
    return load_schema("array_simple.json")


@pytest.fixture
def array_of_objects_schema() -> Dict[str, Any]:
    """Load the array of objects schema fixture."""
    return load_schema("array_of_objects.json")


@pytest.fixture
def complex_nested_schema() -> Dict[str, Any]:
    """Load the complex nested schema fixture."""
    return load_schema("complex_nested.json")


# Sample data fixtures
@pytest.fixture
def valid_person_data() -> Dict[str, Any]:
    """Load valid person sample data."""
    return load_sample_data("valid_person.json")


@pytest.fixture
def valid_user_data() -> Dict[str, Any]:
    """Load valid user sample data."""
    return load_sample_data("valid_user_with_defaults.json")


@pytest.fixture
def valid_nested_address_data() -> Dict[str, Any]:
    """Load valid nested address sample data."""
    return load_sample_data("valid_nested_address.json")


@pytest.fixture
def valid_coercion_data() -> Dict[str, Any]:
    """Load valid coercion sample data."""
    return load_sample_data("valid_with_coercion.json")


# Model fixtures (generated from schemas)
@pytest.fixture
def Person(simple_person_schema):
    """Generate Person model from simple_person_schema."""
    return from_dict(simple_person_schema, "Person")


@pytest.fixture
def User(user_with_defaults_schema):
    """Generate User model from user_with_defaults_schema."""
    return from_dict(user_with_defaults_schema, "User")


@pytest.fixture
def PersonWithAddress(nested_address_schema):
    """Generate PersonWithAddress model from nested_address_schema."""
    return from_dict(nested_address_schema, "PersonWithAddress")


@pytest.fixture
def CoercionModel(coercion_schema):
    """Generate CoercionModel from coercion_schema."""
    return from_dict(coercion_schema, "CoercionModel")


@pytest.fixture
def ValidationModel(validation_schema):
    """Generate ValidationModel from validation_schema."""
    return from_dict(validation_schema, "ValidationModel")

