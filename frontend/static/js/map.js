/**
 * 顏色計算函式
 * @param {number} d - 數據值
 * @param {number} maxVal - 數據中的最大值，用於計算比例
 */
function getColor(d, maxVal) {
    if (!d || d === 0) return '#f1f5f9';
    const ratio = d / maxVal;
    const lightness = 75 - (ratio * 40);
    return `hsl(221, 83%, ${lightness}%)`;
}

/**
 * 初始化地圖
 * @param {Object} mapData - 各國代碼對應的數值 {"USA": 850, "TWN": 500}
 * @param {Object} mapNames - 各國代碼對應的中文名稱 {"USA": "美國", "TWN": "台灣"}
 */
const initWorldMap = (mapData, mapNames) => {
    // 檢查必要的 DOM 與資料是否存在
    if (!document.getElementById('map') || !mapData || !mapNames) {
        console.warn("地圖初始化失敗：缺少 DOM 元件或資料");
        return;
    }

    // 計算當前數據中的最大值，用於顏色比例
    const maxVal = Math.max(...Object.values(mapData), 1);

    const worldBounds = [[-55, -135], [85, 155]];
    const map = L.map('map', {
        zoomSnap: 0.1,
        dragging: false,
        zoomControl: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        touchZoom: false,
        boxZoom: false,
        attributionControl: false
    });

    // 處理不同螢幕尺寸的縮放
    const fitMap = () => {
        map.invalidateSize();
        const isMobile = window.innerWidth < 768;
        const paddingValues = isMobile ? [40, 40] : [10, 10];
        map.fitBounds(worldBounds, { padding: paddingValues, animate: false });
    };

    setTimeout(fitMap, 100);
    window.addEventListener('resize', () => setTimeout(fitMap, 100));

    // 使用本地 GeoJSON 路徑
    const geoJsonUrl = '/static/data/countries.geojson';

    fetch(geoJsonUrl)
        .then(res => res.json())
        .then(geojsonData => {
            L.geoJson(geojsonData, {
                style: (feature) => {
                    const props = feature.properties;
                    // 取得國家代碼 (ISO_A3)
                    const code = (props.ISO_A3 || props.iso_a3 || feature.id || "").toUpperCase();
                    const value = mapData[code] || 0;
                    return {
                        fillColor: getColor(value, maxVal),
                        weight: 1,
                        opacity: 1,
                        color: 'white',
                        fillOpacity: 0.8
                    };
                },
                onEachFeature: (feature, layer) => {
                    const props = feature.properties;
                    const code = (props.ISO_A3 || props.iso_a3 || feature.id || "").toUpperCase();
                    const value = mapData[code] || 0;

                    // 從 mapNames 抓取中文名稱，抓不到則用 geojson 內建名稱
                    const countryName = mapNames[code] || props.name || "未知國家";

                    if (value > 0) {
                        layer.bindTooltip(`<strong>${countryName}</strong><br/>虛假招募職缺數: ${value}`, {
                            sticky: true,
                            direction: 'top'
                        });
                        layer.on({
                            mouseover: (e) => e.target.setStyle({ fillOpacity: 1, weight: 2 }),
                            mouseout: (e) => e.target.setStyle({ fillOpacity: 0.8, weight: 1 })
                        });
                    }
                }
            }).addTo(map);

            renderLegend(mapData, mapNames);
        })
        .catch(err => console.error("GeoJSON 載入失敗:", err));
};

// 繪製地圖圖例
function renderLegend(data, names) {
    const legend = document.getElementById('map-legend');
    if (!legend || !data || !names) return;

    const maxVal = Math.max(...Object.values(data), 1);
    legend.innerHTML = '';

    // 根據傳入的 data 動態生成圖例標籤
    Object.entries(data).forEach(([code, val]) => {
        const countryName = names[code] || code;
        legend.innerHTML += `
            <div class="legend-item" style="display:flex; align-items:center; gap:8px; background:white; padding:5px 15px; border-radius:20px; border:1px solid #e2e8f0; font-size:12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <div style="height:12px; width:12px; border-radius:50%; background:${getColor(val, maxVal)}"></div>
                <span style="font-weight:600; color:#475569;">${countryName}: <span style="color:#1e293b;">${val}</span></span>
            </div>`;
    });
}