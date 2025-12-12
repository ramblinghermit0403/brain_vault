// Background script for Brain Vault Extension

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Open Side Panel on icon click
chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error) => console.error(error));

chrome.runtime.onInstalled.addListener(() => {
    console.log('Brain Vault Extension installed');
});

// Listen for messages from popup or content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'generatePrompt') {
        handleRequest(generatePrompt, request.data, sendResponse);
        return true;
    }
    if (request.action === 'saveMemory') {
        handleRequest(saveMemory, request.data, sendResponse);
        return true;
    }
    if (request.action === 'saveLLMMemory') {
        handleRequest(saveLLMMemory, request.data, sendResponse);
        return true;
    }
    if (request.action === 'searchMemory') {
        handleRequest(searchMemory, request.data, sendResponse);
        return true;
    }
    if (request.action === 'getDocuments') {
        handleRequest(getDocuments, request.data, sendResponse);
        return true;
    }
    if (request.action === 'getMemories') {
        handleRequest(getMemories, request.data, sendResponse);
        return true;
    }
});

async function handleRequest(handler, data, sendResponse) {
    try {
        const result = await handler(data);
        sendResponse({ success: true, data: result });
    } catch (error) {
        sendResponse({ success: false, error: error.message });
    }
}

async function getAuthHeaders() {
    const { token } = await chrome.storage.local.get('token');
    if (!token) {
        throw new Error('Not authenticated. Please login via the popup.');
    }
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

async function generatePrompt(data) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/prompts/generate`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            query: data.query,
            template_id: data.templateId || 'standard',
            context_size: 2000
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate prompt');
    }

    return await response.json();
}

async function saveMemory(data) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/memory/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            title: data.title,
            content: data.content,
            tags: ['extension']
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save memory');
    }

    return await response.json();
}

async function searchMemory(data) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/documents/search`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            query: data.query,
            top_k: 5
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to search memory');
    }

    return await response.json();
}

async function getDocuments() {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/documents/`, {
        method: 'GET',
        headers
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch documents');
    }

    return await response.json();
}

async function getMemories() {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/memory/`, {
        method: 'GET',
        headers
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch memories');
    }

    return await response.json();
}

async function saveLLMMemory(data) {
    const headers = await getAuthHeaders();
    // Using llm/save_memory endpoint which is designed for external inputs
    const response = await fetch(`${API_BASE_URL}/llm/save_memory`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            content: data.content,
            source_llm: data.source || 'extension_content_script',
            model_name: data.model || 'unknown',
            tags: ['extension', data.source],
            url: data.url
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save LLM memory');
    }

    return await response.json();
}
