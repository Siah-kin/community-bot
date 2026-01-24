/**
 * Bonzi Brand Widget - Embed Script
 *
 * DOCUMENTATION: https://github.com/Siah-kin/community-bot/blob/main/widget/README.md
 * FULL MANUAL:   https://bonzi.bot/docs/brand-starter-kit
 *
 * Quick Start:
 * <script src="https://bonzi.bot/widget/embed.js" data-token="0x..." data-symbol="$TOKEN"></script>
 *
 * With container:
 * <div id="bonzi-buy-widget"></div>
 * <script src="https://bonzi.bot/widget/embed.js" data-token="0x..." data-container="bonzi-buy-widget"></script>
 *
 * Options: data-mode="inline|modal|floating", data-theme="light|dark", data-testnet="true"
 */
(function() {
    'use strict';

    // Widget host URL (change in production)
    const WIDGET_HOST = window.BONZI_WIDGET_HOST || 'https://bonzi.bot/widget';

    // Get the current script element to read data attributes
    const currentScript = document.currentScript || (function() {
        const scripts = document.getElementsByTagName('script');
        return scripts[scripts.length - 1];
    })();

    // Configuration from data attributes
    const config = {
        token: currentScript.dataset.token || null,
        symbol: currentScript.dataset.symbol || '$TOKEN',
        testnet: currentScript.dataset.testnet === 'true',
        container: currentScript.dataset.container || null,
        width: currentScript.dataset.width || '400px',
        height: currentScript.dataset.height || '600px',
        theme: currentScript.dataset.theme || 'light', // 'light' or 'dark'
        position: currentScript.dataset.position || 'inline', // 'inline', 'modal', or 'floating'
        buttonText: currentScript.dataset.buttonText || 'Buy ' + (currentScript.dataset.symbol || '$TOKEN'),
        buttonColor: currentScript.dataset.buttonColor || '#7B2D8E'
    };

    // Styles for different display modes
    const styles = `
        .bonzi-widget-container {
            width: ${config.width};
            max-width: 100%;
        }

        .bonzi-widget-iframe {
            width: 100%;
            height: ${config.height};
            border: none;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
        }

        .bonzi-widget-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px 28px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: white;
            background: ${config.buttonColor};
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .bonzi-widget-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(123, 45, 142, 0.3);
        }

        .bonzi-widget-button svg {
            width: 20px;
            height: 20px;
        }

        /* Modal styles */
        .bonzi-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999999;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }

        .bonzi-modal-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .bonzi-modal-content {
            position: relative;
            transform: scale(0.95);
            transition: transform 0.3s;
        }

        .bonzi-modal-overlay.active .bonzi-modal-content {
            transform: scale(1);
        }

        .bonzi-modal-close {
            position: absolute;
            top: -40px;
            right: 0;
            width: 32px;
            height: 32px;
            background: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .bonzi-modal-close:hover {
            background: #f5f5f5;
        }

        /* Floating button styles */
        .bonzi-floating-button {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999998;
        }

        @media (max-width: 480px) {
            .bonzi-widget-container {
                width: 100%;
            }

            .bonzi-widget-iframe {
                border-radius: 0;
                height: 100vh;
            }

            .bonzi-modal-content {
                width: 100%;
                height: 100%;
            }

            .bonzi-modal-close {
                top: 16px;
                right: 16px;
            }
        }
    `;

    // Inject styles
    function injectStyles() {
        const styleEl = document.createElement('style');
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);
    }

    // Build widget URL
    function buildWidgetUrl() {
        const url = new URL(WIDGET_HOST + '/brand-widget.html');
        if (config.token) url.searchParams.set('token', config.token);
        if (config.symbol) url.searchParams.set('symbol', config.symbol);
        if (config.testnet) url.searchParams.set('testnet', 'true');
        if (config.theme === 'dark') url.searchParams.set('theme', 'dark');
        return url.toString();
    }

    // Create iframe
    function createIframe() {
        const iframe = document.createElement('iframe');
        iframe.className = 'bonzi-widget-iframe';
        iframe.src = buildWidgetUrl();
        iframe.allow = 'payment *; clipboard-write *';
        iframe.setAttribute('loading', 'lazy');
        return iframe;
    }

    // Create buy button
    function createButton(onClick) {
        const button = document.createElement('button');
        button.className = 'bonzi-widget-button';
        button.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="9" cy="21" r="1"/>
                <circle cx="20" cy="21" r="1"/>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
            </svg>
            ${config.buttonText}
        `;
        button.addEventListener('click', onClick);
        return button;
    }

    // Create modal
    function createModal() {
        const overlay = document.createElement('div');
        overlay.className = 'bonzi-modal-overlay';

        const content = document.createElement('div');
        content.className = 'bonzi-modal-content bonzi-widget-container';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'bonzi-modal-close';
        closeBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
        `;
        closeBtn.addEventListener('click', () => overlay.classList.remove('active'));

        const iframe = createIframe();

        content.appendChild(closeBtn);
        content.appendChild(iframe);
        overlay.appendChild(content);

        // Close on background click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.classList.remove('active');
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') overlay.classList.remove('active');
        });

        return overlay;
    }

    // Initialize widget based on position mode
    function init() {
        injectStyles();

        if (config.position === 'modal') {
            // Modal mode: show button, open modal on click
            const modal = createModal();
            document.body.appendChild(modal);

            const button = createButton(() => modal.classList.add('active'));

            if (config.container) {
                document.getElementById(config.container).appendChild(button);
            } else {
                // Insert button after script tag
                currentScript.parentNode.insertBefore(button, currentScript.nextSibling);
            }

        } else if (config.position === 'floating') {
            // Floating button mode: fixed button in corner
            const modal = createModal();
            document.body.appendChild(modal);

            const floatingContainer = document.createElement('div');
            floatingContainer.className = 'bonzi-floating-button';

            const button = createButton(() => modal.classList.add('active'));
            floatingContainer.appendChild(button);

            document.body.appendChild(floatingContainer);

        } else {
            // Inline mode: embed directly
            const container = document.createElement('div');
            container.className = 'bonzi-widget-container';
            container.appendChild(createIframe());

            if (config.container) {
                document.getElementById(config.container).appendChild(container);
            } else {
                currentScript.parentNode.insertBefore(container, currentScript.nextSibling);
            }
        }
    }

    // Public API
    window.BonziWidget = {
        open: function() {
            const modal = document.querySelector('.bonzi-modal-overlay');
            if (modal) modal.classList.add('active');
        },
        close: function() {
            const modal = document.querySelector('.bonzi-modal-overlay');
            if (modal) modal.classList.remove('active');
        },
        configure: function(newConfig) {
            Object.assign(config, newConfig);
        }
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
