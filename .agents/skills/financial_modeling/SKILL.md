---
name: financial_modeling
description: >
  Financial modeling and investment philosophy reference for River — covering
  valuation methodologies (DCF, WACC, comps), investment principles from Graham,
  Soros, Taleb, and Lewis, startup fundraising math, and unit economics for
  fintech businesses. Use during fundraising, product pricing, M&A evaluations,
  or investor conversations.
---

# Financial Modeling — River's Reference

> **RULE:** A model is only as good as its assumptions. Always stress-test every
> model against a bear case, base case, and bull case. Never present a single
> number as "the answer."

---

## 1. Core Valuation Methodologies

### 1.1 Comparable Companies Analysis (Trading Comps)

**How it works:** Find 5–10 publicly traded peers. Extract their valuation multiples. Apply to your company's metrics.

**Common Multiples:**
| Multiple | Formula | Use Case |
|---|---|---|
| EV/EBITDA | Enterprise Value ÷ EBITDA | Mature profitable companies |
| EV/Revenue | Enterprise Value ÷ Revenue | Early-stage, high-growth (fintech) |
| P/E | Stock Price ÷ EPS | Profitable, stable companies |
| P/B | Stock Price ÷ Book Value per Share | Banking / financial institutions |
| Price/FCF | Stock Price ÷ Free Cash Flow per Share | Capital-efficient businesses |

**Enterprise Value:**
```
Enterprise Value (EV) = Market Cap + Total Debt − Cash & Equivalents
```

**Indian Fintech Comparable Peers:**
- Paytm (One97 Communications), PB Fintech (PolicyBazaar), Fino Payments Bank, Navi Technologies
- For benchmarking: also look at global comparables (SoFi, Nu Holdings, Revolut last disclosed round)

---

### 1.2 Precedent Transactions Analysis

- Look at past M&A deals in the same sector (Indian fintech acquisitions: BharatPe-PMC Bank, Slice-NESFB merger, InsuranceDekho rounds).
- Precedent multiples typically **20–30% higher** than trading comps due to **control premium**.
- Sources: VCCEdge, Tracxn, Crunchbase, Bloomberg (for disclosed deals).

---

### 1.3 Discounted Cash Flow (DCF)

**Step-by-Step:**

**Step 1: Project Free Cash Flow (FCF) — 5 years**
```
FCF = EBIT × (1 − Tax Rate) + D&A − ΔWorking Capital − CapEx

For fintech startups (pre-profit):
  - Use Revenue × (Gross Margin % − OpEx %) as proxy
  - Conservative: project 3 years explicitly; beyond = terminal value
```

**Step 2: Calculate WACC**
```
WACC = (E/V × Re) + (D/V × Rd × (1 − Tax Rate))

Where:
  E = Market Value of Equity
  D = Market Value of Debt
  V = E + D
  Re = Cost of Equity = Rf + β × (Rm − Rf)
     Rf = Risk-free rate (India 10-yr G-Sec yield ≈ 6.8–7.2%)
     β  = Beta of comparable public companies
     Rm − Rf = India equity risk premium ≈ 6–8%
  Rd = Cost of Debt (interest rate on borrowings)
  Tax Rate = India corporate tax ≈ 25.17% (domestic companies)
```

**Step 3: Terminal Value**
```
Gordon Growth Model: TV = FCF_n × (1 + g) / (WACC − g)
  g = terminal growth rate (conservative: India GDP growth ≈ 6–7%)

Exit Multiple Method: TV = EBITDA_n × Exit Multiple
  (Use sector comps for exit multiple — e.g., 15–20× for fintech in India)
```

**Step 4: Sum PV of FCFs + PV of Terminal Value**
```
Intrinsic Value = Σ [FCFt / (1 + WACC)^t] + [TV / (1 + WACC)^n]
```

**DCF Sense Checks:**
- If terminal value > 70% of total value → model is too back-loaded; revisit growth assumptions.
- Always run sensitivity table: WACC ± 1% vs. terminal growth ± 0.5%.

---

### 1.4 Startup Valuation (Pre-Revenue / Early Stage)

Institutional investors in India use a mix of:
- **VC Method:** Work backwards from expected exit value.
  ```
  Post-Money Valuation = Exit Value in Year 5 / (1 + Target IRR)^5
  Target IRR for India VC: 25–35% (Series A), 20–25% (Series B+)
  ```
- **Berkus Method / Scorecard Method:** Subjective scoring of team, product, market, etc. Typically yields ₹5–25 Cr pre-money for pre-revenue Indian fintech.
- **Revenue Multiple:** For SaaS/fintech with ARR — typical range 5–15× ARR (2024 environment).

---

## 2. Unit Economics (Fintech-Specific)

