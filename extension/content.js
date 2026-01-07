// Content script for Memwyre Extension

console.log('Memwyre Extension loaded');

// Listen for messages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'injectPrompt') {
        injectText(request.text);
        sendResponse({ success: true });
    }
});

function injectText(text) {
    const activeElement = document.activeElement;
    if (activeElement && (activeElement.tagName === 'TEXTAREA' || activeElement.getAttribute('contenteditable') === 'true')) {
        if (activeElement.tagName === 'TEXTAREA') {
            activeElement.value += text;
            activeElement.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            activeElement.textContent += text;
            activeElement.dispatchEvent(new Event('input', { bubbles: true }));
        }
    } else {
        navigator.clipboard.writeText(text).then(() => {
            alert('Memwyre: Prompt copied to clipboard (could not find input box).');
        });
    }
}

function getSource() {
    const host = window.location.hostname;
    if (host.includes('chatgpt')) return 'chatgpt';
    if (host.includes('claude')) return 'claude';
    if (host.includes('gemini') || host.includes('google')) return 'gemini';
    return 'unknown';
}

// --- UI Helper Functions ---

function showFloatingFeedback(btn, message, type = 'info') {
    // Remove existing tooltips for this button
    const existing = document.getElementById('memwyre-tooltip-' + btn.dataset.mwId);
    if (existing) existing.remove();

    if (!btn.dataset.mwId) btn.dataset.mwId = Math.random().toString(36).substr(2, 9);

    const tooltip = document.createElement('div');
    tooltip.id = 'memwyre-tooltip-' + btn.dataset.mwId;
    tooltip.textContent = message;

    // Colors based on type
    let bg = 'rgba(0, 0, 0, 0.8)';
    let color = '#fff';
    if (type === 'error') bg = 'rgba(220, 53, 69, 0.9)';
    if (type === 'success') bg = 'rgba(25, 135, 84, 0.9)';

    tooltip.style.cssText = `
        position: absolute;
        background: ${bg};
        color: ${color};
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        pointer-events: none;
        z-index: 10001;
        opacity: 0;
        transition: opacity 0.2s ease, transform 0.2s ease;
        white-space: nowrap;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    `;

    document.body.appendChild(tooltip);

    // Position relative to button
    const rect = btn.getBoundingClientRect();
    const scrollX = window.scrollX;
    const scrollY = window.scrollY;

    // Default to displaying above
    let top = rect.top + scrollY - 30;
    let left = rect.left + scrollX + (rect.width / 2) - (tooltip.offsetWidth / 2); // Center X

    // Safety check for screen edges implies separate calculation after append to get width, 
    // but initially just centered. Better to set left/top after append.
    // Re-calculate after append
    const tipWidth = tooltip.offsetWidth;
    left = rect.left + scrollX + (rect.width / 2) - (tipWidth / 2);

    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;

    // Animate in
    requestAnimationFrame(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(-5px)';
    });

    // Remove after delay
    setTimeout(() => {
        tooltip.style.opacity = '0';
        tooltip.style.transform = 'translateY(0)';
        setTimeout(() => tooltip.remove(), 200);
    }, 3000);
}

// --- Button Creation Helpers ---

function createSaveButton(textContent, source) {
    const btn = document.createElement('button');
    btn.className = 'brain-vault-save-btn'; // Keep class for consistency or change if CSS not reliant
    const logoUrl = chrome.runtime.getURL('logo.png');
    btn.innerHTML = `<img src="${logoUrl}" style="width: 16px; height: 16px; display: block; opacity: 0.9;">`;
    btn.title = 'Save to Memwyre';
    btn.style.cssText = `
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background-color: transparent;
            color: #333;
            border: none; 
            border-radius: 6px;
            cursor: pointer;
            opacity: 0.9;
            transition: all 0.2s ease;
            margin-right: 4px; 
        `;

    // Hover effects
    btn.onmouseover = () => {
        btn.style.opacity = '1';
        btn.style.backgroundColor = 'rgba(128,128,128,0.15)';
        btn.querySelector('img').style.opacity = '1';
    };
    btn.onmouseout = () => {
        btn.style.opacity = '0.9';
        btn.style.backgroundColor = 'transparent';
        btn.querySelector('img').style.opacity = '0.9';
    };

    btn.onclick = async () => {
        // High visibility spinner (Blue/White contrast)
        btn.innerHTML = '<div style="width: 14px; height: 14px; border: 2px solid rgba(100,100,100,0.3); border-top: 2px solid #007bff; border-radius: 50%; animation: spin 1s linear infinite;"></div>';

        try {
            const response = await chrome.runtime.sendMessage({
                action: 'saveLLMMemory',
                data: {
                    content: textContent,
                    source: source,
                    model: 'unknown',
                    url: window.location.href
                }
            });

            if (response.success) {
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px;"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                showFloatingFeedback(btn, 'Saved to Memwyre!', 'success');
                setTimeout(() => {
                    btn.innerHTML = `<img src="${logoUrl}" style="width: 16px; height: 16px; display: block; opacity: 0.9;">`;
                }, 2000);
            } else {
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
                showFloatingFeedback(btn, response.error || 'Failed to save', 'error');
                setTimeout(() => { btn.innerHTML = `<img src="${logoUrl}" style="width: 16px; height: 16px; display: block; opacity: 0.9;">`; }, 3000);
            }
        } catch (err) {
            console.error(err);
            btn.innerHTML = '❌';
            showFloatingFeedback(btn, 'Error: ' + err.message, 'error');
        }
    };

    return btn;
}

