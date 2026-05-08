# Bonzi Community Bot (Oracle)

Public website + docs for **Bonzi**: an open-source AI community-management stack for Web3 (anti-sybil, raid verification, contributor rewards) plus an **ERC-8004-compatible trust oracle**.

- **Live site:** https://bonzivista.org
- **Telegram:** https://t.me/Bonzivista_bot
- **X:** https://x.com/Bonzi_vista
- **Ethervista:** https://www.ethervista.app/how-it-works
- **Trust API:** https://bonzi-v5.onrender.com/api/trust
- **Agent card:** `.well-known/agent-card.json`

## What’s in this repo?

- Static website (HTML/CSS/JS)
- Docs + manuals (`manual/`, `docs/`, `economics/`, `dao/`, `metrics/`)
- Embeddable widgets (`widget/`)
- ERC-8004 agent discovery refs (`.well-known/`)

> Backend/oracle core is closed-source.

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
2. From repo root:
   ```bash
   export BONZI_NOTIFY_SIGNUP_URL='https://YOUR_FORM_URL_HERE'
   python3 scripts/patch_notify_meta.py
   ```
3. Confirm `index.html` meta `bonzi-notify-signup-url` now holds that URL.
4. `python3 -m http.server 8000` → open `/` → you should see the bar and “Get notified” opens your form (not Telegram).
5. Commit + push → wait for Pages → hard-refresh `bonzivista.org`.

The page **rejects** `t.me` / `telegram.me` in this field on purpose — that URL is only for email signups.

**Optional (aligned with the bot):** On the Bonzi backend, set `BONZI_PUBLIC_NOTIFY_URL` to the same `https://` link if your deploy uses it for `/start`-style links.

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

