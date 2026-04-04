---
name: ui_ux_design
description: >
  UI/UX Agent — designs and builds the Flock frontend using Google Stitch via MCP.
  Generates screens, iterates on layouts, and extracts production HTML/CSS through
  the Stitch MCP server. Owns the design system, user flows, chart integration,
  and educational tooltips.
---

# UI/UX Design Agent — Flock's Visual Layer

> **RULE:** Every screen must feel premium. Dark mode, smooth animations, professional
> charts. If it looks like a homework project, we've failed. Flock should feel like
> Bloomberg Terminal meets Zerodha — powerful but approachable.
>
> **PRIMARY TOOL:** Google Stitch via MCP server. Design screens in Stitch, iterate
> with variants, extract production HTML/CSS, implement in the frontend.

---

## 1. Google Stitch — Design Generation via MCP

### What is Stitch?

Google Stitch is an AI-native UI design platform that generates responsive layouts, mockups,
and frontend code from natural language prompts. The UI/UX Agent uses Stitch as its primary
design tool through the **Model Context Protocol (MCP)** — meaning the agent can programmatically
create, iterate, and export designs without leaving the development environment.

### MCP Server Setup

**Prerequisites:**
- Google Cloud project with billing enabled and Stitch API enabled
- Node.js 18+
- `gcloud auth login` + `gcloud auth application-default login`

**Configuration (add to MCP client config):**

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["-y", "@_davideast/stitch-mcp", "proxy"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "flock-fintech"
      }
    }
  }
}
```

**Automated setup (alternative):**
```bash
npx @_davideast/stitch-mcp init
# Walks through client selection, auth, and config generation
```

**Verify installation:**
```bash
npx @_davideast/stitch-mcp doctor
```

### Available MCP Tools

| Tool | Purpose | When to Use |
|---|---|---|
| `create_project` | Start a new Stitch workspace | Once at project start — create "Flock" project |
| `list_projects` | List available Stitch projects | Verify project exists |
| `get_project` | Get project details | Check project state |
| `generate_screen_from_text` | Generate a UI screen from a natural language prompt | Primary design generation — every new screen |
| `edit_screen` | Modify an existing screen | Iterating on feedback |
| `generate_variants` | Explore different layouts/color schemes | A/B exploration before committing |
| `list_screens` | List screens in a project | Navigation and tracking |
| `fetch_screen_code` | Download HTML/CSS for a screen | Extract production code |
| `fetch_screen_image` | Download a screenshot of a screen | Documentation, review, sharing |
| `extract_design_context` | Extract "Design DNA" (fonts, colors, layout rules) | Maintain consistency across screens |
| `build_site` | Map screens to routes and build a site | Assemble the final frontend |

### Design Workflow (Stitch-First)

```
1. Create Flock project in Stitch
   → create_project("Flock — Portfolio Planner")

2. Feed design system context
   → Use extract_design_context or pass CSS variables as prompt context

3. Generate each screen with detailed prompts
   → generate_screen_from_text("Dark fintech dashboard showing...")

4. Generate variants for A/B exploration
   → generate_variants(screen_id, 3)  # 3 alternatives

5. Select best variant, iterate with edit_screen
   → edit_screen(screen_id, "Make the CTA button more prominent, add glow effect")

6. Extract production HTML/CSS
   → fetch_screen_code(screen_id)  # Ready for implementation

7. Assemble into site
   → build_site({"screens": [{"route": "/", "screen_id": "..."}, ...]})
