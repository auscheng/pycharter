# The Complete Data Journey: From Contract to Runtime Validation

This document describes the complete data production journey using PyCharter, from initial contract specification (collaboration between business units and developers) to runtime validation in production systems.

## Overview: The 5-Stage Journey

```
Business Unit (Data Definitions & Governance)
    ↓
Developer (Data Types & Technical Constraints)
    ↓
Contract File (YAML/JSON) - Single Source of Truth
    ↓
[PyCharter Services: Parse → Store → Generate → Validate]
    ↓
Runtime Validation (Production Systems)
```

---

## Stage 1: Contract Creation (Business + Developer Collaboration)

**Participants**: 
- **Business Unit**: Defines data definitions, governance rules, ownership, and business requirements
- **Developer**: Adds technical constraints, data types, formats, and validation rules

**What Happens**:
- Business stakeholders define what data means, who owns it, and governance policies
- Developers add technical specifications: data types, formats (UUID, email, date-time), validation constraints (minLength, maxLength, pattern), and technical requirements
- Together they create a **data contract file** (YAML or JSON) that serves as the single source of truth

**Contract File Structure** (`data/examples/book/book_contract.yaml`):

```yaml
schema:                    # Developer: Technical schema definition
  type: object
  properties:
    user_id:
      type: string
      format: uuid         # Developer: Technical constraint
      description: Unique identifier for the user
    username:
      type: string
      minLength: 3         # Developer: Technical validation
      maxLength: 20
      pattern: "^[a-z0-9_]+$"
      description: Username (lowercase alphanumeric and underscores only)
    email:
      type: string
      format: email        # Developer: Technical format
      description: User's email address
    age:
      type: integer
      minimum: 0           # Developer: Business rule enforcement
      maximum: 150
      description: User's age in years
    created_at:
      type: string
      format: date-time
      description: Account creation timestamp
  required:
    - user_id
    - username
    - email
    - created_at

governance_rules:          # Business: Data governance policies
  data_retention:
    days: 365              # Business: Retention policy
    description: User data should be retained for 365 days
  pii_fields:              # Business: Privacy requirements
    fields:
      - email
      - user_id
    description: Fields containing personally identifiable information
  access_control:
    level: restricted
    description: User data requires restricted access

ownership:                 # Business: Ownership information
  owner: data-team
  team: engineering
  contact: data-team@example.com
  description: Data team owns user data contracts

metadata:                  # Both: Versioning and documentation
  version: "1.0.0"
  description: User data contract for authentication and profile management
  created: "2024-01-01"
  last_updated: "2024-01-15"
```

**Key Points**:
- Contract file is the **single source of truth** for data structure and rules
- Separates business concerns (governance, ownership) from technical concerns (types, constraints)
- Versioned for tracking changes over time
- Human-readable format (YAML or JSON) for collaboration

**Output**: A contract file that combines business requirements with technical specifications

---

## Stage 2: Contract Parsing (Developer)

**Service**: `pycharter.contract_parser`

**Who**: Developer (automated process, typically in CI/CD or setup scripts)

**What Happens**:
- Contract file is parsed and decomposed into structured components
- Separates `schema`, `governance_rules`, `ownership`, and `metadata` into distinct objects
- Returns a `ContractMetadata` object that makes each component accessible independently

**Code Example**:

```python
from pycharter import parse_contract_file, ContractMetadata

# Parse the contract file (YAML or JSON)
metadata = parse_contract_file("data/examples/book/book_contract.yaml")

# Access decomposed components
schema = metadata.schema              # JSON Schema for model generation
governance = metadata.governance_rules # For governance enforcement
ownership = metadata.ownership         # For access control
metadata_info = metadata.metadata      # Version, description, etc.

# Or parse from a dictionary
contract_dict = {
    "schema": {...},
    "governance_rules": {...},
    "ownership": {...},
    "metadata": {...}
}
metadata = parse_contract(contract_dict)
```

