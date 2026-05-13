// Chart.js rendering functions — Bolder Dark palette

const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

const chartFont = { family: "'Geist', 'Inter', system-ui, sans-serif", size: 12, weight: 500 };

const DARK_PALETTE = ['#a07dff','#f5a9c8','#ffc06b','#6dd3a8','#6cc7e8','#c994e8','#e8b86a','#82d4c4'];
const GRID_COLOR = 'rgba(255,255,255,0.06)';
const TEXT_COLOR = '#c9c5d6';
const TEXT_MUTED = '#8e8aa3';
const TOOLTIP_BG = '#22202d';
const TOOLTIP_BORDER = 'rgba(255,255,255,0.12)';
const SURFACE_BORDER = '#1a1924';

const POS = '#4ade80';
const NEG = '#f87171';
const ACCENT = '#a07dff';

function getChartColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) colors.push(DARK_PALETTE[i % DARK_PALETTE.length]);
    return colors;
}

function tooltipConfig(currency) {
    return {
        backgroundColor: TOOLTIP_BG,
        titleColor: '#f4f2fa',
        bodyColor: '#f4f2fa',
        borderColor: TOOLTIP_BORDER,
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
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => `${d.category_icon || ''} ${d.category_name}`),
            datasets: [{
                data: data.map(d => parseFloat(d.total)),
                backgroundColor: data.map((d, i) => d.category_color || DARK_PALETTE[i % DARK_PALETTE.length]),
                borderWidth: 2,
                borderColor: SURFACE_BORDER,
                hoverBorderWidth: 3,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            cutout: '62%',
            plugins: {
                legend: { position: 'bottom', labels: { padding: 14, font: chartFont, color: TEXT_COLOR, usePointStyle: true, pointStyle: 'circle' } },
                tooltip: {
                    ...tooltipConfig(currency),
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
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.map(d => monthNames[d.month - 1]),
            datasets: [
                {
                    label: 'Income',
                    data: monthlyData.map(d => parseFloat(d.income)),
                    backgroundColor: 'rgba(74, 222, 128, 0.45)',
                    borderColor: POS,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    borderSkipped: false,
                },
                {
                    label: 'Expenses',
                    data: monthlyData.map(d => parseFloat(d.expense)),
                    backgroundColor: 'rgba(248, 113, 113, 0.45)',
                    borderColor: NEG,
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
                    ticks: { callback: v => formatCurrency(v, currency), color: TEXT_MUTED, font: chartFont },
                    grid: { color: GRID_COLOR, drawBorder: false },
                    border: { display: false },
                },
                x: {
                    ticks: { color: TEXT_MUTED, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: TEXT_COLOR, font: chartFont, usePointStyle: true, pointStyle: 'rectRounded' } },
                tooltip: {
                    ...tooltipConfig(currency),
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}

function renderLineChart(canvasId, monthlyData, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.map(d => monthNames[d.month - 1]),
            datasets: [{
                label: 'Net Income',
                data: monthlyData.map(d => parseFloat(d.net || (d.income - d.expense))),
                borderColor: ACCENT,
                backgroundColor: 'rgba(160, 125, 255, 0.15)',
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointRadius: 5,
                pointBackgroundColor: ACCENT,
                pointBorderColor: SURFACE_BORDER,
                pointBorderWidth: 2,
                pointHoverRadius: 8,
                pointStyle: 'circle',
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: { callback: v => formatCurrency(v, currency), color: TEXT_MUTED, font: chartFont },
                    grid: { color: GRID_COLOR, drawBorder: false },
                    border: { display: false },
                },
                x: {
                    ticks: { color: TEXT_MUTED, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: TEXT_COLOR, font: chartFont, usePointStyle: true } },
                tooltip: {
                    ...tooltipConfig(currency),
                    callbacks: { label: ctx => ` Net: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}

function renderTrendChart(canvasId, data, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => `${monthNames[d.month - 1]} ${d.year}`),
            datasets: [
                {
                    label: 'Income',
                    data: data.map(d => parseFloat(d.income)),
                    borderColor: POS,
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 4,
                    pointBackgroundColor: POS,
                    pointBorderColor: SURFACE_BORDER,
                    pointBorderWidth: 2,
                    pointHoverRadius: 7,
                },
                {
                    label: 'Expenses',
                    data: data.map(d => parseFloat(d.expense)),
                    borderColor: NEG,
                    backgroundColor: 'rgba(248, 113, 113, 0.1)',
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 4,
                    pointBackgroundColor: NEG,
                    pointBorderColor: SURFACE_BORDER,
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
                    ticks: { callback: v => formatCurrency(v, currency), color: TEXT_MUTED, font: chartFont },
                    grid: { color: GRID_COLOR, drawBorder: false },
                    border: { display: false },
                },
                x: {
                    ticks: { color: TEXT_MUTED, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: TEXT_COLOR, font: chartFont, usePointStyle: true } },
                tooltip: {
                    ...tooltipConfig(currency),
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}
