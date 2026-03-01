// Chart.js rendering functions

const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

function getChartColors(count) {
    const palette = [
        '#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6',
        '#1abc9c','#e67e22','#34495e','#fd79a8','#636e72',
        '#a29bfe','#00cec9','#fab1a0','#74b9ff','#55efc4',
    ];
    const colors = [];
    for (let i = 0; i < count; i++) colors.push(palette[i % palette.length]);
    return colors;
}

function renderPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => `${d.category_icon || ''} ${d.category_name}`),
            datasets: [{
                data: data.map(d => parseFloat(d.total)),
                backgroundColor: data.map(d => d.category_color || '#6c757d'),
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 12, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.parsed / total) * 100).toFixed(1);
                            return `${ctx.label}: ${formatCurrency(ctx.parsed)} (${pct}%)`;
                        }
                    }
                }
            },
        },
    });
}

function renderBarChart(canvasId, monthlyData) {
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
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: '#2ecc71',
                    borderWidth: 1,
                },
                {
                    label: 'Expenses',
                    data: monthlyData.map(d => parseFloat(d.expense)),
                    backgroundColor: 'rgba(231, 76, 60, 0.7)',
                    borderColor: '#e74c3c',
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, ticks: { callback: v => formatCurrency(v) } },
            },
            plugins: {
                legend: { position: 'bottom' },
                tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}` } },
            },
        },
    });
}

function renderLineChart(canvasId, monthlyData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.map(d => monthNames[d.month - 1]),
            datasets: [{
                label: 'Net Income',
                data: monthlyData.map(d => parseFloat(d.net || (d.income - d.expense))),
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.3,
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: { ticks: { callback: v => formatCurrency(v) } },
            },
            plugins: {
                legend: { position: 'bottom' },
                tooltip: { callbacks: { label: ctx => `Net: ${formatCurrency(ctx.parsed.y)}` } },
            },
        },
    });
}

function renderTrendChart(canvasId, data) {
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
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: false,
                    tension: 0.3,
                },
                {
                    label: 'Expenses',
                    data: data.map(d => parseFloat(d.expense)),
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: false,
                    tension: 0.3,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, ticks: { callback: v => formatCurrency(v) } },
            },
            plugins: {
                legend: { position: 'bottom' },
                tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}` } },
            },
        },
    });
}
