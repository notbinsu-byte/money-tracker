// Formatting utilities

function formatCurrency(amount, currency = 'USD') {
    const num = parseFloat(amount) || 0;
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
    }).format(num);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function debounce(fn, ms) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), ms);
    };
}

// Theme management
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    document.getElementById('theme-icon').textContent = next === 'dark' ? '☀️' : '🌙';
}

// Apply saved theme on load
(function() {
    const saved = localStorage.getItem('theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = saved === 'dark' ? '☀️' : '🌙';
    }
})();
