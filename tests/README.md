# Test Suite

This directory contains the comprehensive test suite for pycharter.

## Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── fixtures/                # Mock data and test fixtures
│   ├── schemas/            # JSON schema examples
│   ├── sample_data/        # Sample data for testing
│   └── expected_outputs/   # Expected model outputs
├── test_converter.py       # Tests for converter module
├── test_coercion_validation.py  # Tests for coercion/validation
├── test_schema_parser.py   # Tests for schema parser
├── test_fixtures.py        # Tests using fixtures
└── test_integration.py     # Integration tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=pycharter --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_converter.py
```

### Run specific test
```bash
pytest tests/test_converter.py::test_from_dict_simple_schema
```

### Run with verbose output
```bash
pytest -v
```

### Run only fast tests (exclude slow markers)
```bash
pytest -m "not slow"
```

## Using Fixtures

The test suite uses pytest fixtures defined in `conftest.py`. These fixtures load mock data from the `fixtures/` directory.

### Example: Using Schema Fixtures

```python
def test_my_feature(simple_person_schema):
    """Test using a schema fixture."""
    Person = from_dict(simple_person_schema, "Person")
    person = Person(name="Test", age=25)
    assert person.name == "Test"
```

### Example: Using Sample Data Fixtures

```python
def test_with_data(simple_person_schema, valid_person_data):
    """Test using both schema and data fixtures."""
    Person = from_dict(simple_person_schema, "Person")
    person = Person(**valid_person_data)
    assert person.name == "Alice Smith"
```

## Available Fixtures

### Schema Fixtures
- `simple_person_schema` - Basic person schema
- `user_with_defaults_schema` - User with default values
- `nested_address_schema` - Nested address structure
- `coercion_schema` - Schema with coercion
- `validation_schema` - Schema with validations
- `coercion_and_validation_schema` - Both features
- `array_simple_schema` - Simple arrays
- `array_of_objects_schema` - Arrays of objects
- `complex_nested_schema` - Deeply nested structure

### Sample Data Fixtures
- `valid_person_data` - Valid person data
- `valid_user_data` - Valid user data
- `valid_nested_address_data` - Valid nested address data
- `valid_coercion_data` - Valid coercion test data

### Model Fixtures
- `Person` - Generated Person model
- `User` - Generated User model
- `PersonWithAddress` - Generated PersonWithAddress model
- `CoercionModel` - Generated CoercionModel
- `ValidationModel` - Generated ValidationModel

## Test Coverage

The test suite aims for comprehensive coverage:
- ✅ Basic schema conversion
- ✅ Nested objects
- ✅ Arrays (simple and complex)
- ✅ Default values
- ✅ Required/optional fields
- ✅ Coercion functions
- ✅ Validation functions
- ✅ Error handling
- ✅ File loading
- ✅ JSON string parsing
- ✅ Edge cases

## Adding New Tests

When adding new tests:

1. **Use fixtures when possible** - Don't duplicate schema definitions
2. **Add fixtures if needed** - If you need new mock data, add it to `fixtures/`
3. **Follow naming conventions** - `test_<feature>_<scenario>`
4. **Add docstrings** - Explain what the test verifies
5. **Test both success and failure cases** - Use `pytest.raises()` for errors

## Fixtures Directory

The `fixtures/` directory serves dual purposes:
1. **Testing** - Provides mock data for tests
2. **Documentation** - Shows users example schemas and data

See `fixtures/README.md` for more information.

