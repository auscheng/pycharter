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

import yaml


class ContractMetadata:
    """
    Container for decomposed contract metadata.
    
    Attributes:
        schema: JSON Schema definition
        governance_rules: Governance rules and policies
        ownership: Ownership information (owner, team, etc.)
        metadata: Additional metadata (version, description, etc.)
        versions: Dictionary tracking versions of all components
    """
    
    def __init__(
        self,
        schema: Dict[str, Any],
        governance_rules: Optional[Dict[str, Any]] = None,
        ownership: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        versions: Optional[Dict[str, str]] = None,
    ):
        self.schema = schema
        self.governance_rules = governance_rules or {}
        self.ownership = ownership or {}
        self.metadata = metadata or {}
        self.versions = versions or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        result = {
            "schema": self.schema,
            "governance_rules": self.governance_rules,
            "ownership": self.ownership,
            "metadata": self.metadata,
        }
        # Add versions if any are present
        if self.versions:
            result["versions"] = self.versions
        return result


def parse_contract(contract_data: Dict[str, Any]) -> ContractMetadata:
    """
    Parse a contract dictionary and decompose into metadata components.
    
    Expected contract structure:
    {
        "schema": {...},              # JSON Schema definition (may contain "version")
        "governance_rules": {...},    # Optional governance rules
        "ownership": {...},           # Optional ownership info
        "metadata": {...},            # Optional additional metadata (may contain "version")
        "coercion_rules": {...},      # Optional coercion rules (may contain "version")
        "validation_rules": {...},   # Optional validation rules (may contain "version")
        "versions": {...}             # Optional explicit version tracking
    }
    
    Args:
        contract_data: Contract data as dictionary
        
    Returns:
        ContractMetadata object with decomposed components and version tracking
        
    Example:
        >>> contract = {
        ...     "schema": {"type": "object", "version": "1.0.0", "properties": {"name": {"type": "string"}}},
        ...     "metadata": {"version": "1.0.0"},
        ...     "ownership": {"owner": "team-data", "team": "data-engineering"}
        ... }
        >>> metadata = parse_contract(contract)
        >>> metadata.schema
        {'type': 'object', 'version': '1.0.0', 'properties': {'name': {'type': 'string'}}}
        >>> metadata.versions
        {'schema': '1.0.0', 'metadata': '1.0.0'}
    """
    schema = contract_data.get("schema", {})
    governance_rules = contract_data.get("governance_rules", {})
    ownership = contract_data.get("ownership", {})
    metadata = contract_data.get("metadata", {})
    coercion_rules = contract_data.get("coercion_rules", {})
    validation_rules = contract_data.get("validation_rules", {})
    
    # If schema is not at top level, check if entire contract is a schema
    if not schema and ("type" in contract_data or "properties" in contract_data):
        schema = contract_data
        # Extract other components if they exist as separate keys
        governance_rules = contract_data.get("governance_rules", {})
        ownership = contract_data.get("ownership", {})
        coercion_rules = contract_data.get("coercion_rules", {})
        validation_rules = contract_data.get("validation_rules", {})
        metadata = {
            k: v for k, v in contract_data.items()
            if k not in ["schema", "governance_rules", "ownership", "coercion_rules", "validation_rules", "versions"]
        }
    
    # Extract versions from all components
    versions: Dict[str, str] = {}
    
    # Check if explicit versions dict is provided
    if "versions" in contract_data and isinstance(contract_data["versions"], dict):
        versions.update(contract_data["versions"])
    
    # Extract version from schema
    if isinstance(schema, dict) and "version" in schema:
        versions["schema"] = schema["version"]
    
    # Extract version from metadata
    if isinstance(metadata, dict) and "version" in metadata:
        versions["metadata"] = metadata["version"]
    
    # Extract version from coercion_rules
    if isinstance(coercion_rules, dict) and "version" in coercion_rules:
        versions["coercion_rules"] = coercion_rules["version"]
    
    # Extract version from validation_rules
    if isinstance(validation_rules, dict) and "version" in validation_rules:
        versions["validation_rules"] = validation_rules["version"]
    
    return ContractMetadata(
        schema=schema,
        governance_rules=governance_rules,
        ownership=ownership,
        metadata=metadata,
        versions=versions,
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

