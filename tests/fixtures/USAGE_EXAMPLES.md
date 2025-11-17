# Using Test Fixtures as Examples

The fixtures in this directory are not just for testing—they're also excellent examples for users learning how to use pycharter.

## Quick Examples

### Example 1: Simple Schema

**Schema** (`schemas/simple_person.json`):
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer"},
    "email": {"type": "string"}
  },
  "required": ["name", "age"]
}
```

**Usage**:
```python
from pycharter import from_dict
import json

# Load schema
with open('tests/fixtures/schemas/simple_person.json') as f:
    schema = json.load(f)

# Generate model
Person = from_dict(schema, "Person")

# Create instance
person = Person(name="Alice", age=30, email="alice@example.com")
print(person.name)  # "Alice"
```

### Example 2: With Coercion

**Schema** (`schemas/with_coercion.json`):
```json
{
  "properties": {
    "id": {
      "type": "string",
      "coercion": "coerce_to_string"
    },
    "count": {
      "type": "integer",
      "coercion": "coerce_to_integer"
    }
  }
}
```

**Usage**:
```python
from pycharter import from_dict
import json

with open('tests/fixtures/schemas/with_coercion.json') as f:
    schema = json.load(f)

Model = from_dict(schema, "MyModel")

# Coercion happens automatically
instance = Model(id=12345, count="42")
print(instance.id)    # "12345" (coerced to string)
print(instance.count) # 42 (coerced to integer)
```

### Example 3: With Validations

**Schema** (`schemas/with_validations.json`):
```json
{
  "properties": {
    "code": {
      "type": "string",
      "validations": {
        "min_length": {"threshold": 3},
        "max_length": {"threshold": 10},
        "no_capital_characters": null
      }
    }
  }
}
```

**Usage**:
```python
from pycharter import from_dict
from pydantic import ValidationError
import json

with open('tests/fixtures/schemas/with_validations.json') as f:
    schema = json.load(f)

Model = from_dict(schema, "MyModel")

# Valid
instance = Model(code="abc123")
print(instance.code)  # "abc123"

# Invalid - too short
try:
    Model(code="ab")
except ValidationError as e:
    print("Validation failed:", e)
```

### Example 4: Nested Objects

**Schema** (`schemas/nested_address.json`):
```json
{
  "properties": {
    "name": {"type": "string"},
    "address": {
      "type": "object",
      "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"}
      }
    }
  }
}
```

**Usage**:
```python
from pycharter import from_dict
import json

with open('tests/fixtures/schemas/nested_address.json') as f:
    schema = json.load(f)

Person = from_dict(schema, "Person")

person = Person(
    name="Alice",
    address={"street": "123 Main St", "city": "NYC", "state": "NY", "zipcode": "10001"}
)

print(person.address.city)  # "NYC"
```

## Copy and Modify

Feel free to:
1. Copy any schema file to use as a starting point
2. Modify it for your needs
3. Use it with `from_file()` or `from_dict()`

These fixtures demonstrate real-world patterns and best practices.

