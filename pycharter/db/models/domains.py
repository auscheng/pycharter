"""
SQLAlchemy model for domains table.

Represents business domains that data feeds belong to.
Examples: "NetlineOps configuration", "Flight Operations", "Customer Data"
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class DomainModel(Base):
    """SQLAlchemy model for domains table."""
    
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_domain_id = Column(Integer, nullable=True)  # For hierarchical domains
    is_active = Column(String(10), default="true", nullable=False)  # "true" or "false"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"schema": "pycharter"},
    )
    
    # Relationships
    data_contracts = relationship("DataContractModel", back_populates="domain")
    parent_domain = relationship("DomainModel", remote_side="DomainModel.id", backref="sub_domains")

