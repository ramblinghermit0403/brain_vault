// Adapter Registry for Memwyre Extension
// Loads and manages site-specific adapters

import chatgptAdapter from './chatgpt.js';
import claudeAdapter from './claude.js';
import geminiAdapter from './gemini.js';
import youtubeAdapter from './youtube.js';
import perplexityAdapter from './perplexity.js';

/**
 * All registered adapters
 */
const adapters = [
    chatgptAdapter,
    claudeAdapter,
    geminiAdapter,
    youtubeAdapter,
    perplexityAdapter
];

/**
 * Gets the appropriate adapter for the current hostname
 * @param {string} hostname - The window.location.hostname
 * @returns {Object|null} - The matching adapter or null
 */
export function getAdapter(hostname) {
    for (const adapter of adapters) {
        if (adapter.match(hostname)) {
            return adapter;
        }
    }
    return null;
}

/**
 * Gets adapter by name
 * @param {string} name - Adapter name (e.g., 'chatgpt', 'claude')
 * @returns {Object|null}
 */
export function getAdapterByName(name) {
    return adapters.find(a => a.name === name) || null;
}

/**
 * Lists all registered adapter names
 * @returns {string[]}
 */
export function listAdapterNames() {
    return adapters.map(a => a.name);
}

/**
 * Gets all adapters (for health checks)
 * @returns {Object[]}
 */
export function getAllAdapters() {
    return adapters;
}

export default {
    getAdapter,
    getAdapterByName,
    listAdapterNames,
    getAllAdapters
};
