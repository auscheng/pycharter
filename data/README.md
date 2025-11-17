# Data Directory

This directory contains all mock data, sample data, schemas, and contract files used by examples and tests.

## Directory Structure

```
data/
├── contracts/          # Data contract files (YAML/JSON)
├── schemas/           # JSON Schema definition files
└── sample_data/       # Sample data files matching the schemas
```

## Contracts (`contracts/`)

Data contract files that demonstrate the contract parser service. These files contain:
- Schema definitions (JSON Schema)
- Governance rules
- Ownership information
- Metadata

**Example**: `user_contract.yaml` - A complete data contract with all components

## Schemas (`schemas/`)

JSON Schema definition files that can be used to generate Pydantic models.

**Files**:
- `user_schema.json` - User schema with standard JSON Schema keywords
- `order_schema.json` - Order schema with x-validators and $ref references
- `product_schema.json` - Product schema with nested objects and arrays
- `activity_schema.json` - Activity schema with coercion

## Sample Data (`sample_data/`)

Sample data files that match the schemas. These are valid examples that should pass validation.

**Files**:
- `user_sample_data.json` - Valid user data
- `order_sample_data.json` - Valid order data
- `product_sample_data.json` - Valid product data
- `activity_sample_data.json` - Valid activity data

## Usage

### In Examples

```python
from pathlib import Path
from pycharter import from_file

# Get data directory
DATA_DIR = Path(__file__).parent.parent / "data"

# Load schema
User = from_file(str(DATA_DIR / "schemas" / "user_schema.json"), "User")

# Load sample data
import json
with open(DATA_DIR / "sample_data" / "user_sample_data.json") as f:
    user_data = json.load(f)

# Use the data
user = User(**user_data)
```

### In Tests

```python
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
schema_path = DATA_DIR / "schemas" / "user_schema.json"
```

## Notes

- All schema files are valid JSON Schema Draft 2020-12
- Sample data files are valid and should pass validation
- Contract files can be in YAML or JSON format
- These files are used by examples and can be referenced in your own code

