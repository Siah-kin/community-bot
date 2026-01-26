# Coming Soon Mode - Claude.ai Handoff

## Goal
Lock down community-bot landing page to "Coming Soon" teaser mode.

## What Stays Accessible
1. **Opening section** (line ~4512) - Logo, "bonzi", tagline
2. **History section** (line ~4524) - Redemption story
3. **3 Reveal slides** (lines ~4534, 4544, 4555) - Pitch text
4. **Statement text** (line ~4561-4562) - "Trading fees fund the tip pool..."
5. **Win98 music player** - Keep fully functional

## Cutoff Point
**Lock JUST BEFORE line 4564:** `<div class="launch-area">`

The **Tokenise button** and everything below should be hidden/locked.

## Changes Required

### 1. Add "Coming Soon" Overlay
Insert just before `<div class="launch-area">`:
```html
<!-- Coming Soon Cutoff -->
<div class="coming-soon-gate">
    <div class="coming-soon-content">
        <span class="lock-icon">🔒</span>
        <h2>Coming Soon</h2>
        <p>Full experience launching shortly.</p>
    </div>
</div>
```

### 2. CSS for Coming Soon Gate
```css
.coming-soon-gate {
    position: relative;
    width: 100%;
    padding: 120px 40px;
    background: linear-gradient(180deg, transparent 0%, rgba(10,10,10,0.95) 30%);
    text-align: center;
}
.coming-soon-content {
    max-width: 400px;
    margin: 0 auto;
}
.coming-soon-content .lock-icon {
    font-size: 48px;
    display: block;
    margin-bottom: 16px;
}
.coming-soon-content h2 {
    font-size: 32px;
    color: var(--purple);
    margin-bottom: 8px;
}
.coming-soon-content p {
    color: var(--gray);
    font-size: 16px;
}
```

### 3. Hide Everything After Cutoff
```css
/* Hide all content after coming-soon-gate */
.coming-soon-gate ~ * {
    display: none !important;
}

/* But keep Win98 player visible */
.win98-player {
    display: flex !important;
}
```

### 4. Lock Nav Items
Replace nav links with locked versions:
```html
<a href="#" class="nav-link locked" onclick="return false;">
    <span class="nav-lock">🔒</span> features
    <span class="nav-coming-soon">Coming Soon</span>
</a>
```

CSS for locked nav:
```css
.nav-link.locked {
    opacity: 0.5;
    cursor: not-allowed;
    position: relative;
}
.nav-link.locked .nav-lock {
    font-size: 10px;
    margin-right: 4px;
}
.nav-link.locked .nav-coming-soon {
    position: absolute;
    bottom: -18px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 9px;
    color: var(--purple);
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.2s;
}
.nav-link.locked:hover .nav-coming-soon {
    opacity: 1;
}
```

### 5. Disable Scroll Past Cutoff
```javascript
// Lock scroll at coming-soon-gate
const gate = document.querySelector('.coming-soon-gate');
if (gate) {
    window.addEventListener('scroll', () => {
        const gateTop = gate.offsetTop;
        if (window.scrollY > gateTop - window.innerHeight + 200) {
            window.scrollTo(0, gateTop - window.innerHeight + 200);
        }
    });
}
```

## Files to Modify
- `index.html` - Add gate HTML, update nav links
- Inline CSS in `index.html` - Add coming-soon styles
- Inline JS in `index.html` - Add scroll lock

## Keep Working
- Win98 music player (bottom bar)
- Sound toggle button
- Playlist functionality
- Opening animations

## Test
1. Page loads with opening + history + reveals + statement
2. Scrolling stops at "Coming Soon" overlay
3. Nav items show lock + "Coming Soon" on hover
4. Music player works normally
5. No access to features, manual, metrics, stake, dao pages
