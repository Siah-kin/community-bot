(() => {
    // Gate check: redirect to slot machine if no access token
    // Skip for dev.html (dev bypass) and index.html (is the gate)
    const _page = location.pathname.split('/').pop() || 'index.html';
    // Public surfaces: no alpha gate (privacy must stay readable from bot/Telegram without slot session).
    const _publicPages = new Set(['index.html', 'dev.html', '404.html', 'privacy.html', 'about.html', 'about', 'stake.html', 'stake-tg.html', 'stake']);
    if (!_publicPages.has(_page)) {
        if (sessionStorage.getItem('bonzi_alpha') !== '1') {
            location.href = location.pathname.substring(0, location.pathname.lastIndexOf('/') + 1) || '/';
            return;
        }
    }

    const THEME_KEY = 'bonzi_theme';
    const LEGACY_THEME_KEY = 'bonzi-theme';

    const navReady = loadNav();
    window.navReady = navReady;

    async function loadNav() {
        const navContainer = document.getElementById('nav-container');
        const menuContainer = document.getElementById('mobile-menu-container');
        if (!navContainer || !menuContainer) return;

        const prefix = getPathPrefix();

        try {
            const _v = '20260602c';
        const [navRes, menuRes] = await Promise.all([
                fetch(prefix + 'includes/nav.html?v=' + _v),
                fetch(prefix + 'includes/mobile-menu.html?v=' + _v)
            ]);

            navContainer.innerHTML = await navRes.text();
            menuContainer.innerHTML = await menuRes.text();

            if (prefix) {
                prefixRelativeUrls(navContainer, prefix);
                prefixRelativeUrls(menuContainer, prefix);
            }

            applyActiveState();
            initTheme();
            initDevMode();
            initNavInteractions();
            initMobileMenu();
            initLanguageSelect();
            initContactLinks();
            initDemoButton();
            // initBrazilButton(); // disabled 2026-05-29: operator request, language switching now uses nav lang-select uniformly

            document.dispatchEvent(new CustomEvent('nav:loaded'));
        } catch (err) {
            console.error('[nav-loader] Failed to load navigation:', err);
        }
    }

    function getPathPrefix() {
        const path = window.location.pathname;
        const subdirs = ['/manual/', '/manual', '/economics/', '/economics', '/research/', '/research', '/vetter/', '/vetter', '/dao/', '/dao', '/metrics/', '/metrics', '/alpha/', '/alpha', '/demo_silverfox/', '/demo_silverfox'];
        const isSubdir = subdirs.some((dir) => path.includes(dir));
        return isSubdir ? '../' : '';
    }

    function prefixRelativeUrls(container, prefix) {
        container.querySelectorAll('[href]').forEach((el) => {
            const href = el.getAttribute('href');
            if (!shouldPrefixUrl(href)) return;
            el.setAttribute('href', prefix + href);
        });

        container.querySelectorAll('img[src]').forEach((img) => {
            const src = img.getAttribute('src');
            if (!shouldPrefixUrl(src)) return;
            img.setAttribute('src', prefix + src);
        });
    }

    function shouldPrefixUrl(value) {
        if (!value) return false;
        if (value.startsWith('#')) return false;
        if (value.startsWith('http://') || value.startsWith('https://')) return false;
        if (value.startsWith('mailto:') || value.startsWith('tel:')) return false;
        if (value.startsWith('/')) return false;
        return true;
    }

    function applyActiveState() {
        const activeKey = getActiveKey(window.location.pathname);
        if (!activeKey) return;
        document.querySelectorAll(`[data-nav="${activeKey}"]`).forEach((el) => {
            el.classList.add('active');
        });
    }

    function getActiveKey(pathname) {
        const cleanPath = pathname.split('?')[0].split('#')[0];

        if (cleanPath.includes('/manual')) return 'manual';
        if (cleanPath.includes('/economics')) return 'economics';
        if (cleanPath.includes('/research')) return 'research';
        if (cleanPath.includes('/whitepaper')) return 'whitepaper';
        if (cleanPath.includes('/vetter')) return 'vetter';
        if (cleanPath.includes('/dao')) return 'dao';
        if (cleanPath.includes('/metrics')) return 'metrics';

        const file = cleanPath.split('/').filter(Boolean).pop();
        if (!file || file === 'index.html') return 'home';
        if (file === 'features.html') return 'features';
        if (file === 'stake.html') return 'stake';
        if (file === 'vote.html') return 'vote';
        if (file === 'privacy.html') return 'privacy';
        return null;
    }

    function initDevMode() {
        const API_BASE = 'https://bonzi-v5.onrender.com';
        const STORAGE_KEY = 'bonzi_cockpit_key';

        // ?cockpit in URL triggers the prompt
        const params = new URLSearchParams(window.location.search);
        if (params.has('cockpit')) {
            window.history.replaceState({}, '', window.location.pathname);
            showCockpitPrompt();
            return;
        }

        // If stored key exists, enable dev mode immediately
        const storedKey = localStorage.getItem(STORAGE_KEY);
        if (storedKey) {
            enableDevMode();
            // Lazy verify — revoke if key is stale
            verifyKey(storedKey).then((ok) => {
                if (!ok) {
                    localStorage.removeItem(STORAGE_KEY);
                    disableDevMode();
                }
            });
        }

        // Clicking any coming-soon item triggers the prompt
        document.querySelectorAll('.nav-coming-soon').forEach((el) => {
            el.style.cursor = 'pointer';
            el.addEventListener('click', showCockpitPrompt);
        });

        function verifyKey(key) {
            return fetch(API_BASE + '/dev/cockpit/ping', {
                headers: { 'X-Cockpit-Key': key },
            })
                .then((r) => r.ok)
                .catch(() => false);
        }

        function enableDevMode() {
            document.body.classList.add('dev-mode');
            document.querySelectorAll('.nav-coming-soon').forEach((el) => {
                const text = el.textContent.trim();
                const link = document.createElement('a');
                link.href = '/' + text + (text === 'stake' ? '.html' : '/');
                link.className = 'nav-link';
                link.textContent = text;
                link.dataset.nav = text;
                el.replaceWith(link);
            });
        }

        function disableDevMode() {
            document.body.classList.remove('dev-mode');
            // Reload to restore coming-soon spans
            window.location.reload();
        }

        function showCockpitPrompt() {
            // Don't stack modals
            if (document.getElementById('cockpit-modal')) return;

            const modal = document.createElement('div');
            modal.id = 'cockpit-modal';
            modal.className = 'cockpit-modal';
            modal.innerHTML = `
                <div class="cockpit-modal-box">
                    <div class="cockpit-modal-title">Cockpit Access</div>
                    <input type="password" id="cockpit-key-input" class="cockpit-input" placeholder="Enter cockpit key" autocomplete="off" />
                    <div class="cockpit-error" id="cockpit-error"></div>
                    <div class="cockpit-actions">
                        <button id="cockpit-cancel" class="cockpit-btn cockpit-btn-cancel">Cancel</button>
                        <button id="cockpit-submit" class="cockpit-btn cockpit-btn-submit">Unlock</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            const input = document.getElementById('cockpit-key-input');
            const error = document.getElementById('cockpit-error');
            const submitBtn = document.getElementById('cockpit-submit');

            input.focus();

            const submit = async () => {
                const key = input.value.trim();
                if (!key) return;
                submitBtn.textContent = '...';
                submitBtn.disabled = true;
                const ok = await verifyKey(key);
                if (ok) {
                    localStorage.setItem(STORAGE_KEY, key);
                    modal.remove();
                    enableDevMode();
                } else {
                    error.textContent = 'Invalid key';
                    submitBtn.textContent = 'Unlock';
                    submitBtn.disabled = false;
                    input.value = '';
                    input.focus();
                }
            };

            submitBtn.addEventListener('click', submit);
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') submit();
            });
            document.getElementById('cockpit-cancel').addEventListener('click', () => modal.remove());
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.remove();
            });
        }
    }

    function initTheme() {
        const saved = localStorage.getItem(THEME_KEY) || localStorage.getItem(LEGACY_THEME_KEY);
        const defaultSetting = document.body.dataset.themeDefault || 'light';
        const defaultTheme = defaultSetting === 'system'
            ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
            : defaultSetting;
        const theme = saved || defaultTheme;
        setTheme(theme);

        const toggle = document.getElementById('theme-toggle');
        if (!toggle) return;
        toggle.addEventListener('click', () => {
            const isDark = !document.body.classList.contains('dark-mode');
            setTheme(isDark ? 'dark' : 'light');
        });
    }

    function setTheme(theme) {
        const isDark = theme === 'dark';
        document.body.classList.toggle('dark-mode', isDark);
        document.body.classList.toggle('light-mode', !isDark);
        localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
        localStorage.setItem(LEGACY_THEME_KEY, isDark ? 'dark' : 'light');
    }

    // Per-page i18n: pages that provide a window.BONZI_I18N dict of
    // { lang: { "data-i18n-key": "translated string" } } get in-place
    // translation via flag clicks. Pages without a dict: flags click but
    // content stays in English (graceful degradation — no GT redirect ever).
    var _i18nOrigText = {};

    function _i18nCacheOrig() {
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var k = el.getAttribute('data-i18n');
            if (_i18nOrigText[k] == null) _i18nOrigText[k] = el.innerHTML;
        });
    }

    // Central JSON cache (i18n/{lang}.json). Authority source for unified pages.
    var _i18nCentralCache = {};

    function _i18nBasePath() {
        var segs = window.location.pathname.split('/').filter(function(s) {
            return s && !s.endsWith('.html');
        });
        return segs.length === 0 ? './' : '../'.repeat(segs.length);
    }

    function _i18nLoadCentral(lang) {
        if (_i18nCentralCache[lang] !== undefined) {
            return Promise.resolve(_i18nCentralCache[lang]);
        }
        return fetch(_i18nBasePath() + 'i18n/' + lang + '.json')
            .then(function(r) { return r.ok ? r.json() : null; })
            .then(function(j) { _i18nCentralCache[lang] = j || null; return _i18nCentralCache[lang]; })
            .catch(function() { _i18nCentralCache[lang] = null; return null; });
    }

    // Central JSON is authority; per-page BONZI_I18N dict is fallback during
    // migration. Dict-only pages (no central keys) keep working unchanged.
    function _i18nApply(lang) {
        var dict = (window.BONZI_I18N && window.BONZI_I18N[lang]) || {};
        _i18nLoadCentral(lang).then(function(central) {
            central = central || {};
            document.documentElement.lang = lang;
            document.querySelectorAll('[data-i18n]').forEach(function(el) {
                var k = el.getAttribute('data-i18n');
                var v = (central[k] != null) ? central[k] : dict[k];
                if (v != null) el.innerHTML = v;
            });
        });
    }

    function _i18nRestoreEn() {
        document.documentElement.lang = 'en';
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var k = el.getAttribute('data-i18n');
            if (_i18nOrigText[k] != null) el.innerHTML = _i18nOrigText[k];
        });
    }

    function _i18nSetActive(lang) {
        // sync active state across both the desktop nav flags and the mobile menu flags
        document.querySelectorAll('#nav-lang-flags button, .mobile-lang-flags button').forEach(function(b) {
            b.classList.toggle('active', b.getAttribute('data-lang') === lang);
        });
    }

    function _i18nSetLang(lang) {
        localStorage.setItem('bonzi_lang', lang);
        localStorage.setItem('bonzi-lang', lang);
        if (lang === 'en') { _i18nRestoreEn(); _i18nSetActive('en'); return; }
        _i18nApply(lang);
        _i18nSetActive(lang);
    }

    // A flag shows only if the page actually delivers that language.
    // Page declares window.BONZI_LANGS = ['en','pt',...]; default is English-only
    // so hardcoded pages never show a flag that does nothing. 'en' is always allowed.
    function _allowedLangs() {
        var a = (window.BONZI_LANGS && window.BONZI_LANGS.length) ? window.BONZI_LANGS.slice() : ['en'];
        if (a.indexOf('en') === -1) a.push('en');
        return a;
    }

    function _wireFlagGroup(container) {
        if (!container) return;
        var allowed = _allowedLangs();
        container.querySelectorAll('button[data-lang]').forEach(function(btn) {
            var L = btn.getAttribute('data-lang');
            if (allowed.indexOf(L) === -1) {
                btn.style.display = 'none';
                return;
            }
            btn.addEventListener('click', function() {
                _i18nSetLang(L);
            });
        });
    }

    function initLanguageSelect() {
        _i18nCacheOrig();
        _wireFlagGroup(document.getElementById('nav-lang-flags'));
        // Mobile menu flags are injected dynamically; wire them after menu loads
        var mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenu) {
            _wireFlagGroup(mobileMenu.querySelector('.mobile-lang-flags'));
        } else {
            // mobile-menu may not be loaded yet; observe for it
            var obs = new MutationObserver(function(_, o) {
                var mm = document.getElementById('mobile-menu');
                if (mm) { _wireFlagGroup(mm.querySelector('.mobile-lang-flags')); o.disconnect(); }
            });
            obs.observe(document.body, { childList: true, subtree: true });
        }
        // Restore saved language preference on page load
        var saved = localStorage.getItem('bonzi_lang') || localStorage.getItem('bonzi-lang') || 'en';
        if (saved && saved !== 'en') { _i18nApply(saved); }
        _i18nSetActive(saved || 'en');
    }

    function initNavInteractions() {
        const navDropdowns = document.querySelectorAll('.nav-dropdown');
        navDropdowns.forEach((dropdown) => {
            const link = dropdown.querySelector('.nav-link');
            if (!link) return;
            link.addEventListener('click', (e) => {
                if (window.matchMedia('(hover: none)').matches) {
                    if (!dropdown.classList.contains('active')) {
                        e.preventDefault();
                        navDropdowns.forEach((d) => d.classList.remove('active'));
                        dropdown.classList.add('active');
                    }
                }
            });
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-dropdown')) {
                navDropdowns.forEach((d) => d.classList.remove('active'));
            }
        });
    }

    function initMobileMenu() {
        const hamburger = document.getElementById('hamburger');
        const mobileMenu = document.getElementById('mobile-menu');
        if (!hamburger || !mobileMenu) return;

        const setMenuState = (open) => {
            hamburger.classList.toggle('active', open);
            mobileMenu.classList.toggle('open', open);
            mobileMenu.classList.toggle('active', open);
            hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
            mobileMenu.setAttribute('aria-hidden', open ? 'false' : 'true');
            document.body.style.overflow = open ? 'hidden' : '';
        };

        const toggleMenu = () => {
            const isOpen = mobileMenu.classList.contains('open') || mobileMenu.classList.contains('active');
            setMenuState(!isOpen);
        };

        const closeMenu = () => setMenuState(false);

        hamburger.addEventListener('click', toggleMenu);
        hamburger.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleMenu();
            }
        });

        mobileMenu.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', closeMenu);
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeMenu();
        });

        window.toggleMobileMenu = toggleMenu;
        window.closeMobileMenu = closeMenu;
    }

    function initContactLinks() {
        const contactModal = document.getElementById('contact-modal');
        const contactNavBtn = document.getElementById('contact-nav-btn');
        const contactMobileBtn = document.getElementById('contact-mobile-btn');

        const openContact = (e) => {
            if (!contactModal) return;
            e.preventDefault();
            if (typeof window.closeMobileMenu === 'function') window.closeMobileMenu();
            contactModal.classList.add('active');
        };

        if (contactNavBtn) {
            contactNavBtn.addEventListener('click', (e) => {
                if (contactModal) openContact(e);
            });
        }

        if (contactMobileBtn) {
            contactMobileBtn.addEventListener('click', (e) => {
                if (contactModal) openContact(e);
            });
        }

        if (contactModal && new URLSearchParams(window.location.search).get('contact')) {
            contactModal.classList.add('active');
            window.history.replaceState({}, '', window.location.pathname);
        }
    }

    function initBrazilButton() {
        if (document.getElementById('br-translate-btn')) return;

        var isTranslated = window.location.hostname.endsWith('.translate.goog');
        var btn = document.createElement('a');
        btn.id = 'br-translate-btn';
        btn.href = '#';

        if (isTranslated) {
            btn.title = 'Back to English';
            btn.setAttribute('aria-label', 'Back to English');
            btn.innerHTML = '\uD83C\uDDFA\uD83C\uDDF8 EN';
        } else {
            btn.title = 'Traduzir para Portugues';
            btn.setAttribute('aria-label', 'Translate to Brazilian Portuguese');
            btn.innerHTML = '\uD83C\uDDE7\uD83C\uDDF7 PT';
        }

        btn.style.cssText = [
            'position: fixed',
            'bottom: 20px',
            'left: 20px',
            'background: #27AE60',
            'color: #FFFFFF',
            'padding: 10px 16px',
            'font-size: 13px',
            'font-weight: 700',
            'letter-spacing: 0.5px',
            'text-decoration: none',
            'z-index: 9999',
            'display: flex',
            'align-items: center',
            'gap: 6px',
            'transition: background 0.2s, transform 0.2s',
            'box-shadow: 0 2px 8px rgba(0,0,0,0.15)',
            'cursor: pointer',
            'font-family: -apple-system, BlinkMacSystemFont, sans-serif'
        ].join(';');

        btn.addEventListener('mouseenter', function() {
            this.style.background = '#1E8449';
            this.style.transform = 'translateY(-2px)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.background = '#27AE60';
            this.style.transform = 'translateY(0)';
        });
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (isTranslated) {
                var h = window.location.hostname.replace('.translate.goog', '').replace(/--/g, '\x00').replace(/-/g, '.').replace(/\x00/g, '-');
                window.location.href = 'https://' + h + window.location.pathname;
            } else {
                window.location.href = 'https://translate.google.com/translate?sl=en&tl=pt&u=' + encodeURIComponent(window.location.href);
            }
        });

        document.body.appendChild(btn);
    }

    function initDemoButton() {
        const demoBtn = document.getElementById('nav-connect-btn');
        if (!demoBtn) return;

        demoBtn.addEventListener('click', () => {
            if (typeof window.openSlotPanel === 'function') {
                window.openSlotPanel();
            } else {
                window.location.href = '/?slot=open';
            }
        });
    }
})();
