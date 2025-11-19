# Database Initialization Guide

This guide shows you how to initialize databases for PyCharter metadata stores.

## Quick Start

### PostgreSQL (Most Common)

PostgreSQL **automatically initializes** the schema when you connect:

```python
from pycharter import PostgresMetadataStore

# Just connect - schema is created automatically!
store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
store.connect()  # Tables created automatically on first connection

# Ready to use
schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
```

### MongoDB

MongoDB requires **no initialization** - collections are created automatically:

```python
from pycharter import MongoDBMetadataStore

store = MongoDBMetadataStore(
    connection_string="mongodb://user:pass@localhost:27017",
    database_name="pycharter"
)
store.connect()  # Collections and indexes created automatically

# Ready to use
schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
```

### Redis

Redis requires **no initialization** - keys are created automatically:

```python
from pycharter import RedisMetadataStore

store = RedisMetadataStore(
    connection_string="redis://localhost:6379/0",
    key_prefix="pycharter"
)
store.connect()  # Keys created automatically when storing data

# Ready to use
schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
```

### In-Memory

In-memory store requires **no initialization**:

```python
from pycharter import InMemoryMetadataStore

store = InMemoryMetadataStore()
store.connect()  # No database needed

# Ready to use
schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
```

---

## Detailed Instructions

### PostgreSQL Initialization

PostgreSQL is the most feature-rich option with automatic schema management.

#### Method 1: Automatic Initialization (Recommended for Development)

```python
from pycharter import PostgresMetadataStore

# Create store with connection string
store = PostgresMetadataStore(
    connection_string="postgresql://user:password@localhost:5432/pycharter"
)

# Connect - schema is automatically created if it doesn't exist
store.connect()  # auto_initialize=True by default

# Check schema status
schema_info = store.get_schema_info()
print(f"Schema valid: {schema_info['valid']}")
print(f"Version: {schema_info['version']}")

# Ready to use!
schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
```

#### Method 2: Manual Initialization (Recommended for Production)

For production, you may want to initialize the schema separately:

```python
from pycharter import PostgresMetadataStore

# Step 1: Initialize schema (run once, e.g., in deployment script)
store = PostgresMetadataStore(connection_string="postgresql://...")
store.connect(auto_initialize=True)  # Creates schema
store.disconnect()

# Step 2: Connect with validation only (in application)
store = PostgresMetadataStore(connection_string="postgresql://...")
store.connect(auto_initialize=False, validate_schema_on_connect=True)
```

#### Method 3: Using CLI (If Available)

```bash
# Initialize schema
pycharter db init postgresql://user:pass@localhost/pycharter

# Then in Python, connect with validation only
store = PostgresMetadataStore(connection_string="postgresql://...")
store.connect(auto_initialize=False, validate_schema_on_connect=True)
```

#### What Gets Created

When PostgreSQL initializes, it creates:

- **Tables**:
  - `schemas` - JSON Schema definitions
  - `governance_rules` - Governance rules
  - `ownership` - Ownership information
  - `metadata` - Additional metadata
  - `pycharter_schema_version` - Schema version tracking

- **Indexes**:
  - Indexes on `schemas.name` and `schemas.version`
  - Indexes on foreign keys
  - Composite indexes for common queries

#### Connection String Format

```
postgresql://[user[:password]@][host][:port][/database]
```

Examples:
- `postgresql://postgres:password@localhost:5432/pycharter`
- `postgresql://user@localhost/pycharter` (no password)
- `postgresql://user:pass@host.example.com:5432/pycharter` (remote)

---

### MongoDB Initialization

MongoDB is schema-less - no initialization needed!

```python
from pycharter import MongoDBMetadataStore

store = MongoDBMetadataStore(
    connection_string="mongodb://user:password@localhost:27017",
    database_name="pycharter"
)

# Connect - collections and indexes created automatically
store.connect()

# Collections are created on first use:
# - schemas
# - governance_rules
# - ownership
# - metadata

# Indexes are created automatically:
# - schemas: name, version
# - governance_rules: schema_id
# - ownership: resource_id
```

#### Connection String Format

```
mongodb://[username:password@]host[:port][/database]
```

