# Sample Data

This directory contains sample data that can be used to test the generated Pydantic models.

## Usage

These sample data files show:
- Valid input data that should pass validation
- Invalid input data that should fail validation
- Edge cases and boundary conditions

## Example

```python
import json
from pathlib import Path
from pycharter import from_dict

# Load schema
schema_path = Path("fixtures/schemas/simple_person.json")
with open(schema_path) as f:
    schema = json.load(f)

# Generate model
Person = from_dict(schema, "Person")

# Load sample data
data_path = Path("fixtures/sample_data/valid_person.json")
with open(data_path) as f:
    data = json.load(f)

# Create instance
person = Person(**data)
```

