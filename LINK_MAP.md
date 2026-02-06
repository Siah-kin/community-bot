# Site Link Architecture Map

Last updated: 2026-02-04

## Site Structure

```
https://siah-kin.github.io/community-bot/
├── index.html              (Home - landing page)
├── features.html           (Features - engineering deep dive)
├── manifesto.html          (Manifesto - confrontational FAQ)
├── faq.html                (Redirect → manifesto.html)
├── privacy.html            (Privacy Policy)
├── docs/                   (Documentation index)
├── metrics/index.html      (System Metrics - GATED)
├── dao/index.html          (DAO Governance - under construction)
├── economics/index.html    (Tokenomics)
└── manual/index.html       (Bot Documentation - GitBook style)
```

## Navigation Matrix

| Page | features | metrics | dao | economics | manual | manifesto | source |
|------|----------|---------|-----|-----------|--------|-----------|--------|
| index.html | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| features.html | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| manifesto.html | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓ |
| privacy.html | ← back only | | | | | | |
| metrics/index.html | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| dao/index.html | ✓ | ✓ | - | ✓ | ✓ | ✓ | ✓ |
| economics/index.html | ✓ | ✓ | ✓ | - | ✓ | ✓ | ✓ |
| manual/index.html | ✓ | ✓ | ✓ | ✓ | - | ✓ | ✓ |

## External Links

| Link | Target | Opens In |
|------|--------|----------|
| GitHub Source | https://github.com/Siah-kin/community-bot | _blank |
| Ethervista | https://ethervista.com | _blank |
| Telegram | https://t.me/ethervista | _blank |

## Internal Link Patterns

### Root-level pages
- Use: `features.html`, `manifesto.html`, `privacy.html`
- Logo links to: `#` (same page) or `index.html`

### Subdirectory pages (/metrics/, /dao/, /economics/, /manual/, /docs/)
- Use: `../features.html`, `../manifesto.html`, etc.
- Logo links to: `../`
- Within same directory: `./`

## SEO Considerations

### Canonical URLs (all pages have)
- index.html: https://siah-kin.github.io/community-bot/
- features.html: https://siah-kin.github.io/community-bot/features.html
- manifesto.html: https://siah-kin.github.io/community-bot/manifesto.html
- docs/: https://siah-kin.github.io/community-bot/docs/
- metrics/: https://siah-kin.github.io/community-bot/metrics/
- dao/: https://siah-kin.github.io/community-bot/dao/
- economics/: https://siah-kin.github.io/community-bot/economics/
- manual/: https://siah-kin.github.io/community-bot/manual/
- privacy.html: https://siah-kin.github.io/community-bot/privacy.html

### Priority (sitemap.xml)
1. index.html (1.0) - Main entry point
2. manual/ (0.9) - High-value documentation
3. features.html, metrics/, economics/, manifesto.html (0.8)
4. dao/ (0.7) - Under construction
5. docs/ (0.6) - Developer docs index
5. privacy.html (0.3) - Legal compliance

## Gated Content

| Page | Gate Type | Requirement |
|------|-----------|-------------|
| metrics/ | Wallet Connect | DAO token/NFT ownership |

## Assets

All pages reference:
- `bonzi-logo.png` (favicon, logo)
- From subdirectories: `../bonzi-logo.png`

## Verification Commands

```bash
# Check all internal links work
for page in index.html features.html manifesto.html privacy.html; do
  echo "=== $page ==="
  grep -oP 'href="[^"#]*"' "$page" | grep -v http
done

# Check subdirectory links
for dir in metrics dao economics manual docs; do
  echo "=== $dir/index.html ==="
  grep -oP 'href="[^"#]*"' "$dir/index.html" | grep -v http
done

# Verify sitemap matches actual files
cat sitemap.xml | grep -oP '(?<=<loc>)[^<]+'
```
