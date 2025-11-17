"""
PyCharter - Data Contract Management and Validation

Five core services:
1. Contract Parser - Reads and decomposes data contract files
2. Metadata Store Client - Database operations for metadata storage
3. Pydantic Generator - Generates Pydantic models from JSON Schema
4. JSON Schema Converter - Converts Pydantic models to JSON Schema
5. Runtime Validator - Lightweight validation utility
"""

__version__ = "0.0.2"

# Service 1: Contract Parser
from pycharter.contract_parser import (
    parse_contract,
    parse_contract_file,
    ContractMetadata,
)

# Service 2: Metadata Store Client
from pycharter.metadata_store import MetadataStoreClient

# Optional metadata store implementations
try:
    from pycharter.metadata_store import InMemoryMetadataStore
except ImportError:
    InMemoryMetadataStore = None

try:
    from pycharter.metadata_store import MongoDBMetadataStore
except ImportError:
    MongoDBMetadataStore = None

try:
    from pycharter.metadata_store import PostgresMetadataStore
except ImportError:
    PostgresMetadataStore = None

try:
    from pycharter.metadata_store import RedisMetadataStore
except ImportError:
    RedisMetadataStore = None

# Service 3: Pydantic Generator
from pycharter.pydantic_generator import (
    generate_model,
    generate_model_file,
    from_dict,
    from_file,
    from_json,
    from_url,
)

# Service 4: JSON Schema Converter
from pycharter.json_schema_converter import (
    to_dict,
    to_file,
    to_json,
    model_to_schema,
)

# Service 5: Runtime Validator
from pycharter.runtime_validator import (
    validate,
    validate_batch,
    ValidationResult,
)

__all__ = [
    # Contract Parser
    "parse_contract",
    "parse_contract_file",
    "ContractMetadata",
    # Metadata Store Client
    "MetadataStoreClient",
    "InMemoryMetadataStore",
    "MongoDBMetadataStore",
    "PostgresMetadataStore",
    "RedisMetadataStore",
    # Pydantic Generator
    "generate_model",
    "generate_model_file",
    "from_dict",
    "from_file",
    "from_json",
    "from_url",
    # JSON Schema Converter
    "to_dict",
    "to_file",
    "to_json",
    "model_to_schema",
    # Runtime Validator
    "validate",
    "validate_batch",
    "ValidationResult",
]
