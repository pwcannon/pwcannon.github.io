// Evaluate on page load so labels expire even when the site is not rebuilt.
(() => {
  const day = 24 * 60 * 60 * 1000;
  function updateRecency() {
    const now = new Date();
    const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    document.querySelectorAll('[data-published]').forEach(marker => {
      const published = Date.parse(`${marker.dataset.published}T00:00:00Z`);
      const age = today - published;
      marker.hidden = !(Number.isFinite(age) && age >= 0 && age < 30 * day);
    });
  }
  updateRecency();
  window.addEventListener('pageshow', updateRecency);
})();
