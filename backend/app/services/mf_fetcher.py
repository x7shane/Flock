"""
Mutual Fund NAV Fetcher Service.

Fetches NAV data from mfapi.in and saves to database.
"""

import asyncio
import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

import httpx
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.mutual_fund import MfNav, MutualFund
from app.models.pipeline import PipelineRun

# mfapi.in free API for Indian MF NAV data
MFAPI_BASE_URL = "https://api.mfapi.in/mf"


class MfFetcher:
    """Fetches Mutual Fund NAV data from mfapi.in."""

    RATE_LIMIT_DELAY = 0.5  # seconds between requests

    def __init__(self):
        self._last_request_time: float = 0.0

    async def _rate_limit(self) -> None:
        """Apply rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch_mf_nav(self, scheme_code: str) -> dict[str, Any] | None:
        """
        Fetch NAV data for a mutual fund scheme.

        Args:
            scheme_code: AMFI scheme code (e.g., "120503")

        Returns:
            Dict with NAV data, or None if fetch failed
        """
        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{MFAPI_BASE_URL}/{scheme_code}")
                if response.status_code != 200:
                    return None

                data = response.json()

                if "data" not in data or not data["data"]:
                    return None

                # Get the latest NAV
                latest = data["data"][0]
                return {
                    "scheme_code": scheme_code,
                    "scheme_name": data.get("meta", {}).get("scheme_name", ""),
                    "nav": float(latest["nav"]),
                    "date": datetime.strptime(latest["date"], "%d-%m-%Y").date(),
                    "fetched_at": datetime.now(UTC),
                }

        except Exception as e:
            logger.error("[MfFetcher] Failed to fetch NAV for scheme %s: %s", scheme_code, e)
            return None

    async def fetch_mf_nav_history(
        self,
        scheme_code: str,
        days: int = 30,
    ) -> list[dict[str, Any]] | None:
        """
        Fetch NAV history for a mutual fund scheme.

        Args:
            scheme_code: AMFI scheme code
            days: Number of days to fetch

        Returns:
            List of NAV records, or None if fetch failed
        """
        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{MFAPI_BASE_URL}/{scheme_code}")
                if response.status_code != 200:
                    return None

                data = response.json()

                if "data" not in data or not data["data"]:
                    return None

                # Parse all NAV records
                nav_records = []
                cutoff_date = date.today() - timedelta(days=days)

                for item in data["data"]:
                    try:
                        nav_date = datetime.strptime(item["date"], "%d-%m-%Y").date()
                        if nav_date >= cutoff_date:
                            nav_records.append({
                                "scheme_code": scheme_code,
                                "nav": float(item["nav"]),
                                "date": nav_date,
                            })
                    except (ValueError, KeyError):
                        continue

                return nav_records

        except Exception as e:
            logger.error("[MfFetcher] Failed to fetch NAV history for scheme %s: %s", scheme_code, e)
            return None

    async def save_mf_nav(
        self,
        session: AsyncSession,
        fund: MutualFund,
        nav_records: list[dict],
    ) -> int:
        """
        Bulk-save NAV records using INSERT … ON CONFLICT DO NOTHING.

        Args:
            session: AsyncSession
            fund: MutualFund model instance
            nav_records: List of {date, nav} dicts

        Returns:
            Number of rows actually inserted (may be < len(nav_records) on re-runs)
        """
        if not nav_records:
            return 0

        rows = [
            {"fund_id": fund.id, "date": r["date"], "nav": float(r["nav"])}
            for r in nav_records
        ]

        result = await session.execute(
            text("""
                INSERT INTO mf_navs (fund_id, date, nav)
                VALUES (:fund_id, :date, :nav)
                ON CONFLICT (fund_id, date) DO NOTHING
            """),
            rows,
        )
        return result.rowcount if result.rowcount is not None else len(rows)

    async def fetch_and_save(
        self,
        session: AsyncSession,
        scheme_code: str,
    ) -> tuple[bool, int, str | None]:
        """
        Incrementally fetch NAV history and save to database.

        Checks the latest NAV date already stored for this fund and fetches
        only the missing days forward to today.  For funds with no history,
        falls back to a 365-day initial load.  Uses a single bulk upsert.

        Args:
            session: AsyncSession
            scheme_code: AMFI scheme code

        Returns:
            (success, records_inserted, error_message)
        """
        # Get fund from database
        fund_result = await session.execute(
            select(MutualFund).where(MutualFund.scheme_code == scheme_code)
        )
        fund = fund_result.scalar_one_or_none()
        if not fund:
            return False, 0, f"Fund {scheme_code} not found in database"

        # Find the last NAV date already stored
        last_result = await session.execute(
            select(func.max(MfNav.date)).where(MfNav.fund_id == fund.id)
        )
        last_date: date | None = last_result.scalar()

        today = date.today()
        if last_date is None:
            days = 365  # initial load
        else:
            days = (today - last_date).days

        if days <= 0:
            return True, 0, None  # already up-to-date

        # Fetch NAV history for the needed window
        nav_history = await self.fetch_mf_nav_history(scheme_code, days=days)
        if nav_history is None:
            return False, 0, f"No NAV data returned for {scheme_code}"

        # Bulk upsert — single round-trip, skips existing dates
        inserted = await self.save_mf_nav(session, fund, nav_history)
        return True, inserted, None


async def run_mf_nav_pipeline() -> PipelineRun:
    """
    Run MF NAV fetch pipeline for all active funds in the database.

    Reads the list of active schemes from the mutual_funds table — no
    hardcoded scheme codes.  Each fund is fetched incrementally (only
    missing days since the last stored NAV date) and uses its own
    short-lived session to avoid Neon idle timeouts.

    Returns:
        PipelineRun with results
    """
    # First, load active scheme codes from the database
    async with async_session_factory() as lookup_session:
        result = await lookup_session.execute(
            select(MutualFund.scheme_code).where(MutualFund.is_active == True)  # noqa: E712
        )
        scheme_codes: list[str] = [row[0] for row in result.all()]

    if not scheme_codes:
        logger.warning("[MfFetcher] No active mutual funds found in database. Seed mutual_funds first.")
        return PipelineRun(
            run_type="mf_nav_fetch",
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            status="completed",
            tickers_total=0,
            tickers_success=0,
            tickers_failed=0,
            error_message="No active funds in mutual_funds table",
        )

    fetcher = MfFetcher()
    run = PipelineRun(
        run_type="mf_nav_fetch",
        started_at=datetime.now(UTC),
        status="running",
        tickers_total=len(scheme_codes),
        tickers_success=0,
        tickers_failed=0,
    )

    # Persist the initial run record
    async with async_session_factory() as init_session:
        init_session.add(run)
        await init_session.commit()
        await init_session.refresh(run)
        run_id = run.id

    success_count = 0
    failed_count = 0
    errors: list[str] = []

    for scheme_code in scheme_codes:
        # Fresh session per fund — keeps connections short-lived for Neon
        async with async_session_factory() as session:
            success, _, error = await fetcher.fetch_and_save(session, scheme_code)
            await session.commit()

        if success:
            success_count += 1
        else:
            failed_count += 1
            if error:
                errors.append(f"{scheme_code}: {error}")

    # Update the run record with final counts
    async with async_session_factory() as final_session:
        result = await final_session.execute(
            select(PipelineRun).where(PipelineRun.id == run_id)
        )
        run = result.scalar_one()
        run.tickers_success = success_count
        run.tickers_failed = failed_count
        run.completed_at = datetime.now(UTC)

        if failed_count == 0:
            run.status = "completed"
        elif success_count == 0:
            run.status = "failed"
            run.error_message = "\n".join(errors[:10])
        else:
            run.status = "partial"
            run.error_message = "\n".join(errors[:10])

        await final_session.commit()

    return run


async def search_mf_schemes(query: str) -> list[dict[str, Any]]:
    """
    Search for mutual fund schemes.

    Args:
        query: Search query (e.g., "HDFC", "Nifty 50")

    Returns:
        List of matching schemes
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("https://api.mfapi.in/mf")
            if response.status_code != 200:
                return []

            data = response.json()
            results = []

            for item in data:
                if query.lower() in item.get("schemeName", "").lower():
                    results.append({
                        "scheme_code": item.get("schemeCode"),
                        "scheme_name": item.get("schemeName"),
                    })

            return results[:20]  # Return top 20 matches

    except Exception:
        return []