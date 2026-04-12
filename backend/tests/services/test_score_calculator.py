"""
Tests for Flock Score Calculator — DB Integration Layer.

Uses mocked AsyncSession to test:
- Loading fundamentals from DB
- SCD2 save logic (create/update/skip)
"""

import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.score_calculator import ScoreCalculator, SCORE_COLUMNS


class TestLoadFundamentals:
    """Tests for loading current fundamentals from the database."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_data(self):
        """Empty DB → empty DataFrame."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        calculator = ScoreCalculator()
        df = await calculator.load_fundamentals(mock_session)
        assert df.empty

    @pytest.mark.asyncio
    async def test_loads_current_records(self):
        """Should load all current fundamental records into DataFrame."""
        # Create a mock Fundamental row
        mock_fundamental = MagicMock()
        mock_fundamental.stock_id = 1
        mock_fundamental.roe = 0.15
        mock_fundamental.roce = 0.18
        mock_fundamental.net_profit_margin = 0.12
        mock_fundamental.revenue_cagr_3yr = 0.20
        mock_fundamental.eps_growth_3yr = 0.15
        mock_fundamental.debt_equity = 0.45
        mock_fundamental.current_ratio = 2.1
        mock_fundamental.interest_coverage = 8.5
        mock_fundamental.free_cash_flow = 5000000.0
        mock_fundamental.pe_ratio = 22.5
        mock_fundamental.pb_ratio = 3.2
        mock_fundamental.peg_ratio = 1.1
        mock_fundamental.dividend_yield = 0.015
        mock_fundamental.promoter_holding_pct = 55.0
        mock_fundamental.promoter_pledge_pct = 2.0
        mock_fundamental.fii_dii_trend = 0.05

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_fundamental]
        mock_session.execute = AsyncMock(return_value=mock_result)

        calculator = ScoreCalculator()
        df = await calculator.load_fundamentals(mock_session)

        assert len(df) == 1
        assert df.iloc[0]["stock_id"] == 1
        assert df.iloc[0]["roe"] == 0.15
        assert df.iloc[0]["pe_ratio"] == 22.5


class TestSaveScoresScd2:
    """Tests for SCD2 score persistence."""

    @pytest.mark.asyncio
    async def test_creates_new_score(self):
        """First score for a stock → INSERT."""
        import pandas as pd

        scores_df = pd.DataFrame([{
            "stock_id": 1,
            "score_balanced": 65.0,
            "score_growth": 60.0,
            "score_value": 70.0,
            "score_conservative": 68.0,
            "pillar_profitability": 72.0,
            "pillar_growth": 55.0,
            "pillar_health": 80.0,
            "pillar_valuation": 58.0,
            "pillar_quality": 45.0,
        }])

        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous
        # No existing FlockScore
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        calculator = ScoreCalculator()
        created, updated, unchanged = await calculator.save_scores_scd2(
            mock_session, scores_df
        )

        assert created == 1
        assert updated == 0
        assert unchanged == 0
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_unchanged_score(self):
        """Same scores → no insert, count as unchanged."""
        import pandas as pd

        scores_df = pd.DataFrame([{
            "stock_id": 1,
            "score_balanced": 65.0,
            "score_growth": 60.0,
            "score_value": 70.0,
            "score_conservative": 68.0,
            "pillar_profitability": 72.0,
            "pillar_growth": 55.0,
            "pillar_health": 80.0,
            "pillar_valuation": 58.0,
            "pillar_quality": 45.0,
        }])

        # Existing FlockScore with same values
        existing = MagicMock()
        existing.score_balanced = 65.0
        existing.score_growth = 60.0
        existing.score_value = 70.0
        existing.score_conservative = 68.0
        existing.pillar_profitability = 72.0
        existing.pillar_growth = 55.0
        existing.pillar_health = 80.0
        existing.pillar_valuation = 58.0
        existing.pillar_quality = 45.0

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute = AsyncMock(return_value=mock_result)

        calculator = ScoreCalculator()
        created, updated, unchanged = await calculator.save_scores_scd2(
            mock_session, scores_df
        )

        assert created == 0
        assert updated == 0
        assert unchanged == 1
        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_updates_changed_score(self):
        """Changed scores → close old record, insert new."""
        import pandas as pd

        scores_df = pd.DataFrame([{
            "stock_id": 1,
            "score_balanced": 70.0,  # Changed from 65 → 70
            "score_growth": 60.0,
            "score_value": 70.0,
            "score_conservative": 68.0,
            "pillar_profitability": 72.0,
            "pillar_growth": 55.0,
            "pillar_health": 80.0,
            "pillar_valuation": 58.0,
            "pillar_quality": 45.0,
        }])

        # Existing FlockScore with different balanced score
        existing = MagicMock()
        existing.score_balanced = 65.0  # Old value
        existing.score_growth = 60.0
        existing.score_value = 70.0
        existing.score_conservative = 68.0
        existing.pillar_profitability = 72.0
        existing.pillar_growth = 55.0
        existing.pillar_health = 80.0
        existing.pillar_valuation = 58.0
        existing.pillar_quality = 45.0
        existing.is_current = True
        existing.valid_to = None

        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute = AsyncMock(return_value=mock_result)

        calculator = ScoreCalculator()
        created, updated, unchanged = await calculator.save_scores_scd2(
            mock_session, scores_df
        )

        assert created == 0
        assert updated == 1
        assert unchanged == 0

        # Old record should be closed
        assert existing.is_current is False
        assert existing.valid_to is not None

        # New record should be added
        mock_session.add.assert_called_once()
