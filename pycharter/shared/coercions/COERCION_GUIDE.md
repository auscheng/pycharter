# Coercion Functions Guide

## Overview

PyCharter provides coercion functions to transform data **before** Pydantic validation. This guide explains when to use each coercion function, with special focus on nullable vs non-nullable variants.

## Key Concept: Nullable vs Non-Nullable

### Non-Nullable Coercions (Standard) - **STRICT**
- **Purpose**: For **required fields** that must always have a valid value
- **Behavior**: **Raises ValueError** if conversion fails or data is null
- **Return type**: Always returns the target type (e.g., `int`, `str`, `bool`)
- **Use when**: Field is required in your schema and must always be valid

### Nullable Coercions - **LENIENT**
- **Purpose**: For **optional fields** that can be null/None
- **Behavior**: **Returns None** if conversion fails or data is null (never raises errors)
- **Return type**: Returns target type OR `None` (e.g., `int | None`, `str | None`)
- **Use when**: Field is optional in your schema and can be missing/invalid

## Detailed Comparison

### 1. String Coercions

#### `coerce_to_string`
```python
# For REQUIRED string fields
coerce_to_string(42)        # → "42"
coerce_to_string(None)      # → None (preserved)
coerce_to_string(pd.NA)     # → None (preserved)
coerce_to_string("value")   # → "value"
```

**Use when**: Field is required and must always be a string.

#### `coerce_to_nullable_string`
```python
# For OPTIONAL string fields
coerce_to_nullable_string(42)        # → "42"
coerce_to_nullable_string(None)      # → None
coerce_to_nullable_string(pd.NA)     # → None
coerce_to_nullable_string("nan")     # → None (string "nan" → None)
coerce_to_nullable_string("value")   # → "value"
```

**Use when**: Field is optional and can be null.

**Key difference**: Handles string representations of null ("nan", "null", etc.) → None

---

### 2. Integer Coercions

#### `coerce_to_integer` ⚠️ **STRICT**
```python
# For REQUIRED integer fields - RAISES ERRORS on failure
coerce_to_integer("42")           # → 42 (int)
coerce_to_integer(3.14)           # → 3 (int)
coerce_to_integer(None)            # ❌ Raises ValueError
coerce_to_integer(pd.NA)           # ❌ Raises ValueError
coerce_to_integer("not_a_number")  # ❌ Raises ValueError
```

**Use when**: Field is required and must always be a valid integer.

**Behavior**: Must succeed or error - never returns None or original value.

#### `coerce_to_nullable_integer` ✅ **LENIENT**
```python
# For OPTIONAL integer fields - RETURNS None on failure
coerce_to_nullable_integer("42")           # → 42 (int)
coerce_to_nullable_integer(3.14)           # → 3 (int)
coerce_to_nullable_integer(None)            # → None
coerce_to_nullable_integer(pd.NA)          # → None
coerce_to_nullable_integer("nan")          # → None
coerce_to_nullable_integer("not_a_number") # → None (not an error!)
```

**Use when**: Field is optional and can be null or invalid.

**Key difference**: Returns `None` instead of raising errors - perfect for optional fields.

---

### 3. Float Coercions

#### `coerce_to_float`
```python
# For REQUIRED float fields
coerce_to_float("3.14")     # → 3.14
coerce_to_float(42)         # → 42.0
coerce_to_float(None)       # → None (preserved)
coerce_to_float(np.nan)     # → None (preserved)
```

**Use when**: Field is required and must always be a float.

#### `coerce_to_nullable_float`
```python
# For OPTIONAL float fields
coerce_to_nullable_float("3.14")     # → 3.14
coerce_to_nullable_float(42)         # → 42.0
coerce_to_nullable_float(None)       # → None
coerce_to_nullable_float(np.nan)     # → None
coerce_to_nullable_float("nan")      # → None
```

**Use when**: Field is optional and can be null.

---

### 4. Boolean Coercions ⚠️ **Important Difference**

#### `coerce_to_boolean`
```python
# For REQUIRED boolean fields
coerce_to_boolean("true")   # → True
coerce_to_boolean("false")  # → False
coerce_to_boolean("")       # → False (empty string → False)
coerce_to_boolean(None)     # → None (preserved)
coerce_to_boolean(pd.NA)    # → None (preserved)
```

**Use when**: Field is required and must always be True or False.

