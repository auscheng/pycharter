"""
Metadata Store Client - Database operations for metadata storage.

Manages tables for:
- Schemas (JSON Schema definitions)
- Governance rules
- Ownership information
- Other metadata
"""

from typing import Any, Dict, List, Optional


class MetadataStoreClient:
    """
    Client for storing and retrieving metadata from a relational database.
    
    This is a base implementation that can be extended for specific databases
    (PostgreSQL, MySQL, etc.) or cloud services (AWS RDS).
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize metadata store client.
        
        Args:
            connection_string: Database connection string (format depends on implementation)
        """
        self.connection_string = connection_string
        self._connection = None
    
    def connect(self) -> None:
        """
        Establish database connection.
        
        Subclasses should implement this method.
        """
        raise NotImplementedError("Subclasses must implement connect()")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            # Subclasses should implement proper cleanup
            self._connection = None
    
    def store_schema(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """
        Store a JSON Schema in the database.
        
        Args:
            schema_name: Name/identifier for the schema
            schema: JSON Schema dictionary
            version: Optional version string
            
        Returns:
            Schema ID or identifier
        """
        raise NotImplementedError("Subclasses must implement store_schema()")
    
    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a schema by ID.
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            Schema dictionary or None if not found
        """
        raise NotImplementedError("Subclasses must implement get_schema()")
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """
        List all stored schemas.
        
        Returns:
            List of schema metadata dictionaries
        """
        raise NotImplementedError("Subclasses must implement list_schemas()")
    
    def store_governance_rule(
        self,
        rule_name: str,
        rule_definition: Dict[str, Any],
        schema_id: Optional[str] = None,
    ) -> str:
        """
        Store a governance rule.
        
        Args:
            rule_name: Name of the governance rule
            rule_definition: Rule definition dictionary
            schema_id: Optional associated schema ID
            
        Returns:
            Rule ID or identifier
        """
        raise NotImplementedError("Subclasses must implement store_governance_rule()")
    
    def get_governance_rules(
        self, schema_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve governance rules.
        
        Args:
            schema_id: Optional schema ID to filter rules
            
        Returns:
            List of governance rule dictionaries
        """
        raise NotImplementedError("Subclasses must implement get_governance_rules()")
    
    def store_ownership(
        self,
        resource_id: str,
        owner: str,
        team: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store ownership information.
        
        Args:
            resource_id: ID of the resource (schema, table, etc.)
            owner: Owner identifier (email, username, etc.)
            team: Optional team name
            additional_info: Optional additional ownership metadata
            
        Returns:
            Ownership record ID
        """
        raise NotImplementedError("Subclasses must implement store_ownership()")
    
    def get_ownership(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve ownership information for a resource.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            Ownership dictionary or None if not found
        """
        raise NotImplementedError("Subclasses must implement get_ownership()")
    
    def store_metadata(
        self,
        resource_id: str,
        metadata: Dict[str, Any],
        resource_type: str = "schema",
    ) -> str:
        """
        Store additional metadata.
        
        Args:
            resource_id: Resource identifier
            metadata: Metadata dictionary
            resource_type: Type of resource (schema, rule, etc.)
            
        Returns:
            Metadata record ID
        """
        raise NotImplementedError("Subclasses must implement store_metadata()")
    
    def get_metadata(
        self, resource_id: str, resource_type: str = "schema"
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a resource.
        
        Args:
            resource_id: Resource identifier
            resource_type: Type of resource
            
        Returns:
            Metadata dictionary or None if not found
        """
        raise NotImplementedError("Subclasses must implement get_metadata()")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