### Key Metrics Every Fintech Must Track
| Metric | Formula | Healthy Benchmark (Fintech) |
|---|---|---|
| **CAC** (Customer Acquisition Cost) | Total Sales & Marketing Spend / New Customers | ₹500–₹2,000 for retail fintech |
| **LTV** (Lifetime Value) | ARPU × Gross Margin % × Customer Lifespan | LTV ≥ 3× CAC |
| **LTV:CAC Ratio** | LTV / CAC | > 3:1 (seek > 5:1 for capital efficiency) |
| **Payback Period** | CAC / Monthly Contribution Margin | < 18 months for fintech |
| **ARPU** (Avg Revenue Per User) | Total Revenue / Active Users | Depends on product |
| **Churn Rate** | Users Lost / Starting Users (monthly) | < 2–3% monthly for fintech |
| **Take Rate** | Platform Revenue / GMV × 100 | 0.5–3% for payment platforms |
| **NDR** (Net Dollar Retention) | (Revenue from existing users, period end) / (Revenue from same users, period start) | > 110% = excellent |
| **Burn Multiple** | Net Burn / Net New ARR | < 1.5× = efficient |
| **Gross Margin** | (Revenue − COGS) / Revenue | 50–75% for fintech (pure software higher) |

---

## 3. Investment Philosophy Principles

### Graham — Value Investing
- **Intrinsic Value:** Based on fundamentals, not market sentiment. Calculate it independently.
- **Margin of Safety:** Buy at significant discount to intrinsic value (≥ 30% for Graham).
- **Mr. Market:** Market is your servant, not your master. Use irrational prices as opportunities.
- **Preferred Metrics:** P/B < 1.5, P/E < 15, Debt/Equity < 0.5, Current Ratio > 2.
- **Application:** When evaluating a potential acquisition or investment — calculate intrinsic value first. If market price > IV, walk away regardless of hype.

### Soros — Reflexivity
- Markets are NOT efficient. Participant expectations shape fundamentals (feedback loops).
- Identify self-reinforcing trends early (boom). Identify reversal signals before the bust.
- **Application for product:** User behaviour shapes your platform's value (network effects). Manage the flywheel; don't let it spin out of control. A viral feature that attracts bad actors can destroy trust instantly.

### Taleb — Antifragility
- **Black Swan events are NOT unpredictable by nature — they are only unpredictable within flawed models.**
- Build systems that gain from volatility: hold cash reserves, avoid single points of failure, maintain optionality.
- **Barbell Strategy:** 90% in very safe/boring infrastructure + 10% in high-risk/high-reward bets. Never the middle (moderate risk = worst of both worlds).
- **Application:** Keep core payment rails boring and redundant. Experiment aggressively only in non-critical features.

### Lessons from Finance History
| Book | Core Lesson | Applied to Our Company |
|---|---|---|
| *Liar's Poker* | Culture of short-termism destroys companies | Set long-term incentives; don't chase quarterly numbers |
| *When Genius Failed* | Extreme leverage + correlation breakdown = catastrophe | Cap leverage in any product at safe multiples with real-time risk checks |
| *The Big Short* | Complexity hides toxicity | Product must be simple enough for users to understand what they're buying |
| *Flash Boys* | Speed asymmetry creates unfair markets | If we build an algo platform — ensure retail users have fair access to execution |
| *The Black Swan* | Fat-tail events are inevitable | Our infra must survive a 10× traffic spike, a partner bank failure, and a regulatory change simultaneously |

---

## 4. Fundraising Reference (India Ecosystem)

### Funding Stage Benchmarks (India Fintech, 2024–2025)
| Stage | Typical Raise | Valuation Range | What Investors Expect |
|---|---|---|---|
| Pre-Seed | ₹50L – ₹2 Cr | ₹2–10 Cr | Strong founder-market fit, problem clarity |
| Seed | ₹2–10 Cr | ₹10–50 Cr | MVP, early users, initial revenue signal |
| Series A | ₹25–100 Cr | ₹100–500 Cr | PMF, LTV:CAC > 3×, growing MoM |
| Series B | ₹100–500 Cr | ₹500 Cr – ₹2,000 Cr | Unit economics positive, path to profitability |

### Key Indian Fintech Investors (Reference)
- **Early Stage:** Blume Ventures, Stellaris, Axilor, 100X.VC, Surge (Sequoia)
- **Growth Stage:** Peak XV (Sequoia India), Accel, Tiger Global, Matrix Partners India
- **Strategic:** Razorpay, BharatPe (as strategic angels), HDFC Bank (for banking partnerships)

### Term Sheet Key Terms
| Term | What to Watch Out For |
|---|---|
| **Pro-rata rights** | Investor right to maintain ownership % in future rounds |
| **Anti-dilution** | Broad-based weighted average (acceptable) vs. full ratchet (avoid) |
| **Liquidation preference** | 1× non-participating (fair) vs. 2× participating (avoid at Seed) |
| **Drag-along rights** | Majority can force minority to approve M&A — ensure governance protections |
| **ESOP pool** | Typically 10–15% reserved; created pre-money (dilutes founders, not investors) |
