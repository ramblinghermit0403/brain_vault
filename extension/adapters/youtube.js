// YouTube Adapter for Memwyre Extension
// Handles all YouTube-specific DOM selectors and injection logic

import {
    createSaveButton,
    createLogoImage,
    queryWithFallback,
    queryAllWithFallback
} from './base.js';

/**
 * YouTube adapter configuration
 * Selectors are ordered by priority - first match wins
 */
const config = {
    name: 'youtube',

    // Hostname matching
    match: (host) => host.includes('youtube'),

    // DOM selectors with fallbacks (priority order)
    selectors: {
        // Video menu for regular videos
        videoMenu: [
            '#menu > ytd-menu-renderer',
            '#menu-container ytd-menu-renderer',
            '#top-level-buttons-computed'
        ],

        // Video title
        videoTitle: [
            '#title > h1 > yt-formatted-string',
            'h1.ytd-video-primary-info-renderer',
            '#title h1'
        ],

        // Shorts action container
        shortsActions: [
            'ytd-reel-player-overlay-renderer #actions',
            '#actions.ytd-reel-player-overlay-renderer',
            '.reel-player-overlay-actions'
        ],

        // Shorts video wrapper
        shortsVideo: [
            'ytd-reel-video-renderer',
            '[class*="reel-video"]'
        ],

        // Shorts title
        shortsTitle: [
            '#overlay .metadata h2',
            '.yt-reel-metadatam-renderer h2',
            '.reel-title'
        ]
    }
};

/**
 * Creates a styled save button for YouTube videos
 */
function createVideoSaveButton(titleGetter) {
    const btn = createSaveButton(titleGetter, config.name);

    // YouTube video-specific styles
    btn.style.width = '36px';
    btn.style.height = '36px';
    btn.style.marginLeft = '8px';

    return btn;
}

/**
 * Creates a styled save button for YouTube Shorts
 */
function createShortsSaveButton(titleGetter) {
    const btn = createSaveButton(titleGetter, config.name);

    // Shorts glassy button style
    btn.style.width = '48px';
    btn.style.height = '48px';
    btn.style.marginBottom = '16px';
    btn.style.marginTop = '0px';
    btn.style.borderRadius = '50%';
    btn.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
    btn.style.backdropFilter = 'blur(4px)';
    btn.style.color = 'white';
    btn.style.border = 'none';
    btn.style.zIndex = '9999';
    btn.style.pointerEvents = 'auto';

    // Larger icon for Shorts
    const img = btn.querySelector('img');
    if (img) {
        img.style.width = '24px';
        img.style.height = '24px';
        img.style.filter = 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))';
    }

    return btn;
}

/**
 * Injects save buttons on YouTube videos and Shorts
 * Non-blocking - uses requestAnimationFrame for DOM mutations
 */
export async function injectSaveButtons() {
    // 1. Regular YouTube Videos
    const videoMenu = queryWithFallback(config.selectors.videoMenu);

    if (videoMenu && !videoMenu.querySelector('.brain-vault-save-btn')) {
        const titleElement = queryWithFallback(config.selectors.videoTitle);
        const title = titleElement ? titleElement.innerText : 'YouTube Video';

        const btn = createVideoSaveButton(() => title);

        requestAnimationFrame(() => {
            videoMenu.prepend(btn);
        });
    }

    // 2. YouTube Shorts
    const shortsOverlays = queryAllWithFallback(config.selectors.shortsActions);

    for (const actionContainer of shortsOverlays) {
        // Check if visible and not already injected
        if (actionContainer.offsetParent === null) continue;
        if (actionContainer.querySelector('.brain-vault-save-btn')) continue;

        // Find title
        let title = 'YouTube Short';
        const activeShort = actionContainer.closest(config.selectors.shortsVideo[0]);

        if (activeShort) {
            const titleEl = queryWithFallback(
                config.selectors.shortsTitle.map(s => activeShort.querySelector(s)).filter(Boolean)
            );
            if (titleEl) title = titleEl.innerText.trim();
        }

        const btn = createShortsSaveButton(() => title);

        requestAnimationFrame(() => {
            actionContainer.prepend(btn);
        });
    }
}

/**
 * YouTube doesn't need context injection
 */
export async function injectContextButton() {
    // No-op for YouTube
    return;
}

export default {
    ...config,
    injectSaveButtons,
    injectContextButton
};
