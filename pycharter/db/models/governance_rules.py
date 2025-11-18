"""
SQLAlchemy model for governance_rules table
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class GovernanceRulesModel(Base):
    """SQLAlchemy model for governance_rules table."""
    
    __tablename__ = "governance_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    rule_definition = Column(JSON, nullable=False)
    schema_id = Column(Integer, ForeignKey("schemas.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    schema = relationship("SchemaModel", back_populates="governance_rules")

