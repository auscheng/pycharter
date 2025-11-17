"""
Pydantic model for Book data structure.

This is the developer-defined model that represents the technical schema.
It will be converted to JSON Schema format.
"""

from datetime import datetime
from typing import ClassVar, List, Optional

from pydantic import BaseModel, Field


class Author(BaseModel):
    """Author information."""

    name: str = Field(..., min_length=1, max_length=100, description="Author's full name")
    email: Optional[str] = Field(None, description="Author's email address")
    bio: Optional[str] = Field(None, max_length=500, description="Author biography")


class Book(BaseModel):
    """Book model with nested author and metadata."""
    
    # Schema version - required for versioning support
    __version__: ClassVar[str] = "1.0.0"

    isbn: str = Field(..., description="International Standard Book Number")
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    author: Author = Field(..., description="Book author")
    description: Optional[str] = Field(None, max_length=2000, description="Book description")
    price: float = Field(..., ge=0, description="Book price in USD")
    pages: int = Field(..., gt=0, description="Number of pages")
    published_date: datetime = Field(..., description="Publication date")
    tags: Optional[List[str]] = Field(None, description="Book tags/categories")
    in_stock: bool = Field(True, description="Whether book is in stock")

