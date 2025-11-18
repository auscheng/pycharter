# Metadata Store Implementations

PyCharter provides multiple metadata store implementations to suit different use cases:

## Available Implementations

### 1. InMemoryMetadataStore
**Use case**: Testing, development, prototyping

**Dependencies**: None (built-in)

**Example**:
```python
from pycharter import InMemoryMetadataStore

store = InMemoryMetadataStore()
store.connect()

schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
schema = store.get_schema(schema_id)
```

---

### 2. MongoDBMetadataStore
**Use case**: Document-based storage, flexible schema evolution

**Dependencies**: `pymongo`
```bash
pip install pymongo
```

**Connection string format**: `mongodb://[username:password@]host[:port][/database]`

**Example**:
```python
from pycharter import MongoDBMetadataStore

store = MongoDBMetadataStore(
    connection_string="mongodb://localhost:27017/pycharter",
    database_name="pycharter"
)
store.connect()

schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
schema = store.get_schema(schema_id)
```

---

### 3. PostgresMetadataStore
**Use case**: Relational data, ACID transactions, complex queries

**Dependencies**: `psycopg2-binary`
```bash
pip install psycopg2-binary
```

**Connection string format**: `postgresql://[user[:password]@][host][:port][/database]`

**Example**:
```python
from pycharter import PostgresMetadataStore

store = PostgresMetadataStore(
    connection_string="postgresql://user:password@localhost/pycharter"
)
store.connect()

schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
schema = store.get_schema(schema_id)
```

**Schema Management**: 
- Schema is automatically initialized and validated on `connect()`
- Version tracking ensures schema compatibility
- Use `store.get_schema_info()` to check schema status
- See [SCHEMA_MANAGEMENT.md](SCHEMA_MANAGEMENT.md) for details

**CLI Tools**:
```bash
# Initialize schema manually
pycharter db init postgresql://user:pass@localhost/pycharter

# Upgrade to latest version
pycharter db upgrade postgresql://user:pass@localhost/pycharter

# Check current revision
pycharter db current postgresql://user:pass@localhost/pycharter

# See migration history
pycharter db history
```

---

### 4. RedisMetadataStore
**Use case**: High-performance caching, fast lookups, temporary storage

**Dependencies**: `redis`
```bash
pip install redis
```

**Connection string format**: `redis://[password@]host[:port][/database]`

**Example**:
```python
from pycharter import RedisMetadataStore

store = RedisMetadataStore(
    connection_string="redis://localhost:6379/0",
    key_prefix="pycharter"
)
store.connect()

schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
schema = store.get_schema(schema_id)
```

---

## Common Usage Pattern

All implementations follow the same interface:

```python
from pycharter import InMemoryMetadataStore  # or any other implementation

# Initialize and connect
store = InMemoryMetadataStore()
store.connect()

# Store schema
schema_id = store.store_schema(
    schema_name="user",
    schema={"type": "object", "properties": {"name": {"type": "string"}}},
    version="1.0"
)

# Store ownership
store.store_ownership(
    resource_id=schema_id,
    owner="data-team",
    team="engineering"
)

# Store governance rule
rule_id = store.store_governance_rule(
    rule_name="pii_encryption",
    rule_definition={"type": "encrypt", "fields": ["email"]},
    schema_id=schema_id
)

# Retrieve data
schema = store.get_schema(schema_id)
ownership = store.get_ownership(schema_id)
rules = store.get_governance_rules(schema_id)

# List all schemas
all_schemas = store.list_schemas()

# Disconnect
store.disconnect()
```

## Context Manager Usage

All stores support context manager syntax:

```python
with InMemoryMetadataStore() as store:
    schema_id = store.store_schema("user", {"type": "object"})
    schema = store.get_schema(schema_id)
    # Automatically disconnects on exit
```

## Choosing the Right Store

- **InMemoryMetadataStore**: Testing, development, demos
- **MongoDBMetadataStore**: Flexible document storage, schema evolution
- **PostgresMetadataStore**: Production systems, complex queries, ACID guarantees
- **RedisMetadataStore**: High-performance caching, temporary storage, fast lookups

