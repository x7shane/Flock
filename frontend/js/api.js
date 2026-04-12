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
};

/** Simulation */
const SimulateAPI = {
  run: (body) =>
    fetchJSON(`${API_BASE}/simulate`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  stressTest: (body) =>
    fetchJSON(`${API_BASE}/simulate/stress-test`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  crises: () => fetchJSON(`${API_BASE}/simulate/crises`),
};

/** SIP Calculator */
const SipAPI = {
  calculate: (body) =>
    fetchJSON(`${API_BASE}/sip/calculate`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  compare: (body) =>
    fetchJSON(`${API_BASE}/sip/compare`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
};
