# Site Link Architecture Map

Last updated: 2026-01-18

## Site Structure

```
https://bonzivista.org/
├── index.html              (Home - landing page)
├── features.html           (Features - engineering deep dive)
├── faq.html                (Manifesto - confrontational FAQ)
├── privacy.html            (Privacy Policy)
├── research/index.html     (System Metrics - GATED)
├── dao/index.html          (DAO Governance - under construction)
├── economics/index.html    (Tokenomics)
└── manual/index.html       (Bot Documentation - GitBook style)
```

## Navigation Matrix

| Page | features | research | dao | economics | manual | faq | source |
|------|----------|----------|-----|-----------|--------|-----|--------|
| index.html | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| features.html | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| faq.html | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓ |
| privacy.html | ← back only | | | | | | |
| research/index.html | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| dao/index.html | ✓ | ✓ | - | ✓ | ✓ | ✓ | ✓ |
| economics/index.html | ✓ | ✓ | ✓ | - | ✓ | ✓ | ✓ |
| manual/index.html | ✓ | ✓ | ✓ | ✓ | - | ✓ | ✓ |

## External Links

| Link | Target | Opens In |
|------|--------|----------|
| Developer Guide | https://bonzivista.org/dev.html | _blank |
| Ethervista | https://ethervista.com | _blank |
| Telegram | https://t.me/Bonzivista_bot | _blank |

## Internal Link Patterns

### Root-level pages
- Use: `features.html`, `faq.html`, `privacy.html`
- Logo links to: `#` (same page) or `index.html`

### Subdirectory pages (/research/, /dao/, /economics/, /manual/)
- Use: `../features.html`, `../faq.html`, etc.
- Logo links to: `../`
- Within same directory: `./`

## SEO Considerations

### Canonical URLs (all pages have)
- index.html: https://bonzivista.org/
- features.html: https://bonzivista.org/features.html
- faq.html: https://bonzivista.org/faq.html
- research/: https://bonzivista.org/research/
- dao/: https://bonzivista.org/dao/
- economics/: https://bonzivista.org/economics/
- manual/: https://bonzivista.org/manual/
- privacy.html: https://bonzivista.org/privacy.html

### Priority (sitemap.xml)
1. index.html (1.0) - Main entry point
2. manual/ (0.9) - High-value documentation
3. features.html, research/, economics/, faq.html (0.8)
4. dao/ (0.7) - Under construction
5. privacy.html (0.3) - Legal compliance

## Gated Content

| Page | Gate Type | Requirement |
|------|-----------|-------------|
| research/ | Wallet Connect | DAO token/NFT ownership |

## Assets

All pages reference:
- `bonzi-logo.png` (favicon, logo)
- From subdirectories: `../bonzi-logo.png`

## Verification Commands

```bash
# Check all internal links work
for page in index.html features.html faq.html privacy.html; do
  echo "=== $page ==="
  grep -oP 'href="[^"#]*"' "$page" | grep -v http
done

# Check subdirectory links
for dir in research dao economics manual; do
  echo "=== $dir/index.html ==="
  grep -oP 'href="[^"#]*"' "$dir/index.html" | grep -v http
done

# Verify sitemap matches actual files
cat sitemap.xml | grep -oP '(?<=<loc>)[^<]+'
```
