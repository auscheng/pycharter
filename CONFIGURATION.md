# PyCharter Configuration and Database Setup

PyCharter follows Airflow's configuration pattern for database credentials, making it easy to manage database connections across different environments. This guide covers database configuration, initialization, and migrations.

## Table of Contents

1. [Database Connection Configuration](#database-connection-configuration)
2. [Database Initialization](#database-initialization)
3. [Database Migrations](#database-migrations)
4. [Troubleshooting](#troubleshooting)

---

## Database Connection Configuration

### Configuration Priority

PyCharter checks for database configuration in this order:

1. **Command-line argument** (highest priority)
   ```bash
   pycharter db init postgresql://user:pass@localhost/pycharter
   ```

2. **Environment variable: `PYCHARTER__DATABASE__SQL_ALCHEMY_CONN`** (Airflow-style)
   ```bash
   export PYCHARTER__DATABASE__SQL_ALCHEMY_CONN=postgresql://user:pass@localhost/pycharter
   ```

3. **Environment variable: `PYCHARTER_DATABASE_URL`** (simpler)
   ```bash
   export PYCHARTER_DATABASE_URL=postgresql://user:pass@localhost/pycharter
   ```

4. **Config file: `pycharter.cfg`** (in project root or `~/.pycharter/`)
   ```ini
   [database]
   sql_alchemy_conn = postgresql://user:pass@localhost/pycharter
   ```

5. **Alembic config: `alembic.ini`** (fallback)
   ```ini
   [alembic]
   sqlalchemy.url = postgresql://user:pass@localhost/pycharter
   ```

### Config File Locations

PyCharter looks for `pycharter.cfg` in:

1. Current working directory
2. `~/.pycharter/pycharter.cfg` (user home directory)
3. Project root (where `alembic.ini` is located)

### Comparison with Airflow

| Feature | Airflow | PyCharter |
|---------|---------|-----------|
| **Env Var (Primary)** | `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` | `PYCHARTER__DATABASE__SQL_ALCHEMY_CONN` |
| **Env Var (Simple)** | N/A | `PYCHARTER_DATABASE_URL` |
| **Config File** | `airflow.cfg` | `pycharter.cfg` |
| **Config Section** | `[database]` | `[database]` |
| **Config Key** | `sql_alchemy_conn` | `sql_alchemy_conn` |

### Best Practices

1. **Development**: Use environment variables
   ```bash
   export PYCHARTER_DATABASE_URL=postgresql://localhost/pycharter_dev
   ```

2. **Production**: Use config file or environment variables (set by deployment system)
   ```ini
   # pycharter.cfg
   [database]
   sql_alchemy_conn = postgresql://user:pass@prod-db:5432/pycharter
   ```

3. **CI/CD**: Use environment variables (set in CI/CD secrets)
   ```yaml
   env:
     PYCHARTER_DATABASE_URL: ${{ secrets.DATABASE_URL }}
   ```

4. **Docker**: Use environment variables or mounted config file
   ```dockerfile
   ENV PYCHARTER_DATABASE_URL=postgresql://user:pass@db:5432/pycharter
   ```

### Security Notes

- Never commit `pycharter.cfg` with credentials to version control
- Use environment variables or secrets management in production
- Consider using `pycharter.cfg.example` as a template (without credentials)

---

## Database Initialization

### Quick Start by Database Type

#### PostgreSQL (Most Common)

PostgreSQL **automatically initializes** the schema when you connect:

```python
from pycharter import PostgresMetadataStore

# Just connect - schema is created automatically!
store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
store.connect()  # Tables created automatically on first connection

# Ready to use
schema_id = store.store_schema("user", {"type": "object", "version": "1.0.0"}, version="1.0.0")
```

#### MongoDB

MongoDB requires **no initialization** - collections are created automatically:

```python
from pycharter import MongoDBMetadataStore

store = MongoDBMetadataStore(
    connection_string="mongodb://user:pass@localhost:27017",
    database_name="pycharter"
)
store.connect()  # Collections and indexes created automatically

# Ready to use
schema_id = store.store_schema("user", {"type": "object", "version": "1.0.0"}, version="1.0.0")
```

#### Redis

Redis requires **no initialization** - keys are created automatically:

```python
from pycharter import RedisMetadataStore

store = RedisMetadataStore(
    connection_string="redis://localhost:6379/0",
    key_prefix="pycharter"
)
store.connect()  # Keys created automatically when storing data

# Ready to use
schema_id = store.store_schema("user", {"type": "object", "version": "1.0.0"}, version="1.0.0")
```

#### In-Memory

In-memory store requires **no initialization**:

```python
from pycharter import InMemoryMetadataStore

store = InMemoryMetadataStore()
store.connect()  # No database needed

# Ready to use
schema_id = store.store_schema("user", {"type": "object", "version": "1.0.0"}, version="1.0.0")
```

### PostgreSQL Initialization (Detailed)

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

# Ready to use!
schema_id = store.store_schema("user", {"type": "object", "version": "1.0.0"}, version="1.0.0")
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

#### Method 3: Using CLI

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

#### Connection String Formats

**PostgreSQL**:
```
postgresql://[user[:password]@][host][:port][/database]
```
Examples:
- `postgresql://postgres:password@localhost:5432/pycharter`
- `postgresql://user@localhost/pycharter` (no password)
- `postgresql://user:pass@host.example.com:5432/pycharter` (remote)

**MongoDB**:
```
mongodb://[username:password@]host[:port][/database]
```
Examples:
- `mongodb://localhost:27017`
- `mongodb://user:password@localhost:27017`
- `mongodb://user:password@host1:27017,host2:27017/pycharter` (replica set)

**Redis**:
```
redis://[password@]host[:port][/database]
```
Examples:
- `redis://localhost:6379`
- `redis://localhost:6379/0` (database 0)
- `redis://:password@localhost:6379` (with password)

### Docker Setup

#### PostgreSQL

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

#### MongoDB

```bash
docker run -d \
  --name pycharter-mongo \
  -e MONGO_INITDB_ROOT_USERNAME=rootUser \
  -e MONGO_INITDB_ROOT_PASSWORD=rootPassword \
  -p 27017:27017 \
  mongodb/mongodb-community-server:latest
```

Connection: `mongodb://rootUser:rootPassword@localhost:27017`

#### Redis

```bash
docker run -d \
  --name pycharter-redis \
  -p 6379:6379 \
  redis:latest
```

Connection: `redis://localhost:6379/0`

### CLI Initialization

If you're using PostgreSQL with the CLI, you can initialize the database:

```bash
# If you configured via environment variable or config file:
pycharter db init

# Or pass the connection string directly:
pycharter db init postgresql://user:password@localhost:5432/pycharter
```

This will:
1. ✅ Create all database tables (schemas, coercion_rules, validation_rules, etc.)
2. ✅ Create all indexes
3. ✅ Set up Alembic version tracking
4. ✅ Stamp the database with the current revision

### Verify Initialization

Check that everything worked:

```bash
# Check current database revision
pycharter db current

# View migration history
pycharter db history
```

You should see output like:
```
Current database revision: ac3d8fcc3e60
```

---

## Database Migrations

When you need to change the database structure (add columns, tables, indexes, etc.), you'll create and apply migrations using Alembic.

### Workflow Overview

1. **Modify SQLAlchemy models** in `pycharter/db/models/`
2. **Generate migration** using Alembic
3. **Review migration file** (auto-generated, may need manual edits)
4. **Test migration** on development database
5. **Apply migration** to production

### Step-by-Step: Creating a Migration

#### Example: Adding a New Column

Let's say you want to add a `description` field to the `schemas` table.

**Step 1: Modify the SQLAlchemy Model**

Edit `pycharter/db/models/schema.py`:

```python
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base

class SchemaModel(Base):
    __tablename__ = "schemas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=True)
    schema_data = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)  # ← NEW COLUMN
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ... rest of the model
```

**Step 2: Generate Migration**

Make sure your database URL is configured, then run:

```bash
# Set database URL (if not already configured)
export PYCHARTER_DATABASE_URL=postgresql://user:password@localhost:5432/pycharter

# Generate migration
alembic revision --autogenerate -m "Add description to schemas table"
```

This creates a new migration file in `pycharter/db/migrations/versions/` like:
```
abc123def456_add_description_to_schemas_table.py
```

**Step 3: Review the Generated Migration**

Open the generated migration file and review it:

```python
"""Add description to schemas table

Revision ID: abc123def456
Revises: ac3d8fcc3e60
Create Date: 2025-11-19 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'ac3d8fcc3e60'  # Points to previous migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add column
    op.add_column('schemas', sa.Column('description', sa.Text(), nullable=True))

def downgrade() -> None:
    # Remove column (for rollback)
    op.drop_column('schemas', 'description')
```

**Important**: Review the migration carefully:
- ✅ Check that `upgrade()` does what you expect
- ✅ Check that `downgrade()` can reverse the changes
- ✅ Verify column types, constraints, and defaults
- ✅ Remove any unwanted changes (Alembic sometimes detects unrelated changes)

**Step 4: Test the Migration**

Test on a development database first:

```bash
# Apply the migration
pycharter db upgrade

# Verify the change
pycharter db current  # Should show new revision

# Test rollback (optional)
pycharter db downgrade --revision -1
pycharter db upgrade  # Re-apply
```

**Step 5: Apply to Production**

Once tested, apply to production:

```bash
# Backup database first!
pg_dump -h localhost -U user pycharter > backup.sql

# Apply migration
pycharter db upgrade
```

### Common Migration Scenarios

#### Adding a New Table

**1. Create Model** (`pycharter/db/models/new_table.py`):
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pycharter.db.models.base import Base

class NewTableModel(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**2. Import in `pycharter/db/models/__init__.py`**:
```python
from pycharter.db.models.new_table import NewTableModel
```

**3. Generate migration**:
```bash
alembic revision --autogenerate -m "Add new_table"
```

#### Adding a Column

**1. Modify model** (add column to existing model)

**2. Generate migration**:
```bash
alembic revision --autogenerate -m "Add column_name to table_name"
```

#### Adding an Index

**1. Modify model** (add index):
```python
from sqlalchemy import Index

class SchemaModel(Base):
    # ... columns ...
    
    __table_args__ = (
        Index('idx_schemas_name_version', 'name', 'version'),
    )
```

**2. Generate migration**:
```bash
alembic revision --autogenerate -m "Add index to schemas"
```

#### Modifying a Column Type

**1. Modify model** (change column type)

**2. Generate migration** and **manually edit** if needed:
```python
def upgrade() -> None:
    # Alembic may generate this, but you might need to adjust
    op.alter_column('table_name', 'column_name',
                    type_=sa.String(500),  # New type
                    existing_type=sa.String(255))  # Old type
```

### Migration Commands Reference

#### View Current Revision
```bash
pycharter db current
```

#### View Migration History
```bash
pycharter db history
```

#### Upgrade to Latest
```bash
pycharter db upgrade
```

#### Upgrade to Specific Revision
```bash
pycharter db upgrade --revision abc123def456
```

#### Downgrade One Step
```bash
pycharter db downgrade --revision -1
```

#### Downgrade to Specific Revision
```bash
pycharter db downgrade --revision ac3d8fcc3e60
```

#### Generate Migration (Manual)
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Description"

# Create empty migration (for manual SQL)
alembic revision -m "Description"
```

### Migration Best Practices

#### 1. Always Test First
- Test migrations on a development database
- Verify both `upgrade()` and `downgrade()` work
- Test with real data if possible

#### 2. Review Auto-Generated Migrations
- Alembic's autogenerate is helpful but not perfect
- Always review and edit migration files
- Remove unwanted changes
- Add data migrations if needed

#### 3. Use Descriptive Messages
```bash
# Good
alembic revision --autogenerate -m "Add description column to schemas table"

# Bad
alembic revision --autogenerate -m "update"
```

#### 4. Version Control
- Commit migration files to version control
- Never edit existing migrations that have been applied
- Create new migrations for additional changes

#### 5. Backup Before Production
```bash
# Always backup before applying migrations
pg_dump -h localhost -U user pycharter > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 6. Data Migrations
If you need to migrate data (not just schema), add it to the migration:

```python
def upgrade() -> None:
    # Schema change
    op.add_column('schemas', sa.Column('description', sa.Text(), nullable=True))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE schemas SET description = 'Default description' WHERE description IS NULL")
    )
```

### Complete Migration Workflow Example

```bash
# 1. Configure database
export PYCHARTER_DATABASE_URL=postgresql://user:pass@localhost:5432/pycharter

# 2. Initialize (first time only)
pycharter db init

# 3. Make changes to models
# Edit pycharter/db/models/schema.py

# 4. Generate migration
alembic revision --autogenerate -m "Add description to schemas"

# 5. Review migration file
# Edit pycharter/db/migrations/versions/xxx_add_description_to_schemas.py

# 6. Test migration
pycharter db upgrade
pycharter db current  # Verify

# 7. Apply to production (after testing)
pycharter db upgrade
```

---

## Troubleshooting

### Configuration Issues

**Problem**: Can't connect to database

**Solutions**:
- Check connection string format
- Verify database is running
- Check credentials
- Verify network connectivity

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

### Migration Fails

**Problem**: Migration fails with error

**Solution**:
```bash
# Check current state
pycharter db current

# View migration history
pycharter db history

# Try to fix manually or rollback
pycharter db downgrade --revision -1
```

### Tables Already Exist

**Problem**: `pycharter db init` says tables already exist

**Solution**: Use `--force` flag or stamp the database:
```bash
pycharter db init --force
# OR
alembic stamp head
```

### Migration Out of Sync

**Problem**: Database state doesn't match migrations

**Solution**: Stamp database to current state:
```bash
# Check what revision database thinks it's at
pycharter db current

# Stamp to correct revision
alembic stamp head  # or specific revision
```

### Need to Edit Migration

**Problem**: Need to modify a migration before applying

**Solution**: Edit the migration file before running `pycharter db upgrade`. Never edit migrations that have already been applied to production.

---

## Summary

- **Configuration**: Use environment variables or config files (see [Database Connection Configuration](#database-connection-configuration))
- **Initialization**: Most stores auto-initialize on connect; PostgreSQL can use CLI: `pycharter db init`
- **Create Migration**: Modify models → `alembic revision --autogenerate -m "message"`
- **Apply Migration**: `pycharter db upgrade`
- **Rollback**: `pycharter db downgrade --revision -1`
- **Check Status**: `pycharter db current`

For more details, see:
- `pycharter/db/README.md` - Database management overview
- `DATA_JOURNEY.md` - Complete workflow guide
- Alembic documentation: https://alembic.sqlalchemy.org/

## Configuration Priority

PyCharter checks for database configuration in this order:

1. **Command-line argument** (highest priority)
   ```bash
   pycharter db init postgresql://user:pass@localhost/pycharter
   ```

2. **Environment variable: `PYCHARTER__DATABASE__SQL_ALCHEMY_CONN`** (Airflow-style)
   ```bash
   export PYCHARTER__DATABASE__SQL_ALCHEMY_CONN=postgresql://user:pass@localhost/pycharter
   ```

3. **Environment variable: `PYCHARTER_DATABASE_URL`** (simpler)
   ```bash
   export PYCHARTER_DATABASE_URL=postgresql://user:pass@localhost/pycharter
   ```

4. **Config file: `pycharter.cfg`** (in project root or `~/.pycharter/`)
   ```ini
   [database]
   sql_alchemy_conn = postgresql://user:pass@localhost/pycharter
   ```

5. **Alembic config: `alembic.ini`** (fallback)
   ```ini
   [alembic]
   sqlalchemy.url = postgresql://user:pass@localhost/pycharter
   ```

## Usage Examples

### CLI Commands

Once configured, you can run commands without passing the database URL:

```bash
# Initialize database
pycharter db init

# Upgrade database
pycharter db upgrade

# Check current revision
pycharter db current

# View migration history
pycharter db history
```

### Python Code

`PostgresMetadataStore` also uses the configuration:

```python
from pycharter import PostgresMetadataStore

# Uses configuration automatically
store = PostgresMetadataStore()
store.connect()

# Or override with explicit connection string
store = PostgresMetadataStore("postgresql://other:db@localhost:5432/other_db")
```

## Config File Locations

PyCharter looks for `pycharter.cfg` in:

1. Current working directory
2. `~/.pycharter/pycharter.cfg` (user home directory)
3. Project root (where `alembic.ini` is located)

## Comparison with Airflow

| Feature | Airflow | PyCharter |
|---------|---------|-----------|
| **Env Var (Primary)** | `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` | `PYCHARTER__DATABASE__SQL_ALCHEMY_CONN` |
| **Env Var (Simple)** | N/A | `PYCHARTER_DATABASE_URL` |
| **Config File** | `airflow.cfg` | `pycharter.cfg` |
| **Config Section** | `[database]` | `[database]` |
| **Config Key** | `sql_alchemy_conn` | `sql_alchemy_conn` |

## Best Practices

1. **Development**: Use environment variables
   ```bash
   export PYCHARTER_DATABASE_URL=postgresql://localhost/pycharter_dev
   ```

2. **Production**: Use config file or environment variables (set by deployment system)
   ```ini
   # pycharter.cfg
   [database]
   sql_alchemy_conn = postgresql://user:pass@prod-db:5432/pycharter
   ```

3. **CI/CD**: Use environment variables (set in CI/CD secrets)
   ```yaml
   env:
     PYCHARTER_DATABASE_URL: ${{ secrets.DATABASE_URL }}
   ```

4. **Docker**: Use environment variables or mounted config file
   ```dockerfile
   ENV PYCHARTER_DATABASE_URL=postgresql://user:pass@db:5432/pycharter
   ```

## Security Notes

- Never commit `pycharter.cfg` with credentials to version control
- Use environment variables or secrets management in production
- Consider using `pycharter.cfg.example` as a template (without credentials)

