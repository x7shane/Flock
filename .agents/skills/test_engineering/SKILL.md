---
name: test_engineering
description: >
  Test Agent — writes and maintains automated tests for the Flock project.
  Covers unit tests, integration tests, and API tests. Ensures coverage meets
  quality gates before Code Reviewer Agent approves any PR.
---

# Test Engineering Agent — Skill File

## Role

The Test Agent writes, maintains, and runs automated tests for every component of Flock. It works alongside the Code Reviewer Agent — the Reviewer won't approve a PR until the Test Agent confirms adequate coverage. The Test Agent does NOT review code quality (that's the Reviewer's job). It focuses exclusively on **verifying behavior through tests**.

---

## Testing Stack

| Tool | Purpose | Why |
|---|---|---|
| **pytest** | Test runner + framework | Industry standard for Python. Fixture system, parametrize, plugins. |
| **pytest-asyncio** | Async test support | FastAPI routes and data fetchers are async. |
| **pytest-cov** | Coverage reporting | Tracks which lines/branches are tested. |
| **httpx** | Async HTTP client for API tests | FastAPI's recommended test client via `AsyncClient`. |
| **factory-boy** | Test data factories | Generate realistic test objects without manual construction. |
| **freezegun** | Time mocking | Financial calculations depend on dates — need deterministic time. |
| **pytest-mock** | Mocking utilities | Mock external APIs (yfinance, jugaad-data) to avoid network calls. |

---

## Test Structure

### Directory Layout

```
Flock/backend/tests/
├── conftest.py                  ← Shared fixtures (DB session, test client, mock data)
├── factories/                   ← Factory-boy factories for test data
│   ├── __init__.py
│   ├── stock_factory.py         ← Creates realistic Stock objects
│   ├── price_factory.py         ← Creates OHLCV price records
│   └── fund_factory.py          ← Creates mutual fund NAV records
├── unit/                        ← Unit tests (no DB, no network, fast)
│   ├── test_scoring.py          ← Flock Score calculation logic
│   ├── test_monte_carlo.py      ← Monte Carlo simulation math
│   ├── test_historical_sim.py   ← Historical stress test logic
│   ├── test_factors.py          ← Individual factor calculations (ROE, ROCE, etc.)
│   └── test_sip_calculator.py   ← SIP calculation math
├── integration/                 ← Integration tests (uses DB, mocked external APIs)
│   ├── test_data_pipeline.py    ← Fetcher → cleaner → DB insert flow
│   ├── test_scoring_pipeline.py ← Raw data → factors → score end-to-end
│   └── test_simulation_flow.py  ← Portfolio input → simulation → output
├── api/                         ← API endpoint tests (uses test HTTP client)
│   ├── test_stock_endpoints.py  ← GET /api/v1/stocks, GET /api/v1/stocks/{ticker}
│   ├── test_score_endpoints.py  ← GET /api/v1/score/{ticker}
│   ├── test_simulate_endpoint.py ← POST /api/v1/simulate
│   └── test_health.py           ← GET /health
└── fixtures/                    ← Static test data files
    ├── sample_ohlcv.csv         ← Known price data for deterministic tests
    ├── sample_fundamentals.json ← Known fundamental data
    └── crisis_periods.json      ← Crisis period definitions for stress tests
```

### Naming Conventions

| Convention | Example |
|---|---|
| Test files: `test_<module>.py` | `test_scoring.py` |
| Test functions: `test_<what>_<condition>_<expected>` | `test_roe_calculation_with_negative_equity_returns_zero` |
| Fixture functions: descriptive noun | `sample_portfolio`, `mock_yfinance_response` |
| Factory classes: `<Model>Factory` | `StockFactory`, `PriceFactory` |

---

## Test Types & When to Use

### Unit Tests (80% of all tests)

**What**: Test a single function or class in isolation. No DB, no network, no filesystem.
**Speed**: Milliseconds per test.
**When**: Every calculation, transformation, validation function.

```python
# Example: Testing ROE factor calculation
def test_roe_calculation_normal_case():
    """ROE = Net Income / Shareholder Equity"""
    result = calculate_roe(net_income=50_000, shareholder_equity=200_000)
    assert result == 0.25  # 25%

def test_roe_calculation_negative_equity_returns_none():
    """Negative equity means the ratio is meaningless."""
    result = calculate_roe(net_income=50_000, shareholder_equity=-100_000)
    assert result is None

def test_roe_calculation_zero_equity_returns_none():
    """Avoid division by zero."""
    result = calculate_roe(net_income=50_000, shareholder_equity=0)
    assert result is None
```

### Integration Tests (15% of all tests)

**What**: Test multiple components working together. May use a test database.
**Speed**: Seconds per test.
**When**: Data pipeline flows, scoring pipeline, simulation pipeline.

```python
# Example: Testing the scoring pipeline end-to-end
async def test_scoring_pipeline_produces_valid_score(db_session, sample_stock_data):
    """Given raw fundamentals, the scoring pipeline should produce a 0-100 score."""
    # Insert sample data
    await insert_fundamentals(db_session, sample_stock_data)
    
    # Run scoring
    score = await calculate_flock_score("RELIANCE", preset="balanced")
    
    assert 0 <= score <= 100
    assert isinstance(score, float)
```

### API Tests (5% of all tests)

**What**: Test HTTP endpoints end-to-end via the FastAPI test client.
**Speed**: Seconds per test.
**When**: Every API route.

