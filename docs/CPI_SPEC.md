# CPI-253 (Combined Progression Index) Spec

**CPI-253** is a 10‑dimension scoring framework (253 points max) used by SIAH to report trust/quality in a standardized format.

## Dimensions (max points)

- **D1 — Cult Metrics** (25): community depth & non-price engagement
- **D2 — On-Chain Forensics** (25): wallet analysis, tips, liquidity signals
- **D3 — Lunarpunk** (25): decentralization, sybil resistance
- **D4 — ERC‑8004 Technical** (25): registry integration, agent card, TEE posture
- **D5 — Ostrom Commons** (25): governance + cooperation dynamics
- **D6 — Antifragility** (25): stress response, redundancy, modularity
- **D7 — Economic Antifragility** (25): revenue diversity, runway independence
- **D8 — Business Antifragility** (25): optionality, learning rate, skin‑in‑the‑game
- **D9 — Security Posture** (28): audits, fail‑closed defaults, PQC readiness
- **D10 — Closed‑Loop Integrity** (25): regenerative economics (real yield, obligations-first)

## Tiers (total points)

- **S:** 203–253 (80%+)
- **A:** 152–202 (60–80%)
- **B:** 101–151 (40–60%)
- **C:** 51–100 (20–40%)
- **F:** 0–50 (<20%)

## Notes

- CPI is reported as a **dimension breakdown** + **total score**.
- Missing signals map to **neutral** defaults until coverage improves.

Implementation reference: `Bonzi_v5/src/systems/trust/multi_oracle/cpi_mapping.py`

