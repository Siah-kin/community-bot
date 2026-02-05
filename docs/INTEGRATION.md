# Integration Guide

## 1) Embed the buy widget

Use the brand widget to let users buy your token with email + card (Coinbase onramp).

Start here: `docs/WIDGET_INTEGRATION_GUIDE.md`

## 2) Query trust scores (wallet screening)

Use the Trust Oracle to screen wallets for:
- airdrops / whitelists
- raid rewards (anti-farm)
- partner due diligence

API reference: `docs/API.md`

Example:

```bash
curl "https://bonzi-v5.onrender.com/api/trust/0xYOUR_WALLET"
```

## 3) ERC-8004 agent discovery

To index or verify SIAH in registries/crawlers:

- `/.well-known/agent.json`
- `/.well-known/agent-card.json`

Repo reference card: `.well-known/agent-card.json`

## 4) Agent-to-agent (A2A) usage

If you’re an AI agent integrating with SIAH:

- Use the Trust Oracle endpoints to query reputation before actions.
- Use `/api/tip` to send A2A tips for verified helpful behavior.

If agent auth is enabled server-side, include `X-Agent-*` headers (signature + nonce + timestamp).

## 5) Self-hosting

This repo is a static site. You can host it anywhere (GitHub Pages, Netlify, S3).

The hosted backend (API, bot, oracle logic) is maintained in `Bonzi_v5`.

