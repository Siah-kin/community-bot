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

# Bonzi/WETH Univ2-style pair (Ethervista) — ETH/BONZI mid only, not USD.
BONZI_PAIR = "0x970cf9b7346fbaea0588f03356a104100eb675e2".lower()
WETH_MAINNET = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"

SEL_PAIR_TOKEN0 = "0x0dfe1681"  # token0()
SEL_PAIR_TOKEN1 = "0xd21220a7"  # token1()
SEL_PAIR_GET_RESERVES = "0x0902f1ac"  # getReserves()

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

# Public lens: ~1% of 1B supply (supply share != share of staking pool).
REFERENCE_STAKE_BONZI_UNITS = 10_000_000.0


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


def _decode_address_words(result_hex: str) -> str:
    hx = result_hex[2:] if result_hex.startswith("0x") else result_hex
    word = hx[-64:] if len(hx) >= 64 else hx
    return ("0x" + word[-40:]).lower()


def _decode_reserves_two_uints(result_hex: str) -> tuple[int, int]:
    """Abi-encoded reserve0, reserve1 (each 32-byte word)."""
    hx = result_hex[2:] if result_hex.startswith("0x") else result_hex
    if len(hx) < 128:
        raise ValueError("bad getReserves length")
    return int(hx[0:64], 16), int(hx[64:128], 16)


