// Gemini Adapter for Memwyre Extension
// Handles all Gemini-specific DOM selectors and injection logic

import {
    createSaveButton,
    createInjectButton,
    queryWithFallback,
    queryAllWithFallback
} from './base.js';

/**
 * Gemini adapter configuration
 * Selectors are ordered by priority - first match wins
 */
const config = {
    name: 'gemini',

    // Hostname matching
    match: (host) => host.includes('gemini') || host.includes('google'),

    // DOM selectors with fallbacks (priority order)
    selectors: {
        // Model response text containers
        modelResponseText: [
            '.model-response-text',
            '[class*="response-text"]',
            '.markdown-content',
            'model-response'
        ],

        // Toolbar where save button is injected
        buttonsContainer: [
            '.buttons-container-v2',
            '.buttons-container',
            '[class*="action-buttons"]',
            '.response-actions'
        ],

        // Model turn wrapper
        modelTurn: [
            'model-turn-component',
            '[class*="model-turn"]',
            '.conversation-container'
        ],

        // Spacer element for button positioning
        spacer: [
            '.spacer',
            '[class*="spacer"]'
        ],

        // Input area selectors
        inputArea: [
            'rich-textarea textarea',
            'textarea[aria-label*="prompt"]',
            'div[contenteditable="true"]',
            '.ql-editor'
        ],

        // Input action area
        inputActions: [
            '.model-picker-container',
            '.input-buttons-wrapper-bottom',
            '[class*="input-actions"]'
        ]
    }
};

/**
 * Injects save buttons on model responses
 * Non-blocking - uses requestAnimationFrame for DOM mutations
 */
export async function injectSaveButtons() {
    const toolbars = queryAllWithFallback(config.selectors.buttonsContainer);

    for (const toolbar of toolbars) {
        if (toolbar.querySelector('.brain-vault-save-btn')) continue;

        // Find the model turn container
        let container = null;
        for (const selector of config.selectors.modelTurn) {
            container = toolbar.closest(selector);
            if (container) break;
        }
        if (!container) continue;

        // Find the response text element
        const textElement = queryWithFallback(
            config.selectors.modelResponseText.map(s => container.querySelector(s)).filter(Boolean)
        ) || container.querySelector(config.selectors.modelResponseText[0]);

        if (!textElement) continue;

        const btn = createSaveButton(() => textElement.innerText, config.name);

        // Find spacer for insertion point
        const spacer = toolbar.querySelector(config.selectors.spacer[0]);

        // Non-blocking DOM insert
        requestAnimationFrame(() => {
            if (spacer) {
                toolbar.insertBefore(btn, spacer);
            } else {
                toolbar.appendChild(btn);
            }
        });
    }
}

/**
 * Injects context button near input area
 * Non-blocking - uses requestAnimationFrame for DOM mutations
 */
export async function injectContextButton() {
    const actionContainer = queryWithFallback(config.selectors.inputActions);

    if (!actionContainer) return;
    if (actionContainer.querySelector('.brain-vault-inject-btn')) return;

    const getInputArea = () => queryWithFallback(config.selectors.inputArea);
    const btn = createInjectButton(getInputArea);

    // Gemini-specific styling
    btn.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: transparent;
        border: none;
        cursor: pointer;
        opacity: 0.9;
        transition: all 0.2s ease;
        margin-right: 8px;
    `;

    btn.onmouseover = () => {
        btn.style.backgroundColor = 'rgba(128,128,128,0.1)';
        btn.style.opacity = '1';
    };
    btn.onmouseout = () => {
        btn.style.backgroundColor = 'transparent';
        btn.style.opacity = '0.9';
    };

    // Non-blocking DOM prepend
    requestAnimationFrame(() => {
        actionContainer.prepend(btn);
    });
}

export default {
    ...config,
    injectSaveButtons,
    injectContextButton
};
