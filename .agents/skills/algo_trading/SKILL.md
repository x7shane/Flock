---
name: algo_trading
description: >
  Deep knowledge on algorithmic trading for River — covering strategies, backtesting
  rules, risk management frameworks, India-specific broker APIs (Zerodha, Angel One,
  Upstox), and open-source tooling. Use when designing or evaluating any trading engine,
  signal system, or automated strategy for Indian markets.
---

# Algorithmic Trading — River's Reference

> **RULE:** Always validate a strategy against historical data before live deployment.
> Always account for slippage, taxes, and brokerage. A strategy that looks profitable
> in a backtest without these costs is worthless.

---

## 1. Strategy Categories

### 1.1 Mean Reversion
**Core Idea:** Asset prices tend to revert to their historical mean after deviating significantly.

| Variant | Mechanism | Tools |
|---|---|---|
| Single Asset | Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought) | RSI, Bollinger Bands, Z-score |
| Pairs Trading | Two correlated stocks diverge; short outperformer, long underperformer | Cointegration test (Engle-Granger), spread Z-score |
| Statistical Arb | Multi-asset mean reversion via linear regression residuals | Johansen cointegration, PCA |

**Key Risk:** Does not work in strong trending or breakout markets. Must include a **trend filter** (e.g., ADX > 25 = trending = skip mean reversion signals).

---

### 1.2 Momentum / Trend Following
**Core Idea:** Assets in strong trends tend to continue in that direction.

| Signal | Mechanism |
|---|---|
| Moving Average Crossover | 9 EMA crosses above 21 EMA (short-term bullish) |
| Golden Cross / Death Cross | 50-day MA crosses 200-day MA — long-term trend signal |
| Dual Momentum (Gary Antonacci) | Rank assets by 12-month return; long top performers |
| Breakout | Price breaks above resistance with high volume = buy |

**Key Risk:** Sharp reversals (flash crashes, policy announcements) cause severe drawdown. Must have **hard stop-loss** and **position sizing rules**.

---

### 1.3 Arbitrage
**Core Idea:** Same (or equivalent) asset priced differently on two venues — simultaneously buy on cheaper, sell on expensive venue.

| Type | Example | Reality Check |
|---|---|---|
| Exchange Arbitrage | Nifty futures on NSE vs. BFX | Window is microseconds — retail algo cannot compete with HFT |
| Cash-Futures Arbitrage | Spot Nifty vs. Nifty Futures (exploit mispricing) | Viable for retail with sufficient capital margin |
| ETF Arbitrage | ETF NAV vs. market price | Requires liquidity and fast execution |
| Statistical Arbitrage | Cointegrated pair spread z-score | Most viable for retail — minutes-to-hour timeframe |

**Key Risk:** Arbitrage windows are shrinking due to HFT. For retail, **only pursue statistical or cash-futures arb** — pure price arbitrage is not viable.

---

### 1.4 Market Making
**Core Idea:** Quote both bid and ask simultaneously. Profit from the bid-ask spread. Be the "house."

- **Profit Source:** Capturing the spread on each round-trip.
- **Inventory Risk:** Position accumulates on one side if market moves strongly.
- **Adverse Selection:** Risk of trading against an informed participant who knows something you don't.
- **Viable For:** Only if your platform has direct access to exchange order books and very low latency. Not practical for retail strategies.

---

### 1.5 Event-Driven / Fundamental
**Core Idea:** Enter positions around known events (earnings, corporate actions, macro releases).

| Event | Strategy |
|---|---|
| Quarterly Earnings | Buy implied volatility before earnings (straddle); sell post-announcement |
| F&O Expiry | Volatility typically spikes near expiry; theta decay accelerates in final week |
| Budget / RBI Policy | High uncertainty → buy volatility (straddle/strangle) pre-event |
| Corporate Actions | Dividend arbitrage; bonus share pricing effects |

---

## 2. Technical Indicators (Implementation Reference)

### Momentum Indicators
```python
# RSI (Relative Strength Index) — period = 14 standard
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.ewm(com=period-1, adjust=False).mean()
avg_loss = loss.ewm(com=period-1, adjust=False).mean()
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
# RSI < 30 = oversold | RSI > 70 = overbought
```

