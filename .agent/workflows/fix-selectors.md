---
description: Fix broken selectors when LLM websites update their DOM
---

# Selector Fix Workflow

When ChatGPT, Claude, Gemini, or YouTube updates their DOM and breaks the extension buttons, follow this workflow.

## Step 1: Detection

Run the health check:
```bash
python backend/scripts/dom_health_check.py
```

Output shows what's broken:
```
🔍 Checking ChatGPT...
  ❌ inputActions: BROKEN
```

---

## Step 2: Investigate

1. Open the affected site (e.g., chatgpt.com) in Chrome
2. Press **F12** → DevTools
3. Use **Element Inspector** (Ctrl+Shift+C) to click on the target element
4. Right-click the element → **Copy → Copy selector**

**Target elements to look for:**
| Selector Name | What to Find |
|---------------|--------------|
| `assistantMessage` | The AI's response container |
| `messageToolbar` | Buttons row below AI response (copy, like, etc.) |
| `inputArea` | The text input box where you type prompts |
| `inputActions` | Buttons near the input (send, attach, etc.) |

---

## Step 3: Fix in content.js

Open `extension/content.js` and find the `ADAPTERS` object:

```javascript
const ADAPTERS = {
    chatgpt: {
        selectors: {
            inputActions: [
                'div[class*="new-selector-here"]',  // ← Add new selector at TOP
                'div[class*="[grid-area:trailing]"]',  // ← Old ones become fallbacks
                '.flex.items-center.gap-2'
            ]
        }
    }
}
```

> **Important:** Add new selector at the TOP of the array (highest priority). Keep old ones as fallbacks.

---

## Step 4: Verify

// turbo
1. Reload extension in Chrome:
   - Go to `chrome://extensions`
   - Find Memwyre → Click refresh icon

2. Visit the site and check buttons appear

// turbo
3. Re-run health check:
```bash
python backend/scripts/dom_health_check.py --site chatgpt
```

---

## Step 5: Update Health Check Config

Keep `dom_health_check.py` in sync by updating `SITE_CONFIGS`:

```python
SITE_CONFIGS = {
    "chatgpt": {
        "selectors": {
            "inputActions": [
                'div[class*="new-selector-here"]',  # ← Same as content.js
                ...
            ]
        }
    }
}
```

---

## Quick Reference

| Site | Fix Location |
|------|--------------|
| ChatGPT | `ADAPTERS.chatgpt.selectors` |
| Claude | `ADAPTERS.claude.selectors` |
| Gemini | `ADAPTERS.gemini.selectors` |
| YouTube | `ADAPTERS.youtube.selectors` |

**Files to update:**
- `extension/content.js` → ADAPTERS object
- `backend/scripts/dom_health_check.py` → SITE_CONFIGS (for future checks)
