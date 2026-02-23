# Contributing

Thanks for helping improve Bonzi.

## Quick workflow

1. Fork the repo + create a branch
2. Make your changes
3. Run the validations (optional but recommended)
4. Open a PR with a short description + screenshots (for UI changes)

## Local preview

This repo is a static site. Any local server works:

```bash
python3 -m http.server 8000
open http://localhost:8000/
```

## Validations

Nav + footer consistency scripts live in `scripts/`:

```bash
python3 scripts/validate_nav.py
python3 scripts/validate_footer.py
```

## Content guidelines

- Don’t commit secrets: API keys belong in local `.env` files (see `metrics/.env.example`).
- Prefer linking to canonical docs instead of duplicating long content.
- Keep copy factual and avoid publishing private/internal strategy notes.
- For translations, update the JSON files in `i18n/` and verify the page still renders.

## Where to edit

- Homepage + marketing pages: root `*.html`
- Manual pages: `manual/`
- Tokenomics: `economics/`
- DAO: `dao/`
- Metrics + whitepaper: `metrics/`
- Widgets: `widget/`

