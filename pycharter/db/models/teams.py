"""
SQLAlchemy model for teams table.

Represents teams that have access control permissions (read/write) for data contracts.
Examples: operations-team, data-team, engineering-team
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class TeamModel(Base):
    """SQLAlchemy model for teams table."""
    
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    team_type = Column(String(50), nullable=True)  # e.g., "engineering", "operations", "data"
    is_active = Column(String(10), default="true", nullable=False)  # "true" or "false"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"schema": "pycharter"},
    )
    
    # Relationships
    access_permissions = relationship(
        "DataContractTeamAccess",
        back_populates="team"
    )