def _pair_implied_eth_per_bonzi_tokens(rpc: str) -> float | None:
    """Rough mid: WETH_reserve / BONZI_reserve (18-decimal floats)."""
    try:
        t0 = _decode_address_words(_rpc_call(rpc, BONZI_PAIR, SEL_PAIR_TOKEN0))
        t1 = _decode_address_words(_rpc_call(rpc, BONZI_PAIR, SEL_PAIR_TOKEN1))
        r0, r1 = _decode_reserves_two_uints(_rpc_call(rpc, BONZI_PAIR, SEL_PAIR_GET_RESERVES))
    except (OSError, RuntimeError, ValueError, IndexError):
        return None
    tok = TOKEN.lower()
    weth_l = WETH_MAINNET.lower()
    if t0 == tok and t1 == weth_l:
        bonzi_wei, eth_wei = r0, r1
    elif t1 == tok and t0 == weth_l:
        bonzi_wei, eth_wei = r1, r0
    else:
        return None
    if bonzi_wei <= 0:
        return None
    return (eth_wei / 10**18) / (bonzi_wei / 10**18)


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

    share_of_live_staking_pool_pct: float | None = None
    reference_vs_pool_note: str | None = None
    if supply_tokens > 0 and staked_tokens > 0:
        raw_share = 100.0 * (REFERENCE_STAKE_BONZI_UNITS / staked_tokens)
        if REFERENCE_STAKE_BONZI_UNITS > staked_tokens:
            reference_vs_pool_note = (
                "Reference exceeds live staking aggregate; pacing below uses the whole pool slice."
            )
            share_of_live_staking_pool_pct = None
        else:
            share_of_live_staking_pool_pct = round(raw_share, 6)

    # Linear historical pace: cumulative claimed ETH / pool age — not forward guidance.
    daily_mean_eth_claimed: float | None = None
    annualized_pool_eth_pace_estimate: float | None = None
    linear_monthly_eth_for_reference_stake: float | None = None
    linear_annual_eth_for_reference_stake: float | None = None
    linear_yield_usd_apr_proxy_on_reference_pct: float | None = None
    linear_monthly_usd_yield_proxy_reference: float | None = None
    if (
        total_eth_claimed_f is not None
        and pool_age_days
        and pool_age_days >= 8
        and staked_tokens > 0
    ):
        daily_mean_eth_claimed = total_eth_claimed_f / float(pool_age_days)
        annualized_pool_eth_pace_estimate = round(daily_mean_eth_claimed * 365.0, 12)
        if REFERENCE_STAKE_BONZI_UNITS <= staked_tokens:
            stake_frac = REFERENCE_STAKE_BONZI_UNITS / staked_tokens
            linear_annual_eth_for_reference_stake = round(
                daily_mean_eth_claimed * 365.0 * stake_frac, 14
            )
            linear_monthly_eth_for_reference_stake = round(
                (linear_annual_eth_for_reference_stake or 0) / 12.0, 14
            )
        else:
            linear_annual_eth_for_reference_stake = annualized_pool_eth_pace_estimate
            linear_monthly_eth_for_reference_stake = round(
                (annualized_pool_eth_pace_estimate or 0) / 12.0, 14
            )
            if reference_vs_pool_note is None:
                reference_vs_pool_note = (
                    "Live pool smaller than reference; pacing uses entire pool disbursement baseline."
                )
        if eth_usd and bonzi_usd and bonzi_usd > 0 and linear_monthly_eth_for_reference_stake:
            principal_usd = REFERENCE_STAKE_BONZI_UNITS * bonzi_usd
            annual_eth = linear_monthly_eth_for_reference_stake * 12.0
            linear_yield_usd_apr_proxy_on_reference_pct = round(
                (annual_eth * eth_usd / principal_usd) * 100.0, 6
            )
            linear_monthly_usd_yield_proxy_reference = round(
                linear_monthly_eth_for_reference_stake * eth_usd, 4
            )

    pool_health_pulse: dict[str, Any] = {
        "router_factory_match_observed": router_live.lower() == expected_lower,
        "bonzi_supply_locked_pct": round(locked_pct, 6),
        "dune_aggregate_currently_staking_wallets_optional": currently_staking,
        "dune_aggregate_unique_claimer_wallets_optional": unique_claimers,
        "concentration_explainer_public": (
            "On explorers, circulating supply sometimes sits behind a modest count of labelled "
            "addresses; wallets here are indexer aggregates and not a census of humans."
        ),
    }

    wallet_lens_illustrative: dict[str, Any] = {
        "reference_bonzi_units": REFERENCE_STAKE_BONZI_UNITS,
        "supply_fraction_pct": round((REFERENCE_STAKE_BONZI_UNITS / supply_tokens) * 100, 8)
        if supply_tokens > 0
        else None,
        "share_of_live_staking_pool_pct": share_of_live_staking_pool_pct,
        "share_method_note_public": reference_vs_pool_note,
        "linearized_eth_yield_note_public": (
            "Straight-line extrapolation from cumulative indexer ETH paid ÷ staking pool age × 365 × "
            "your share of today's pool total — backward pace only; contract math differs from a "
            "savings APR."
        ),
        "daily_mean_eth_claimed_pace_aggregate": daily_mean_eth_claimed,
        "annualized_pool_eth_disburse_pace_estimate": annualized_pool_eth_pace_estimate,
        "annualized_eth_for_reference_stake_linear": linear_annual_eth_for_reference_stake,
        "monthly_eth_for_reference_stake_linear": linear_monthly_eth_for_reference_stake,
        "usd_apr_proxy_pct_on_reference_stake_coin_gecko_optional": linear_yield_usd_apr_proxy_on_reference_pct,
        "usd_monthly_yield_proxy_optional": linear_monthly_usd_yield_proxy_reference,
    }

    eth_per_bonzi_pair_mid: float | None = None
    staking_tvl_eth_proxy_from_pair_mid: float | None = None
    # ETH-mid APR = (backward ETH/year pace) / (locked BONZI × pair-implied ETH per BONZI).
    # When the pair's WETH side is thin vs BONZI reserves, implied ETH/BONZI is tiny and TVL_ETH
    # understates locked value — %-yield blows up without being a fair user APR. Omit from hero.
    TVL_ETH_PROXY_MIN_FOR_PCT_PUBLIC = 10.0
    ETH_PER_BONZI_PAIR_ILLIQUID_BELOW = 1e-7

    annualized_pool_reward_yield_estimate_eth_mid_proxy_pct: float | None = None
    annualized_yield_eth_mid_proxy_pct_computed_optional: float | None = None
    eth_mid_proxy_unreliable_for_hero_pct = False
    eth_mid_proxy_unreliable_public_reason: str | None = None
    try:
        eth_per_bonzi_pair_mid = _pair_implied_eth_per_bonzi_tokens(rpc)
    except (OSError, RuntimeError, ValueError, IndexError, TypeError):
        eth_per_bonzi_pair_mid = None
    if (
        eth_per_bonzi_pair_mid
        and eth_per_bonzi_pair_mid > 0
        and staked_tokens > 0
    ):
        staking_tvl_eth_proxy_from_pair_mid = round(
            staked_tokens * eth_per_bonzi_pair_mid, 12
        )
        if (
            annualized_pool_eth_pace_estimate is not None
            and annualized_pool_eth_pace_estimate >= 0
            and staking_tvl_eth_proxy_from_pair_mid > 0
        ):
            annualized_pool_reward_yield_estimate_eth_mid_proxy_pct = round(
                (
                    float(annualized_pool_eth_pace_estimate)
                    / float(staking_tvl_eth_proxy_from_pair_mid)
                )
                * 100.0,
                6,
            )
            thin_tvl = staking_tvl_eth_proxy_from_pair_mid < TVL_ETH_PROXY_MIN_FOR_PCT_PUBLIC
            thin_pair = eth_per_bonzi_pair_mid < ETH_PER_BONZI_PAIR_ILLIQUID_BELOW
            if thin_tvl or thin_pair:
                annualized_yield_eth_mid_proxy_pct_computed_optional = (
                    annualized_pool_reward_yield_estimate_eth_mid_proxy_pct
                )
                annualized_pool_reward_yield_estimate_eth_mid_proxy_pct = None
                eth_mid_proxy_unreliable_for_hero_pct = True
                eth_mid_proxy_unreliable_public_reason = (
                    "APR percent not shown: the main BONZI/WETH pair has very little WETH next to "
                    "BONZI reserves, so 'ETH value of locked BONZI' from that mid (~"
                    + f"{staking_tvl_eth_proxy_from_pair_mid:.2f}"
                    + " ETH here) is not a fair TVL denominator. Use pool ETH/year pace instead."
                )

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
        "pool_health_pulse_illustrative": pool_health_pulse,
        "wallet_lens_10m_supply_illustrative": wallet_lens_illustrative,
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
            "eth_per_bonzi_pair_reserve_mid": eth_per_bonzi_pair_mid,
            "staking_tvl_eth_proxy_from_pair_mid": staking_tvl_eth_proxy_from_pair_mid,
            "annualized_pool_reward_yield_estimate_eth_mid_proxy_pct": (
                annualized_pool_reward_yield_estimate_eth_mid_proxy_pct
            ),
            "annualized_yield_eth_mid_proxy_pct_computed_optional": (
                annualized_yield_eth_mid_proxy_pct_computed_optional
            ),
            "eth_mid_proxy_unreliable_for_hero_pct": eth_mid_proxy_unreliable_for_hero_pct,
            "eth_mid_proxy_unreliable_public_reason_optional": eth_mid_proxy_unreliable_public_reason,
            "pool_aggregate_eth_reward_pace_per_year_illustrative": annualized_pool_eth_pace_estimate,
            "pool_aggregate_eth_claimed_total_optional": total_eth_claimed_f,
            "eth_mid_apr_method_note_public": (
                "ETH mid from main BONZI/WETH pair reserves; headline % = linear annual ETH paid (indexer/Dune "
                "cumulative ÷ pool age × 365) ÷ ETH notional of locked BONZI implied by pair mid. Thin WETH vs "
                "BONZI in the pair makes that denominator unreliable — we omit the % and show ETH/year pace instead."
            ),
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
