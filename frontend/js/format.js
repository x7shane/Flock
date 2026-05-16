/**
 * Flock Formatting Utilities — Jake's Number Formatters
 *
 * INR formatting, percentage formatting, score badge assignment.
 */

/** Format number as INR currency with ₹ symbol and commas */
function formatINR(amount) {
  if (amount == null || isNaN(amount)) return '—';
  const abs = Math.abs(amount);
  let formatted;

  if (abs >= 1e7) {
    formatted = '₹' + (amount / 1e7).toFixed(2) + ' Cr';
  } else if (abs >= 1e5) {
    formatted = '₹' + (amount / 1e5).toFixed(2) + ' L';
  } else {
    formatted = '₹' + amount.toLocaleString('en-IN', {
      maximumFractionDigits: 0,
    });
  }

  return formatted;
}

/** Format INR with full precision */
function formatINRFull(amount) {
  if (amount == null || isNaN(amount)) return '—';
  return '₹' + amount.toLocaleString('en-IN', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  });
}

/** Format percentage with + sign for positive */
function formatPct(value, decimals = 1) {
  if (value == null || isNaN(value)) return '—';
  const sign = value > 0 ? '+' : '';
  return sign + value.toFixed(decimals) + '%';
}

/** Format percentage without sign */
function formatPctUnsigned(value, decimals = 1) {
  if (value == null || isNaN(value)) return '—';
  return value.toFixed(decimals) + '%';
}

/** Get Flock Score badge CSS class based on score range */
function getScoreBadgeClass(score) {
  if (score == null) return 'score-average';
  if (score >= 90) return 'score-excellent';
  if (score >= 70) return 'score-good';
  if (score >= 50) return 'score-average';
  if (score >= 30) return 'score-below-avg';
  return 'score-poor';
}

/** Get semantic color class for a value (positive = green, negative = red) */
function getValueColor(value) {
  if (value == null) return '';
  if (value > 0) return 'text-success';
  if (value < 0) return 'text-danger';
  return '';
}

/** Format large numbers with K/M/B suffix */
function formatCompact(num) {
  if (num == null || isNaN(num)) return '—';
  const abs = Math.abs(num);
  if (abs >= 1e9) return (num / 1e9).toFixed(1) + 'B';
  if (abs >= 1e6) return (num / 1e6).toFixed(1) + 'M';
  if (abs >= 1e3) return (num / 1e3).toFixed(1) + 'K';
  return num.toFixed(0);
}
