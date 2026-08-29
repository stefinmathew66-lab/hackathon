// Hackathon Hunter Dashboard Client Logic v2.0
let allHackathons = [];
let currentFilter = {
    region: 'all',      // 'all', 'india', 'online'
    category: 'all',    // 'all', 'AI & ML', 'Web3 & Crypto', etc.
    city: 'all',        // 'all', 'Bengaluru', 'Delhi-NCR', etc.
    prize: 'all',       // 'all', 'mega', 'high', 'cash', 'swag'
    platform: 'all',    // 'all', 'Devfolio', 'Unstop', etc.
    search: '',
    sort: 'featured'
};

// DOM Elements
const searchInput = document.getElementById('search-input');
const searchClearBtn = document.getElementById('search-clear');
const regionTabs = document.getElementById('region-tabs');
const categoryChips = document.getElementById('category-chips');
const cityChips = document.getElementById('city-chips');
const platformChips = document.getElementById('platform-chips');
const prizeSelect = document.getElementById('prize-select');
const sortSelect = document.getElementById('sort-select');
const hackathonsGrid = document.getElementById('hackathons-grid');
const loadingState = document.getElementById('loading-state');
const emptyState = document.getElementById('empty-state');
const resultsCount = document.getElementById('results-count');
const refreshBtn = document.getElementById('btn-refresh');
const exportBtn = document.getElementById('btn-export-menu');
const exportDropdown = document.getElementById('export-dropdown');
const resetFiltersBtn = document.getElementById('btn-reset-filters');
const resetAllBtn = document.getElementById('btn-reset-all');
const alertsBtn = document.getElementById('btn-open-alerts');
const alertsModal = document.getElementById('alerts-modal');
const modalClose = document.getElementById('modal-close');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');
const syncTimeText = document.getElementById('sync-time-text');

// Stats Elements
const statTotal = document.getElementById('stat-total');
const statIndia = document.getElementById('stat-india');
const statOnline = document.getElementById('stat-online');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    fetchHackathons();
    setupEventListeners();

    // Auto-refresh in the browser every 15 minutes
    setInterval(() => {
        fetchHackathons(false);
    }, 900000);
});

