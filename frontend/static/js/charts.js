// 統一顏色配置
const chartColors = ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#0ea5e9"];
// 註冊 ChartDataLabels 外掛
if (window.ChartDataLabels && window.Chart) {
    Chart.register(ChartDataLabels);

    try {
        Chart.defaults.plugins = Chart.defaults.plugins || {};
        Chart.defaults.plugins.datalabels = Chart.defaults.plugins.datalabels || {};
        Chart.defaults.plugins.datalabels.display = false;
    } catch (e) { }
}


// --- 內容防呆：避免圖表/表格出現 undefined ---
const safeText = (v, fallback = "未分類") => {
    if (v === undefined || v === null) return fallback;
    const s = String(v).trim();
    return s ? s : fallback;
};

const safeLabels = (arr) => (Array.isArray(arr) ? arr.map(v => safeText(v, "未分類")) : []);
const safeCells = (row) => (Array.isArray(row) ? row.map(v => safeText(v, "—")) : []);

// 表格渲染函式
const renderTable = (containerId, headers, rows) => {
    const container = document.getElementById(containerId);
    if (!container) return;

    const escapeAttr = (v) => String(v ?? '')
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    const html = `
    <table class="data-table">
      <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
      <tbody>${(rows || [])
            .map(r => `<tr>${safeCells(r)
                .map(c => `<td title="${escapeAttr(c)}">${c}</td>`)
                .join('')
                }</tr>`)
            .join('')
        }</tbody>
    </table>`;

    container.innerHTML = html;
};


// 初始化所有圖表
const initCharts = (rankingData, sectionData) => {
    // 排行榜
    if (document.getElementById('rankingChart')) {
        const labels = safeLabels(rankingData?.labels);
        const values = rankingData?.values || [];
        new Chart(document.getElementById('rankingChart'), {
            type: 'bar',
            data: {
                labels,
                datasets: [{ label: '筆數', data: values, backgroundColor: chartColors }]
            }
        });
    }

    // 圓餅圖 (分析一)
    if (document.getElementById('pieChart')) {
        const labels = safeLabels(sectionData?.section1?.labels);
        const values = sectionData?.section1?.values || [];
        new Chart(document.getElementById('pieChart'), {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: chartColors,
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '65%',
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    // 顯示數值標籤
                    datalabels: {
                        display: true,
                        formatter: (value) => {
                            const n = Number(value);
                            if (!Number.isFinite(n)) return value ?? "";
                            return n.toLocaleString();
                        },
                        // 樣式設定
                        color: '#ffffff',
                        font: { weight: '700' },
                        anchor: 'center',
                        align: 'center',
                        clamp: true
                    }
                }
            }
        });
    }

    // 折線圖 (分析二)
    if (document.getElementById('lineChart')) {
        const labels = safeLabels(sectionData?.section2?.labels);
        const values = sectionData?.section2?.values || [];
        new Chart(document.getElementById('lineChart'), {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: '職缺數（聘僱型態 Top 6）',
                    data: values,
                    borderColor: chartColors[0],
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            }
        });
    }

    // 區域圖 (分析三)
    if (document.getElementById('areaChart')) {
        const labels = safeLabels(sectionData?.section3?.labels);
        const main = sectionData?.section3?.main || [];
        const sub = sectionData?.section3?.sub || [];
        new Chart(document.getElementById('areaChart'), {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { label: '詐騙', data: main, fill: true, backgroundColor: 'rgba(59, 130, 246, 0.4)' },
                    { label: '非詐騙', data: sub, fill: true, backgroundColor: 'rgba(139, 92, 246, 0.4)' }
                ]

            },
            options: {
                scales: {
                    x: { title: { display: true, text: '產業類別' } },
                    y: { title: { display: true, text: '職缺數量' } }
                }
            }
        });
    }

    // 雷達圖 (分析四)
    if (document.getElementById('radarChart')) {
        const labels = safeLabels(sectionData?.section4?.labels);
        const values = sectionData?.section4?.values || [];
        new Chart(document.getElementById('radarChart'), {
            type: 'radar',
            data: {
                labels,
                datasets: [{ label: '可疑特徵強度', data: values, backgroundColor: 'rgba(236, 72, 153, 0.2)', borderColor: '#ec4899' }]
            }
        });
    }

    // 分組直條圖 (分析五)
    if (document.getElementById('groupedBarChart')) {
        const labels = safeLabels(sectionData?.section5?.labels);
        const prodA = sectionData?.section5?.prodA || [];
        const prodB = sectionData?.section5?.prodB || [];
        new Chart(document.getElementById('groupedBarChart'), {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: '詐騙', data: prodA, backgroundColor: chartColors[0] },
                    { label: '非詐騙', data: prodB, backgroundColor: chartColors[1] }
                ]
            }
        });
    }

    // 堆疊直條圖 (分析六)
    if (document.getElementById('stackedBarChart')) {
        const labels = safeLabels(sectionData?.section6?.labels);
        const external = sectionData?.section6?.external || [];
        const internal = sectionData?.section6?.internal || [];
        const other = sectionData?.section6?.other || [];
        new Chart(document.getElementById('stackedBarChart'), {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: '有遠端', data: external, backgroundColor: chartColors[2] },
                    { label: '無公司Logo', data: internal, backgroundColor: chartColors[3] },
                    { label: '無面試題目', data: other, backgroundColor: chartColors[4] }
                ]
            },
            options: { scales: { x: { stacked: true }, y: { stacked: true } } }
        });
    }

    // 散點圖 (分析七)
    if (document.getElementById('scatterChart')) {
        const points = sectionData?.section7 || [];
        new Chart(document.getElementById('scatterChart'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '各聘僱型態散點分佈',
                    data: points,
                    backgroundColor: chartColors[5]
                }]
            },
            options: {
                scales: {
                    x: { title: { display: true, text: '有公司 Logo 的比例 (%)' } },
                    y: { title: { display: true, text: '有面試題目(Questions) 的比例 (%)' } }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const r = ctx.raw || {};
                                const name = r.label ?? `點#${ctx.dataIndex + 1}`;
                                const x = (r.x ?? ctx.parsed.x);
                                const y = (r.y ?? ctx.parsed.y);
                                const n = (r.count ?? '—');
                                const fr = (r.fraud_rate ?? '—');
                                return `${name}｜Logo：${Number(x).toFixed(1)}%｜Questions：${Number(y).toFixed(1)}%｜樣本：${n}｜詐騙率：${fr}%`;
                            }
                        }
                    }
                }
            }
        });
    }
};

