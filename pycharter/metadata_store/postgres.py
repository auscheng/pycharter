"""
PostgreSQL Metadata Store Implementation

Stores metadata in PostgreSQL tables.
"""

import json
from typing import Any, Dict, List, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    psycopg2 = None

from pycharter.metadata_store.client import MetadataStoreClient

try:
    from alembic.runtime.migration import MigrationContext
    from sqlalchemy import create_engine, inspect
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False
    MigrationContext = None
    create_engine = None
    inspect = None

try:
    from pycharter.config import get_database_url
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    get_database_url = None


class PostgresMetadataStore(MetadataStoreClient):
    """
    PostgreSQL metadata store implementation.
    
    Stores metadata in PostgreSQL tables:
    - schemas: JSON Schema definitions
    - governance_rules: Governance rules
    - ownership: Ownership information
    - metadata: Additional metadata
    - coercion_rules: Coercion rules for data transformation
    - validation_rules: Validation rules for data validation
    
    Connection string format: postgresql://[user[:password]@][host][:port][/database]
    
    Example:
        >>> store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
        >>> store.connect()
        >>> schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
        >>> store.store_coercion_rules(schema_id, {"age": "coerce_to_integer"}, version="1.0")
        >>> store.store_validation_rules(schema_id, {"age": {"is_positive": {}}}, version="1.0")
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize PostgreSQL metadata store.
        
        Args:
            connection_string: Optional PostgreSQL connection string.
                              If not provided, will use configuration from:
                              - PYCHARTER__DATABASE__SQL_ALCHEMY_CONN env var
                              - PYCHARTER_DATABASE_URL env var
                              - pycharter.cfg config file
                              - alembic.ini config file
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PostgresMetadataStore. "
                "Install with: pip install psycopg2-binary"
            )
        
        # If no connection string provided, try to get from configuration
        if not connection_string and CONFIG_AVAILABLE:
            connection_string = get_database_url()
            if connection_string:
                # Store it for later use
                pass
        
        if not connection_string:
            raise ValueError(
                "connection_string is required. Provide it directly, or configure it via:\n"
                "  - Environment variable: PYCHARTER__DATABASE__SQL_ALCHEMY_CONN or PYCHARTER_DATABASE_URL\n"
                "  - Config file: pycharter.cfg [database] sql_alchemy_conn\n"
                "  - Config file: alembic.ini sqlalchemy.url"
            )
        
        super().__init__(connection_string)
        self._connection = None
    
    def connect(self, auto_initialize: bool = True, validate_schema_on_connect: bool = True) -> None:
        """
        Connect to PostgreSQL and ensure schema is initialized.
        
        Args:
            auto_initialize: If True, automatically initialize schema if missing
            validate_schema_on_connect: If True, validate schema after connection
            
        Raises:
            ValueError: If connection_string is missing
            RuntimeError: If schema validation fails and auto_initialize is False
        """
        if not self.connection_string:
            raise ValueError("connection_string is required for PostgreSQL")
        
        self._connection = psycopg2.connect(self.connection_string)
        
        # Check if schema is initialized using Alembic
        if validate_schema_on_connect:
            if not self._is_schema_initialized():
                if auto_initialize:
                    # Schema not initialized, but we can't auto-initialize here
                    # User should run 'pycharter db init' first
                    raise RuntimeError(
                        "Database schema is not initialized. "
                        "Please run 'pycharter db init' to initialize the schema, "
                        "or set auto_initialize=False and validate_schema_on_connect=False."
                    )
                else:
                    raise RuntimeError(
                        "Database schema is not initialized. "
                        "Please run 'pycharter db init' to initialize the schema."
                    )
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _is_schema_initialized(self) -> bool:
        """
        Check if the database schema is initialized.
        
        Returns:
            True if schema is initialized, False otherwise
        """
        if not self._connection:
            return False
        
        try:
            # Check if required tables exist
            with self._connection.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'schemas'
                    )
                """)
                return cur.fetchone()[0]
        except Exception:
            return False
    
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        initialized = self._is_schema_initialized()
        
        # Try to get Alembic revision if available
        revision = None
        if ALEMBIC_AVAILABLE and initialized:
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
            schema: JSON Schema dictionary (must contain "version" field or it will be added)
            version: Required version string (must match schema["version"] if present)
            
        Returns:
            Schema ID
            
        Raises:
            ValueError: If version is missing or doesn't match schema version
        """
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # Ensure schema has version
        if "version" not in schema:
            schema = dict(schema)  # Make a copy
            schema["version"] = version
        elif schema.get("version") != version:
            raise ValueError(
                f"Version mismatch: provided version '{version}' does not match "
                f"schema version '{schema.get('version')}'"
            )
        
        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO schemas (name, version, schema_data)
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
            
        Raises:
            ValueError: If schema is found but doesn't have a version field
        """
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute(
                    "SELECT schema_data, version FROM schemas WHERE id = %s AND version = %s",
                    (schema_id, version),
                )
            else:
                cur.execute(
                    "SELECT schema_data, version FROM schemas WHERE id = %s ORDER BY version DESC LIMIT 1",
                    (schema_id,),
                )
            row = cur.fetchone()
            if row:
                # JSONB is already parsed as dict by psycopg2
                schema_data = row["schema_data"]
                stored_version = row.get("version")
                
                if isinstance(schema_data, str):
                    schema_data = json.loads(schema_data)
                
                # Ensure schema has version
                if "version" not in schema_data:
                    schema_data = dict(schema_data)  # Make a copy
                    schema_data["version"] = stored_version or "1.0.0"
                
                # Validate schema has version
                if "version" not in schema_data:
                    raise ValueError(f"Schema {schema_id} does not have a version field")
                
                return schema_data
        return None
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all stored schemas."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, version FROM schemas ORDER BY name, version")
            return [
                {
                    "id": str(row["id"]),
                    "name": row.get("name"),
                    "version": row.get("version"),
                }
                for row in cur.fetchall()
            ]
    
    def store_governance_rule(
        self,
        rule_name: str,
        rule_definition: Dict[str, Any],
        schema_id: Optional[str] = None,
    ) -> str:
        """Store a governance rule."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO governance_rules (name, rule_definition, schema_id)
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if schema_id:
                cur.execute("""
                    SELECT id, name, rule_definition, schema_id
                    FROM governance_rules
                    WHERE schema_id = %s
                """, (schema_id,))
            else:
                cur.execute("""
                    SELECT id, name, rule_definition, schema_id
                    FROM governance_rules
                """)
            
            return [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "definition": json.loads(row["rule_definition"]) if isinstance(row["rule_definition"], str) else row["rule_definition"],
                    "schema_id": str(row["schema_id"]) if row["schema_id"] else None,
                }
                for row in cur.fetchall()
            ]
    
    def store_ownership(
        self,
        resource_id: str,
        owner: str,
        team: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store ownership information."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO ownership (resource_id, owner, team, additional_info)
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT owner, team, additional_info
                FROM ownership
                WHERE resource_id = %s
            """, (resource_id,))
            
            row = cur.fetchone()
            if row:
                additional_info = row.get("additional_info")
                if isinstance(additional_info, str):
                    additional_info = json.loads(additional_info)
                elif additional_info is None:
                    additional_info = {}
                return {
                    "owner": row["owner"],
                    "team": row.get("team"),
                    "additional_info": additional_info,
                }
        return None
    
    def store_metadata(
        self,
        resource_id: str,
        metadata: Dict[str, Any],
        resource_type: str = "schema",
    ) -> str:
        """Store additional metadata."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO metadata (resource_id, resource_type, metadata_data)
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT metadata_data
                FROM metadata
                WHERE resource_id = %s AND resource_type = %s
            """, (resource_id, resource_type))
            
            row = cur.fetchone()
            if row:
                metadata_data = row["metadata_data"]
                if isinstance(metadata_data, str):
                    return json.loads(metadata_data)
                return metadata_data
        return None
    
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # Convert schema_id to integer if it's a string
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO coercion_rules (schema_id, version, rules)
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # Convert schema_id to integer if it's a string
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute("""
                    SELECT rules
                    FROM coercion_rules
                    WHERE schema_id = %s AND version = %s
                """, (schema_id_int, version))
            else:
                # Get latest version (most recent by created_at)
                cur.execute("""
                    SELECT rules
                    FROM coercion_rules
                    WHERE schema_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (schema_id_int,))
            
            row = cur.fetchone()
            if row:
                rules = row["rules"]
                if isinstance(rules, str):
                    return json.loads(rules)
                return rules
        return None
    
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # Convert schema_id to integer if it's a string
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO validation_rules (schema_id, version, rules)
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
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # Convert schema_id to integer if it's a string
        schema_id_int = int(schema_id) if isinstance(schema_id, str) else schema_id
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute("""
                    SELECT rules
                    FROM validation_rules
                    WHERE schema_id = %s AND version = %s
                """, (schema_id_int, version))
            else:
                # Get latest version (most recent by created_at)
                cur.execute("""
                    SELECT rules
                    FROM validation_rules
                    WHERE schema_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (schema_id_int,))
            
            row = cur.fetchone()
            if row:
                rules = row["rules"]
                if isinstance(rules, str):
                    return json.loads(rules)
                return rules
        return None

