---
name: forex_trading
description: >
  Forex and currency markets reference for River — covering forex fundamentals
  (pairs, pips, spreads, leverage), FEMA regulations for Indian residents, INR
  currency derivatives on NSE/BSE, cross-border payment infrastructure, and how
  fintech companies handle foreign exchange exposure. Use when dealing with
  currency trading features, cross-border payments, or any FX-related product.
---

# Forex & Currency Markets — River's Reference

> **RULE FOR INDIA:** Retail forex speculation on offshore spot platforms is
> ILLEGAL under FEMA. Never build a product that facilitates this for Indian users.
> All currency trading features must use SEBI-registered exchanges (NSE/BSE) only.
> When in doubt — check `india_regulations/SKILL.md` and consult legal counsel.

---

## 1. Forex Fundamentals

### 1.1 Currency Pairs

**Structure:**
```
EUR/USD = 1.0850
 ↑    ↑       ↑
Base Quote  Exchange Rate
Currency Currency (How many Quote units per 1 Base unit)

EUR = Euro (Base)   → What you're buying or selling
USD = US Dollar (Quote) → The pricing currency
Rate = 1.0850 means 1 Euro costs 1.0850 US Dollars
```

**Pair Categories:**
| Category | Description | Examples | Spread |
|---|---|---|---|
| **Majors** | USD paired with 7 major currencies | EUR/USD, GBP/USD, USD/JPY, USD/CHF | Tightest (0.1–1 pip) |
| **Minors / Crosses** | Major currencies without USD | EUR/GBP, EUR/JPY, GBP/JPY | Moderate (1–3 pips) |
| **Exotics** | Major currency + emerging market currency | USD/INR, USD/BRL, EUR/TRY | Wide (5–50 pips) |

**INR-Specific Pairs (India Legal):**
```
USD/INR  — Most liquid INR pair in India
EUR/INR  — Available on NSE
GBP/INR  — Available on NSE
JPY/INR  — Available on NSE (quoted as JPY per 100 units in India)

Cross-currency (no INR — available on NSE since 2018):
EUR/USD, GBP/USD, USD/JPY
```

---

### 1.2 Pips, Lots, Spreads

**Pip (Percentage in Point):**
```
Most pairs:    1 pip = 0.0001 (4th decimal place)
               EUR/USD moves from 1.0850 → 1.0851 = +1 pip

JPY pairs:     1 pip = 0.01 (2nd decimal place)
               USD/JPY moves from 149.50 → 149.51 = +1 pip

USD/INR:       1 pip = 0.0025 (contract specification on NSE)
               USD/INR moves from 83.50 → 83.5025 = +1 pip
```

**Lot Sizes (India NSE Currency Derivatives):**
```
USD/INR:   1 lot = USD 1,000
EUR/INR:   1 lot = EUR 1,000
GBP/INR:   1 lot = GBP 1,000
JPY/INR:   1 lot = JPY 100,000
```

**Pip Value Calculation (USD/INR example):**
```
Contract size    = USD 1,000
1 pip            = ₹0.0025
Pip Value/lot    = USD 1,000 × 0.0025 = ₹2.50 per lot

If you trade 10 lots:
  Movement of 1 pip = ₹25.00 P&L
  Movement of 100 pips = ₹2,500 P&L
```

**Spread:**
```
Bid Price:  What the market pays you to SELL base currency
Ask Price:  What you pay to BUY base currency
Spread    = Ask − Bid (Your immediate cost on entry)

Example USD/INR:
  Bid: 83.5000 | Ask: 83.5025
  Spread = 0.0025 = 1 pip

Types:
  Fixed Spread:    Stays constant regardless of market conditions
  Variable Spread: Widens during news events and low liquidity
```

---

### 1.3 Leverage & Margin

**How Leverage Works:**
```
Leverage 50:1 means:
  You control ₹50 of currency for every ₹1 of margin

Example (USD/INR futures, 10 lots):
  Contract value = 10 × USD 1,000 = USD 10,000 = ~₹8,30,000
  Margin required (typically 2–5%) = ~₹16,600–₹41,500
  Leverage = ₹8,30,000 / ₹41,500 ≈ 20:1

Risk: A 1% adverse move = 20% loss on your margin.
      If USD/INR moves 83 paise against you → margin call.
```

