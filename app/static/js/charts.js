// Chart.js rendering functions — Soft Pastel Style

const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

// Shared font config for all charts
const chartFont = { family: "'Patrick Hand', cursive", size: 13 };

function getChartColors(count) {
    const palette = [
        '#d7c4f2','#ffd6cc','#c8e6c9','#ffe4cc','#e1bee7',
        '#b2ebf2','#ffccbc','#c5cae9','#f8bbd0','#cfd8dc',
        '#ede7f6','#b2ebf2','#ffcdd2','#bbdefb','#dcedc8',
    ];
    const colors = [];
    for (let i = 0; i < count; i++) colors.push(palette[i % palette.length]);
    return colors;
}

function renderPieChart(canvasId, data, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#c2c7d0' : '#4a4458';
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => `${d.category_icon || ''} ${d.category_name}`),
            datasets: [{
                data: data.map(d => parseFloat(d.total)),
                backgroundColor: data.map(d => d.category_color || '#d7c4f2'),
                borderWidth: 2,
                borderColor: isDark ? '#2d2640' : '#ffffff',
                hoverBorderWidth: 3,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            cutout: '55%',
            plugins: {
                legend: { position: 'bottom', labels: { padding: 14, font: { ...chartFont, size: 12 }, color: textColor, usePointStyle: true, pointStyle: 'circle' } },
                tooltip: {
                    backgroundColor: isDark ? '#2d2640' : '#fffbfe',
                    titleColor: isDark ? '#e8e0f0' : '#4a4458',
                    bodyColor: isDark ? '#e8e0f0' : '#4a4458',
                    borderColor: isDark ? '#e1bee7' : '#d7c4f2',
                    borderWidth: 2,
                    cornerRadius: 12,
                    titleFont: chartFont,
                    bodyFont: chartFont,
                    padding: 10,
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
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#c2c7d0' : '#4a4458';
    const gridColor = isDark ? 'rgba(225,190,231,0.08)' : 'rgba(215,196,242,0.2)';
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.map(d => monthNames[d.month - 1]),
            datasets: [
                {
                    label: 'Income',
                    data: monthlyData.map(d => parseFloat(d.income)),
                    backgroundColor: 'rgba(200, 230, 201, 0.6)',
                    borderColor: '#a5d6a7',
                    borderWidth: 2,
                    borderRadius: 10,
                    borderSkipped: false,
                },
                {
                    label: 'Expenses',
                    data: monthlyData.map(d => parseFloat(d.expense)),
                    backgroundColor: 'rgba(255, 205, 210, 0.6)',
                    borderColor: '#ef9a9a',
                    borderWidth: 2,
                    borderRadius: 10,
                    borderSkipped: false,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => formatCurrency(v, currency), color: textColor, font: chartFont },
                    grid: { color: gridColor, drawBorder: false },
                    border: { dash: [4, 4] },
                },
                x: {
                    ticks: { color: textColor, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: textColor, font: chartFont, usePointStyle: true, pointStyle: 'rectRounded' } },
                tooltip: {
                    backgroundColor: isDark ? '#2d2640' : '#fffbfe',
                    titleColor: isDark ? '#e8e0f0' : '#4a4458',
                    bodyColor: isDark ? '#e8e0f0' : '#4a4458',
                    borderColor: isDark ? '#e1bee7' : '#d7c4f2',
                    borderWidth: 2,
                    cornerRadius: 12,
                    titleFont: chartFont,
                    bodyFont: chartFont,
                    padding: 10,
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}

function renderLineChart(canvasId, monthlyData, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#c2c7d0' : '#4a4458';
    const gridColor = isDark ? 'rgba(225,190,231,0.08)' : 'rgba(215,196,242,0.2)';
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.map(d => monthNames[d.month - 1]),
            datasets: [{
                label: 'Net Income',
                data: monthlyData.map(d => parseFloat(d.net || (d.income - d.expense))),
                borderColor: '#d7c4f2',
                backgroundColor: 'rgba(215, 196, 242, 0.15)',
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointRadius: 6,
                pointBackgroundColor: '#d7c4f2',
                pointBorderColor: isDark ? '#2d2640' : '#ffffff',
                pointBorderWidth: 2.5,
                pointHoverRadius: 9,
                pointStyle: 'circle',
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: { callback: v => formatCurrency(v, currency), color: textColor, font: chartFont },
                    grid: { color: gridColor, drawBorder: false },
                    border: { dash: [4, 4] },
                },
                x: {
                    ticks: { color: textColor, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: textColor, font: chartFont, usePointStyle: true } },
                tooltip: {
                    backgroundColor: isDark ? '#2d2640' : '#fffbfe',
                    titleColor: isDark ? '#e8e0f0' : '#4a4458',
                    bodyColor: isDark ? '#e8e0f0' : '#4a4458',
                    borderColor: isDark ? '#e1bee7' : '#d7c4f2',
                    borderWidth: 2,
                    cornerRadius: 12,
                    titleFont: chartFont,
                    bodyFont: chartFont,
                    padding: 10,
                    callbacks: { label: ctx => ` Net: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}

function renderTrendChart(canvasId, data, currency = 'USD') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#c2c7d0' : '#4a4458';
    const gridColor = isDark ? 'rgba(225,190,231,0.08)' : 'rgba(215,196,242,0.2)';
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => `${monthNames[d.month - 1]} ${d.year}`),
            datasets: [
                {
                    label: 'Income',
                    data: data.map(d => parseFloat(d.income)),
                    borderColor: '#c8e6c9',
                    backgroundColor: 'rgba(200, 230, 201, 0.1)',
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 5,
                    pointBackgroundColor: '#c8e6c9',
                    pointBorderColor: isDark ? '#2d2640' : '#ffffff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                    borderDash: [],
                },
                {
                    label: 'Expenses',
                    data: data.map(d => parseFloat(d.expense)),
                    borderColor: '#ffcdd2',
                    backgroundColor: 'rgba(255, 205, 210, 0.1)',
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 5,
                    pointBackgroundColor: '#ffcdd2',
                    pointBorderColor: isDark ? '#2d2640' : '#ffffff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => formatCurrency(v, currency), color: textColor, font: chartFont },
                    grid: { color: gridColor, drawBorder: false },
                    border: { dash: [4, 4] },
                },
                x: {
                    ticks: { color: textColor, font: chartFont },
                    grid: { display: false },
                },
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: textColor, font: chartFont, usePointStyle: true } },
                tooltip: {
                    backgroundColor: isDark ? '#2d2640' : '#fffbfe',
                    titleColor: isDark ? '#e8e0f0' : '#4a4458',
                    bodyColor: isDark ? '#e8e0f0' : '#4a4458',
                    borderColor: isDark ? '#e1bee7' : '#d7c4f2',
                    borderWidth: 2,
                    cornerRadius: 12,
                    titleFont: chartFont,
                    bodyFont: chartFont,
                    padding: 10,
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y, currency)}` },
                },
            },
        },
    });
}
