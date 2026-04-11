/**
 * StockSage — Main JavaScript
 * Global utilities, clock, flash messages, and shared helpers.
 */

// ── Footer clock ──
function updateFooterTime() {
  const el = document.getElementById("footerTime");
  if (el) {
    const now = new Date();
    el.textContent = now.toLocaleTimeString("en-US", {
      hour: "2-digit", minute: "2-digit", second: "2-digit",
      timeZoneName: "short"
    });
  }
}
setInterval(updateFooterTime, 1000);
updateFooterTime();

// ── Auto-dismiss flash messages ──
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.transition = "opacity 0.5s";
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 500);
    }, 5000);
  });
});

// ── Ticker input auto-uppercase ──
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[name="ticker"]').forEach(input => {
    input.addEventListener("input", () => {
      const pos = input.selectionStart;
      input.value = input.value.toUpperCase();
      input.setSelectionRange(pos, pos);
    });
  });
});

// ── Format large numbers (e.g. market cap) ──
window.formatLargeNumber = function(num) {
  if (!num) return "—";
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
  if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
  return `$${num.toLocaleString()}`;
};

// ── PWA Service Worker Registration ──
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => console.log('[SW] Registered:', reg.scope))
      .catch(err => console.warn('[SW] Registration failed:', err));
  });
}

// ── Theme Toggle (called from base.html) ──
window.toggleTheme = function () {
  fetch('/profile/theme', { method: 'POST' })
    .then(r => r.json())
    .then(d => {
      document.documentElement.setAttribute('data-theme', d.theme);
      const icon = document.getElementById('themeIcon');
      if (icon) icon.textContent = d.theme === 'light' ? '☀' : '◑';
    });
};
