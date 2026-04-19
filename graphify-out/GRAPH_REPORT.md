# Graph Report - /home/shades/Documents/Claude_Projects/Flock  (2026-04-20)

## Corpus Check
- 57 files · ~30,855 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 682 nodes · 1373 edges · 37 communities detected
- Extraction: 51% EXTRACTED · 49% INFERRED · 0% AMBIGUOUS · INFERRED: 668 edges (avg confidence: 0.59)
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

## God Nodes (most connected - your core abstractions)
1. `PipelineRun` - 81 edges
2. `Stock` - 63 edges
3. `MutualFund` - 54 edges
4. `PriceFetcher` - 51 edges
5. `MfFetcher` - 50 edges
6. `FundamentalsFetcher` - 49 edges
7. `Fundamental` - 43 edges
8. `GoldFetcher` - 41 edges
9. `MfNav` - 31 edges
10. `StockPrice` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Gold price data.  - GoldPrice: Daily gold prices in INR per gram` --uses--> `Base`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/models/gold.py → /home/shades/Documents/Claude_Projects/Flock/backend/app/db/base.py
- `Daily Gold prices (INR per gram).` --uses--> `Base`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/models/gold.py → /home/shades/Documents/Claude_Projects/Flock/backend/app/db/base.py
- `Audit log for data pipeline executions.` --uses--> `Base`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/app/models/pipeline.py → /home/shades/Documents/Claude_Projects/Flock/backend/app/db/base.py
- `If no existing fundamental, a new record with is_current=True is created.` --uses--> `Fundamental`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/tests/services/test_fundamentals_fetcher.py → /home/shades/Documents/Claude_Projects/Flock/backend/app/models/stock.py
- `If data hasn't changed, no new record should be inserted.` --uses--> `Fundamental`  [INFERRED]
  /home/shades/Documents/Claude_Projects/Flock/backend/tests/services/test_fundamentals_fetcher.py → /home/shades/Documents/Claude_Projects/Flock/backend/app/models/stock.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (76): Base, mock_session(), override_settings(), Shared pytest fixtures for Flock backend tests.  Provides:   - Override settings, Force test-safe settings. Prevents real DB connections during unit tests., A MagicMock that mimics an AsyncSession.      execute() returns a mock scalars-c, A minimal Stock ORM object for testing., A minimal Fundamental record for testing SCD2 logic. (+68 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (46): calculate_flock_score(), calculate_pillar_score(), normalize_factor(), Flock Score — Fundamental Scoring Engine.  Pure math layer: no database, no asyn, Normalize a single factor value to 0-100 percentile rank.      Args:         val, Average the factor percentile scores within a pillar, excluding None values., Weighted sum of pillar scores, re-normalized if any pillar is missing.      Args, Score the entire universe of stocks from raw fundamentals.      Args:         fu (+38 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (51): Base, SQLAlchemy Declarative Base.  All ORM models inherit from this Base class. Impor, Base class for all SQLAlchemy ORM models in Flock., DeclarativeBase, SQLAlchemy ORM Models.  All models are imported here so Alembic can autodetect t, MfFetcher, Mutual Fund NAV Fetcher Service.  Fetches NAV data from mfapi.in and saves to da, Save NAV data to database.          Args:             session: AsyncSession (+43 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (46): BaseModel, FlockScoreResponse, PillarScores, Pydantic schemas for Flock Score API responses., Pillar-level score breakdown., Flock Score for a single stock., Lightweight stock info for listing., StockListItem (+38 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (31): calculate_sip_projections(), compare_sip_scenarios(), SIP (Systematic Investment Plan) Calculator.  Calculates future value projection, Compare SIP outcomes across different return scenarios.      Useful for showing, Calculate SIP future value.      Standard SIP Formula:         FV = P × [((1+r)^, Tests for SIP (Systematic Investment Plan) Calculator.  Pure math tests — no moc, Step-up SIP should include yearly breakdown., Each year's monthly amount should exceed previous year's. (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (29): _calculate_statistics(), Monte Carlo Simulation Engine.  Portfolio-level Monte Carlo using Geometric Brow, Run portfolio-level Monte Carlo simulation using correlated GBM.      Args:, Simplified Monte Carlo for a single asset (no covariance needed).      Convenien, Calculate all user-facing statistics from Monte Carlo results., Validate Monte Carlo inputs., run_monte_carlo(), run_single_asset_monte_carlo() (+21 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (29): get_available_crises(), Historical Stress Test Engine.  Simulates how a user's portfolio would have perf, Simulate how the user's portfolio would have performed during a crisis.      Arg, Run stress tests against ALL available crisis periods.      Returns:         Lis, Return list of available crisis scenarios for the UI., run_all_stress_tests(), run_stress_test(), _make_crisis_prices() (+21 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (31): get_gold_price_history(), GoldFetcher, Gold Price Fetcher Service.  Fetches gold price data from yfinance (GC=F for gol, Save gold price to database.          Args:             session: AsyncSession, Fetch gold price and save to database.          Args:             session: Async, Run gold price fetch pipeline.      Returns:         PipelineRun with results, Get gold price history from database.      Args:         days: Number of days to, Fetches gold price data from yfinance (GC=F × INR=X → INR/gram). (+23 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (23): build_covariance_matrix(), estimate_return_parameters(), Estimate annualized expected return and volatility from historical prices., Build annualized covariance matrix from daily prices.      Args:         price_d, _make_price_dataframe(), _make_price_series(), Tests for Monte Carlo Simulation Engine.  All tests are pure math — no mocking n, Covariance matrix must be symmetric. (+15 more)

### Community 9 - "Community 9"
Cohesion: 0.1
Nodes (25): Flock Score Calculator — DB Integration Layer.  Reads current fundamentals from, Save computed scores to the flock_scores table using SCD2.          For each sto, Compare current DB scores with newly computed scores., Full scoring pipeline: load → compute → save.          Returns:             (cre, Top-level entry point: creates a PipelineRun, runs scoring, logs results., Orchestrates: load fundamentals → compute scores → save with SCD2., Load all current Fundamental records into a DataFrame.          Returns:, Run the scoring engine on the loaded fundamentals.          Args:             fu (+17 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (14): fetch_single_fundamentals(), FundamentalsFetcher, run_fundamentals_pipeline(), Tests for FundamentalsFetcher service — specifically SCD2 version tracking logic, If no existing fundamental, a new record with is_current=True is created., If data hasn't changed, no new record should be inserted., When data changes, old record is closed (is_current=False) and new is inserted., Values > 1 are assumed to be percentages and should be divided by 100. (+6 more)

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (11): BaseSettings, Flock Application Configuration.  Loads settings from environment variables (via, Application settings loaded from environment variables., Settings, Tests for app.core.config — Settings loading and parsing., Verify default values when no env vars are set., Verify CORS_ORIGINS string → list conversion., Verify environment variables override defaults. (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.1
Nodes (14): get_db(), Async Database Session Management.  Provides:   - engine: AsyncEngine connected, Yields an async database session for a single request.      Usage in a route:, Tests for app.db.session — Session factory and get_db dependency.  These are lig, Verify the async_session_factory is properly configured., expire_on_commit=False is critical for async — prevents lazy loading errors., Verify engine is configured with sensible pool settings., pool_pre_ping=True ensures stale connections are detected before use. (+6 more)

### Community 13 - "Community 13"
Cohesion: 0.2
Nodes (9): NamedTuple, get_sectors(), get_stock_by_ticker(), get_stocks_by_sector(), Nifty 200 Universe - Static list of stocks.  The Nifty 200 index represents abou, Get stock info by ticker., Get stocks filtered by sector., Get list of unique sectors. (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.22
Nodes (9): do_run_migrations(), Alembic migration environment.  Configured for async SQLAlchemy with PostgreSQL., Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations with a connection., Run migrations in 'online' mode with async engine., Run migrations in 'online' mode., run_async_migrations(), run_migrations_offline() (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.25
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (5): downgrade(), Add SCD2 tracking to fundamentals and flock_scores tables  Revision ID: scd2_fun, Add SCD2 tracking to fundamentals and flock_scores tables., Remove SCD2 tracking from fundamentals and flock_scores tables., upgrade()

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (3): health_check(), Flock API — Application Entrypoint.  Run with:     uvicorn app.main:app --reload, Liveness probe for monitoring and deployment health checks.

### Community 18 - "Community 18"
Cohesion: 0.5
Nodes (1): Initial schema: stocks, mutual_funds, prices, fundamentals, scores  Revision ID:

### Community 19 - "Community 19"
Cohesion: 0.83
Nodes (3): closeMobileNav(), openMobileNav(), toggleMobileNav()

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (0): 

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
Nodes (1): Parse CORS_ORIGINS string into a list.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

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
Nodes (1): get_db should yield an AsyncSession-compatible object.

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): If an exception is raised inside the dependency, rollback must be called.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **175 isolated node(s):** `Flock API — Application Entrypoint.  Run with:     uvicorn app.main:app --reload`, `Liveness probe for monitoring and deployment health checks.`, `Flock Application Configuration.  Loads settings from environment variables (via`, `Application settings loaded from environment variables.`, `Parse CORS_ORIGINS string into a list.` (+170 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 20`** (2 nodes): `fetchJSON()`, `api.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Parse CORS_ORIGINS string into a list.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `__init__.py`
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
- **Thin community `Community 34`** (1 nodes): `get_db should yield an AsyncSession-compatible object.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `If an exception is raised inside the dependency, rollback must be called.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PipelineRun` connect `Community 0` to `Community 9`, `Community 2`, `Community 10`, `Community 7`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `score_all_stocks()` connect `Community 1` to `Community 9`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `ScoreCalculator` connect `Community 9` to `Community 0`, `Community 2`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `PipelineRun` (e.g. with `Base` and `SQLAlchemy ORM Models.  All models are imported here so Alembic can autodetect t`) actually correct?**
  _`PipelineRun` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `Stock` (e.g. with `SQLAlchemy ORM Models.  All models are imported here so Alembic can autodetect t` and `Base`) actually correct?**
  _`Stock` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `MutualFund` (e.g. with `Base` and `SQLAlchemy ORM Models.  All models are imported here so Alembic can autodetect t`) actually correct?**
  _`MutualFund` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `PriceFetcher` (e.g. with `PipelineRun` and `Stock`) actually correct?**
  _`PriceFetcher` has 42 INFERRED edges - model-reasoned connections that need verification._