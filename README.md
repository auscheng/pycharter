# PyCharter

> **Dynamically generate Pydantic models from JSON schemas with coercion and validation support**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**PyCharter** is a powerful Python library that automatically converts JSON schemas into fully-functional Pydantic models. It fully supports the JSON Schema Draft 2020-12 standard, including all standard validation keywords (minLength, maxLength, pattern, enum, minimum, maximum, etc.), while also providing extensions for pre-validation coercion and post-validation checks. It handles nested objects, arrays, and custom validators, with all validation logic stored as data (not Python code).

## ✨ Features

- 🚀 **Dynamic Model Generation** - Convert JSON schemas to Pydantic models at runtime
- 📋 **JSON Schema Compliant** - Full support for JSON Schema Draft 2020-12 standard
- 🔄 **Type Coercion** - Automatic type conversion before validation (e.g., string → integer)
- ✅ **Custom Validators** - Built-in and extensible validation rules
- 🏗️ **Nested Structures** - Full support for nested objects and arrays
- 📦 **Multiple Input Formats** - Load schemas from dicts, JSON strings, files, or URLs
- 🎯 **Type Safe** - Full type hints and Pydantic v2 compatibility
- 🔧 **Extensible** - Register custom coercion and validation functions
- 📊 **Data-Driven** - All validation logic stored as JSON data, not Python code

## 📦 Installation

```bash
pip install pycharter
```

## 🚀 Quick Start

```python
from pycharter import from_dict

# Define your JSON schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}

# Generate a Pydantic model
Person = from_dict(schema, "Person")

# Use it like any Pydantic model
person = Person(name="Alice", age=30, email="alice@example.com")
print(person.name)  # Output: Alice
print(person.age)   # Output: 30
```

## 🏗️ Core Services & Data Production Journey

PyCharter provides **five core services** that work together to support a complete data production journey, from contract specification to runtime validation. Each service plays a critical role in managing data contracts and ensuring data quality throughout your pipeline.

### The Data Production Journey

The typical data production workflow follows this path:

```
1. Data Contract Specification
   ↓
2. Contract Parsing
   ↓
3. Metadata Storage
   ↓
4. Pydantic Model Generation
   ↓
5. Runtime Validation
```

### 1. 📄 Contract Parser (`pycharter.contract_parser`)

**Purpose**: Reads and decomposes data contract files into structured metadata components.

**When to Use**: At the beginning of your data production journey, when you have data contract files (YAML or JSON) that need to be processed and understood.

**How It Works**:
- Accepts data contract files containing schema definitions, governance rules, ownership information, and metadata
- Decomposes the contract into distinct components: `schema`, `governance_rules`, `ownership`, and `metadata`
- Returns a `ContractMetadata` object that separates concerns and makes each component accessible

**Example**:
```python
from pycharter import parse_contract_file, ContractMetadata

# Parse a contract file (YAML or JSON)
metadata = parse_contract_file("data_contract.yaml")

# Access decomposed components
schema = metadata.schema              # JSON Schema definition
governance = metadata.governance_rules # Governance policies
ownership = metadata.ownership         # Owner/team information
metadata_info = metadata.metadata      # Additional metadata
```

**Contribution to Journey**: The contract parser is the **entry point** that takes raw contract specifications and prepares them for downstream processing. It ensures that contracts are properly structured and that all components (schema, governance, ownership) are separated for independent handling.

---

### 2. 💾 Metadata Store Client (`pycharter.metadata_store`)

**Purpose**: Manages persistent storage and retrieval of decomposed metadata in a relational database.

**When to Use**: After parsing contracts, when you need to store metadata components (schemas, governance rules, ownership) in a database for versioning, querying, and governance.

**How It Works**:
- Connects to relational databases (PostgreSQL, MySQL, AWS RDS, etc.)
- Provides methods to store and retrieve schemas, governance rules, ownership information, and metadata
- Supports versioning and querying of stored metadata
- Base class that can be extended for specific database implementations

