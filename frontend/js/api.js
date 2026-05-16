/**
 * Flock API Client — Jake's HTTP Layer
 *
 * All API calls go through this module. Base URL is auto-detected.
 */

const API_BASE = '/api/v1';

async function fetchJSON(url, options = {}) {
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    return await res.json();
  } catch (e) {
    console.error(`[API] ${url}:`, e.message);
    throw e;
  }
}

/** Stocks */
const StocksAPI = {
  list: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetchJSON(`${API_BASE}/stocks${qs ? '?' + qs : ''}`);
  },
  sectors: () => fetchJSON(`${API_BASE}/stocks/sectors`),
  /** Get Flock score breakdown for a single stock */
  getScore: (ticker) => fetchJSON(`${API_BASE}/stocks/${ticker}/score`),
  /** Get raw fundamental data (ROE, PE, D/E etc.) for a single stock */
  getFundamentals: (ticker) => fetchJSON(`${API_BASE}/stocks/${ticker}/fundamentals`),
};

/** Simulation (Monte Carlo + Stress Tests) */
const SimulateAPI = {
  /** Run Monte Carlo simulation */
  run: (body) =>
    fetchJSON(`${API_BASE}/simulate`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  /** Run historical stress test */
  stressTest: (body) =>
    fetchJSON(`${API_BASE}/simulate/stress-test`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  /** List available crisis scenarios */
  crises: () => fetchJSON(`${API_BASE}/simulate/crises`),
};

/** SIP Calculator */
const SipAPI = {
  /**
   * Calculate SIP projection
   * @param {number} monthlyAmount - Monthly investment in INR
   * @param {number} expectedReturn - Expected annual return (e.g., 0.12 for 12%)
   * @param {number} years - Investment period in years
   * @param {number} stepUp - Annual step-up percentage (optional)
   */
  calculate: (monthlyAmount, expectedReturn, years, stepUp = 0) =>
    fetchJSON(`${API_BASE}/sip/calculate`, {
      method: 'POST',
      body: JSON.stringify({
        monthly_amount: monthlyAmount,
        expected_annual_return: expectedReturn,
        time_horizon_years: years,
        annual_step_up_pct: stepUp,
      }),
    }),

  /** Compare multiple SIP scenarios */
  compare: (body) =>
    fetchJSON(`${API_BASE}/sip/compare`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
};
