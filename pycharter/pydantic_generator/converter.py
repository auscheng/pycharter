"""
Main converter module providing a clean API for JSON schema to Pydantic conversion.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel

from pycharter.pydantic_generator.generator import schema_to_model
from pycharter.shared.schema_parser import validate_schema


def from_dict(schema: Dict[str, Any], model_name: str = "DynamicModel") -> Type[BaseModel]:
    """
    Convert a JSON schema dictionary to a Pydantic model.
    
    Args:
        schema: The JSON schema as a dictionary
        model_name: Name for the generated Pydantic model class
        
    Returns:
        A Pydantic model class
        
    Example:
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "name": {"type": "string", "description": "Person's name"},
        ...         "age": {"type": "integer", "description": "Person's age"}
        ...     },
        ...     "required": ["name"]
        ... }
        >>> Person = from_dict(schema, "Person")
        >>> person = Person(name="Alice", age=30)
        >>> person.name
        'Alice'
        >>> person.age
        30
    """
    validate_schema(schema)
    return schema_to_model(schema, model_name)


def from_json(json_string: str, model_name: str = "DynamicModel") -> Type[BaseModel]:
    """
    Convert a JSON schema string to a Pydantic model.
    
    Args:
        json_string: The JSON schema as a string
        model_name: Name for the generated Pydantic model class
        
    Returns:
        A Pydantic model class
        
    Example:
        >>> schema_json = '''
        ... {
        ...     "type": "object",
        ...     "properties": {
        ...         "name": {"type": "string"}
        ...     }
        ... }
        ... '''
        >>> Person = from_json(schema_json, "Person")
    """
    schema = json.loads(json_string)
    return from_dict(schema, model_name)


def from_file(file_path: Union[str, Path], model_name: Optional[str] = None) -> Type[BaseModel]:
    """
    Load a JSON schema from a file and convert it to a Pydantic model.
    
    Args:
        file_path: Path to the JSON schema file
        model_name: Name for the generated Pydantic model class.
                   If None, uses the file stem as the model name.
        
    Returns:
        A Pydantic model class
        
    Example:
        >>> # Assuming schema.json exists
        >>> Person = from_file("schema.json", "Person")
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {file_path}")
    
    if model_name is None:
        model_name = path.stem.capitalize()
    
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    return from_dict(schema, model_name)


def from_url(url: str, model_name: str = "DynamicModel") -> Type[BaseModel]:
    """
    Load a JSON schema from a URL and convert it to a Pydantic model.
    
    Args:
        url: URL to the JSON schema
        model_name: Name for the generated Pydantic model class
        
    Returns:
        A Pydantic model class
        
    Example:
        >>> # Load schema from a URL
        >>> Person = from_url("https://example.com/schema.json", "Person")
    """
    try:
        import urllib.request
        
        with urllib.request.urlopen(url) as response:
            schema = json.loads(response.read().decode())
        
        return from_dict(schema, model_name)
    except ImportError:
        raise ImportError("urllib is required for from_url. It should be available in Python standard library.")
    except Exception as e:
        raise ValueError(f"Failed to load schema from URL: {e}")