**Example**:
```python
from pycharter import MetadataStoreClient, parse_contract_file

# Parse contract
metadata = parse_contract_file("contract.yaml")

# Store in database (subclass MetadataStoreClient for your database)
class MyMetadataStore(MetadataStoreClient):
    def store_schema(self, schema_name, schema, version=None):
        # Implement database-specific storage logic
        pass

client = MyMetadataStore(connection_string="postgresql://...")
client.connect()

# Store decomposed components
schema_id = client.store_schema("user_schema", metadata.schema, version="1.0")
client.store_ownership(schema_id, owner="data-team", team="engineering")
client.store_governance_rule("pii_rule", {"type": "encrypt"}, schema_id)

# Retrieve later
stored_schema = client.get_schema(schema_id)
```

**Contribution to Journey**: The metadata store is the **persistence layer** that ensures contracts and their components are versioned, searchable, and accessible across your organization. It enables governance, audit trails, and schema evolution tracking.

---

### 3. 🏭 Pydantic Generator (`pycharter.pydantic_generator`)

**Purpose**: Dynamically generates fully-functional Pydantic models from JSON Schema definitions.

**When to Use**: After storing schemas (or directly from parsed contracts), when you need to generate Python models for type-safe data validation and processing.

**How It Works**:
- Takes JSON Schema definitions (from contracts or metadata store)
- Programmatically generates Pydantic model classes at runtime
- Supports all JSON Schema Draft 2020-12 features plus custom coercions and validations
- Can generate models from dictionaries, JSON strings, files, or URLs
- Optionally generates Python files with model definitions

**Example**:
```python
from pycharter import from_dict, generate_model_file, MetadataStoreClient

# Option 1: Generate from parsed contract
metadata = parse_contract_file("contract.yaml")
UserModel = from_dict(metadata.schema, "User")

# Option 2: Generate from stored schema
client = MetadataStoreClient(...)
schema = client.get_schema("user_schema_v1")
UserModel = from_dict(schema, "User")

# Option 3: Generate and save to file
generate_model_file(schema, "user_model.py", "User")
```

**Contribution to Journey**: The Pydantic generator is the **transformation engine** that converts declarative JSON Schema definitions into executable Python models. It bridges the gap between contract specifications (data) and runtime validation (code), enabling type-safe data processing.

---

### 4. 🔄 JSON Schema Converter (`pycharter.json_schema_converter`)

**Purpose**: Converts existing Pydantic models back into JSON Schema format (reverse conversion).

**When to Use**: When you have existing Pydantic models and need to generate JSON Schema definitions, or when you want to round-trip between schemas and models.

**How It Works**:
- Takes Pydantic model classes as input
- Generates JSON Schema dictionaries that represent the model structure
- Preserves validation rules, types, and constraints
- Can output to dictionaries, JSON strings, or files

**Example**:
```python
from pycharter import to_dict, to_file, to_json
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool = True

# Convert to JSON Schema
schema = to_dict(Product)
json_string = to_json(Product)
to_file(Product, "product_schema.json")

# Now you can use the schema with other services
ProductModel = from_dict(schema, "Product")  # Round-trip
```

**Contribution to Journey**: The JSON Schema converter enables **bidirectional conversion** between models and schemas. It's useful for:
- Generating schemas from existing code
- Round-trip validation (schema → model → schema)
- Integrating with systems that require JSON Schema format
- Documenting existing models as schemas

---

### 5. ✅ Runtime Validator (`pycharter.runtime_validator`)

**Purpose**: Lightweight validation utility for validating data against generated Pydantic models in production data pipelines.

**When to Use**: In your data processing scripts, ETL pipelines, API endpoints, or any place where you need to validate incoming data against contract specifications.

**How It Works**:
- Takes a Pydantic model (generated from a schema) and raw data
- Validates data against the model's constraints
- Returns a `ValidationResult` with validation status, validated data, and errors
- Supports single record and batch validation
- Can be used in strict mode (raises exceptions) or lenient mode (returns results)

**Example**:
```python
from pycharter import validate, validate_batch, from_dict, MetadataStoreClient

# Get model (from store or contract)
client = MetadataStoreClient(...)
schema = client.get_schema("user_schema_v1")
UserModel = from_dict(schema, "User")

# Validate single record
result = validate(UserModel, {"name": "Alice", "age": 30})
if result.is_valid:
    print(f"Valid user: {result.data.name}")
else:
    print(f"Validation errors: {result.errors}")

# Validate batch (e.g., in ETL pipeline)
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": "invalid"}  # Will fail validation
]

results = validate_batch(UserModel, users)
valid_users = [r.data for r in results if r.is_valid]
invalid_count = sum(1 for r in results if not r.is_valid)
```

