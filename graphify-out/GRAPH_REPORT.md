# Graph Report - /home/shades/Documents/Claude_Projects/Flock  (2026-05-10)

## Corpus Check
- 62 files · ~100,427 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 734 nodes · 1532 edges · 40 communities detected
- Extraction: 48% EXTRACTED · 52% INFERRED · 0% AMBIGUOUS · INFERRED: 791 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]

## God Nodes (most connected - your core abstractions)
1. `PipelineRun` - 94 edges
2. `Stock` - 88 edges
3. `MutualFund` - 63 edges
4. `Fundamental` - 52 edges
5. `FundamentalsFetcher` - 52 edges
6. `PriceFetcher` - 51 edges
7. `MfFetcher` - 50 edges
8. `GoldFetcher` - 41 edges
9. `StockPrice` - 35 edges
10. `MfNav` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Base` --uses--> `Gold price data.  - GoldPrice: Daily gold prices in INR per gram`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/db/base.py → /home/shades/Documents/Claude_Projects/Flock/backend/app/models/gold.py
- `Base` --uses--> `Daily Gold prices (INR per gram).`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/db/base.py → /home/shades/Documents/Claude_Projects/Flock/backend/app/models/gold.py
- `Stock` --uses--> `Database Initialization Script.  Usage:     python -m scripts.init_db [--seed]`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/models/stock.py → /home/shades/Documents/Claude_Projects/Flock/backend/scripts/init_db.py
- `Stock` --uses--> `Initialize the database.      1. Run Alembic migrations     2. Optionally seed w`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/models/stock.py → /home/shades/Documents/Claude_Projects/Flock/backend/scripts/init_db.py
- `Stock` --uses--> `Seed the database with Nifty 200 stocks.`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/models/stock.py → /home/shades/Documents/Claude_Projects/Flock/backend/scripts/init_db.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (98): Base, DailyPipeline, IncrementalPipeline, Daily Pipeline Orchestration.  Orchestrates all daily data fetches: - Stock pric, Run fundamentals fetch pipeline with SCD2., Run MF NAV fetch pipeline., Run MF NAV fetch pipeline., Run gold price fetch pipeline. (+90 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (46): calculate_flock_score(), calculate_pillar_score(), normalize_factor(), Flock Score — Fundamental Scoring Engine.  Pure math layer: no database, no asyn, Normalize a single factor value to 0-100 percentile rank.      Args:         val, Average the factor percentile scores within a pillar, excluding None values., Weighted sum of pillar scores, re-normalized if any pillar is missing.      Args, Score the entire universe of stocks from raw fundamentals.      Args:         fu (+38 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (46): Base, SQLAlchemy Declarative Base.  All ORM models inherit from this Base class. Impor, Base class for all SQLAlchemy ORM models in Flock., DeclarativeBase, SQLAlchemy ORM Models.  All models are imported here so Alembic can autodetect t, MfFetcher, Mutual Fund NAV Fetcher Service.  Fetches NAV data from mfapi.in and saves to da, Save NAV data to database.          Args:             session: AsyncSession (+38 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (31): calculate_sip_projections(), compare_sip_scenarios(), SIP (Systematic Investment Plan) Calculator.  Calculates future value projection, Compare SIP outcomes across different return scenarios.      Useful for showing, Calculate SIP future value.      Standard SIP Formula:         FV = P × [((1+r)^, Tests for SIP (Systematic Investment Plan) Calculator.  Pure math tests — no moc, Step-up SIP should include yearly breakdown., Each year's monthly amount should exceed previous year's. (+23 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (29): _calculate_statistics(), Monte Carlo Simulation Engine.  Portfolio-level Monte Carlo using Geometric Brow, Run portfolio-level Monte Carlo simulation using correlated GBM.      Args:, Simplified Monte Carlo for a single asset (no covariance needed).      Convenien, Calculate all user-facing statistics from Monte Carlo results., Validate Monte Carlo inputs., run_monte_carlo(), run_single_asset_monte_carlo() (+21 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (27): A minimal Fundamental record for testing SCD2 logic., sample_fundamental(), fetch_single_fundamentals(), FundamentalsFetcher, Fundamentals Fetcher Service with SCD2 Logic.  Fetches fundamental factors from, Check if fundamental data has actually changed.          Compares all 16 factors, Save fundamentals with SCD2 logic.          1. Get current fundamental record (i, Fetch fundamentals and save with SCD2.          Args:             session: Async (+19 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (29): get_available_crises(), Historical Stress Test Engine.  Simulates how a user's portfolio would have perf, Simulate how the user's portfolio would have performed during a crisis.      Arg, Run stress tests against ALL available crisis periods.      Returns:         Lis, Return list of available crisis scenarios for the UI., run_all_stress_tests(), run_stress_test(), _make_crisis_prices() (+21 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (34): BaseModel, list_crises(), Pydantic schemas for simulation API (Monte Carlo + Stress Test)., Request body for Monte Carlo simulation., List available crisis scenarios for stress testing., Monte Carlo output statistics., Run Monte Carlo simulation on a portfolio.      For MVP, uses synthetic return p, Monte Carlo simulation result. (+26 more)

### Community 8 - "Community 8"
Cohesion: 0.1
Nodes (28): Run Flock Score computation after data fetches complete., Flock Score Calculator — DB Integration Layer.  Reads current fundamentals from, Save computed scores to the flock_scores table using SCD2.          For each sto, Compare current DB scores with newly computed scores., Full scoring pipeline: load → compute → save.          Returns:             (cre, Top-level entry point: creates a PipelineRun, runs scoring, logs results., Orchestrates: load fundamentals → compute scores → save with SCD2., Load all current Fundamental records into a DataFrame.          Returns: (+20 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (20): BaseSettings, Flock Application Configuration.  Loads settings from environment variables (via, Application settings loaded from environment variables., Settings, mock_session(), override_settings(), Shared pytest fixtures for Flock backend tests.  Provides:   - Override settings, Force test-safe settings. Prevents real DB connections during unit tests. (+12 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (23): build_covariance_matrix(), estimate_return_parameters(), Estimate annualized expected return and volatility from historical prices., Build annualized covariance matrix from daily prices.      Args:         price_d, _make_price_dataframe(), _make_price_series(), Tests for Monte Carlo Simulation Engine.  All tests are pure math — no mocking n, Covariance matrix must be symmetric. (+15 more)

### Community 11 - "Community 11"
Cohesion: 0.18
Nodes (24): FlockScoreResponse, FundamentalsResponse, PillarScores, Pydantic schemas for Flock Score API responses., Pillar-level score breakdown., Flock Score for a single stock., Lightweight stock info for listing., Current fundamental factors for a stock — all 16 Flock factors. (+16 more)

### Community 12 - "Community 12"
Cohesion: 0.1
Nodes (14): get_db(), Async Database Session Management.  Provides:   - engine: AsyncEngine connected, Yields an async database session for a single request.      Usage in a route:, Tests for app.db.session — Session factory and get_db dependency.  These are lig, Verify the async_session_factory is properly configured., expire_on_commit=False is critical for async — prevents lazy loading errors., Verify engine is configured with sensible pool settings., pool_pre_ping=True ensures stale connections are detected before use. (+6 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (17): downgrade(), Add SCD2 tracking to fundamentals and flock_scores tables  Revision ID: scd2_fun, Add SCD2 tracking to fundamentals and flock_scores tables., Remove SCD2 tracking from fundamentals and flock_scores tables., upgrade(), do_run_migrations(), Alembic migration environment.  Configured for async SQLAlchemy with PostgreSQL., Run migrations in 'offline' mode.      This configures the context with just a U (+9 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (17): NamedTuple, get_sectors(), get_stock_by_ticker(), get_stocks_by_sector(), get_tickers(), Nifty 200 Universe - Static list of stocks.  The Nifty 200 index represents abou, Get list of all Nifty 200 tickers., Get stock info by ticker. (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.25
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 0.38
Nodes (6): init_database(), main(), Database Initialization Script.  Usage:     python -m scripts.init_db [--seed], Initialize the database.      1. Run Alembic migrations     2. Optionally seed w, Seed the database with Nifty 200 stocks., seed_nifty_200()

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (4): main(), Seed Nifty 200 Stocks.  Usage:     python -m scripts.seed_stocks  This script po, Seed the database with Nifty 200 stocks., seed_stocks()

### Community 18 - "Community 18"
Cohesion: 0.5
Nodes (3): health_check(), Flock API — Application Entrypoint.  Run with:     uvicorn app.main:app --reload, Liveness probe for monitoring and deployment health checks.

### Community 19 - "Community 19"
Cohesion: 0.5
Nodes (1): Initial schema: stocks, mutual_funds, prices, fundamentals, scores  Revision ID:

### Community 20 - "Community 20"
Cohesion: 0.83
Nodes (3): closeMobileNav(), openMobileNav(), toggleMobileNav()

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Parse CORS_ORIGINS string into a list.

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): get_db should yield an AsyncSession-compatible object.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): If an exception is raised inside the dependency, rollback must be called.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Current fundamental factors for a stock — all 16 Flock factors.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Yields an async database session for a single request.      Usage in a route:

## Knowledge Gaps
- **184 isolated node(s):** `Flock API — Application Entrypoint.  Run with:     uvicorn app.main:app --reload`, `Liveness probe for monitoring and deployment health checks.`, `Flock Application Configuration.  Loads settings from environment variables (via`, `Application settings loaded from environment variables.`, `Parse CORS_ORIGINS string into a list.` (+179 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 21`** (2 nodes): `fetchJSON()`, `api.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Parse CORS_ORIGINS string into a list.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `get_db should yield an AsyncSession-compatible object.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `If an exception is raised inside the dependency, rollback must be called.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Current fundamental factors for a stock — all 16 Flock factors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Yields an async database session for a single request.      Usage in a route:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Stock` connect `Community 0` to `Community 2`, `Community 5`, `Community 8`, `Community 9`, `Community 11`, `Community 16`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `PipelineRun` connect `Community 0` to `Community 8`, `Community 2`, `Community 5`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `run_monte_carlo()` connect `Community 4` to `Community 7`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Are the 90 inferred relationships involving `PipelineRun` (e.g. with `Base` and `SQLAlchemy ORM Models.  All models are imported here so Alembic can autodetect t`) actually correct?**
  _`PipelineRun` has 90 INFERRED edges - model-reasoned connections that need verification._
- **Are the 84 inferred relationships involving `Stock` (e.g. with `Stocks API — list Nifty 200 universe.` and `List stocks in the Nifty 200 universe with their current Flock Score.      Reads`) actually correct?**
  _`Stock` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `MutualFund` (e.g. with `Base` and `SQLAlchemy ORM Models.  All models are imported here so Alembic can autodetect t`) actually correct?**
  _`MutualFund` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `Fundamental` (e.g. with `Stocks API — list Nifty 200 universe.` and `List stocks in the Nifty 200 universe with their current Flock Score.      Reads`) actually correct?**
  _`Fundamental` has 48 INFERRED edges - model-reasoned connections that need verification._