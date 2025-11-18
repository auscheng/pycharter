"""
SQLAlchemy model for metadata table
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from pycharter.db.models.base import Base


class MetadataModel(Base):
    """SQLAlchemy model for metadata table."""
    
    __tablename__ = "metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=False)
    metadata_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("resource_id", "resource_type", name="uq_metadata_resource"),
    )

