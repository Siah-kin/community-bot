# Translation Inventory — bonzivista.org + Bonzi bot

_Generated 2026-06-08. Grounded in grep/key-diff, not memory._

## Why "done" kept being false

Four different translation mechanisms coexist. There is no single place to
check coverage, so a page can pass one check and still show English.

- **System A** — `js/i18n-loader.js` reads central `i18n/{en,pt,zh}.json`
  (259 keys), applies to `[data-i18n]` via `textContent`, storage `bonzi_lang`.
- **System B** — `js/nav-loader.js` reads a per-page inline `window.BONZI_I18N`
  dict, applies to `[data-i18n]` via `innerHTML`. Different storage key.
- **System C** — the page's own inline `I18N` JS object (slot game, staking).
- **System D** — separate translated HTML files (`*-pt.html`).

Conflicts found:
- `about.html` runs System A AND System B on the same 12 elements (race).
- `vote.html` has 11 `data-i18n` markers but no dict and no loader — never translated.
- `baas.html` / `features.html` include the loader but key nothing — fully English.

## Central JSON state (System A)

- `i18n/en.json`: 259 keys. Consumed mainly by `manual/index.html`.
- `i18n/pt.json`: 14 keys missing (all `baas.*`).
- `i18n/zh.json`: 225 keys missing.
- `i18n/fr.json`, `ru.json`, `tr.json`: do not exist.

## Bonzi bot strings (separate, Bonzi_v5 repo)

- `src/infra/localization/strings/en.json`: 438 keys.
- `pt-BR.json`: 1 missing (`dao.dm_fixed`).
- `zh-CN.json`: 1 missing (`dao.dm_fixed`).
- `fr.json`, `ru.json`, `tr.json`: do not exist.

## Page-by-page (top level)

- `index.html` (2843 ln) — slot game, System C inline object.
- `manual/index.html` — System A, 259 central keys (the big guide hub).
- `about.html` (380) — System A + B conflict, 12 keys.
- `dev.html` (6898) — System B, 84 keys.
- `manifesto.html` (1332) — System B, 16 keys.
- `vote.html` (889) — 11 dead `data-i18n` markers, no translations.
- `stake.html` (4682) — System C inline, 0 `data-i18n`.
- `features.html` (666) — loader included, 0 keys → English.
- `baas.html` (864) — loader included, 0 keys → English.
- `404.html` (55) — no i18n.
- `coming-soon.html` (112) — no i18n.
- `faq.html` (13) — no i18n.
- `privacy.html` (19) — no i18n.
- `stake-tg.html` (1) — redirect stub.

## Subdirectory pages (not yet string-counted)

`dao/`, `economics/`, `metrics/` (+ `metrics-pt.html`), `stake/`, `vetter/`,
`research/` (+ `openbox-proof-pt.html`), `demo_silverfox/`.

## Verification gate (per the operator)

A page is "done" for a language only when BOTH hold:
1. `key-diff {lang}.json vs en.json` = 0 missing.
2. `grep` for user-visible English outside the i18n system on that page = 0 hits.
