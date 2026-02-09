// Claude Adapter for Memwyre Extension
// Handles all Claude-specific DOM selectors and injection logic

import {
    createSaveButton,
    createInjectButton,
    queryWithFallback,
    queryAllWithFallback
} from './base.js';

/**
 * Claude adapter configuration
 * Selectors are ordered by priority - first match wins
 */
const config = {
    name: 'claude',

    // Hostname matching
    match: (host) => host.includes('claude'),

    // DOM selectors with fallbacks (priority order)
    selectors: {
        // Assistant message containers
        assistantMessage: [
            '.font-claude-message',
            '[data-testid="assistant-message"]',
            '.assistant-message',
            '[class*="claude-message"]'
        ],

        // Toolbar where save button is injected
        messageToolbar: [
            '.flex.items-center.gap-1',
            '[class*="message-toolbar"]',
            '.flex.gap-1'
        ],

        // Input area selectors
        inputArea: [
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="Message"]',
            '.ProseMirror'
        ],

        // Input container for positioning
        inputContainer: [
            '[class*="input-container"]',
            '.flex.flex-col.gap-2',
            'form'
        ]
    }
};

/**
 * Injects save buttons on assistant messages
 * Non-blocking - uses requestAnimationFrame for DOM mutations
 */
export async function injectSaveButtons() {
    const messages = queryAllWithFallback(config.selectors.assistantMessage);

    for (const msg of messages) {
        // Find toolbar - check parent and sibling elements
        let toolbar = null;

        // Try parent's toolbar first
        const parent = msg.parentElement;
        if (parent) {
            toolbar = queryWithFallback(config.selectors.messageToolbar.map(s =>
                parent.matches(s) ? s : null
            ).filter(Boolean));

            if (!toolbar) {
                toolbar = parent.querySelector(config.selectors.messageToolbar[0]);
            }
        }

        // Try sibling/adjacent toolbar
        if (!toolbar && parent?.parentElement) {
            for (const selector of config.selectors.messageToolbar) {
                toolbar = parent.parentElement.querySelector(selector);
                if (toolbar) break;
            }
        }

        // Also check for button parent
        if (!toolbar) {
            const buttonParent = msg.parentElement?.parentElement?.querySelector('div.flex button')?.parentElement;
            if (buttonParent) toolbar = buttonParent;
        }

        if (!toolbar || toolbar.querySelector('.brain-vault-save-btn')) continue;

        const btn = createSaveButton(() => msg.innerText, config.name);

        // Non-blocking DOM append
        requestAnimationFrame(() => {
            toolbar.appendChild(btn);
        });
    }
}

/**
 * Injects context button near input area
 * Non-blocking - uses requestAnimationFrame for DOM mutations
 */
export async function injectContextButton() {
    const inputArea = queryWithFallback(config.selectors.inputArea);
    if (!inputArea) return;

    const parent = inputArea.parentElement;
    if (!parent || parent.querySelector('.brain-vault-inject-btn')) return;

    if (getComputedStyle(parent).position === 'static') {
        parent.style.position = 'relative';
    }

    const getInputArea = () => queryWithFallback(config.selectors.inputArea);
    const btn = createInjectButton(getInputArea);

    // Claude-specific positioning
    btn.style.position = 'absolute';
    btn.style.right = '60px';
    btn.style.bottom = '8px';
    btn.style.opacity = '0.9';

    // Non-blocking DOM append
    requestAnimationFrame(() => {
        parent.appendChild(btn);
    });
}

export default {
    ...config,
    injectSaveButtons,
    injectContextButton
};