function setupEventListeners() {
    // Search input with debouncing
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        searchClearBtn.classList.toggle('hidden', !val);
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilter.search = val.toLowerCase();
            renderFilteredHackathons();
        }, 150);
    });

    searchClearBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchClearBtn.classList.add('hidden');
        currentFilter.search = '';
        renderFilteredHackathons();
    });

    // Region Tabs
    regionTabs.addEventListener('click', (e) => {
        const btn = e.target.closest('.tab-btn');
        if (!btn) return;
        regionTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter.region = btn.dataset.region;
        renderFilteredHackathons();
    });

    // Category Chips
    categoryChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        categoryChips.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentFilter.category = chip.dataset.category;
        renderFilteredHackathons();
    });

    // City Chips
    cityChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        cityChips.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentFilter.city = chip.dataset.city;
        renderFilteredHackathons();
    });

    // Platform Chips
    platformChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        platformChips.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentFilter.platform = chip.dataset.platform;
        renderFilteredHackathons();
    });

    // Prize Selector
    prizeSelect.addEventListener('change', (e) => {
        currentFilter.prize = e.target.value;
        renderFilteredHackathons();
    });

    // Sort select
    sortSelect.addEventListener('change', (e) => {
        currentFilter.sort = e.target.value;
        renderFilteredHackathons();
    });

    // Reset All Filters
    const resetFn = () => {
        currentFilter = {
            region: 'all',
            category: 'all',
            city: 'all',
            prize: 'all',
            platform: 'all',
            search: '',
            sort: 'featured'
        };
        searchInput.value = '';
        searchClearBtn.classList.add('hidden');
        regionTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.region === 'all'));
        categoryChips.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c.dataset.category === 'all'));
        cityChips.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c.dataset.city === 'all'));
        platformChips.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c.dataset.platform === 'all'));
        prizeSelect.value = 'all';
        sortSelect.value = 'featured';
        renderFilteredHackathons();
        showToast('All filters reset! 🔄');
    };

    if (resetFiltersBtn) resetFiltersBtn.addEventListener('click', resetFn);
    if (resetAllBtn) resetAllBtn.addEventListener('click', resetFn);

    // Refresh Data button
    refreshBtn.addEventListener('click', () => {
        fetchHackathons(true);
        showToast('Refreshing live data from all sources... ⚡');
    });

    // Export Dropdown
    exportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exportDropdown.classList.toggle('show');
    });

    document.addEventListener('click', () => {
        exportDropdown.classList.remove('show');
    });

    exportDropdown.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', (e) => {
            e.preventDefault();
            const format = a.dataset.export;
            triggerExport(format);
        });
    });

    // Alerts Modal
    alertsBtn.addEventListener('click', () => {
        alertsModal.classList.remove('hidden');
    });

    modalClose.addEventListener('click', () => {
        alertsModal.classList.add('hidden');
    });

    alertsModal.addEventListener('click', (e) => {
        if (e.target === alertsModal) alertsModal.classList.add('hidden');
    });

    // Modal tabs
    document.querySelectorAll('.modal-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.modal-tab-pane').forEach(p => p.classList.add('hidden'));
            btn.classList.add('active');
            const target = document.getElementById(btn.dataset.target);
            if (target) target.classList.remove('hidden');
        });
    });

    // WhatsApp test button
    const btnSendWa = document.getElementById('btn-send-wa');
    if (btnSendWa) {
        btnSendWa.addEventListener('click', async () => {
            const phone = document.getElementById('wa-phone').value.trim();
            const apikey = document.getElementById('wa-key').value.trim();
            const statusBox = document.getElementById('alert-status-msg');

            statusBox.className = 'status-box';
            statusBox.innerText = 'Sending message to your WhatsApp...';
            statusBox.classList.remove('hidden');

            try {
                const res = await fetch('/api/notify/whatsapp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: phone || null, apikey: apikey || null })
                });
                const data = await res.json();
                if (res.ok) {
                    statusBox.className = 'status-box success';
                    statusBox.innerText = `✓ ${data.message}`;
                } else {
                    statusBox.className = 'status-box error';
                    statusBox.innerText = `✗ ${data.detail || 'Failed to send WhatsApp alert'}`;
                }
            } catch (err) {
                statusBox.className = 'status-box error';
                statusBox.innerText = `✗ Network error: ${err.message}`;
            }
        });
    }

    // Telegram test button
    const btnSendTg = document.getElementById('btn-send-tg');
    if (btnSendTg) {
        btnSendTg.addEventListener('click', async () => {
            const token = document.getElementById('tg-token').value.trim();
            const chat = document.getElementById('tg-chat').value.trim();
            const statusBox = document.getElementById('alert-status-msg');
            
            statusBox.className = 'status-box';
            statusBox.innerText = 'Broadcasting to Telegram...';
            statusBox.classList.remove('hidden');

            try {
                const res = await fetch('/api/notify/telegram', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token: token || null, chat_id: chat || null })
                });
                const data = await res.json();
                if (res.ok) {
                    statusBox.className = 'status-box success';
                    statusBox.innerText = `✓ ${data.message}`;
                } else {
                    statusBox.className = 'status-box error';
                    statusBox.innerText = `✗ ${data.detail || 'Failed to broadcast alert'}`;
                }
            } catch (err) {
                statusBox.className = 'status-box error';
                statusBox.innerText = `✗ Network error: ${err.message}`;
            }
        });
    }

    // Discord test button
    const btnSendDiscord = document.getElementById('btn-send-discord');
    if (btnSendDiscord) {
        btnSendDiscord.addEventListener('click', async () => {
            const webhook = document.getElementById('discord-webhook').value.trim();
            const statusBox = document.getElementById('alert-status-msg');

            statusBox.className = 'status-box';
            statusBox.innerText = 'Sending alert...';
            statusBox.classList.remove('hidden');

            try {
                const res = await fetch('/api/notify/discord', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ webhook_url: webhook || null })
                });
                const data = await res.json();
                if (res.ok) {
                    statusBox.className = 'status-box success';
                    statusBox.innerText = `✓ ${data.message}`;
                } else {
                    statusBox.className = 'status-box error';
                    statusBox.innerText = `✗ ${data.detail || 'Failed to send alert'}`;
                }
            } catch (err) {
                statusBox.className = 'status-box error';
                statusBox.innerText = `✗ Network error: ${err.message}`;
            }
        });
    }
}

