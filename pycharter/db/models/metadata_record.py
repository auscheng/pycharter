"""
SQLAlchemy model for metadata_record table

Note: Table is named 'metadata_record' instead of 'metadata' because 'metadata' is a reserved word in SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from pycharter.db.models.base import Base


class MetadataModel(Base):
    """SQLAlchemy model for metadata_record table."""
    
    __tablename__ = "metadata_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=False)
    metadata_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("resource_id", "resource_type", name="uq_metadata_record_resource"),
        {"schema": "pycharter"},
    )

