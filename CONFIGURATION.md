# PyCharter Configuration

PyCharter follows Airflow's configuration pattern for database credentials, making it easy to manage database connections across different environments.

## Quick Start

### Option 1: Environment Variable (Recommended)

```bash
export PYCHARTER_DATABASE_URL=postgresql://user:password@localhost:5432/pycharter
pycharter db init
pycharter db upgrade
```

### Option 2: Airflow-style Environment Variable

```bash
export PYCHARTER__DATABASE__SQL_ALCHEMY_CONN=postgresql://user:password@localhost:5432/pycharter
pycharter db init
```

### Option 3: Config File

Create `pycharter.cfg`:

```ini
[database]
sql_alchemy_conn = postgresql://user:password@localhost:5432/pycharter
```

Then run:
```bash
pycharter db init
```

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

