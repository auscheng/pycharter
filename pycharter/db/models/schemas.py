"""
SQLAlchemy model for schemas table
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class SchemaModel(Base):
    """SQLAlchemy model for schemas table."""
    
    __tablename__ = "schemas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=True)
    schema_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_schemas_name_version"),
        {"schema": "pycharter"},
    )
    
    # Relationships
    coercion_rules = relationship("CoercionRulesModel", back_populates="schema", cascade="all, delete-orphan")
    validation_rules = relationship("ValidationRulesModel", back_populates="schema", cascade="all, delete-orphan")
    governance_rules = relationship("GovernanceRulesModel", back_populates="schema")