**Why This Matters**:
- Separates concerns: schema can be used independently for model generation
- Governance rules can be enforced separately
- Ownership information can be used for access control
- Metadata can be used for versioning and documentation

**Output**: Structured `ContractMetadata` object with separated components

---

## Stage 3: Metadata Storage (Developer)

**Service**: `pycharter.metadata_store`

**Who**: Developer (one-time setup, then automated)

**What Happens**:
- Decomposed metadata components are stored in a relational database
- Schemas are versioned for evolution tracking
- Governance rules and ownership are linked to schemas
- Enables querying, versioning, and retrieval of stored metadata

**Code Example**:

```python
from pycharter import MetadataStoreClient

# Implement for your database (PostgreSQL, MySQL, MongoDB, etc.)
class MyMetadataStore(MetadataStoreClient):
    def connect(self):
        # Connect to your database
        self._connection = psycopg2.connect(self.connection_string)
    
    def store_schema(self, schema_name, schema, version=None):
        # Store schema in database with versioning
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO schemas (name, version, schema_json) VALUES (%s, %s, %s) RETURNING id",
            (schema_name, version, json.dumps(schema))
        )
        return cursor.fetchone()[0]
    
    def get_schema(self, schema_id):
        # Retrieve schema by ID
        cursor = self._connection.cursor()
        cursor.execute("SELECT schema_json FROM schemas WHERE id = %s", (schema_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None

# Store the parsed contract
store = MyMetadataStore(connection_string="postgresql://user:pass@localhost/db")
store.connect()

# Store schema with versioning
schema_id = store.store_schema(
    schema_name="user",
    schema=metadata.schema,
    version=metadata.metadata.get("version", "1.0.0")
)

# Store ownership (for access control and accountability)
store.store_ownership(
    schema_id=schema_id,
    owner=metadata.ownership.get("owner"),
    team=metadata.ownership.get("team"),
    additional_info={"contact": metadata.ownership.get("contact")}
)

# Store governance rules (for policy enforcement)
for rule_name, rule_data in metadata.governance_rules.items():
    store.store_governance_rule(rule_name, rule_data, schema_id)

store.disconnect()
```

**Why This Matters**:
- **Versioning**: Track schema evolution over time
- **Queryability**: Find schemas by name, version, owner, etc.
- **Audit Trail**: Know who owns what and when it changed
- **Centralized Storage**: Single source of truth in database
- **Multi-Application**: Multiple applications can retrieve same schemas

**Output**: All metadata stored in database, versioned and queryable

---

## Stage 4: Model Generation (Developer - On-Demand)

**Service**: `pycharter.pydantic_generator`

**Who**: Developer (in application code, ETL scripts, APIs)

**What Happens**:
- Retrieve schema from metadata store (or use directly from parsed contract)
- Dynamically generate Pydantic model class at runtime
- Model includes all validations, constraints, and types from the schema
- Model is fully functional and can be used like any Pydantic model

**Code Example**:

```python
from pycharter import from_dict, from_file, from_json

# Option 1: Get schema from metadata store
store.connect()
schema = store.get_schema(schema_id)  # Retrieve stored schema
store.disconnect()

# Option 2: Use schema directly from parsed contract
schema = metadata.schema

# Option 3: Load from file
schema = json.load(open("schema.json"))

# Generate Pydantic model dynamically
UserModel = from_dict(schema, "User")

# Now you have a fully-functional Pydantic model!
# It includes all validations: UUID format, email format, minLength, etc.

# Use it like any Pydantic model
user = UserModel(
    user_id="123e4567-e89b-12d3-a456-426614174000",
    username="alice",
    email="alice@example.com",
    age=30,
    created_at="2024-01-15T10:30:00Z"
)

# Validation happens automatically
try:
    invalid_user = UserModel(username="ab", email="not-email", age=-5)
except ValidationError as e:
    print("Validation failed:", e)
```

