# Bonzi Community Bot (Oracle)

Public website + docs for **Bonzi**: an open-source AI community-management stack for Web3 (anti-sybil, raid verification, contributor rewards) plus an **ERC-8004-compatible trust oracle**.

- **Live site:** https://bonzivista.org
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

## Slot page + email notify strip (`index.html`)

- **`bonzi-api-origin`**: HTTPS base where `/api/slotgame/*` lives (production default in the meta tag).
- **`bonzi-notify-signup-url`**: Your **hosted email signup URL** — Mailchimp, Chimpmail, or any `https://` form page you control. Typical Mailchimp links use `list-manage.com`, `mailchi.mp`, or `chimp*.com`. Leave **empty** to hide the purple bar.

**Quick test**

1. In MailChimp/Chimpmail, copy the **hosted signup form** URL (must start with `https://`).
2. From repo root, either export the URL:

   ```bash
   export BONZI_NOTIFY_SIGNUP_URL='https://YOUR_FORM_URL_HERE'
   python3 scripts/patch_notify_meta.py
   ```

   or put **one HTTPS line** in a gitignored file (helps avoid pasting URLs into shell history):

   ```bash
   printf '%s\n' 'https://YOUR_FORM_URL_HERE' > scripts/bonzi_notify_signup_url.local.txt
   export BONZI_NOTIFY_SIGNUP_FILE=scripts/bonzi_notify_signup_url.local.txt
   python3 scripts/patch_notify_meta.py
   ```

   The script also **blocks** `t.me` / `telegram.me` so Telegram links cannot be committed here by mistake.

3. Confirm `index.html` meta `bonzi-notify-signup-url` now holds that URL.
4. `python3 -m http.server 8000` → open `/` → you should see the bar and “Get notified” opens your form (not Telegram).
5. Commit + push → wait for Pages → hard-refresh `bonzivista.org`.

The page **rejects** Telegram hosts in this field on purpose (`index.html` + patch script guard) — that URL is only for email signups.

**Optional (aligned with the bot):** In Render for Bonzi_v5, set `BONZI_PUBLIC_NOTIFY_URL` to the same `https://` link (Blueprint lists the key next to `SLOTGAME_PUBLIC_RULES_ORIGIN` in `render.yaml`) so `/start` can show **Get notified**.

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

