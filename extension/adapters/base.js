// Base adapter utilities - shared across all site adapters
// All functions are async-first and non-blocking

/**
 * Shows a floating tooltip near a button
 * @param {HTMLElement} btn - The button element
 * @param {string} message - Message to display
 * @param {'info'|'error'|'success'} type - Tooltip type
 */
export function showFloatingFeedback(btn, message, type = 'info') {
    const existing = document.getElementById('memwyre-tooltip-' + btn.dataset.mwId);
    if (existing) existing.remove();

    if (!btn.dataset.mwId) btn.dataset.mwId = Math.random().toString(36).substr(2, 9);

    const tooltip = document.createElement('div');
    tooltip.id = 'memwyre-tooltip-' + btn.dataset.mwId;
    tooltip.textContent = message;

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

    const rect = btn.getBoundingClientRect();
    const scrollX = window.scrollX;
    const scrollY = window.scrollY;
    const tipWidth = tooltip.offsetWidth;
    const top = rect.top + scrollY - 30;
    const left = rect.left + scrollX + (rect.width / 2) - (tipWidth / 2);

    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;

    requestAnimationFrame(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(-5px)';
    });

    setTimeout(() => {
        tooltip.style.opacity = '0';
        tooltip.style.transform = 'translateY(0)';
        setTimeout(() => tooltip.remove(), 200);
    }, 3000);
}

/**
 * Creates a spinner element for loading states
 * @returns {HTMLElement}
 */
export function createSpinner() {
    const spinner = document.createElement('div');
    spinner.style.cssText = `
        width: 14px;
        height: 14px;
        border: 2px solid rgba(100,100,100,0.3);
        border-top: 2px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    `;
    return spinner;
}

/**
 * Creates a checkmark SVG for success states
 * @returns {SVGElement}
 */
export function createCheckmark() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "#666666");
    svg.setAttribute("stroke-width", "3");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.style.width = "20px";
    svg.style.height = "20px";
    const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    polyline.setAttribute("points", "20 6 9 17 4 12");
    svg.appendChild(polyline);
    return svg;
}

/**
 * Creates an X SVG for error states
 * @returns {SVGElement}
 */
export function createErrorIcon() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "#666666");
    svg.setAttribute("stroke-width", "3");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.style.width = "20px";
    svg.style.height = "20px";
    const line1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line1.setAttribute("x1", "18"); line1.setAttribute("y1", "6");
    line1.setAttribute("x2", "6"); line1.setAttribute("y2", "18");
    const line2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line2.setAttribute("x1", "6"); line2.setAttribute("y1", "6");
    line2.setAttribute("x2", "18"); line2.setAttribute("y2", "18");
    svg.appendChild(line1);
    svg.appendChild(line2);
    return svg;
}

/**
 * Gets the extension logo URL
 * @returns {string}
 */
export function getLogoUrl() {
    return chrome.runtime.getURL('logo.png');
}

/**
 * Creates the Memwyre logo image element
 * @param {Object} options - Styling options
 * @returns {HTMLImageElement}
 */
export function createLogoImage(options = {}) {
    const { width = '16px', height = '16px', opacity = '0.9', filter = '' } = options;
    const img = document.createElement('img');
    img.src = getLogoUrl();
    img.style.width = width;
    img.style.height = height;
    img.style.display = 'block';
    img.style.opacity = opacity;
    if (filter) img.style.filter = filter;
    return img;
}

/**
 * Tries multiple selectors and returns the first match
 * @param {string[]} selectors - Array of CSS selectors to try
 * @returns {Element|null}
 */
export function queryWithFallback(selectors) {
    for (const selector of selectors) {
        try {
            const element = document.querySelector(selector);
            if (element) return element;
        } catch (e) {
            console.warn(`Memwyre: Invalid selector "${selector}"`, e);
        }
    }
    return null;
}

/**
 * Tries multiple selectors and returns all matches
 * @param {string[]} selectors - Array of CSS selectors to try
 * @returns {Element[]}
 */
export function queryAllWithFallback(selectors) {
    for (const selector of selectors) {
        try {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) return Array.from(elements);
        } catch (e) {
            console.warn(`Memwyre: Invalid selector "${selector}"`, e);
        }
    }
    return [];
}

/**
 * Creates a save button with async click handler
 * @param {Function} contentGetter - Async function to get content
 * @param {string} source - Platform source identifier
 * @returns {HTMLButtonElement}
 */