**India-Specific Margin (NSE Currency Derivatives):**
```
Initial Margin = SPAN Margin + Exposure Margin
  SPAN Margin:     Calculated by NSE's risk engine (typically 1.5–3% of contract value)
  Exposure Margin: Additional buffer (typically 1% of contract value)

Margin for USD/INR futures (1 lot = USD 1,000):
  At rate of ₹83.50 → Contract value ≈ ₹83,500
  SPAN (~2%) ≈ ₹1,670
  Exposure (~1%) ≈ ₹835
  Total margin per lot ≈ ₹2,500–₹3,500 (varies daily)
```

---

## 2. India Forex Regulations (FEMA Deep Dive)

### 2.1 Legal Framework
- **FEMA (Foreign Exchange Management Act), 1999:** Governs all foreign exchange transactions for Indian residents.
- **RBI:** Issues circulars that modify FEMA rules (follow RBI Master Direction on Risk Management and Interbank Dealings).
- **SEBI:** Regulates currency derivatives on Indian exchanges.

### 2.2 What Indian Residents CAN Do

| Activity | Allowed | Conditions |
|---|---|---|
| Trade USD/INR futures (NSE/BSE) | ✅ Yes | Via SEBI-registered broker |
| Trade EUR/INR, GBP/INR, JPY/INR futures | ✅ Yes | Via SEBI-registered broker |
| Trade EUR/USD, GBP/USD, USD/JPY cross-currency futures (NSE) | ✅ Yes | No underlying exposure needed (post-2018 NSE rules) |
| Trade currency options (USD/INR) | ✅ Yes | European-style only |
| Hedge genuine forex exposure | ✅ Yes | Must have documented underlying exposure |
| Open foreign currency account abroad (FCNB/FCNR) | ✅ Yes | Specific purpose accounts |
| Remit money abroad under LRS | ✅ Yes | Up to USD 2,50,000 per financial year |

### 2.3 What Indian Residents CANNOT Do

| Activity | Status | Penalty |
|---|---|---|
| Trade on offshore spot forex platforms (FOREX.com, XM, IC Markets, OANDA) | ❌ ILLEGAL | FEMA: Up to 3× amount + imprisonment up to 3 years |
| Trade CFDs (Contracts for Difference) on any asset | ❌ ILLEGAL | Same |
| Trade binary options | ❌ ILLEGAL | Same + IT Act provisions |
| Use LRS remittances for speculative forex trading | ❌ ILLEGAL | FEMA + Income Tax scrutiny |
| Maintain a foreign forex trading account funded from India | ❌ ILLEGAL | Same |
| Accept crypto as payment in lieu of forex settlement | ❌ Grey Zone | Treat as illegal until RBI clarifies |

> ⚠️ **As a fintech founder:** If ANY user asks about offshore forex platforms — this is a legal red line.
> Our platform must NOT facilitate, link to, or implicitly endorse offshore forex trading for Indian users.
> This is a SEBI + RBI + ED (Enforcement Directorate) triple-threat risk.

---

### 2.4 Underlying Exposure Requirement
Per RBI circulars:
- Large positions in currency derivatives (especially beyond USD 100 million equivalent) require **documented underlying foreign currency exposure** (import/export contracts, ECB loan, etc.).
- **For small retail traders:** RBI allows limited speculative positions without underlying exposure — but the intent of the framework is hedging, not speculation.

---

## 3. Forex Market Structure

### Global Forex Market Hours
```
Market sessions (IST = UTC+5:30):
  Sydney:    5:00 AM – 2:00 PM IST
  Tokyo:     6:30 AM – 3:30 PM IST
  London:    1:30 PM – 10:30 PM IST  ← Highest liquidity
  New York:  6:30 PM – 1:30 AM IST
  Overlap:   London + New York (6:30 PM – 10:30 PM IST) = Peak Volume

India NSE Currency Segment:    9:00 AM – 5:00 PM IST (Mon–Fri)
```

### Key Market Drivers
| Driver | Impact |
|---|---|
| **Interest Rate Differentials** | Higher interest rates → currency appreciation (carry trade) |
| **Inflation Data (CPI/WPI)** | Higher inflation → currency depreciation |
| **Current Account Deficit/Surplus** | India's CAD = structural INR weakness driver |
| **FII/FPI Flows** | Foreign investor buying Indian equity/debt → INR strengthens |
| **RBI Intervention** | RBI buys/sells USD to manage USD/INR volatility |
| **Crude Oil Prices** | India imports 85% of oil needs → Higher crude = INR weakens |
| **US Federal Reserve Policy** | Fed rate hike → USD strength → INR weakens |
| **Geopolitical Events** | Risk-off = USD/JPY/CHF strengthens; INR and EM currencies weaken |

