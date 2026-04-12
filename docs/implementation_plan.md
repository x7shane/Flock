# Flock — Implementation Plan (v1.1)

> This is a **thinking document**, not a final blueprint. River & Shades discuss openly here.
> Nothing is set in stone until both co-founders agree.
>
> **v0.2 Changes:** Tech stack updated (PostgreSQL, Go migration path), simulation confirmed
> (Monte Carlo + Historical for MVP, GARCH for V2), scoring factors now extensible + educational.
>
> **v1.1 Changes:** Added Git Agent, Code Reviewer Agent, and Test Agent to the agent map.
> Added formal V2 Backlog section to track deferred items.

---

## 1. What Is Flock?

A **free, bootstrapped web platform** where Indian retail investors can:

1. Input their investment goals (capital, time horizon, max risk tolerance)
2. Explore a universe of fundamentally scored assets (stocks, gold, index funds/SIP)
3. Build a portfolio from that universe
4. See **probability-based outcomes** — how likely is this portfolio to hit their target, what are the risks, what's the volatility forecast

**We are NOT an advisor. We are an analytical mirror.** (Option C — Educational tool)

---

## 2. Asset Universe (Shades' Call)

| Asset Class           | Universe                                                      | Free Data Source                                           | Status            |
| --------------------- | ------------------------------------------------------------- | ---------------------------------------------------------- | ----------------- |
| **Equities**          | Nifty 200 (~200 stocks)                                       | `yfinance` (price) + `jugaad-data` (NSE data)              | ✅ Confirmed free |
| **Gold**              | Gold spot INR, SGB (Sovereign Gold Bonds)                     | `yfinance` (GC=F gold futures) + IBJA rates scraping       | ✅ Free           |
| **Index Funds / SIP** | Top mutual fund schemes (Nifty 50 index, Nifty Next 50, etc.) | `mfapi.in` (FREE, no API key needed) + `mftool` Python lib | ✅ Confirmed free |

**Data sources — all free, all community-built or open:**

- `yfinance` — Yahoo Finance wrapper. Most stable. Append `.NS` for NSE stocks.
- `jugaad-data` — Best-maintained NSE scraper. Has built-in caching. CLI + Python API.
- `mfapi.in` — REST API for mutual fund NAVs from AMFI. No auth needed. `GET api.mfapi.in/mf/{scheme_code}`
- `mftool` — Python lib wrapping AMFI data. Returns Pandas DataFrames.
- Gold: `yfinance` ticker `GC=F` (USD) converted to INR, or scrape IBJA for official INR gold rate.

> [!NOTE]
> All data sources are unofficial scrapers or wrappers. They're free but may break if source websites change. We accept this for MVP. Migration path: paid APIs (EODHD, Kite Connect) when revenue comes.

---

## 3. The Agents We Need to Build

Each agent is a specialized AI role with its own skill file. Here's what Flock needs:

### Agent Map

| Agent                              | Role                                                                                                                    | Skills it Needs                                              |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **River (Co-founder / Architect)** | Overall project oversight, architecture decisions, regulatory checks, skill updates                                     | Master SKILL.md (already built)                              |
| **Quant Agent**                    | Designs the scoring engine, probability models, volatility calculations                                                 | `algo_trading`, `market_microstructure`, new: `quant_models` |
| **Data Agent**                     | Builds and maintains the data pipeline — fetching, caching, cleaning stock/MF/gold data                                 | New: `data_pipeline` skill                                   |
| **UI/UX Agent**                    | Designs and builds the frontend — communicates with Google Stitch for UI generation                                     | New: `ui_ux_design` skill                                    |
| **Git Agent**                      | Manages git branches, pull requests, merges. Enforces branching strategy and commit standards.                          | New: `git_workflow` skill                                    |
| **Code Reviewer Agent**            | Reviews all code changes for quality, patterns, security, and performance before merge approval. Works with Test Agent. | New: `code_review` skill                                     |
| **Test Agent**                     | Writes and maintains automated tests (unit, integration, API). Validates coverage before reviewer approves.             | New: `test_engineering` skill                                |
| **Security Agent**                 | Reviews every component for security compliance before it ships                                                         | `fintech_security` (already built)                           |
| **Compliance Agent**               | Ensures every screen has proper disclaimers, no regulatory violations                                                   | `india_regulations` (already built)                          |

