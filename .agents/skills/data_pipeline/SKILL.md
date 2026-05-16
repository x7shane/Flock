---
name: data_pipeline
description: >
  Data Agent — owns the entire data lifecycle for Flock. Fetching from external
  sources (yfinance, jugaad-data, mfapi.in), caching, cleaning, validation,
  and storing in PostgreSQL.
---

# Data Pipeline Agent — Flock's Data Backbone

> **RULE:** No external API call without a timeout. No data insertion without validation.
> No cache read without a staleness check. Never serve stale data silently.

---

## 1. Data Source Reference

### 1.1 Stock Prices — yfinance

```python
import yfinance as yf

# Single stock — always append .NS for NSE
df = yf.download("RELIANCE.NS", start="2021-01-01", end="2024-12-31", timeout=30)

# Batch fetch (more efficient)
tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
df = yf.download(tickers, start="2021-01-01", end="2024-12-31",
                 group_by="ticker", timeout=30, threads=True)
```

- Use `Adj Close` for return calculations (accounts for splits/dividends)
- Rate: ~2,000 requests/hour. Add 0.5s delay between calls.
- Always set `timeout=30`

### 1.2 Stock Fundamentals — yfinance .info

```python
ticker = yf.Ticker("RELIANCE.NS")
info = ticker.info

fundamentals = {
    "roe": info.get("returnOnEquity"),
    "pe_ratio": info.get("trailingPE"),
    "pb_ratio": info.get("priceToBook"),
    "peg_ratio": info.get("pegRatio"),
    "dividend_yield": info.get("dividendYield"),
    "debt_equity": info.get("debtToEquity"),
    "current_ratio": info.get("currentRatio"),
    "profit_margins": info.get("profitMargins"),
    "revenue_growth": info.get("revenueGrowth"),
    "earnings_growth": info.get("earningsGrowth"),
    "free_cashflow": info.get("freeCashflow"),
    "market_cap": info.get("marketCap"),
    "sector": info.get("sector"),
}
```

> [!WARNING]
> `.info` calls are SLOW (~1-2s per ticker). For 200 stocks = 3-6 minutes. Always pre-fetch and cache in DB.

### 1.3 Mutual Fund NAVs — mfapi.in

```python
import requests
response = requests.get("https://api.mfapi.in/mf/119551", timeout=15)
data = response.json()  # {"meta": {...}, "data": [{"date": "...", "nav": "..."}, ...]}
```

**Key Index Fund Scheme Codes:**

| Fund | Code |
|---|---|
| SBI Nifty 50 Index | 119551 |
| UTI Nifty 50 Index | 120716 |
| HDFC Nifty Next 50 | 135657 |
| Motilal Oswal Midcap 150 | 147649 |
| Nippon Smallcap 250 | 148187 |

### 1.4 Gold Data

```python
gold_usd = yf.download("GC=F", start="2021-01-01", timeout=30)
usdinr = yf.download("INR=X", start="2021-01-01", timeout=30)
gold_per_gram_inr = (gold_usd["Close"] * usdinr["Close"]) / 31.1035
```

---

## 2. Pipeline Architecture

```
[Scheduled Trigger: Daily 7 PM IST]
    ↓
[Fetch] → yfinance prices + fundamentals + mfapi NAVs + gold
    ↓
[Validate] → NaN check, High>=Low, outlier detection, date sorting
    ↓
[Clean] → Forward-fill gaps (1-2 days max), Adj Close normalization
    ↓
[Store] → Upsert to PostgreSQL with cache timestamps
    ↓
[Post-Process] → Recalculate Flock Scores + covariance matrix
```

### Fetcher Base Pattern

```python
from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    SOURCE_NAME: str = "unknown"
    DEFAULT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY_BASE: float = 1.0

    @abstractmethod
    async def fetch(self, **kwargs) -> pd.DataFrame:
        pass

    async def fetch_with_retry(self, **kwargs):
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self.fetch(**kwargs)
                if result is not None and not result.empty:
                    return result
            except Exception as e:
                delay = self.RETRY_DELAY_BASE * (2 ** attempt)
                logger.warning(f"[{self.SOURCE_NAME}] Attempt {attempt+1} failed: {e}")
                await asyncio.sleep(delay)
        return None
```