```python
# MACD = 12 EMA - 26 EMA | Signal = 9 EMA of MACD
ema12 = df['close'].ewm(span=12, adjust=False).mean()
ema26 = df['close'].ewm(span=26, adjust=False).mean()
macd = ema12 - ema26
signal = macd.ewm(span=9, adjust=False).mean()
histogram = macd - signal
# Bullish: MACD crosses above Signal | Bearish: MACD crosses below Signal
```

### Volatility Indicators
```python
# Bollinger Bands — period=20, std=2
sma = df['close'].rolling(20).mean()
std = df['close'].rolling(20).std()
upper_band = sma + (2 * std)
lower_band = sma - (2 * std)
# Buy when price touches lower band in uptrend
# Sell when price touches upper band in downtrend
```

```python
# ATR (Average True Range) — used for stop-loss sizing
high_low = df['high'] - df['low']
high_close = abs(df['high'] - df['close'].shift())
low_close = abs(df['low'] - df['close'].shift())
true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
atr = true_range.ewm(span=14, adjust=False).mean()
# Stop loss = entry_price - (2 × ATR)
```

### Trend Indicators
```python
# ADX (Average Directional Index) — trend strength
# ADX > 25: trending market | ADX < 20: sideways/ranging
# Use TA-Lib: talib.ADX(high, low, close, timeperiod=14)
```

---

## 3. Key Risk Management Rules (Non-Negotiable)

### Position Sizing (Kelly Criterion Simplified)
```
Position Size % = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
                  ─────────────────────────────────────────────
                               Avg Win

Use HALF-KELLY in practice (too aggressive at full Kelly)
```

### Fixed Fractional Risk
- Risk no more than **1-2% of total capital per trade**.
- Example: ₹10 lakh capital → max ₹10,000–₹20,000 at risk per trade.
- Stop-loss placement: Entry − (N × ATR), where N = 1.5 to 2.5.

### Portfolio-Level Controls
| Control | Rule |
|---|---|
| Max Daily Loss | Halt trading if daily P&L drops > 5% of capital (kill switch) |
| Max Drawdown | Reduce position sizes by 50% if drawdown exceeds 10% |
| Sector Concentration | No more than 30% of capital in one sector |
| Single Stock Limit | No more than 5% of capital in a single stock position |
| Overnight Risk | Limit overnight positions to 20% of capital (gap risk) |

### Sharpe Ratio Benchmark
```
Sharpe Ratio = (Strategy Return - Risk-Free Rate) / Strategy StdDev

> 1.0 = Acceptable
> 1.5 = Good
> 2.0 = Excellent
> 3.0 = Exceptional (usually means overfitting — verify!)
```

---

## 4. Backtesting Rules (Anti-Hallucination Framework)

### The Seven Deadly Sins of Backtesting

| Sin | Description | Fix |
|---|---|---|
| **Lookahead Bias** | Using future data to make past decisions | Enforce strict timestamp ordering; use `.shift(1)` on signals |
| **Survivorship Bias** | Testing only on stocks that still exist | Use point-in-time universe (include delisted stocks) |
| **Overfitting** | Too many parameters tuned to historical data | Fewer parameters; use out-of-sample period |
| **Ignoring Slippage** | Assuming perfect fill at signal price | Add 0.05–0.1% slippage per trade (India market) |
| **Ignoring Costs** | No brokerage, STT, GST, exchange fees | See cost table below |
| **Data Snooping** | Testing 100 strategies and reporting the best one | Adjust for multiple comparisons (Bonferroni correction) |
| **Regime Blindness** | Strategy tested only in bull market data | Test across bull, bear, and sideways regimes separately |

### India Trading Cost Structure (2025)
| Cost | Equity Delivery | Equity Intraday | F&O (Options) |
|---|---|---|---|
| Brokerage (Zerodha) | 0% | 0.03% or ₹20 max | ₹20 flat per order |
| STT (Securities Transaction Tax) | 0.1% (buy+sell) | 0.025% (sell side) | 0.0625% (sell, exercised) |
| Exchange Transaction Charge | 0.00297% NSE | 0.00297% NSE | 0.053% (NSE Futures) |
| GST | 18% on brokerage | 18% on brokerage | 18% on brokerage |
| SEBI Charges | ₹10/crore | ₹10/crore | ₹10/crore |
| Stamp Duty | 0.015% (buy) | 0.003% (buy) | 0.003% (buy) |

