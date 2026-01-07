document.addEventListener('DOMContentLoaded', async () => {
    // Views
    const loginView = document.getElementById('login-view');
    const mainApp = document.getElementById('main-app');

    // Login Elements

    const saveTokenBtn = document.getElementById('save-token');
    const logoutBtn = document.getElementById('logout-btn');

    // Tabs
    const tabs = document.querySelectorAll('.tab-segment');
    const views = document.querySelectorAll('.view');

    // Generate Elements
    const genQuery = document.getElementById('gen-query');
    const genBtn = document.getElementById('gen-btn');
    const genResult = document.getElementById('gen-result');
    const genCopy = document.getElementById('gen-copy');
    const modelParamsInput = document.getElementById('model-params'); // NEW

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
    // 1. Generate Prompt
    genBtn.addEventListener('click', async () => {
        const query = genQuery.value.trim();
        const modelParams = modelParamsInput ? modelParamsInput.value.trim() : '';

        if (!query) return;

        setLoading(genBtn, true, 'Generating...');
        genResult.classList.add('hidden');
        genCopy.classList.add('hidden');

        try {
            // Send modelParams along with query
            const response = await sendMessage('generatePrompt', { query, model_params: modelParams });
            if (response.success) {
                genResult.textContent = response.data.prompt;
                genResult.classList.remove('hidden');
                genCopy.classList.remove('hidden');
            } else {
                showToast(response.error, 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(genBtn, false, 'Generate Prompt');
        }
    });

    genCopy.addEventListener('click', () => {
        navigator.clipboard.writeText(genResult.textContent);
        showToast('Prompt copied to clipboard!');
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
                showToast('Memory saved successfully!');
            } else {
                showToast(response.error, 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(saveBtn, false, 'Save to Memory');
        }
    });

    // 3. Search Memory
    searchBtn.addEventListener('click', async () => {
        const query = searchQuery.value.trim();
        if (!query) return;

        setLoading(searchBtn, true, 'Searching...');
        searchResults.classList.add('hidden');
        searchResults.innerHTML = '';

        try {
            const response = await sendMessage('searchMemory', { query });
            if (response.success) {
                renderResults(response.data);
            } else {
                showToast(response.error, 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(searchBtn, false, 'Search');
        }
    });

    // Fetch latest memories and files when Retrieve tab is clicked
    document.querySelector('.tab-segment[data-tab="search"]').addEventListener('click', async () => {
        searchResults.innerHTML = '<div class="status-msg">Loading latest items...</div>';
        searchResults.classList.remove('hidden');

        try {
            const response = await sendMessage('getDocuments', {});
            if (response.success) {
                // Process Memories
                const memories = response.data
                    .filter(d => d.doc_type === 'memory')
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                    .slice(0, 5)
                    .map(d => ({
                        content: d.content,
                        metadata: { type: 'Memory', created_at: d.created_at, title: d.title }
                    }));

                // Process Files
                const files = response.data
                    .filter(d => d.doc_type === 'file')
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                    .slice(0, 5)
                    .map(d => ({
                        content: d.content,
                        metadata: { type: 'File', created_at: d.created_at, title: d.title }
                    }));

                searchResults.innerHTML = '';

                if (memories.length > 0) {
                    const memHeader = document.createElement('div');
                    memHeader.className = 'result-meta';
                    memHeader.style.marginTop = '12px';
                    memHeader.textContent = 'RECENT MEMORIES';
                    searchResults.appendChild(memHeader);
                    renderResultItems(memories, searchResults);
                }

                if (files.length > 0) {
                    const fileHeader = document.createElement('div');
                    fileHeader.className = 'result-meta';
                    fileHeader.style.marginTop = '16px';
                    fileHeader.textContent = 'RECENT FILES';
                    searchResults.appendChild(fileHeader);
                    renderResultItems(files, searchResults);
                }

                if (memories.length === 0 && files.length === 0) {
                    searchResults.innerHTML = '<div class="status-msg">No items found.</div>';
                }
            } else {
                showToast(response.error, 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    function renderResults(items) {
        searchResults.innerHTML = '';
        if (items.length === 0) {
            searchResults.textContent = 'No results found.';
            searchResults.classList.remove('hidden');
            return;
        }
        renderResultItems(items, searchResults);
        searchResults.classList.remove('hidden');
    }

    function renderResultItems(items, container) {
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'result-item';

            // Truncate content for display
            const MAX_LENGTH = 150;
            const displayContent = item.content.length > MAX_LENGTH
                ? item.content.substring(0, MAX_LENGTH) + '...'
                : item.content;

            // Handle different metadata structures (flat vs nested)
            let title = "Unknown";
            let dateStr = "";
            let score = "";

            if (item.metadata) {
                // If it's a search result from vector store, metadata is flat
                // If it's from getDocuments, we manually constructed metadata object
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
                <div class="result-content" style="margin-bottom:12px;">${displayContent}</div>
                <button class="secondary-btn copy-btn" style="width:100%; margin-top:0;">Copy to Clipboard</button>
            `;

            // Add copy functionality
            const copyBtn = div.querySelector('.copy-btn');
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(item.content);
                showToast('Copied to clipboard!');
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

    // New Toast Function
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        // Icon based on type
        const icon = type === 'error' ? '❌' : 'ℹ️';
        if (type === 'success') icon = '✅'; // Optional if used explicitly

        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

        container.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'toastFadeOut 0.3s ease-out forwards';
            setTimeout(() => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            }, 300); // Wait for fade out
        }, 3000);
    }

    // Deprecated but kept for compatibility logic updates above -> redirected to showToast
    function showError(el, msg) {
        showToast(msg, 'error');
    }
});
