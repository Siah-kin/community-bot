# Link Policy - ENFORCED BY HOOKS

**Last updated:** 2026-02-05

## Canonical Social Links (ONLY THESE)

| Platform | Canonical URL | Usage |
|----------|---------------|-------|
| **Telegram** | `https://t.me/Bonzivista_bot` | All bot/contact links |
| **X** | `https://x.com/Bonzi_vista` | All social/updates links |
| **Ethervista** | `https://www.ethervista.app/how-it-works` | Product/docs links |

## Rules

### 1. NO ALTERNATIVE BOT LINKS
These are **BANNED** (will fail pre-commit):
- `t.me/Bonzi_Community_bot`
- `t.me/BonziVistaBot`
- `t.me/SiahBot`
- `t.me/bonzi_raider_bot`
- `t.me/bonzisiah`
- Any other bot variant

### 2. NO ALTERNATIVE X ACCOUNTS
These are **BANNED** in body content:
- `x.com/ethaboringtoshi`
- `x.com/ethervista`
- `x.com/deabordefiants`

**Exception:** Source references (e.g., MustStopMurad for memecoin criteria) are allowed.

### 3. ETHERVISTA CONSISTENCY
- Use `www.ethervista.app` NOT `ethervista.com`
- Link to `/how-it-works` for general references
- `docs.ethervista.app` → use `/how-it-works` instead

### 4. PARTNER LINKS
Partner links are ONLY allowed in:
- Footer sections
- Explicit "Partners" sections
- Source/reference citations

NOT allowed in:
- CTAs
- Navigation
- Body content

## Why This Matters

1. **Phishing risk** - Multiple bot names confuse users, attackers exploit this
2. **Brand dilution** - Inconsistent links fragment community
3. **SEO/Trust** - Single canonical source builds authority
4. **Maintenance** - One link to update, not 50

## Enforcement

Pre-commit hook at `.claude/hooks/check-links.sh` validates:
- No banned Telegram variants
- No banned X accounts in body
- Consistent Ethervista URLs

**Violations block commit.**
