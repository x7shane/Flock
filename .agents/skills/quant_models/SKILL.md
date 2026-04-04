---
name: quant_models
description: >
  Quantitative Modeling and Simulation algorithms for the Quant Agent.
  Defines the math and implementation blueprint for Monte Carlo estimation
  (Geometric Brownian Motion), Historical Stress Testing, and the 16 core
  fundamental scoring factors for Flock.
---

# Quant Models — Flock Engine Reference

> **RULE:** Performance matters. Always use vectorized operations via `numpy` and `pandas`. Do not loop over simulated paths iteratively. Never build logic that looks into the future (avoid lookahead bias in historical analysis).

---

## 1. Monte Carlo Simulation Engine

### 1.1 Methodology: Geometric Brownian Motion (GBM)
We simulate future portfolio values under the assumption that asset returns follow a log-normal distribution.

**Stochastic Differential Equation:**
`dS = μSdt + σSdW`
Where:
- `dS`: Change in stock price
- `μ` (mu): Expected annualized return (drift)
- `σ` (sigma): Annualized volatility
- `dW`: Wiener process (Brownian motion) element

**Discrete Time Implementation (Log Returns):**
```python
import numpy as np

# dt = Time step (e.g., 1/252 for daily)
# n_days = Total simulation days
# n_sims = Number of paths (min 10,000 for MVP)

# 1. Generate random shocks normal(0, 1) setup
Z = np.random.normal(0, 1, size=(n_sims, n_days))

# 2. Geometric Brownian Motion path generation (Vectorized)
# S_T = S_0 * exp((mu - (sigma^2)/2)*dt + sigma*sqrt(dt)*Z)
drift = (mu - (sigma**2) / 2) * dt
diffusion = sigma * np.sqrt(dt) * Z

# 3. Compute continuous compounded returns
daily_log_returns = drift + diffusion

# 4. Convert to portfolio cumulative values
# Add correlation using Cholesky Decomposition if dealing with multiple assets!
```

### 1.2 Correlated Multi-Asset Monte Carlo
We must account for correlations between stocks. Portfolio variance is heavily influenced by how assets co-move.

**Implementation Steps:**
1. Calculate the covariance matrix `C` of historical daily log returns.
2. Perform Cholesky Decomposition: `L = np.linalg.cholesky(C)`
3. Generate uncorrelated random normal variables: `Z`
4. Create correlated random variables Z_corr = `L @ Z`

### 1.3 Key Metrics Output
After generating `n_sims` final portfolio values:
- **Expected Return (Mean):** Expected endpoint.
- **Value at Risk (VaR) 95%:** 5th percentile of portfolio final values.
- **Goal Hit Probability:** Count of paths that end above user's target / Total paths.
- **Max Drawdown:** Compute the rolling maximum and calculate the maximum negative drop across generated time-series.

---

## 2. Historical Simulation (Stress Testing)

### 2.1 Methodology
Applying historical crisis windows directly to the current portfolio weights to see the impact of past "market bloodbaths".

### 2.2 Hardcoded Historical Crisis Scenarios (India Context)
Calculate the max drawdown for the weighted portfolio if held through these dates:

*   **2008 Financial Crisis:** Jan 1, 2008 – Mar 9, 2009
*   **Taper Tantrum:** May 22, 2013 – Aug 28, 2013
*   **Demonetization:** Nov 8, 2016 – Dec 26, 2016
*   **COVID-19 Crash:** Feb 19, 2020 – Mar 23, 2020

### 2.3 Implementation Logic
```python
# 1. Slice historical dataframe to crisis date range
# 2. Calculate daily cumulative returns for the portfolio using user's weights
# 3. Calculate Max Drawdown: min(cumulative_return / running_max - 1)
# 4. Output: Max percentage loss & days to recover to pre-crisis high
```

---

## 3. Fundamental Factor Scoring Equations

The overall **Flock Score** is a weighted sum of 5 pillars. Each pillar normalizes the metric into a 0-100 logic.

### 3.1 Profitability (25% Default Weight)
*   **ROE (Return on Equity):** `Net Income / Average Shareholder Equity`
    *   *Scoring:* > 20% = Excellent, 15-20% = Good, < 10% = Poor
*   **ROCE (Return on Capital Employed):** `EBIT / (Total Assets - Current Liabilities)`
*   **Net Profit Margin:** `Net Income / Total Revenue`

### 3.2 Growth (25% Default Weight)
*   **3Y Revenue CAGR:** `(Revenue_Current / Revenue_3_Years_Ago)^(1/3) - 1`
*   **3Y EPS CAGR:** `(EPS_Current / EPS_3_Years_Ago)^(1/3) - 1`

### 3.3 Financial Health (20% Default Weight)
*   **Debt to Equity:** `Total Debt / Total Shareholder Equity`
    *   *Scoring:* < 0.5 = Excellent, 0.5 - 1.0 = Moderate, > 1.5 = High Risk. (Note: Exclude banks/NBFCs from this standard formula, use Capital Adequacy Ratio for financials).
*   **Current Ratio:** `Current Assets / Current Liabilities`
*   **Interest Coverage:** `EBIT / Interest Expense`

### 3.4 Valuation (15% Default Weight)
*   **P/E Ratio (TTM):** `Current Price / Trailing 12M EPS`
    *   *Scoring:* Measured relatively against sector median.
*   **P/B Ratio:** `Current Price / Book Value per Share`
*   **PEG Ratio:** `P/E Ratio / Expected EPS Growth Rate`

### 3.5 Quality / Governance (15% Default Weight)
*   **Promoter Holding:** Percentage of shares held by founders. Higher = better skin in the game.
*   **Promoter Pledging:** Percentage of promoter shares put up as collateral for loans. Higher = red flag.

---

## 4. Default Pillar Presets

The engine must support calculating scores dynamically based on the user's weight preset:

| Preset Name | Profitability | Growth | Health | Valuation | Quality |
|---|---|---|---|---|---|
| **Balanced (Default)** | 20% | 20% | 25% | 20% | 15% |
| **Growth** | 15% | 35% | 15% | 15% | 20% |
| **Value** | 20% | 10% | 25% | 35% | 10% |
| **Conservative** | 25% | 10% | 35% | 15% | 15% |
