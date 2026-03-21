# API Reference (Bonzi)

This repository is a static site; the live API is hosted separately.

**Base URL (hosted):** `https://bonzi-v5.onrender.com`

## Health

- `GET /healthz` → `{ "status": "ok", "service": "bonzi-platform" }`
- `GET /health` → same

## Well-known (agent discovery)

- `GET /.well-known/agent.json` (A2A discovery)
- `GET /.well-known/agent-card.json` (ERC-8004)

Both return the current agent card JSON.

## Trust Oracle

### Get trust by wallet

- `GET /api/trust/{wallet}`

Example:

```bash
curl "https://bonzi-v5.onrender.com/api/trust/0xYOUR_WALLET"
```

### Get trust by Telegram user id

- `GET /api/trust/user/{user_id}`

### Get cooperation signals by wallet

- `GET /api/trust/cooperation/{wallet}`

### Multi-oracle composite + CPI reports

- `GET /api/trust/composite/{user_id}`
- `GET /api/trust/cpi/{user_id}`
- `GET /api/trust/explain/{user_id}`

### ERC-8004 status

- `GET /api/trust/erc8004/status`

### Attestations + credits (experimental)

- `POST /api/trust/attest`
- `GET /api/trust/credits/{agent}`
- `GET /api/trust/attestations/{agent}`
- `GET /api/trust/bridge/status`

## A2A tipping

- `POST /api/tip`
- `GET /api/tip/balance/{agent}`
- `GET /api/tip/leaderboard`
- `GET /api/tip/history`
- `POST /api/tip/claim`
- `GET /api/agent/{agent}/vet`

## Contact

- `POST /api/contact`

Body:

```json
{
  "category": "partnership | bugs | proposals",
  "name": "Your name",
  "email": "you@example.com",
  "message": "Your message (10–2000 chars)"
}
```

## Authentication + payments (advanced)

Some endpoints support/require:

- **Agent auth headers:** `X-Agent-ID`, `X-Agent-Signature`, `X-Agent-Timestamp`, `X-Agent-Nonce` (or `X-API-Key`)
- **x402 payments:** when enabled server-side, send `X-Payment-Token` and handle HTTP `402`

For implementation details, see the `Bonzi_v5` backend repository (`src/api/middleware/agent_auth.py`, `src/api/middleware/x402_payment.py`).

