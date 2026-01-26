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
**Keep the Tokenise button visible.** Add "Coming Soon" text directly below it.
Lock everything AFTER the launch-area (line ~4574 onwards).

## Changes Required

### 1. Add "Coming Soon" Below Tokenise Button
Insert AFTER the `<button class="tokenise-btn">` (line ~4572):
```html
<!-- Coming Soon text -->
<p class="coming-soon-text">Coming Soon</p>
```

So the launch-area becomes:
```html
<div class="launch-area">
    <div class="launch-sentence">
        <span class="trigger-text">Launch Your </span><span class="trigger-word" id="trigger-word">Future</span>
    </div>
    <button class="tokenise-btn" id="launch-trigger">Tokenise</button>
    <p class="coming-soon-text">Coming Soon</p>  <!-- ADD THIS -->
</div>
```

### 2. CSS for Coming Soon Text
```css
.coming-soon-text {
    margin-top: 16px;
    font-size: 14px;
    color: var(--gray);
    text-transform: uppercase;
    letter-spacing: 2px;
}
```

### 3. Hide Everything After Launch Area
```css
/* Hide all sections after statement (which contains launch-area) */
.statement ~ section,
.statement ~ .pain-section,
.statement ~ .solutions-section,
.statement ~ .comparison-section,
.statement ~ .demo-section,
.statement ~ .pricing-section,
.statement ~ .mission-section,
.statement ~ .links-section,
.statement ~ footer {
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