**Note**: Empty strings and null-like strings convert to `False`, but actual `None` is preserved.

#### `coerce_to_nullable_boolean`
```python
# For OPTIONAL boolean fields
coerce_to_nullable_boolean("true")   # → True
coerce_to_nullable_boolean("false")   # → False
coerce_to_nullable_boolean("")        # → None (empty string → None)
coerce_to_nullable_boolean("nan")     # → None (string "nan" → None)
coerce_to_nullable_boolean(None)      # → None
coerce_to_nullable_boolean(pd.NA)     # → None
```

**Use when**: Field is optional and can be null.

**Key difference**: 
- Empty strings → `None` (not `False`)
- Null values → `None` (not `False`)
- More appropriate for optional boolean fields

---

### 5. Datetime Coercions

#### `coerce_to_datetime`
```python
# For REQUIRED datetime fields
coerce_to_datetime("2024-01-01")     # → datetime(2024, 1, 1)
coerce_to_datetime(None)              # → None (preserved)
coerce_to_datetime(pd.NaT)           # → None (preserved)
coerce_to_datetime("")                # → "" (empty string preserved)
```

**Use when**: Field is required and must always be a datetime.

**Note**: Empty strings are preserved as-is (not converted to None).

#### `coerce_to_nullable_datetime`
```python
# For OPTIONAL datetime fields
coerce_to_nullable_datetime("2024-01-01")  # → datetime(2024, 1, 1)
coerce_to_nullable_datetime(None)          # → None
coerce_to_nullable_datetime(pd.NaT)        # → None
coerce_to_nullable_datetime("")            # → None (empty string → None)
coerce_to_nullable_datetime("nan")         # → None
```

**Use when**: Field is optional and can be null.

**Key difference**: Empty strings → `None` (not preserved as empty string).

---

### 6. UUID Coercions

#### `coerce_to_uuid`
```python
# For REQUIRED UUID fields
coerce_to_uuid("123e4567-e89b-12d3-a456-426614174000")  # → UUID object
coerce_to_uuid(None)                                     # → None (preserved)
```

**Use when**: Field is required and must always be a UUID.

#### `coerce_to_nullable_uuid`
```python
# For OPTIONAL UUID fields
coerce_to_nullable_uuid("123e4567-e89b-12d3-a456-426614174000")  # → UUID object
coerce_to_nullable_uuid(None)                                     # → None
coerce_to_nullable_uuid("nan")                                    # → None
```

**Use when**: Field is optional and can be null.

---

## Special Coercion Functions

### `coerce_to_none`
**Purpose**: Preprocessing step to normalize all null types to Python `None`

```python
coerce_to_none(pd.NA)      # → None
coerce_to_none(pd.NaT)     # → None
coerce_to_none(np.nan)     # → None
coerce_to_none("nan")      # → None
coerce_to_none(None)       # → None
coerce_to_none("value")    # → "value" (unchanged)
```

**Use when**: 
- You want to normalize all null types before other coercions
- As a preprocessing step in data cleaning pipelines
- When working with pandas DataFrames with mixed null types

**Example**:
```python
# In your coercion rules
{
  "field_name": "coerce_to_none"  # First normalize nulls
}
# Then apply type coercion
{
  "field_name": "coerce_to_nullable_integer"  # Then convert to int
}
```

### `coerce_to_json`
**Purpose**: Convert dict or string to JSON string

```python
coerce_to_json({"key": "value"})           # → '{"key": "value"}'
coerce_to_json('{"key": "value"}')         # → '{"key": "value"}'
coerce_to_json("{'key': 'value'}")         # → '{"key": "value"}' (Python dict string)
```

**Use when**: 
- Field should store JSON data as a string
- Converting Python dict strings to proper JSON
- Normalizing JSON data formats

### `coerce_empty_to_null`
**Purpose**: Convert empty values to None

```python
coerce_empty_to_null("")       # → None
coerce_empty_to_null([])       # → None
coerce_empty_to_null({})       # → None
coerce_empty_to_null("value")  # → "value" (unchanged)
```

**Use when**: 
- You want empty strings/lists/dicts to be treated as null
- For optional fields where empty = missing

---

## Decision Tree: Which Coercion to Use?

