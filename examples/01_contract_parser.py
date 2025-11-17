#!/usr/bin/env python3
"""
Example 1: Contract Parser Service

Demonstrates how to parse data contract files (YAML or JSON) and decompose them
into structured metadata components: schema, governance_rules, ownership, and metadata.
"""

from pathlib import Path

from pycharter import ContractMetadata, parse_contract, parse_contract_file

# Get data directory
DATA_DIR = Path(__file__).parent.parent / "data"


def example_parse_from_file():
    """Parse a contract from a YAML file."""
    print("=" * 70)
    print("Example 1a: Parsing Contract from YAML File")
    print("=" * 70)
    
    contract_path = DATA_DIR / "examples" / "book_contract.yaml"
    
    # Parse the contract file
    metadata = parse_contract_file(str(contract_path))
    
    print(f"\n✓ Parsed contract from: {contract_path}")
    print(f"\nSchema properties: {list(metadata.schema.get('properties', {}).keys())}")
    print(f"Governance rules: {list(metadata.governance_rules.keys())}")
    print(f"Ownership: {metadata.ownership}")
    print(f"Metadata version: {metadata.metadata.get('version')}")
    
    return metadata


def example_parse_from_dict():
    """Parse a contract from a dictionary."""
    print("\n" + "=" * 70)
    print("Example 1b: Parsing Contract from Dictionary")
    print("=" * 70)
    
    contract_dict = {
        "schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "name": {"type": "string", "minLength": 1},
                "price": {"type": "number", "minimum": 0},
            },
            "required": ["product_id", "name", "price"],
        },
        "governance_rules": {
            "data_retention": {"days": 730},
        },
        "ownership": {
            "owner": "product-team",
            "team": "catalog",
        },
        "metadata": {
            "version": "1.0.0",
            "description": "Product catalog contract",
        },
    }
    
    # Parse the contract dictionary
    metadata = parse_contract(contract_dict)
    
    print(f"\n✓ Parsed contract from dictionary")
    print(f"\nSchema type: {metadata.schema.get('type')}")
    print(f"Required fields: {metadata.schema.get('required', [])}")
    print(f"Owner: {metadata.ownership.get('owner')}")
    print(f"Data retention: {metadata.governance_rules.get('data_retention', {}).get('days')} days")
    
    return metadata


def example_access_components():
    """Demonstrate accessing decomposed components."""
    print("\n" + "=" * 70)
    print("Example 1c: Accessing Decomposed Components")
    print("=" * 70)
    
    contract_path = DATA_DIR / "examples" / "book_contract.yaml"
    metadata = parse_contract_file(str(contract_path))
    
    # Access individual components
    schema = metadata.schema
    governance = metadata.governance_rules
    ownership = metadata.ownership
    metadata_info = metadata.metadata
    
    print("\n✓ Components separated and accessible:")
    print(f"  - Schema has {len(schema.get('properties', {}))} properties")
    print(f"  - Governance has {len(governance)} rules")
    print(f"  - Owner: {ownership.get('owner')}")
    print(f"  - Version: {metadata_info.get('version')}")
    
    # Convert to dictionary if needed
    full_dict = metadata.to_dict()
    print(f"\n✓ Can convert to dictionary: {len(full_dict)} top-level keys")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Contract Parser Service Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    metadata1 = example_parse_from_file()
    metadata2 = example_parse_from_dict()
    example_access_components()
    
    print("\n" + "=" * 70)
    print("✓ All Contract Parser examples completed!")
    print("=" * 70 + "\n")

