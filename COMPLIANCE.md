# JSON Schema Compliance

Charter is designed to be fully compliant with the JSON Schema Draft 2020-12 standard while providing extensions for enhanced functionality.

## JSON Schema Standard Support

Charter validates all schemas against the JSON Schema Draft 2020-12 standard before processing. This ensures that:

1. **Schemas are valid JSON Schema** - All schemas must conform to the JSON Schema standard
2. **Standard keywords are supported** - All standard validation keywords work as expected
3. **Extensions are clearly defined** - Custom fields are documented and optional

## Standard JSON Schema Keywords

The following standard JSON Schema keywords are fully supported:

### String Constraints
- `minLength` - Minimum string length
- `maxLength` - Maximum string length
- `pattern` - Regular expression pattern matching
- `format` - String format (stored for reference, can be used with custom validators)

### Number Constraints
- `minimum` - Minimum value (inclusive)
- `maximum` - Maximum value (inclusive)
- `exclusiveMinimum` - Minimum value (exclusive)
- `exclusiveMaximum` - Maximum value (exclusive)
- `multipleOf` - Must be a multiple of this value

### Array Constraints
- `minItems` - Minimum array length
- `maxItems` - Maximum array length
- `uniqueItems` - Array items must be unique

### Value Constraints
- `enum` - List of allowed values
- `const` - Single allowed value

### Other Standard Keywords
- `type` - Data type (string, integer, number, boolean, array, object, null)
- `properties` - Object properties
- `items` - Array item schema
- `required` - Required fields
- `default` - Default values
- `description` - Field description
- `title` - Field title
- `examples` - Example values

## Charter Extensions

Charter adds two optional extension fields that can be used alongside standard JSON Schema:

### `coercion` (Pre-validation)
Specifies a coercion function to apply before validation. This allows type conversion (e.g., string to integer) before standard validation runs.

```json
{
  "type": "integer",
  "coercion": "coerce_to_integer"
}
```

### `validations` (Post-validation)
Specifies additional validation rules to apply after standard validation. These are custom validators that can perform complex checks.

```json
{
  "type": "string",
  "validations": {
    "min_length": {"threshold": 3},
    "no_capital_characters": null
  }
}
```

## Schema Validation

All schemas are validated using the `jsonschema` library (if available) against the JSON Schema Draft 2020-12 standard. If `jsonschema` is not available, basic validation is performed.

### Strict Mode

You can enable strict mode to only allow standard JSON Schema fields (no extensions):

```python
from pycharter.shared.schema_parser import validate_schema

# Strict mode - only standard JSON Schema
validate_schema(schema, strict_json_schema=True)
```

## Data-Driven Validation

All validation logic in Charter is **data-driven**. This means:

1. **No Python code required** - Validation rules are defined in JSON
2. **Dynamic model generation** - Models are created at runtime from JSON schemas
3. **Extensible** - Custom coercions and validations can be registered, but the rules themselves are stored as data

### Example: Fully Data-Driven Schema

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "minLength": 3,
      "maxLength": 10,
      "pattern": "^[a-z]+$",
      "coercion": "coerce_to_string",
      "validations": {
        "no_capital_characters": null
      }
    }
  }
}
```

This schema uses:
- Standard JSON Schema: `minLength`, `maxLength`, `pattern`
- Charter extensions: `coercion`, `validations`

All of this is stored as JSON data and can be loaded from files, URLs, or dictionaries.

## Nested Schemas

Charter fully supports nested object schemas, which are recursively processed:

```json
{
  "type": "object",
  "properties": {
    "address": {
      "type": "object",
      "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"}
      },
      "required": ["street", "city"]
    }
  }
}
```

Each nested object becomes its own Pydantic model, ensuring full type safety and validation.

## Compatibility

- **JSON Schema Draft 2020-12** - Full support
- **Pydantic v2** - Full compatibility
- **Python 3.10+** - Required

## Validation Flow

1. **Schema Validation** - Validate schema against JSON Schema standard
2. **Coercion** (if specified) - Apply pre-validation type conversion
3. **Standard Validation** - Apply JSON Schema constraints (minLength, pattern, etc.)
4. **Pydantic Validation** - Apply Pydantic type validation
5. **Custom Validations** (if specified) - Apply post-validation rules

This ensures that all validation logic is applied in the correct order and that schemas are compliant with JSON Schema standards.

