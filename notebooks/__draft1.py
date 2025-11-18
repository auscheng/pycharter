"""
Complete PyCharter Data Journey for Aircraft Dataset

This script demonstrates the full pycharter workflow:
1. Convert Pydantic model to JSON Schema
2. Create coercion and validation rules
3. Create metadata
4. Store everything in InMemoryMetadataStore
5. Validate data using stored components
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import importlib.util

import pandas as pd
import yaml

from pycharter import (
    # Service 1: Contract Parser
    parse_contract,
    parse_contract_file,
    ContractMetadata,
    # Service 2: Metadata Store
    MetadataStoreClient,
    InMemoryMetadataStore,
    # Service 3: Pydantic Generator
    from_dict,
    from_json,
    from_file,
    from_url,
    generate_model,
    # Service 4: JSON Schema Converter
    to_dict,
    to_json,
    to_file,
    model_to_schema,
    # Service 5: Runtime Validator
    validate,
    validate_batch,
    ValidationResult,
    validate_with_store,
    get_model_from_store,
)

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR.parent / 'data'
EXAMPLES_DIR = DATA_DIR / 'examples'
AIRCRAFT_DIR = EXAMPLES_DIR / 'aircraft'
AIRCRAFT_CONTRACT = AIRCRAFT_DIR / 'aircraft_contract.yaml'
AIRCRAFT_COERCION_RULES = AIRCRAFT_DIR / 'aircraft_coercion_rules.json'
AIRCRAFT_METADATA = AIRCRAFT_DIR / 'aircraft_metadata.json'
AIRCRAFT_SCHEMA = AIRCRAFT_DIR / 'aircraft_schema.json'
AIRCRAFT_VALIDATION_RULES = AIRCRAFT_DIR / 'aircraft_validation_rules.json'

# Import Aircraft model using importlib for robust path handling
aircraft_models_path = AIRCRAFT_DIR / 'aircraft_models.py'
spec = importlib.util.spec_from_file_location("aircraft_models", aircraft_models_path)
aircraft_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aircraft_models)
Aircraft = aircraft_models.Aircraft

df = pd.read_csv(AIRCRAFT_DIR / 'aircraft.csv')


def load_json_or_yaml(file_path: Path) -> Dict[str, Any]:
    """
    Load data from a JSON or YAML file.
    
    Automatically detects format based on file extension.
    
    Args:
        file_path: Path to JSON or YAML file
        
    Returns:
        Dictionary containing the loaded data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If format is unsupported or YAML is not available
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    suffix = file_path.suffix.lower()
    
    if suffix in [".yaml", ".yml"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported formats: .json, .yaml, .yml"
        )


def parse_aircraft_date(date_str: str) -> Optional[datetime]:
    """Parse aircraft date format (e.g., '01-JAN-14') to datetime."""
    if pd.isna(date_str) or not date_str or str(date_str).strip() == '':
        return None
    try:
        # Handle format like '01-JAN-14' -> 2014-01-01
        # Map 2-digit year: 00-50 -> 2000-2050, 51-99 -> 1951-1999
        parts = str(date_str).strip().split('-')
        if len(parts) == 3:
            day, month_str, year_str = parts
            month_map = {
                'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
            }
            month = month_map.get(month_str.upper())
            if month:
                year = int(year_str)
                # Convert 2-digit year to 4-digit (00-50 -> 2000-2050, 51-99 -> 1951-1999)
                if year <= 50:
                    year += 2000
                else:
                    year += 1900
                return datetime(year, month, int(day))
    except (ValueError, KeyError, AttributeError):
        pass
    return None


