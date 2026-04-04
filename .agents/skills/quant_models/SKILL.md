---
name: quant_models
description: >
  Quant Agent — the mathematical brain of Flock. Owns all scoring formulas,
  probability simulation engines (Monte Carlo, Historical Stress Test), volatility
  models, and statistical methods. Every number Flock shows a user originates
  from logic defined in this skill file.
---

# Quantitative Models — Flock's Mathematical Core

> **RULE:** Every formula here must be implementable with NumPy/SciPy/Pandas.
> No proprietary libraries. No black boxes. If we can't explain the math to a
> user in a tooltip, we don't ship it.

---

## 1. Flock Score — Fundamental Scoring Engine

### Architecture

```
Raw Fundamentals (16 factors)
        ↓
Per-Factor Normalization (percentile rank within Nifty 200)
        ↓
Pillar Aggregation (weighted average within each pillar)
        ↓
Final Score (weighted sum of pillar scores × user-selected weights)
        ↓
Flock Score: 0–100
```

### Factor Normalization

**Method: Percentile Rank within the Nifty 200 universe.**

For each factor, rank all ~200 stocks and convert to a 0–100 percentile score:

```python
import numpy as np
from scipy.stats import percentileofscore

def normalize_factor(values: np.ndarray, ticker_value: float, higher_is_better: bool = True) -> float:
    """
    Normalize a single factor value to 0-100 percentile rank.
    
    Args:
        values: Array of all stock values for this factor in the universe
        ticker_value: The specific stock's value for this factor
        higher_is_better: True for ROE, ROCE. False for Debt/Equity, P/E.
    
    Returns:
        Percentile score 0-100. Higher = better for that factor.
    """
    if ticker_value is None or np.isnan(ticker_value):
        return None  # Missing data — handled by pillar aggregation
    
    percentile = percentileofscore(values[~np.isnan(values)], ticker_value, kind='rank')
    
    if not higher_is_better:
        percentile = 100 - percentile  # Invert: lower raw value = higher score
    
    return round(percentile, 2)
```

### Factor Direction Map

| Factor | Higher is Better? | Notes |
|---|---|---|
| ROE | ✅ Yes | Higher return on equity = better |
| ROCE | ✅ Yes | Higher return on capital = better |
| Net Profit Margin | ✅ Yes | Higher margin = more profitable |
| Revenue CAGR (3yr) | ✅ Yes | Faster growth = better |
| EPS Growth (3yr) | ✅ Yes | Growing earnings = better |
| Debt/Equity | ❌ No (lower is better) | Less debt = safer |
| Current Ratio | ✅ Yes | Higher = more liquid |
| Interest Coverage | ✅ Yes | Higher = can pay interest easily |
| Free Cash Flow | ✅ Yes | More free cash = better |
| P/E Ratio (TTM) | ❌ No (lower is better) | Lower = cheaper relative to earnings |
| P/B Ratio | ❌ No (lower is better) | Lower = cheaper relative to book |
| PEG Ratio | ❌ No (lower is better) | Lower = cheaper relative to growth |
| Dividend Yield | ✅ Yes | Higher yield = more cash returned |
| Promoter Holding % | ✅ Yes | Higher = more skin in the game |
| Promoter Pledge % | ❌ No (lower is better) | Lower = less risk |
| FII/DII Trends | ✅ Yes | Increasing = smart money buying |

### Pillar Aggregation

Each pillar's score is the **average of its constituent factor percentiles** (excluding missing factors):

```python
def calculate_pillar_score(factor_scores: dict[str, float | None], pillar_factors: list[str]) -> float:
    """
    Average the factor percentile scores within a pillar, excluding None values.
    
    Args:
        factor_scores: Dict of factor_name → percentile score (0-100 or None)
        pillar_factors: List of factor names belonging to this pillar
    
    Returns:
        Pillar score 0-100, or None if all factors are missing.
    """
    valid_scores = [
        factor_scores[f] for f in pillar_factors 
        if f in factor_scores and factor_scores[f] is not None
    ]
    
    if not valid_scores:
        return None  # Entire pillar missing — exclude from final score
    
    return round(sum(valid_scores) / len(valid_scores), 2)
```

