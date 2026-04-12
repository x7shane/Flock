"""
Flock Score Calculator — DB Integration Layer.

Reads current fundamentals from the database, runs them through the scoring
engine, and stores the results as FlockScore records with SCD2 versioning.
"""

import logging
from datetime import UTC, datetime
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.pipeline import PipelineRun
from app.models.stock import FlockScore, Fundamental
from app.services.scoring_engine import score_all_stocks

logger = logging.getLogger(__name__)

# Columns in FlockScore that carry the actual score values
SCORE_COLUMNS = [
    "score_balanced", "score_growth", "score_value", "score_conservative",
    "pillar_profitability", "pillar_growth", "pillar_health",
    "pillar_valuation", "pillar_quality",
]

# Tolerance for floating-point comparison when detecting score changes
_SCORE_TOLERANCE = 0.01


class ScoreCalculator:
    """
    Orchestrates: load fundamentals → compute scores → save with SCD2.
    """

    async def load_fundamentals(self, session: AsyncSession) -> pd.DataFrame:
        """
        Load all current Fundamental records into a DataFrame.

        Returns:
            DataFrame with one row per stock, columns matching the 16 factor
            names plus 'stock_id'. Empty DataFrame if no data exists.
        """
        result = await session.execute(
            select(Fundamental).where(Fundamental.is_current == True)  # noqa: E712
        )
        rows = result.scalars().all()

        if not rows:
            logger.warning("No current fundamentals found — scoring aborted")
            return pd.DataFrame()

        records: list[dict[str, Any]] = []
        for row in rows:
            records.append({
                "stock_id": row.stock_id,
                "roe": row.roe,
                "roce": row.roce,
                "net_profit_margin": row.net_profit_margin,
                "revenue_cagr_3yr": row.revenue_cagr_3yr,
                "eps_growth_3yr": row.eps_growth_3yr,
                "debt_equity": row.debt_equity,
                "current_ratio": row.current_ratio,
                "interest_coverage": row.interest_coverage,
                "free_cash_flow": row.free_cash_flow,
                "pe_ratio": row.pe_ratio,
                "pb_ratio": row.pb_ratio,
                "peg_ratio": row.peg_ratio,
                "dividend_yield": row.dividend_yield,
                "promoter_holding_pct": row.promoter_holding_pct,
                "promoter_pledge_pct": row.promoter_pledge_pct,
                "fii_dii_trend": row.fii_dii_trend,
            })

        logger.info("Loaded %d current fundamental records", len(records))
        return pd.DataFrame(records)

    def compute_scores(self, fundamentals_df: pd.DataFrame) -> pd.DataFrame:
        """
        Run the scoring engine on the loaded fundamentals.

        Args:
            fundamentals_df: DataFrame from load_fundamentals().

        Returns:
            DataFrame with stock_id + all score columns.
        """
        if fundamentals_df.empty:
            return pd.DataFrame()

        scores_df = score_all_stocks(fundamentals_df)
        logger.info("Computed scores for %d stocks", len(scores_df))
        return scores_df

    async def save_scores_scd2(
        self,
        session: AsyncSession,
        scores_df: pd.DataFrame,
    ) -> tuple[int, int, int]:
        """
        Save computed scores to the flock_scores table using SCD2.

        For each stock:
        - If no current FlockScore exists → INSERT new record
        - If current FlockScore exists and scores changed → close old, INSERT new
        - If current FlockScore exists and scores unchanged → skip

        Args:
            session: AsyncSession
            scores_df: DataFrame from compute_scores()

        Returns:
            Tuple of (created, updated, unchanged) counts
        """
        created = 0
        updated = 0
        unchanged = 0
        now = datetime.now(UTC)

        for _, row in scores_df.iterrows():
            stock_id = int(row["stock_id"])

            # Fetch current FlockScore for this stock
            result = await session.execute(
                select(FlockScore).where(
                    FlockScore.stock_id == stock_id,
                    FlockScore.is_current == True,  # noqa: E712
                )
            )
            current = result.scalar_one_or_none()

            # Build the new score dict
            new_scores = {col: row.get(col) for col in SCORE_COLUMNS}

            if current is None:
                # First score for this stock — insert
                flock_score = FlockScore(
                    stock_id=stock_id,
                    valid_from=now,
                    is_current=True,
                    computed_at=now,
                    **{k: v for k, v in new_scores.items() if v is not None},
                )
                session.add(flock_score)
                created += 1

            elif self._scores_changed(current, new_scores):
                # Scores changed — close old record, insert new
                current.valid_to = now
                current.is_current = False

                flock_score = FlockScore(
                    stock_id=stock_id,
                    valid_from=now,
                    is_current=True,
                    computed_at=now,
                    **{k: v for k, v in new_scores.items() if v is not None},
                )
                session.add(flock_score)
                updated += 1

            else:
                unchanged += 1

        await session.flush()
        logger.info(
            "Scores saved: %d created, %d updated, %d unchanged",
            created, updated, unchanged,
        )
        return created, updated, unchanged

    def _scores_changed(
        self,
        current: FlockScore,
        new_scores: dict[str, float | None],
    ) -> bool:
        """Compare current DB scores with newly computed scores."""
        for col in SCORE_COLUMNS:
            old_val = getattr(current, col, None)
            new_val = new_scores.get(col)

            # Both None → no change
            if old_val is None and new_val is None:
                continue

            # One is None, other isn't → changed
            if old_val is None or new_val is None:
                return True

            # Numeric comparison with tolerance
            if abs(float(old_val) - float(new_val)) > _SCORE_TOLERANCE:
                return True

        return False

    async def run(self, session: AsyncSession) -> tuple[int, int, int]:
        """
        Full scoring pipeline: load → compute → save.

        Returns:
            (created, updated, unchanged) counts
        """
        fundamentals_df = await self.load_fundamentals(session)
        scores_df = self.compute_scores(fundamentals_df)

        if scores_df.empty:
            logger.warning("No scores computed — nothing to save")
            return 0, 0, 0

        return await self.save_scores_scd2(session, scores_df)


async def run_scoring_pipeline() -> PipelineRun:
    """
    Top-level entry point: creates a PipelineRun, runs scoring, logs results.
    """
    run = PipelineRun(
        run_type="flock_score_compute",
        started_at=datetime.now(UTC),
        status="running",
        tickers_total=0,
        tickers_success=0,
        tickers_failed=0,
    )

    try:
        calculator = ScoreCalculator()

        async with async_session_factory() as session:
            created, updated, unchanged = await calculator.run(session)

            run.tickers_total = created + updated + unchanged
            run.tickers_success = created + updated + unchanged
            run.tickers_failed = 0
            run.completed_at = datetime.now(UTC)
            run.status = "completed"

            session.add(run)
            await session.commit()

        logger.info(
            "Scoring pipeline complete: %d created, %d updated, %d unchanged",
            created, updated, unchanged,
        )

    except Exception as e:
        logger.error("Scoring pipeline failed: %s", e, exc_info=True)
        run.completed_at = datetime.now(UTC)
        run.status = "failed"
        run.error_message = str(e)

        try:
            async with async_session_factory() as session:
                session.add(run)
                await session.commit()
        except Exception:
            logger.error("Failed to log pipeline error", exc_info=True)

    return run
