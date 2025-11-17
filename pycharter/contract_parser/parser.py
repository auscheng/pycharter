"""
Contract Parser - Decomposes data contract files into metadata components.

A data contract file contains:
- Schema definitions (JSON Schema)
- Governance rules
- Ownership information
- Other metadata
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ContractMetadata:
    """
    Container for decomposed contract metadata.
    
    Attributes:
        schema: JSON Schema definition
        governance_rules: Governance rules and policies
        ownership: Ownership information (owner, team, etc.)
        metadata: Additional metadata (version, description, etc.)
    """
    
    def __init__(
        self,
        schema: Dict[str, Any],
        governance_rules: Optional[Dict[str, Any]] = None,
        ownership: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.schema = schema
        self.governance_rules = governance_rules or {}
        self.ownership = ownership or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "schema": self.schema,
            "governance_rules": self.governance_rules,
            "ownership": self.ownership,
            "metadata": self.metadata,
        }


def parse_contract(contract_data: Dict[str, Any]) -> ContractMetadata:
    """
    Parse a contract dictionary and decompose into metadata components.
    
    Expected contract structure:
    {
        "schema": {...},              # JSON Schema definition
        "governance_rules": {...},    # Optional governance rules
        "ownership": {...},           # Optional ownership info
        "metadata": {...}             # Optional additional metadata
    }
    
    Args:
        contract_data: Contract data as dictionary
        
    Returns:
        ContractMetadata object with decomposed components
        
    Example:
        >>> contract = {
        ...     "schema": {"type": "object", "properties": {"name": {"type": "string"}}},
        ...     "ownership": {"owner": "team-data", "team": "data-engineering"}
        ... }
        >>> metadata = parse_contract(contract)
        >>> metadata.schema
        {'type': 'object', 'properties': {'name': {'type': 'string'}}}
    """
    schema = contract_data.get("schema", {})
    governance_rules = contract_data.get("governance_rules", {})
    ownership = contract_data.get("ownership", {})
    metadata = contract_data.get("metadata", {})
    
    # If schema is not at top level, check if entire contract is a schema
    if not schema and ("type" in contract_data or "properties" in contract_data):
        schema = contract_data
        # Extract other components if they exist as separate keys
        governance_rules = contract_data.get("governance_rules", {})
        ownership = contract_data.get("ownership", {})
        metadata = {
            k: v for k, v in contract_data.items()
            if k not in ["schema", "governance_rules", "ownership"]
        }
    
    return ContractMetadata(
        schema=schema,
        governance_rules=governance_rules,
        ownership=ownership,
        metadata=metadata,
    )


def parse_contract_file(file_path: str) -> ContractMetadata:
    """
    Load and parse a contract file (YAML or JSON).
    
    Args:
        file_path: Path to contract file
        
    Returns:
        ContractMetadata object with decomposed components
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported or invalid
        
    Example:
        >>> metadata = parse_contract_file("contract.yaml")
        >>> print(metadata.schema)
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Contract file not found: {file_path}")
    
    # Determine file format
    suffix = path.suffix.lower()
    
    if suffix in [".yaml", ".yml"]:
        if not YAML_AVAILABLE:
            raise ValueError(
                "YAML support requires 'pyyaml' package. Install with: pip install pyyaml"
            )
        with open(path, "r", encoding="utf-8") as f:
            contract_data = yaml.safe_load(f)
    elif suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            contract_data = json.load(f)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported formats: .json, .yaml, .yml"
        )
    
    if not isinstance(contract_data, dict):
        raise ValueError(f"Contract file must contain a dictionary/object, got {type(contract_data)}")
    
    return parse_contract(contract_data)

