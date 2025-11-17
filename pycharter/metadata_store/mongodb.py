"""
MongoDB Metadata Store Implementation

Stores metadata in MongoDB collections.
"""

import json
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    MongoClient = None
    Collection = None
    Database = None

from pycharter.metadata_store.client import MetadataStoreClient


class MongoDBMetadataStore(MetadataStoreClient):
    """
    MongoDB metadata store implementation.
    
    Stores metadata in MongoDB collections:
    - schemas: JSON Schema definitions
    - governance_rules: Governance rules
    - ownership: Ownership information
    - metadata: Additional metadata
    
    Connection string format: mongodb://[username:password@]host[:port][/database]
    
    Example:
        >>> store = MongoDBMetadataStore("mongodb://localhost:27017/pycharter")
        >>> store.connect()
        >>> schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
    """
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: str = "pycharter",
    ):
        """
        Initialize MongoDB metadata store.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Database name (default: "pycharter")
        """
        if not MONGO_AVAILABLE:
            raise ImportError(
                "pymongo is required for MongoDBMetadataStore. "
                "Install with: pip install pymongo"
            )
        super().__init__(connection_string)
        self.database_name = database_name
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
    
    def connect(self) -> None:
        """Connect to MongoDB."""
        if not self.connection_string:
            raise ValueError("connection_string is required for MongoDB")
        
        self._client = MongoClient(self.connection_string)
        self._db = self._client[self.database_name]
        self._connection = self._db
        
        # Create indexes for better query performance
        self._db.schemas.create_index("name")
        self._db.schemas.create_index("version")
        self._db.governance_rules.create_index("schema_id")
        self._db.ownership.create_index("resource_id")
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._connection = None
    
    def store_schema(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        version: str,
    ) -> str:
        """
        Store a schema in MongoDB.
        
        Args:
            schema_name: Name/identifier for the schema
            schema: JSON Schema dictionary (must contain "version" field or it will be added)
            version: Required version string (must match schema["version"] if present)
            
        Returns:
            Schema ID
            
        Raises:
            ValueError: If version is missing or doesn't match schema version
        """
        if self._db is None:
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
        
        doc = {
            "name": schema_name,
            "version": version,
            "schema": schema,
        }
        result = self._db.schemas.insert_one(doc)
        return str(result.inserted_id)
    
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
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        from bson import ObjectId
        try:
            doc = self._db.schemas.find_one({"_id": ObjectId(schema_id)})
        except Exception:
            # If ObjectId conversion fails, try as string
            doc = self._db.schemas.find_one({"_id": schema_id})
        
        if doc:
            schema = doc.get("schema")
            stored_version = doc.get("version")
            
            # If version specified, check it matches
            if version and stored_version and stored_version != version:
                return None  # Version mismatch
            
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
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        schemas = []
        for doc in self._db.schemas.find({}, {"name": 1, "version": 1}):
            schemas.append({
                "id": str(doc["_id"]),
                "name": doc.get("name"),
                "version": doc.get("version"),
            })
        return schemas
    
    def store_governance_rule(
        self,
        rule_name: str,
        rule_definition: Dict[str, Any],
        schema_id: Optional[str] = None,
    ) -> str:
        """Store a governance rule."""
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        doc = {
            "name": rule_name,
            "definition": rule_definition,
            "schema_id": schema_id,
        }
        result = self._db.governance_rules.insert_one(doc)
        return str(result.inserted_id)
    
    def get_governance_rules(
        self, schema_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve governance rules."""
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        query = {}
        if schema_id:
            query["schema_id"] = schema_id
        
        rules = []
        for doc in self._db.governance_rules.find(query):
            rules.append({
                "id": str(doc["_id"]),
                "name": doc.get("name"),
                "definition": doc.get("definition"),
                "schema_id": doc.get("schema_id"),
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
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        doc = {
            "resource_id": resource_id,
            "owner": owner,
            "team": team,
            "additional_info": additional_info or {},
        }
        # Use upsert to update if exists
        self._db.ownership.update_one(
            {"resource_id": resource_id},
            {"$set": doc},
            upsert=True
        )
        return resource_id
    
    def get_ownership(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve ownership information."""
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        doc = self._db.ownership.find_one({"resource_id": resource_id})
        if doc:
            return {
                "owner": doc.get("owner"),
                "team": doc.get("team"),
                "additional_info": doc.get("additional_info", {}),
            }
        return None
    
    def store_metadata(
        self,
        resource_id: str,
        metadata: Dict[str, Any],
        resource_type: str = "schema",
    ) -> str:
        """Store additional metadata."""
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        doc = {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "metadata": metadata,
        }
        key = f"{resource_type}:{resource_id}"
        self._db.metadata.update_one(
            {"resource_id": resource_id, "resource_type": resource_type},
            {"$set": doc},
            upsert=True
        )
        return key
    
    def get_metadata(
        self, resource_id: str, resource_type: str = "schema"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata."""
        if self._db is None:
            raise RuntimeError("Not connected. Call connect() first.")
        
        doc = self._db.metadata.find_one({
            "resource_id": resource_id,
            "resource_type": resource_type
        })
        if doc:
            return doc.get("metadata")
        return None

