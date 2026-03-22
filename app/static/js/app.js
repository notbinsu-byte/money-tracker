// API helper
const api = {
    async get(url) {
        const resp = await fetch(url);
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(err.detail || 'Request failed');
        }
        return resp.json();
    },

    async post(url, data) {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(err.detail || 'Request failed');
        }
        if (resp.status === 204) return null;
        return resp.json();
    },

    async put(url, data) {
        const resp = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(err.detail || 'Request failed');
        }
        return resp.json();
    },

    async del(url) {
        const resp = await fetch(url, { method: 'DELETE' });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(err.detail || 'Request failed');
        }
        return null;
    },
};

// Mobile nav toggle
function toggleNav() {
    const nav = document.getElementById('nav-links');
    const btn = document.getElementById('hamburger');
    const isOpen = nav.classList.toggle('open');
    btn.classList.toggle('active', isOpen);
    btn.setAttribute('aria-expanded', isOpen);
}

// Close nav on link click (mobile)
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const nav = document.getElementById('nav-links');
            const btn = document.getElementById('hamburger');
            if (nav) nav.classList.remove('open');
            if (btn) btn.classList.remove('active');
        });
    });
});

// Notification system
let _notifyTimeout = null;
function notify(message, type = 'info') {
    const el = document.getElementById('notification');
    if (_notifyTimeout) clearTimeout(_notifyTimeout);
    el.textContent = message;
    el.className = `notification ${type}`;
    el.style.display = 'block';
    el.style.animation = 'slideIn 0.3s ease';
    _notifyTimeout = setTimeout(() => {
        el.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => { el.style.display = 'none'; }, 300);
    }, 3000);
}
