---
description: Run DOM health check to validate extension selectors on LLM sites
---

# DOM Health Check Workflow

This workflow validates that the Memwyre extension's DOM selectors are still working on ChatGPT, Claude, Gemini, and YouTube.

## Prerequisites

1. Ensure Playwright is installed:
```bash
pip install playwright
playwright install chromium
```

## Running the Health Check

// turbo
1. Navigate to the backend scripts directory:
```bash
cd backend/scripts
```

// turbo
2. Run the health check on all sites:
```bash
python dom_health_check.py
```

3. Or check a specific site:
```bash
python dom_health_check.py --site chatgpt
python dom_health_check.py --site claude
python dom_health_check.py --site gemini
python dom_health_check.py --site youtube
```

4. Save report to file:
```bash
python dom_health_check.py -o health_report.md
```

## Understanding the Output

- ✅ **OK**: Primary selector works
- ⚠️ **FALLBACK**: Primary failed, but a fallback selector works
- ❌ **BROKEN**: All selectors failed - needs fixing
- 🚫 **ERROR**: Site couldn't be loaded

## Fixing Broken Selectors

1. Open the affected site in Chrome DevTools (F12)
2. Inspect the target element (e.g., assistant message, input area)
3. Copy the new selector
4. Update `extension/content.js` → find the `ADAPTERS` object → update the relevant site's selectors array
5. Re-run health check to verify

## Scheduling (Recommended)

Run this check every 2-3 days to catch breaking changes early:

**Windows Task Scheduler:**
```
schtasks /create /tn "Memwyre DOM Check" /tr "python C:\path\to\dom_health_check.py" /sc daily /st 09:00
```

**Linux/Mac cron:**
```
0 9 */2 * * python /path/to/dom_health_check.py
```