**Why This Matters**:
- **Dynamic Generation**: No need to write model classes manually
- **Always Up-to-Date**: Models generated from latest schema version
- **Type Safety**: Full Pydantic type checking and validation
- **Runtime Flexibility**: Generate models on-demand when needed
- **Consistency**: All applications use same schema definitions

**Output**: A Pydantic model class ready for validation

---

## Stage 5: Runtime Validation (Developer - In Production)

**Service**: `pycharter.runtime_validator`

**Who**: Developer (in production code: ETL pipelines, APIs, data processing scripts)

**What Happens**:
- Validate incoming data against the generated Pydantic model
- Catch contract violations early before data enters your system
- Return structured validation results with error details
- Support both single record and batch validation

**Code Example**:

```python
from pycharter import validate, validate_batch, ValidationResult

# Single record validation (e.g., API endpoint)
def process_api_request(incoming_data: dict):
    result: ValidationResult = validate(UserModel, incoming_data)
    
    if result.is_valid:
        # Data passes all validations from contract
        validated_user = result.data
        # Continue processing...
        save_to_database(validated_user)
        return {"status": "success", "user_id": validated_user.user_id}
    else:
        # Contract violations detected
        return {
            "status": "error",
            "errors": result.errors,
            "message": "Data does not conform to contract"
        }

# Batch validation (e.g., ETL pipeline processing CSV or database records)
def process_etl_batch(batch_of_records: list[dict]):
    results = validate_batch(UserModel, batch_of_records)
    
    valid_records = [r.data for r in results if r.is_valid]
    invalid_records = [
        {"data": batch_of_records[i], "errors": r.errors}
        for i, r in enumerate(results) if not r.is_valid
    ]
    
    # Process valid records
    save_to_database(valid_records)
    
    # Handle invalid records (log, send to DLQ, etc.)
    if invalid_records:
        log_validation_errors(invalid_records)
        send_to_dead_letter_queue(invalid_records)
    
    return {
        "processed": len(batch_of_records),
        "valid": len(valid_records),
        "invalid": len(invalid_records)
    }

# Strict mode (raises exceptions instead of returning results)
def strict_validation(data: dict):
    try:
        result = validate(UserModel, data, strict=True)
        return result.data
    except ValidationError as e:
        # Handle exception
        raise ValueError(f"Contract violation: {e}")
```

**Why This Matters**:
- **Early Detection**: Catch data quality issues before they propagate
- **Contract Enforcement**: Ensure all data conforms to business and technical rules
- **Error Reporting**: Detailed error messages help identify issues
- **Production Safety**: Prevent bad data from entering your systems
- **Batch Processing**: Efficiently validate large datasets

**Output**: Validated data ready for processing, or error information for invalid data

---

## Complete End-to-End Flow

### Developer Workflow Example

Here's a complete example showing all stages working together:

```python
from pycharter import (
    parse_contract_file,
    MetadataStoreClient,
    from_dict,
    validate,
    ValidationResult
)

# ============================================================
# SETUP PHASE (One-time or when contract changes)
# ============================================================

# Step 1: Parse contract (from business + developer collaboration)
metadata = parse_contract_file("data/examples/book/book_contract.yaml")

# Step 2: Store in database
store = MyMetadataStore(connection_string="postgresql://...")
store.connect()

schema_id = store.store_schema(
    schema_name="user",
    schema=metadata.schema,
    version=metadata.metadata.get("version", "1.0.0")
)

store.store_ownership(
    schema_id=schema_id,
    owner=metadata.ownership.get("owner"),
    team=metadata.ownership.get("team")
)

# Store governance rules
for rule_name, rule_data in metadata.governance_rules.items():
    store.store_governance_rule(rule_name, rule_data, schema_id)

store.disconnect()

# ============================================================
# RUNTIME PHASE (In production code)
# ============================================================

# Step 3: Retrieve schema and generate model (on-demand)
store.connect()
schema = store.get_schema(schema_id)  # Get latest version
UserModel = from_dict(schema, "User")  # Generate model
store.disconnect()

# Step 4: Validate incoming data (in your ETL/API/processing code)
def process_incoming_user_data(raw_data: dict):
    result: ValidationResult = validate(UserModel, raw_data)
    
    if result.is_valid:
        # Data passes all validations from contract
        validated_user = result.data
        # Continue processing...
        return validated_user
    else:
        # Contract violations detected
        raise ValueError(f"Data contract violation: {result.errors}")
```

