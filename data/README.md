# Data Directory

This directory contains complete examples demonstrating the PyCharter workflow with all components.

## Directory Structure

```
data/
└── examples/                      # Complete examples with all components
    ├── book/                      # Book data contract example
    │   ├── book_models.py              # Pydantic models (developer-defined)
    │   ├── book_schema.json            # JSON Schema (generated from models)
    │   ├── book_coercion_rules.json    # Coercion rules (developer + business)
    │   ├── book_validation_rules.json   # Validation rules (developer + business)
    │   ├── book_metadata.json          # Metadata (business-defined)
    │   └── book_contract.yaml          # Consolidated contract (all components)
    ├── aircraft/                  # Aircraft data contract example
    │   ├── aircraft_models.py          # Pydantic models
    │   ├── aircraft_schema.json        # JSON Schema
    │   ├── aircraft_schema.yaml        # JSON Schema (YAML format)
    │   ├── aircraft_coercion_rules.json    # Coercion rules
    │   ├── aircraft_coercion_rules.yaml    # Coercion rules (YAML format)
    │   ├── aircraft_validation_rules.json  # Validation rules
    │   ├── aircraft_validation_rules.yaml  # Validation rules (YAML format)
    │   ├── aircraft_metadata.json          # Metadata
    │   ├── aircraft_metadata.yaml          # Metadata (YAML format)
    │   ├── aircraft_contract.yaml          # Consolidated contract
    │   └── aircraft.csv                    # Sample data
    ├── airports_and_geographic_information/  # Additional examples
    │   └── airport_and_geographic_information_models.py
    └── README.md                   # Detailed documentation (this file)
```

## Complete Examples

The `examples/` directory contains complete, working examples demonstrating all aspects of the PyCharter workflow.

### Book Data Contract Example

The `book/` subdirectory contains a simple, well-documented example perfect for learning PyCharter.

### Aircraft Data Contract Example

The `aircraft/` subdirectory contains a comprehensive real-world example with:
- 41 fields with complex data types
- Both JSON and YAML format files
- Complete workflow demonstration in `notebooks/__draft1.py`
- Sample CSV data for validation

## Book Example Components

1. **Pydantic Models** (`book/book_models.py`)
   - Developer-defined technical schema as Python code
   - Contains `Book` and `Author` models with nested structures
   - Demonstrates type hints, Field constraints, and validation

2. **JSON Schema** (`book/book_schema.json`)
   - Generated from Pydantic models using `to_dict()`
   - Standard JSON Schema Draft 2020-12 format
   - Can be stored, versioned, and used across systems

3. **Coercion Rules** (`book/book_coercion_rules.json`)
   - Pre-validation data transformation rules
   - Defines how to convert data types (string → integer, etc.)
   - Example: `"isbn": "coerce_to_string"` ensures ISBN is always a string

4. **Validation Rules** (`book/book_validation_rules.json`)
   - Post-validation business rules
   - Custom validation beyond standard JSON Schema
   - Example: `"price": {"greater_than_or_equal_to": {"threshold": 0}}`

5. **Metadata** (`book/book_metadata.json`)
   - Business-defined ownership, governance, and business rules
   - Version information, team ownership, data retention policies
   - Business rules (pricing, inventory management)

6. **Consolidated Contract** (`book/book_contract.yaml`)
   - All components merged into a single YAML file
   - Can be parsed by `parse_contract_file()`
   - Single source of truth for the complete contract

## Workflows

### Separated Workflow (Recommended)

1. **Developer** writes `book/book_models.py` (Pydantic models)
2. **Developer** converts to `book/book_schema.json` using `to_dict()`
3. **Developer + Business** define `book/book_coercion_rules.json` and `book/book_validation_rules.json`
4. **Business** defines `book/book_metadata.json`
5. **All components stored separately** in metadata store
6. **Runtime** retrieves and combines all components for validation

### Combined Workflow (Alternative)

1. All components combined into `book/book_contract.yaml`
2. Contract parsed using `parse_contract_file()`
3. Components extracted and stored in metadata store
4. Runtime validation uses stored components

## Usage Examples

### Parse Consolidated Contract

```python
from pathlib import Path
from pycharter import parse_contract_file

contract_path = Path("data/examples/book/book_contract.yaml")
metadata = parse_contract_file(str(contract_path))

print(metadata.schema)  # JSON Schema
print(metadata.ownership)  # Ownership info
print(metadata.governance_rules)  # Governance rules
print(metadata.versions)  # Component versions
```

### Validate Directly from Contract (No Database)

