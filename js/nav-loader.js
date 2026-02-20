(() => {
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
            const [navRes, menuRes] = await Promise.all([
                fetch(prefix + 'includes/nav.html'),
                fetch(prefix + 'includes/mobile-menu.html')
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

            document.dispatchEvent(new CustomEvent('nav:loaded'));
        } catch (err) {
            console.error('[nav-loader] Failed to load navigation:', err);
        }
    }

    function getPathPrefix() {
        const path = window.location.pathname;
        const subdirs = ['/manual/', '/manual', '/economics/', '/economics', '/research/', '/research', '/vetter/', '/vetter', '/dao/', '/dao', '/metrics/', '/metrics'];
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
        if (file === 'manifesto.html') return 'manifesto';
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

    function initLanguageSelect() {
        const select = document.getElementById('lang-select');
        if (!select) return;

        const savedLang = localStorage.getItem('bonzi-lang');
        if (savedLang) select.value = savedLang;

        select.addEventListener('change', (e) => {
            const lang = e.target.value;
            localStorage.setItem('bonzi-lang', lang);
            if (typeof setLanguage === 'function') setLanguage(lang);
        });
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
