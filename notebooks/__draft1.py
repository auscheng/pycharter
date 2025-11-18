"""
Simple PyCharter Example

Demonstrates the core pycharter workflow:
1. Convert Pydantic model to JSON Schema
2. Load coercion rules, validation rules, and metadata
3. Store everything in InMemoryMetadataStore and PostgreSQL
4. Build consolidated contract and save to file
5. Validate data using stored components
"""

from pathlib import Path
import importlib.util
import pandas as pd
import yaml

from pycharter import (
    InMemoryMetadataStore,
    PostgresMetadataStore,
    to_dict,
    to_file,
    validate_with_store,
    validate_batch_with_store,
    build_contract,
    ContractArtifacts,
)

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
AIRCRAFT_DIR = SCRIPT_DIR.parent / 'data' / 'examples' / 'aircraft'

# Import Aircraft model
spec = importlib.util.spec_from_file_location("aircraft_models", AIRCRAFT_DIR / 'aircraft_models.py')
aircraft_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aircraft_models)
Aircraft = aircraft_models.Aircraft

# Load data
df = pd.read_csv(AIRCRAFT_DIR / 'aircraft.csv')


def load_yaml(file_path: Path):
    """Load YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Step 1: Convert Pydantic model to JSON Schema
schema = to_dict(Aircraft)
to_file(Aircraft, str(AIRCRAFT_DIR / 'aircraft_schema.yaml'))

# Step 2: Load rules and metadata
coercion_rules = load_yaml(AIRCRAFT_DIR / 'aircraft_coercion_rules.yaml')["rules"]
validation_rules = load_yaml(AIRCRAFT_DIR / 'aircraft_validation_rules.yaml')["rules"]
metadata = load_yaml(AIRCRAFT_DIR / 'aircraft_metadata.yaml')

# Step 3a: Store in InMemoryMetadataStore (for quick testing)
in_memory_store = InMemoryMetadataStore()
in_memory_store.connect()

schema_id = in_memory_store.store_schema("aircraft", schema, version="1.0.0")
in_memory_store.store_coercion_rules(schema_id, coercion_rules, version="1.0.0")
in_memory_store.store_validation_rules(schema_id, validation_rules, version="1.0.0")
in_memory_store.store_metadata(schema_id, metadata, "schema")
in_memory_store.store_ownership(schema_id, owner="operations-team", team="data-engineering")

# Step 3b: Store in PostgreSQL database
try:
    postgres_store = PostgresMetadataStore(
        connection_string="postgresql://postgres:1234567890@localhost:5432/postgres"
    )
    postgres_store.connect()
    
    # Store all components in PostgreSQL
    pg_schema_id = postgres_store.store_schema("aircraft", schema, version="1.0.0")
    postgres_store.store_coercion_rules(pg_schema_id, coercion_rules, version="1.0.0")
    postgres_store.store_validation_rules(pg_schema_id, validation_rules, version="1.0.0")
    postgres_store.store_metadata(pg_schema_id, metadata, "schema")
    postgres_store.store_ownership(pg_schema_id, owner="operations-team", team="data-engineering")
    
    # Store governance rules
    for rule_name, rule_data in metadata.get("governance_rules", {}).items():
        postgres_store.store_governance_rule(rule_name, rule_data, pg_schema_id)
    
    print(f"✓ Stored in PostgreSQL (schema_id: {pg_schema_id})")
    
    # Verify retrieval from PostgreSQL
    retrieved_schema = postgres_store.get_schema(pg_schema_id)
    retrieved_coercion = postgres_store.get_coercion_rules(pg_schema_id, version="1.0.0")
    retrieved_validation = postgres_store.get_validation_rules(pg_schema_id, version="1.0.0")
    retrieved_metadata = postgres_store.get_metadata(pg_schema_id, "schema")
    retrieved_ownership = postgres_store.get_ownership(pg_schema_id)
    print(f"  Retrieved schema: {retrieved_schema['title'] if retrieved_schema else 'None'}")
    print(f"  Retrieved coercion rules: {len(retrieved_coercion) if retrieved_coercion else 0} rules")
    print(f"  Retrieved validation rules: {len(retrieved_validation) if retrieved_validation else 0} rules")
    print(f"  Retrieved metadata: {retrieved_metadata['title'] if retrieved_metadata else 'None'}")
    print(f"  Retrieved ownership: {retrieved_ownership['owner'] if retrieved_ownership else 'None'}")
    
    # Use PostgreSQL store for validation (now has full feature parity)
    store = postgres_store
    schema_id = pg_schema_id
except Exception as e:
    print(f"⚠ PostgreSQL not available: {e}")
    print("  Using InMemoryMetadataStore instead")
    store = in_memory_store

# Step 3c: Build consolidated contract and save to file
ownership = store.get_ownership(schema_id)
governance_rules = metadata.get("governance_rules", {})

artifacts = ContractArtifacts(
    schema=schema,
    coercion_rules={"rules": coercion_rules, "version": "1.0.0"},
    validation_rules={"rules": validation_rules, "version": "1.0.0"},
    metadata=metadata,
    ownership=ownership,
    governance_rules=governance_rules,
)

contract = build_contract(artifacts)

# Save contract to YAML file
with open(AIRCRAFT_DIR / 'aircraft_contract.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(contract, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

# Step 4: Validate data
sample_data = df.iloc[0].to_dict()
sample_data = {k: (None if pd.isna(v) else v) for k, v in sample_data.items()}
sample_data['metadata'] = {}

result = validate_with_store(store, schema_id, sample_data, strict=False)
print(f"Validation result: {'✓ Valid' if result.is_valid else '✗ Invalid'}")

# Batch validation
batch_data = []
for i in range(min(5, len(df))):
    row = df.iloc[i].to_dict()
    row = {k: (None if pd.isna(v) else v) for k, v in row.items()}
    row['metadata'] = {}
    batch_data.append(row)

batch_results = validate_batch_with_store(store, schema_id, batch_data, strict=False)
valid_count = sum(1 for r in batch_results if r.is_valid)
print(f"Batch validation: {valid_count}/{len(batch_results)} valid")
