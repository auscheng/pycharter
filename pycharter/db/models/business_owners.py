"""
SQLAlchemy model for business_owners table.

Represents business owners or stakeholders responsible for data feeds.
Examples: IOC, Product Team, Data Engineering
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class BusinessOwnerModel(Base):
    """SQLAlchemy model for business_owners table."""
    
    __tablename__ = "business_owners"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    is_active = Column(String(10), default="true", nullable=False)  # "true" or "false"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"schema": "pycharter"},
    )
    
    # Relationships
    data_contract_owners = relationship(
        "DataContractBusinessOwner",
        back_populates="business_owner",
        cascade="all, delete-orphan"
    )

