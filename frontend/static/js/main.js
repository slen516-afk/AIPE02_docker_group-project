const navConfig = [
    { id: "hero", label: "標題區塊" }, { id: "ranking", label: "排行榜" },
    { id: "section-1", label: "圓餅圖" }, { id: "section-2", label: "折線圖" },
    { id: "section-3", label: "區域圖" }, { id: "section-4", label: "雷達圖" },
    { id: "section-5", label: "分組直條圖" }, { id: "section-6", label: "堆疊直條圖" },
    { id: "section-7", label: "散點圖" }, { id: "world-map", label: "世界地圖" }
];

const initNav = () => {
    const container = document.getElementById('nav-items');
    if (!container) return;
    container.innerHTML = navConfig.map(item => `
        <li><button onclick="scrollToSection('${item.id}')" data-nav-id="${item.id}" class="nav-btn w-full block">${item.label}</button></li>
    `).join('');
};

const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
    if (window.innerWidth < 1024) toggleSidebar();
};

const toggleSidebar = () => {
    document.getElementById('sidebar').classList.toggle('-translate-x-full');
    document.getElementById('overlay').classList.toggle('hidden');
    document.getElementById('menu-toggle').classList.toggle('is-open');
};

document.getElementById('menu-toggle').onclick = toggleSidebar;
document.getElementById('overlay').onclick = toggleSidebar;

window.onscroll = () => {
    let current = "";
    navConfig.forEach(item => {
        const sec = document.getElementById(item.id);
        if (sec && window.pageYOffset >= sec.offsetTop - 150) current = item.id;
    });
    document.querySelectorAll('[data-nav-id]').forEach(btn => btn.classList.toggle('sidebar-active', btn.dataset.navId === current));
};

window.onload = async () => {
    try {
        // 從後端取得資料
        const response = await fetch('/api/data');
        const allData = await response.json();

        lucide.createIcons();
        initNav();

        // 分發資料給各個組件
        // 排行榜與圖表
        if (typeof initCharts === "function") {
            initCharts(allData.ranking, allData.charts);
        }

        // 地圖
        if (typeof initWorldMap === "function") {
            initWorldMap(allData.map, allData.map_names);
        }

        // 表格
        renderTable('table-container-1', ["月份", "銷售額", "成長率"], allData.tables.table1);
        renderTable('table-container-2', ["產品", "銷量", "評分"], allData.tables.table2);

    } catch (error) {
        console.error("資料對接失敗:", error);
    }
};
