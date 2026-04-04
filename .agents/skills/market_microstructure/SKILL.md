---
name: market_microstructure
description: >
  Market microstructure and technical analysis reference for River — covering
  candlestick patterns, key indicators (RSI, MACD, Bollinger Bands, ATR),
  order types, order book dynamics, support/resistance, and how to build
  charting features for Indian markets (NSE/BSE). Use when building trading
  tools, charting features, or educating users about price action.
---

# Market Microstructure & Technical Analysis — River's Reference

> **RULE:** Technical analysis is a tool for probability, not certainty.
> Never present any indicator or pattern as a guaranteed signal.
> Always combine multiple confirmations (pattern + indicator + volume) before acting.

---

## 1. Candlestick Patterns (High-Reliability)

### Single Candle Patterns

| Pattern | Shape | Signal | Reliability |
|---|---|---|---|
| **Doji** | Open ≈ Close, small body with wicks | Indecision — watch for reversal after strong trend | Medium |
| **Hammer** | Small body at top, long lower wick (≥ 2× body), at bottom of downtrend | Bullish reversal | High |
| **Hanging Man** | Same shape as hammer but at top of uptrend | Bearish reversal | High |
| **Shooting Star** | Small body at bottom, long upper wick, at top of uptrend | Bearish reversal | High |
| **Inverted Hammer** | Small body at top, long upper wick, at bottom of downtrend | Bullish reversal (needs confirmation) | Medium |
| **Marubozu** | No wicks — body spans entire candle range | Strong momentum in direction of candle | High |
| **Spinning Top** | Small body, near-equal wicks | Indecision / consolidation | Low |

### Two-Candle Patterns

| Pattern | Description | Signal |
|---|---|---|
| **Bullish Engulfing** | Second (green) candle completely engulfs first (red) candle | Strong bullish reversal |
| **Bearish Engulfing** | Second (red) candle completely engulfs first (green) candle | Strong bearish reversal |
| **Tweezer Bottom** | Two candles with same low — second one green | Bullish reversal at support |
| **Tweezer Top** | Two candles with same high — second one red | Bearish reversal at resistance |
| **Harami (Bullish)** | Small green candle inside prior large red candle | Potential bullish reversal |
| **Harami (Bearish)** | Small red candle inside prior large green candle | Potential bearish reversal |

### Three-Candle Patterns (Most Reliable)

| Pattern | Description | Signal |
|---|---|---|
| **Morning Star** | Red candle → small body (doji/spinning top) → green candle closing > midpoint of first candle | Strong bullish reversal |
| **Evening Star** | Green candle → small body → red candle closing < midpoint of first candle | Strong bearish reversal |
| **Three White Soldiers** | Three consecutive green candles, each closing near its high | Strong bullish continuation |
| **Three Black Crows** | Three consecutive red candles, each closing near its low | Strong bearish continuation |
| **Three Inside Up** | Harami → confirmation candle closes above both | Bullish reversal |
| **Three Inside Down** | Bearish Harami → confirmation candle closes below both | Bearish reversal |

---

## 2. Technical Indicators — Complete Reference

### 2.1 Trend Indicators

**Moving Averages:**
```
Simple Moving Average (SMA):   SMA_n = (P1 + P2 + ... + Pn) / n
Exponential Moving Average (EMA): EMA_t = Price_t × k + EMA_(t-1) × (1-k)
                                   where k = 2 / (n + 1)

Common periods:
  9-day EMA:   Very fast signal (intraday traders)
  21-day EMA:  Short-term trend
  50-day SMA:  Medium-term trend (institutional reference)
  200-day SMA: Long-term trend (bull/bear market divider)

Golden Cross:    50-day SMA crosses ABOVE 200-day SMA → Bullish
Death Cross:     50-day SMA crosses BELOW 200-day SMA → Bearish
```

**ADX (Average Directional Index):**
```
ADX Range:
  0–20:  Weak / no trend (avoid directional strategies)
  20–25: Emerging trend
  25–50: Strong trend (momentum strategies ideal)
  50+:   Extreme trend (may be overextended)

Rule: Only trade mean reversion when ADX < 20.
      Only trade momentum when ADX > 25.
```

---

### 2.2 Momentum Indicators

