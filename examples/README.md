# PyCharter Examples

This directory contains focused examples demonstrating each of PyCharter's five core services and a complete workflow example.

## Service Examples

Each example focuses on a specific service:

### 1. Contract Parser (`01_contract_parser.py`)
- Parse contract files (YAML/JSON)
- Parse contract dictionaries
- Access decomposed components (schema, governance, ownership, metadata)

**Run**: `python examples/01_contract_parser.py`

### 2. Metadata Store (`02_metadata_store.py`)
- Store metadata in database
- Retrieve stored schemas
- Use built-in implementations (InMemory, MongoDB, PostgreSQL, Redis)
- Implement custom database backends

**Available Implementations**:
- `InMemoryMetadataStore` - In-memory storage (testing/development)
- `MongoDBMetadataStore` - MongoDB document storage (requires `pymongo`)
- `PostgresMetadataStore` - PostgreSQL relational storage (requires `psycopg2-binary`)
- `RedisMetadataStore` - Redis key-value storage (requires `redis`)

**Run**: `python examples/02_metadata_store.py`

### 3. Pydantic Generator (`03_pydantic_generator.py`)
- Generate models from dictionaries
- Generate models from files
- Generate models from JSON strings
- Generate model files
- Handle nested objects and arrays

**Run**: `python examples/03_pydantic_generator.py`

### 4. JSON Schema Converter (`04_json_schema_converter.py`)
- Convert models to JSON Schema dictionaries
- Convert models to JSON strings
- Convert models to files
- Round-trip conversion (schema → model → schema)
- Preserve field constraints

**Run**: `python examples/04_json_schema_converter.py`

### 5. Runtime Validator (`05_runtime_validator.py`)
- Validate single records
- Validate batch data
- Strict vs lenient mode
- Use in ETL pipelines
- Validate with stored schemas (database-backed)
- Validate directly from contract files (no database required)

**Two Validation Modes**:
- **Database-Backed**: Use `validate_with_store()` to retrieve schemas/rules from metadata store
- **Contract-Based**: Use `validate_with_contract()` to validate directly from contract files/dicts

**Run**: `python examples/05_runtime_validator.py`

## Complete Workflow

### Complete Workflow (`complete_workflow.py`)
Demonstrates all five services working together in a complete data production journey:
1. Parse contract → 2. Store metadata → 3. Generate model → 4. Convert schema → 5. Validate data

**Run**: `python examples/complete_workflow.py`

### Separated Workflow (`06_separated_workflow.py`)
Demonstrates the improved workflow where schemas, metadata, and coercion/validation rules are stored separately:
1. Business provides metadata → 2. Developer writes Pydantic model → 3. Both define rules → 4. Store separately → 5. Runtime validation

**Run**: `python examples/06_separated_workflow.py`

**Key Features**:
- Business metadata stored separately
- Developer schemas (Pydantic → JSON Schema) stored separately
- Coercion and validation rules stored separately
- Runtime function retrieves and combines all components automatically

**Note**: This example may reference functions that are not yet implemented. See the main README for current capabilities.

## Additional Examples

### Comprehensive Examples (`example_usage.py`)
A comprehensive script demonstrating various features including:
- Standard JSON Schema keywords (minLength, maxLength, pattern, enum, etc.)
- Coercion and validation (PyCharter extensions)
- $ref and definitions
- Format fields (uuid, email, date-time)
- Reverse conversion (Pydantic → JSON Schema)
- Validation errors

**Run**: `python examples/example_usage.py`

**Note**: This example uses data from `data/schemas/` and `data/sample_data/` directories.

## Data Files

All data files (schemas, sample data, contracts) are located in the `data/` directory at the project root:

- `data/examples/` - Complete example with all components:
  - `book_models.py` - Pydantic models (developer-defined)
  - `book_schema.json` - JSON Schema (generated from models)
  - `book_coercion_rules.json` - Coercion rules
  - `book_validation_rules.json` - Validation rules
  - `book_metadata.json` - Business metadata
  - `book_contract.yaml` - Consolidated contract (all components)

