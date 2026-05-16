# Database Management Scripts

## Setup

### Quick Start

```bash
# Start PostgreSQL and run all setup steps
./scripts/setup_database.sh --seed
```

### Manual Steps

1. **Start PostgreSQL** (Docker):
   ```bash
   cd /home/shades/Documents/Claude_Projects/Flock
   docker compose up -d db
   ```

2. **Run Migrations**:
   ```bash
   cd backend
   source venv/bin/activate
   python -m scripts.run_migrations
   ```

3. **Seed Nifty 200 Stocks**:
   ```bash
   python -m scripts.seed_stocks
   ```

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_migrations.py` | Run Alembic migrations | `python -m scripts.run_migrations` |
| `seed_stocks.py` | Populate Nifty 200 stocks | `python -m scripts.seed_stocks` |
| `init_db.py` | Combined init + optional seed | `python -m scripts.init_db --seed` |
| `setup_database.sh` | Full setup (Docker + migrations + seed) | `./scripts/setup_database.sh --seed` |

## Database Schema

The database includes the following tables:

| Table | Purpose |
|-------|---------|
| `stocks` | Nifty 200 stock universe (ticker, company, sector) |
| `stock_prices` | Daily OHLCV price data |
| `fundamentals` | 16 fundamental factors (SCD2 versioned) |
| `flock_scores` | Pre-computed Flock scores (SCD2 versioned) |
| `mutual_funds` | Mutual fund schemes |
| `mf_navs` | Daily NAV data |
| `gold_prices` | Daily gold prices |
| `pipeline_runs` | Data pipeline execution logs |
| `alembic_version` | Migration version tracking |

## Connection Details

- **Host**: localhost:5432
- **Database**: flock_db
- **Username**: flock
- **Password**: flock_password
- **Connection String**: `postgresql+asyncpg://flock:flock_password@localhost:5432/flock_db`

## Verification

```bash
# Check stock count
PGPASSWORD=flock_password psql -h localhost -U flock -d flock_db \
  -c "SELECT COUNT(*) FROM stocks;"

# Check migrations
PGPASSWORD=flock_password psql -h localhost -U flock -d flock_db \
  -c "SELECT * FROM alembic_version;"
```