> [!IMPORTANT]
> **For each agent, we create a SKILL.md inside `.agents/skills/` that defines:**
>
> - What the agent knows
> - What tools/APIs it uses
> - What rules it must follow
> - What it delivers

### New Skill Files to Create

```
Flock/.agents/skills/
├── SKILL.md                      ← Master (done)
├── quant_models/SKILL.md         ← NEW: scoring formulas, simulation math, volatility models
├── data_pipeline/SKILL.md        ← NEW: fetcher patterns, caching, data cleaning, API reference
├── ui_ux_design/SKILL.md         ← NEW: design system, component library, Google Stitch integration
├── git_workflow/SKILL.md         ← NEW: branching strategy, PR workflow, commit standards
├── code_review/SKILL.md          ← NEW: review checklist, quality gates, patterns enforcement
├── test_engineering/SKILL.md     ← NEW: test strategies, coverage rules, fixture patterns
├── algo_trading/SKILL.md         ← Done
├── financial_modeling/SKILL.md   ← Done
├── fintech_architecture/SKILL.md ← Done
├── fintech_security/SKILL.md     ← Done
├── forex_trading/SKILL.md        ← Done
├── india_regulations/SKILL.md    ← Done
└── market_microstructure/SKILL.md ← Done
```

---

## 4. Tech Stack (Bootstrapped — All Free & Open Source)

### The Language Decision: Python Now, Go Later

**Why not Go from day 1?**
All our critical data libraries (`yfinance`, `jugaad-data`, `mfapi`, `mftool`, `numpy`, `scipy`, `pandas`) are **Python-only**. Rewriting them in Go would take months before we ship a single feature.

**The plan:**

- **MVP (Now):** Python + FastAPI. Ships fast, all libraries work natively.
- **V2 (When we scale):** Migrate the API gateway layer to Go for performance. Keep Python as computation workers behind gRPC. This is exactly what Zerodha did — started Python/Django, moved hot paths to Go.

```
MVP Architecture:          V2 Architecture (when needed):
[Frontend] → [FastAPI]     [Frontend] → [Go API Gateway] → [Python Workers via gRPC]
                ↓                              ↓
         [PostgreSQL]                    [PostgreSQL]
```

### Full Stack Table

| Layer                 | Choice                                  | Why                                                                                                        | Cost |
| --------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---- |
| **Backend (MVP)**     | Python 3.12 + FastAPI                   | All finance libraries native. Async. Auto-docs.                                                            | FREE |
| **Backend (V2 Path)** | Go API Gateway + Python Workers         | Go for concurrency + Python for computation                                                                | FREE |
| **Database**          | **PostgreSQL 16**                       | ACID-compliant, concurrent connections, avoids SQLite migration pain later. Production-grade from day one. | FREE |
| **Frontend**          | HTML + Vanilla CSS + JavaScript         | No build step, no node_modules, instant iteration. Premium dark UI.                                        | FREE |
| **Price Charts**      | Lightweight Charts (TradingView OSS)    | Professional candlestick charts. 70KB library.                                                             | FREE |
| **Stats Charts**      | Chart.js                                | Probability distributions, risk gauges, pie charts                                                         | FREE |
| **Simulation**        | NumPy + SciPy                           | Monte Carlo, statistical distributions, matrix operations                                                  | FREE |
| **MF Data**           | mfapi.in + mftool                       | Mutual fund NAVs from AMFI                                                                                 | FREE |
| **Stock Data**        | yfinance + jugaad-data                  | Historical OHLCV + NSE fundamentals                                                                        | FREE |
| **Gold Data**         | yfinance (GC=F) + IBJA scrape           | Gold spot price in INR                                                                                     | FREE |
| **Dev Server**        | Uvicorn + Gunicorn                      | ASGI server for FastAPI with worker processes                                                              | FREE |
| **OS**                | Linux (Ubuntu Server)                   | Open source, secure, what we're already on                                                                 | FREE |
| **Deployment**        | Render / Railway free tier (when ready) | Free tier for MVP traffic                                                                                  | FREE |
| **UI Design Tool**    | Google Stitch (via UI/UX Agent)         | Generate UI mockups and components                                                                         | FREE |

