# Bonzi Vista public site (`community-bot`)

**What this is:** the **public website** for Bonzi Vista, hosted on **GitHub Pages**: static HTML, CSS, and JavaScript. Visitors get the slot landing page, the **MIT-licensed** BONZI staking mini-app in the browser, manuals, and other public pages.

**What this is not:** the hosted Telegram bot, private APIs, databases, or server-side product code. Those are not in this repository. Forking here gives you the **public site and open front-end assets** only.

**Live site:** https://bonzivista.org

---

### Badges

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Live site](https://img.shields.io/badge/site-bonzivista.org-7c3aed.svg)](https://bonzivista.org/)
[![Slot (source)](https://img.shields.io/badge/slot-index.html-111827.svg)](https://github.com/Siah-kin/community-bot/blob/main/index.html)
[![Staking (source)](https://img.shields.io/badge/staking-stake--tg.html-111827.svg)](https://github.com/Siah-kin/community-bot/blob/main/stake-tg.html)

---

### What you can review here (no private repo needed)

| Area | Where |
|------|--------|
| Slot + homepage funnel | [`index.html`](index.html) |
| Staking mini-app (wallet UI, on-chain calls in-page) | [`stake-tg.html`](stake-tg.html) |
| Staking FAQ copy (EN / PT / zh-CN) | [`stake-faq-i18n.json`](stake-faq-i18n.json) |

**Help:** [Telegram @Bonzivista_bot](https://t.me/Bonzivista_bot)

**GitHub About text:** see [`docs/REPO_ABOUT.md`](docs/REPO_ABOUT.md) (one line for the repo description field).

---

### Deploy (Pages)

This repo is built for **GitHub Pages**. Use **one** deploy source in repo **Settings → Pages** (either **GitHub Actions** with [`.github/workflows/pages.yml`](.github/workflows/pages.yml) or **Deploy from a branch**), not both at once. After a deploy, hard-refresh if HTML looks cached.

---

### Quick links

- Site: https://bonzivista.org · https://siah-kin.github.io/community-bot/
- Staking: https://bonzivista.org/stake-tg.html
- FAQ JSON: https://bonzivista.org/stake-faq-i18n.json
- Source: https://github.com/Siah-kin/community-bot
- Ethervista primer: https://www.ethervista.app/how-it-works

---

### Repo layout (short)

- Static pages at repo root and under `manual/`, `docs/`, `economics/`, `dao/`, `metrics/`, etc.
- Embeds under `widget/`
- Optional discovery metadata under `.well-known/` (machine-readable; verify anything you rely on against your own checks).

---

### Staking mini-app (for auditors)

| File | Role |
|------|------|
| [`stake-tg.html`](stake-tg.html) | Main staking UI |
| [`stake-faq-i18n.json`](stake-faq-i18n.json) | FAQ strings |
| [`stake.html`](stake.html) | Alternate / legacy page |

No server-side custody in this repo; wallet signing happens in the browser per the scripts in those HTML files.

---

### Run locally

```bash
python3 -m http.server 8000
```

Then open the URL your terminal prints (often http://localhost:8000/) and browse `/`, `stake-tg.html`, etc.

---

### Maintainer note (keep out of visitor copy)

Backend wiring for the waitlist, slot API host, and production checks live with the **hosted service** and internal runbooks, not in this README. If you maintain the stack, use your private ops docs and the repo’s `docs/` tree for HTTP details; do not paste SQL, table names, or environment keys into public issues.

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT — see [`LICENSE`](LICENSE). Trademarks and third-party assets may have separate terms; see notices in individual files where applicable.
