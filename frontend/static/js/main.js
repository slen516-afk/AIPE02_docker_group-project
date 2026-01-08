const navConfig = [
    { id: "hero", label: "主題" },
    { id: "ranking", label: "可疑職稱 Top5" },
    { id: "section-1", label: "疑似詐騙比例" },
    { id: "section-2", label: "聘僱型態分佈" },
    { id: "section-3", label: "產業風險對比" },
    { id: "section-4", label: "紅旗雷達" },
    { id: "section-5", label: "條件對比" },
    { id: "section-6", label: "紅旗結構" },
    { id: "section-7", label: "關聯分析" },
    { id: "world-map", label: "地理分佈" }
];

const initNav = () => {
    const container = document.getElementById('nav-items');
    if (!container) return;
    container.innerHTML = navConfig.map(item => `
        <li><button onclick="scrollToSection('${item.id}')" data-nav-id="${item.id}" class="nav-btn w-full block">${item.label}</button></li>
    `).join('');
};

const setActiveNav = (id, opts = { scroll: false }) => {
    const buttons = document.querySelectorAll('[data-nav-id]');
    buttons.forEach(btn => btn.classList.toggle('sidebar-active', btn.dataset.navId === id));
    if (opts && opts.scroll) {
        const activeBtn = document.querySelector(`[data-nav-id="${id}"]`);
        if (activeBtn && typeof activeBtn.scrollIntoView === 'function') {
            activeBtn.scrollIntoView({ block: 'nearest', inline: 'nearest' });
        }
    }
};

const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
    setActiveNav(id, { scroll: true });
    if (window.innerWidth < 1024) toggleSidebar();
};

const toggleSidebar = () => {
    document.getElementById('sidebar').classList.toggle('-translate-x-full');
    document.getElementById('overlay').classList.toggle('hidden');
    document.getElementById('menu-toggle').classList.toggle('is-open');
};

document.getElementById('menu-toggle').onclick = toggleSidebar;
document.getElementById('overlay').onclick = toggleSidebar;

let _spyTicking = false;
let _spyCurrent = "";

const onScrollSpy = () => {
    if (_spyTicking) return;
    _spyTicking = true;

    window.requestAnimationFrame(() => {
        let current = "";

        navConfig.forEach(item => {
            const sec = document.getElementById(item.id);
            if (!sec) return;
            const top = sec.getBoundingClientRect().top;
            if (top <= 160) current = item.id;
        });

        if (current && current !== _spyCurrent) {
            _spyCurrent = current;
            setActiveNav(current, { scroll: true });
        }

        _spyTicking = false;
    });
};

window.addEventListener('scroll', onScrollSpy, { passive: true });

window.onload = async () => {
    try {
        // 從後端取得資料
        const response = await fetch('/api/data');
        if (!response.ok) {
            const t = await response.text();
            throw new Error(`API /api/data 回應失敗：${response.status} ${response.statusText}\n${t.slice(0, 300)}`);
        }
        const allData = await response.json();

        lucide.createIcons();
        initNav();
        onScrollSpy();

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
        renderTable('table-container-1', ["聘僱型態", "可疑職缺數", "占比(%)"], allData.tables.table1);
        renderTable('table-container-2', ["特徵", "命中次數", "可疑度"], allData.tables.table2);

    } catch (error) {
        console.error("資料對接失敗:", error);
    }
};
