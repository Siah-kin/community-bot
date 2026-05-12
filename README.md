# Bonzi Community Bot (Oracle)

**What this repo is:** the **public website** for Bonzi Vista (GitHub Pages): static HTML/CSS/JS, manuals, the **MIT-licensed** BONZI staking mini-app client, slot landing page, metrics, widgets, and ERC-8004 **discovery** files under `.well-known/`.

**What this repo is not:** the Telegram bot runtime, admin dashboard, RAG stack, or trust engine **source code**—those live in private product infrastructure. Forking this repo gives you the **public site and open clients**, not a copy-paste of the full product backend.

**GitHub About text:** keep it aligned with [docs/REPO_ABOUT.md](docs/REPO_ABOUT.md). Do not use legacy wording that claims this repo *is* the full AI bot with RAG and dashboards.

**Agent discovery JSON** (`.well-known/agent*.json`) may be **auto-synced from the live API**; treat listed skills as **API surface / intent**, not a warranty that every path is live or row-proven for your tenant until you verify it.

- **Live site:** https://bonzivista.org

**GitHub Pages priority:** Every push to `main` should refresh the public site. This repo ships [`.github/workflows/pages.yml`](.github/workflows/pages.yml): turn it on under **Settings → Pages → Build and deployment → Source: GitHub Actions**. That runs a deploy on each `main` push with **concurrency** so overlapping pushes **finish** in order instead of cancelling mid-upload (set `cancel-in-progress: false`). If Pages looks stuck after a push, open **Actions** for the latest **Deploy GitHub Pages** run, confirm it is green, then hard-refresh `bonzivista.org` (CDN can cache HTML briefly). If you still use **Deploy from a branch** (`main` / root), pushes update Pages without Actions; pick **one** source in Settings to avoid duplicate or failed workflows. From Bonzi_v5, run `scripts/development/publish_public_pages_mirror.sh` to copy `data/static/tg/*` and push `main` in one step.
- **Telegram:** https://t.me/Bonzivista_bot
- **X:** https://x.com/Bonzi_vista
- **Ethervista:** https://www.ethervista.app/how-it-works
- **Trust API:** https://bonzi-v5.onrender.com/api/trust
- **Agent card (HTTPS):** https://bonzivista.org/.well-known/agent-card.json

## Quick links for testers

Public checkpoints only; no secrets. **Production** vs **GitHub Pages** hosts the **same repo** (`main` builds `gh-pages`).

- **Site:** https://bonzivista.org and https://siah-kin.github.io/community-bot/
- **Stake mini-app:** https://bonzivista.org/stake-tg.html · Pages: https://siah-kin.github.io/community-bot/stake-tg.html
- **FAQ bundle:** https://bonzivista.org/stake-faq-i18n.json · https://siah-kin.github.io/community-bot/stake-faq-i18n.json (**tracked on `main`** — `git pull` before auditing stale checkouts; introduced in `f49027b`.)
- **Source (MIT):** https://github.com/Siah-kin/community-bot
- **Telegram:** https://t.me/bonzivista_bot · **Community FAQ:** https://t.me/Bonzivision
- **Ethervista primer:** https://www.ethervista.app/how-it-works
- **Trust API sample:** `https://bonzi-v5.onrender.com/api/trust/<wallet>`

## What’s in this repo?

- Static website (HTML/CSS/JS)
- Docs + manuals (`manual/`, `docs/`, `economics/`, `dao/`, `metrics/`)
- Embeddable widgets (`widget/`)
- ERC-8004 agent discovery refs (`.well-known/`)

> Backend/oracle core is closed-source.

## BONZI staking mini-app (for external reviewers)

Third-party developers (for example **Ethervista**) can review the **public, MIT-licensed client** for the Telegram / browser stake flow without access to the private backend repo.

| Artifact | Path in this repo |
|----------|-------------------|
| Mini-app (HTML, CSS, wallet UI, staking tabs) | [`stake-tg.html`](stake-tg.html) |
| FAQ copy bundle (EN / PT / zh-CN), loaded at runtime | [`stake-faq-i18n.json`](stake-faq-i18n.json) |
| Alternate / legacy stake page | [`stake.html`](stake.html) |

- **Live:** https://bonzivista.org/stake-tg.html (primary) · https://siah-kin.github.io/community-bot/stake-tg.html (GitHub Pages same build)
- **On-chain interaction** is from the user’s wallet via the scripts in `stake-tg.html` (read the contract and RPC usage there). This repo does **not** hold server-side custody or signing.
- **Metrics and public JSON** linked from the footer and tiles are served from this site under `metrics/` where applicable; paths are ordinary HTTPS fetches.
- **Not open-sourced here:** Python bot, APIs, databases, and orchestration live in the separate **Bonzi_v5** codebase (see note above). Showing this repo is enough for “inspect the staking web client and public data dependencies,” not the full product backend.

Fork, audit, or open issues against this repo; `LICENSE` is MIT.

## Run locally

```bash
python3 -m http.server 8000
open http://localhost:8000/
```

## Slot page + first-party waitlist (`index.html`)

- **`bonzi-api-origin`**: HTTPS base where `/api/slotgame/*` and **`/api/public/waitlist`** live (Bonzi_v5 webhook host).
- **Default:** `bonzi-waitlist-mode` is **`first_party`**. The footer shows an inline email field that **POSTs JSON** to **`{bonzi-api-origin}/api/public/waitlist`** and stores rows in **Postgres** (`public_email_waitlist`) on the backend. No third-party form host.
- **Legacy override:** If you set **`bonzi-notify-signup-url`** to an external **`https://`** page (hosted form elsewhere), the footer switches to a single **Join** link and hides the inline form. Use `scripts/patch_notify_meta.py` the same way as before **only** when you intentionally want that override.

**Quick test (first-party)**

1. Ensure Bonzi_v5 production has **`USE_POSTGRES=true`** and a working **`DATABASE_URL`**.
2. `python3 -m http.server 8000` in this repo → open `/` → submit an email → expect HTTP 200 from `https://<your-api-host>/api/public/waitlist` (check browser devtools Network).
3. On Render shell: `SELECT email_normalized, source, created_at FROM public_email_waitlist ORDER BY created_at DESC LIMIT 5;`

**Telegram `/start` CTA:** By default the bot uses **`https://bonzivista.org/#email-updates`** so **Get notified** scrolls users to this section. Override with **`BONZI_PUBLIC_NOTIFY_URL`** on Render if needed; set **`BONZI_PUBLIC_SITE_ORIGIN`** if the public site hostname changes. Set **`BONZI_PUBLIC_NOTIFY_DISABLED=1`** to remove the button entirely.

## API (quick examples)

See `docs/API.md` for the full reference.

```bash
curl "https://bonzi-v5.onrender.com/api/trust/0xYOUR_WALLET"
```

## Notes on audio assets

This repo ships with a tiny **placeholder** audio file so UI elements don’t 404, but no copyrighted music.

See `static/audio/README.md`.

## Contributing

See `CONTRIBUTING.md`.

## License

MIT (see `LICENSE`).

Trademarks, brand assets, and third‑party content may be subject to additional restrictions; see `LICENSE` and individual file headers where applicable.

