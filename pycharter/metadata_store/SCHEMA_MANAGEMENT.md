# Database Schema Management

PyCharter provides robust database schema management following best practices from tools like Airflow and Dagster.

## Overview

When using `PostgresMetadataStore`, PyCharter ensures your database has the correct schema before storing data. This follows the same pattern as Airflow (`airflow db init`) and Dagster's schema initialization.

## How It Works

### Automatic Schema Initialization

By default, `PostgresMetadataStore.connect()` automatically:
1. **Validates** the database schema
2. **Initializes** the schema if it doesn't exist
3. **Verifies** all required tables are present
4. **Tracks** schema version in `pycharter_schema_version` table

```python
from pycharter import PostgresMetadataStore

store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
store.connect()  # Automatically initializes schema if needed
```

### Schema Versioning

PyCharter tracks schema versions in the `pycharter_schema_version` table:
- **Version**: Current schema version (e.g., "1.0.0")
- **Applied at**: When the schema was initialized/updated
- **Description**: Migration description

### Schema Validation

Before operations, PyCharter validates:
- ✅ Schema version table exists
- ✅ All required tables exist
- ✅ Schema version matches expected version
- ✅ All indexes are present

## Usage Patterns

### Pattern 1: Automatic Initialization (Recommended)

```python
from pycharter import PostgresMetadataStore

# Schema is automatically initialized on connect()
store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
store.connect()  # auto_initialize=True by default

# Check schema status
info = store.get_schema_info()
print(f"Schema valid: {info['valid']}")
print(f"Version: {info['version']}")
```

### Pattern 2: Manual Initialization (Production)

For production environments, you may want to initialize the schema separately:

```python
from pycharter import PostgresMetadataStore, initialize_schema
import psycopg2

# Initialize schema manually (e.g., in deployment script)
conn = psycopg2.connect("postgresql://user:pass@localhost/pycharter")
initialize_schema(conn)
conn.close()

# Then connect with validation only
store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
store.connect(auto_initialize=False, validate_schema_on_connect=True)
```

### Pattern 3: Schema Validation Only

```python
from pycharter import validate_schema
import psycopg2

conn = psycopg2.connect("postgresql://user:pass@localhost/pycharter")
result = validate_schema(conn)

if result["valid"]:
    print("✓ Schema is valid")
else:
    print(f"✗ Schema validation failed: {result['message']}")
```

## CLI Tools

PyCharter provides CLI tools for schema management (using Alembic):

### Initialize Schema

```bash
pycharter db init postgresql://user:pass@localhost/pycharter
```

### Upgrade Schema

```bash
pycharter db upgrade postgresql://user:pass@localhost/pycharter
```

### Check Current Revision

```bash
pycharter db current postgresql://user:pass@localhost/pycharter
```

### View Migration History

```bash
pycharter db history
```

For more details, see [pycharter/db/README.md](../db/README.md).

## Database Schema

The pycharter schema includes:

### Core Tables
- `pycharter_schema_version` - Schema version tracking
- `schemas` - JSON Schema definitions
- `coercion_rules` - Coercion rules
- `validation_rules` - Validation rules
- `metadata` - Additional metadata
- `ownership` - Ownership information
- `governance_rules` - Governance rules

### Indexes
- Indexes on `schemas.name` and `schemas.version`
- Indexes on foreign keys for performance
- Composite indexes for common queries

## Best Practices

### 1. Production Deployment

**Recommended approach** (like Airflow/Dagster):

```bash
# Step 1: Initialize schema in deployment script
pycharter db init $DATABASE_URL

# Step 2: Upgrade to latest version
pycharter db upgrade $DATABASE_URL

# Step 3: Application connects with validation
store = PostgresMetadataStore(DATABASE_URL)
store.connect(auto_initialize=False, validate_schema_on_connect=True)
```

### 2. Development/Testing

**Automatic initialization** is fine:

```python
store = PostgresMetadataStore("postgresql://localhost/pycharter")
store.connect()  # Auto-initializes if needed
```

### 3. CI/CD Pipelines

```yaml
# Example GitHub Actions workflow
- name: Initialize Database Schema
  run: |
    pycharter db init ${{ secrets.DATABASE_URL }}
  
- name: Upgrade Database Schema
  run: |
    pycharter db upgrade ${{ secrets.DATABASE_URL }}
```

### 4. Docker/Kubernetes

```dockerfile
# In Dockerfile or init container
RUN pycharter db init $DATABASE_URL
```

## Comparison with Airflow/Dagster

| Feature | Airflow | Dagster | PyCharter |
|---------|---------|---------|-----------|
| **Schema Versioning** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Auto-initialization** | `airflow db init` | Manual | ✅ Auto (optional) |
| **Schema Validation** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Migration System** | Alembic | Custom | ✅ Alembic |
| **CLI Tools** | `airflow db` | Custom | ✅ `pycharter db` |

## Migration Strategy

### Current Approach (v1.0.0)

- **Idempotent**: Can run multiple times safely
- **Versioned**: Tracks schema version in database
- **Validated**: Checks schema before operations

### Future Migrations

When schema changes are needed:
1. Update `SCHEMA_VERSION` in `migrations.py`
2. Add migration logic to handle schema updates
3. Update `initialize_schema()` to apply new changes
4. Test migration on development database

## Troubleshooting

### Schema Not Initialized

```bash
# Error: "Schema not initialized"
# Solution: Initialize schema using CLI
pycharter db init postgresql://user:pass@localhost/pycharter
```

### Version Mismatch

```bash
# Error: "Schema version mismatch"
# Solution: Check current version and upgrade
pycharter db current postgresql://user:pass@localhost/pycharter
pycharter db upgrade postgresql://user:pass@localhost/pycharter
```

### Missing Tables

```bash
# Error: "Missing tables"
# Solution: Re-initialize or upgrade schema
pycharter db init postgresql://user:pass@localhost/pycharter --force
# Or upgrade if already initialized
pycharter db upgrade postgresql://user:pass@localhost/pycharter
```

## Summary

PyCharter's schema management ensures:
- ✅ **Guaranteed schema**: Database always has correct schema before use
- ✅ **Version tracking**: Know which schema version is deployed
- ✅ **Validation**: Catch schema issues early
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **Production-ready**: Follows industry best practices (Airflow/Dagster pattern)