def clean_aircraft_data(row: pd.Series) -> Dict[str, Any]:
    """
    Clean aircraft data for validation:
    1. Convert NaN to None for optional fields
    2. Parse date strings to datetime objects
    3. Add required metadata field
    """
    data = row.to_dict()
    
    # Convert pandas NaN/NaT to None (Python None)
    cleaned = {}
    for key, value in data.items():
        if pd.isna(value):
            cleaned[key] = None
        else:
            cleaned[key] = value
    
    # Parse date fields
    if 'VALID_SINCE' in cleaned and cleaned['VALID_SINCE']:
        cleaned['VALID_SINCE'] = parse_aircraft_date(cleaned['VALID_SINCE'])
    if 'VALID_UNTIL' in cleaned and cleaned['VALID_UNTIL']:
        cleaned['VALID_UNTIL'] = parse_aircraft_date(cleaned['VALID_UNTIL'])
    if 'LAST_UPDATE' in cleaned and cleaned['LAST_UPDATE']:
        cleaned['LAST_UPDATE'] = parse_aircraft_date(cleaned['LAST_UPDATE'])
    
    # Add required metadata field if missing
    if 'metadata' not in cleaned:
        cleaned['metadata'] = {}
    
    return cleaned


def create_aircraft_schema() -> Dict[str, Any]:
    """Step 1: Convert Aircraft Pydantic model to JSON Schema using pycharter."""
    print("=" * 70)
    print("Step 1: Converting Aircraft Pydantic Model to JSON Schema")
    print("=" * 70)
    
    # Use pycharter's model_to_schema to convert
    schema = model_to_schema(Aircraft)
    
    print(f"✓ Schema generated successfully")
    print(f"  Title: {schema.get('title', 'N/A')}")
    print(f"  Type: {schema.get('type', 'N/A')}")
    print(f"  Properties: {len(schema.get('properties', {}))} fields")
    print(f"  Required fields: {len(schema.get('required', []))}")
    
    # Save to file for reference
    to_file(Aircraft, str(AIRCRAFT_SCHEMA))
    print(f"✓ Schema saved to: {AIRCRAFT_SCHEMA}")
    
    return schema


def load_coercion_rules() -> Dict[str, str]:
    """Step 2a: Load coercion rules from JSON or YAML file."""
    print("\n" + "=" * 70)
    print("Step 2a: Loading Coercion Rules")
    print("=" * 70)
    
    # Try YAML first, fallback to JSON
    yaml_path = AIRCRAFT_COERCION_RULES.with_suffix('.yaml')
    json_path = AIRCRAFT_COERCION_RULES
    
    if yaml_path.exists():
        file_path = yaml_path
        file_type = "YAML"
    elif json_path.exists():
        file_path = json_path
        file_type = "JSON"
    else:
        raise FileNotFoundError(f"Coercion rules file not found: {yaml_path} or {json_path}")
    
    coercion_data = load_json_or_yaml(file_path)
    coercion_rules = coercion_data["rules"]
    
    print(f"✓ Loaded {len(coercion_rules)} coercion rules from {file_path.name} ({file_type})")
    print(f"  Required fields: {sum(1 for v in coercion_rules.values() if 'nullable' not in v)}")
    print(f"  Optional fields: {sum(1 for v in coercion_rules.values() if 'nullable' in v)}")
    print(f"  Version: {coercion_data.get('version', 'N/A')}")
    
    return coercion_rules


def load_validation_rules() -> Dict[str, Any]:
    """Step 2b: Load validation rules from JSON or YAML file."""
    print("\n" + "=" * 70)
    print("Step 2b: Loading Validation Rules")
    print("=" * 70)
    
    # Try YAML first, fallback to JSON
    yaml_path = AIRCRAFT_VALIDATION_RULES.with_suffix('.yaml')
    json_path = AIRCRAFT_VALIDATION_RULES
    
    if yaml_path.exists():
        file_path = yaml_path
        file_type = "YAML"
    elif json_path.exists():
        file_path = json_path
        file_type = "JSON"
    else:
        raise FileNotFoundError(f"Validation rules file not found: {yaml_path} or {json_path}")
    
    validation_data = load_json_or_yaml(file_path)
    validation_rules = validation_data["rules"]
    
    print(f"✓ Loaded {len(validation_rules)} validation rules from {file_path.name} ({file_type})")
    print(f"  String validations: {sum(1 for v in validation_rules.values() if 'max_length' in v or 'non_empty_string' in v)}")
    print(f"  Numeric validations: {sum(1 for v in validation_rules.values() if 'greater_than_or_equal_to' in v)}")
    print(f"  Enum validations: {sum(1 for v in validation_rules.values() if 'only_allow' in v)}")
    print(f"  Version: {validation_data.get('version', 'N/A')}")
    
    return validation_rules


