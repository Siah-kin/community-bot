# Nav Bar Consistency Fix - Claude.ai Handoff

## Problem
Nav bar is inconsistent across pages. Elements missing:
- Bonzi logo (left)
- "stake" link (between metrics and dao)
- Theme toggle (moon/sun icon)
- Language selector dropdown
- Connect button

## Root Cause
Each HTML page has inline `<style>` CSS that overrides `bonzi-design.css`. The `nav-right` section gets hidden.

## Pages to Audit
Open each locally, screenshot nav, identify what's missing:

1. `metrics/index.html` - just fixed, verify
2. `stake.html` - should have full nav
3. `vote.html` - likely missing elements
4. `privacy.html` - likely missing elements
5. `dao/index.html` - REFERENCE (correct nav)
6. `index.html` - homepage

## Correct Nav HTML Structure
```html
<nav>
    <a href="./" class="nav-logo"><img src="bonzi-logo.png" alt="" class="nav-logo-img">Bonzi</a>

    <div class="nav-links">
        <!-- dropdowns: features, manual, manifesto, economics -->
        <div class="nav-divider"></div>
        <a href="metrics/" class="nav-link gated">metrics</a>
        <a href="stake.html" class="nav-link gated">stake</a>
        <a href="dao/" class="nav-link gated">dao</a>
        <div class="nav-divider"></div>
        <a href="index.html?contact=1" class="nav-link">contact</a>
    </div>

    <div class="nav-right">
        <select class="nav-lang-select" id="lang-select">
            <option value="en">EN</option>
            <option value="pt">PT</option>
            <option value="zh">ZH</option>
            <option value="tr">TR</option>
            <option value="ru">RU</option>
            <option value="fr">FR</option>
        </select>
        <button class="theme-toggle" id="theme-toggle">
            <svg class="icon-moon">...</svg>
            <svg class="icon-sun">...</svg>
        </button>
        <button class="nav-connect-btn" id="nav-connect-btn">connect</button>
    </div>
</nav>
```

## Required Inline CSS (add to each page's `<style>`)
```css
.nav-right { display: flex; align-items: center; gap: 12px; }
.nav-lang-select {
    background: transparent;
    border: 1px solid var(--gray-light);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    cursor: pointer;
}
.theme-toggle {
    background: transparent;
    border: 1px solid var(--gray-light);
    border-radius: 6px;
    padding: 6px 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
}
.theme-toggle svg { width: 16px; height: 16px; }
.theme-toggle .icon-sun { display: none; }
body.light-mode .theme-toggle .icon-moon { display: none; }
body.light-mode .theme-toggle .icon-sun { display: block; }
.nav-connect-btn {
    background: var(--purple);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
}
```

## Theme Toggle JS (add to each page)
```javascript
function initTheme() {
    const saved = localStorage.getItem('bonzi-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    document.body.classList.toggle('light-mode', theme === 'light');
}
initTheme();

document.getElementById('theme-toggle')?.addEventListener('click', function() {
    const isLight = document.body.classList.toggle('light-mode');
    localStorage.setItem('bonzi-theme', isLight ? 'light' : 'dark');
});
```

## Future Fix: Extract to Shared Include
Consider creating `includes/nav.html` and using JS to load it, or switch to a static site generator.