**Total monthly cost: ₹0**

> [!NOTE]
> **Why PostgreSQL over SQLite?** Shades correctly pushed for the optimal choice. SQLite is single-writer and struggles with concurrent access. PostgreSQL handles concurrent reads/writes, supports proper indexing for financial queries, and means we never face a painful migration. Docker makes PostgreSQL setup trivial: `docker run -d postgres:16`.

---

## 5. Simulation Methods — ✅ DECIDED

### MVP: Monte Carlo + Historical Simulation

| Method                         | Role in Flock                                                                   | Status        |
| ------------------------------ | ------------------------------------------------------------------------------- | ------------- |
| **Monte Carlo** (10,000 paths) | Core probability engine — "68% chance you hit 12% CAGR"                         | ✅ MVP        |
| **Historical Simulation**      | Stress test — "What if COVID-2020 / demonetization happened to YOUR portfolio?" | ✅ MVP        |
| **GARCH + Monte Carlo**        | Dynamic volatility modeling — more realistic during turbulent markets           | 📋 V2 Release |
| **Bootstrap Resampling**       | Fallback for stocks with <3 years of history                                    | 📋 V2 Release |

### Monte Carlo Engine Design

```
Inputs:  Stock returns (mean, covariance matrix), portfolio weights, capital, time horizon
Process: 10,000 simulated paths using Geometric Brownian Motion
Outputs:
  - Probability of hitting target return
  - Value at Risk (VaR) at 95% confidence
  - Max Drawdown probability
  - Expected return range (10th–90th percentile)
  - Optimal holding period suggestion
```

### Historical Stress Test Engine Design

```
Inputs:  User's portfolio, historical crisis periods database
Crisis Scenarios (pre-loaded):
  - 2008 Global Financial Crisis
  - 2013 Taper Tantrum (INR crash)
  - 2016 Demonetization
  - 2020 COVID Crash
  - 2022 FII Selloff
Outputs:
  - "During COVID-2020, your portfolio would have dropped X% and recovered in Y months"
  - Max drawdown per crisis
  - Recovery time estimation
```

### V2: GARCH Enhancement

```
Why GARCH matters: Standard Monte Carlo uses FIXED volatility.
Reality: Volatility CLUSTERS — bad days follow bad days.
GARCH captures this by modeling time-varying volatility.
Result: More realistic risk estimates during turbulent markets.
We build this after MVP validates that users care about volatility depth.
```

---

## 6. Fundamental Scoring — Factors & Weights

### Design Philosophy (Agreed with Shades)

1. **Factors are extensible** — we start with 16, but the system must support adding more without breaking scores.
2. **Factors are educational** — each factor on the UI will have a tooltip/explainer so users LEARN what ROE, Debt/Equity etc. mean while using Flock. This makes us an educational tool AND keeps us firmly in Option C territory.
3. **Pillar weights are user-customizable** — we provide a sensible default, but users can slide the weights to match their style (growth / value / balanced / conservative).

### Current Factor Library (v1 — Extensible)

