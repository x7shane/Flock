# Flock API Contract

> **Draft Version:** 0.1
> **Base URL:** `/api/v1`
> **Formats:** All requests and responses are `application/json`

---

## 1. Stocks & Data

### `GET /stocks`
Retrieve a paginated list of the Nifty 200 universe.

**Query Parameters:**
- `page` (int, default: 1)
- `limit` (int, default: 50)
- `search` (string, optional): Search by ticker or company name.
- `sort` (string, optional): `flock_score_desc`, `market_cap_desc`, `ticker_asc`

**Response:**
```json
{
  "data": [
    {
      "ticker": "RELIANCE.NS",
      "company_name": "Reliance Industries Limited",
      "sector": "Energy",
      "flock_score": 82.5,
      "last_price": 2895.50
    }
  ],
  "meta": {
    "total": 200,
    "page": 1,
    "has_next": true
  }
}
```

### `GET /stocks/{ticker}`
Retrieve detailed fundamentals and score breakdown for a specific stock.

**Response:**
```json
{
  "ticker": "RELIANCE.NS",
  "company_name": "Reliance Industries Limited",
  "flock_score": {
    "total": 82.5,
    "preset": "balanced",
    "pillars": {
      "profitability": 85.0,
      "growth": 78.5,
      "health": 90.0,
      "valuation": 65.0,
      "quality": 88.0
    }
  },
  "fundamentals": {
    "roe": 0.25,
    "pe_ratio": 28.5,
    "debt_equity": 0.45
  }
}
```

---

## 2. Simulation & Modeling

### `POST /simulate/portfolio`
Run a Monte Carlo and Historical Stress Test on a defined portfolio.

**Request Body:**
```json
{
  "capital_inr": 1000000,
  "time_horizon_years": 10,
  "portfolio": [
    {
      "ticker": "RELIANCE.NS",
      "weight": 0.50
    },
    {
      "ticker": "HDFCBANK.NS",
      "weight": 0.50
    }
  ]
}
```

**Response:**
```json
{
  "monte_carlo": {
    "probability_positive_return": 95.5,
    "probability_10pct_cagr": 68.2,
    "var_95_inr": 150000,
    "median_cagr_pct": 12.5,
    "expected_final_value_inr": 3247000,
    "return_range_10_90_pct": [6.5, 18.2]
  },
  "stress_tests": [
    {
      "crisis_name": "2020 COVID Crash",
      "portfolio_max_drawdown_pct": -28.5,
      "max_drawdown_date": "2020-03-23"
    }
  ]
}
```

### `POST /simulate/sip`
Run an SIP projection.

**Request Body:**
```json
{
  "monthly_investment_inr": 10000,
  "expected_annual_return_pct": 12.0,
  "time_horizon_years": 10,
  "annual_step_up_pct": 10.0
}
```

**Response:**
```json
{
  "total_invested_inr": 1912490,
  "future_value_inr": 3546720,
  "wealth_gain_inr": 1634230,
  "effective_cagr_pct": 12.0
}
```