**Total round-trip cost estimate for F&O:** ~₹60–80 per lot (varies by premium). Always include in backtest P&L.

### Walk-Forward Testing
```
1. Divide historical data into 10 equal segments.
2. Train/optimize strategy on segments 1–7 (in-sample).
3. Test on segments 8–10 (out-of-sample).
4. Repeat by rolling the training window forward.
5. If out-of-sample Sharpe < 50% of in-sample Sharpe → strategy is overfitted.
```

---

## 5. Indian Broker APIs

### Zerodha Kite Connect (Primary Choice)
| Feature | Detail |
|---|---|
| **Auth** | OAuth 2.0 — `request_token` → `access_token` (expires daily at 6 AM) |
| **WebSocket** | `wss://ws.kite.trade` — real-time tick data (LTP, depth, OHLC) |
| **Order Rate Limit** | 3 orders/second per API key |
| **Historical Data** | Up to 2000 candles per API call; max 60 days for minute data |
| **Python SDK** | `pip install kiteconnect` — `github.com/zerodha/kiteconnect-python` |
| **Paper Trading** | Not natively supported — use mock order manager |

```python
# Zerodha auth flow
from kiteconnect import KiteConnect
kite = KiteConnect(api_key="your_api_key")
# Step 1: Redirect user to login URL
print(kite.login_url())
# Step 2: After redirect, get request_token from URL params
request_token = "abc123"
data = kite.generate_session(request_token, api_secret="your_secret")
kite.set_access_token(data["access_token"])
# Step 3: Place order
kite.place_order(variety=kite.VARIETY_REGULAR,
                 exchange=kite.EXCHANGE_NSE,
                 tradingsymbol="INFY",
                 transaction_type=kite.TRANSACTION_TYPE_BUY,
                 quantity=1,
                 order_type=kite.ORDER_TYPE_MARKET,
                 product=kite.PRODUCT_CNC)
```

### Angel One SmartAPI
- REST API + WebSocket. No per-order charges for algo users.
- Supports: Equity, F&O, Commodity (MCX), Currency.
- TOTP-based auth (time-based OTP for session).
- Python SDK: `pip install smartapi-python`

### Upstox API v2
- OAuth 2.0 auth. Good historical data access.
- Supports: Equity, F&O, Currency.
- WebSocket: Market data streaming.
- Python SDK: `pip install upstox-python`

---

## 6. Open-Source Tooling

| Tool | Purpose | Install |
|---|---|---|
| **Backtrader** | Full-featured Python backtesting framework | `pip install backtrader` |
| **Zipline-Reloaded** | Event-driven backtesting (Quantopian fork) | `pip install zipline-reloaded` |
| **TA-Lib** | 200+ technical indicators (C library with Python wrapper) | `pip install TA-Lib` |
| **Pandas-TA** | Pure-Python TA library (no C dependency) | `pip install pandas-ta` |
| **VectorBT** | Vectorized backtesting (very fast, GPU-capable) | `pip install vectorbt` |
| **PyAlgoTrade** | Simple event-driven backtesting | `pip install pyalgotrade` |
| **Quantstats** | Portfolio analytics & tearsheet generation | `pip install quantstats` |
| **yFinance** | Free historical data (Yahoo Finance) | `pip install yfinance` |
| **NSEPython** | Unofficial NSE data scraper (India-specific) | `pip install nsepython` |

---

## 7. SEBI Compliance for Algo Strategies

- **Registration Required:** All strategies interacting with Indian exchanges via API must be tagged in broker's system.
- **Audit Log Mandatory:** Every order must log: timestamp, strategy ID, signal reason, order parameters, execution price.
- **Kill Switch:** Must be able to halt ALL algo trading within seconds. SEBI audit may ask for evidence this exists.
- **No Spoofing / Layering:** Placing orders with intent to cancel before execution is market manipulation — SEBI prosecutes.
- **Fat Finger Check:** Always implement sanity check on order size and price before submission (e.g., reject if quantity > 10× normal, or price > 5% from LTP).