def load_metadata() -> Dict[str, Any]:
    """Step 2c: Load metadata from JSON or YAML file."""
    print("\n" + "=" * 70)
    print("Step 2c: Loading Metadata")
    print("=" * 70)
    
    # Try YAML first, fallback to JSON
    yaml_path = AIRCRAFT_METADATA.with_suffix('.yaml')
    json_path = AIRCRAFT_METADATA
    
    if yaml_path.exists():
        file_path = yaml_path
        file_type = "YAML"
    elif json_path.exists():
        file_path = json_path
        file_type = "JSON"
    else:
        raise FileNotFoundError(f"Metadata file not found: {yaml_path} or {json_path}")
    
    metadata = load_json_or_yaml(file_path)
    
    # Update dynamic fields if needed
    metadata["data_quality"]["total_records"] = len(df)
    metadata["data_quality"]["last_updated"] = datetime.now().isoformat()
    
    print(f"✓ Loaded metadata from {file_path.name} ({file_type})")
    print(f"  Version: {metadata['version']}")
    print(f"  Total records: {metadata['data_quality']['total_records']}")
    print(f"  Governance rules: {len(metadata['governance_rules'])}")
    print(f"  Business rules: {len(metadata['business_rules'])}")
    
    return metadata


def store_in_metadata_store(
    schema: Dict[str, Any],
    coercion_rules: Dict[str, str],
    validation_rules: Dict[str, Any],
    metadata: Dict[str, Any],
) -> tuple[InMemoryMetadataStore, str]:
    """Step 3: Store all components in InMemoryMetadataStore."""
    print("\n" + "=" * 70)
    print("Step 3: Storing Components in InMemoryMetadataStore")
    print("=" * 70)
    
    # Initialize store
    store = InMemoryMetadataStore()
    store.connect()
    print("✓ Connected to InMemoryMetadataStore")
    
    # Store schema
    schema_id = store.store_schema(
        schema_name="aircraft",
        schema=schema,
        version="1.0.0"
    )
    print(f"✓ Stored schema (ID: {schema_id})")
    
    # Store coercion rules
    coercion_id = store.store_coercion_rules(
        schema_id=schema_id,
        coercion_rules=coercion_rules,
        version="1.0.0"
    )
    print(f"✓ Stored coercion rules (ID: {coercion_id})")
    
    # Store validation rules
    validation_id = store.store_validation_rules(
        schema_id=schema_id,
        validation_rules=validation_rules,
        version="1.0.0"
    )
    print(f"✓ Stored validation rules (ID: {validation_id})")
    
    # Store metadata
    metadata_id = store.store_metadata(
        resource_id=schema_id,
        metadata=metadata,
        resource_type="schema"
    )
    print(f"✓ Stored metadata (ID: {metadata_id})")
    
    # Store ownership
    store.store_ownership(
        resource_id=schema_id,
        owner="operations-team",
        team="data-engineering"
    )
    print(f"✓ Stored ownership (owner: operations-team, team: data-engineering)")
    
    # Verify retrieval
    print("\n✓ Verifying stored components:")
    retrieved_schema = store.get_schema(schema_id)
    print(f"  Schema: {'✓' if retrieved_schema else '✗'} ({len(retrieved_schema.get('properties', {}))} properties)")
    
    retrieved_coercion = store.get_coercion_rules(schema_id, version="1.0.0")
    print(f"  Coercion rules: {'✓' if retrieved_coercion else '✗'} ({len(retrieved_coercion) if retrieved_coercion else 0} rules)")
    
    retrieved_validation = store.get_validation_rules(schema_id, version="1.0.0")
    print(f"  Validation rules: {'✓' if retrieved_validation else '✗'} ({len(retrieved_validation) if retrieved_validation else 0} rules)")
    
    retrieved_metadata = store.get_metadata(schema_id)
    print(f"  Metadata: {'✓' if retrieved_metadata else '✗'}")
    
    retrieved_ownership = store.get_ownership(schema_id)
    print(f"  Ownership: {'✓' if retrieved_ownership else '✗'}")
    
    return store, schema_id