| #   | Factor             | Pillar        | What It Measures                                      | User-Friendly Tooltip                                                           |
| --- | ------------------ | ------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------- |
| 1   | ROE                | Profitability | How efficiently the company uses shareholder money    | "High ROE = company makes good profits from the money shareholders invested"    |
| 2   | ROCE               | Profitability | Profitability relative to ALL capital (equity + debt) | "Measures how well the company uses ALL its money, not just shareholder money"  |
| 3   | Net Profit Margin  | Profitability | Profit after ALL expenses                             | "Out of every ₹100 earned, how much is actual profit?"                          |
| 4   | Revenue CAGR (3yr) | Growth        | Consistency of sales growth                           | "How fast has the company grown its sales over the last 3 years?"               |
| 5   | EPS Growth (3yr)   | Growth        | Earnings per share growth                             | "Is the company making more money for each share you own, year over year?"      |
| 6   | Debt/Equity        | Health        | Financial leverage / fragility                        | "How much borrowed money vs own money. Lower = safer."                          |
| 7   | Current Ratio      | Health        | Can the company pay its short-term bills?             | "Can the company pay bills due in the next 12 months? Above 1.5 = comfortable." |
| 8   | Interest Coverage  | Health        | Can it pay loan interest from profits?                | "How easily can profits cover loan interest? Higher = safer."                   |
| 9   | Free Cash Flow     | Health        | Actual cash generated after expenses                  | "After paying everything, how much real cash is left? Positive = good sign."    |
| 10  | P/E Ratio (TTM)    | Valuation     | Is the stock expensive relative to earnings?          | "How many years of current earnings does the stock price represent?"            |
| 11  | P/B Ratio          | Valuation     | Price relative to book (asset) value                  | "Are you paying more or less than the company's actual asset value?"            |
| 12  | PEG Ratio          | Valuation     | P/E adjusted for growth                               | "P/E considering growth. Below 1 = potentially undervalued grower."             |
| 13  | Dividend Yield     | Valuation     | Cash return percentage                                | "How much cash does the company pay you annually just for holding the stock?"   |
| 14  | Promoter Holding % | Quality       | Founder/owner skin in the game                        | "Do the company's owners own a big chunk of it? >50% = strong conviction."      |
| 15  | Promoter Pledge %  | Quality       | Owners borrowing against their shares                 | "Are owners using their shares as loan collateral? High = risky signal."        |
| 16  | FII/DII Trends     | Quality       | Are big institutional investors buying or selling?    | "Are professional investors increasing or decreasing their position?"           |

### Pillar Weights — User Customizable with Default Presets

**How it works in the UI:**

- User gets 5 sliders (one per pillar), each 0–100%.
- Total must equal 100%.
- Pre-built presets they can choose from:

| Preset                    | Profitability | Growth    | Health    | Valuation | Quality   | Who It's For                        |
| ------------------------- | ------------- | --------- | --------- | --------- | --------- | ----------------------------------- |
| **🟢 Balanced (Default)** | 20%           | 20%       | 25%       | 20%       | 15%       | Most users — safe starting point    |
| **🚀 Growth**             | 15%           | 35%       | 15%       | 15%       | 20%       | Users chasing high-growth companies |
| **🛡️ Value**              | 20%           | 10%       | 25%       | 35%       | 10%       | Graham-style bargain hunters        |
| **🏦 Conservative**       | 25%           | 10%       | 35%       | 15%       | 15%       | Capital preservation focus          |
| **🎛️ Custom**             | User sets     | User sets | User sets | User sets | User sets | Advanced users                      |

> [!IMPORTANT]
> **OPEN DISCUSSION — Shades, what should the DEFAULT preset be?**
> River's vote: **Balanced** — gives equal respect to all pillars. We can always change this based on user feedback.
> Alternative: Could we default to different presets based on the user's risk tolerance input? (Low risk → Conservative preset, High risk → Growth preset). This would be smart but adds UI complexity.

---

## 7. Rough Project Phases

| Phase         | What                                                                                                             | Status |
| ------------- | ---------------------------------------------------------------------------------------------------------------- | ------ |
| **Phase 0**   | ✅ Skill library built. Co-founder alignment.                                                                    | DONE   |
| **Phase 1**   | Build agent skill files (quant_models, data_pipeline, ui_ux_design, git_workflow, code_review, test_engineering) | TODO   |
| **Phase 1.5** | Setup Git Agent — branching strategy, branch protections, PR templates                                           | TODO   |
| **Phase 2**   | Project structure + DB schema + API contract + docker-compose                                                    | TODO   |
| **Phase 3**   | Data pipeline MVP — fetch & cache Nifty 200 + Gold + MF data                                                     | TODO   |
| **Phase 4**   | Fundamental scoring engine (Flock Score)                                                                         | TODO   |
| **Phase 5**   | Probability engine (Monte Carlo + Historical)                                                                    | TODO   |
| **Phase 6**   | Frontend MVP (planner tool — dark mode, charts)                                                                  | TODO   |
| **Phase 7**   | Test Agent writes test suites + Code Reviewer validates all modules                                              | TODO   |
| **Phase 8**   | Legal disclaimers, final polish                                                                                  | TODO   |
| **Phase 9**   | Deploy to free tier (Vercel/Render/Railway)                                                                      | TODO   |

