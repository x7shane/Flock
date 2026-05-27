"""
Seed Mutual Funds from mfapi.in.

Fetches the full scheme catalogue from mfapi.in and seeds the
mutual_funds table with popular index funds / ETFs.

NO hardcoded scheme codes — funds are discovered dynamically
by matching scheme names against curated category keywords.

Usage:
    python -m scripts.seed_mutual_funds               # Seed all categories
    python -m scripts.seed_mutual_funds --dry-run     # Print matches, no DB write
    python -m scripts.seed_mutual_funds --category "Nifty 50"  # Single category

Categories seeded:
    - Nifty 50 Index
    - Nifty Next 50 Index
    - Nifty 100 Index
    - Nifty 200 Index
    - Nifty 500 Index
    - Nifty Midcap 150 Index
    - Nifty Smallcap 250 Index
    - Nifty Bank Index
    - Nifty IT Index
    - Nifty Pharma Index
    - S&P BSE Sensex Index
    - Gold ETF / FoF
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.core.config import settings
from app.db.session import async_session_factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed_mf")

MFAPI_ALL_SCHEMES_URL = "https://api.mfapi.in/mf"

# ---------------------------------------------------------------------------
# Category definitions — each entry maps a human-readable category name to
# a list of keyword patterns.  A scheme must match ALL keywords in a tuple
# (AND logic), and any tuple in the list is sufficient (OR logic between
# tuples).  Matching is case-insensitive against the scheme name.
# ---------------------------------------------------------------------------
CATEGORIES: dict[str, list[tuple[str, ...]]] = {
    "Nifty 50 Index": [
        ("nifty 50", "index"),
        ("nifty50", "index"),
        ("nifty 50", "etf"),
        ("nifty50", "etf"),
    ],
    "Nifty Next 50 Index": [
        ("nifty next 50", "index"),
        ("nifty next 50", "etf"),
        ("niftynext50",),
        ("junior nifty",),
        ("nifty jr",),
    ],
    "Nifty 100 Index": [
        ("nifty 100", "index"),
        ("nifty100", "index"),
    ],
    "Nifty 200 Index": [
        ("nifty 200", "index"),
        ("nifty200", "index"),
    ],
    "Nifty 500 Index": [
        ("nifty 500", "index"),
        ("nifty500", "index"),
    ],
    "Nifty Midcap 150 Index": [
        ("nifty midcap 150", "index"),
        ("midcap150", "index"),
        ("nifty midcap150",),
    ],
    "Nifty Smallcap 250 Index": [
        ("nifty smallcap 250", "index"),
        ("smallcap250", "index"),
        ("nifty smallcap250",),
    ],
    "Nifty Bank Index": [
        ("bank nifty", "index"),
        ("banknifty", "index"),
        ("nifty bank", "index"),
        ("bank nifty", "etf"),
        ("banknifty", "etf"),
    ],
    "Nifty IT Index": [
        ("nifty it", "index"),
        ("nifty it", "etf"),
    ],
    "Nifty Pharma Index": [
        ("nifty pharma", "index"),
        ("nifty pharma", "etf"),
    ],
    "S&P BSE Sensex Index": [
        ("sensex", "index"),
        ("sensex", "etf"),
        ("bse sensex",),
    ],
    "Gold ETF / FoF": [
        ("gold", "etf"),
        ("gold", "fund of fund"),
        ("gold", "fof"),
        ("goldbees",),
        ("gold bees",),
    ],
}

# Keywords that disqualify a scheme — removes IDCW variants, old re-listings,
# and duplicate plan types so we keep roughly one representative fund per AMC.
EXCLUDE_KEYWORDS: list[str] = [
    # Income / dividend variants (we only want Growth / direct growth)
    " idcw",
    "idcw ",
    "dividend reinvestment",
    "dividend payout",
    "dividend option",
    "weekly",
    "monthly",
    # Gold FoF duplicates — keep ETF itself, skip FoF wrappers
    "gold etf fund of fund",
    "gold etf fof",
    "gold fof",
    "gold and silver",          # mixed commodity, not pure gold
    "world gold",               # overseas fund, not INR gold
    # Old names / re-listed funds from defunct AMCs
    "goldman sachs",
    "benchmark exchange",
    # Regular plan noise — prefer Direct where both exist
    # (we include both but exclude the most verbose duplicates)
    "regular plan - idcw",
    "direct plan - idcw",
]


def _matches_category(name_lower: str, patterns: list[tuple[str, ...]]) -> bool:
    """Return True if the scheme name matches any pattern tuple."""
    for keyword_set in patterns:
        if all(kw in name_lower for kw in keyword_set):
            return True
    return False


def _is_excluded(name_lower: str) -> bool:
    """Return True if the scheme should be skipped (noise)."""
    return any(kw in name_lower for kw in EXCLUDE_KEYWORDS)


def _detect_category(scheme_name: str) -> str | None:
    """
    Return the first matching category for a scheme name, or None.

    Checks categories in the order defined in CATEGORIES.
    """
    name_lower = scheme_name.lower()
    if _is_excluded(name_lower):
        return None
    for category, patterns in CATEGORIES.items():
        if _matches_category(name_lower, patterns):
            return category
    return None


async def fetch_all_schemes() -> list[dict]:
    """
    Fetch the complete scheme list from mfapi.in.

    Returns:
        List of {schemeCode, schemeName} dicts.
    """
    logger.info("Fetching full scheme list from %s ...", MFAPI_ALL_SCHEMES_URL)
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(MFAPI_ALL_SCHEMES_URL)
        response.raise_for_status()
        data = response.json()

    logger.info("Received %d total schemes from mfapi.in", len(data))
    return data


def discover_funds(
    all_schemes: list[dict],
    category_filter: str | None = None,
) -> list[dict]:
    """
    Filter schemes into matched index fund records.

    Args:
        all_schemes: Raw list from mfapi.in
        category_filter: If given, only return funds for this category.

    Returns:
        List of {scheme_code, scheme_name, category} dicts, deduplicated.
    """
    seen_codes: set[str] = set()
    matched: list[dict] = []

    for item in all_schemes:
        code = str(item.get("schemeCode", "")).strip()
        name = item.get("schemeName", "").strip()
        if not code or not name:
            continue

        category = _detect_category(name)
        if category is None:
            continue
        if category_filter and category != category_filter:
            continue
        if code in seen_codes:
            continue

        seen_codes.add(code)
        matched.append({
            "scheme_code": code,
            "scheme_name": name,
            "category": category,
        })

    # Sort for a deterministic, readable output
    matched.sort(key=lambda x: (x["category"], x["scheme_name"]))
    return matched


async def seed_funds(funds: list[dict], dry_run: bool = False) -> None:
    """
    Upsert discovered funds into the mutual_funds table.

    Existing records are updated (name/category may have changed).
    New records are inserted with is_active=True.
    """
    if dry_run:
        print("\n  [DRY RUN] Would insert/update the following funds:\n")
        for f in funds:
            print(f"  {f['scheme_code']:8s}  {f['category']:30s}  {f['scheme_name']}")
        print(f"\n  Total: {len(funds)} funds — nothing written to DB.\n")
        return

    async with async_session_factory() as session:
        # Bulk upsert — ON CONFLICT updates name and category in case they changed
        await session.execute(
            text("""
                INSERT INTO mutual_funds (scheme_code, scheme_name, category, is_active, created_at, updated_at)
                VALUES (:scheme_code, :scheme_name, :category, true, NOW(), NOW())
                ON CONFLICT (scheme_code) DO UPDATE SET
                    scheme_name = EXCLUDED.scheme_name,
                    category    = EXCLUDED.category,
                    is_active   = true,
                    updated_at  = NOW()
            """),
            funds,
        )
        await session.commit()

    logger.info("Seeded %d mutual fund records into DB.", len(funds))


async def run(dry_run: bool = False, category_filter: str | None = None) -> None:
    """Main seeding flow."""
    # 1. Fetch full catalogue
    all_schemes = await fetch_all_schemes()

    # 2. Discover index funds by keyword matching
    funds = discover_funds(all_schemes, category_filter=category_filter)

    if not funds:
        logger.warning("No funds matched. Check your category filter or keyword patterns.")
        return

    # 3. Print summary
    from collections import Counter
    counts = Counter(f["category"] for f in funds)
    print(f"\n  {'CATEGORY':<35} {'FUNDS':>5}")
    print(f"  {'-'*42}")
    for cat, n in sorted(counts.items()):
        print(f"  {cat:<35} {n:>5}")
    print(f"  {'-'*42}")
    print(f"  {'TOTAL':<35} {len(funds):>5}\n")

    # 4. Seed (or dry-run)
    await seed_funds(funds, dry_run=dry_run)

    if not dry_run:
        # 5. Verify
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM mutual_funds WHERE is_active = true")
            )
            total = result.scalar()
        print(f"  ✅ mutual_funds table now has {total} active funds.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed mutual funds from mfapi.in")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print matched funds without writing to the database",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        metavar="NAME",
        help='Only seed a specific category, e.g. "Nifty 50 Index"',
    )
    args = parser.parse_args()

    asyncio.run(run(dry_run=args.dry_run, category_filter=args.category))


if __name__ == "__main__":
    main()
