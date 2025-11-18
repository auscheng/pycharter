"""Initial schema

Revision ID: ac3d8fcc3e60
Revises: 
Create Date: 2025-11-18 17:13:51.669324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac3d8fcc3e60'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create schemas table
    op.create_table(
        'schemas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('schema_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'version', name='uq_schemas_name_version')
    )
    
    # Create governance_rules table
    op.create_table(
        'governance_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rule_definition', sa.JSON(), nullable=False),
        sa.Column('schema_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['schema_id'], ['schemas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create ownership table
    op.create_table(
        'ownership',
        sa.Column('resource_id', sa.String(length=255), nullable=False),
        sa.Column('owner', sa.String(length=255), nullable=False),
        sa.Column('team', sa.String(length=255), nullable=True),
        sa.Column('additional_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('resource_id')
    )
    
    # Create metadata table
    op.create_table(
        'metadata',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('metadata_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resource_id', 'resource_type', name='uq_metadata_resource')
    )
    
    # Create coercion_rules table
    op.create_table(
        'coercion_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('schema_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('rules', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['schema_id'], ['schemas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('schema_id', 'version', name='uq_coercion_rules_schema_version')
    )
    
    # Create validation_rules table
    op.create_table(
        'validation_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('schema_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('rules', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['schema_id'], ['schemas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('schema_id', 'version', name='uq_validation_rules_schema_version')
    )
    
    # Create indexes
    op.create_index('idx_schemas_name', 'schemas', ['name'], unique=False)
    op.create_index('idx_schemas_version', 'schemas', ['version'], unique=False)
    op.create_index('idx_governance_schema_id', 'governance_rules', ['schema_id'], unique=False)
    op.create_index('idx_metadata_resource', 'metadata', ['resource_id', 'resource_type'], unique=False)
    op.create_index('idx_coercion_schema_id', 'coercion_rules', ['schema_id'], unique=False)
    op.create_index('idx_coercion_version', 'coercion_rules', ['version'], unique=False)
    op.create_index('idx_validation_schema_id', 'validation_rules', ['schema_id'], unique=False)
    op.create_index('idx_validation_version', 'validation_rules', ['version'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_validation_version', table_name='validation_rules')
    op.drop_index('idx_validation_schema_id', table_name='validation_rules')
    op.drop_index('idx_coercion_version', table_name='coercion_rules')
    op.drop_index('idx_coercion_schema_id', table_name='coercion_rules')
    op.drop_index('idx_metadata_resource', table_name='metadata')
    op.drop_index('idx_governance_schema_id', table_name='governance_rules')
    op.drop_index('idx_schemas_version', table_name='schemas')
    op.drop_index('idx_schemas_name', table_name='schemas')
    
    # Drop tables (in reverse order due to foreign keys)
    op.drop_table('validation_rules')
    op.drop_table('coercion_rules')
    op.drop_table('metadata')
    op.drop_table('ownership')
    op.drop_table('governance_rules')
    op.drop_table('schemas')