---

## 8. Parking Lot (Discuss Later)

- [ ] **Lawyer for legal disclaimer** — draft ourselves for MVP, engage lawyer before public launch
- [ ] **SEBI RIA registration** — explore after MVP traction validates the idea
- [ ] **Paid data sources** — migrate to EODHD or Kite Connect when revenue begins
- [ ] **Mobile app** — web-first, mobile later based on user demand
- [ ] **User accounts & persistence** — MVP can be session-based (no login needed). Add accounts later.
- [ ] **Revenue model** — freemium? premium features? advisory upgrade? Decide after PMF.

---

## 9. V2 Backlog (Deferred from MVP Review)

Items flagged during the v1.0 plan review. These are **not blockers** for MVP but must be addressed in V2.

### Simulation & Modeling

- [ ] **GARCH + Monte Carlo** — Dynamic volatility modeling for turbulent markets
- [ ] **Bootstrap Resampling** — Fallback for stocks with <3 years of history
- [ ] **Fat-tail disclaimer** — GBM assumes log-normal returns; Indian mid/small caps have fat tails. Add statistical disclaimer to simulation output.
- [ ] **Rolling correlation windows** — Decide on correlation matrix recalculation frequency (currently undefined)

### Scoring Engine

- [ ] **Sector-relative scoring** — Score factors (e.g., ROE) against sector peers instead of absolute Nifty 200 ranking
- [ ] **Missing factor handling rules** — Define scoring behavior when a company lacks a factor (e.g., no dividends). Currently undefined.
- [ ] **Score recalculation cadence** — Batch nightly vs on-demand vs after each data refresh

### Data Pipeline

- [ ] **Paid data source migration** — EODHD / Kite Connect when revenue justifies it
- [ ] **Data staleness alerts** — If a fetch fails, serve cached data with "last updated X hours ago" warning
- [ ] **Rate limiting strategy** — Exponential backoff + per-source cooldowns for yfinance / jugaad-data
- [ ] **Data validation layer** — NaN handling, stock split adjustments, bonus adjustments before data hits PostgreSQL
- [ ] **Full historical gold analysis** — Beyond simple allocation

### Frontend & UX

- [ ] **Auto-select preset based on risk tolerance** — Low risk → Conservative, High risk → Growth (adds UI complexity)
- [ ] **User accounts & portfolio persistence** — Login, saved portfolios, session history
- [ ] **Mobile app** — Web-first, mobile on user demand

### Compliance & Legal

- [ ] **Disclaimer framework** — Define which disclaimers appear on which screens, exact legal language
- [ ] **Terms of Use gate** — Require acceptance before tool access
- [ ] **SEBI RIA registration** — Explore after MVP traction
- [ ] **Lawyer engagement** — Professional legal review before public launch

### Architecture

- [ ] **Go API Gateway migration** — Move hot paths to Go, keep Python as gRPC workers
- [ ] **Crisis period seed data file** — Externalize crisis definitions (dates, sectors) from code to config

---

## Final Decisions (From Shades)

All open questions have been resolved for the MVP:

1. **Simulation approach:** Monte Carlo + Historical for MVP. GARCH for V2.
2. **Scoring weights:** User-customizable with presets. The **DEFAULT** preset will be used for simplicity at launch.
3. **Gold representation:** Simple gold allocation for MVP. Full historical gold analysis will be a V2 feature.
4. **Index Fund SIP:** Built as a **separate SIP calculator** in the MVP, as monthly flow math differs from lump-sum portfolio analysis.
5. **Agent priority:** We will build the **Quant Agent** first, as the statistical logic forms the core engine of Flock.

---

> **Plan Status:** APPROVED (v1.1)
> **Next Step:** Create remaining agent skill files (git_workflow, code_review, test_engineering, quant_models, data_pipeline, ui_ux_design), then project structure setup.