### Pillar Definitions

```python
PILLARS = {
    "profitability": ["roe", "roce", "net_profit_margin"],
    "growth":        ["revenue_cagr_3yr", "eps_growth_3yr"],
    "health":        ["debt_equity", "current_ratio", "interest_coverage", "free_cash_flow"],
    "valuation":     ["pe_ratio", "pb_ratio", "peg_ratio", "dividend_yield"],
    "quality":       ["promoter_holding_pct", "promoter_pledge_pct", "fii_dii_trend"],
}
```

### Preset Weights

```python
PRESETS = {
    "balanced":     {"profitability": 0.20, "growth": 0.20, "health": 0.25, "valuation": 0.20, "quality": 0.15},
    "growth":       {"profitability": 0.15, "growth": 0.35, "health": 0.15, "valuation": 0.15, "quality": 0.20},
    "value":        {"profitability": 0.20, "growth": 0.10, "health": 0.25, "valuation": 0.35, "quality": 0.10},
    "conservative": {"profitability": 0.25, "growth": 0.10, "health": 0.35, "valuation": 0.15, "quality": 0.15},
}
```

### Final Flock Score

```python
def calculate_flock_score(
    pillar_scores: dict[str, float | None],
    weights: dict[str, float]
) -> float:
    """
    Weighted sum of pillar scores, re-normalized if any pillar is missing.
    
    Returns:
        Flock Score 0-100. Higher = fundamentally stronger.
    """
    valid_pillars = {
        p: score for p, score in pillar_scores.items()
        if score is not None and p in weights
    }
    
    if not valid_pillars:
        return 0.0  # No data at all
    
    # Re-normalize weights to sum to 1.0 (handles missing pillars)
    total_weight = sum(weights[p] for p in valid_pillars)
    
    score = sum(
        valid_pillars[p] * (weights[p] / total_weight)
        for p in valid_pillars
    )
    
    return round(score, 2)
```

> [!NOTE]
> **Missing factor handling (MVP):** If a factor is None/NaN, it's excluded from the pillar average. If an entire pillar is missing, its weight is redistributed proportionally to the remaining pillars. This is simple and avoids penalizing stocks for missing non-mandatory data (e.g., dividends for growth companies).

---

## 2. Monte Carlo Simulation Engine

### Theory: Geometric Brownian Motion (GBM)

Asset prices are modeled as:

```
S(t) = S(0) × exp[(μ - σ²/2)t + σ√t × Z]

Where:
  S(t) = Price at time t
  S(0) = Current price
  μ    = Expected annual return (from historical log returns)
  σ    = Annual volatility (from historical log returns)
  Z    = Random draw from N(0,1) — standard normal
  t    = Time step (in years)
```

### Portfolio-Level Monte Carlo

For a portfolio of N assets, we need to account for **correlations** between assets:

