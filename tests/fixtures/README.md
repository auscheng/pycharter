# Test Fixtures and Mock Data

This directory contains mock data used for testing pycharter. These fixtures are also useful for users to understand:

- **What input schemas look like** - See `schemas/` directory
- **How to structure JSON schemas** - Various examples from simple to complex
- **Expected behavior** - See `expected_outputs/` directory

## Directory Structure

```
fixtures/
├── schemas/              # JSON schema examples (input data)
│   ├── simple_person.json
│   ├── nested_address.json
│   ├── with_coercion.json
│   ├── with_validations.json
│   └── ...
├── expected_outputs/     # Examples of generated models
└── sample_data/          # Sample data for testing models
```

## Schema Examples

### Simple Schemas
- `simple_person.json` - Basic object with string and integer fields
- `user_with_defaults.json` - Schema with default values

### Nested Structures
- `nested_address.json` - Object with nested address object
- `complex_nested.json` - Deeply nested structure with arrays

### Arrays
- `array_simple.json` - Simple arrays of primitives
- `array_of_objects.json` - Arrays containing nested objects

### Advanced Features
- `with_coercion.json` - Pre-validation type coercion
- `with_validations.json` - Post-validation rules
- `with_coercion_and_validation.json` - Both features combined

## Using These Fixtures

### In Tests

```python
import json
from pathlib import Path
from pycharter import from_dict

# Load a schema fixture
fixture_path = Path(__file__).parent / "fixtures" / "schemas" / "simple_person.json"
with open(fixture_path) as f:
    schema = json.load(f)

# Use it in tests
Person = from_dict(schema, "Person")
person = Person(name="Alice", age=30)
assert person.name == "Alice"
```

### For Learning

These fixtures serve as examples for users:
- Copy a schema file to understand the structure
- Modify it to test your own use cases
- See how different features work together

## Adding New Fixtures

When adding new test cases:
1. Add the schema to `schemas/` directory
2. Use descriptive names (e.g., `user_with_nested_profile.json`)
3. Include a `description` field explaining what the schema demonstrates
4. Add corresponding test data in `sample_data/` if needed

