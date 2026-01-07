// 統一顏色配置
const chartColors = ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#0ea5e9"];

// 表格渲染函式
const renderTable = (containerId, headers, rows) => {
    const container = document.getElementById(containerId);
    if (!container) return;
    const html = `
        <table class="data-table">
            <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
            <tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody>
        </table>`;
    container.innerHTML = html;
};

// 初始化所有圖表
const initCharts = (rankingData, sectionData) => {
    // 排行榜
    if (document.getElementById('rankingChart')) {
        new Chart(document.getElementById('rankingChart'), {
            type: 'bar',
            data: {
                labels: rankingData.labels,
                datasets: [{ data: rankingData.values, backgroundColor: chartColors }]
            }
        });
    }

    // 圓餅圖 (分析一)
    if (document.getElementById('pieChart')) {
        new Chart(document.getElementById('pieChart'), {
            type: 'doughnut',
            data: {
                labels: sectionData.section1.labels,
                datasets: [{ data: sectionData.section1.values, backgroundColor: chartColors }]
            },
            options: { cutout: '65%' }
        });
    }

    // 折線圖 (分析二)
    if (document.getElementById('lineChart')) {
        new Chart(document.getElementById('lineChart'), {
            type: 'line',
            data: {
                labels: sectionData.section2.labels,
                datasets: [{
                    label: '銷售額',
                    data: sectionData.section2.values,
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
        new Chart(document.getElementById('areaChart'), {
            type: 'line',
            data: {
                labels: sectionData.section3.labels,
                datasets: [
                    { label: '主要', data: sectionData.section3.main, fill: true, backgroundColor: 'rgba(59, 130, 246, 0.4)' },
                    { label: '次要', data: sectionData.section3.sub, fill: true, backgroundColor: 'rgba(139, 92, 246, 0.4)' }
                ]
            }
        });
    }

    // 雷達圖 (分析四)
    if (document.getElementById('radarChart')) {
        new Chart(document.getElementById('radarChart'), {
            type: 'radar',
            data: {
                labels: sectionData.section4.labels,
                datasets: [{ data: sectionData.section4.values, backgroundColor: 'rgba(236, 72, 153, 0.2)', borderColor: '#ec4899' }]
            }
        });
    }

    // 分組直條圖 (分析五)
    if (document.getElementById('groupedBarChart')) {
        new Chart(document.getElementById('groupedBarChart'), {
            type: 'bar',
            data: {
                labels: sectionData.section5.labels,
                datasets: [
                    { label: '產品 A', data: sectionData.section5.prodA, backgroundColor: chartColors[0] },
                    { label: '產品 B', data: sectionData.section5.prodB, backgroundColor: chartColors[1] }
                ]
            }
        });
    }

    // 堆疊直條圖 (分析六)
    if (document.getElementById('stackedBarChart')) {
        new Chart(document.getElementById('stackedBarChart'), {
            type: 'bar',
            data: {
                labels: sectionData.section6.labels,
                datasets: [
                    { label: '外部來源', data: sectionData.section6.external, backgroundColor: chartColors[2] },
                    { label: '內部推薦', data: sectionData.section6.internal, backgroundColor: chartColors[3] },
                    { label: '其他', data: sectionData.section6.other, backgroundColor: chartColors[4] }
                ]
            },
            options: { scales: { x: { stacked: true }, y: { stacked: true } } }
        });
    }

    // 散點圖 (分析七)
    if (document.getElementById('scatterChart')) {
        new Chart(document.getElementById('scatterChart'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '職缺關聯分佈',
                    data: sectionData.section7,
                    backgroundColor: chartColors[5]
                }]
            }
        });
    }
};