Examples:
- `mongodb://localhost:27017`
- `mongodb://user:password@localhost:27017`
- `mongodb://user:password@localhost:27017/pycharter`
- `mongodb://user:password@host1:27017,host2:27017/pycharter` (replica set)

---

### Redis Initialization

Redis is key-value storage - no schema needed!

```python
from pycharter import RedisMetadataStore

store = RedisMetadataStore(
    connection_string="redis://localhost:6379/0",
    key_prefix="pycharter"  # Optional, defaults to "pycharter"
)

# Connect - keys created automatically when storing data
store.connect()

# Keys are created on first use with pattern:
# - pycharter:schemas:{schema_id}
# - pycharter:schemas:index (set of all schema IDs)
# - pycharter:governance:{rule_id}
# - pycharter:ownership:{resource_id}
# - pycharter:metadata:{resource_type}:{resource_id}
```

#### Connection String Format

```
redis://[password@]host[:port][/database]
```

Examples:
- `redis://localhost:6379`
- `redis://localhost:6379/0` (database 0)
- `redis://:password@localhost:6379` (with password)
- `redis://user:password@localhost:6379/0`

---

## Docker Setup

### PostgreSQL

```bash
docker run -d \
  --name pycharter-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pycharter \
  -p 5432:5432 \
  postgres:latest
```

Connection: `postgresql://postgres:postgres@localhost:5432/pycharter`

### MongoDB

```bash
docker run -d \
  --name pycharter-mongo \
  -e MONGO_INITDB_ROOT_USERNAME=rootUser \
  -e MONGO_INITDB_ROOT_PASSWORD=rootPassword \
  -p 27017:27017 \
  mongodb/mongodb-community-server:latest
```

Connection: `mongodb://rootUser:rootPassword@localhost:27017`

### Redis

```bash
docker run -d \
  --name pycharter-redis \
  -p 6379:6379 \
  redis:latest
```

Connection: `redis://localhost:6379/0`

---

## Environment Variables

You can configure database connections using environment variables:

```bash
# PostgreSQL
export PYCHARTER_DATABASE_URL=postgresql://user:pass@localhost/pycharter
export PYCHARTER__DATABASE__SQL_ALCHEMY_CONN=postgresql://user:pass@localhost/pycharter

# Then in Python
from pycharter import PostgresMetadataStore

# Connection string read from environment
store = PostgresMetadataStore()  # No connection_string needed
store.connect()
```

---

## Complete Example

Here's a complete example showing initialization and usage:

```python
from pycharter import PostgresMetadataStore, parse_contract_file

# 1. Initialize database
store = PostgresMetadataStore(
    connection_string="postgresql://postgres:postgres@localhost:5432/pycharter"
)
store.connect()  # Schema created automatically

# 2. Parse and store a contract
metadata = parse_contract_file("data/examples/book_contract.yaml")

schema_id = store.store_schema(
    schema_name="book",
    schema=metadata.schema,
    version=metadata.metadata.get("version", "1.0.0")
)

store.store_ownership(
    resource_id=schema_id,
    owner=metadata.ownership.get("owner"),
    team=metadata.ownership.get("team")
)

# 3. Retrieve and use
stored_schema = store.get_schema(schema_id)
print(f"Stored schema: {stored_schema.get('type')}")

# 4. Clean up
store.disconnect()
```

---

## Troubleshooting

### PostgreSQL: "relation does not exist"

**Solution**: Schema wasn't initialized. Run:
```python
store.connect(auto_initialize=True)
```

### PostgreSQL: "permission denied"

**Solution**: User needs CREATE TABLE permission:
```sql
GRANT CREATE ON DATABASE pycharter TO your_user;
```

### MongoDB: "authentication failed"

**Solution**: Check username/password in connection string:
```python
# Correct format
connection_string="mongodb://username:password@localhost:27017"
```

### Redis: "Connection refused"

**Solution**: Make sure Redis is running:
```bash
docker ps | grep redis
# or
redis-cli ping  # Should return PONG
```

---

## Next Steps

- See `examples/08_database_initialization.py` for runnable examples
- See `tests/test_metadata_stores.py` for test examples
- See `pycharter/metadata_store/README.md` for implementation details