function createBaseInjectButton() {
    const btn = document.createElement('button');
    btn.className = 'brain-vault-inject-btn';
    const logoUrl = chrome.runtime.getURL('logo.png');
    btn.innerHTML = `<img src="${logoUrl}" style="width: 20px; height: 20px; display: block;">`;
    btn.title = 'Insert Context from Memwyre';

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
        z-index: 1000;
        transition: all 0.2s ease;
        opacity: 0.9;
    `;

    btn.onmouseover = () => {
        btn.style.backgroundColor = 'rgba(128,128,128,0.1)';
        btn.style.transform = 'scale(1.05)';
        btn.style.opacity = '1';
    };
    btn.onmouseout = () => {
        btn.style.backgroundColor = 'transparent';
        btn.style.transform = 'scale(1)';
        btn.style.opacity = '0.9';
    };

    btn.onclick = async () => {
        const logoUrl = chrome.runtime.getURL('logo.png');
        // High visibility spinner
        btn.innerHTML = '<div style="width: 16px; height: 16px; border: 2px solid rgba(100,100,100,0.3); border-top: 2px solid #007bff; border-radius: 50%; animation: spin 1s linear infinite;"></div>';

        try {
            const inputArea = document.querySelector('textarea') || document.querySelector('div[contenteditable="true"]');
            let query = '';
            // Safe query extraction
            if (inputArea) {
                if (inputArea.tagName === 'TEXTAREA') {
                    query = inputArea.value;
                } else {
                    query = inputArea.innerText;
                }
            }

            if (!query || query.trim().length < 2) {
                showFloatingFeedback(btn, 'Please type a query first', 'error');
                btn.innerHTML = `<img src="${logoUrl}" style="width: 20px; height: 20px; display: block;">`;
                return;
            }

            const response = await chrome.runtime.sendMessage({
                action: 'searchMemory',
                data: { query: query }
            });

            if (response && response.success && response.data && response.data.length > 0) {
                const contextText = response.data.map(item => {
                    const date = item.metadata && item.metadata.created_at ? new Date(item.metadata.created_at).toLocaleDateString() : 'Unknown Date';
                    const source = item.metadata && item.metadata.source ? item.metadata.source : 'Memwyre';
                    return `[Source: ${source} | Date: ${date}]\n${item.text}`;
                }).join('\n\n---\n\n');

                const fullInjection = `\n\n[SYSTEM: The following context is retrieved from the user's Memwyre. Use it to answer the request if relevant.]\n\n${contextText}\n\n[END CONTEXT]\n\n`;

                if (inputArea.tagName === 'TEXTAREA') {
                    const start = inputArea.selectionStart || inputArea.value.length;
                    const end = inputArea.selectionEnd || inputArea.value.length;
                    const text = inputArea.value;
                    inputArea.value = text.substring(0, start) + fullInjection + text.substring(end);
                    inputArea.dispatchEvent(new Event('input', { bubbles: true }));
                } else if (inputArea) {
                    inputArea.textContent += fullInjection;
                    inputArea.dispatchEvent(new Event('input', { bubbles: true }));
                }

                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px;"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                showFloatingFeedback(btn, 'Context Injected!', 'success');
                setTimeout(() => {
                    btn.innerHTML = `<img src="${logoUrl}" style="width: 20px; height: 20px; display: block;">`;
                }, 2000);

            } else {
                btn.innerHTML = '⚠️';
                showFloatingFeedback(btn, 'No relevant memories found', 'info');
                setTimeout(() => {
                    btn.innerHTML = `<img src="${logoUrl}" style="width: 20px; height: 20px; display: block;">`;
                }, 2000);

                const errorMsg = response && response.error ? response.error : 'No relevant memories found.';
                console.log(errorMsg);
                if (errorMsg.includes('Not authenticated')) {
                    showFloatingFeedback(btn, 'Please Login to Memwyre', 'error');
                }
            }

        } catch (err) {
            console.error('Injection error:', err);
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
            showFloatingFeedback(btn, 'Error: ' + err.message, 'error');
            setTimeout(() => {
                btn.innerHTML = `<img src="${logoUrl}" style="width: 20px; height: 20px; display: block;">`;
            }, 2000);
        }
    };

    return btn;
}