```python
import numpy as np

def run_monte_carlo(
    expected_returns: np.ndarray,    # Shape: (N,) — annual expected return per asset
    covariance_matrix: np.ndarray,   # Shape: (N, N) — annual covariance matrix
    weights: np.ndarray,             # Shape: (N,) — portfolio weights, sum to 1.0
    initial_capital: float,          # Starting capital in INR
    time_horizon_years: float,       # Investment period
    num_simulations: int = 10_000,   # Number of Monte Carlo paths
    time_steps_per_year: int = 252,  # Trading days per year
    seed: int = 42,                  # Reproducibility
) -> dict:
    """
    Run portfolio-level Monte Carlo simulation using correlated GBM.
    
    Returns dict with:
      - final_values: array of terminal portfolio values (num_simulations,)
      - paths: array of portfolio value paths (num_simulations, total_steps)
      - statistics: dict of summary statistics
    """
    np.random.seed(seed)
    
    num_assets = len(expected_returns)
    total_steps = int(time_horizon_years * time_steps_per_year)
    dt = 1 / time_steps_per_year
    
    # Cholesky decomposition for correlated random draws
    L = np.linalg.cholesky(covariance_matrix)
    
    # Portfolio return and volatility
    portfolio_return = weights @ expected_returns
    portfolio_vol = np.sqrt(weights @ covariance_matrix @ weights)
    
    # Generate correlated random shocks
    # Shape: (num_simulations, total_steps)
    Z = np.random.standard_normal((num_simulations, total_steps))
    
    # GBM path generation (portfolio level)
    drift = (portfolio_return - 0.5 * portfolio_vol**2) * dt
    diffusion = portfolio_vol * np.sqrt(dt) * Z
    
    log_returns = drift + diffusion
    cumulative_returns = np.cumsum(log_returns, axis=1)
    
    paths = initial_capital * np.exp(cumulative_returns)
    
    # Prepend initial capital
    paths = np.column_stack([np.full(num_simulations, initial_capital), paths])
    
    final_values = paths[:, -1]
    
    # Calculate statistics
    statistics = _calculate_statistics(
        final_values, paths, initial_capital, time_horizon_years
    )
    
    return {
        "final_values": final_values,
        "paths": paths,
        "statistics": statistics,
    }
```

### Output Statistics

```python
def _calculate_statistics(
    final_values: np.ndarray,
    paths: np.ndarray,
    initial_capital: float,
    time_horizon_years: float,
) -> dict:
    """Calculate all user-facing statistics from Monte Carlo results."""
    
    returns = (final_values - initial_capital) / initial_capital
    cagr_values = (final_values / initial_capital) ** (1 / time_horizon_years) - 1
    
    # Probability of target returns
    prob_positive = np.mean(returns > 0) * 100
    prob_10pct = np.mean(cagr_values > 0.10) * 100
    prob_15pct = np.mean(cagr_values > 0.15) * 100
    
    # Value at Risk (VaR) — 95% confidence
    # "In 95% of scenarios, you won't lose more than ₹X"
    var_95 = initial_capital - np.percentile(final_values, 5)
    
    # Conditional VaR (Expected Shortfall) — average loss in worst 5%
    worst_5pct = final_values[final_values <= np.percentile(final_values, 5)]
    cvar_95 = initial_capital - np.mean(worst_5pct) if len(worst_5pct) > 0 else 0
    
    # Max Drawdown (across all paths)
    peak = np.maximum.accumulate(paths, axis=1)
    drawdowns = (peak - paths) / peak
    max_drawdown_per_path = np.max(drawdowns, axis=1)
    
    # Return range (10th to 90th percentile)
    return_p10 = np.percentile(cagr_values, 10) * 100
    return_p50 = np.percentile(cagr_values, 50) * 100
    return_p90 = np.percentile(cagr_values, 90) * 100
    
    return {
        "probability_positive_return": round(prob_positive, 1),
        "probability_10pct_cagr": round(prob_10pct, 1),
        "probability_15pct_cagr": round(prob_15pct, 1),
        "var_95_inr": round(var_95, 2),
        "cvar_95_inr": round(cvar_95, 2),
        "median_cagr_pct": round(return_p50, 2),
        "return_range_10_90_pct": [round(return_p10, 2), round(return_p90, 2)],
        "median_final_value_inr": round(np.median(final_values), 2),
        "expected_final_value_inr": round(np.mean(final_values), 2),
        "max_drawdown_median_pct": round(np.median(max_drawdown_per_path) * 100, 2),
        "max_drawdown_worst_5pct": round(np.percentile(max_drawdown_per_path, 95) * 100, 2),
    }
```

### Estimating μ and σ from Historical Data

