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


class PostgresMetadataStore(MetadataStoreClient):
    """
    PostgreSQL metadata store implementation.
    
    Stores metadata in PostgreSQL tables:
    - schemas: JSON Schema definitions
    - governance_rules: Governance rules
    - ownership: Ownership information
    - metadata: Additional metadata
    
    Connection string format: postgresql://[user[:password]@][host][:port][/database]
    
    Example:
        >>> store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
        >>> store.connect()
        >>> schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize PostgreSQL metadata store.
        
        Args:
            connection_string: PostgreSQL connection string
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PostgresMetadataStore. "
                "Install with: pip install psycopg2-binary"
            )
        super().__init__(connection_string)
        self._connection = None
    
    def connect(self) -> None:
        """Connect to PostgreSQL and create tables if needed."""
        if not self.connection_string:
            raise ValueError("connection_string is required for PostgreSQL")
        
        self._connection = psycopg2.connect(self.connection_string)
        self._create_tables()
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _create_tables(self) -> None:
        """Create tables if they don't exist."""
        with self._connection.cursor() as cur:
            # Schemas table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schemas (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    version VARCHAR(50),
                    schema_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, version)
                )
            """)
            
            # Governance rules table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS governance_rules (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    rule_definition JSONB NOT NULL,
                    schema_id INTEGER REFERENCES schemas(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ownership table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ownership (
                    resource_id VARCHAR(255) PRIMARY KEY,
                    owner VARCHAR(255) NOT NULL,
                    team VARCHAR(255),
                    additional_info JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Metadata table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id SERIAL PRIMARY KEY,
                    resource_id VARCHAR(255) NOT NULL,
                    resource_type VARCHAR(50) NOT NULL,
                    metadata_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(resource_id, resource_type)
                )
            """)
            
            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_schemas_name ON schemas(name)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_schemas_version ON schemas(version)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_governance_schema_id ON governance_rules(schema_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_metadata_resource ON metadata(resource_id, resource_type)")
            
            self._connection.commit()
    
    def store_schema(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """Store a schema in PostgreSQL."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
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
    
    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a schema by ID."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT schema_data FROM schemas WHERE id = %s", (schema_id,))
            row = cur.fetchone()
            if row:
                # JSONB is already parsed as dict by psycopg2
                schema_data = row["schema_data"]
                if isinstance(schema_data, str):
                    return json.loads(schema_data)
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

