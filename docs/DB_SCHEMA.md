# Flock Database Schema

> **Draft Version:** 0.1
> **Engine:** PostgreSQL 16
> **ORM:** SQLAlchemy (Async)

## Design Principles
1. **Soft Deletes:** Records are flagged `is_active = false`, rarely deleted.
2. **Audit Trails:** `created_at` and `updated_at` on all mutable tables.
3. **Data Integrity:** Strict foreign keys and unique constraints to prevent duplication.

---

## 1. Domain: Entities & Metadata

### `stocks`
Stores the universe of Indian equities (Nifty 200).
- `id` (PK, Serial)
- `ticker` (VARCHAR, Unique, e.g., 'RELIANCE.NS')
- `company_name` (VARCHAR)
- `sector` (VARCHAR)
- `industry` (VARCHAR)
- `is_active` (BOOLEAN, default: true)
- `created_at`, `updated_at`

### `mutual_funds`
Stores the curated list of Index Funds.
- `id` (PK, Serial)
- `scheme_code` (VARCHAR, Unique, e.g., '119551')
- `scheme_name` (VARCHAR)
- `category` (VARCHAR)
- `is_active` (BOOLEAN)
- `created_at`, `updated_at`

---

## 2. Domain: Market Data

### `stock_prices`
Daily OHLCV. High frequency table.
- `id` (PK, BigSerial)
- `stock_id` (FK -> stocks.id)
- `date` (DATE)
- `open`, `high`, `low`, `close`, `adj_close` (NUMERIC)
- `volume` (BIGINT)
- **Constraint:** `UNIQUE (stock_id, date)`
- **Index:** `(stock_id, date DESC)`

### `mf_navs`
Daily mutual fund NAVs.
- `id` (PK, BigSerial)
- `fund_id` (FK -> mutual_funds.id)
- `date` (DATE)
- `nav` (NUMERIC)
- **Constraint:** `UNIQUE (fund_id, date)`

### `gold_prices`
Daily Gold prices (INR per gram).
- `id` (PK, BigSerial)
- `date` (DATE, Unique)
- `price_per_gram_inr` (NUMERIC)
- `fetched_at` (TIMESTAMP)

---

## 3. Domain: Advanced Analytics

### `fundamentals`
1-to-1 with `stocks`. Contains the 16 factors needed for the Flock Score.
- `id` (PK, Serial)
- `stock_id` (FK -> stocks.id, Unique)
- `roe`, `roce`, `pe_ratio`, `debt_equity`, `dividend_yield`, ... (NUMERIC)
- `fetched_at` (TIMESTAMP)

### `flock_scores`
Pre-computed scores based on the fundamental factors.
- `id` (PK, Serial)
- `stock_id` (FK -> stocks.id, Unique)
- `score_balanced`, `score_growth`, `score_value`, `score_conservative` (NUMERIC)
- `pillar_profitability`, `pillar_growth`, ... (NUMERIC)
- `computed_at` (TIMESTAMP)

---

## 4. Domain: System Monitoring

### `pipeline_runs`
Logs the execution of data pipeline jobs.
- `id` (PK, Serial)
- `run_type` (VARCHAR: 'prices', 'fundamentals', etc)
- `started_at`, `completed_at` (TIMESTAMP)
- `status` (VARCHAR)
- `tickers_total`, `tickers_success`, `tickers_failed` (INTEGER)
- `error_message` (TEXT)