```python
def estimate_return_parameters(
    price_series: pd.Series,
    min_years: int = 3,
) -> tuple[float, float]:
    """
    Estimate annualized expected return and volatility from historical prices.
    
    Uses log returns for mathematical consistency with GBM.
    
    Args:
        price_series: Daily closing prices (DatetimeIndex)
        min_years: Minimum years of data required
    
    Returns:
        (annual_expected_return, annual_volatility)
    
    Raises:
        ValueError: If insufficient data
    """
    trading_days = len(price_series)
    years_of_data = trading_days / 252
    
    if years_of_data < min_years:
        raise ValueError(
            f"Need {min_years}+ years of data, got {years_of_data:.1f} years"
        )
    
    # Log returns
    log_returns = np.log(price_series / price_series.shift(1)).dropna()
    
    # Annualize
    daily_mean = log_returns.mean()
    daily_std = log_returns.std()
    
    annual_return = daily_mean * 252
    annual_volatility = daily_std * np.sqrt(252)
    
    return annual_return, annual_volatility
```

### Covariance Matrix Construction

```python
def build_covariance_matrix(
    price_dataframe: pd.DataFrame,
    method: str = "sample",  # "sample" for MVP, "shrinkage" for V2
) -> np.ndarray:
    """
    Build annualized covariance matrix from daily prices.
    
    Args:
        price_dataframe: DataFrame with tickers as columns, dates as index
        method: "sample" (standard) or "shrinkage" (Ledoit-Wolf, V2)
    
    Returns:
        Annualized covariance matrix (N × N)
    """
    log_returns = np.log(price_dataframe / price_dataframe.shift(1)).dropna()
    
    if method == "sample":
        cov_daily = log_returns.cov()
    elif method == "shrinkage":
        # V2: Ledoit-Wolf shrinkage for better estimates
        from sklearn.covariance import LedoitWolf
        lw = LedoitWolf().fit(log_returns)
        cov_daily = pd.DataFrame(
            lw.covariance_, 
            index=log_returns.columns, 
            columns=log_returns.columns
        )
    
    # Annualize: multiply by 252
    cov_annual = cov_daily * 252
    
    return cov_annual.values
```

> [!IMPORTANT]
> **MVP uses 3-5 years of historical data** with sample covariance. V2 will add Ledoit-Wolf shrinkage and rolling windows. The seed parameter ensures reproducibility for testing — remove or randomize for production.

---

## 3. Historical Stress Test Engine

### Crisis Period Database

```python
CRISIS_PERIODS = {
    "2008_global_financial_crisis": {
        "name": "2008 Global Financial Crisis",
        "start": "2008-01-01",
        "end": "2009-03-31",
        "peak_to_trough": "2008-01-09 to 2008-10-27",
        "nifty_50_drawdown_pct": -59.9,
        "description": "Global banking collapse. Lehman Brothers failed. Indian markets fell ~60%.",
    },
    "2013_taper_tantrum": {
        "name": "2013 Taper Tantrum (INR Crash)",
        "start": "2013-05-22",
        "end": "2013-09-30",
        "peak_to_trough": "2013-05-22 to 2013-08-28",
        "nifty_50_drawdown_pct": -14.2,
        "description": "US Fed hinted at tapering QE. FIIs pulled $12B from India. INR hit ₹68.85/$.",
    },
    "2016_demonetization": {
        "name": "2016 Demonetization",
        "start": "2016-11-08",
        "end": "2017-03-31",
        "peak_to_trough": "2016-11-08 to 2016-12-26",
        "nifty_50_drawdown_pct": -7.8,
        "description": "India banned ₹500 and ₹1000 notes overnight. Cash-dependent sectors crashed.",
        "worst_sectors": ["real_estate", "consumer_discretionary", "financials"],
    },
    "2020_covid_crash": {
        "name": "2020 COVID Crash",
        "start": "2020-02-19",
        "end": "2020-06-30",
        "peak_to_trough": "2020-02-19 to 2020-03-23",
        "nifty_50_drawdown_pct": -38.4,
        "description": "Global pandemic lockdown. Fastest 30%+ crash in history. Fastest recovery too.",
    },
    "2022_fii_selloff": {
        "name": "2022 FII Selloff",
        "start": "2022-01-01",
        "end": "2022-06-30",
        "peak_to_trough": "2022-01-18 to 2022-06-17",
        "nifty_50_drawdown_pct": -16.6,
        "description": "FIIs sold ₹2.1 lakh crore in H1 2022. Highest ever FII outflow.",
    },
}
```

