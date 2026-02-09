// Perplexity Adapter for Memwyre Extension
// Handles all Perplexity-specific DOM selectors and injection logic

import {
    createSaveButton,
    createInjectButton,
    queryWithFallback,
    queryAllWithFallback
} from './base.js';

/**
 * Perplexity adapter configuration
 * Selectors are ordered by priority - first match wins
 */
const config = {
    name: 'perplexity',

    // Hostname matching
    match: (host) => host.includes('perplexity'),

    // DOM selectors with fallbacks (priority order)
    selectors: {
        // Input area - contenteditable div
        inputArea: [
            '#ask-input',
            'div[contenteditable="true"][role="textbox"]',
            'div[data-lexical-editor="true"]'
        ],

        // Container for inject button - left of model selector
        inputActionsRight: [
            '.flex.items-center.justify-self-end.col-start-3',
            'div.col-start-3.row-start-2',
            '.grid-rows-1fr-auto .col-start-3'
        ],

        // Model selector button to insert before
        modelSelector: [
            'button[aria-label="Choose a model"]',
            'button:has-text("Model")',
            'span:has-text("Model")'
        ],

        // Response action toolbar (left division with Share, Download, Copy, Rewrite)
        responseToolbarLeft: [
            '.flex.items-center.justify-between > div:first-child',
            '.-ml-sm.gap-xs.flex.flex-shrink-0.items-center',
            '.flex.items-center.justify-between .flex-shrink-0:first-child'
        ],

        // Rewrite button to insert after
        rewriteButton: [
            'button[aria-label="Rewrite"]',
            'button:has(svg use[xlink\\:href="#pplx-icon-repeat"])'
        ],

        // Response text content
        responseContent: [
            '.prose',
            '.markdown-content',
            '[class*="answer-content"]',
            '.whitespace-pre-wrap'
        ]
    }
};

/**
 * Injects save buttons on Perplexity responses
 * Non-blocking - uses requestAnimationFrame for DOM mutations
 */
export async function injectSaveButtons() {
    const toolbars = queryAllWithFallback(config.selectors.responseToolbarLeft);

    for (const toolbar of toolbars) {
        if (toolbar.querySelector('.brain-vault-save-btn')) continue;

        // Find the parent response container to get the text
        const responseContainer = toolbar.closest('[class*="answer"]') ||
            toolbar.closest('.prose')?.parentElement ||
            toolbar.parentElement?.parentElement;

        const textElement = responseContainer?.querySelector('.prose') ||
            responseContainer?.querySelector('.whitespace-pre-wrap');

        const btn = createSaveButton(
            () => textElement?.innerText || 'Perplexity Response',
            config.name
        );

        // Match Perplexity's button style
        btn.style.cssText = `
            display: inline-flex; align-items: center; justify-content: center;
            width: 32px; height: 32px; border-radius: 9999px;
            background-color: transparent; border: none; cursor: pointer;
            opacity: 0.7; transition: all 0.3s ease;
        `;
        btn.onmouseover = () => {
            btn.style.backgroundColor = 'rgba(128,128,128,0.1)';
            btn.style.opacity = '1';
        };
        btn.onmouseout = () => {
            btn.style.backgroundColor = 'transparent';
            btn.style.opacity = '0.7';
        };

        // Insert after the Rewrite button (rightmost in left division)
        const rewriteBtn = toolbar.querySelector(config.selectors.rewriteButton[0]);
        requestAnimationFrame(() => {
            if (rewriteBtn) {
                rewriteBtn.after(btn);
            } else {
                toolbar.appendChild(btn);
            }
        });
    }
}

/**
 * Injects context button near input area (left of model selector)
 * Non-blocking - uses requestAnimationFrame for DOM mutations
 */
export async function injectContextButton() {
    const actionContainer = queryWithFallback(config.selectors.inputActionsRight);
    if (!actionContainer || actionContainer.querySelector('.brain-vault-inject-btn')) return;

    const getInputArea = () => queryWithFallback(config.selectors.inputArea);
    const btn = createInjectButton(getInputArea);

    // Match Perplexity's button style
    btn.style.cssText = `
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 9999px;
        background-color: transparent; border: none; cursor: pointer;
        opacity: 0.7; transition: all 0.3s ease; margin-right: 4px;
    `;
    btn.onmouseover = () => {
        btn.style.backgroundColor = 'rgba(128,128,128,0.1)';
        btn.style.opacity = '1';
    };
    btn.onmouseout = () => {
        btn.style.backgroundColor = 'transparent';
        btn.style.opacity = '0.7';
    };

    // Insert before the model selector button
    const modelBtn = actionContainer.querySelector(config.selectors.modelSelector[0]);
    requestAnimationFrame(() => {
        if (modelBtn) {
            modelBtn.parentElement.insertBefore(btn, modelBtn.parentElement.firstChild);
        } else {
            actionContainer.prepend(btn);
        }
    });
}

export default {
    ...config,
    injectSaveButtons,
    injectContextButton
};