---

## 3. Data Validation Rules

### Price Validation

| Rule | Check | Action |
|---|---|---|
| Close must exist | `df["Close"].isna()` | Log warning, skip row |
| High >= Low | `df["High"] < df["Low"]` | Log warning, flag for review |
| Volume > 0 | `df["Volume"] == 0` | Allow up to 5 days (holidays) |
| Single-day move >20% | `pct_change().abs() > 0.20` | Verify if split/bonus, don't auto-discard |
| Dates sorted | `index.is_monotonic_increasing` | Sort if not |

### Fundamental Validation Ranges

| Field | Expected Range | Notes |
|---|---|---|
| pe_ratio | 0 — 500 | High-growth stocks can exceed 100 |
| pb_ratio | 0 — 100 | |
| roe | -1.0 — 2.0 | -100% to 200% |
| debt_equity | 0 — 1000 | |
| current_ratio | 0 — 50 | |
| dividend_yield | 0 — 0.30 | 0-30% |

---

## 4. Database Schema

See `data_pipeline/schema.sql` for the full DDL. Core tables:

| Table | Purpose | Key Columns |
|---|---|---|
| `stocks` | Universe master | ticker, company_name, sector, is_active |
| `stock_prices` | Daily OHLCV | stock_id, date, open/high/low/close/adj_close/volume |
| `fundamentals` | Latest snapshot per stock | stock_id, all 16 factors, fetched_at |
| `mutual_funds` | MF scheme master | scheme_code, scheme_name, category |
| `mf_navs` | Daily NAV history | fund_id, date, nav |
| `gold_prices` | Daily gold INR/gram | date, price_per_gram_inr |
| `flock_scores` | Pre-computed scores | stock_id, score per preset, pillar scores |
| `pipeline_runs` | Audit log | run_type, status, tickers_success/failed, warnings |

**Key indexes:** `stock_prices(stock_id, date DESC)`, `mf_navs(fund_id, date DESC)`, `flock_scores(score_balanced DESC)`

---

## 5. Caching & Refresh Strategy

| Data Type | Refresh | Why |
|---|---|---|
| Stock prices | Daily 7 PM IST | Market closes 3:30 PM, allow settlement |
| Fundamentals | Weekly (Saturday) | Changes quarterly, weekly is plenty |
| MF NAVs | Daily 11 PM IST | AMCs publish evening |
| Gold | Daily 7 PM IST | With stock prices |
| Flock Scores | After fundamentals refresh | Depends on fundamentals |
| Covariance matrix | Weekly | Stable enough for MVP |

### Staleness Check

```python
def is_data_stale(fetched_at: datetime, max_age_hours: int = 24) -> bool:
    return (datetime.utcnow() - fetched_at) > timedelta(hours=max_age_hours)
```

If stale, serve cached + show warning: *"Data last updated X hours ago."*

---

## 6. Rate Limiting

```python
class RateLimiter:
    def __init__(self, calls_per_second: float = 2.0):
        self.delay = 1.0 / calls_per_second
        self._last_call = 0

    async def wait(self):
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_call
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self._last_call = asyncio.get_event_loop().time()
```

---

## 7. Error Handling Principles

1. **One ticker failing must NOT crash the pipeline.** Wrap each in try/except.
2. **Partial success is OK.** 195/200 is "partial", not "failed".
3. **Always serve something.** Failed fetch → serve cache + staleness warning.
4. **Rate limit yourself.** Better to run 5min longer than get IP-banned.
5. **Log everything** to `pipeline_runs` table.
6. **Never delete historical data.** Only append or update.

---

## Data Agent Operating Rules

1. **Never call external APIs in request handlers.** All data pre-fetched, served from PostgreSQL.
2. **Validate before insert.** Always run validation checks before DB upsert.
3. **Handle market holidays gracefully.** No new data on non-weekend ≠ failure.
4. **Coordinate with Quant Agent.** After data refresh, trigger score recalculation.
5. **Nifty 200 ticker list:** Maintain as static CSV, update quarterly on rebalance.