### Stress Test Logic

```python
def run_stress_test(
    portfolio_tickers: list[str],
    portfolio_weights: np.ndarray,
    historical_prices: pd.DataFrame,  # Columns = tickers, Index = dates
    crisis_id: str,
    initial_capital: float,
) -> dict:
    """
    Simulate how the user's portfolio would have performed during a historical crisis.
    
    Returns:
        Dict with drawdown, recovery time, worst day, and narrative summary.
    """
    crisis = CRISIS_PERIODS[crisis_id]
    start = pd.Timestamp(crisis["start"])
    end = pd.Timestamp(crisis["end"])
    
    # Filter prices to crisis period
    crisis_prices = historical_prices.loc[start:end, portfolio_tickers]
    
    if crisis_prices.empty:
        return {"error": f"No price data available for {crisis['name']}"}
    
    # Calculate weighted portfolio returns
    daily_returns = crisis_prices.pct_change().dropna()
    portfolio_returns = (daily_returns * portfolio_weights).sum(axis=1)
    
    # Cumulative portfolio value
    portfolio_value = initial_capital * (1 + portfolio_returns).cumprod()
    
    # Peak tracking
    peak = portfolio_value.expanding().max()
    drawdown = (portfolio_value - peak) / peak
    
    max_drawdown = drawdown.min()
    max_drawdown_date = drawdown.idxmin()
    
    # Recovery: when does portfolio return to pre-crisis peak?
    pre_crisis_peak = portfolio_value.iloc[0]
    recovery_mask = portfolio_value.loc[max_drawdown_date:] >= pre_crisis_peak
    
    if recovery_mask.any():
        recovery_date = recovery_mask.idxmax()
        recovery_days = (recovery_date - max_drawdown_date).days
    else:
        recovery_date = None
        recovery_days = None  # Didn't recover within the period
    
    # Worst single day
    worst_day_return = portfolio_returns.min()
    worst_day_date = portfolio_returns.idxmin()
    
    return {
        "crisis_name": crisis["name"],
        "crisis_description": crisis["description"],
        "portfolio_max_drawdown_pct": round(max_drawdown * 100, 2),
        "max_drawdown_date": str(max_drawdown_date.date()),
        "worst_single_day_pct": round(worst_day_return * 100, 2),
        "worst_single_day_date": str(worst_day_date.date()),
        "recovery_days": recovery_days,
        "recovery_date": str(recovery_date.date()) if recovery_date else "Did not recover in period",
        "final_value_inr": round(portfolio_value.iloc[-1], 2),
        "loss_inr": round(initial_capital - portfolio_value.min(), 2),
        "nifty_50_drawdown_pct": crisis["nifty_50_drawdown_pct"],
    }
```

---

## 4. SIP Calculator (Separate Module)

### Why Separate from Portfolio Simulator

SIP (Systematic Investment Plan) uses **monthly periodic investments**, not a lump sum. The math is fundamentally different — it's a series of individual investments, each compounding from its own start date.