### USD/INR Specific Dynamics
```
Key Structural Factors:
- India has persistent Current Account Deficit (CAD) → structural USD demand → INR weakness bias
- RBI actively manages USD/INR (does not freely float)
- RBI maintains forex reserves (~USD 650+ billion) to defend INR
- Range-bound behaviour in short term; secular depreciation over long-term

Historical Context:
  2005: ₹43/USD    2010: ₹45/USD    2015: ₹65/USD
  2020: ₹75/USD    2023: ₹83/USD    (gradual structural depreciation)
```

---

## 4. Forex for Fintech Products

### 4.1 Cross-Border Payments (Legal Framework)

| Use Case | Mechanism | Regulation |
|---|---|---|
| **Outward Remittance** (India → Abroad) | LRS (Liberalised Remittance Scheme) | Max USD 2,50,000/year/resident. Purpose determines tax/TCS. |
| **Inward Remittance** (Abroad → India) | FIRC (Foreign Inward Remittance Certificate) issued by AD bank | Must be received through authorized dealer bank |
| **Export Payments** | FEMA compliant bank account; SOFTEX filing for software exports | AD-I bank authorization needed |
| **Import Payments** | Via AD bank, specific purpose | BOE (Bill of Entry) required |

**TCS on LRS (Tax Collected at Source) — Current Rules:**
```
Purpose               TCS Rate
Education loan        0.5% above ₹7 lakh
Education (direct)    5% above ₹7 lakh
Medical               5% above ₹7 lakh
Other purposes        20% above ₹7 lakh (significantly increased in 2023)
```

### 4.2 Forex Risk Management for Fintech Companies

If you build a product that holds foreign currency balances or settles cross-border:

| Risk | Description | Hedge |
|---|---|---|
| **Translation Risk** | USD-denominated revenue converted to INR at unfavorable rate | Forward contracts or USD/INR futures hedge |
| **Transaction Risk** | FX rate moves between agreement and settlement | Buy forward cover equal to exposure |
| **Economic Risk** | Long-term business impact of exchange rate movements | Natural hedge — match revenue and cost currencies |

**Natural Hedge Example:**
```
If you earn USD from international clients and pay USD for AWS/cloud:
  USD inflows offset USD outflows → reduced net USD/INR exposure
  Only hedge the NET exposure, not gross flows
```

### 4.3 Forex APIs for Fintech Products

| Provider | Use Case | Cost |
|---|---|---|
| **Razorpay / Cashfree** | Accept international payments in INR equivalent | Per-transaction fee |
| **PayPal / Stripe** | International card acceptance (supports INR settlement) | 2–3% per transaction + conversion fee |
| **Wise (TransferWise) API** | Cross-border money transfer at near-mid-market rates | Subscribe to API; per-conversion fee |
| **Open Exchange Rates API** | Real-time and historical FX rates (data only) | Free tier available |
| **Fixer.io** | Currency conversion rates API | Freemium |
| **RBI Reference Rate** | Official RBI USD/INR reference rate (non-commercial) | Free — scrape from RBI website |

```python
# Get RBI reference rate (INR/USD) — scrape approach
import requests
from bs4 import BeautifulSoup

def get_rbi_reference_rate():
    url = "https://www.rbi.org.in/scripts/ReferenceRateArchive.aspx"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Parse the table for USD/INR reference rate
    # Always use this for regulatory/reporting purposes
    pass  # Complete implementation per RBI's page structure
```

---

## 5. Quick Reference Numbers

| Parameter | Value |
|---|---|
| LRS Annual Limit | USD 2,50,000 per resident per financial year |
| TCS on LRS (non-education/medical) | 20% above ₹7 lakh |
| NSE Currency Segment Hours | 9:00 AM – 5:00 PM IST |
| USD/INR Lot Size (NSE) | USD 1,000 per lot |
| FEMA Violation Penalty | Up to 3× amount involved + up to 3 years imprisonment |
| RBI Forex Reserves (approx.) | ~USD 650 billion (2025) |
| India Current Account Deficit | Structural feature — approximately 1–2% of GDP |
| India Crude Oil Import Dependence | ~85% of oil demand met by imports |
