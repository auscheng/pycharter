# Database Initialization and Migration Guide

This guide explains how to initialize your PyCharter database and perform migrations when you need to change the database structure.

## Part 1: Database Initialization

### Step 1: Configure Database Connection

First, set up your database connection. You have three options:

**Option A: Environment Variable (Recommended)**
```bash
export PYCHARTER_DATABASE_URL=postgresql://user:password@localhost:5432/pycharter
```

**Option B: Config File**
Create `pycharter.cfg` in your project root:
```ini
[database]
sql_alchemy_conn = postgresql://user:password@localhost:5432/pycharter
```

**Option C: Command-line Argument**
You can pass the connection string directly to commands (shown below).

### Step 2: Initialize the Database

Run the initialization command:

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

### Step 3: Verify Initialization

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

## Part 2: Database Migrations

When you need to change the database structure (add columns, tables, indexes, etc.), you'll create and apply migrations.

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

---

## Common Migration Scenarios

### Adding a New Table

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

### Adding a Column

**1. Modify model** (add column to existing model)

**2. Generate migration**:
```bash
alembic revision --autogenerate -m "Add column_name to table_name"
```

### Adding an Index

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

### Modifying a Column Type

**1. Modify model** (change column type)

**2. Generate migration** and **manually edit** if needed:
```python
def upgrade() -> None:
    # Alembic may generate this, but you might need to adjust
    op.alter_column('table_name', 'column_name',
                    type_=sa.String(500),  # New type
                    existing_type=sa.String(255))  # Old type
```

---

## Migration Commands Reference

### View Current Revision
```bash
pycharter db current
```

### View Migration History
```bash
pycharter db history
```

### Upgrade to Latest
```bash
pycharter db upgrade
```

### Upgrade to Specific Revision
```bash
pycharter db upgrade --revision abc123def456
```

### Downgrade One Step
```bash
pycharter db downgrade --revision -1
```

### Downgrade to Specific Revision
```bash
pycharter db downgrade --revision ac3d8fcc3e60
```

### Generate Migration (Manual)
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Description"

# Create empty migration (for manual SQL)
alembic revision -m "Description"
```

---

## Best Practices

### 1. Always Test First
- Test migrations on a development database
- Verify both `upgrade()` and `downgrade()` work
- Test with real data if possible

### 2. Review Auto-Generated Migrations
- Alembic's autogenerate is helpful but not perfect
- Always review and edit migration files
- Remove unwanted changes
- Add data migrations if needed

### 3. Use Descriptive Messages
```bash
# Good
alembic revision --autogenerate -m "Add description column to schemas table"

# Bad
alembic revision --autogenerate -m "update"
```

### 4. Version Control
- Commit migration files to version control
- Never edit existing migrations that have been applied
- Create new migrations for additional changes

### 5. Backup Before Production
```bash
# Always backup before applying migrations
pg_dump -h localhost -U user pycharter > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 6. Data Migrations
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

---

## Troubleshooting

### Migration Fails

**Problem**: Migration fails with error
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

## Complete Example Workflow

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

## Summary

- **Initialization**: `pycharter db init` (one-time setup)
- **Create Migration**: Modify models → `alembic revision --autogenerate -m "message"`
- **Apply Migration**: `pycharter db upgrade`
- **Rollback**: `pycharter db downgrade --revision -1`
- **Check Status**: `pycharter db current`

For more details, see:
- `pycharter/db/README.md` - Database management overview
- `CONFIGURATION.md` - Configuration options
- Alembic documentation: https://alembic.sqlalchemy.org/