**RSI (Relative Strength Index) — Period: 14**
```
RS = Average Gain (14 periods) / Average Loss (14 periods)
RSI = 100 − (100 / (1 + RS))

Interpretation:
  RSI < 30:  Oversold → potential Buy signal
  RSI > 70:  Overbought → potential Sell signal
  RSI = 50:  Midpoint — neutral
  RSI Divergence:
    Bullish: Price makes lower low, RSI makes higher low → bullish reversal
    Bearish: Price makes higher high, RSI makes lower high → bearish reversal
```

**MACD (Moving Average Convergence Divergence) — Standard: 12, 26, 9**
```
MACD Line   = 12 EMA − 26 EMA
Signal Line = 9 EMA of MACD Line
Histogram   = MACD Line − Signal Line

Signals:
  Bullish Crossover: MACD crosses ABOVE Signal Line → Buy
  Bearish Crossover: MACD crosses BELOW Signal Line → Sell
  Zero Line Cross:   MACD crossing from negative to positive = stronger bullish signal
  Histogram:         Expanding histogram = momentum increasing; shrinking = weakening
  Divergence:        Same interpretation as RSI divergence
```

**Stochastic Oscillator — Standard: 14, 3, 3**
```
%K = (Current Close − Lowest Low_14) / (Highest High_14 − Lowest Low_14) × 100
%D = 3-period SMA of %K

Interpretation:
  < 20 = Oversold
  > 80 = Overbought
  Signal: %K crossing above %D in oversold zone = Buy
          %K crossing below %D in overbought zone = Sell
```

---

### 2.3 Volatility Indicators

**Bollinger Bands — Period: 20, StdDev: 2**
```
Middle Band = 20-period SMA
Upper Band  = SMA + (2 × StdDev)
Lower Band  = SMA − (2 × StdDev)

Signals:
  Price at lower band + bullish candle → Buy (in uptrend context)
  Price at upper band + bearish candle → Sell (in downtrend context)
  Squeeze (bands narrow) → Low volatility → Breakout imminent
  Walk the band (price stays on upper/lower) → Strong trend, not reversal

Bandwidth = (Upper − Lower) / Middle × 100
  Low bandwidth = consolidation ahead of breakout
```

**ATR (Average True Range) — Period: 14**
```
True Range = MAX(High − Low, |High − Prev Close|, |Low − Prev Close|)
ATR = 14-period Wilder's Moving Average of True Range

Uses:
  Stop-Loss: Place stop at Entry − (1.5 × ATR) for long positions
  Position Sizing: Risk ₹/ATR to determine lot size
  Volatility filter: High ATR = avoid mean reversion; Low ATR = avoid momentum
```

**VIX India (India VIX)**
```
India VIX measures expected volatility of Nifty 50 over next 30 days.
  VIX < 15:  Low fear — markets complacent; potential for correction
  VIX 15–20: Normal uncertainty
  VIX > 20:  High fear — potential buying opportunity (contrarian)
  VIX > 30:  Panic — extreme risk; trading extremely difficult
```

---

### 2.4 Volume Indicators

**Volume Profile:**
- **POC (Point of Control):** Price level with highest traded volume — acts as major support/resistance.
- **VAH (Value Area High):** Upper boundary where 70% of volume traded.
- **VAL (Value Area Low):** Lower boundary where 70% of volume traded.
- Price inside Value Area = consolidation. Price outside = directional move.

**OBV (On-Balance Volume):**
```
OBV = Previous OBV + Volume (if Close > Prev Close)
    = Previous OBV − Volume (if Close < Prev Close)

Signal: OBV rising with price = confirmed trend
        OBV flat/falling with rising price = divergence → potential reversal
```

---

## 3. Support & Resistance

### Types of Support/Resistance
| Type | Description | Strength |
|---|---|---|
| **Horizontal S/R** | Previous swing highs/lows | High |
| **Trendlines** | Diagonal lines connecting swing points | High when tested 3+ times |
| **Moving Averages** | 50-day, 200-day SMA act as dynamic S/R | High (especially at round numbers) |
| **Fibonacci Retracements** | 23.6%, 38.2%, 50%, 61.8%, 78.6% of a move | Medium-High |
| **Round Numbers** | ₹100, ₹500, ₹1000 levels on stocks; 20000, 22000 on Nifty | High (psychological) |
| **Volume Profile POC** | High-volume price nodes | Very High |

