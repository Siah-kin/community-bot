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
            initNavInteractions();
            initMobileMenu();
            initLanguageSelect();
            initContactLinks();

            document.dispatchEvent(new CustomEvent('nav:loaded'));
        } catch (err) {
            console.error('[nav-loader] Failed to load navigation:', err);
        }
    }

    function getPathPrefix() {
        const path = window.location.pathname;
        const subdirs = ['/manual/', '/manual', '/economics/', '/economics', '/vetter/', '/vetter', '/dao/', '/dao', '/metrics/', '/metrics'];
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
})();
