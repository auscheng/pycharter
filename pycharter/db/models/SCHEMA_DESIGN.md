# Database Schema Design

## Overview

This document describes the database schema for PyCharter, which manages data contracts and their associated metadata, rules, and relationships.

## Core Architecture

The schema is organized into:
1. **Component Tables**: Store the actual contract components (schema, rules, metadata, ownership)
2. **Entity Tables**: Store reference entities (systems, data feeds, business owners, domains, teams)
3. **Data Contract Table**: Central join table that links all components and entities together
4. **Join Tables**: Many-to-many relationship tables

## Entity Tables

### 1. Systems (`systems`)
Represents external systems that data feeds interact with.

**Purpose**: Track systems that data feeds pull from, push to, or use as sources.

**Fields**:
- `id` (PK)
- `name` (unique) - e.g., "NetlineOpsReplica", "SCR", "Fleetwise"
- `description`
- `system_type` - e.g., "database", "api", "data_warehouse"
- `connection_info` - Connection details (JSON string)
- `is_active`
- `created_at`, `updated_at`

**Relationships**:
- Many-to-many with `data_contracts` via:
  - `data_contract_system_pulls` (pulls_from)
  - `data_contract_system_pushes` (pushes_to)
  - `data_contract_system_sources` (system_sources)

### 2. Data Feeds (`data_feeds`)
Represents data feeds (datasets) that are served.

**Purpose**: Each data feed can have multiple versions (data contracts).

**Fields**:
- `id` (PK)
- `name` (unique) - e.g., "Aircraft", "Airport", "Operator"
- `title`
- `description`
- `feed_type` - e.g., "Operational", "Analytical", "Reference"
- `is_active`
- `created_at`, `updated_at`

**Relationships**:
- One-to-many with `data_contracts` (each feed has multiple contract versions)
- Many-to-many with itself via `data_feed_dependencies` (dependencies)

### 3. Business Owners (`business_owners`)
Represents business owners or stakeholders responsible for data feeds.

**Purpose**: Track who owns/manages each data feed.

**Fields**:
- `id` (PK)
- `name` (unique) - e.g., "IOC", "Product Team", "Data Engineering"
- `description`
- `contact_email`
- `department`
- `is_active`
- `created_at`, `updated_at`

**Relationships**:
- Many-to-many with `data_contracts` via `data_contract_business_owners`

### 4. Domains (`domains`)
Represents business domains that data feeds belong to.

**Purpose**: Organize data feeds by business domain.

**Fields**:
- `id` (PK)
- `name` (unique) - e.g., "NetlineOps configuration", "Flight Operations"
- `description`
- `parent_domain_id` (FK to domains) - For hierarchical domains
- `is_active`
- `created_at`, `updated_at`

**Relationships**:
- One-to-many with `data_contracts`
- Self-referential (parent/child domains)

### 5. Teams (`teams`)
Represents teams that have access control permissions for data contracts.

**Purpose**: Manage read/write access permissions.

**Fields**:
- `id` (PK)
- `name` (unique) - e.g., "operations-team", "data-team"
- `description`
- `team_type` - e.g., "engineering", "operations", "data"
- `is_active`
- `created_at`, `updated_at`

**Relationships**:
- Many-to-many with `data_contracts` via `data_contract_team_access` (with permission type: read/write)

## Component Tables (Existing)

### 1. Schemas (`schemas`)
Stores JSON Schema definitions.

### 2. Coercion Rules (`coercion_rules`)
Stores coercion rules for data transformation.

### 3. Validation Rules (`validation_rules`)
Stores validation rules beyond standard JSON Schema.

### 4. Governance Rules (`governance_rules`)
Stores governance policies (data retention, PII, access control).

### 5. Metadata (`metadata_record`)
Stores additional metadata (generic resource metadata).

**Note**: Table is named `metadata_record` instead of `metadata` because `metadata` is a reserved word in SQLAlchemy.

### 6. Ownership (`ownership`)
Stores ownership information (owner, team, additional info).

## Central Join Table

### Data Contracts (`data_contracts`)
**Purpose**: Central table that links all components and entities together. Each row represents a versioned data contract for a specific data feed.