```python
# Example: Testing stock list endpoint
async def test_get_stocks_returns_list(client):
    response = await client.get("/api/v1/stocks")
    assert response.status_code == 200
    data = response.json()
    assert "stocks" in data
    assert isinstance(data["stocks"], list)

async def test_get_stocks_with_invalid_sort_returns_422(client):
    response = await client.get("/api/v1/stocks?sort=invalid_field")
    assert response.status_code == 422
```

---

## Coverage Requirements

### Quality Gates

| Metric | Minimum | Target |
|---|---|---|
| **Overall line coverage** | 80% | 90% |
| **Scoring engine coverage** | 95% | 100% |
| **Monte Carlo engine coverage** | 90% | 95% |
| **API endpoint coverage** | 85% | 95% |
| **Data pipeline coverage** | 75% | 85% |

### What MUST Be Tested (Non-Negotiable)

1. **Every factor calculation** (all 16 factors in the Flock Score)
2. **Every scoring preset** (Balanced, Growth, Value, Conservative)
3. **Monte Carlo output ranges** (VaR, max drawdown, percentile returns)
4. **Historical stress test** (all 5 crisis periods)
5. **Every API endpoint** (happy path + at least 2 error cases)
6. **SIP calculator** (monthly flow math)
7. **Data validation** (NaN handling, missing data, corrupt input)

### What Can Skip Tests (For Now)

- Static HTML/CSS/JS (frontend) — visual testing is manual for MVP
- Configuration loading — simple enough to verify by inspection
- Third-party library internals — we trust yfinance/numpy, we test our usage of them

---

## Fixture & Mock Patterns

### External API Mocking (Critical)

**Rule: Tests NEVER call real external APIs.** All yfinance, jugaad-data, mfapi.in calls are mocked.

```python
# conftest.py — Mock yfinance for all tests
@pytest.fixture
def mock_yfinance(mocker):
    """Mock yfinance.download to return deterministic OHLCV data."""
    mock_data = pd.DataFrame({
        'Open': [100.0, 101.0, 99.5],
        'High': [102.0, 103.0, 101.0],
        'Low': [99.0, 100.0, 98.5],
        'Close': [101.5, 99.5, 100.0],
        'Volume': [1000000, 1200000, 900000]
    }, index=pd.date_range('2024-01-01', periods=3))
    
    mocker.patch('yfinance.download', return_value=mock_data)
    return mock_data
```

### Database Fixtures

```python
# conftest.py — Test database that rolls back after each test
@pytest.fixture
async def db_session():
    """Create a test DB session that rolls back after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()
```

### Financial Test Data

```python
# factories/stock_factory.py
class StockFactory(factory.Factory):
    class Meta:
        model = StockFundamentals
    
    ticker = factory.Sequence(lambda n: f"STOCK{n:03d}")
    roe = factory.Faker('pyfloat', min_value=0.05, max_value=0.35)
    roce = factory.Faker('pyfloat', min_value=0.08, max_value=0.40)
    debt_equity = factory.Faker('pyfloat', min_value=0.0, max_value=2.0)
    pe_ratio = factory.Faker('pyfloat', min_value=5.0, max_value=80.0)
    market_cap = factory.Faker('pyfloat', min_value=1e9, max_value=1e13)
```

---

## Test Execution

### Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests (fast)
pytest tests/unit/

# Run a specific test file
pytest tests/unit/test_scoring.py

# Run tests matching a pattern
pytest -k "test_roe"

# Run with verbose output
pytest -v

# Run async tests
pytest --asyncio-mode=auto
```

### CI Integration (When Ready)

Tests run automatically on every PR via the Git Agent's workflow:
1. PR opened → Test suite triggered
2. All tests must pass (zero failures)
3. Coverage must meet minimum thresholds
4. Results reported back to the PR

---

## Test Agent Operating Rules

1. **Write tests BEFORE or ALONGSIDE code, never after.** Test-first ensures testable design.
2. **Tests must be deterministic.** No random seeds without `np.random.seed()`. No time-dependent tests without `freezegun`.
3. **Tests must be independent.** Running tests in any order produces the same result.
4. **Tests must be fast.** The full unit test suite should complete in <30 seconds. If a test is slow, it belongs in `integration/`.
5. **Mock external dependencies, not internal logic.** Mock yfinance/mfapi, but test actual scoring functions.
6. **Every bug fix comes with a regression test.** If it broke once, we test that it can't break again.
7. **Delete obsolete tests.** Dead tests are worse than no tests — they give false confidence.

---

## Integration with Other Agents

| Agent | Interaction |
|---|---|
| **Code Reviewer Agent** | Reviewer checks that tests exist and are meaningful. If Reviewer finds untested code, they request Test Agent to add coverage. |
| **Git Agent** | Git Agent won't merge until Test Agent confirms all tests pass and coverage meets thresholds. |
| **Quant Agent** | When Quant Agent designs new formulas, Test Agent writes corresponding mathematical validation tests. |
| **Data Agent** | When Data Agent adds a new data source, Test Agent creates mock fixtures and validation tests for the new fetcher. |

---

## Test Philosophy

> **"A test that doesn't catch bugs is a waste. A test that catches the wrong bugs is dangerous.
> Write tests that verify BEHAVIOR, not IMPLEMENTATION."**

- Test what the function DOES, not HOW it does it internally.
- If you refactor a function and the tests break but the behavior didn't change — the tests were wrong.
- Good tests are documentation. Reading the test should tell you exactly what the function is supposed to do.
