"""
PostgreSQL Metadata Store Implementation

Stores metadata in PostgreSQL tables within a dedicated schema.
"""

import json
from typing import Any, Dict, List, Optional

import psycopg2
from alembic.runtime.migration import MigrationContext
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine

from pycharter.metadata_store.client import MetadataStoreClient

try:
    from pycharter.config import get_database_url
except ImportError:
    get_database_url = None


class PostgresMetadataStore(MetadataStoreClient):
    """
    PostgreSQL metadata store implementation.
    
    Stores metadata in PostgreSQL tables within the specified schema (default: "pycharter"):
    - schemas: JSON Schema definitions
    - governance_rules: Governance rules
    - ownership: Ownership information
    - metadata: Additional metadata
    - coercion_rules: Coercion rules for data transformation
    - validation_rules: Validation rules for data validation
    
    Connection string format: postgresql://[user[:password]@][host][:port][/database]
    
    The schema namespace is automatically created if it doesn't exist when connecting.
    However, tables must be initialized separately using 'pycharter db init' (similar to 
    'airflow db init'). All tables are created in the specified schema (not in the public schema).
    
    Example:
        >>> # First, initialize the database schema
        >>> # Run: pycharter db init postgresql://user:pass@localhost/pycharter
        >>> 
        >>> # Then connect
        >>> store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
        >>> store.connect()  # Only connects and validates schema
        >>> schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
        >>> store.store_coercion_rules(schema_id, {"age": "coerce_to_integer"}, version="1.0")
        >>> store.store_validation_rules(schema_id, {"age": {"is_positive": {}}}, version="1.0")
        
    To use a different schema name:
        >>> store = PostgresMetadataStore(
        ...     "postgresql://user:pass@localhost/pycharter",
        ...     schema_name="my_custom_schema"
        ... )
    """
    
    def __init__(self, connection_string: Optional[str] = None, schema_name: str = "pycharter"):
        """
        Initialize PostgreSQL metadata store.
        
        Args:
            connection_string: Optional PostgreSQL connection string.
                              If not provided, will use configuration from:
                              - PYCHARTER__DATABASE__SQL_ALCHEMY_CONN env var
                              - PYCHARTER_DATABASE_URL env var
                              - pycharter.cfg config file
                              - alembic.ini config file
            schema_name: PostgreSQL schema name to use (default: "pycharter")
        """
        # Try to get connection string from config if not provided
        if not connection_string and get_database_url:
            connection_string = get_database_url()
        
        if not connection_string:
            raise ValueError(
                "connection_string is required. Provide it directly, or configure it via:\n"
                "  - Environment variable: PYCHARTER__DATABASE__SQL_ALCHEMY_CONN or PYCHARTER_DATABASE_URL\n"
                "  - Config file: pycharter.cfg [database] sql_alchemy_conn\n"
                "  - Config file: alembic.ini sqlalchemy.url"
            )
        
        super().__init__(connection_string)
        self.schema_name = schema_name
        self._connection = None
    
    def connect(self, validate_schema_on_connect: bool = True) -> None:
        """
        Connect to PostgreSQL and validate schema.
        
        Args:
            validate_schema_on_connect: If True, validate that tables exist after connection
            
        Raises:
            ValueError: If connection_string is missing
            RuntimeError: If schema validation fails (tables don't exist)
            
        Note:
            This method only connects and validates. To initialize the database schema,
            run 'pycharter db init' first (similar to 'airflow db init').
        """
        if not self.connection_string:
            raise ValueError("connection_string is required for PostgreSQL")
        
        self._connection = psycopg2.connect(self.connection_string)
        self._ensure_schema_exists()
        self._set_search_path()
        
        if validate_schema_on_connect and not self._is_schema_initialized():
            raise RuntimeError(
                "Database schema is not initialized. "
                "Please run 'pycharter db init' to initialize the schema first.\n"
                f"Example: pycharter db init {self.connection_string}"
            )
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    # Connection management helpers
    
    def _ensure_schema_exists(self) -> None:
        """Create the PostgreSQL schema namespace if it doesn't exist."""
        if not self._connection:
            return
        
        with self._connection.cursor() as cur:
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema_name}"')
            self._connection.commit()
    
    def _set_search_path(self) -> None:
        """Set search_path to use the schema."""
        with self._connection.cursor() as cur:
            cur.execute(f'SET search_path TO "{self.schema_name}", public')
            self._connection.commit()
    
    def _is_schema_initialized(self) -> bool:
        """Check if the database schema is initialized."""
        if not self._connection:
            return False
        
        try:
            with self._connection.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = %s AND table_name = 'schemas'
                    )
                """, (self.schema_name,))
                return cur.fetchone()[0]
        except Exception:
            return False
    
    def _require_connection(self) -> None:
        """Raise error if not connected."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
    
    def _parse_jsonb(self, value: Any) -> Dict[str, Any]:
        """Parse JSONB value (psycopg2 may return dict or str)."""
        if isinstance(value, str):
            return json.loads(value)
        return value if value is not None else {}
    
    def _table_name(self, table: str) -> str:
        """Get fully qualified table name."""
        return f'"{self.schema_name}".{table}'
    
    # Schema info
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get information about the current database schema.
        
        Returns:
            Dictionary with schema information:
            {
                "revision": str or None,
                "initialized": bool,
                "message": str
            }
        """
        self._require_connection()
        
        initialized = self._is_schema_initialized()
        revision = None
        
        if initialized:
            try:
                engine = create_engine(self.connection_string)
                with engine.connect() as conn:
                    context = MigrationContext.configure(conn)
                    revision = context.get_current_revision()
            except Exception:
                pass
        
        return {
            "revision": revision,
            "initialized": initialized,
            "message": f"Schema initialized: {initialized}" + (f" (revision: {revision})" if revision else "")
        }
    
    # Schema operations
    
    def store_schema(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        version: str,
    ) -> str:
        """
        Store a schema in PostgreSQL.
        
        Args:
            schema_name: Name/identifier for the schema
            schema: JSON Schema dictionary
            version: Required version string (must match schema["version"] if present)
            
        Returns:
            Schema ID as string
            
        Raises:
            ValueError: If version is missing or doesn't match schema version
        """
        self._require_connection()
        
        # Ensure schema has version
        if "version" not in schema:
            schema = dict(schema)
            schema["version"] = version
        elif schema.get("version") != version:
            raise ValueError(
                f"Version mismatch: provided version '{version}' does not match "
                f"schema version '{schema.get('version')}'"
            )
        
        with self._connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self._table_name("schemas")} (name, version, schema_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (name, version) 
                DO UPDATE SET schema_data = EXCLUDED.schema_data
                RETURNING id
            """, (schema_name, version, json.dumps(schema)))
            
            schema_id = cur.fetchone()[0]
            self._connection.commit()
            return str(schema_id)
    
    def get_schema(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a schema by ID and optional version.
        
        Args:
            schema_id: Schema identifier
            version: Optional version string (if None, returns latest version)
            
        Returns:
            Schema dictionary with version included, or None if not found
        """
        self._require_connection()
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute(
                    f'SELECT schema_data, version FROM {self._table_name("schemas")} '
                    'WHERE id = %s AND version = %s',
                    (schema_id, version),
                )
            else:
                cur.execute(
                    f'SELECT schema_data, version FROM {self._table_name("schemas")} '
                    'WHERE id = %s ORDER BY version DESC LIMIT 1',
                    (schema_id,),
                )
            
            row = cur.fetchone()
            if not row:
                return None
            
            schema_data = self._parse_jsonb(row["schema_data"])
            stored_version = row.get("version")
            
            # Ensure schema has version
            if "version" not in schema_data:
                schema_data = dict(schema_data)
                schema_data["version"] = stored_version or "1.0.0"
            
            return schema_data
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all stored schemas."""
        self._require_connection()
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f'SELECT id, name, version FROM {self._table_name("schemas")} '
                'ORDER BY name, version'
            )
            return [
                {
                    "id": str(row["id"]),
                    "name": row.get("name"),
                    "version": row.get("version"),
                }
                for row in cur.fetchall()
            ]
    
    # Governance rules
    
    def store_governance_rule(
        self,
        rule_name: str,
        rule_definition: Dict[str, Any],
        schema_id: Optional[str] = None,
    ) -> str:
        """Store a governance rule."""
        self._require_connection()
        
        with self._connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self._table_name("governance_rules")} (name, rule_definition, schema_id)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (rule_name, json.dumps(rule_definition), schema_id))
            
            rule_id = cur.fetchone()[0]
            self._connection.commit()
            return str(rule_id)
    
    def get_governance_rules(
        self, schema_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve governance rules."""
        self._require_connection()
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if schema_id:
                cur.execute(f"""
                    SELECT id, name, rule_definition, schema_id
                    FROM {self._table_name("governance_rules")}
                    WHERE schema_id = %s
                """, (schema_id,))
            else:
                cur.execute(f"""
                    SELECT id, name, rule_definition, schema_id
                    FROM {self._table_name("governance_rules")}
                """)
            
            return [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "definition": self._parse_jsonb(row["rule_definition"]),
                    "schema_id": str(row["schema_id"]) if row["schema_id"] else None,
                }
                for row in cur.fetchall()
            ]
    
    # Ownership
    
    def store_ownership(
        self,
        resource_id: str,
        owner: str,
        team: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store ownership information."""
        self._require_connection()
        
        with self._connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self._table_name("ownership")} (resource_id, owner, team, additional_info)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (resource_id)
                DO UPDATE SET
                    owner = EXCLUDED.owner,
                    team = EXCLUDED.team,
                    additional_info = EXCLUDED.additional_info,
                    updated_at = CURRENT_TIMESTAMP
            """, (resource_id, owner, team, json.dumps(additional_info or {})))
            
            self._connection.commit()
            return resource_id
    
    def get_ownership(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve ownership information."""
        self._require_connection()
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                SELECT owner, team, additional_info
                FROM {self._table_name("ownership")}
                WHERE resource_id = %s
            """, (resource_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return {
                "owner": row["owner"],
                "team": row.get("team"),
                "additional_info": self._parse_jsonb(row.get("additional_info")),
            }
    
    # Metadata
    
    def store_metadata(
        self,
        resource_id: str,
        metadata: Dict[str, Any],
        resource_type: str = "schema",
    ) -> str:
        """Store additional metadata."""
        self._require_connection()
        
        with self._connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self._table_name("metadata")} (resource_id, resource_type, metadata_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (resource_id, resource_type)
                DO UPDATE SET metadata_data = EXCLUDED.metadata_data
                RETURNING id
            """, (resource_id, resource_type, json.dumps(metadata)))
            
            metadata_id = cur.fetchone()[0]
            self._connection.commit()
            return f"{resource_type}:{resource_id}"
    
    def get_metadata(
        self, resource_id: str, resource_type: str = "schema"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata."""
        self._require_connection()
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                SELECT metadata_data
                FROM {self._table_name("metadata")}
                WHERE resource_id = %s AND resource_type = %s
            """, (resource_id, resource_type))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return self._parse_jsonb(row["metadata_data"])
    
    # Coercion rules
    
    def store_coercion_rules(
        self,
        schema_id: str,
        coercion_rules: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """
        Store coercion rules for a schema.
        
        Args:
            schema_id: Schema identifier
            coercion_rules: Dictionary of coercion rules
            version: Optional version string
            
        Returns:
            Rule ID or identifier
        """
        self._require_connection()
        
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self._table_name("coercion_rules")} (schema_id, version, rules)
                VALUES (%s, %s, %s)
                ON CONFLICT (schema_id, version)
                DO UPDATE SET rules = EXCLUDED.rules
                RETURNING id
            """, (schema_id_int, version, json.dumps(coercion_rules)))
            
            rule_id = cur.fetchone()[0]
            self._connection.commit()
            return f"coercion:{schema_id}" + (f":{version}" if version else "")
    
    def get_coercion_rules(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve coercion rules for a schema.
        
        Args:
            schema_id: Schema identifier
            version: Optional version string (if None, returns latest version)
            
        Returns:
            Dictionary of coercion rules, or None if not found
        """
        self._require_connection()
        
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute(f"""
                    SELECT rules
                    FROM {self._table_name("coercion_rules")}
                    WHERE schema_id = %s AND version = %s
                """, (schema_id_int, version))
            else:
                cur.execute(f"""
                    SELECT rules
                    FROM {self._table_name("coercion_rules")}
                    WHERE schema_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (schema_id_int,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return self._parse_jsonb(row["rules"])
    
    # Validation rules
    
    def store_validation_rules(
        self,
        schema_id: str,
        validation_rules: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """
        Store validation rules for a schema.
        
        Args:
            schema_id: Schema identifier
            validation_rules: Dictionary of validation rules
            version: Optional version string
            
        Returns:
            Rule ID or identifier
        """
        self._require_connection()
        
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self._table_name("validation_rules")} (schema_id, version, rules)
                VALUES (%s, %s, %s)
                ON CONFLICT (schema_id, version)
                DO UPDATE SET rules = EXCLUDED.rules
                RETURNING id
            """, (schema_id_int, version, json.dumps(validation_rules)))
            
            rule_id = cur.fetchone()[0]
            self._connection.commit()
            return f"validation:{schema_id}" + (f":{version}" if version else "")
    
    def get_validation_rules(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve validation rules for a schema.
        
        Args:
            schema_id: Schema identifier
            version: Optional version string (if None, returns latest version)
            
        Returns:
            Dictionary of validation rules, or None if not found
        """
        self._require_connection()
        
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute(f"""
                    SELECT rules
                    FROM {self._table_name("validation_rules")}
                    WHERE schema_id = %s AND version = %s
                """, (schema_id_int, version))
            else:
                cur.execute(f"""
                    SELECT rules
                    FROM {self._table_name("validation_rules")}
                    WHERE schema_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (schema_id_int,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return self._parse_jsonb(row["rules"])