```python
from pycharter import validate_with_contract, get_model_from_contract

# Simplest: validate directly from file
result = validate_with_contract(
    "data/examples/book/book_contract.yaml",
    {
        "isbn": "9780123456789",
        "title": "Python Guide",
        "author": {"name": "John Doe"},
        "price": 39.99,
        "pages": 500,
        "published_date": "2024-01-15T10:00:00Z"
    }
)

if result.is_valid:
    print(f"Valid book: {result.data.title}")

# Efficient: get model once, validate multiple times
BookModel = get_model_from_contract("data/examples/book/book_contract.yaml")
result1 = validate(BookModel, data1)
result2 = validate(BookModel, data2)
```

### Generate Schema from Pydantic Model

```python
from pycharter import to_dict
from data.examples.book.book_models import Book

schema = to_dict(Book)
# Save to book/book_schema.json
```

### Store Components Separately

```python
from pycharter import InMemoryMetadataStore
import json

store = InMemoryMetadataStore()
store.connect()

# Load components
with open("data/examples/book/book_schema.json") as f:
    schema = json.load(f)
with open("data/examples/book/book_coercion_rules.json") as f:
    coercion_rules = json.load(f)["rules"]
with open("data/examples/book/book_validation_rules.json") as f:
    validation_rules = json.load(f)["rules"]
with open("data/examples/book/book_metadata.json") as f:
    metadata = json.load(f)

# Store separately
schema_id = store.store_schema("book", schema, version="1.0.0")
store.store_metadata(schema_id, metadata, "schema")
store.store_coercion_rules(schema_id, coercion_rules, "1.0.0")
store.store_validation_rules(schema_id, validation_rules, "1.0.0")
```

### Runtime Validation

```python
from pycharter import validate_with_store

# Automatically retrieves and combines all components
result = validate_with_store(
    store=store,
    schema_id=schema_id,
    data={
        "isbn": "9780123456789",
        "title": "Python Programming",
        "author": {"name": "John Doe", "email": "john@example.com"},
        "price": 29.99,
        "pages": 500,
        "published_date": "2024-01-15T10:00:00Z"
    },
    version="1.0.0"
)

if result.is_valid:
    print(f"Valid book: {result.data.title}")
```

## Key Points

1. **Separation of Concerns**: Schema, rules, and metadata are defined separately
2. **Independent Versioning**: Each component can be versioned independently
3. **Collaboration**: Business and developer can work in parallel
4. **Flexibility**: Components can be combined at runtime or stored as a single contract
5. **Standards Compliance**: Schema follows JSON Schema Draft 2020-12 standard

## File Descriptions

### `book/book_models.py`
Developer-defined Pydantic models that represent the technical schema. This is what developers write as Python code.

**Example**:
```python
from data.examples.book.book_models import Book, Author

book = Book(
    isbn="9780123456789",
    title="Python Programming",
    author=Author(name="John Doe"),
    price=29.99,
    pages=500,
    published_date="2024-01-15T10:00:00Z"
)
```

### `book/book_schema.json`
JSON Schema equivalent of the Pydantic models. Generated automatically using `to_dict(Book)`.

**Purpose**: Standard JSON Schema format that can be stored, versioned, and used across systems.

### `book/book_coercion_rules.json`
Rules for data transformation before validation. Defines how to convert incoming data types.

**Example**:
```json
{
  "rules": {
    "isbn": "coerce_to_string",
    "price": "coerce_to_float",
    "pages": "coerce_to_integer"
  }
}
```

### `book/book_validation_rules.json`
Additional validation rules beyond standard JSON Schema. Custom business and technical validation.

**Example**:
```json
{
  "rules": {
    "isbn": {
      "min_length": {"threshold": 10}
    },
    "price": {
      "greater_than_or_equal_to": {"threshold": 0}
    }
  }
}
```

### `book/book_metadata.json`
Business-defined metadata including ownership, governance, versioning, and business rules.

**Example**:
```json
{
  "owner": "product-team",
  "team": "data-engineering",
  "governance_rules": {
    "data_retention": {"days": 2555},
    "access_control": {"level": "public"}
  },
  "business_rules": {
    "pricing": {"currency": "USD", "min_price": 0.0}
  }
}
```

### `book/book_contract.yaml`
Consolidated contract combining all components into a single YAML file. This is the single source of truth that can be parsed by `parse_contract_file()`.

**Structure**:
```yaml
schema:                    # JSON Schema with coercion/validation merged
  type: object
  properties:
    isbn:
      type: string
      coercion: coerce_to_string
      validations:
        min_length: {threshold: 10}
    # ... more fields

metadata:                  # Version and description
  version: "1.0.0"
  description: "Book data contract"

ownership:                 # Ownership information
  owner: product-team
  team: data-engineering

governance_rules:          # Governance policies
  data_retention:
    days: 2555

business_rules:            # Business rules
  pricing:
    currency: USD
```

## See Also

- [Examples Directory](../../examples/) - Usage examples for each service
- [Data Journey Guide](../../DATA_JOURNEY.md) - Complete workflow documentation
- [Main README](../../README.md) - Project overview and installation