export function createSaveButton(contentGetter, source) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'brain-vault-save-btn';

    const img = createLogoImage({ width: '16px', height: '16px' });
    btn.appendChild(img);

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

    btn.onmouseover = () => {
        btn.style.opacity = '1';
        btn.style.backgroundColor = 'rgba(128,128,128,0.15)';
        const btnImg = btn.querySelector('img');
        if (btnImg) btnImg.style.opacity = '1';
    };
    btn.onmouseout = () => {
        btn.style.opacity = '0.9';
        btn.style.backgroundColor = 'transparent';
        const btnImg = btn.querySelector('img');
        if (btnImg) btnImg.style.opacity = '0.9';
    };

    btn.onclick = async (e) => {
        e.stopPropagation();

        const originalIcon = btn.querySelector('img')?.cloneNode(true);

        // Loading state
        btn.replaceChildren(createSpinner());
        btn.disabled = true;
        btn.style.cursor = 'default';

        try {
            let response;
            if (source === 'youtube') {
                response = await chrome.runtime.sendMessage({
                    action: 'ingestYouTube',
                    data: { url: window.location.href }
                });
            } else {
                const content = typeof contentGetter === 'function'
                    ? await Promise.resolve(contentGetter())
                    : contentGetter;

                response = await chrome.runtime.sendMessage({
                    action: 'saveLLMMemory',
                    data: {
                        content,
                        source,
                        model: 'unknown',
                        url: window.location.href
                    }
                });
            }

            if (response.success) {
                btn.replaceChildren(createCheckmark());
                showFloatingFeedback(btn, 'Saved to Memwyre!', 'success');

                setTimeout(() => {
                    if (!btn.isConnected) return;
                    if (originalIcon) {
                        btn.replaceChildren(originalIcon);
                    } else {
                        btn.replaceChildren(createLogoImage({ width: '16px', height: '16px' }));
                    }
                    btn.disabled = false;
                    btn.style.cursor = 'pointer';
                }, 2000);
            } else {
                throw new Error(response.error || 'Failed to save');
            }
        } catch (err) {
            console.error('Memwyre save error:', err);
            btn.replaceChildren(createErrorIcon());
            showFloatingFeedback(btn, 'Error: ' + err.message, 'error');

            setTimeout(() => {
                if (!btn.isConnected) return;
                btn.replaceChildren(createLogoImage({ width: '16px', height: '16px' }));
                btn.disabled = false;
                btn.style.cursor = 'pointer';
            }, 3000);
        }
    };

    return btn;
}

/**
 * Creates the inject context button with async click handler
 * @param {Function} getInputArea - Function to get the input element
 * @returns {HTMLButtonElement}
 */
export function createInjectButton(getInputArea) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'brain-vault-inject-btn';

    const img = createLogoImage({ width: '20px', height: '20px' });
    btn.appendChild(img);

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
        btn.replaceChildren(createSpinner());

        try {
            const inputArea = typeof getInputArea === 'function' ? getInputArea() : getInputArea;

            let query = '';
            if (inputArea) {
                query = inputArea.tagName === 'TEXTAREA' ? inputArea.value : inputArea.innerText;
            }

            if (!query || query.trim().length < 2) {
                showFloatingFeedback(btn, 'Please type a query first', 'error');
                btn.replaceChildren(createLogoImage({ width: '20px', height: '20px' }));
                return;
            }

            const response = await chrome.runtime.sendMessage({
                action: 'searchMemory',
                data: { query }
            });

            if (response?.success && response.data?.length > 0) {
                const jsonContent = JSON.stringify(response.data, null, 2);
                const systemPrompt = buildSystemPrompt();
                const fullInjection = `\n\n${systemPrompt}\n\n${jsonContent}\n\n[END CONTEXT]\n\n`;

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

                btn.replaceChildren(createCheckmark());
                showFloatingFeedback(btn, 'Context Injected!', 'success');
            } else {
                btn.textContent = '⚠️';
                showFloatingFeedback(btn, 'No relevant memories found', 'info');

                if (response?.error?.includes('Not authenticated')) {
                    showFloatingFeedback(btn, 'Please Login to Memwyre', 'error');
                }
            }

            setTimeout(() => {
                btn.replaceChildren(createLogoImage({ width: '20px', height: '20px' }));
            }, 2000);

        } catch (err) {
            console.error('Memwyre injection error:', err);
            btn.replaceChildren(createErrorIcon());
            showFloatingFeedback(btn, 'Error: ' + err.message, 'error');

            setTimeout(() => {
                btn.replaceChildren(createLogoImage({ width: '20px', height: '20px' }));
            }, 2000);
        }
    };

    return btn;
}

/**
 * Builds the system prompt for context injection
 * @returns {string}
 */
function buildSystemPrompt() {
    return `[SYSTEM: The following context is retrieved from the user's Brain Vault. Use it to answer the request if relevant.

**Understanding the Context:**
The context contains search results from a memory system. Each result has multiple components you can use:

1. **Snippet Result**: The text content found in relevant documents or memories.
2. **Dates & Timing**:
   - **Event Date**: This is the **PRE-RESOLVED Absolute Date** of the event (derived from 'valid_from').
     * **Start Date Rule**: If the text suggests a duration (e.g. "last week", "camping trip", "picnic week"), treat this date as the **START** of that period.
     * **Timezone Tolerance**: Stored dates are in UTC. If your calculated answer seems off by 1 day (e.g. June 1st vs June 2nd), acknowledge that the event likely occurred **around** this date or **starting** this week.
     * **Trust the System**: Do NOT try to re-calculate "last week" from the current date. The system has done it for you and put it here.
   - **Valid Until**: The **End Date** of the event.
   - **Range**: If 'Valid Until' is present, the event covers the [Event Date, Valid Until] range. Use this range in your answer.

**How to Answer:**
1. **Analyze Temporal Context**:
   - Does the text refer to a "Day" (e.g. "On Friday") or a "Period" (e.g. "last week")?
2. **Formulate Date**:
   - **For Periods**: Answer with "The week of [Event Date]" or "Starting [Event Date]". Avoid asserting strictly "On [Event Date]" if the event is a week long.
   - **For Specific Days**: Use the Event Date.
3. **Address Mismatches**:
   - If the Question expects a range ("When did she...") and facts are broad, use a Range.
   - **Missing by a Day**: If the date falls on a boundary (e.g. 1st vs 30th), be inclusive.

Instructions:
- First, think through the problem step by step. Show your reasoning process.
- **Explicitly cite the dates** found.
- **Prioritize Ranges/Periods** over single dates for broad events.
- Base your answer ONLY on the provided context.

**Response Format:**
Think step by step, then provide your answer.]`;
}
