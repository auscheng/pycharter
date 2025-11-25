"""
SQLAlchemy model for data_contracts table.

This is the central join table that links all components of a data contract:
- Schema
- Coercion Rules
- Validation Rules
- Governance Rules
- Metadata
- Ownership
- Data Feed
- Domain
- Systems (pull_from, pushes_to, system_sources)
- Business Owners
- Teams (access control)

Each data contract represents a versioned contract for a specific data feed.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pycharter.db.models.base import Base


class DataContractModel(Base):
    """SQLAlchemy model for data_contracts table."""
    
    __tablename__ = "data_contracts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core identifiers
    name = Column(String(255), nullable=False)  # Contract name (e.g., "Aircraft")
    version = Column(String(50), nullable=False)  # Contract version (e.g., "1.0.0")
    status = Column(String(50), nullable=True)  # e.g., "active", "deprecated", "draft"
    
    # Foreign keys to component tables
    schema_id = Column(Integer, ForeignKey("pycharter.schemas.id", ondelete="CASCADE"), nullable=False)
    coercion_rules_id = Column(Integer, ForeignKey("pycharter.coercion_rules.id", ondelete="SET NULL"), nullable=True)
    validation_rules_id = Column(Integer, ForeignKey("pycharter.validation_rules.id", ondelete="SET NULL"), nullable=True)
    governance_rules_id = Column(Integer, ForeignKey("pycharter.governance_rules.id", ondelete="SET NULL"), nullable=True)
    metadata_id = Column(Integer, ForeignKey("pycharter.metadata_record.id", ondelete="SET NULL"), nullable=True)
    ownership_id = Column(String(255), ForeignKey("pycharter.ownership.resource_id", ondelete="SET NULL"), nullable=True)
    
    # Foreign keys to entity tables
    data_feed_id = Column(Integer, ForeignKey("pycharter.data_feeds.id", ondelete="CASCADE"), nullable=False)
    domain_id = Column(Integer, ForeignKey("pycharter.domains.id", ondelete="SET NULL"), nullable=True)
    
    # Additional contract metadata
    description = Column(Text, nullable=True)
    is_data_feed = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_data_contracts_name_version"),
        {"schema": "pycharter"},
    )
    
    # Relationships to component tables
    schema = relationship("SchemaModel", foreign_keys=[schema_id])
    coercion_rules = relationship("CoercionRulesModel", foreign_keys=[coercion_rules_id])
    validation_rules = relationship("ValidationRulesModel", foreign_keys=[validation_rules_id])
    governance_rules = relationship("GovernanceRulesModel", foreign_keys=[governance_rules_id])
    metadata_record = relationship("MetadataModel", foreign_keys=[metadata_id])
    ownership = relationship("OwnershipModel", foreign_keys=[ownership_id])
    
    # Relationships to entity tables
    data_feed = relationship("DataFeedModel", back_populates="data_contracts")
    domain = relationship("DomainModel", back_populates="data_contracts")
    
    # Relationships to join tables for many-to-many relationships
    system_pulls = relationship("DataContractSystemPull", back_populates="data_contract", cascade="all, delete-orphan")
    system_pushes = relationship("DataContractSystemPush", back_populates="data_contract", cascade="all, delete-orphan")
    system_sources = relationship("DataContractSystemSource", back_populates="data_contract", cascade="all, delete-orphan")
    business_owners = relationship("DataContractBusinessOwner", back_populates="data_contract", cascade="all, delete-orphan")
    team_access = relationship("DataContractTeamAccess", back_populates="data_contract", cascade="all, delete-orphan")
    feed_dependencies = relationship("DataFeedDependency", back_populates="data_contract", cascade="all, delete-orphan")


# Join tables for many-to-many relationships

class DataContractSystemPull(Base):
    """Join table for data_contracts and systems (pulls_from relationship)."""
    
    __tablename__ = "data_contract_system_pulls"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_contract_id = Column(Integer, ForeignKey("pycharter.data_contracts.id", ondelete="CASCADE"), nullable=False)
    system_id = Column(Integer, ForeignKey("pycharter.systems.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("data_contract_id", "system_id", name="uq_dc_system_pull"),
        {"schema": "pycharter"},
    )
    
    data_contract = relationship("DataContractModel", back_populates="system_pulls")
    system = relationship("SystemModel", back_populates="data_contracts_pull_from")


class DataContractSystemPush(Base):
    """Join table for data_contracts and systems (pushes_to relationship)."""
    
    __tablename__ = "data_contract_system_pushes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_contract_id = Column(Integer, ForeignKey("pycharter.data_contracts.id", ondelete="CASCADE"), nullable=False)
    system_id = Column(Integer, ForeignKey("pycharter.systems.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("data_contract_id", "system_id", name="uq_dc_system_push"),
        {"schema": "pycharter"},
    )
    
    data_contract = relationship("DataContractModel", back_populates="system_pushes")
    system = relationship("SystemModel", back_populates="data_contracts_push_to")


class DataContractSystemSource(Base):
    """Join table for data_contracts and systems (system_sources relationship)."""
    
    __tablename__ = "data_contract_system_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_contract_id = Column(Integer, ForeignKey("pycharter.data_contracts.id", ondelete="CASCADE"), nullable=False)
    system_id = Column(Integer, ForeignKey("pycharter.systems.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("data_contract_id", "system_id", name="uq_dc_system_source"),
        {"schema": "pycharter"},
    )
    
    data_contract = relationship("DataContractModel", back_populates="system_sources")
    system = relationship("SystemModel", back_populates="data_contracts_source")


class DataContractBusinessOwner(Base):
    """Join table for data_contracts and business_owners."""
    
    __tablename__ = "data_contract_business_owners"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_contract_id = Column(Integer, ForeignKey("pycharter.data_contracts.id", ondelete="CASCADE"), nullable=False)
    business_owner_id = Column(Integer, ForeignKey("pycharter.business_owners.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("data_contract_id", "business_owner_id", name="uq_dc_business_owner"),
        {"schema": "pycharter"},
    )
    
    data_contract = relationship("DataContractModel", back_populates="business_owners")
    business_owner = relationship("BusinessOwnerModel", back_populates="data_contract_owners")


class DataContractTeamAccess(Base):
    """Join table for data_contracts and teams (access control)."""
    
    __tablename__ = "data_contract_team_access"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_contract_id = Column(Integer, ForeignKey("pycharter.data_contracts.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("pycharter.teams.id", ondelete="CASCADE"), nullable=False)
    permission = Column(String(20), nullable=False)  # "read" or "write"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("data_contract_id", "team_id", "permission", name="uq_dc_team_access"),
        {"schema": "pycharter"},
    )
    
    data_contract = relationship("DataContractModel", back_populates="team_access")
    team = relationship("TeamModel", back_populates="read_permissions")


class DataFeedDependency(Base):
    """Join table for data_contracts and their dependencies (other data feeds)."""
    
    __tablename__ = "data_feed_dependencies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_contract_id = Column(Integer, ForeignKey("pycharter.data_contracts.id", ondelete="CASCADE"), nullable=False)
    dependency_feed_id = Column(Integer, ForeignKey("pycharter.data_feeds.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(50), nullable=True)  # e.g., "required", "optional"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("data_contract_id", "dependency_feed_id", name="uq_data_feed_dependency"),
        {"schema": "pycharter"},
    )
    
    data_contract = relationship("DataContractModel", back_populates="feed_dependencies")
    dependency_feed = relationship("DataFeedModel", foreign_keys=[dependency_feed_id])

