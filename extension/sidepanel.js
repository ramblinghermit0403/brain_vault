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
                showError(searchResults, response.error);
            }
        } catch (err) {
            showError(searchResults, err.message);
        } finally {
            setLoading(searchBtn, false, 'Search');
        }
    });

    // Fetch latest memories and files when Retrieve tab is clicked
    document.querySelector('.tab[data-tab="search"]').addEventListener('click', async () => {
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
                showError(searchResults, response.error);
            }
        } catch (err) {
            showError(searchResults, err.message);
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
            const displayContent = item.content.length > 150 ? item.content.substring(0, 150) + '...' : item.content;
            const title = item.metadata.title || item.metadata.type;
            const date = item.metadata.created_at ? new Date(item.metadata.created_at).toLocaleDateString() : '';

            div.innerHTML = `
                <div class="result-header" style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span class="result-meta" style="font-weight:600;">${title}</span>
                    <span class="result-meta">${date}</span>
                </div>
                <div style="margin-bottom:8px;">${displayContent}</div>
                <button class="secondary-btn copy-btn" style="padding:4px 8px; font-size:11px; width:auto; margin-top:0;">Copy</button>
            `;

            // Add copy functionality
            const copyBtn = div.querySelector('.copy-btn');
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(item.content);
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => copyBtn.textContent = originalText, 1500);
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

    function showError(el, msg) {
        el.textContent = 'Error: ' + msg;
        el.classList.remove('hidden');
        el.classList.add('error'); // Ensure error styling if applicable
    }
});
