# PyCharter Architecture

This repository provides five core services for data contract management and validation.

## Service Structure

### 1. Contract Parser (`pycharter.contract_parser`)
**Purpose**: Reads data contract files (YAML or JSON) and decomposes them into distinct metadata components.

**Location**: `pycharter/contract_parser/`

**Key Functions**:
- `parse_contract(contract_data)` - Parse contract dictionary
- `parse_contract_file(file_path)` - Load and parse contract file
- `ContractMetadata` - Container for decomposed metadata (schema, governance_rules, ownership, metadata)

**Example**:
```python
from pycharter import parse_contract_file, ContractMetadata

metadata = parse_contract_file("contract.yaml")
print(metadata.schema)
print(metadata.ownership)
```

### 2. Metadata Store Client (`pycharter.metadata_store`)
**Purpose**: Connects to a relational database (like AWS RDS) and manages storage/retrieval of decomposed metadata.

**Location**: `pycharter/metadata_store/`

**Key Classes**:
- `MetadataStoreClient` - Base client class (subclass for specific database implementations)

**Methods**:
- `store_schema()` - Store JSON Schema
- `get_schema()` - Retrieve schema
- `store_governance_rule()` - Store governance rules
- `store_ownership()` - Store ownership information
- `store_metadata()` - Store additional metadata

**Example**:
```python
from pycharter import MetadataStoreClient

client = MetadataStoreClient(connection_string="...")
# Subclass and implement for your database
```

### 3. Pydantic Generator (`pycharter.pydantic_generator`)
**Purpose**: Takes a JSON Schema and programmatically generates a Pydantic model.

**Location**: `pycharter/pydantic_generator/`

**Key Functions**:
- `generate_model(schema, model_name)` - Generate Pydantic model class
- `generate_model_file(schema, output_path, model_name)` - Generate Python file with model
- `from_dict()`, `from_json()`, `from_file()`, `from_url()` - Convenience functions

**Example**:
```python
from pycharter import from_dict, generate_model_file

schema = {"type": "object", "properties": {"name": {"type": "string"}}}
Person = from_dict(schema, "Person")
generate_model_file(schema, "person_model.py", "Person")
```

### 4. JSON Schema Converter (`pycharter.json_schema_converter`)
**Purpose**: Takes (complex) Pydantic models and programmatically generates an "enhanced or customized" JSON Schema.

**Location**: `pycharter/json_schema_converter/`

**Key Functions**:
- `to_dict(model)` - Convert model to JSON Schema dictionary
- `to_json(model)` - Convert model to JSON Schema string
- `to_file(model, file_path)` - Write JSON Schema to file
- `model_to_schema(model)` - Low-level conversion function

**Example**:
```python
from pycharter import to_dict, to_file
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

schema = to_dict(Person)
to_file(Person, "person_schema.json")
```

### 5. Runtime Validator (`pycharter.runtime_validator`)
**Purpose**: Lightweight utility that can be imported into any data processing script. Uses generated Pydantic models to perform data validation.

**Location**: `pycharter/runtime_validator/`

**Key Functions**:
- `validate(model, data)` - Validate data against model
- `validate_batch(model, data_list)` - Validate batch of data
- `ValidationResult` - Result container (is_valid, data, errors)

**Example**:
```python
from pycharter import validate, ValidationResult

result = validate(Person, {"name": "Alice", "age": 30})
if result.is_valid:
    print(result.data.name)
else:
    print(result.errors)
```

## Shared Utilities (`pycharter.shared`)

Common utilities used across all services:
- **Coercions** - Pre-validation transformations
- **Validations** - Post-validation checks
- **JSON Schema Support** - Standard JSON Schema constraint handling
- **Schema Resolver** - Reference resolution ($ref, definitions)
- **Schema Parser** - Schema validation and normalization

## Directory Structure

```
pycharter/
├── __init__.py                 # Main package exports
├── contract_parser/            # Service 1
│   ├── __init__.py
│   └── parser.py
├── metadata_store/             # Service 2
│   ├── __init__.py
│   └── client.py
├── pydantic_generator/         # Service 3
│   ├── __init__.py
│   ├── generator.py
│   └── converter.py
├── json_schema_converter/      # Service 4
│   ├── __init__.py
│   ├── converter.py
│   └── reverse_converter.py
├── runtime_validator/           # Service 5
│   ├── __init__.py
│   └── validator.py
└── shared/                      # Shared utilities
    ├── __init__.py
    ├── coercions/
    ├── validations/
    ├── json_schema_support.py
    ├── schema_resolver.py
    ├── schema_parser.py
    └── json_schema_validator.py
```

## Usage Flow

1. **Parse Contract**: Read contract file and decompose metadata
2. **Store Metadata**: Save to database using MetadataStoreClient
3. **Generate Models**: Create Pydantic models from schemas
4. **Convert Schemas**: Convert models back to JSON Schema (if needed)
5. **Validate Data**: Use Runtime Validator in data processing scripts

## Design Principles

- **Explicit**: Clear separation of concerns, each service has a single responsibility
- **Readable**: Well-documented code with clear function names
- **Maintainable**: Shared utilities prevent code duplication
- **Simple**: No over-engineering, straightforward implementations