def validate_with_store_example(store: InMemoryMetadataStore, schema_id: str):
    """Step 4: Demonstrate validation using stored components."""
    print("\n" + "=" * 70)
    print("Step 4: Validating Data Using Stored Components")
    print("=" * 70)
    
    # Get a sample row from the dataframe - use raw data, let pycharter handle coercion
    sample_row = df.iloc[0]
    raw_data = sample_row.to_dict()
    
    # Convert pandas NaN to None for optional fields (but keep date strings as strings)
    raw_data_cleaned = {}
    for key, value in raw_data.items():
        if pd.isna(value):
            raw_data_cleaned[key] = None
        else:
            raw_data_cleaned[key] = value
    
    # Add required metadata field
    raw_data_cleaned['metadata'] = {}
    
    print(f"\nTesting validation with first row (raw data, coercion will be applied):")
    print(f"  Registration: {raw_data_cleaned.get('REGISTRATION')}")
    print(f"  Operator: {raw_data_cleaned.get('AC_OPERATOR')}")
    print(f"  Valid Since (raw): {raw_data_cleaned.get('VALID_SINCE')} (type: {type(raw_data_cleaned.get('VALID_SINCE')).__name__})")
    
    # Validate using pycharter's validate_with_store - it will apply coercion rules
    result = validate_with_store(
        store=store,
        schema_id=schema_id,
        data=raw_data_cleaned,
        strict=False
    )
    
    if result.is_valid:
        print("\n✓ Validation successful!")
        print(f"  Registration: {result.data.registration}")
        print(f"  Operator: {result.data.ac_operator}")
        print(f"  Valid Since: {result.data.valid_since} (coerced from string)")
        print(f"  Valid Until: {result.data.valid_until} (coerced from string)")
        print(f"  Max Takeoff Weight: {result.data.max_takeoff_wgt}")
    else:
        print("\n✗ Validation failed (showing first 5 errors):")
        for error in result.errors[:5]:
            if isinstance(error, dict):
                loc = error.get('loc', 'unknown')
                msg = error.get('msg', 'unknown error')
                print(f"  - {loc}: {msg}")
            else:
                print(f"  - {error}")
        print(f"\n  Note: Some errors may be due to model constraints (e.g., ACARS enum)")
        print(f"        that don't allow None for optional enum fields.")
    
    # Test batch validation with raw data
    print(f"\nTesting batch validation with first 5 rows (raw data):")
    batch_data = []
    for i in range(min(5, len(df))):
        row_dict = df.iloc[i].to_dict()
        # Convert NaN to None, keep strings as strings
        cleaned = {}
        for key, value in row_dict.items():
            if pd.isna(value):
                cleaned[key] = None
            else:
                cleaned[key] = value
        cleaned['metadata'] = {}
        batch_data.append(cleaned)
    
    from pycharter import validate_batch_with_store
    batch_results = validate_batch_with_store(
        store=store,
        schema_id=schema_id,
        data_list=batch_data,
        strict=False
    )
    
    valid_count = sum(1 for r in batch_results if r.is_valid)
    print(f"  Valid: {valid_count}/{len(batch_results)}")
    print(f"  Invalid: {len(batch_results) - valid_count}/{len(batch_results)}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Complete PyCharter Data Journey for Aircraft Dataset")
    print("=" * 70)
    
    # Step 1: Convert model to schema
    schema = create_aircraft_schema()
    
    # Step 2: Load rules and metadata from JSON files
    coercion_rules = load_coercion_rules()
    validation_rules = load_validation_rules()
    metadata = load_metadata()
    
    # Step 3: Store in metadata store
    store, schema_id = store_in_metadata_store(
        schema=schema,
        coercion_rules=coercion_rules,
        validation_rules=validation_rules,
        metadata=metadata
    )
    
    # Step 4: Validate using stored components
    validate_with_store_example(store, schema_id)
    
    print("\n" + "=" * 70)
    print("✓ Complete PyCharter Data Journey Completed Successfully!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Schema ID: {schema_id}")
    print(f"  Schema version: 1.0.0")
    print(f"  Coercion rules: {len(coercion_rules)}")
    print(f"  Validation rules: {len(validation_rules)}")
    print(f"  Total records: {len(df)}")