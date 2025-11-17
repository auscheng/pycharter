# Expected Outputs

This directory contains examples of what the generated Pydantic models look like and how they behave.

## Usage

These examples show:
- What fields are available on generated models
- How to access nested properties
- What validation errors look like
- How coercion transforms data

## Example

Given the schema in `schemas/simple_person.json`:

```python
from pycharter import from_dict
import json

# Load schema
with open('schemas/simple_person.json') as f:
    schema = json.load(f)

# Generate model
Person = from_dict(schema, "Person")

# Create instance
person = Person(name="Alice", age=30, email="alice@example.com")

# Access fields
print(person.name)   # "Alice"
print(person.age)    # 30
print(person.email)  # "alice@example.com"

# Model validation
person.model_dump()  # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
```

