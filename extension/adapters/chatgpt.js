// ChatGPT Adapter for Memwyre Extension
// Handles all ChatGPT-specific DOM selectors and injection logic

import {
    createSaveButton,
    createInjectButton,
    queryWithFallback,
    queryAllWithFallback,
    createLogoImage
} from './base.js';

/**
 * ChatGPT adapter configuration
 * Selectors are ordered by priority - first match wins
 */
const config = {
    name: 'chatgpt',

    // Hostname matching
    match: (host) => host.includes('chatgpt'),

    // DOM selectors with fallbacks (priority order)
    selectors: {
        // Assistant message containers
        assistantMessage: [
            'div[data-message-author-role="assistant"]',
            'article[data-role="assistant"]',
            '[data-testid*="conversation-turn-assistant"]',
            '.agent-turn .markdown'
        ],

        // Toolbar where save button is injected
        messageToolbar: [
            '.flex.flex-wrap.items-center.gap-y-4',
            '[class*="message-actions"]',
            '.flex.items-center.gap-1'
        ],

        // Conversation turn wrapper
        conversationTurn: [
            'div.group\\/conversation-turn',
            '[data-testid*="conversation-turn"]',
            'article[data-scroll-anchor]'
        ],

        // Input area selectors
        inputArea: [
            '#prompt-textarea',
            'textarea[data-id="root"]',
            'div[contenteditable="true"][role="textbox"]',
            'textarea[placeholder*="Message"]'
        ],

        // Input action buttons container
        inputActions: [
            'div[class*="[grid-area:trailing]"]',
            '.flex.items-center.gap-2',
            '[class*="input-actions"]'
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
        // Find the conversation turn wrapper
        let row = null;
        for (const selector of config.selectors.conversationTurn) {
            row = msg.closest(selector);
            if (row) break;
        }
        if (!row) row = msg.parentElement?.parentElement;
        if (!row) continue;

        // Find toolbars within this row
        const toolbars = queryAllWithFallback(config.selectors.messageToolbar)
            .filter(bar => row.contains(bar));

        for (const bar of toolbars) {
            if (bar.querySelector('.brain-vault-save-btn')) continue;

            const btn = createSaveButton(() => msg.innerText, config.name);

            // Non-blocking DOM append
            requestAnimationFrame(() => {
                bar.appendChild(btn);
            });
        }
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

    // ChatGPT-specific styling
    btn.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: transparent;
        border: none;
        cursor: pointer;
        opacity: 0.9;
        transition: all 0.2s ease;
        margin-right: 4px;
        color: currentColor;
    `;

    btn.onmouseover = () => {
        btn.style.backgroundColor = 'rgba(128,128,128,0.15)';
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
