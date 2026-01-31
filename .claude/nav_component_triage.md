# Nav Component Extraction - Codex Triage

**Created**: 2026-01-31
**Priority**: P1
**Owner**: Codex

## Problem
Navigation is duplicated across 8+ HTML files. Mobile hamburger menu missing on most pages. Each update requires editing all files.

## Current State
- `index.html` - Has hamburger + mobile menu (DONE)
- `features.html` - Has hamburger + mobile menu (DONE)
- `dao/index.html` - Has hamburger (needs mobile menu sync)
- **Missing hamburger**: manual/index.html, manifesto.html, economics/index.html, privacy.html, stake.html, vote.html

## Task: Extract Nav to Shared Component

### 1. Create `includes/nav.html`
```html
<!-- Mobile Hamburger -->
<div class="hamburger" id="hamburger" onclick="toggleMobileMenu()">
    <span></span>
    <span></span>
    <span></span>
</div>

<a href="./" class="nav-logo"><img src="bonzi-logo.png" alt="" class="nav-logo-img">Bonzi</a>

<div class="nav-links">
    <div class="nav-dropdown">
        <a href="features.html" class="nav-link" data-i18n="nav.features">features</a>
        <div class="nav-dropdown-menu">
            <a href="features.html#retail">Telegram Bot</a>
            <a href="features.html#developer">GitHub OSS</a>
            <a href="features.html#enterprise">BaaS</a>
            <a href="features.html#agent">ERC-8004 API</a>
        </div>
    </div>
    <!-- ... other dropdowns ... -->
    <div class="nav-divider"></div>
    <span class="nav-link gated" style="cursor: not-allowed; opacity: 0.5;">metrics <small style="font-size:9px;">Coming Soon</small></span>
    <span class="nav-link gated" style="cursor: not-allowed; opacity: 0.5;">stake <small style="font-size:9px;">Coming Soon</small></span>
    <span class="nav-link gated" style="cursor: not-allowed; opacity: 0.5;">dao <small style="font-size:9px;">Coming Soon</small></span>
    <div class="nav-divider"></div>
    <a href="index.html?contact=1" class="nav-link" data-i18n="nav.contact">contact</a>
</div>

<div class="nav-right">
    <select class="nav-lang-select" id="lang-select" aria-label="Language">
        <option value="en">EN</option>
        <option value="pt">PT</option>
        <option value="zh">ZH</option>
        <option value="tr">TR</option>
        <option value="ru">RU</option>
        <option value="fr">FR</option>
    </select>
    <button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">
        <!-- moon/sun SVGs -->
    </button>
    <button class="nav-connect-btn" id="nav-connect-btn" disabled>Coming Soon</button>
</div>
```

### 2. Create `includes/mobile-menu.html`
```html
<div class="mobile-menu" id="mobile-menu">
    <a href="features.html" data-i18n="nav.features">features</a>
    <a href="manual/" data-i18n="nav.manual">manual</a>
    <a href="manifesto.html" data-i18n="nav.manifesto">manifesto</a>
    <a href="economics/" data-i18n="nav.economics">economics</a>
    <div class="menu-divider"></div>
    <span class="menu-gated">metrics <small>Coming Soon</small></span>
    <span class="menu-gated">stake <small>Coming Soon</small></span>
    <span class="menu-gated">dao <small>Coming Soon</small></span>
    <div class="menu-divider"></div>
    <a href="index.html?contact=1" data-i18n="nav.contact">contact</a>
</div>
```

### 3. Create `js/nav-loader.js`
```javascript
// Load nav component into all pages
async function loadNav() {
    const navContainer = document.getElementById('nav-container');
    const mobileMenuContainer = document.getElementById('mobile-menu-container');

    // Determine path prefix based on current location
    const isSubdir = window.location.pathname.includes('/manual/') ||
                     window.location.pathname.includes('/economics/') ||
                     window.location.pathname.includes('/dao/') ||
                     window.location.pathname.includes('/metrics/');
    const prefix = isSubdir ? '../' : '';

    // Load nav
    const navRes = await fetch(prefix + 'includes/nav.html');
    navContainer.innerHTML = await navRes.text();

    // Load mobile menu
    const menuRes = await fetch(prefix + 'includes/mobile-menu.html');
    mobileMenuContainer.innerHTML = await menuRes.text();

    // Fix relative paths if in subdir
    if (isSubdir) {
        navContainer.querySelectorAll('a[href^="features"], a[href^="index"], a[href^="manifesto"]').forEach(a => {
            a.href = '../' + a.getAttribute('href');
        });
        navContainer.querySelector('.nav-logo img').src = '../bonzi-logo.png';
    }

    // Mark current page as active
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    navContainer.querySelectorAll('.nav-link').forEach(link => {
        if (link.href.includes(currentPage)) {
            link.classList.add('active');
        }
    });

    // Initialize theme toggle
    initTheme();
}

function toggleMobileMenu() {
    document.getElementById('hamburger').classList.toggle('active');
    document.getElementById('mobile-menu').classList.toggle('open');
}

function initTheme() {
    const saved = localStorage.getItem('bonzi_theme');
    if (saved === 'dark') document.body.classList.add('dark-mode');

    document.getElementById('theme-toggle')?.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('bonzi_theme',
            document.body.classList.contains('dark-mode') ? 'dark' : 'light');
    });
}

document.addEventListener('DOMContentLoaded', loadNav);
```

### 4. Update each HTML page
Replace inline `<nav>...</nav>` with:
```html
<nav id="nav-container"></nav>
<div id="mobile-menu-container"></div>
<script src="js/nav-loader.js"></script>
```

### 5. Create `css/nav.css`
Extract all nav-related CSS into shared file.

## Files to Update
1. index.html
2. features.html
3. manual/index.html
4. manifesto.html
5. economics/index.html
6. dao/index.html
7. privacy.html
8. stake.html
9. vote.html

## Acceptance Criteria
- [ ] `includes/nav.html` created with full nav structure
- [ ] `includes/mobile-menu.html` created
- [ ] `js/nav-loader.js` handles path prefixes for subdirs
- [ ] `css/nav.css` extracted with all nav styles
- [ ] All 9 pages updated to use loader
- [ ] Hamburger works on mobile (all pages)
- [ ] Language selector synced across pages
- [ ] Theme toggle works across pages
- [ ] Active page highlighted in nav

## Test Locally
```bash
cd community-bot-temp
python3 -m http.server 8000
# Open http://localhost:8000 and test all pages on mobile viewport
```
