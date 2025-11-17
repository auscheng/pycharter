"""
Redis Metadata Store Implementation

Stores metadata in Redis using JSON serialization.
"""

import json
from typing import Any, Dict, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from pycharter.metadata_store.client import MetadataStoreClient


class RedisMetadataStore(MetadataStoreClient):
    """
    Redis metadata store implementation.
    
    Stores metadata in Redis with the following key patterns:
    - schemas:{schema_id}: JSON Schema definitions
    - schemas:index: Set of all schema IDs
    - governance:{rule_id}: Governance rules
    - governance:index: Set of all rule IDs
    - ownership:{resource_id}: Ownership information
    - metadata:{resource_type}:{resource_id}: Additional metadata
    
    Connection string format: redis://[password@]host[:port][/database]
    
    Example:
        >>> store = RedisMetadataStore("redis://localhost:6379/0")
        >>> store.connect()
        >>> schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
    """
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        key_prefix: str = "pycharter",
    ):
        """
        Initialize Redis metadata store.
        
        Args:
            connection_string: Redis connection string
            key_prefix: Prefix for all keys (default: "pycharter")
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis is required for RedisMetadataStore. "
                "Install with: pip install redis"
            )
        super().__init__(connection_string)
        self.key_prefix = key_prefix
        self._client: Optional[redis.Redis] = None
    
    def connect(self) -> None:
        """Connect to Redis."""
        if not self.connection_string:
            raise ValueError("connection_string is required for Redis")
        
        self._client = redis.from_url(self.connection_string, decode_responses=True)
        # Test connection
        self._client.ping()
        self._connection = self._client
    
    def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._connection = None
    
    def _key(self, *parts: str) -> str:
        """Generate a Redis key with prefix."""
        return f"{self.key_prefix}:{':'.join(parts)}"
    
    def store_schema(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        version: str,
    ) -> str:
        """
        Store a schema in Redis.
        
        Args:
            schema_name: Name/identifier for the schema
            schema: JSON Schema dictionary (must contain "version" field or it will be added)
            version: Required version string (must match schema["version"] if present)
            
        Returns:
            Schema ID
            
        Raises:
            ValueError: If version is missing or doesn't match schema version
        """
        if not self._client:
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
        
        # Generate schema ID
        schema_id = f"{schema_name}:{version}"
        
        # Store schema data
        schema_data = {
            "id": schema_id,
            "name": schema_name,
            "version": version,
            "schema": schema,
        }
        self._client.set(
            self._key("schemas", schema_id),
            json.dumps(schema_data)
        )
        
        # Add to index
        self._client.sadd(self._key("schemas", "index"), schema_id)
        
        return schema_id
    
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
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # If version specified, try to get specific version
        if version:
            # Try versioned key first
            versioned_id = f"{schema_id.split(':')[0]}:{version}" if ":" not in schema_id else f"{schema_id.rsplit(':', 1)[0]}:{version}"
            data = self._client.get(self._key("schemas", versioned_id))
            if data:
                schema_data = json.loads(data)
                schema = schema_data.get("schema")
                if schema and "version" not in schema:
                    schema = dict(schema)
                    schema["version"] = version
                if schema and "version" not in schema:
                    raise ValueError(f"Schema {schema_id} does not have a version field")
                return schema
        
        # Try original schema_id
        data = self._client.get(self._key("schemas", schema_id))
        if data:
            schema_data = json.loads(data)
            schema = schema_data.get("schema")
            stored_version = schema_data.get("version")
            
            # Ensure schema has version
            if schema and "version" not in schema:
                schema = dict(schema)  # Make a copy
                schema["version"] = stored_version or "1.0.0"
            
            # Validate schema has version
            if schema and "version" not in schema:
                raise ValueError(f"Schema {schema_id} does not have a version field")
            
            return schema
        return None
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all stored schemas."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        schema_ids = self._client.smembers(self._key("schemas", "index"))
        schemas = []
        
        for schema_id in schema_ids:
            data = self._client.get(self._key("schemas", schema_id))
            if data:
                schema_data = json.loads(data)
                schemas.append({
                    "id": schema_data.get("id"),
                    "name": schema_data.get("name"),
                    "version": schema_data.get("version"),
                })
        
        return schemas
    
    def store_governance_rule(
        self,
        rule_name: str,
        rule_definition: Dict[str, Any],
        schema_id: Optional[str] = None,
    ) -> str:
        """Store a governance rule."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        rule_id = f"rule:{rule_name}:{schema_id or 'global'}"
        
        rule_data = {
            "id": rule_id,
            "name": rule_name,
            "definition": rule_definition,
            "schema_id": schema_id,
        }
        
        self._client.set(
            self._key("governance", rule_id),
            json.dumps(rule_data)
        )
        
        # Add to index
        self._client.sadd(self._key("governance", "index"), rule_id)
        
        # If associated with schema, add to schema's rule set
        if schema_id:
            self._client.sadd(
                self._key("schemas", schema_id, "rules"),
                rule_id
            )
        
        return rule_id
    
    def get_governance_rules(
        self, schema_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve governance rules."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        if schema_id:
            # Get rules for specific schema
            rule_ids = self._client.smembers(
                self._key("schemas", schema_id, "rules")
            )
        else:
            # Get all rules
            rule_ids = self._client.smembers(self._key("governance", "index"))
        
        rules = []
        for rule_id in rule_ids:
            data = self._client.get(self._key("governance", rule_id))
            if data:
                rule_data = json.loads(data)
                rules.append({
                    "id": rule_data.get("id"),
                    "name": rule_data.get("name"),
                    "definition": rule_data.get("definition"),
                    "schema_id": rule_data.get("schema_id"),
                })
        
        return rules
    
    def store_ownership(
        self,
        resource_id: str,
        owner: str,
        team: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store ownership information."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        ownership_data = {
            "owner": owner,
            "team": team,
            "additional_info": additional_info or {},
        }
        
        self._client.set(
            self._key("ownership", resource_id),
            json.dumps(ownership_data)
        )
        
        return resource_id
    
    def get_ownership(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve ownership information."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        data = self._client.get(self._key("ownership", resource_id))
        if data:
            return json.loads(data)
        return None
    
    def store_metadata(
        self,
        resource_id: str,
        metadata: Dict[str, Any],
        resource_type: str = "schema",
    ) -> str:
        """Store additional metadata."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        key = f"{resource_type}:{resource_id}"
        self._client.set(
            self._key("metadata", key),
            json.dumps(metadata)
        )
        
        # Add to index
        self._client.sadd(
            self._key("metadata", resource_type, "index"),
            resource_id
        )
        
        return key
    
    def get_metadata(
        self, resource_id: str, resource_type: str = "schema"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        key = f"{resource_type}:{resource_id}"
        data = self._client.get(self._key("metadata", key))
        if data:
            return json.loads(data)
        return None

