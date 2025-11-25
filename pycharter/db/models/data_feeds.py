"""
SQLAlchemy model for data_feeds table.

Represents data feeds (datasets) that are served. Each data feed can have
multiple data contracts (versions).
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class DataFeedModel(Base):
    """SQLAlchemy model for data_feeds table."""
    
    __tablename__ = "data_feeds"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    feed_type = Column(String(50), nullable=True)  # e.g., "Operational", "Analytical", "Reference"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"schema": "pycharter"},
    )
    
    # Relationships
    data_contracts = relationship("DataContractModel", back_populates="data_feed", cascade="all, delete-orphan")
    dependencies = relationship(
        "DataFeedDependency",
        foreign_keys="[DataFeedDependency.dependency_feed_id]",
        back_populates="dependency_feed"
    )