**Contribution to Journey**: The runtime validator is the **enforcement layer** that ensures data quality in production. It validates actual data against contract specifications, catching violations early and preventing bad data from propagating through your systems.

---

### Complete Workflow Example

Here's how all five services work together in a complete data production journey:

```python
from pycharter import (
    parse_contract_file,
    MetadataStoreClient,
    from_dict,
    validate,
    to_dict
)

# Step 1: Parse contract specification
metadata = parse_contract_file("user_contract.yaml")

# Step 2: Store metadata in database
class MyStore(MetadataStoreClient):
    # ... implement database methods
    pass

store = MyStore(connection_string="...")
store.connect()
schema_id = store.store_schema("user", metadata.schema, version="1.0")
store.store_ownership(schema_id, owner="data-team", team="engineering")

# Step 3: Generate Pydantic model from stored schema
schema = store.get_schema(schema_id)
UserModel = from_dict(schema, "User")

# Step 4: (Optional) Convert model back to schema for documentation
schema_doc = to_dict(UserModel)

# Step 5: Validate data in production pipeline
def process_user_data(raw_data):
    result = validate(UserModel, raw_data)
    if result.is_valid:
        # Process validated data
        return result.data
    else:
        # Handle validation errors
        raise ValueError(f"Invalid data: {result.errors}")
```

---

### Service Integration Summary

| Service | Input | Output | Journey Stage |
|---------|-------|--------|---------------|
| **Contract Parser** | Contract files (YAML/JSON) | `ContractMetadata` | Contract Specification → Parsing |
| **Metadata Store** | `ContractMetadata` | Stored metadata (DB) | Parsing → Storage |
| **Pydantic Generator** | JSON Schema | Pydantic models | Storage → Model Generation |
| **JSON Schema Converter** | Pydantic models | JSON Schema | (Bidirectional) |
| **Runtime Validator** | Pydantic models + Data | `ValidationResult` | Model Generation → Validation |

Each service is designed to be **independent** yet **composable**, allowing you to use them individually or together as part of a complete data contract management system.

## 📖 Documentation

- **[Data Journey Guide](DATA_JOURNEY.md)** - Complete guide to the data production journey, including both combined and separated workflows

## 📚 Usage Examples

### Basic Usage

```python
from pycharter import from_dict, from_json, from_file

# From dictionary
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "published": {"type": "boolean", "default": False}
    }
}
Article = from_dict(schema, "Article")

# From JSON string
schema_json = '{"type": "object", "properties": {"name": {"type": "string"}}}'
User = from_json(schema_json, "User")

# From file
Product = from_file("product_schema.json", "Product")
```

### Nested Objects

```python
from pycharter import from_dict

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "zipcode": {"type": "string"}
            }
        }
    }
}

Person = from_dict(schema, "Person")
person = Person(
    name="Alice",
    address={
        "street": "123 Main St",
        "city": "New York",
        "zipcode": "10001"
    }
)

print(person.address.city)  # Output: New York
```

### Arrays and Collections

```python
from pycharter import from_dict

schema = {
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number"}
                }
            }
        }
    }
}

Cart = from_dict(schema, "Cart")
cart = Cart(
    tags=["python", "pydantic"],
    items=[
        {"name": "Apple", "price": 1.50},
        {"name": "Banana", "price": 0.75}
    ]
)

print(cart.items[0].name)  # Output: Apple
```

### Coercion and Validation

Charter supports **coercion** (pre-validation transformation) and **validation** (post-validation checks):

```python
from pycharter import from_dict

schema = {
    "type": "object",
    "properties": {
        "flight_number": {
            "type": "integer",
            "coercion": "coerce_to_integer"  # Convert string/float to int
        },
        "destination": {
            "type": "string",
            "coercion": "coerce_to_string",
            "validations": {
                "min_length": {"threshold": 3},
                "max_length": {"threshold": 3},
                "no_capital_characters": None,
                "only_allow": {"allowed_values": ["abc", "def", "ghi"]}
            }
        },
        "distance": {
            "type": "number",
            "coercion": "coerce_to_float",
            "validations": {
                "greater_than_or_equal_to": {"threshold": 0}
            }
        }
    }
}

Flight = from_dict(schema, "Flight")

# Coercion happens automatically
flight = Flight(
    flight_number="123",    # Coerced to int: 123
    destination="abc",      # Passes all validations
    distance="100.5"        # Coerced to float: 100.5
)
```