```
Is the field REQUIRED in your schema?
├─ YES → Use non-nullable coercion (e.g., coerce_to_string)
│         └─ Field must always be valid
│         └─ Will RAISE ERROR if invalid/null
│         └─ Return type: Always target type (int, str, bool, etc.)
│
└─ NO → Use nullable coercion (e.g., coerce_to_nullable_string)
        └─ Field can be null/invalid
        └─ Will RETURN None if invalid/null (never errors)
        └─ Return type: Target type OR None (int | None, str | None, etc.)
        
Key Principle:
├─ Non-nullable = STRICT (must succeed or error)
└─ Nullable = LENIENT (returns None on failure)
```

## Practical Examples

### Example 1: Required vs Optional Fields

```json
{
  "schema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string"},           // REQUIRED
      "email": {"type": "string"},             // REQUIRED
      "phone": {"type": ["string", "null"]}    // OPTIONAL
    },
    "required": ["user_id", "email"]
  },
  "coercion_rules": {
    "rules": {
      "user_id": "coerce_to_string",           // Required → non-nullable
      "email": "coerce_to_string",             // Required → non-nullable
      "phone": "coerce_to_nullable_string"     // Optional → nullable
    }
  }
}
```

### Example 2: Pandas DataFrame with NaN Values

```python
import pandas as pd
from pycharter import validate, from_dict

# DataFrame with NaN values
df = pd.DataFrame({
    "age": [25, 30, pd.NA, 35],           # Optional field
    "name": ["Alice", "Bob", "Charlie", "David"]  # Required field
})

# Schema with optional age field
schema = {
    "type": "object",
    "properties": {
        "age": {"type": ["integer", "null"]},    # Optional
        "name": {"type": "string"}                # Required
    },
    "required": ["name"]
}

# Coercion rules
coercion_rules = {
    "rules": {
        "age": "coerce_to_nullable_integer",  # Optional → nullable
        "name": "coerce_to_string"            # Required → non-nullable
    }
}

# Generate model and validate
Person = from_dict(schema, "Person")
result = validate(Person, df.iloc[0].to_dict())
```

### Example 3: Boolean Field with Missing Values

```json
{
  "coercion_rules": {
    "rules": {
      "is_active": "coerce_to_boolean",              // Required boolean
      "is_verified": "coerce_to_nullable_boolean"    // Optional boolean
    }
  }
}
```

**Behavior**:
- `is_active`: `""` → `False`, `None` → `None` (validation error if required)
- `is_verified`: `""` → `None`, `None` → `None` (valid for optional field)

## Summary Table

| Coercion Function | Use For | Behavior on Null/Invalid | Return Type |
|------------------|---------|-------------------------|-------------|
| `coerce_to_string` | Required strings | **Raises ValueError** | `str` |
| `coerce_to_nullable_string` | Optional strings | **Returns None** | `str \| None` |
| `coerce_to_integer` | Required integers | **Raises ValueError** | `int` |
| `coerce_to_nullable_integer` | Optional integers | **Returns None** | `int \| None` |
| `coerce_to_float` | Required floats | **Raises ValueError** | `float` |
| `coerce_to_nullable_float` | Optional floats | **Returns None** | `float \| None` |
| `coerce_to_boolean` | Required booleans | **Raises ValueError** | `bool` |
| `coerce_to_nullable_boolean` | Optional booleans | **Returns None** | `bool \| None` |
| `coerce_to_datetime` | Required datetimes | **Raises ValueError** | `datetime` |
| `coerce_to_nullable_datetime` | Optional datetimes | **Returns None** | `datetime \| None` |
| `coerce_to_uuid` | Required UUIDs | **Raises ValueError** | `UUID` |
| `coerce_to_nullable_uuid` | Optional UUIDs | **Returns None** | `UUID \| None` |

**Key**: Non-nullable = strict (errors), Nullable = lenient (returns None)

## Best Practices

1. **Match coercion to schema**: Use nullable coercions for optional fields, non-nullable for required fields
2. **Preprocess with `coerce_to_none`**: When working with pandas DataFrames, normalize nulls first
3. **Use nullable boolean for optional flags**: `coerce_to_nullable_boolean` is better for optional boolean fields
4. **Combine coercions**: You can chain coercions (e.g., `coerce_to_none` then `coerce_to_nullable_integer`)
5. **Test with real data**: Always test with your actual data sources (CSV, API responses, etc.)

