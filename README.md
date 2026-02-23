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