```

### Screen Generation Prompts

When calling `generate_screen_from_text`, include Flock's design DNA in every prompt:

```
Context: Fintech portfolio planning tool. Dark mode UI.
Colors: Deep navy (#0a0e17) background, blue (#3b82f6) accent, 
green (#10b981) for positive, red (#ef4444) for negative.
Font: Inter. Style: Bloomberg Terminal meets Zerodha — premium and approachable.
Charts: TradingView Lightweight Charts for prices, Chart.js for statistics.

Screen: [describe the specific screen here]
```

**Example prompts for Flock screens:**

| Screen | Prompt Summary |
|---|---|
| **Landing** | "Hero section with headline 'What if you could see your portfolio's future?' dark gradient background, glowing CTA button, animated particle effect" |
| **Goal Input** | "Form with capital input (INR), time horizon slider (1-30 years), risk tolerance slider (Conservative to Aggressive), dark card layout" |
| **Stock Explorer** | "Sortable data table with Flock Score badges (color-coded 0-100), sector tags, mini sparkline charts, search/filter bar" |
| **Portfolio Builder** | "Split panel: left side stock list with weight sliders, right side live pie chart, preset buttons (Balanced/Growth/Value/Conservative)" |
| **Results Dashboard** | "Monte Carlo distribution chart (histogram), key stat cards (VaR, CAGR range, probability), historical crisis cards with drawdown percentages" |
| **SIP Calculator** | "Clean form with monthly amount, return rate, horizon inputs. Results panel with future value, wealth gain, animated counter" |

---

## 1. Design System

### Color Palette — Dark Mode First

```css
:root {
  /* Backgrounds */
  --bg-primary:     #0a0e17;     /* Deep navy — main background */
  --bg-secondary:   #111827;     /* Card backgrounds */
  --bg-tertiary:    #1a2332;     /* Elevated cards, modals */
  --bg-hover:       #1e2a3a;     /* Hover states */

  /* Text */
  --text-primary:   #f1f5f9;     /* Main text — near white */
  --text-secondary: #94a3b8;     /* Muted text, labels */
  --text-muted:     #64748b;     /* Disabled, placeholder */

  /* Accent — Flock Brand */
  --accent-primary: #3b82f6;     /* Blue — primary actions */
  --accent-hover:   #2563eb;     /* Blue hover */
  --accent-glow:    rgba(59, 130, 246, 0.15); /* Glow effect */

  /* Semantic Colors */
  --success:        #10b981;     /* Green — positive returns, good scores */
  --warning:        #f59e0b;     /* Amber — caution, medium scores */
  --danger:         #ef4444;     /* Red — negative returns, risk alerts */
  --info:           #6366f1;     /* Indigo — informational */

  /* Borders */
  --border-subtle:  #1e293b;     /* Subtle borders */
  --border-default: #334155;     /* Standard borders */

  /* Shadows */
  --shadow-sm:      0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md:      0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg:      0 8px 24px rgba(0, 0, 0, 0.5);
  --shadow-glow:    0 0 20px var(--accent-glow);

  /* Spacing Scale */
  --space-xs:  4px;
  --space-sm:  8px;
  --space-md:  16px;
  --space-lg:  24px;
  --space-xl:  32px;
  --space-2xl: 48px;

  /* Border Radius */
  --radius-sm:  6px;
  --radius-md:  10px;
  --radius-lg:  16px;
  --radius-xl:  24px;
  --radius-full: 9999px;

  /* Typography */
  --font-sans: 'Inter', -apple-system, system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

### Typography Scale

```css
/* Import Inter from Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.text-xs   { font-size: 0.75rem; line-height: 1rem; }
.text-sm   { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg   { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl   { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl  { font-size: 1.5rem; line-height: 2rem; font-weight: 600; }
.text-3xl  { font-size: 1.875rem; line-height: 2.25rem; font-weight: 700; }
```

---

## 2. User Flow

### Primary Flow: Portfolio Planner

```
[1. Landing Page]
  "What if you could see your portfolio's future?"
  → CTA: "Start Planning" button
        ↓
[2. Goal Input]
  - Investment capital (INR)
  - Time horizon (years)
  - Risk tolerance (slider: Conservative → Aggressive)
  → "Explore Stocks" button
        ↓
[3. Stock Explorer]
  - Sorted by Flock Score (default preset matches risk tolerance)
  - Table: Ticker | Name | Sector | Flock Score | Price | 1Y Return
  - Click any stock → Stock Detail card (mini chart + factor breakdown)
  - "Add to Portfolio" button per stock
        ↓
[4. Portfolio Builder]
  - Selected stocks shown with weight sliders (default: equal weight)
  - Real-time pie chart of allocation
  - Pillar weight preset selector (Balanced/Growth/Value/Conservative/Custom)
  → "Simulate" button
        ↓
[5. Results Dashboard]
  - Monte Carlo probability distribution chart
  - Key stats: Prob of positive return, VaR, Expected CAGR range
  - Historical stress test cards (5 crises)
  - "What if COVID happened to YOUR portfolio?" narrative boxes
  → "Modify Portfolio" (goes back to step 4)
  → "Start Over" (goes back to step 2)
```

### Secondary Flow: SIP Calculator

```
[SIP Page]
  - Monthly SIP amount
  - Expected annual return (or fund selection)
  - Time horizon
  - Step-up percentage (optional)
  → Results: Total invested, Future value, Wealth gain, CAGR
```

---

## 3. Key Screens & Components

### 3.1 Navigation

- **Top navbar**: Logo (left) | Stock Explorer | SIP Calculator | About (right)
- Sticky, glass-morphism background: `backdrop-filter: blur(12px); background: rgba(10, 14, 23, 0.8);`
- Active page indicator: underline with `--accent-primary`

### 3.2 Cards (Primary UI Element)

```css
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.card:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}
```

### 3.3 Flock Score Badge

Visual score indicator — color-coded by range:

```
90-100: 🟢 Excellent (--success)
70-89:  🔵 Good (--accent-primary)
50-69:  🟡 Average (--warning)
30-49:  🟠 Below Average (blend warning/danger)
0-29:   🔴 Poor (--danger)
```

Display as a circular gauge or pill badge with gradient fill.

### 3.4 Factor Tooltips (Educational)

Every factor in the scoring breakdown must have a `?` icon that reveals a tooltip:

```css
.tooltip {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  font-size: 0.8rem;
  color: var(--text-secondary);
  max-width: 280px;
  box-shadow: var(--shadow-md);
}
```

Tooltip content comes from the factor library in `quant_models/SKILL.md`.

### 3.5 Charts

**Price Charts — Lightweight Charts (TradingView OSS)**
```html
<script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
```

Config for dark theme:
```javascript
const chart = LightweightCharts.createChart(container, {
  width: 800,
  height: 400,
  layout: {
    background: { color: '#111827' },
    textColor: '#94a3b8',
  },
  grid: {
    vertLines: { color: '#1e293b' },
    horzLines: { color: '#1e293b' },
  },
  crosshair: {
    mode: LightweightCharts.CrosshairMode.Normal,
  },
});
```

**Stats Charts — Chart.js**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
```

Used for: probability distribution histogram, pie chart (portfolio allocation), bar charts (factor scores), gauge chart (risk meter).

---

## 4. Responsive Design

### Breakpoints

```css
/* Mobile first */
@media (min-width: 640px)  { /* sm - tablet */ }
@media (min-width: 768px)  { /* md - small laptop */ }
@media (min-width: 1024px) { /* lg - desktop */ }
@media (min-width: 1280px) { /* xl - wide desktop */ }
```

### Layout Rules

- **Stock Explorer table**: Full table on desktop → stacked cards on mobile
- **Charts**: Full width on all screens. Minimum height 300px.
- **Portfolio Builder**: Side-by-side on desktop (stocks + pie chart) → stacked on mobile
- **Results Dashboard**: 2-column grid on desktop → single column on mobile

---

## 5. Animations & Micro-interactions

```css
/* Smooth page transitions */
.page-enter {
  opacity: 0;
  transform: translateY(10px);
  animation: fadeInUp 0.3s ease forwards;
}

@keyframes fadeInUp {
  to { opacity: 1; transform: translateY(0); }
}

/* Score counter animation */
@keyframes countUp {
  from { --score: 0; }
}

/* Loading skeleton */
.skeleton {
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-tertiary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Button press effect */
.btn:active {
  transform: scale(0.97);
}
```

---

## 6. Disclaimers (Compliance Integration)

Every page that shows scores or simulation results MUST include:

```html
<footer class="disclaimer">
  <p>⚠️ Flock is an educational tool, NOT investment advice. Past performance does not
  guarantee future results. Always consult a SEBI-registered advisor before investing.</p>
</footer>
```

The results dashboard must show the full 5-point disclaimer from `quant_models/SKILL.md`.

---

## 7. Accessibility

- All interactive elements: `tabindex`, `aria-label`
- Color contrast: minimum 4.5:1 for body text, 3:1 for large text
- Chart data: always provide a text summary alongside visual charts
- Focus rings: visible `outline` on keyboard focus (don't remove with `outline: none`)

---

## UI/UX Agent Operating Rules

1. **Stitch-first workflow.** Design every screen in Google Stitch via MCP before writing HTML. Extract production code with `fetch_screen_code`.
2. **Dark mode only for MVP.** Light mode is V2.
3. **No framework dependencies.** HTML + Vanilla CSS + JS. No React, no Vue, no Tailwind.
4. **CDN for chart libraries.** Lightweight Charts and Chart.js from CDN, not npm.
5. **Every number must be formatted.** INR with ₹ symbol and commas. Percentages with % suffix.
6. **Loading states are mandatory.** Every data-dependent component shows a skeleton loader until data arrives.
7. **Mobile responsive.** Every screen must work on 375px width (iPhone SE).
8. **Educational tooltips on every factor.** This is what keeps us in the "educational tool" lane.
9. **Feed design DNA to every Stitch prompt.** Include colors, fonts, and style context so all screens are visually consistent.
10. **Generate variants before committing.** Use `generate_variants` to explore at least 2-3 options for major screens before picking one.

---

## Integration with Other Agents

| Agent | Interaction |
|---|---|
| **Quant Agent** | Provides factor tooltips text, score badge ranges, simulation output fields — UI/UX Agent renders them. |
| **Data Agent** | Provides API response shapes — UI/UX Agent builds components to consume them. |
| **Code Reviewer Agent** | Reviews frontend HTML/CSS/JS for quality, accessibility, responsiveness. |
| **Compliance Agent** | Provides disclaimer text that must appear on specific screens. |
| **River (Architect)** | Approves major design decisions, user flow changes. |