**Contract Format**: Contracts are YAML or JSON files with the following structure:
```yaml
schema:                    # JSON Schema with coercion/validation
  type: object
  properties:
    field_name:
      type: string
      coercion: coerce_to_string  # Optional: PyCharter extension
      validations:                 # Optional: PyCharter extension
        min_length: {threshold: 1}

metadata:                  # Version and description
  version: "1.0.0"
  description: "Contract description"

ownership:                 # Ownership information
  owner: team-name
  team: department-name

governance_rules:          # Governance policies
  data_retention:
    days: 365
```

See `data/README.md` for detailed information about the data structure and formats.

## Running Examples

### Prerequisites

1. **Install the package**:
   ```bash
   pip install -e .
   # or with dev dependencies
   pip install -e ".[dev]"
   ```

2. **Optional dependencies** (for specific metadata stores):
   ```bash
   # For MongoDB
   pip install pymongo
   
   # For PostgreSQL
   pip install psycopg2-binary
   
   # For Redis
   pip install redis
   ```

### Run Individual Examples

```bash
# From project root
python examples/01_contract_parser.py
python examples/02_metadata_store.py
python examples/03_pydantic_generator.py
python examples/04_json_schema_converter.py
python examples/05_runtime_validator.py
python examples/complete_workflow.py
```

### Run All Examples

```bash
# Run each example script
for script in examples/0*.py examples/complete_workflow.py; do
    python "$script"
done
```

### Testing Metadata Stores

To test all metadata store implementations with your local Docker containers:

```bash
python tests/test_metadata_stores.py
```

This will test:
- InMemoryMetadataStore (always available)
- MongoDBMetadataStore (requires MongoDB running)
- PostgresMetadataStore (requires PostgreSQL running)
- RedisMetadataStore (requires Redis running)

## Example Output

Each example script provides:
- Clear section headers
- Step-by-step demonstrations
- Success/failure indicators (✓/✗)
- Explanatory output
- Error handling examples

## Next Steps

1. **Explore individual services** - Run each numbered example to understand specific services
2. **See the complete workflow** - Run `complete_workflow.py` to see all services together
3. **Modify examples** - Adapt examples to your use case
4. **Read the docs** - Check the main `README.md` for full documentation

## Notes

- **Data Location**: All examples use data from the `data/` directory
  - `data/examples/` - Complete book example with all components
  - `data/schemas/` - JSON Schema files
  - `data/sample_data/` - Sample data files
- **Self-Contained**: Examples are self-contained and can be run independently
- **Temporary Files**: Some examples may create temporary files (like generated models) that can be cleaned up
- **Package Installation**: Make sure you have the package installed: `pip install -e .` or `make install-dev`
- **Metadata Stores**: The `InMemoryMetadataStore` is always available. Other stores require their respective database drivers to be installed
- **Contract Files**: Contract files should be in YAML or JSON format with `schema`, `metadata`, `ownership`, and `governance_rules` sections

## Quick Start Example

Here's a quick example showing the basic workflow:

```python
from pycharter import (
    parse_contract_file,
    InMemoryMetadataStore,
    from_dict,
    validate,
)

# 1. Parse contract
metadata = parse_contract_file("data/examples/book_contract.yaml")

# 2. Store in metadata store
store = InMemoryMetadataStore()
store.connect()
schema_id = store.store_schema("book", metadata.schema, version="1.0.0")
store.store_ownership(schema_id, owner=metadata.ownership.get("owner"))

# 3. Generate Pydantic model
stored_schema = store.get_schema(schema_id)
BookModel = from_dict(stored_schema, "Book")

# 4. Validate data
result = validate(BookModel, {
    "isbn": "9780123456789",
    "title": "Python Programming",
    "author": {"name": "John Doe"},
    "price": 29.99,
    "pages": 500,
    "published_date": "2024-01-15T10:00:00Z"
})

if result.is_valid:
    print(f"Valid book: {result.data.title}")
```
