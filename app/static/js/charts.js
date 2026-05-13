// Chart.js rendering functions — Bolder Dark palette, theme-aware

const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

const chartFont = { family: "'Geist', 'Inter', system-ui, sans-serif", size: 12, weight: 500 };

const DARK_PALETTE = ['#a07dff','#f5a9c8','#ffc06b','#6dd3a8','#6cc7e8','#c994e8','#e8b86a','#82d4c4'];
const LIGHT_PALETTE = ['#7350de','#db6aa0','#d97706','#16a34a','#0891b2','#9333ea','#b45309','#0d9488'];

function getTheme() {
    return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
}

function chartTokens() {
    const t = getTheme();
    if (t === 'light') {
        return {
            palette: LIGHT_PALETTE,
            gridColor: 'rgba(20,16,32,0.08)',
            textColor: '#4a4458',
            textMuted: '#74708a',
            tooltipBg: '#ffffff',
            tooltipBorder: 'rgba(20,16,32,0.14)',
            tooltipText: '#1a1024',
            surfaceBorder: '#ffffff',
            pos: '#16a34a',
            neg: '#dc2626',
            accent: '#7350de',
            posBgFill: 'rgba(22,163,74,0.18)',
            negBgFill: 'rgba(220,38,38,0.18)',
            accentBgFill: 'rgba(115,80,222,0.15)',
        };
    }
    return {
        palette: DARK_PALETTE,
        gridColor: 'rgba(255,255,255,0.06)',
        textColor: '#c9c5d6',
        textMuted: '#8e8aa3',
        tooltipBg: '#22202d',
        tooltipBorder: 'rgba(255,255,255,0.12)',
        tooltipText: '#f4f2fa',
        surfaceBorder: '#1a1924',
        pos: '#4ade80',
        neg: '#f87171',
        accent: '#a07dff',
        posBgFill: 'rgba(74,222,128,0.10)',
        negBgFill: 'rgba(248,113,113,0.10)',
        accentBgFill: 'rgba(160,125,255,0.15)',
    };
}

function getChartColors(count) {
    const palette = chartTokens().palette;
    const colors = [];
    for (let i = 0; i < count; i++) colors.push(palette[i % palette.length]);
    return colors;
}

function tooltipConfig() {
    const c = chartTokens();
    return {
        backgroundColor: c.tooltipBg,
        titleColor: c.tooltipText,
        bodyColor: c.tooltipText,
        borderColor: c.tooltipBorder,
        borderWidth: 1,
        cornerRadius: 8,
        titleFont: chartFont,
        bodyFont: chartFont,
        padding: 10,
        displayColors: true,
        boxPadding: 4,
    };
}

function renderPieChart(canvasId, data, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const c = chartTokens();
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => `${d.category_icon || ''} ${d.category_name}`),
            datasets: [{
                data: data.map(d => parseFloat(d.total)),
                backgroundColor: data.map((d, i) => d.category_color || c.palette[i % c.palette.length]),
                borderWidth: 2,
                borderColor: c.surfaceBorder,
                hoverBorderWidth: 3,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            cutout: '62%',
            plugins: {
                legend: { position: 'bottom', labels: { padding: 14, font: chartFont, color: c.textColor, usePointStyle: true, pointStyle: 'circle' } },
                tooltip: {
                    ...tooltipConfig(),
                    callbacks: {
                        label: ctx => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.parsed / total) * 100).toFixed(1);
                            return ` ${ctx.label}: ${formatCurrency(ctx.parsed, currency)} (${pct}%)`;
                        }
                    }
                }
            },
        },
    });
}

function renderBarChart(canvasId, monthlyData, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const c = chartTokens();
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.map(d => monthNames[d.month - 1]),
            datasets: [
                {
                    label: 'Income',
                    data: monthlyData.map(d => parseFloat(d.income)),
                    backgroundColor: c.posBgFill,
                    borderColor: c.pos,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    borderSkipped: false,
                },
                {
                    label: 'Expenses',
                    data: monthlyData.map(d => parseFloat(d.expense)),
                    backgroundColor: c.negBgFill,
                    borderColor: c.neg,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    borderSkipped: false,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => formatCurrency(v, currency), color: c.textMuted, font: chartFont },
                    grid: { color: c.gridColor, drawBorder: false },
                    border: { display: false },
                },
                x: {
                    ticks: { color: c.textMuted, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: c.textColor, font: chartFont, usePointStyle: true, pointStyle: 'rectRounded' } },
                tooltip: {
                    ...tooltipConfig(),
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}

function renderLineChart(canvasId, monthlyData, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const c = chartTokens();
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.map(d => monthNames[d.month - 1]),
            datasets: [{
                label: 'Net Income',
                data: monthlyData.map(d => parseFloat(d.net || (d.income - d.expense))),
                borderColor: c.accent,
                backgroundColor: c.accentBgFill,
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointRadius: 5,
                pointBackgroundColor: c.accent,
                pointBorderColor: c.surfaceBorder,
                pointBorderWidth: 2,
                pointHoverRadius: 8,
                pointStyle: 'circle',
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: { callback: v => formatCurrency(v, currency), color: c.textMuted, font: chartFont },
                    grid: { color: c.gridColor, drawBorder: false },
                    border: { display: false },
                },
                x: {
                    ticks: { color: c.textMuted, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: c.textColor, font: chartFont, usePointStyle: true } },
                tooltip: {
                    ...tooltipConfig(),
                    callbacks: { label: ctx => ` Net: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}

function renderTrendChart(canvasId, data, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const c = chartTokens();
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => `${monthNames[d.month - 1]} ${d.year}`),
            datasets: [
                {
                    label: 'Income',
                    data: data.map(d => parseFloat(d.income)),
                    borderColor: c.pos,
                    backgroundColor: c.posBgFill,
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 4,
                    pointBackgroundColor: c.pos,
                    pointBorderColor: c.surfaceBorder,
                    pointBorderWidth: 2,
                    pointHoverRadius: 7,
                },
                {
                    label: 'Expenses',
                    data: data.map(d => parseFloat(d.expense)),
                    borderColor: c.neg,
                    backgroundColor: c.negBgFill,
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 4,
                    pointBackgroundColor: c.neg,
                    pointBorderColor: c.surfaceBorder,
                    pointBorderWidth: 2,
                    pointHoverRadius: 7,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => formatCurrency(v, currency), color: c.textMuted, font: chartFont },
                    grid: { color: c.gridColor, drawBorder: false },
                    border: { display: false },
                },
                x: {
                    ticks: { color: c.textMuted, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: c.textColor, font: chartFont, usePointStyle: true } },
                tooltip: {
                    ...tooltipConfig(),
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}
