/**
 * i18n Loader for Bonzi Community Bot
 *
 * Loads translations from JSON files and applies them to [data-i18n] elements.
 * Works with subdirectory pages (manual/, economics/, dao/) via basePath detection.
 *
 * Usage:
 *   1. Include this script in your HTML: <script src="js/i18n-loader.js"></script>
 *      (or "../js/i18n-loader.js" for subdirectory pages)
 *   2. Add data-i18n="key" attributes to translatable elements
 *   3. Add a language selector with id="lang-select"
 *
 * The loader:
 *   - Reads language preference from localStorage('bonzi_lang')
 *   - Falls back to English if translation key is missing
 *   - Caches loaded translations for performance
 */

(function() {
    'use strict';

    // Detect base path for i18n files based on current page location
    function getBasePath() {
        const path = window.location.pathname;
        // Count directory depth from root
        const segments = path.split('/').filter(s => s && !s.endsWith('.html'));
        if (segments.length === 0) {
            return './';
        }
        // For subdirectories like /manual/, /economics/, /dao/, /metrics/
        return '../'.repeat(segments.length);
    }

    const basePath = getBasePath();
    const i18nPath = basePath + 'i18n/';

    // Cache for loaded translations
    const translationCache = {};

    // Load translations for a language
    async function loadTranslations(lang) {
        // Return cached version if available
        if (translationCache[lang]) {
            return translationCache[lang];
        }

        try {
            const response = await fetch(i18nPath + lang + '.json');
            if (!response.ok) {
                console.warn('[i18n] Translation file not found for:', lang);
                return null;
            }
            const translations = await response.json();
            translationCache[lang] = translations;
            return translations;
        } catch (error) {
            console.warn('[i18n] Error loading translations for:', lang, error);
            return null;
        }
    }

    // Apply translations to all [data-i18n] elements
    async function applyTranslations(lang) {
        // Always load English as fallback
        const enTranslations = await loadTranslations('en');
        const translations = lang === 'en' ? enTranslations : await loadTranslations(lang);

        // Use requested language translations with English fallback
        const t = translations || enTranslations;
        const fallback = enTranslations || {};

        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t && t[key]) {
                el.textContent = t[key];
            } else if (fallback[key]) {
                // Fallback to English if key missing in requested language
                el.textContent = fallback[key];
            }
        });

        // Save language preference
        localStorage.setItem('bonzi_lang', lang);
    }

    // Initialize i18n
    let _initRan = false;
    async function init() {
        // Get saved language or default to English
        const savedLang = localStorage.getItem('bonzi_lang') || 'en';

        // Apply translations on every init pass (covers nav-injected i18n strings
        // that were not in DOM during the first pass).
        if (savedLang !== 'en') {
            await applyTranslations(savedLang);
        }

        // Set up language selector if it exists - bind once even if init runs twice.
        const langSelect = document.getElementById('lang-select');
        if (langSelect && !langSelect.dataset.i18nBound) {
            langSelect.value = savedLang;
            langSelect.addEventListener('change', (e) => {
                applyTranslations(e.target.value);
            });
            langSelect.dataset.i18nBound = '1';
        }

        _initRan = true;
    }

    // Export for manual use if needed
    window.bonziI18n = {
        applyTranslations,
        loadTranslations,
        getBasePath,
        init
    };

    // Initialize when DOM is ready (catches static [data-i18n] elements)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Re-initialize after nav-loader injects the nav (catches the lang-select
    // and any [data-i18n] strings inside the injected nav/mobile-menu).
    document.addEventListener('nav:loaded', init);
})();