## 📋 Standard JSON Schema Support

Charter supports all standard JSON Schema Draft 2020-12 validation keywords:

| Keyword | Type | Description | Example |
|---------|------|-------------|---------|
| `minLength` | string | Minimum string length | `{"minLength": 3}` |
| `maxLength` | string | Maximum string length | `{"maxLength": 10}` |
| `pattern` | string | Regular expression pattern | `{"pattern": "^[a-z]+$"}` |
| `enum` | any | Allowed values | `{"enum": ["a", "b", "c"]}` |
| `const` | any | Single allowed value | `{"const": "fixed"}` |
| `minimum` | number | Minimum value (inclusive) | `{"minimum": 0}` |
| `maximum` | number | Maximum value (inclusive) | `{"maximum": 100}` |
| `exclusiveMinimum` | number | Minimum value (exclusive) | `{"exclusiveMinimum": 0}` |
| `exclusiveMaximum` | number | Maximum value (exclusive) | `{"exclusiveMaximum": 100}` |
| `multipleOf` | number | Must be multiple of | `{"multipleOf": 2}` |
| `minItems` | array | Minimum array length | `{"minItems": 1}` |
| `maxItems` | array | Maximum array length | `{"maxItems": 10}` |
| `uniqueItems` | array | Array items must be unique | `{"uniqueItems": true}` |

All schemas are validated against JSON Schema standard before processing, ensuring compliance.

## 🔧 Built-in Coercions (Charter Extensions)

| Coercion | Description |
|----------|-------------|
| `coerce_to_string` | Convert int, float, bool, datetime, dict, list to string |
| `coerce_to_integer` | Convert float, string (numeric), bool, datetime to int |
| `coerce_to_float` | Convert int, string (numeric), bool to float |
| `coerce_to_boolean` | Convert int, string to bool |
| `coerce_to_datetime` | Convert string (ISO format), timestamp to datetime |
| `coerce_to_uuid` | Convert string to UUID |

## ✅ Built-in Validations (Charter Extensions)

| Validation | Description | Configuration |
|------------|-------------|---------------|
| `min_length` | Minimum length for strings/arrays | `{"threshold": N}` |
| `max_length` | Maximum length for strings/arrays | `{"threshold": N}` |
| `only_allow` | Only allow specific values | `{"allowed_values": [...]}` |
| `greater_than_or_equal_to` | Numeric minimum | `{"threshold": N}` |
| `less_than_or_equal_to` | Numeric maximum | `{"threshold": N}` |
| `no_capital_characters` | No uppercase letters | `null` |
| `no_special_characters` | Only alphanumeric and spaces | `null` |

> **Note**: Charter extensions (`coercion` and `validations`) are optional and can be used alongside standard JSON Schema keywords. All validation logic is stored as data in the JSON schema, making it fully data-driven.

## 🎨 Custom Coercions and Validations

Extend Charter with your own coercion and validation functions:

```python
from pycharter.shared.coercions import register_coercion
from pycharter.shared.validations import register_validation

# Register custom coercion
def coerce_to_uppercase(data):
    if isinstance(data, str):
        return data.upper()
    return data

register_coercion("coerce_to_uppercase", coerce_to_uppercase)

# Register custom validation
def must_be_positive(threshold=0):
    def _validate(value, info):
        if value <= threshold:
            raise ValueError(f"Value must be > {threshold}")
        return value
    return _validate

register_validation("must_be_positive", must_be_positive)
```

## 📖 API Reference

### Main Functions

- **`from_dict(schema: dict, model_name: str = "DynamicModel")`** - Create model from dictionary
- **`from_json(json_string: str, model_name: str = "DynamicModel")`** - Create model from JSON string
- **`from_file(file_path: str, model_name: str = None)`** - Create model from JSON file
- **`from_url(url: str, model_name: str = "DynamicModel")`** - Create model from URL
- **`schema_to_model(schema: dict, model_name: str = "DynamicModel")`** - Low-level model generator

