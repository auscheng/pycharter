"""
SQLAlchemy model for coercion_rules table
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class CoercionRulesModel(Base):
    """SQLAlchemy model for coercion_rules table."""
    
    __tablename__ = "coercion_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_id = Column(Integer, ForeignKey("pycharter.schemas.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(50), nullable=True)
    rules = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("schema_id", "version", name="uq_coercion_rules_schema_version"),
        {"schema": "pycharter"},
    )
    
    # Relationships
    schema = relationship("SchemaModel", back_populates="coercion_rules")

