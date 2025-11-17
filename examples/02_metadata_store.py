#!/usr/bin/env python3
"""
Example 2: Metadata Store Client

Demonstrates how to store and retrieve metadata components in a database.
This example shows the base class interface - you'll need to subclass
MetadataStoreClient for your specific database implementation.
"""

from pathlib import Path

from pycharter import MetadataStoreClient, parse_contract_file


class ExampleMetadataStore(MetadataStoreClient):
    """
    Example implementation of MetadataStoreClient.
    
    In production, you would implement actual database operations here.
    This example uses in-memory storage for demonstration.
    """
    
    def __init__(self, connection_string: str = None):
        super().__init__(connection_string)
        # In-memory storage for demonstration
        self._schemas = {}
        self._governance_rules = {}
        self._ownership = {}
        self._metadata = {}
        self._next_id = 1
    
    def connect(self):
        """Establish connection (mock for this example)."""
        print("  ✓ Connected to metadata store")
        self._connection = "connected"
    
    def disconnect(self):
        """Close connection."""
        self._connection = None
        print("  ✓ Disconnected from metadata store")
    
    def store_schema(self, schema_name: str, schema: dict, version: str = None):
        """Store a schema."""
        schema_id = self._next_id
        self._next_id += 1
        key = f"{schema_name}:{version}" if version else schema_name
        self._schemas[schema_id] = {
            "id": schema_id,
            "name": schema_name,
            "version": version,
            "schema": schema,
        }
        print(f"  ✓ Stored schema '{schema_name}' (ID: {schema_id}, Version: {version})")
        return schema_id
    
    def get_schema(self, schema_id: int):
        """Retrieve a schema."""
        if schema_id in self._schemas:
            return self._schemas[schema_id]["schema"]
        return None
    
    def store_ownership(self, schema_id: int, owner: str = None, team: str = None, **kwargs):
        """Store ownership information."""
        self._ownership[schema_id] = {
            "owner": owner,
            "team": team,
            **kwargs,
        }
        print(f"  ✓ Stored ownership for schema {schema_id} (Owner: {owner}, Team: {team})")
    
    def store_governance_rule(self, rule_name: str, rule: dict, schema_id: int = None):
        """Store a governance rule."""
        rule_id = self._next_id
        self._next_id += 1
        self._governance_rules[rule_id] = {
            "id": rule_id,
            "name": rule_name,
            "rule": rule,
            "schema_id": schema_id,
        }
        print(f"  ✓ Stored governance rule '{rule_name}' (ID: {rule_id})")
        return rule_id


def example_store_metadata():
    """Demonstrate storing metadata from a parsed contract."""
    print("=" * 70)
    print("Example 2a: Storing Metadata from Parsed Contract")
    print("=" * 70)
    
    # Parse a contract
    contract_path = Path(__file__).parent.parent / "data" / "contracts" / "user_contract.yaml"
    metadata = parse_contract_file(str(contract_path))
    
    # Create and connect to metadata store
    store = ExampleMetadataStore(connection_string="example://database")
    store.connect()
    
    try:
        # Store schema
        schema_id = store.store_schema(
            schema_name="user",
            schema=metadata.schema,
            version=metadata.metadata.get("version", "1.0.0"),
        )
        
        # Store ownership
        store.store_ownership(
            schema_id=schema_id,
            owner=metadata.ownership.get("owner"),
            team=metadata.ownership.get("team"),
            contact=metadata.ownership.get("contact"),
        )
        
        # Store governance rules
        for rule_name, rule_data in metadata.governance_rules.items():
            store.store_governance_rule(rule_name, rule_data, schema_id)
        
        print(f"\n✓ All metadata components stored for schema ID: {schema_id}")
        
        return store, schema_id
    
    finally:
        store.disconnect()


def example_retrieve_metadata():
    """Demonstrate retrieving stored metadata."""
    print("\n" + "=" * 70)
    print("Example 2b: Retrieving Stored Metadata")
    print("=" * 70)
    
    # Store some metadata first
    store = ExampleMetadataStore()
    store.connect()
    
    try:
        # Store a schema
        schema_id = store.store_schema(
            schema_name="product",
            schema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                },
            },
            version="1.0.0",
        )
        
        # Retrieve the schema
        stored_schema = store.get_schema(schema_id)
        
        if stored_schema:
            print(f"\n✓ Retrieved schema (ID: {schema_id})")
            print(f"  Properties: {list(stored_schema.get('properties', {}).keys())}")
        else:
            print(f"\n✗ Schema not found (ID: {schema_id})")
    
    finally:
        store.disconnect()


def example_custom_implementation():
    """Show how to create a custom implementation."""
    print("\n" + "=" * 70)
    print("Example 2c: Custom Database Implementation")
    print("=" * 70)
    
    print("""
To implement for your database (e.g., PostgreSQL), subclass MetadataStoreClient:

```python
import psycopg2
from pycharter import MetadataStoreClient

class PostgreSQLMetadataStore(MetadataStoreClient):
    def connect(self):
        self._connection = psycopg2.connect(self.connection_string)
    
    def store_schema(self, schema_name: str, schema: dict, version: str = None):
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO schemas (name, version, schema_json) VALUES (%s, %s, %s) RETURNING id",
            (schema_name, version, json.dumps(schema))
        )
        return cursor.fetchone()[0]
    
    def get_schema(self, schema_id: int):
        cursor = self._connection.cursor()
        cursor.execute("SELECT schema_json FROM schemas WHERE id = %s", (schema_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None
```

Then use it:
```python
store = PostgreSQLMetadataStore(connection_string="postgresql://...")
store.connect()
schema_id = store.store_schema("user", schema_dict, version="1.0.0")
```
""")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Metadata Store Service Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    store, schema_id = example_store_metadata()
    example_retrieve_metadata()
    example_custom_implementation()
    
    print("\n" + "=" * 70)
    print("✓ All Metadata Store examples completed!")
    print("=" * 70 + "\n")