// --- Main Injection Logic ---

function injectSaveButtons() {
    const source = getSource();
    if (source === 'unknown') return;

    if (source === 'chatgpt') {
        const msgs = document.querySelectorAll('div[data-message-author-role="assistant"]');
        msgs.forEach(msg => {
            const row = msg.closest('div.group\\/conversation-turn') || msg.parentElement.parentElement;
            if (!row) return;

            const actionBars = row.querySelectorAll('.flex.flex-wrap.items-center.gap-y-4');
            actionBars.forEach(bar => {
                if (!bar.querySelector('.brain-vault-save-btn')) {
                    const btn = createSaveButton(msg.innerText, source);
                    bar.appendChild(btn);
                }
            });
        });
        return;
    } else if (source === 'claude') {
        const msgs = document.querySelectorAll('.font-claude-message');
        msgs.forEach(msg => {
            const toolbar = msg.parentElement.querySelector('.flex.items-center.gap-1') || msg.parentElement.parentElement.querySelector('div.flex button')?.parentElement;
            if (toolbar && !toolbar.querySelector('.brain-vault-save-btn')) {
                const btn = createSaveButton(msg.innerText, source);
                toolbar.appendChild(btn);
            }
        });
        return;
    } else if (source === 'gemini') {
        const toolbars = document.querySelectorAll('.buttons-container-v2');
        toolbars.forEach(toolbar => {
            if (toolbar.querySelector('.brain-vault-save-btn')) return;

            const container = toolbar.closest('model-turn-component') || toolbar.closest('.conversation-container');
            if (!container) return;

            const textElement = container.querySelector('.model-response-text');
            if (textElement) {
                const btn = createSaveButton(textElement.innerText, source);
                const spacer = toolbar.querySelector('.spacer');
                if (spacer) {
                    toolbar.insertBefore(btn, spacer);
                } else {
                    toolbar.appendChild(btn);
                }
            }
        });
        return;
    }
}

function injectContextButton() {
    const source = getSource();
    if (source === 'unknown') return;

    if (source === 'chatgpt') {
        const actionContainer = document.querySelector('div[class*="[grid-area:trailing]"]');

        if (actionContainer) {
            if (actionContainer.querySelector('.brain-vault-inject-btn')) return;

            const btn = createBaseInjectButton();
            // Style for Flexbox context (ChatGPT)
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

            actionContainer.prepend(btn);
            return;
        }
    }

    if (source === 'gemini') {
        const actionContainer = document.querySelector('.model-picker-container') || document.querySelector('.input-buttons-wrapper-bottom');

        if (actionContainer) {
            if (actionContainer.querySelector('.brain-vault-inject-btn')) return;

            const btn = createBaseInjectButton();
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
                margin-right: 8px; /* Spacing from model select */
            `;
            btn.onmouseover = () => {
                btn.style.backgroundColor = 'rgba(128,128,128,0.1)';
                btn.style.opacity = '1';
            };
            btn.onmouseout = () => {
                btn.style.backgroundColor = 'transparent';
                btn.style.opacity = '0.9';
            };

            actionContainer.prepend(btn);
            return;
        }
    }

    // --- Fallback ---
    const inputArea = document.querySelector('textarea') || document.querySelector('div[contenteditable="true"]');
    if (!inputArea) return;

    const parent = inputArea.parentElement;
    if (parent.querySelector('.brain-vault-inject-btn')) return;

    if (getComputedStyle(parent).position === 'static') parent.style.position = 'relative';

    let rightOffset = '50px';
    let bottomOffset = '8px';

    if (source === 'chatgpt') {
        rightOffset = '60px';
        bottomOffset = '10px';
    } else if (source === 'gemini') {
        rightOffset = '90px';
        bottomOffset = '12px';
    } else if (source === 'claude') {
        rightOffset = '60px';
    }

    const btn = createBaseInjectButton();
    btn.style.position = 'absolute';
    btn.style.right = rightOffset;
    btn.style.bottom = bottomOffset;
    btn.style.opacity = '0.9';

    parent.appendChild(btn);
}

// Global Spinner Style
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
`;
document.head.appendChild(spinnerStyle);

// --- Observer ---

const observer = new MutationObserver((mutations) => {
    injectSaveButtons();
    injectContextButton();
});

observer.observe(document.body, { childList: true, subtree: true });

// Initial run
setTimeout(() => {
    injectSaveButtons();
    injectContextButton();
}, 2000);