---

## Key Benefits of This Journey

### 1. Single Source of Truth
- Contract file defines everything: schema, governance, ownership, metadata
- No duplication or drift between definitions
- Changes propagate automatically through the system

### 2. Separation of Concerns
- **Business**: Defines governance rules, ownership, retention policies
- **Developer**: Defines technical constraints, types, formats, validations
- Both collaborate in the same contract file but maintain their domains

### 3. Versioning & Evolution
- Track schema evolution over time in database
- Support multiple versions simultaneously
- Enable gradual migration and rollback

### 4. Runtime Flexibility
- Generate models on-demand from stored schemas
- No need to redeploy code when schemas change
- Applications automatically use latest schema versions

### 5. Type Safety & Validation
- Pydantic models provide full type checking
- All contract validations enforced automatically
- Catch errors early in the pipeline

### 6. Early Error Detection
- Validate data before it enters your systems
- Prevent bad data from propagating
- Detailed error messages help identify issues

### 7. Multi-Application Support
- One contract → Stored once → Multiple apps retrieve
- All applications validate against same contract
- Ensures consistency across the organization

---

## Real-World Scenarios

### Scenario 1: New Contract Version

**Flow**:
```
Business updates contract → Developer parses new version → 
Store new version in database → Applications automatically retrieve new version → 
Validation uses updated rules
```

**Code**:
```python
# Parse new contract version
metadata_v2 = parse_contract_file("data/examples/book/book_contract.yaml")

# Store as new version
schema_id_v2 = store.store_schema(
    schema_name="user",
    schema=metadata_v2.schema,
    version="2.0.0"  # New version
)

# Applications can query by version
schema_v1 = store.get_schema_by_name_and_version("user", "1.0.0")
schema_v2 = store.get_schema_by_name_and_version("user", "2.0.0")
```

### Scenario 2: Multiple Applications

**Flow**:
```
One contract → Stored once in database → 
Multiple apps retrieve schema → Each generates its own model → 
All validate against same contract
```

**Code**:
```python
# Application A (ETL Pipeline)
schema = store.get_schema(schema_id)
UserModel = from_dict(schema, "User")
# ... validate ETL data

# Application B (API Service)
schema = store.get_schema(schema_id)  # Same schema
UserModel = from_dict(schema, "User")
# ... validate API requests

# Application C (Data Quality Tool)
schema = store.get_schema(schema_id)  # Same schema
UserModel = from_dict(schema, "User")
# ... validate data quality checks
```

### Scenario 3: Schema Evolution

**Flow**:
```
Old schema v1.0 → New schema v1.1 → Both stored in database → 
Apps can query by version → Gradual migration possible → 
Old apps use v1.0, new apps use v1.1
```

**Code**:
```python
# Store multiple versions
schema_id_v1 = store.store_schema("user", schema_v1, version="1.0.0")
schema_id_v2 = store.store_schema("user", schema_v2, version="1.1.0")

# Legacy application uses old version
legacy_schema = store.get_schema(schema_id_v1)
LegacyUserModel = from_dict(legacy_schema, "User")

# New application uses new version
new_schema = store.get_schema(schema_id_v2)
NewUserModel = from_dict(new_schema, "User")
```

---

## Best Practices

### 1. Contract Design
- Keep contracts versioned and documented
- Separate business concerns from technical concerns
- Use descriptive field names and descriptions
- Include examples in metadata