### Fibonacci Levels (Key Retracement Zones)
```
After a significant move from Point A to Point B:
  23.6% retracement = Shallow pullback (strong trend)
  38.2% retracement = Normal pullback — watch for bounce
  50.0% retracement = Midpoint — key level
  61.8% retracement = "Golden ratio" — most important Fibonacci level
  78.6% retracement = Deep retracement — trend may be reversing

How to calculate:
  Retracement Level = B − (B − A) × Fibonacci %
```

---

## 4. Order Types (NSE/BSE)

| Order Type | Description | When to Use |
|---|---|---|
| **Market Order (MKT)** | Execute immediately at best available price | When speed is priority; slippage risk |
| **Limit Order (L)** | Execute only at specified price or better | When price precision matters |
| **Stop-Loss Order (SL)** | Triggers market order when price hits stop level | Downside protection |
| **Stop-Loss Limit (SL-M)** | Triggers limit order when price hits stop | More control on fill price but may not execute |
| **After Market Order (AMO)** | Placed after market hours; executed at open | Convenience for working hours |
| **Cover Order (CO)** | Market order with mandatory SL — enables higher leverage (intraday) | Intraday with risk control |
| **Bracket Order (BO)** | Entry + target + stop-loss in single order | Full position management |
| **Disclosed Quantity** | Reveals only a fraction of total order size to market | Large orders to avoid market impact |

---

## 5. Order Book Dynamics

```
Order Book Structure:
   BID SIDE (Buyers)      ASK SIDE (Sellers)
   ──────────────────     ─────────────────
   ₹100.00 × 5,000        ₹100.05 × 3,000   ← Best Ask (Offer)
   ₹99.95  × 12,000       ₹100.10 × 8,000
   ₹99.90  × 25,000       ₹100.20 × 15,000
   ↑ Best Bid

Spread = Best Ask − Best Bid = ₹100.05 − ₹100.00 = ₹0.05

Market Impact: A large market buy order will consume multiple ask levels,
               pushing the price up (positive slippage for buyer).
```

**Key Concepts:**
- **Bid-Ask Spread:** Tighter spreads = more liquid = less cost to trade.
- **Market Depth:** How much volume exists at each price level.
- **Iceberg Orders:** Large orders split and revealed partially to avoid market impact.
- **VWAP (Volume-Weighted Average Price):** Institutional benchmark for execution quality.
  ```
  VWAP = Σ(Price × Volume) / Σ(Volume)
  Buying below VWAP throughout day = outperforming the day's average fill.
  ```

---

## 6. Building Charting Features (India Context)

### Data Sources for Charts
| Source | Data Type | Cost | Latency |
|---|---|---|---|
| Zerodha Kite WebSocket | Real-time tick (LTP, OHLC, Volume, Depth) | Requires Kite Connect subscription | ~10ms |
| NSE Website | EOD historical data | Free | Next day |
| True Data | Intraday historical + live tick | Paid (~₹500–₹2000/month) | ~50ms |
| Global DataFeed | Historical + live tick | Paid | ~50ms |
| Yahoo Finance (yfinance) | EOD historical (delayed) | Free | 15-min delay |

### Charting Libraries (Open Source)
| Library | Language | Best For |
|---|---|---|
| **Lightweight Charts** (TradingView) | JavaScript | Professional candlestick charts in browser |
| **ECharts** | JavaScript | Highly customizable; good for dashboards |
| **Plotly** | Python / JS | Research, Jupyter notebooks |
| **Matplotlib + mplfinance** | Python | Backtesting visualizations |
| **D3.js** | JavaScript | Fully custom, max flexibility |

### OHLCV Data Format (Standard)
```json
{
  "symbol": "NIFTY50",
  "exchange": "NSE",
  "interval": "5min",
  "candles": [
    {
      "timestamp": "2025-04-04T09:15:00+05:30",
      "open": 22450.30,
      "high": 22489.75,
      "low": 22440.10,
      "close": 22475.50,
      "volume": 1250000
    }
  ]
}
```