**Fields**:
- `id` (PK)
- `name` - Contract name (e.g., "Aircraft")
- `version` - Contract version (e.g., "1.0.0")
- `status` - e.g., "active", "deprecated", "draft"
- `schema_id` (FK to schemas) - **Required**
- `coercion_rules_id` (FK to coercion_rules) - Optional
- `validation_rules_id` (FK to validation_rules) - Optional
- `governance_rules_id` (FK to governance_rules) - Optional
- `metadata_id` (FK to metadata_record) - Optional
- `ownership_id` (FK to ownership) - Optional
- `data_feed_id` (FK to data_feeds) - **Required**
- `domain_id` (FK to domains) - Optional
- `description`
- `is_data_feed`
- `created_at`, `updated_at`, `created_by`, `updated_by`

**Unique Constraint**: `(name, version)`

**Relationships**:
- One-to-one with `schemas` (required)
- One-to-one with `coercion_rules` (optional)
- One-to-one with `validation_rules` (optional)
- One-to-one with `governance_rules` (optional)
- One-to-one with `metadata_record` (optional)
- One-to-one with `ownership` (optional)
- Many-to-one with `data_feeds` (required)
- Many-to-one with `domains` (optional)
- Many-to-many with `systems` via join tables
- Many-to-many with `business_owners` via join table
- Many-to-many with `teams` via join table
- One-to-many with `data_feed_dependencies`

## Join Tables

### 1. Data Contract System Pulls (`data_contract_system_pulls`)
Links data contracts to systems they pull from.

### 2. Data Contract System Pushes (`data_contract_system_pushes`)
Links data contracts to systems they push to.

### 3. Data Contract System Sources (`data_contract_system_sources`)
Links data contracts to their system sources.

### 4. Data Contract Business Owners (`data_contract_business_owners`)
Links data contracts to their business owners.

### 5. Data Contract Team Access (`data_contract_team_access`)
Links data contracts to teams with access permissions (read/write).

### 6. Data Feed Dependencies (`data_feed_dependencies`)
Links data contracts to their dependencies (other data feeds).

## Example Usage

### Creating a Data Contract

```python
# 1. Create or get entities
system = SystemModel(name="NetlineOpsReplica", system_type="database")
data_feed = DataFeedModel(name="Aircraft", feed_type="Operational")
business_owner = BusinessOwnerModel(name="IOC")
domain = DomainModel(name="NetlineOps configuration")
team = TeamModel(name="operations-team")

# 2. Create component records
schema = SchemaModel(name="Aircraft", version="1.0.0", schema_data={...})
coercion_rules = CoercionRulesModel(schema_id=schema.id, rules={...})
validation_rules = ValidationRulesModel(schema_id=schema.id, rules={...})
governance_rules = GovernanceRulesModel(name="aircraft_governance", rule_definition={...})
metadata = MetadataModel(resource_id="aircraft", resource_type="schema", metadata_data={...})
ownership = OwnershipModel(resource_id="aircraft", owner="IOC", team="data-engineering")

# 3. Create data contract
data_contract = DataContractModel(
    name="Aircraft",
    version="1.0.0",
    status="active",
    schema_id=schema.id,
    coercion_rules_id=coercion_rules.id,
    validation_rules_id=validation_rules.id,
    governance_rules_id=governance_rules.id,
    metadata_id=metadata.id,
    ownership_id=ownership.resource_id,
    data_feed_id=data_feed.id,
    domain_id=domain.id,
    is_data_feed=True
)

# 4. Create join table records
DataContractSystemPull(data_contract_id=data_contract.id, system_id=system.id)
DataContractBusinessOwner(data_contract_id=data_contract.id, business_owner_id=business_owner.id)
DataContractTeamAccess(data_contract_id=data_contract.id, team_id=team.id, permission="read")
```

## Benefits of This Design

1. **Normalization**: Entities are stored once and referenced, avoiding duplication
2. **Flexibility**: Easy to add new relationships without changing core tables
3. **Queryability**: Can easily query "all contracts that pull from system X" or "all contracts owned by business owner Y"
4. **Versioning**: Each data contract is versioned, allowing multiple versions per data feed
5. **Audit Trail**: Created/updated timestamps and user tracking
6. **Referential Integrity**: Foreign keys ensure data consistency

## Migration Path

When migrating existing data:
1. Create entity records for all unique values in metadata
2. Create data feed records
3. Create data contract records linking to existing component records
4. Create join table records based on metadata relationships