```python
def calculate_sip_projections(
    monthly_amount: float,          # INR invested per month
    expected_annual_return: float,  # e.g., 0.12 for 12%
    time_horizon_years: int,        # e.g., 10
    annual_step_up_pct: float = 0,  # Optional: increase SIP by X% yearly
) -> dict:
    """
    Calculate SIP future value using the standard annuity formula.
    
    Formula: FV = P × [((1+r)^n - 1) / r] × (1+r)
    Where:
        P = Monthly investment
        r = Monthly rate of return (annual / 12)
        n = Total months
    """
    monthly_rate = expected_annual_return / 12
    total_months = time_horizon_years * 12
    
    if annual_step_up_pct > 0:
        # Step-up SIP: calculate year by year
        total_invested = 0
        future_value = 0
        current_monthly = monthly_amount
        
        for year in range(time_horizon_years):
            for month in range(12):
                months_remaining = total_months - (year * 12 + month) - 1
                future_value += current_monthly * ((1 + monthly_rate) ** months_remaining)
                total_invested += current_monthly
            current_monthly *= (1 + annual_step_up_pct / 100)
    else:
        # Standard SIP formula
        total_invested = monthly_amount * total_months
        future_value = monthly_amount * (
            ((1 + monthly_rate) ** total_months - 1) / monthly_rate
        ) * (1 + monthly_rate)
    
    wealth_gain = future_value - total_invested
    
    return {
        "total_invested_inr": round(total_invested, 2),
        "future_value_inr": round(future_value, 2),
        "wealth_gain_inr": round(wealth_gain, 2),
        "absolute_return_pct": round((wealth_gain / total_invested) * 100, 2),
        "effective_cagr_pct": round(
            ((future_value / total_invested) ** (1 / time_horizon_years) - 1) * 100, 2
        ),
    }
```

---

## 5. Key Mathematical Assumptions & Disclaimers

### What We Tell the User

Every simulation output screen MUST display:

```
⚠️ IMPORTANT DISCLAIMERS:
1. These simulations use historical data and statistical models. Past performance 
   does not guarantee future results.
2. The Monte Carlo model assumes returns follow a log-normal distribution. In reality, 
   extreme market events (crashes, sudden rallies) happen more often than the model predicts.
3. Results do not account for taxes, transaction costs, or inflation unless explicitly stated.
4. This is an educational tool, NOT investment advice. Always consult a SEBI-registered 
   advisor before making investment decisions.
5. The Flock Score is a quantitative ranking, not a buy/sell recommendation.
```

### Assumptions We Make (Must Document)

| Assumption | Reality Check | Impact |
|---|---|---|
| Log-normal returns | Fat tails exist in Indian equities | Underestimates extreme event risk |
| Constant correlation | Correlations spike during crashes | Portfolio diversification overstated in crises |
| 252 trading days/year | India has ~250 actual trading days | Negligible impact |
| Historical μ and σ predict future | Structural breaks happen | Cannot forecast regime changes |
| No transaction costs in simulation | Real portfolios have costs | Overstates net returns slightly |

---

## 6. V2 Roadmap (Quant Extensions)

Items deferred from MVP. See V2 Backlog in implementation plan.

- **GARCH(1,1) volatility** — Time-varying volatility to replace constant σ
- **Ledoit-Wolf shrinkage** — Better covariance matrix estimation for small samples
- **Bootstrap resampling** — For stocks with <3 years of history
- **Sector-relative scoring** — Z-score within sector instead of absolute universe rank
- **Efficient Frontier visualization** — Show the optimal risk/return boundary for portfolios
- **Black-Litterman model** — Incorporate user views into expected returns

---

## Quant Agent Operating Rules

1. **Every formula must be unit-tested.** If the Test Agent can't verify it, it doesn't ship.
2. **All random processes must accept a seed parameter.** Reproducibility is non-negotiable for testing.
3. **NaN/None propagation must be explicit.** Never silently convert missing data to 0.
4. **Round user-facing numbers.** INR values to 2 decimals. Percentages to 1-2 decimals.
5. **Validate inputs.** Negative capital, weights not summing to 1, empty price series — all must raise clear errors.
6. **Document every assumption.** If a number appears on screen, the user should be able to trace it back to a formula in this file.
