"""
SQLAlchemy model for systems table.

Represents external systems that data feeds pull from, push to, or use as sources.
Examples: NetlineOpsReplica, SCR, Fleetwise, NetlineBase
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class SystemModel(Base):
    """SQLAlchemy model for systems table."""
    
    __tablename__ = "systems"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    system_type = Column(String(50), nullable=True)  # e.g., "database", "api", "data_warehouse"
    connection_info = Column(Text, nullable=True)  # JSON string or connection details
    is_active = Column(String(10), default="true", nullable=False)  # "true" or "false"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"schema": "pycharter"},
    )
    
    # Relationships
    data_contracts_pull_from = relationship(
        "DataContractSystemPull",
        back_populates="system"
    )
    data_contracts_push_to = relationship(
        "DataContractSystemPush",
        back_populates="system"
    )
    data_contracts_source = relationship(
        "DataContractSystemSource",
        back_populates="system"
    )

