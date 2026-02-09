// Background script for Brain Vault Extension

const API_BASE_URL = 'http://localhost:8000/api/v1';

// --- Auth Helper ---

async function fetchWithAuth(endpoint, options = {}) {
    // 1. Get Tokens
    const { token, refreshToken } = await chrome.storage.local.get(['token', 'refreshToken']);

    if (!token) {
        throw new Error('Not authenticated. Please login via the side panel.');
    }

    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    // 2. Initial Request
    let response = await fetch(url, { ...options, headers });

    // 3. Handle 401 (Refresh Logic)
    if (response.status === 401) {
        console.log("Token expired, attempting refresh...");

        if (!refreshToken) {
            await logout();
            throw new Error('Session expired. Please login again.');
        }

        try {
            // Try explicit refresh
            const refreshResp = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }) // Backend schema expected
            });

            if (!refreshResp.ok) {
                console.error("Refresh failed", await refreshResp.text());
                throw new Error('Refresh failed');
            }

            const data = await refreshResp.json();

            // Save new tokens
            await chrome.storage.local.set({
                token: data.access_token,
                refreshToken: data.refresh_token || refreshToken // Use new or keep old
            });

            console.log("Token refreshed successfully.");

            // Retry Original Request
            headers['Authorization'] = `Bearer ${data.access_token}`;
            response = await fetch(url, { ...options, headers });

        } catch (err) {
            console.error("Auth Loop Error:", err);
            await logout();
            throw new Error('Session expired. Please login again.');
        }
    }

    // 4. Handle Standard Errors
    if (!response.ok) {
        let errorMsg = 'Request failed';
        try {
            const errorData = await response.json();
            errorMsg = errorData.detail || errorMsg;
        } catch (e) { }
        throw new Error(errorMsg);
    }

    return await response.json();
}

async function logout() {
    await chrome.storage.local.remove(['token', 'refreshToken', 'user']);
    // Optional: Notify sidepanel to show login screen
    // runtime.sendMessage not reliable if popup closed, but storage listener handles UI
}

async function generatePrompt(data) {
    return await fetchWithAuth('/prompts/generate', {
        method: 'POST',
        body: JSON.stringify({
            query: data.query,
            template_id: data.templateId || 'standard',
            context_size: 2000
        })
    });
}

async function saveMemory(data) {
    return await fetchWithAuth('/memory/', {
        method: 'POST',
        body: JSON.stringify({
            title: data.title,
            content: data.content,
            tags: ['extension']
        })
    });
}

async function searchMemory(data) {
    return await fetchWithAuth('/retrieval/search', {
        method: 'POST',
        body: JSON.stringify({
            query: data.query,
            top_k: data.top_k || 5,
            view: "auto"
        })
    });
}

async function getDocuments() {
    return await fetchWithAuth('/memory/', {
        method: 'GET'
    });
}

async function getMemories() {
    return await fetchWithAuth('/memory/', {
        method: 'GET'
    });
}

async function saveLLMMemory(data) {
    return await fetchWithAuth('/llm/save_memory', {
        method: 'POST',
        body: JSON.stringify({
            content: data.content,
            source_llm: data.source || 'extension_content_script',
            model_name: data.model || 'unknown',
            tags: ['extension', data.source],
            url: data.url
        })
    });
}

async function ingestUrl(data) {
    return await fetchWithAuth('/ingest/url', {
        method: 'POST',
        body: JSON.stringify({
            url: data.url,
            tags: ['extension', 'web-clip']
        })
    });
}

async function ingestYouTube(data) {
    return await fetchWithAuth('/documents/upload-youtube', {
        method: 'POST',
        body: JSON.stringify({
            url: data.url,
            tags: ['extension']
        })
    });
}

// --- Message Router ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'saveToken') {
        chrome.storage.local.set({
            token: request.token,
            refreshToken: request.refreshToken,
            user: request.user
        }).then(() => {
            console.log('Token saved to extension storage.');
            sendResponse({ success: true });
        });
        return true; // Async response
    }

    // Handlers that require async response
    const handleAsync = async () => {
        try {
            let result;
            switch (request.action) {
                case 'saveLLMMemory':
                    result = await saveLLMMemory(request.data);
                    break;
                case 'ingestPage':
                    result = await ingestUrl(request.data);
                    break;
                case 'ingestYouTube': // NEW Special handler for YouTube
                    result = await ingestYouTube(request.data);
                    break;
                case 'searchMemory':
                    result = await searchMemory(request.data);
                    break;
                case 'generatePrompt':
                    result = await generatePrompt(request.data);
                    break;
                case 'saveMemory':
                    result = await saveMemory(request.data);
                    break;
                case 'getDocuments':
                    result = await getDocuments();
                    break;
                case 'getMemories':
                    result = await getMemories();
                    break;
                default:
                    throw new Error(`Unknown action: ${request.action}`);
            }
            sendResponse({ success: true, data: result });
        } catch (error) {
            console.error(`Action ${request.action} failed:`, error);
            sendResponse({ success: false, error: error.message });
        }
    };

    // Trigger async handler for data actions
    if (['saveLLMMemory', 'ingestPage', 'ingestYouTube', 'searchMemory', 'generatePrompt', 'saveMemory', 'getDocuments', 'getMemories'].includes(request.action)) {
        handleAsync();
        return true; // Keep channel open
    }
});

// --- Setup Side Panel Behavior ---
chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error) => console.error(error));

// --- Context Menus ---
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "memwyre-save-page",
        title: "Save Page to MemWyre",
        contexts: ["page"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "memwyre-save-page") {
        // Send message to internal router directly (reusing ingestUrl logic)
        ingestUrl({ url: tab.url, title: tab.title })
            .then(() => {
                // Optional: Notify user via script injection or badge
                console.log("Page saved via context menu");
                chrome.action.setBadgeText({ text: "OK", tabId: tab.id });
                setTimeout(() => chrome.action.setBadgeText({ text: "", tabId: tab.id }), 2000);
            })
            .catch((err) => {
                console.error("Context Menu Save Failed", err);
                chrome.action.setBadgeText({ text: "ERR", tabId: tab.id });
                chrome.action.setBadgeBackgroundColor({ color: "#FF0000", tabId: tab.id });
            });
    }
});
