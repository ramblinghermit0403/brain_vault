// Content script for Brain Vault Extension

console.log('Brain Vault Extension loaded');

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
            alert('Brain Vault: Prompt copied to clipboard (could not find input box).');
        });
    }
}

// Universal Capture: Button Injection
// Selectors for different LLMs
const SELECTORS = {
    chatgpt: {
        message: 'div[data-message-author-role="assistant"]', // Generic, might need adjustment
        container: '.markdown' // Often the content wrapper
    },
    claude: {
        message: '.font-claude-message',
        container: '.font-claude-message'
    },
    gemini: {
        message: 'model-response', // Tag name often? Or class?
        container: '.model-response-text'
    }
};

function getSource() {
    const host = window.location.hostname;
    if (host.includes('chatgpt')) return 'chatgpt';
    if (host.includes('claude')) return 'claude';
    if (host.includes('gemini') || host.includes('google')) return 'gemini';
    return 'unknown';
}

function injectSaveButtons() {
    const source = getSource();
    if (source === 'unknown') return;

    // Simplified selector strategy: Look for paragraph blocks or message containers
    // This is fragile and requires maintenance.
    // For MVP, we'll try to find message containers and append a small button.

    let messages = [];
    if (source === 'chatgpt') {
        messages = document.querySelectorAll('div[data-message-author-role="assistant"]');
    } else if (source === 'claude') {
        messages = document.querySelectorAll('.font-claude-message');
    } else if (source === 'gemini') {
        messages = document.querySelectorAll('.model-response-text'); // Approximation
    }

    messages.forEach(msg => {
        // Check if already injected
        if (msg.querySelector('.brain-vault-save-btn')) return;

        const btn = document.createElement('button');
        btn.className = 'brain-vault-save-btn';
        btn.innerHTML = '💾 Save to Vault';
        btn.style.cssText = `
            font-size: 12px;
            padding: 4px 8px;
            margin-top: 8px;
            background-color: #4f46e5;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s;
            display: block;
        `;
        btn.onmouseover = () => btn.style.opacity = '1';
        btn.onmouseout = () => btn.style.opacity = '0.7';

        btn.onclick = async () => {
            btn.innerHTML = 'Saving...';
            const content = msg.innerText; // Get text content

            try {
                const response = await chrome.runtime.sendMessage({
                    action: 'saveLLMMemory',
                    data: {
                        content: content,
                        source: source,
                        model: 'unknown',
                        url: window.location.href
                    }
                });

                if (response.success) {
                    btn.innerHTML = '✅ Saved';
                    btn.style.backgroundColor = '#10b981';
                } else {
                    btn.innerHTML = '❌ Error';
                    alert(response.error);
                }
            } catch (err) {
                console.error(err);
                btn.innerHTML = '❌ Error';
            }
        };

        msg.appendChild(btn);
    });
}

// Observe DOM changes to inject buttons as new messages arrive
const observer = new MutationObserver((mutations) => {
    injectSaveButtons();
});

observer.observe(document.body, { childList: true, subtree: true });

// Initial run
setTimeout(injectSaveButtons, 2000);