### 2. Storage Strategy
- Store all contract components (schema, governance, ownership)
- Use proper versioning (semantic versioning recommended)
- Implement proper indexing for fast retrieval
- Consider retention policies for old versions

### 3. Model Generation
- Generate models on-demand rather than at startup
- Cache generated models when appropriate
- Handle schema changes gracefully
- Log model generation for debugging

### 4. Validation Strategy
- Validate early in your pipeline
- Use batch validation for large datasets
- Log validation errors for monitoring
- Send invalid data to dead letter queues
- Provide clear error messages to users

### 5. Monitoring & Observability
- Track validation success/failure rates
- Monitor schema version usage
- Alert on high validation failure rates
- Track contract evolution over time

---

## Summary

The PyCharter data journey provides a complete solution for managing data contracts from specification to runtime validation:

1. **Contract Creation**: Business and developers collaborate to define data contracts
2. **Contract Parsing**: Decompose contracts into structured components
3. **Metadata Storage**: Store components in database with versioning
4. **Model Generation**: Dynamically generate Pydantic models from schemas
5. **Runtime Validation**: Validate data against contracts in production

This journey ensures:
- ✅ Single source of truth (contract files)
- ✅ Separation of concerns (business vs. technical)
- ✅ Versioning and evolution tracking
- ✅ Runtime flexibility and type safety
- ✅ Early error detection and prevention
- ✅ Consistency across multiple applications

By following this journey, you can maintain data quality, enforce contracts, and ensure consistency across your entire data infrastructure.

---

## Separated Workflow: Schema, Metadata, and Rules Stored Separately

The separated workflow is an improved approach where schemas, metadata, and coercion/validation rules are stored and managed separately, enabling better collaboration between business units and developers.

### Overview

The separated workflow addresses the need for:
1. **Business units** to define metadata (ownership, governance, versioning) independently
2. **Developers** to define schemas (as Pydantic models) independently
3. **Both** to collaborate on coercion and validation rules
4. **Runtime** to retrieve and combine all components automatically

### The Separated Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Business Unit Provides Metadata                     │
│ - Ownership information                                      │
│ - Governance rules                                           │
│ - Version information                                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Developer Writes Pydantic Model                    │
│ - Define data types and structure                           │
│ - Convert to JSON Schema                                    │
│ - Store schema separately                                   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Developer + Business Define Rules                  │
│ - Coercion rules (data transformation)                      │
│ - Validation rules (business + technical checks)            │
│ - Store rules separately                                    │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Store All Components Separately                     │
│ - Schema stored in database                                 │
│ - Metadata stored in database                               │
│ - Coercion rules stored in database                         │
│ - Validation rules stored in database                       │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Runtime Validation                                  │
│ - Retrieve schema from store                                │
│ - Retrieve coercion rules from store                        │
│ - Retrieve validation rules from store                      │
│ - Merge all components                                      │
│ - Generate Pydantic model                                   │
│ - Validate data                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step: Separated Workflow

#### Step 1: Business Unit Provides Metadata

```python
business_metadata = {
    "owner": "data-team",
    "team": "engineering",
    "contact": "data-team@example.com",
    "description": "User data contract for authentication",
    "governance_rules": {
        "data_retention": {"days": 365},
        "pii_fields": {"fields": ["email", "user_id"]},
    },
    "version": "1.0.0",
}
```

#### Step 2: Developer Writes Pydantic Model and Converts to JSON Schema

```python
from pydantic import BaseModel, Field
from pycharter import to_dict

# Developer writes Pydantic model
class User(BaseModel):
    user_id: str = Field(..., description="Unique identifier")
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., description="User's email address")
    age: int = Field(..., ge=0, le=150)

# Convert to JSON Schema
schema = to_dict(User)
```

#### Step 3: Developer + Business Define Coercion and Validation Rules