## 🎯 Design Principles & Requirements

Charter is designed to meet the following core requirements:

### ✅ JSON Schema Standard Compliance

All schemas must abide by conventional JSON Schema syntax and qualify as valid JSON Schema:

- **Validation**: All schemas are validated against JSON Schema Draft 2020-12 standard before processing
- **Standard Keywords**: Full support for all standard validation keywords (minLength, pattern, enum, minimum, maximum, etc.)
- **Compliance**: Uses `jsonschema` library for validation with graceful fallback

### ✅ Data-Driven Validation Logic

All schema information and complex field validation logic is stored as **data**, not Python code:

- **Coercion**: Referenced by name (string) in JSON: `"coercion": "coerce_to_integer"`
- **Validations**: Referenced by name with configuration (dict) in JSON: `"validations": {"min_length": {"threshold": 3}}`
- **No Code Required**: Validation rules are defined entirely in JSON schema files
- **Example**: `{"coercion": "coerce_to_string", "validations": {"min_length": {"threshold": 3}}}`

### ✅ Dynamic Pydantic Model Generation

Models are created dynamically at runtime from JSON schemas:

- **Runtime Generation**: Uses `pydantic.create_model()` to generate models on-the-fly
- **Dynamic Validators**: Field validators are dynamically attached using `field_validator` decorators
- **Multiple Sources**: Models can be created from dicts, JSON strings, files, or URLs
- **No Static Code**: All models are generated from data, not pre-defined classes

### ✅ Nested Schema Support

Full support for nested object schemas and complex structures:

- **Recursive Processing**: Nested objects are recursively processed into their own Pydantic models
- **Arrays of Objects**: Arrays containing nested objects are fully supported
- **Deep Nesting**: Deeply nested structures work correctly with full type safety
- **Type Safety**: Each nested object becomes its own typed Pydantic model

### ✅ Extension Fields

Custom fields can be added to JSON Schema to extend functionality:

- **`coercion`**: Pre-validation type conversion (e.g., string → integer)
- **`validations`**: Post-validation custom rules
- **Optional**: Extensions work alongside standard JSON Schema keywords
- **Separated**: Extensions are clearly distinguished from standard JSON Schema

### ✅ Complex Field Validation

Support for both standard and custom field validators:

- **Standard Validators**: minLength, pattern, enum, minimum, maximum, etc. (JSON Schema standard)
- **Custom Validators**: Extensible validation rules via `validations` field
- **Validation Order**: Coercion → Standard Validation → Pydantic Validation → Custom Validations
- **Factory Pattern**: Validators are factory functions that return validation functions

## 🚀 Development Setup

### Quick Setup

```bash
# Run setup script
./setup.sh

# Activate environment
source venv/bin/activate

# Run tests
pytest
```

### Using Make

```bash
make install-dev    # Install package and dev dependencies
make test          # Run tests
make format        # Format code with black and isort
make lint          # Run type checking with mypy
make check         # Run all checks (format, lint, test)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pycharter --cov-report=html

# Run specific test file
pytest tests/test_converter.py

# Run tests matching a pattern
pytest -k "coercion"
```

## 📦 Publishing to PyPI

```bash
# Update version in pyproject.toml
# Clean previous builds
make clean

# Build package
make build

# Test on TestPyPI
make publish-test

# Publish to PyPI
make publish
```

## 📋 JSON Schema Compliance

PyCharter is fully compliant with **JSON Schema Draft 2020-12** standard:

- All schemas are validated against the standard before processing
- Full support for all standard keywords (minLength, maxLength, pattern, enum, minimum, maximum, etc.)
- Optional extensions (`coercion` and `validations`) work alongside standard keywords
- Strict mode available to enforce standard-only schemas

## 🔗 Requirements

- Python 3.10+
- Pydantic >= 2.0.0
- jsonschema >= 4.0.0 (optional, for enhanced validation)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [GitHub](https://github.com/auscheng/schemantic)
- **Issues**: [GitHub Issues](https://github.com/auscheng/schemantic/issues)
- **Documentation**: [GitHub README](https://github.com/auscheng/schemantic#readme)

---

**Made with ❤️ for the Python community**
