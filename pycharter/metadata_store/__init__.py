"""
Metadata Store Client Service

Connects to a relational database (like AWS RDS) and manages storage/retrieval
of decomposed metadata (schemas, governance rules, ownership, etc.).
"""

from pycharter.metadata_store.client import MetadataStoreClient

__all__ = [
    "MetadataStoreClient",
]

