document.addEventListener('DOMContentLoaded', async () => {
    // Views
    const loginView = document.getElementById('login-view');
    const mainApp = document.getElementById('main-app');

    // Login Elements
    const tokenInput = document.getElementById('token-input');
    const saveTokenBtn = document.getElementById('save-token');
    const logoutBtn = document.getElementById('logout-btn');

    // Tabs
    const tabs = document.querySelectorAll('.tab');
    const views = document.querySelectorAll('.view');

    // Generate Elements
    const genQuery = document.getElementById('gen-query');
    const genBtn = document.getElementById('gen-btn');
    const genResult = document.getElementById('gen-result');
    const genCopy = document.getElementById('gen-copy');

    // Save Elements
    const saveTitle = document.getElementById('save-title');
    const saveContent = document.getElementById('save-content');
    const saveBtn = document.getElementById('save-btn');
    const saveStatus = document.getElementById('save-status');

    // Search Elements
    const searchQuery = document.getElementById('search-query');
    const searchBtn = document.getElementById('search-btn');
    const searchResults = document.getElementById('search-results');

    // Check Auth
    const { token } = await chrome.storage.local.get('token');
    if (token) {
        showMain();
    } else {
        showLogin();
    }

    // --- Auth Handlers ---

    saveTokenBtn.addEventListener('click', async () => {
        const token = tokenInput.value.trim();
        if (token) {
            await chrome.storage.local.set({ token });
            showMain();
        }
    });

    logoutBtn.addEventListener('click', async () => {
        await chrome.storage.local.remove('token');
        showLogin();
    });

    function showLogin() {
        loginView.classList.remove('hidden');
        mainApp.classList.add('hidden');
    }

    function showMain() {
        loginView.classList.add('hidden');
        mainApp.classList.remove('hidden');
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
        });
    });

    // --- Feature Handlers ---

    // 1. Generate Prompt
    genBtn.addEventListener('click', async () => {
        const query = genQuery.value.trim();
        if (!query) return;

        setLoading(genBtn, true, 'Generating...');
        genResult.classList.add('hidden');
        genCopy.classList.add('hidden');

        try {
            const response = await sendMessage('generatePrompt', { query });
            if (response.success) {
                genResult.textContent = response.data.prompt;
                genResult.classList.remove('hidden');
                genCopy.classList.remove('hidden');
            } else {
                showError(genResult, response.error);
            }
        } catch (err) {
            showError(genResult, err.message);
        } finally {
            setLoading(genBtn, false, 'Generate Prompt');
        }
    });

    genCopy.addEventListener('click', () => {
        navigator.clipboard.writeText(genResult.textContent);
        genCopy.textContent = 'Copied!';
        setTimeout(() => genCopy.textContent = 'Copy to Clipboard', 2000);
    });

    // 2. Save Memory
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
                saveStatus.textContent = 'Saved successfully!';
                saveStatus.className = 'success';
            } else {
                saveStatus.textContent = 'Error: ' + response.error;
                saveStatus.className = 'error';
            }
        } catch (err) {
            saveStatus.textContent = 'Error: ' + err.message;
            saveStatus.className = 'error';
        } finally {
            setLoading(saveBtn, false, 'Save to Memory');
        }
    });

    // 3. Search Memory & List Memories
    const recentMemories = document.getElementById('recent-memories');

    // Load memories on startup if in main view
    if (token) {
        loadMemories();
    }

    async function loadMemories() {
        recentMemories.innerHTML = '<div class="loading-spinner" style="text-align:center; color:#9ca3af; font-size:12px; padding:20px;">Loading recent memories...</div>';
        try {
            const response = await sendMessage('getMemories');
            if (response.success) {
                renderMemories(response.data, recentMemories);
            } else {
                recentMemories.innerHTML = `<div class="error">Error loading memories: ${response.error}</div>`;
            }
        } catch (err) {
            recentMemories.innerHTML = `<div class="error">Error: ${err.message}</div>`;
        }
    }

    function renderMemories(items, container) {
        container.innerHTML = '';
        if (items.length === 0) {
            container.innerHTML = '<div style="text-align:center; color:#9ca3af; font-size:12px; padding:20px;">No memories found.</div>';
            return;
        }

        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'memory-item';

            // Format date
            const date = new Date(item.created_at).toLocaleDateString();
            const type = item.type === 'memory' ? 'Memory' : 'Document';
            const typeColor = item.type === 'memory' ? '#10b981' : '#3b82f6';

            div.innerHTML = `
                <div class="memory-header">
                    <h3 class="memory-title">${item.title || 'Untitled'}</h3>
                    <span class="memory-meta" style="color:${typeColor}">${type} • ${date}</span>
                </div>
                <div class="memory-content">${item.content}</div>
                <button class="copy-btn" data-content="${encodeURIComponent(item.content)}">Copy</button>
            `;
            container.appendChild(div);
        });

        // Add event listeners for copy buttons
        container.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const content = decodeURIComponent(e.target.dataset.content);
                navigator.clipboard.writeText(content);
                const originalText = e.target.textContent;
                e.target.textContent = 'Copied!';
                setTimeout(() => e.target.textContent = originalText, 1500);
            });
        });
    }

    searchBtn.addEventListener('click', async () => {
        const query = searchQuery.value.trim();
        if (!query) {
            // If empty, reload recent
            searchResults.classList.add('hidden');
            recentMemories.classList.remove('hidden');
            loadMemories();
            return;
        }

        setLoading(searchBtn, true, 'Searching...');
        searchResults.classList.add('hidden');
        recentMemories.classList.add('hidden'); // Hide recent list while searching
        searchResults.innerHTML = '';

        try {
            const response = await sendMessage('searchMemory', { query });
            if (response.success) {
                if (response.data.length === 0) {
                    searchResults.innerHTML = '<div style="text-align:center; color:#9ca3af; font-size:12px; padding:20px;">No results found.</div>';
                } else {
                    // Reuse render logic but map search results to format
                    const formattedResults = response.data.map(res => ({
                        title: res.metadata.title || 'Search Result',
                        content: res.content,
                        created_at: res.metadata.created_at || new Date().toISOString(),
                        type: res.metadata.doc_type || 'memory'
                    }));
                    renderMemories(formattedResults, searchResults);
                }
                searchResults.classList.remove('hidden');
            } else {
                showError(searchResults, response.error);
            }
        } catch (err) {
            showError(searchResults, err.message);
        } finally {
            setLoading(searchBtn, false, 'Search');
        }
    });

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

    function showError(el, msg) {
        el.textContent = 'Error: ' + msg;
        el.classList.remove('hidden');
        el.classList.add('error'); // Ensure error styling if applicable
    }
});