// Fetch Hackathons from API
async function fetchHackathons(forceRefresh = false) {
    loadingState.classList.remove('hidden');
    hackathonsGrid.classList.add('hidden');
    emptyState.classList.add('hidden');

    try {
        const url = `/api/hackathons?refresh=${forceRefresh}`;
        const res = await fetch(url);
        const data = await res.json();
        allHackathons = data.hackathons || [];
        
        if (syncTimeText) {
            syncTimeText.innerText = `Auto-synced (${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})`;
        }

        updateStats();
        renderFilteredHackathons();
    } catch (err) {
        console.error('Error fetching hackathons:', err);
        loadingState.innerHTML = `<p style="color: #f87171;">Failed to load hackathons. Please check connection and click Refresh.</p>`;
    } finally {
        loadingState.classList.add('hidden');
    }
}

function updateStats() {
    statTotal.innerText = allHackathons.length;
    statIndia.innerText = allHackathons.filter(h => h.is_india).length;
    statOnline.innerText = allHackathons.filter(h => h.is_online && !h.is_india).length;
}

// Filter and Render Hackathons
function renderFilteredHackathons() {
    let filtered = [...allHackathons];

    // 1. Region Filter
    if (currentFilter.region === 'india') {
        filtered = filtered.filter(h => h.is_india);
    } else if (currentFilter.region === 'online') {
        filtered = filtered.filter(h => h.is_online && !h.is_india);
    }

    // 2. Category Track Filter
    if (currentFilter.category !== 'all') {
        filtered = filtered.filter(h => (h.category || '').toLowerCase() === currentFilter.category.toLowerCase());
    }

    // 3. City Filter
    if (currentFilter.city !== 'all') {
        filtered = filtered.filter(h => (h.city || '').toLowerCase() === currentFilter.city.toLowerCase());
    }

    // 4. Platform Filter
    if (currentFilter.platform !== 'all') {
        filtered = filtered.filter(h => h.platform.toLowerCase() === currentFilter.platform.toLowerCase());
    }

    // 5. Prize Pool Filter
    if (currentFilter.prize === 'mega') {
        filtered = filtered.filter(h => (h.prize_usd_approx || 0) >= 6000);
    } else if (currentFilter.prize === 'high') {
        filtered = filtered.filter(h => (h.prize_usd_approx || 0) >= 1000 && (h.prize_usd_approx || 0) < 6000);
    } else if (currentFilter.prize === 'cash') {
        filtered = filtered.filter(h => (h.prize_usd_approx || 0) > 0);
    } else if (currentFilter.prize === 'swag') {
        filtered = filtered.filter(h => (h.prize_usd_approx || 0) === 0);
    }

    // 6. Search Query
    if (currentFilter.search) {
        const q = currentFilter.search;
        filtered = filtered.filter(h =>
            h.title.toLowerCase().includes(q) ||
            (h.description || '').toLowerCase().includes(q) ||
            (h.location || '').toLowerCase().includes(q) ||
            (h.city || '').toLowerCase().includes(q) ||
            (h.category || '').toLowerCase().includes(q) ||
            (h.prize_pool || '').toLowerCase().includes(q) ||
            h.tags.some(t => t.toLowerCase().includes(q))
        );
    }

    // 7. Sort
    if (currentFilter.sort === 'name') {
        filtered.sort((a, b) => a.title.localeCompare(b.title));
    } else if (currentFilter.sort === 'prizes') {
        filtered.sort((a, b) => (b.prize_usd_approx || 0) - (a.prize_usd_approx || 0));
    }

    resultsCount.innerText = filtered.length;

    if (filtered.length === 0) {
        hackathonsGrid.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');
    hackathonsGrid.classList.remove('hidden');
    hackathonsGrid.innerHTML = filtered.map(h => createHackathonCardHtml(h)).join('');
    lucide.createIcons();
    attachCardActionHandlers();
}

function createHackathonCardHtml(h) {
    const modeBadge = h.is_india 
        ? `<span class="card-mode-badge india">🇮🇳 India</span>` 
        : `<span class="card-mode-badge">🌐 Global Online</span>`;

    const prize = h.prize_pool || 'Prizes & Swag';
    const locationStr = h.city && h.city !== 'Online (Virtual)' ? `${h.city} • ${h.location || 'In-Person'}` : (h.location || 'Online');
    const categoryBadge = `<span class="card-category-badge">${escapeHtml(h.category || 'Open')}</span>`;
    const tagsHtml = h.tags.slice(0, 3).map(t => `<span class="tag-pill">${escapeHtml(t)}</span>`).join('');

    return `
        <article class="hackathon-card">
            <div class="card-header-bar">
                <div style="display: flex; gap: 0.4rem; align-items: center;">
                    <span class="platform-tag plat-${h.platform}">${h.platform}</span>
                    ${categoryBadge}
                </div>
                ${modeBadge}
            </div>

            <div class="card-body">
                <h3 class="card-title" title="${escapeHtml(h.title)}">${escapeHtml(h.title)}</h3>
                <p class="card-desc">${escapeHtml(h.description || `Build and compete at ${h.title} on ${h.platform}.`)}</p>

                <div class="card-info-grid">
                    <div class="info-item">
                        <span class="info-label">Prize Pool</span>
                        <span class="info-val val-prize">${escapeHtml(prize)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">City / Venue</span>
                        <span class="info-val" title="${escapeHtml(locationStr)}">${escapeHtml(locationStr)}</span>
                    </div>
                </div>

                <div class="tags-list">
                    ${tagsHtml}
                </div>
            </div>

            <div class="card-footer">
                <a href="${h.url}" target="_blank" rel="noopener noreferrer" class="btn-apply">
                    <span>Apply / View</span>
                    <i data-lucide="external-link"></i>
                </a>
                <button class="btn-icon-action btn-copy" data-url="${h.url}" title="Copy Direct Link">
                    <i data-lucide="copy"></i>
                </button>
                <button class="btn-icon-action btn-calendar" 
                    data-title="${escapeHtml(h.title)}" 
                    data-url="${h.url}" 
                    data-desc="${escapeHtml(h.description || '')}"
                    title="Add to Google Calendar">
                    <i data-lucide="calendar"></i>
                </button>
            </div>
        </article>
    `;
}

function attachCardActionHandlers() {
    // Copy URL handler
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const url = btn.dataset.url;
            navigator.clipboard.writeText(url).then(() => {
                showToast('Link copied to clipboard! 📋');
            });
        });
    });

    // Calendar Handler
    document.querySelectorAll('.btn-calendar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const title = encodeURIComponent(btn.dataset.title);
            const details = encodeURIComponent(`${btn.dataset.desc}\n\nApply here: ${btn.dataset.url}`);
            const calUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&location=Online`;
            window.open(calUrl, '_blank');
        });
    });
}

function triggerExport(format) {
    const params = new URLSearchParams({
        format: format,
        ...(currentFilter.region === 'india' && { india_only: 'true' }),
        ...(currentFilter.region === 'online' && { online_only: 'true' }),
        ...(currentFilter.category !== 'all' && { category: currentFilter.category }),
        ...(currentFilter.city !== 'all' && { city: currentFilter.city }),
        ...(currentFilter.platform !== 'all' && { platform: currentFilter.platform }),
        ...(currentFilter.search && { q: currentFilter.search })
    });
    window.location.href = `/api/export?${params.toString()}`;
    showToast(`Downloading ${format.toUpperCase()} export... 🚀`);
}

function showToast(message) {
    toastMessage.innerText = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 2800);
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
