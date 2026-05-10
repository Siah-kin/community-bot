#!/usr/bin/env python3
"""
Validate public staking_analytics.json before GitHub Pages publish.

Checks:
  - Canonical router equality (factory read vs expected literal)
  - snapshot / generated timestamps present
  - No obvious secret blobs in serialized JSON (Dune/Etherscan key patterns)
  - Optional staleness ceiling on generated_at_utc (--freshness-hours)

Exit 1 on violation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROUTER_EXPECTED = "0x9bD63C5D44fF28390df1EaaFD4eB4BD73E94A72a"

_SECRET_PATTERNS = [
    re.compile(r"dune.?api.?key\s*[=:]", re.I),
    re.compile(r"x-dune-api-key", re.I),
    re.compile(r"etherscan.?api.?key\s*[=:]", re.I),
    re.compile(r"rnd_[a-zA-Z0-9_]{16,}", re.I),
    re.compile(r"sk_live_[a-zA-Z0-9]{16,}", re.I),
]


def validate_file(
    path: Path,
    *,
    freshness_hours: float | None,
    allow_leaderboard_empty: bool,
) -> list[str]:
    errors: list[str] = []
    raw = path.read_text(encoding="utf-8")

    if any(p.search(raw) for p in _SECRET_PATTERNS):
        errors.append(
            "Secret-like pattern detected in JSON text (blocked). "
            "Remove API key material — public artifact only."
        )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    gen = data.get("generated_at_utc")
    if not gen or not isinstance(gen, str):
        errors.append("Missing generated_at_utc (ISO string required).")

    snap = data.get("snapshot_date")
    if not snap or not isinstance(snap, str):
        errors.append("Missing snapshot_date (YYYY-MM-DD).")

    c = data.get("contracts") or {}
    rd = (
        isinstance(c.get("router_read_from_factory"), str)
        and c["router_read_from_factory"].strip().lower().replace(" ", "")
    )
    ex = ROUTER_EXPECTED.lower()
    expected_field = (
        isinstance(c.get("router_expected_canonical"), str)
        and c["router_expected_canonical"].strip().lower() == ex
    )
    if rd != ex:
        errors.append(
            f"Router mismatch: router_read_from_factory={c.get('router_read_from_factory')} "
            f"expected {ROUTER_EXPECTED}"
        )
    if not expected_field:
        errors.append("router_expected_canonical must equal canonical ROUTER_EXPECTED.")

    if not bool(c.get("factory_router_equals_expected")):
        errors.append("factory_router_equals_expected must be True.")

    lc = data.get("onchain_live") or {}
    if lc.get("locked_percent_of_supply_rounded") is None:
        errors.append("onchain_live.locked_percent_of_supply_rounded is required.")

    if freshness_hours is not None and gen:
        try:
            # Accept ...Z suffix
            g_clean = gen.replace("Z", "+00:00")
            gt = datetime.fromisoformat(g_clean)
            if gt.tzinfo is None:
                gt = gt.replace(tzinfo=timezone.utc)
            age_h = (datetime.now(timezone.utc) - gt).total_seconds() / 3600.0
            if age_h > freshness_hours:
                errors.append(
                    f"Stale: generated_at_utc age {age_h:.2f}h exceeds --freshness-hours {freshness_hours}"
                )
        except ValueError:
            errors.append("generated_at_utc not parseable as ISO8601.")

    roi = data.get("roi_pool_aggregate_illustrative") or {}
    if not roi.get("snapshot_datetime_utc"):
        errors.append(
            "roi_pool_aggregate_illustrative.snapshot_datetime_utc required (paired methodology snapshot)."
        )
    if roi.get("realized_vs_estimated_clarifier") is None or roi.get(
        "historical_aggregate_label"
    ) is None:
        errors.append(
            "ROI section must expose historical_aggregate_label and realized_vs_estimated_clarifier."
        )

    lb = data.get("leaderboards") or {}
    stakers_empty = len(lb.get("top_stakers_by_amount") or []) == 0
    earners_empty = len(lb.get("top_eth_earners_lifetime") or []) == 0
    if stakers_empty and earners_empty and not allow_leaderboard_empty:
        errors.append(
            "Leaderboards empty — pass --allow-empty-leaderboards for CI until "
            "Dune/Etherscan population is wired, or regenerate after pipeline fills rows."
        )

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path, nargs="?", default=Path(__file__).parent / "staking_analytics.json")
    ap.add_argument(
        "--freshness-hours",
        type=float,
        default=None,
        help="Fail if older than N hours (omit for CI leniency)",
    )
    ap.add_argument(
        "--allow-empty-leaderboards",
        action="store_true",
        help="Permit empty top_stakers / top_eth_earners (pre-Dune ingest)",
    )
    args = ap.parse_args()
    errs = validate_file(
        args.path.resolve(),
        freshness_hours=args.freshness_hours,
        allow_leaderboard_empty=args.allow_empty_leaderboards,
    )
    if errs:
        print(f"staking_analytics validation FAIL: {args.path}", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"staking_analytics OK: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
