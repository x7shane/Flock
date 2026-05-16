"""Add SCD2 tracking to fundamentals and flock_scores tables

Revision ID: scd2_fundamentals_flock
Revises: 09908929e295
Create Date: 2026-04-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'scd2_fundamentals_flock'
down_revision: Union[str, Sequence[str], None] = '09908929e295'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add SCD2 tracking to fundamentals and flock_scores tables."""

    # ========================================
    # FUNDAMENTALS TABLE
    # ========================================

    # Step 1: Drop the existing unique constraint on stock_id
    # Note: PostgreSQL auto-generated name has '_key' suffix
    op.drop_constraint('fundamentals_stock_id_key', 'fundamentals', type_='unique')

    # Step 2: Add SCD2 columns (nullable first to allow existing rows)
    op.add_column('fundamentals', sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True))
    op.add_column('fundamentals', sa.Column('valid_to', sa.DateTime(timezone=True), nullable=True))
    op.add_column('fundamentals', sa.Column('is_current', sa.Boolean(), nullable=True))

    # Step 3: Populate existing records with SCD2 defaults
    # Use fetched_at as valid_from for existing records
    op.execute(text("""
        UPDATE fundamentals
        SET valid_from = fetched_at,
            valid_to = NULL,
            is_current = TRUE
        WHERE valid_from IS NULL
    """))

    # Step 4: Make columns non-nullable
    op.alter_column('fundamentals', 'valid_from', nullable=False)
    op.alter_column('fundamentals', 'is_current', nullable=False)

    # Step 5: Add new unique constraint and index
    op.create_unique_constraint('uq_fundamentals_stock_valid_from', 'fundamentals', ['stock_id', 'valid_from'])
    op.create_index('ix_fundamentals_current', 'fundamentals', ['stock_id', 'is_current'])

    # ========================================
    # FLOCK_SCORES TABLE
    # ========================================

    # Step 1: Drop the existing unique constraint on stock_id
    # Note: PostgreSQL auto-generated name has '_key' suffix
    op.drop_constraint('flock_scores_stock_id_key', 'flock_scores', type_='unique')

    # Step 2: Add SCD2 columns (nullable first to allow existing rows)
    op.add_column('flock_scores', sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True))
    op.add_column('flock_scores', sa.Column('valid_to', sa.DateTime(timezone=True), nullable=True))
    op.add_column('flock_scores', sa.Column('is_current', sa.Boolean(), nullable=True))

    # Step 3: Populate existing records with SCD2 defaults
    # Use computed_at as valid_from for existing records
    op.execute(text("""
        UPDATE flock_scores
        SET valid_from = computed_at,
            valid_to = NULL,
            is_current = TRUE
        WHERE valid_from IS NULL
    """))

    # Step 4: Make columns non-nullable
    op.alter_column('flock_scores', 'valid_from', nullable=False)
    op.alter_column('flock_scores', 'is_current', nullable=False)

    # Step 5: Add new unique constraint and index
    op.create_unique_constraint('uq_flock_scores_stock_valid_from', 'flock_scores', ['stock_id', 'valid_from'])
    op.create_index('ix_flock_scores_current', 'flock_scores', ['stock_id', 'is_current'])


def downgrade() -> None:
    """Remove SCD2 tracking from fundamentals and flock_scores tables."""

    # ========================================
    # FLOCK_SCORES TABLE (reverse order)
    # ========================================

    # Drop SCD2 indexes and constraints
    op.drop_index('ix_flock_scores_current', table_name='flock_scores')
    op.drop_constraint('uq_flock_scores_stock_valid_from', 'flock_scores', type_='unique')

    # Drop SCD2 columns
    op.drop_column('flock_scores', 'is_current')
    op.drop_column('flock_scores', 'valid_to')
    op.drop_column('flock_scores', 'valid_from')

    # Restore original unique constraint on stock_id
    op.create_unique_constraint('flock_scores_stock_id_key', 'flock_scores', ['stock_id'])

    # ========================================
    # FUNDAMENTALS TABLE (reverse order)
    # ========================================

    # Drop SCD2 indexes and constraints
    op.drop_index('ix_fundamentals_current', table_name='fundamentals')
    op.drop_constraint('uq_fundamentals_stock_valid_from', 'fundamentals', type_='unique')

    # Drop SCD2 columns
    op.drop_column('fundamentals', 'is_current')
    op.drop_column('fundamentals', 'valid_to')
    op.drop_column('fundamentals', 'valid_from')

    # Restore original unique constraint on stock_id
    op.create_unique_constraint('fundamentals_stock_id_key', 'fundamentals', ['stock_id'])