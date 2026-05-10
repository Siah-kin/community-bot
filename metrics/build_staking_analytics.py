#!/usr/bin/env python3
"""
Build metrics/staking_analytics.json — public-facing only (safe to GitHub Pages).

Reads:
  - Ethereum mainnet JSON-RPC (no key required; uses resilient URL list).
  - Optional CoinGecko contract price + ETH price (no key).
  - metrics-data.json bonzi aggregate (typically from Dune via fetch_metrics.py).

Never writes secrets. API keys for DUNE_ETHERSCAN stay in operator .env when extending.

Usage:
  python3 build_staking_analytics.py
  python3 build_staking_analytics.py --metrics-path metrics-data.json --out staking_analytics.json
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Hard facts (immutable for this analytics surface — validator enforces canonical router casing)
CHAIN_ID = 1
TOKEN = "0xd6175692026bcd7cb12a515e39cf0256ef35cb86"
HARDSTAKE = "0x3618158bb8d07111e476f4de28676dff050d1a53"
FACTORY = "0x9a27cb5ae0B2cEe0bb71f9A85C0D60f3920757B4"
ROUTER_EXPECTED_CANONICAL = "0x9bD63C5D44fF28390df1EaaFD4eB4BD73E94A72a"

# Verified keccak selectors (Ethereum)
# Ethervista HARDSTAKE template: pool aggregate is public `totalSupply` (not ERC20 — staked wei).
# Fallback: some deployments may expose `totalStaked(address)`.
SEL_TOTAL_SUPPLY = "0x18160ddd"  # totalSupply()
SEL_TOTAL_STAKED_ADDRESS = (
    "0x9bfd8d61" + TOKEN[2:].lower().rjust(64, "0")
)  # totalStaked(address) — optional
SEL_ROUTER = "0xf887ea40"  # router()

DEFAULT_RPC_URLS = (
    "https://eth.drpc.org",
    "https://rpc.ankr.com/eth",
    "https://eth.llamarpc.com",
    "https://cloudflare-eth.com",
)


def _rpc_call(rpc_url: str, to: str, data: str, timeout: int = 20) -> str:
    """Return raw 0x-prefixed hex result or raise."""
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": to, "data": data}, "latest"],
        }
    ).encode()
    req = Request(
        rpc_url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "bonzi-staking-analytics/1"},
        method="POST",
    )
    with urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode())
    if body.get("error"):
        raise RuntimeError(str(body["error"]))
    result = body.get("result")
    if not result or not isinstance(result, str):
        raise RuntimeError("Invalid eth_call result")
    return result


def _hex_to_int(h: str) -> int:
    return int(h, 16)


def _pick_working_rpc(urls: list[str]) -> str:
    for u in urls:
        try:
            payload = json.dumps(
                {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}
            ).encode()
            req = Request(
                u,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "bonzi-staking-analytics/1"},
                method="POST",
            )
            with urlopen(req, timeout=12) as resp:
                body = json.loads(resp.read().decode())
            if body.get("result"):
                return u
        except (OSError, HTTPError, URLError, ValueError, RuntimeError):
            continue
    return urls[0]


def _http_get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": "bonzi-staking-analytics/1"}, method="GET")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _fetch_coingecko_prices() -> tuple[float | None, float | None]:
    """(bonzi_usd, eth_usd) from CoinGecko simple token price by contract."""
    eth_usd: float | None = None
    bonzi_usd: float | None = None
    try:
        j = _http_get_json(
            "https://api.coingecko.com/api/v3/simple/price"
            "?ids=ethereum&vs_currencies=usd"
        )
        eth_usd = float(j.get("ethereum", {}).get("usd") or 0) or None
    except (OSError, ValueError, TypeError, KeyError):
        pass
    try:
        j2 = _http_get_json(
            "https://api.coingecko.com/api/v3/simple/token_price/ethereum"
            f"?contract_addresses={TOKEN}&vs_currencies=usd"
        )
        row = j2.get(TOKEN.lower()) or j2.get(TOKEN)
        if row:
            bonzi_usd = float(row.get("usd") or 0) or None
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return bonzi_usd, eth_usd
def build_payload(
    metrics_bonzi: dict[str, Any] | None,
    rpc_urls: list[str],
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    generated_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    snapshot_date = now.strftime("%Y-%m-%d")

    rpc = _pick_working_rpc(rpc_urls)
    pool_total_method = "hardstake_totalSupply"
    try:
        staked_hex = _rpc_call(rpc, HARDSTAKE, SEL_TOTAL_SUPPLY)
    except RuntimeError:
        pool_total_method = "totalStaked_token"
        staked_hex = _rpc_call(rpc, HARDSTAKE, SEL_TOTAL_STAKED_ADDRESS)
    router_hex = _rpc_call(rpc, FACTORY, SEL_ROUTER)
    supply_hex = _rpc_call(rpc, TOKEN, SEL_TOTAL_SUPPLY)
    supply_wei = _hex_to_int(supply_hex)
    staked_wei = _hex_to_int(staked_hex)
    router_live = ("0x" + router_hex[-40:]).lower()
    expected_lower = ROUTER_EXPECTED_CANONICAL.lower()

    locked_pct = 0.0
    if supply_wei > 0:
        locked_pct = 100.0 * (staked_wei / supply_wei)

    decimals = 10**18
    supply_tokens = supply_wei / decimals
    staked_tokens = staked_wei / decimals

    bonzi_usd, eth_usd = _fetch_coingecko_prices()
    mb = metrics_bonzi or {}
    total_eth_claimed = mb.get("total_eth_distributed")
    unique_claimers = mb.get("unique_claimers")
    currently_staking = mb.get("currently_staking")

    tvl_proxy_usd: float | None = None
    if bonzi_usd:
        tvl_proxy_usd = round(staked_tokens * bonzi_usd, 2)

    total_eth_claimed_f: float | None = None
    if total_eth_claimed is not None:
        try:
            total_eth_claimed_f = float(total_eth_claimed)
        except (TypeError, ValueError):
            total_eth_claimed_f = None

    launch = mb.get("launch_date")
    pool_age_days: int | None = None
    if launch:
        try:
            ld = datetime.strptime(str(launch)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            pool_age_days = max(1, (now - ld).days)
        except ValueError:
            pool_age_days = None

    annualized_yield_estimate_pct: float | None = None
    if (
        eth_usd
        and tvl_proxy_usd
        and tvl_proxy_usd > 0
        and total_eth_claimed_f is not None
        and pool_age_days
        and pool_age_days > 7
    ):
        rewarded_usd = total_eth_claimed_f * eth_usd
        years = pool_age_days / 365.0
        if years > 0:
            # Pool-aggregate illustrative: cumulative rewards USD / proxy TVL USD / years
            annualized_yield_estimate_pct = round((rewarded_usd / tvl_proxy_usd) / years * 100, 4)

    bonzi_qty_1000: float | None = None
    if bonzi_usd and bonzi_usd > 0:
        bonzi_qty_1000 = round(1000.0 / bonzi_usd, 8)

    reward_to_tvl_lifetime_raw: float | None = None
    if eth_usd and tvl_proxy_usd and tvl_proxy_usd > 0 and total_eth_claimed_f is not None:
        reward_usd = total_eth_claimed_f * eth_usd
        reward_to_tvl_lifetime_raw = round(reward_usd / tvl_proxy_usd, 6)

    top_stakers: list[dict[str, Any]] = []
    stakers_src = "none"
    top_earners: list[dict[str, Any]] = []
    earn_src = "pending_dune"

    benchmarks = [
        {
            "id": "eth_staking_ref",
            "label": "Ethereum L1 staking APR (widely cited reference)",
            "typical_yield_apr_approx_pct_low": 2.5,
            "typical_yield_apr_approx_pct_high": 5.5,
            "note_public": (
                "Public reference bands only; contemporaneous staking yield varies "
                "(protocol + operator). Not a projection of Bonzi payouts."
            ),
        },
        {
            "id": "defi_lending_band",
            "label": "DeFi ETH yield (very broad illustrative band)",
            "typical_yield_apr_approx_pct_low": 1.5,
            "typical_yield_apr_approx_pct_high": 25.0,
            "note_public": (
                "Large variance by venue, tenor, collateral, and risk. Included as "
                "context only—not a comparator to realized Bonzi hardstake flow."
            ),
        },
    ]

    vista_metrics = mb.get("_vista_eth_distributed")
    # caller may attach vista_eth on merge
    if vista_metrics is not None:
        try:
            benchmarks.append(
                {
                    "id": "vista_hardstake_aggregate",
                    "label": "VISTA aggregate hardstake ETH distributed (metrics-data)",
                    "total_eth_distributed_snapshot": float(vista_metrics),
                    "note_public": (
                        "Off-chain analytic aggregate from curated metrics hub; snapshot date "
                        f"outside this object—see metrics-data.json.updated"
                    ),
                }
            )
        except (TypeError, ValueError):
            pass

    return {
        "schema_version": 1,
        "generated_at_utc": generated_iso,
        "snapshot_date": snapshot_date,
        "chain_id": CHAIN_ID,
        "access_model": "public_json_only",
        "contracts": {
            "bonzi_token": TOKEN.lower(),
            "bonzi_hardstake": HARDSTAKE.lower(),
            "factory": FACTORY.lower(),
            "router_expected_canonical": ROUTER_EXPECTED_CANONICAL,
            "router_read_from_factory": router_live.lower(),
            "factory_router_equals_expected": router_live.lower() == expected_lower,
        },
        "onchain_live": {
            "rpc_primary_used": rpc,
            "pool_aggregate_read_method": pool_total_method,
            "total_supply_tokens": supply_tokens,
            "pool_total_staked_tokens": staked_tokens,
            "locked_percent_of_supply_rounded": round(locked_pct, 6),
        },
        "market_prices_optional": {
            "bonzi_usd": bonzi_usd,
            "eth_usd": eth_usd,
            "price_source_public": "coingecko_simple_api",
            "snapshot_note": (
                "CoinGecko snapshots are indicative; oracle pricing for execution may "
                "differ. Used only for illustrative USD denominators."
            ),
        },
        "aggregate_claims_optional": {
            "total_eth_distributed_aggregate": total_eth_claimed_f,
            "unique_claimers": unique_claimers,
            "currently_staking_wallets_aggregate": currently_staking,
            "source": "metrics_data_json_bonzi_slice_dune_derived",
        },
        "leaderboards": {
            "top_stakers_by_amount": top_stakers,
            "top_stakers_source": stakers_src,
            "top_eth_earners_lifetime": top_earners,
            "top_eth_earners_source": earn_src,
            "leaderboard_truncation_notice": (
                "When populated, explorer links truncate display; addresses are lowercase "
                "0x hex. No private wallets—public chain only."
            ),
        },
        "roi_pool_aggregate_illustrative": {
            "snapshot_datetime_utc": generated_iso,
            "usd_notional": 1000,
            "bonzi_units_representing_1000_usd": bonzi_qty_1000,
            "historical_aggregate_label": (
                "Cumulative ETH paid to claiming stakers vs rough TVL proxy (live locks × CoinGecko BONZI). "
                "Not your personal IRR. Does not imply future returns."
            ),
            "tvl_proxy_usd": tvl_proxy_usd,
            "lifetime_reward_usd_vs_tvl_proxy": reward_to_tvl_lifetime_raw,
            "pool_age_days_est": pool_age_days,
            "annualized_pool_reward_yield_estimate_pct": annualized_yield_estimate_pct,
            "realized_vs_estimated_clarifier": (
                "realized_aggregate = summed claims from indexer (Dune) in metrics slice; "
                "annualized estimate = (realized_reward_usd / tvl_proxy_usd) prorated "
                "to one year via pool_age_days_est."
            ),
        },
        "benchmarks_illustrative": benchmarks,
        "methodology_public": (
            "On-chain pool total uses HARDSTAKE.totalSupply() per Ethervista HARDSTAKE template; "
            "BONZI denominator uses token totalSupply(). Fallback: totalStaked(BONZI) if deployed with that view. "
            "Regenerated by metrics/build_staking_analytics.py. Dune aggregates only as fresh as metrics-data.json. "
            "Run metrics/validate_staking_analytics.py before publishing."
        ),
    }


def write_staking_analytics_json(
    metrics_json_path: Path,
    output_path: Path,
    rpc_urls: list[str] | None = None,
) -> dict[str, Any]:
    bonzi_slice: dict[str, Any] = {}
    vista_eth = None
    if metrics_json_path.is_file():
        with open(metrics_json_path, encoding="utf-8") as f:
            md = json.load(f)
            bonzi_slice = md.get("bonzi") or {}
            vista_eth = md.get("vista", {}).get("total_eth_distributed")
            bonzi_slice = dict(bonzi_slice)
            bonzi_slice["_vista_eth_distributed"] = vista_eth
    urls = rpc_urls or list(DEFAULT_RPC_URLS)
    extra = os.environ.get("STAKING_RPC_URLS")
    if extra:
        urls = [u.strip() for u in extra.split(",") if u.strip()] + urls

    payload = build_payload(metrics_bonzi=bonzi_slice, rpc_urls=urls)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=False)
        f.write("\n")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--metrics-path",
        default=str(Path(__file__).resolve().parent / "metrics-data.json"),
        help="metrics-data.json (bonzi vista slices)",
    )
    ap.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent / "staking_analytics.json"),
        help="Public output path",
    )
    args = ap.parse_args()

    outp = Path(args.out)
    p = write_staking_analytics_json(Path(args.metrics_path), outp)
    eq = p["contracts"].get("factory_router_equals_expected")
    print(f"Wrote {outp}")
    print(f"  factory_router_equals_expected: {eq}")
    print(f"  locked_percent_of_supply_rounded: {p['onchain_live']['locked_percent_of_supply_rounded']}")


if __name__ == "__main__":
    main()
