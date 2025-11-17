"""
Reverse converter module providing a clean API for Pydantic model to JSON Schema conversion.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from pycharter.json_schema_converter.converter import model_to_schema


def to_dict(
    model: Type[BaseModel],
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a JSON Schema dictionary.
    
    Args:
        model: The Pydantic model class to convert
        title: Optional title for the schema
        description: Optional description for the schema
        
    Returns:
        JSON Schema as a dictionary
        
    Example:
        >>> from pydantic import BaseModel, Field
        >>> class Person(BaseModel):
        ...     name: str = Field(..., min_length=3)
        ...     age: int = Field(ge=0)
        >>> schema = to_dict(Person)
        >>> schema["properties"]["name"]["minLength"]
        3
    """
    return model_to_schema(model, title=title, description=description)


def to_json(
    model: Type[BaseModel],
    title: Optional[str] = None,
    description: Optional[str] = None,
    indent: int = 2,
) -> str:
    """
    Convert a Pydantic model to a JSON Schema string.
    
    Args:
        model: The Pydantic model class to convert
        title: Optional title for the schema
        description: Optional description for the schema
        indent: JSON indentation level
        
    Returns:
        JSON Schema as a JSON string
        
    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     name: str
        >>> schema_json = to_json(User)
        >>> print(schema_json)
    """
    schema = model_to_schema(model, title=title, description=description)
    return json.dumps(schema, indent=indent)


def to_file(
    model: Type[BaseModel],
    file_path: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    indent: int = 2,
) -> None:
    """
    Convert a Pydantic model to a JSON Schema file.
    
    Args:
        model: The Pydantic model class to convert
        file_path: Path to the output JSON file
        title: Optional title for the schema
        description: Optional description for the schema
        indent: JSON indentation level
        
    Example:
        >>> from pydantic import BaseModel
        >>> class Product(BaseModel):
        ...     name: str
        ...     price: float
        >>> to_file(Product, "product_schema.json")
    """
    schema = model_to_schema(model, title=title, description=description)
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(schema, f, indent=indent)

