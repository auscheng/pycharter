"""
SQLAlchemy model for ownership table
"""

from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func

from pycharter.db.models.base import Base


class OwnershipModel(Base):
    """SQLAlchemy model for ownership table."""
    
    __tablename__ = "ownership"
    
    resource_id = Column(String(255), primary_key=True)
    owner = Column(String(255), nullable=False)
    team = Column(String(255), nullable=True)
    additional_info = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

