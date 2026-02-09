"""
DOM Health Check Script for Memwyre Extension

This script validates that the extension's DOM selectors still work on target sites.
Run every second day (or on-demand) to detect breaking changes before users report them.

Usage:
    python dom_health_check.py
    python dom_health_check.py --site chatgpt
    python dom_health_check.py --fix  # Suggest fixes for broken selectors

Requirements:
    pip install playwright
    playwright install chromium
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


# ============================================================================
# SELECTOR CONFIGURATIONS - Mirror of extension adapters
# ============================================================================

SITE_CONFIGS = {
    "chatgpt": {
        "name": "ChatGPT",
        "url": "https://chatgpt.com/",
        "selectors": {
            "assistantMessage": [
                'div[data-message-author-role="assistant"]',
                'article[data-role="assistant"]',
                '[data-testid*="conversation-turn-assistant"]'
            ],
            "messageToolbar": [
                '.flex.flex-wrap.items-center.gap-y-4',
                '[class*="message-actions"]'
            ],
            "inputArea": [
                '#prompt-textarea',
                'textarea[data-id="root"]',
                'div[contenteditable="true"][role="textbox"]'
            ],
            "inputActions": [
                'div[class*="[grid-area:trailing]"]',
                '.flex.items-center.gap-2'
            ]
        },
        "critical_selectors": ["inputArea", "inputActions"]
    },
    
    "claude": {
        "name": "Claude",
        "url": "https://claude.ai/",
        "selectors": {
            "assistantMessage": [
                '.font-claude-message',
                '[data-testid="assistant-message"]',
                '[class*="claude-message"]'
            ],
            "messageToolbar": [
                '.flex.items-center.gap-1',
                '[class*="message-toolbar"]'
            ],
            "inputArea": [
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]',
                '.ProseMirror'
            ]
        },
        "critical_selectors": ["inputArea"]
    },
    
    "gemini": {
        "name": "Gemini",
        "url": "https://gemini.google.com/",
        "selectors": {
            "modelResponseText": [
                '.model-response-text',
                '[class*="response-text"]',
                '.markdown-content'
            ],
            "buttonsContainer": [
                '.buttons-container-v2',
                '.buttons-container',
                '[class*="action-buttons"]'
            ],
            "inputArea": [
                'rich-textarea textarea',
                'textarea[aria-label*="prompt"]',
                'div[contenteditable="true"]'
            ],
            "inputActions": [
                '.model-picker-container',
                '.input-buttons-wrapper-bottom'
            ]
        },
        "critical_selectors": ["inputArea"]
    },
    
    "youtube": {
        "name": "YouTube",
        "url": "https://www.youtube.com/",
        "selectors": {
            "videoMenu": [
                '#menu > ytd-menu-renderer',
                '#menu-container ytd-menu-renderer'
            ],
            "videoTitle": [
                '#title > h1 > yt-formatted-string',
                'h1.ytd-video-primary-info-renderer'
            ]
        },
        "critical_selectors": ["videoMenu"]
    },
    
    "perplexity": {
        "name": "Perplexity",
        "url": "https://www.perplexity.ai/",
        "selectors": {
            "inputArea": [
                '#ask-input',
                'div[contenteditable="true"][role="textbox"]',
                'div[data-lexical-editor="true"]'
            ],
            "inputActionsRight": [
                '.flex.items-center.justify-self-end.col-start-3',
                'div.col-start-3.row-start-2'
            ],
            "modelSelector": [
                'button[aria-label="Choose a model"]'
            ],
            "responseToolbarLeft": [
                '.flex.items-center.justify-between > div:first-child',
                '.-ml-sm.gap-xs.flex.flex-shrink-0.items-center'
            ],
            "rewriteButton": [
                'button[aria-label="Rewrite"]'
            ]
        },
        "critical_selectors": ["inputArea", "inputActionsRight"]
    }
}


# ============================================================================
# HEALTH CHECK ENGINE
# ============================================================================

class HealthCheckResult:
    def __init__(self, site: str, selector_name: str, selectors: list[str]):
        self.site = site
        self.selector_name = selector_name
        self.selectors = selectors
        self.working_selector: Optional[str] = None
        self.all_failed = True
        self.error: Optional[str] = None
    
    @property
    def status(self) -> str:
        if self.error:
            return "ERROR"
        if self.all_failed:
            return "BROKEN"
        if self.working_selector == self.selectors[0]:
            return "OK"
        return "FALLBACK"
    
    def to_dict(self) -> dict:
        return {
            "site": self.site,
            "selector_name": self.selector_name,
            "status": self.status,
            "working_selector": self.working_selector,
            "primary_selector": self.selectors[0] if self.selectors else None,
            "error": self.error
        }


async def check_selector(page: Page, selectors: list[str]) -> Optional[str]:
    """Try each selector and return the first one that finds an element."""
    for selector in selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                return selector
        except Exception:
            continue
    return None


async def check_site(browser: Browser, site_key: str, config: dict) -> list[HealthCheckResult]:
    """Check all selectors for a single site."""
    results = []
    
    print(f"\n🔍 Checking {config['name']}...")
    
    try:
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate with timeout
        await page.goto(config["url"], wait_until="domcontentloaded", timeout=30000)
        
        # Wait for dynamic content to load
        await asyncio.sleep(3)
        
        # Check each selector group
        for selector_name, selectors in config["selectors"].items():
            result = HealthCheckResult(site_key, selector_name, selectors)
            
            working = await check_selector(page, selectors)
            if working:
                result.working_selector = working
                result.all_failed = False
            
            results.append(result)
            
            # Print inline status
            status_icon = "✅" if result.status == "OK" else "⚠️" if result.status == "FALLBACK" else "❌"
            print(f"  {status_icon} {selector_name}: {result.status}")
        
        await context.close()
        
    except Exception as e:
        # If site fails entirely, mark all selectors as error
        for selector_name, selectors in config["selectors"].items():
            result = HealthCheckResult(site_key, selector_name, selectors)
            result.error = str(e)
            results.append(result)
        print(f"  ❌ Site error: {e}")
    
    return results


async def run_health_check(site_filter: Optional[str] = None) -> dict:
    """Run health checks on all or specified sites."""
    all_results = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for site_key, config in SITE_CONFIGS.items():
            if site_filter and site_key != site_filter:
                continue
            
            results = await check_site(browser, site_key, config)
            all_results[site_key] = [r.to_dict() for r in results]
        
        await browser.close()
    
    return all_results


# ============================================================================
# FIX SUGGESTIONS
# ============================================================================

HEURISTIC_SELECTORS = {
    # Common patterns that might work as fallbacks
    "inputArea": [
        'textarea',
        'div[contenteditable="true"]',
        '[role="textbox"]',
        '.ql-editor',
        '.ProseMirror'
    ],
    "assistantMessage": [
        '[data-role="assistant"]',
        '[class*="assistant"]',
        '[class*="response"]',
        '.markdown',
        'article'
    ],
    "messageToolbar": [
        '.flex.items-center',
        '[class*="actions"]',
        '[class*="toolbar"]',
        'button:has-text("Copy")'
    ]
}


async def suggest_fixes(page: Page, broken_result: HealthCheckResult) -> list[str]:
    """Suggest alternative selectors for broken ones."""
    suggestions = []
    
    # Try heuristic selectors
    heuristics = HEURISTIC_SELECTORS.get(broken_result.selector_name, [])
    for selector in heuristics:
        try:
            element = await page.query_selector(selector)
            if element:
                suggestions.append(selector)
        except Exception:
            continue
    
    return suggestions[:3]  # Return top 3 suggestions


# ============================================================================
# REPORTING
# ============================================================================

def generate_report(results: dict) -> str:
    """Generate a markdown report of health check results."""
    lines = [
        "# Memwyre Extension DOM Health Check Report",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Summary",
        ""
    ]
    
    # Count statuses
    total_ok = 0
    total_fallback = 0
    total_broken = 0
    total_error = 0
    
    for site_key, site_results in results.items():
        for result in site_results:
            status = result["status"]
            if status == "OK":
                total_ok += 1
            elif status == "FALLBACK":
                total_fallback += 1
            elif status == "BROKEN":
                total_broken += 1
            else:
                total_error += 1
    
    lines.append(f"- ✅ OK: {total_ok}")
    lines.append(f"- ⚠️ Using Fallback: {total_fallback}")
    lines.append(f"- ❌ Broken: {total_broken}")
    lines.append(f"- 🚫 Errors: {total_error}")
    lines.append("")
    
    # Detailed results per site
    lines.append("## Detailed Results")
    lines.append("")
    
    for site_key, site_results in results.items():
        config = SITE_CONFIGS.get(site_key, {})
        lines.append(f"### {config.get('name', site_key)}")
        lines.append("")
        lines.append("| Selector | Status | Working | Primary |")
        lines.append("|----------|--------|---------|---------|")
        
        for result in site_results:
            status_icon = {
                "OK": "✅",
                "FALLBACK": "⚠️",
                "BROKEN": "❌",
                "ERROR": "🚫"
            }.get(result["status"], "?")
            
            working = result["working_selector"] or "N/A"
            primary = result["primary_selector"] or "N/A"
            
            # Truncate long selectors
            if len(working) > 40:
                working = working[:37] + "..."
            if len(primary) > 40:
                primary = primary[:37] + "..."
            
            lines.append(f"| {result['selector_name']} | {status_icon} {result['status']} | `{working}` | `{primary}` |")
        
        lines.append("")
    
    # Action items
    broken_items = []
    for site_key, site_results in results.items():
        for result in site_results:
            if result["status"] in ("BROKEN", "ERROR"):
                broken_items.append(f"- **{site_key}.{result['selector_name']}**: {result.get('error') or 'No element found'}")
    
    if broken_items:
        lines.append("## ⚠️ Action Required")
        lines.append("")
        lines.append("The following selectors need to be fixed:")
        lines.append("")
        lines.extend(broken_items)
        lines.append("")
        lines.append("**Next steps:**")
        lines.append("1. Visit the affected site in DevTools")
        lines.append("2. Inspect the target element's current structure")
        lines.append("3. Update the selector in `extension/content.js` under the ADAPTERS object")
        lines.append("4. Re-run this health check to verify")
    
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="DOM Health Check for Memwyre Extension")
    parser.add_argument("--site", choices=list(SITE_CONFIGS.keys()), help="Check only this site")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of report")
    parser.add_argument("--output", "-o", type=Path, help="Save report to file")
    
    args = parser.parse_args()
    
    print("🚀 Memwyre DOM Health Check")
    print("=" * 40)
    
    results = await run_health_check(args.site)
    
    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = generate_report(results)
    
    print("\n" + "=" * 40)
    
    if args.output:
        args.output.write_text(output)
        print(f"📄 Report saved to: {args.output}")
    else:
        print(output)
    
    # Exit with error code if any selectors are broken
    has_broken = any(
        r["status"] in ("BROKEN", "ERROR")
        for site_results in results.values()
        for r in site_results
    )
    
    sys.exit(1 if has_broken else 0)


if __name__ == "__main__":
    asyncio.run(main())
