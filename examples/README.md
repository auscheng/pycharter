# PyCharter Examples

This directory contains focused examples demonstrating each of PyCharter's five core services and a complete workflow example.

## Service Examples

Each example focuses on a specific service:

### 1. Contract Parser (`01_contract_parser.py`)
- Parse contract files (YAML/JSON)
- Parse contract dictionaries
- Access decomposed components (schema, governance, ownership, metadata)

**Run**: `python examples/01_contract_parser.py`

### 2. Metadata Store (`02_metadata_store.py`)
- Store metadata in database
- Retrieve stored schemas
- Implement custom database backends

**Run**: `python examples/02_metadata_store.py`

### 3. Pydantic Generator (`03_pydantic_generator.py`)
- Generate models from dictionaries
- Generate models from files
- Generate models from JSON strings
- Generate model files
- Handle nested objects and arrays

**Run**: `python examples/03_pydantic_generator.py`

### 4. JSON Schema Converter (`04_json_schema_converter.py`)
- Convert models to JSON Schema dictionaries
- Convert models to JSON strings
- Convert models to files
- Round-trip conversion (schema → model → schema)
- Preserve field constraints

**Run**: `python examples/04_json_schema_converter.py`

### 5. Runtime Validator (`05_runtime_validator.py`)
- Validate single records
- Validate batch data
- Strict vs lenient mode
- Use in ETL pipelines
- Validate with stored schemas

**Run**: `python examples/05_runtime_validator.py`

## Complete Workflow

### Complete Workflow (`complete_workflow.py`)
Demonstrates all five services working together in a complete data production journey:
1. Parse contract → 2. Store metadata → 3. Generate model → 4. Convert schema → 5. Validate data

**Run**: `python examples/complete_workflow.py`

## Legacy Examples

### Comprehensive Examples (`example_usage.py`)
A comprehensive script demonstrating various features including:
- Standard JSON Schema keywords
- x-validators format
- $ref and definitions
- Format fields
- Reverse conversion
- Validation errors

**Run**: `python examples/example_usage.py`

## Data Files

All data files (schemas, sample data, contracts) are located in the `data/` directory at the project root:

- `data/schemas/` - JSON Schema files
- `data/sample_data/` - Sample data files
- `data/contracts/` - Data contract files (YAML/JSON)

See `data/README.md` for more information.

## Running Examples

### Run Individual Examples

```bash
# From project root
python examples/01_contract_parser.py
python examples/02_metadata_store.py
python examples/03_pydantic_generator.py
python examples/04_json_schema_converter.py
python examples/05_runtime_validator.py
python examples/complete_workflow.py
```

### Run All Examples

```bash
# Run each example script
for script in examples/0*.py examples/complete_workflow.py; do
    python "$script"
done
```

## Example Output

Each example script provides:
- Clear section headers
- Step-by-step demonstrations
- Success/failure indicators (✓/✗)
- Explanatory output
- Error handling examples

## Next Steps

1. **Explore individual services** - Run each numbered example to understand specific services
2. **See the complete workflow** - Run `complete_workflow.py` to see all services together
3. **Modify examples** - Adapt examples to your use case
4. **Read the docs** - Check the main `README.md` for full documentation

## Notes

- All examples use data from the `data/` directory
- Examples are self-contained and can be run independently
- Some examples create temporary files (like generated models) that can be cleaned up
- Make sure you have the package installed: `pip install -e .` or `make install-dev`