```python
# Coercion rules (data transformation before validation)
coercion_rules = {
    "user_id": "coerce_to_string",
    "age": "coerce_to_integer",
}

# Validation rules (additional checks after validation)
validation_rules = {
    "username": {
        "no_capital_characters": None,  # Business requirement
        "min_length": {"threshold": 3},  # Developer constraint
    },
    "age": {
        "is_positive": {"threshold": 0},  # Business requirement
    },
}
```

#### Step 4: Store All Components Separately

```python
from pycharter import InMemoryMetadataStore

store = InMemoryMetadataStore()
store.connect()

# Store schema (from developer)
schema_id = store.store_schema("user", schema, version="1.0.0")

# Store metadata (from business)
store.store_metadata(schema_id, business_metadata, "schema")

# Store coercion rules (from developer + business)
store.store_coercion_rules(schema_id, coercion_rules, "1.0.0")

# Store validation rules (from developer + business)
store.store_validation_rules(schema_id, validation_rules, "1.0.0")
```

#### Step 5: Runtime Validation

```python
from pycharter import validate_with_store, get_model_from_store

# Option 1: Use convenience function (retrieves all and validates)
result = validate_with_store(
    store=store,
    schema_id=schema_id,
    data=incoming_data,
    strict=False,
)

# Option 2: Get model once and reuse
UserModel = get_model_from_store(store, schema_id, "User")
result = validate(UserModel, incoming_data)
```

### Benefits of Separated Workflow

1. **Clear Separation of Concerns**: Business owns metadata, developer owns schema, both collaborate on rules
2. **Independent Versioning**: Each component can be versioned independently
3. **Independent Updates**: Update components without affecting others
4. **Better Collaboration**: Business and developer can work in parallel
5. **Runtime Flexibility**: Retrieve and combine components on-demand

### API Reference: Separated Workflow

#### Store Components Separately

```python
# Store schema
schema_id = store.store_schema(schema_name, schema, version=None)

# Store metadata
store.store_metadata(resource_id, metadata, resource_type="schema")

# Store coercion rules
store.store_coercion_rules(schema_id, coercion_rules, version=None)

# Store validation rules
store.store_validation_rules(schema_id, validation_rules, version=None)
```

#### Retrieve Components

```python
# Get schema only
schema = store.get_schema(schema_id)

# Get coercion rules only
coercion_rules = store.get_coercion_rules(schema_id, version=None)

# Get validation rules only
validation_rules = store.get_validation_rules(schema_id, version=None)

# Get complete schema (with rules merged automatically)
complete_schema = store.get_complete_schema(schema_id, version=None)
```

#### Runtime Validation Functions

```python
# Validate with store (retrieves all components automatically)
result = validate_with_store(store, schema_id, data, version=None, strict=False)

# Validate batch with store
results = validate_batch_with_store(store, schema_id, data_list, version=None, strict=False)

# Get model from store (for multiple validations)
Model = get_model_from_store(store, schema_id, model_name=None, version=None)
```

### Comparison: Combined vs Separated Workflow

| Aspect | Combined Workflow | Separated Workflow |
|--------|------------------|-------------------|
| **Contract File** | Single file with all components | Components stored separately |
| **Business Input** | Part of contract file | Separate metadata |
| **Developer Input** | Part of contract file | Separate schema |
| **Rules** | Embedded in schema | Stored separately |
| **Versioning** | Single version for all | Independent versions |
| **Updates** | Update entire contract | Update components independently |
| **Collaboration** | Requires coordination | Parallel work possible |
| **Runtime** | Parse contract → generate model | Retrieve → merge → generate model |

### When to Use Separated Workflow

Use the separated workflow when:
- Business and developer teams work independently
- You need independent versioning of components
- Schemas change frequently but metadata is stable (or vice versa)
- You want maximum flexibility in runtime validation
- You're building a large-scale data contract management system

See `examples/06_separated_workflow.py` for a complete working example.

