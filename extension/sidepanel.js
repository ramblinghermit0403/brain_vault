document.addEventListener('DOMContentLoaded', async () => {
    // Views
    const loginView = document.getElementById('login-view');
    const mainApp = document.getElementById('main-app');

    // Login Elements
    const saveTokenBtn = document.getElementById('save-token');
    const logoutBtn = document.getElementById('logout-btn');

    // Settings Elements
    const settingsBtn = document.getElementById('settings-btn');
    const backSettingsBtn = document.getElementById('back-from-settings');
    const viewSettings = document.getElementById('view-settings');
    const tabsContainer = document.getElementById('tabs-container');

    // Tabs
    const tabs = document.querySelectorAll('.tab-segment');
    const views = document.querySelectorAll('.view');

    // Save Elements
    const saveTitle = document.getElementById('save-title');
    const saveContent = document.getElementById('save-content');
    const saveBtn = document.getElementById('save-btn');
    const saveStatus = document.getElementById('save-status');

    // Search Elements
    const searchQuery = document.getElementById('search-query');
    const searchBtn = document.getElementById('search-btn');
    const searchResults = document.getElementById('search-results');
    const searchK = document.getElementById('search-k');

    // Memories Elements
    const refreshBtn = document.getElementById('refresh-memories');

    // Check Auth
    const { token } = await chrome.storage.local.get('token');
    if (token) {
        showMain();
    } else {
        showLogin();
    }

    // Listen for token changes (Auto-update UI after login)
    chrome.storage.onChanged.addListener((changes, area) => {
        if (area === 'local' && changes.token) {
            if (changes.token.newValue) {
                showMain();
            } else {
                showLogin();
            }
        }
    });

    // --- Auth Handlers ---

    saveTokenBtn.addEventListener('click', () => {
        chrome.tabs.create({ url: 'http://localhost:5173/login?source=extension' });
    });

    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await chrome.storage.local.remove('token');
            showLogin();
        });
    }

    // --- Settings Navigation ---

    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            // Hide all views and tabs
            views.forEach(v => v.classList.remove('active'));
            tabsContainer.classList.add('hidden');

            // Show settings
            viewSettings.classList.add('active');
        });
    }

    if (backSettingsBtn) {
        backSettingsBtn.addEventListener('click', () => {
            // Hide settings
            viewSettings.classList.remove('active');
            tabsContainer.classList.remove('hidden');

            // Restore active tab (default to memories if none)
            const activeTab = document.querySelector('.tab-segment.active');
            if (activeTab) {
                const targetId = activeTab.getAttribute('data-tab');
                document.getElementById(`view-${targetId}`).classList.add('active');
            } else {
                document.getElementById('view-memories').classList.add('active');
            }
        });
    }

    function showLogin() {
        loginView.classList.remove('hidden');
        mainApp.classList.add('hidden');
    }

    function showMain() {
        loginView.classList.add('hidden');
        mainApp.classList.remove('hidden');

        // Ensure settings are closed and tabs are visible
        if (viewSettings) viewSettings.classList.remove('active');
        if (tabsContainer) tabsContainer.classList.remove('hidden');

        // Restore active view based on active tab
        const activeTab = document.querySelector('.tab-segment.active');
        if (activeTab) {
            const targetId = activeTab.getAttribute('data-tab');
            const targetView = document.getElementById(`view-${targetId}`);
            if (targetView) targetView.classList.add('active');

            // If memories is the active tab, load content
            if (targetId === 'memories') {
                setTimeout(() => loadMemoriesAndDocuments(), 100);
            }
        } else {
            // Default fallback if no tab is active
            const memTab = document.querySelector('[data-tab="memories"]');
            if (memTab) memTab.classList.add('active');

            const memView = document.getElementById('view-memories');
            if (memView) memView.classList.add('active');

            setTimeout(() => loadMemoriesAndDocuments(), 100);
        }
    }

    // --- Tab Handlers ---

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all
            tabs.forEach(t => t.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));

            // Add active class to clicked
            tab.classList.add('active');
            const viewId = `view-${tab.dataset.tab}`;
            document.getElementById(viewId).classList.add('active');

            // Load data for Memories tab
            if (tab.dataset.tab === 'memories') {
                loadMemoriesAndDocuments();
            }
        });
    });

    // --- Feature Handlers ---

    // 1. Save Memory
    saveBtn.addEventListener('click', async () => {
        const content = saveContent.value.trim();
        const title = saveTitle.value.trim() || 'Extension Clip';

        if (!content) return;

        setLoading(saveBtn, true, 'Saving...');
        saveStatus.className = 'hidden';

        try {
            const response = await sendMessage('saveMemory', { title, content });
            if (response.success) {
                saveContent.value = '';
                saveTitle.value = '';
                showToast('Memory saved successfully!');
            } else {
                showToast(response.error, 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(saveBtn, false, 'Save Memory');
        }
    });

    // 2. Search Memory with custom k value and filter
    const searchIcon = document.getElementById('search-icon');
    const loadingIcon = document.getElementById('loading-icon');
    const searchFilter = document.getElementById('search-filter');

    searchBtn.addEventListener('click', async () => {
        const query = searchQuery.value.trim();
        if (!query) return;

        const topK = parseInt(searchK.value) || 5;
        const filter = searchFilter.value;

        // Show loading state
        searchBtn.disabled = true;
        searchIcon.classList.add('hidden');
        loadingIcon.classList.remove('hidden');
        searchResults.classList.add('hidden');
        searchResults.innerHTML = '';

        try {
            const response = await sendMessage('searchMemory', { query, top_k: topK });
            if (response.success) {
                renderResults(response.data, filter);
            } else {
                showToast(response.error, 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            // Reset loading state
            searchBtn.disabled = false;
            searchIcon.classList.remove('hidden');
            loadingIcon.classList.add('hidden');
        }
    });

    // Allow Enter key to search
    searchQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });

    // 3. Load Memories and Documents with filter
    const memoriesContainer = document.getElementById('memories-container');
    const memoriesFilter = document.getElementById('memories-filter');
    let allMemoriesData = { memories: [], documents: [] }; // Cache data

    async function loadMemoriesAndDocuments() {
        memoriesContainer.innerHTML = '<div class="status-msg">Loading...</div>';

        try {
            const response = await sendMessage('getDocuments', {});
            if (response.success) {
                // Process Memories
                allMemoriesData.memories = response.data
                    .filter(d => d.doc_type === 'memory')
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                    .slice(0, 15)
                    .map(d => ({
                        content: d.content,
                        metadata: { type: 'memory', created_at: d.created_at, title: d.title }
                    }));

                // Process Documents/Files
                allMemoriesData.documents = response.data
                    .filter(d => d.doc_type === 'file' || d.doc_type === 'document')
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                    .slice(0, 15)
                    .map(d => ({
                        content: d.content || d.title || 'No content',
                        metadata: { type: 'document', created_at: d.created_at, title: d.title }
                    }));

                // Render based on filter
                renderMemoriesWithFilter();
            } else {
                showToast(response.error, 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
            memoriesContainer.innerHTML = '<div class="status-msg">Error loading data.</div>';
        }
    }

    function renderMemoriesWithFilter() {
        const filter = memoriesFilter.value;
        memoriesContainer.innerHTML = '';

        let itemsToRender = [];

        if (filter === 'all') {
            // Show memories section
            if (allMemoriesData.memories.length > 0) {
                const memHeader = document.createElement('div');
                memHeader.className = 'section-header';
                memHeader.innerHTML = '<span class="section-title">Memories</span>';
                memoriesContainer.appendChild(memHeader);
                renderResultItems(allMemoriesData.memories, memoriesContainer);
            }
            // Show documents section
            if (allMemoriesData.documents.length > 0) {
                const docHeader = document.createElement('div');
                docHeader.className = 'section-header';
                docHeader.style.marginTop = '16px';
                docHeader.innerHTML = '<span class="section-title">Documents</span>';
                memoriesContainer.appendChild(docHeader);
                renderResultItems(allMemoriesData.documents, memoriesContainer);
            }
            if (allMemoriesData.memories.length === 0 && allMemoriesData.documents.length === 0) {
                memoriesContainer.innerHTML = '<div class="status-msg">No items yet.</div>';
            }
        } else if (filter === 'memories') {
            if (allMemoriesData.memories.length > 0) {
                renderResultItems(allMemoriesData.memories, memoriesContainer);
            } else {
                memoriesContainer.innerHTML = '<div class="status-msg">No memories yet.</div>';
            }
        } else if (filter === 'documents') {
            if (allMemoriesData.documents.length > 0) {
                renderResultItems(allMemoriesData.documents, memoriesContainer);
            } else {
                memoriesContainer.innerHTML = '<div class="status-msg">No documents yet.</div>';
            }
        }
    }

    // Filter change handler
    if (memoriesFilter) {
        memoriesFilter.addEventListener('change', renderMemoriesWithFilter);
    }

    // Refresh button
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadMemoriesAndDocuments);
    }

    function renderResults(items, filter = 'all') {
        searchResults.innerHTML = '';

        if (items.length === 0) {
            searchResults.textContent = 'No results found.';
            searchResults.classList.remove('hidden');
            return;
        }

        // Separate facts and chunks/memories
        let facts = items.filter(item => item.metadata?.type === 'fact');
        let chunks = items.filter(item => item.metadata?.type !== 'fact');

        // Apply filter
        if (filter === 'facts') {
            chunks = [];
        } else if (filter === 'memories') {
            facts = [];
        }

        // Check if anything to show
        if (facts.length === 0 && chunks.length === 0) {
            searchResults.textContent = 'No results found.';
            searchResults.classList.remove('hidden');
            return;
        }

        // Render Chunks/Memories section
        if (chunks.length > 0) {
            const chunksHeader = document.createElement('div');
            chunksHeader.className = 'section-header';
            chunksHeader.innerHTML = '<span class="section-title">Memories</span>';
            searchResults.appendChild(chunksHeader);
            renderResultItems(chunks, searchResults);
        }

        // Render Facts section
        if (facts.length > 0) {
            const factsHeader = document.createElement('div');
            factsHeader.className = 'section-header';
            factsHeader.style.marginTop = '16px';
            factsHeader.innerHTML = '<span class="section-title">Facts</span>';
            searchResults.appendChild(factsHeader);
            renderResultItems(facts, searchResults);
        }

        searchResults.classList.remove('hidden');
    }

    function renderResultItems(items, container) {
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'result-item';

            // Handle both 'text' (from search results) and 'content' (from documents)
            const itemContent = item.content || item.text || '';

            // Truncate content for display
            const MAX_LENGTH = 150;
            const displayContent = itemContent.length > MAX_LENGTH
                ? itemContent.substring(0, MAX_LENGTH) + '...'
                : itemContent;

            // Handle different metadata structures (flat vs nested)
            let title = "Unknown";
            let dateStr = "";
            let score = "";

            if (item.metadata) {
                title = item.metadata.title || item.metadata.source || "Untitled";
                if (item.metadata.created_at) {
                    dateStr = new Date(item.metadata.created_at).toLocaleDateString();
                }
            }
            if (item.score) {
                score = Math.round(item.score * 100) + '%';
            }

            div.innerHTML = `
                <div class="result-header" style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span class="result-title">${title}</span>
                    <span class="result-meta">${score || dateStr}</span>
                </div>
                <div class="result-content" style="margin-bottom:8px;">${displayContent}</div>
                <button class="secondary-btn copy-btn" style="width:100%; margin-top:0;">Copy to Clipboard</button>
            `;

            // Add copy functionality with visual feedback
            const copyBtn = div.querySelector('.copy-btn');
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(itemContent);

                // Visual feedback - green button with "Copied" text
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('copied');

                setTimeout(() => {
                    copyBtn.textContent = originalText;
                    copyBtn.classList.remove('copied');
                }, 2000);
            });

            container.appendChild(div);
        });
    }

    // --- Helpers ---

    function sendMessage(action, data) {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({ action, data }, (response) => {
                resolve(response || { success: false, error: 'No response from background script' });
            });
        });
    }

    function setLoading(btn, isLoading, text) {
        btn.disabled = isLoading;
        btn.textContent = text;
    }

    // Toast Function
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        // Icon based on type
        let icon = type === 'error' ? '❌' : 'ℹ️';
        if (type === 'success') icon = '✅';

        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

        container.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'toastFadeOut 0.3s ease-out forwards';
            setTimeout(() => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
});
