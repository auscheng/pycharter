"""
In-Memory Metadata Store Implementation

A simple in-memory implementation useful for testing and development.
"""

import json
from typing import Any, Dict, List, Optional

from pycharter.metadata_store.client import MetadataStoreClient


class InMemoryMetadataStore(MetadataStoreClient):
    """
    In-memory metadata store implementation.
    
    Useful for testing, development, or when persistence is not required.
    All data is stored in memory and will be lost when the instance is destroyed.
    
    Example:
        >>> store = InMemoryMetadataStore()
        >>> store.connect()
        >>> schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
        >>> schema = store.get_schema(schema_id)
    """
    
    def __init__(self):
        """Initialize in-memory store."""
        super().__init__()
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._governance_rules: Dict[str, Dict[str, Any]] = {}
        self._ownership: Dict[str, Dict[str, Any]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
    
    def connect(self) -> None:
        """Connect to in-memory store (no-op for in-memory)."""
        self._connection = "connected"
    
    def disconnect(self) -> None:
        """Disconnect from in-memory store."""
        self._connection = None
    
    def store_schema(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """Store a schema in memory."""
        schema_id = f"schema_{self._next_id}"
        self._next_id += 1
        self._schemas[schema_id] = {
            "id": schema_id,
            "name": schema_name,
            "version": version,
            "schema": schema,
        }
        return schema_id
    
    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a schema by ID."""
        if schema_id in self._schemas:
            return self._schemas[schema_id]["schema"]
        return None
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all stored schemas."""
        return [
            {
                "id": schema_id,
                "name": data["name"],
                "version": data["version"],
            }
            for schema_id, data in self._schemas.items()
        ]
    
    def store_governance_rule(
        self,
        rule_name: str,
        rule_definition: Dict[str, Any],
        schema_id: Optional[str] = None,
    ) -> str:
        """Store a governance rule."""
        rule_id = f"rule_{self._next_id}"
        self._next_id += 1
        self._governance_rules[rule_id] = {
            "id": rule_id,
            "name": rule_name,
            "definition": rule_definition,
            "schema_id": schema_id,
        }
        return rule_id
    
    def get_governance_rules(
        self, schema_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve governance rules."""
        rules = list(self._governance_rules.values())
        if schema_id:
            rules = [r for r in rules if r.get("schema_id") == schema_id]
        return rules
    
    def store_ownership(
        self,
        resource_id: str,
        owner: str,
        team: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store ownership information."""
        self._ownership[resource_id] = {
            "owner": owner,
            "team": team,
            "additional_info": additional_info or {},
        }
        return resource_id
    
    def get_ownership(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve ownership information."""
        return self._ownership.get(resource_id)
    
    def store_metadata(
        self,
        resource_id: str,
        metadata: Dict[str, Any],
        resource_type: str = "schema",
    ) -> str:
        """Store additional metadata."""
        key = f"{resource_type}:{resource_id}"
        self._metadata[key] = {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "metadata": metadata,
        }
        return key
    
    def get_metadata(
        self, resource_id: str, resource_type: str = "schema"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata."""
        key = f"{resource_type}:{resource_id}"
        if key in self._metadata:
            return self._metadata[key]["metadata"]
        return None
    
    def store_coercion_rules(
        self,
        schema_id: str,
        coercion_rules: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """Store coercion rules for a schema."""
        key = f"coercion:{schema_id}"
        if version:
            key = f"{key}:{version}"
        self._metadata[key] = {
            "schema_id": schema_id,
            "version": version,
            "type": "coercion_rules",
            "rules": coercion_rules,
        }
        return key
    
    def get_coercion_rules(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve coercion rules for a schema."""
        # Try versioned first
        if version:
            key = f"coercion:{schema_id}:{version}"
            if key in self._metadata and self._metadata[key].get("type") == "coercion_rules":
                return self._metadata[key]["rules"]
        
        # Try latest (no version)
        key = f"coercion:{schema_id}"
        if key in self._metadata and self._metadata[key].get("type") == "coercion_rules":
            return self._metadata[key]["rules"]
        
        return None
    
    def store_validation_rules(
        self,
        schema_id: str,
        validation_rules: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """Store validation rules for a schema."""
        key = f"validation:{schema_id}"
        if version:
            key = f"{key}:{version}"
        self._metadata[key] = {
            "schema_id": schema_id,
            "version": version,
            "type": "validation_rules",
            "rules": validation_rules,
        }
        return key
    
    def get_validation_rules(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve validation rules for a schema."""
        # Try versioned first
        if version:
            key = f"validation:{schema_id}:{version}"
            if key in self._metadata and self._metadata[key].get("type") == "validation_rules":
                return self._metadata[key]["rules"]
        
        # Try latest (no version)
        key = f"validation:{schema_id}"
        if key in self._metadata and self._metadata[key].get("type") == "validation_rules":
            return self._metadata[key]["rules"]
        
        return None

