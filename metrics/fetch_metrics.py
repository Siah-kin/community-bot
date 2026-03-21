#!/usr/bin/env python3
"""
Fetch VISTA and BONZI metrics from Dune API + external market context.

Usage:
  python fetch_metrics.py              # Full fetch (Dune + market) - monthly
  python fetch_metrics.py --market-only # Market context only - hourly/daily

Requires: DUNE_API_KEY environment variable (for full fetch)
Market context APIs are free and require no keys.
Never commit API keys. Use .env file or export.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Load from .env if exists
ENV_FILE = Path(__file__).parent / '.env'
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ.setdefault(key, val.strip('"\''))

API_KEY = os.environ.get('DUNE_API_KEY')
BASE_URL = "https://api.dune.com/api/v1/query"

# Validate key format (Dune keys are ~40 chars)
if API_KEY and (len(API_KEY) < 30 or ' ' in API_KEY):
    print("Warning: DUNE_API_KEY looks invalid")
    API_KEY = None

# Dune Query IDs - Update after creating queries in Dune UI
QUERIES = {
    # VISTA (existing)
    'vista_hhi': '6591451',
    'vista_staker_retention': '6591349',
    'vista_diamond_hands': '6591316',
    'vista_weekly_trend': '6591328',
    'vista_tenure': '6591332',
    'vista_1k_holders': '6591686',  # Tier 3: $1K+ Holders
    'vista_eth_distributed': '6591480',
    'vista_lp_distributed': '6591489',
    'vista_all_distributions': '6591567',  # Comprehensive: LP + Hardlock LP + Hardstake
    'vista_nakamoto': '6591646',  # Tier 3: Nakamoto Coefficient

    # BONZI (new - ADD IDs after creating queries)
    'bonzi_lp_distributed': '6591492',
    'bonzi_hhi': '6591469',
    'bonzi_staker_retention': '6591406',
    'bonzi_diamond_hands': '6591411',
    'bonzi_weekly_trend': '6591436',
    'bonzi_tenure': '6591445',
    'bonzi_1k_holders': '6591684',  # Tier 3: $1K+ Holders
    'bonzi_eth_distributed': '6591483',
    'bonzi_nakamoto': '6591678',  # Tier 3: Nakamoto Coefficient
}

# Contract addresses
CONTRACTS = {
    'vista': {
        'token': '0xc9bca88b04581699fab5aa276ccaff7df957cbbf',
        'lp_pair': '0xfdd05552f1377aa488afed744c8024358af02041',
        'hardstake': '0xee5a6f8a55b02689138c195031d09bafdc7d278f',
        'hardlock_lp': '0x9099ef7f34dc1af0d27e49dc5b604bccc03dcb21',
        'launch_date': '2024-09-01',
    },
    'bonzi': {
        'token': '0xd6175692026bcd7cb12a515e39cf0256ef35cb86',
        'lp_pair': '0x970cf9b7346fbaea0588f03356a104100eb675e2',
        'hardstake': '0x3618158bb8d07111e476f4de28676dff050d1a53',
        'launch_date': '2024-12-01',
    },
    # Ethervista Protocol (shared infrastructure)
    'protocol': {
        'router': '0xCEDd366065A146a039B92Db35756ecD7688FCC77',
        'factory': '0x9a27cb5ae0B2cEe0bb71f9A85C0D60f3920757B4',
        'token_factory': '0x1a97A037A120Db530dDCe8370e24EaD0FE9cf5d0',
        'hardlock_universal': '0xF6B510928ab880507246CD6946b7F061Eb8A9C78',
        'autobuy_burner': '0xe17A0C382c8332A889EC9D026D6948e26C7f617D',
    }
}

# Function selectors
STAKE_METHOD = "0x666da64f"
UNSTAKE_METHOD = "0x2e1a7d4d"


def fetch_query(query_id: str, retries: int = 3) -> list:
    """Fetch results from a Dune query with retry logic."""
    if not query_id:
        return []

    url = f"{BASE_URL}/{query_id}/results"
    headers = {"x-dune-api-key": API_KEY}

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 401:
                print("  Error: Invalid API key")
                return []
            if response.status_code == 429:
                print(f"  Rate limited, waiting... (attempt {attempt + 1})")
                import time
                time.sleep(5 * (attempt + 1))
                continue

            response.raise_for_status()
            data = response.json()
            return data.get('result', {}).get('rows', [])

        except requests.exceptions.Timeout:
            print(f"  Timeout (attempt {attempt + 1}/{retries})")
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
            break

    return []


def fetch_token_metrics(token: str, queries: dict) -> dict:
    """Fetch all metrics for a single token."""
    prefix = token.lower()
    launch = CONTRACTS[token]['launch_date']

    metrics = {
        'token_address': CONTRACTS[token]['token'],
        'hardstake_address': CONTRACTS[token].get('hardstake'),
        'launch_date': launch,
        'token_age_months': calculate_age_months(launch),
        'total_holders': None,
        'top_10_pct': None,
        'hhi_score': None,
        'total_stakers': None,
        'diamond_hands': None,
        'diamond_hands_pct': None,
        'currently_staking': None,
        'retention_pct': None,
        'avg_tenure_days': None,
        'max_tenure_days': None,
        'holders_1k_plus': None,
        'holders_10k_plus': None,
        'weekly_trend': [],
        'net_flow_7d': None,
        'total_eth_distributed': None,
        'unique_claimers': None,
        'avg_claim_eth': None,
        'max_single_claim': None,
        # LP distributions (separate from Hardstake)
        'lp_total_eth': None,
        'lp_total_distributions': None,
        'lp_unique_recipients': None,
        # Tier 3 metrics
        'nakamoto_coefficient': None,
    }

    # Fetch HHI
    if queries.get(f'{prefix}_hhi'):
        try:
            rows = fetch_query(queries[f'{prefix}_hhi'])
            if rows:
                row = rows[0]
                metrics['hhi_score'] = row.get('hhi_score')
                metrics['top_10_pct'] = row.get('top_10_pct')
                metrics['total_holders'] = row.get('total_holders')
                print(f"  {token} HHI: {row.get('hhi_score')}")
        except Exception as e:
            print(f"  Error fetching {token} HHI: {e}")

    # Fetch staker retention
    if queries.get(f'{prefix}_staker_retention'):
        try:
            rows = fetch_query(queries[f'{prefix}_staker_retention'])
            staking = 0
            exited = 0
            for row in rows:
                if row.get('action') == 'staking':
                    staking = row.get('wallets', 0)
                elif row.get('action') == 'exited':
                    exited = row.get('wallets', 0)
            total = staking + exited
            if total > 0:
                metrics['currently_staking'] = staking
                metrics['total_stakers'] = total
                metrics['retention_pct'] = round(100 * staking / total, 1)
                print(f"  {token} Retention: {staking}/{total} ({metrics['retention_pct']}%)")
        except Exception as e:
            print(f"  Error fetching {token} retention: {e}")

    # Fetch diamond hands
    if queries.get(f'{prefix}_diamond_hands'):
        try:
            rows = fetch_query(queries[f'{prefix}_diamond_hands'])
            if rows:
                metrics['diamond_hands'] = rows[0].get('diamond_hands')
                print(f"  {token} Diamond hands: {rows[0].get('diamond_hands')}")
        except Exception as e:
            print(f"  Error fetching {token} diamond hands: {e}")

    # Fetch tenure
    if queries.get(f'{prefix}_tenure'):
        try:
            rows = fetch_query(queries[f'{prefix}_tenure'])
            if rows:
                row = rows[0]
                metrics['avg_tenure_days'] = round(row.get('avg_tenure_days', 0))
                metrics['max_tenure_days'] = row.get('max_tenure_days')
                print(f"  {token} Avg tenure: {metrics['avg_tenure_days']} days")
        except Exception as e:
            print(f"  Error fetching {token} tenure: {e}")

    # Fetch weekly trend
    if queries.get(f'{prefix}_weekly_trend'):
        try:
            rows = fetch_query(queries[f'{prefix}_weekly_trend'])
            trend = []
            for row in rows[:12]:  # Last 12 weeks
                trend.append({
                    "week": row.get('week', '')[:10],
                    "stakes": row.get('stakes', 0),
                    "unstakes": row.get('unstakes', 0)
                })
            metrics['weekly_trend'] = trend
            if trend:
                latest = trend[0]
                metrics['net_flow_7d'] = latest['stakes'] - latest['unstakes']
            print(f"  {token} Weekly trend: {len(trend)} weeks")
        except Exception as e:
            print(f"  Error fetching {token} weekly trend: {e}")

    # Fetch $1K+ holders
    if queries.get(f'{prefix}_1k_holders'):
        try:
            rows = fetch_query(queries[f'{prefix}_1k_holders'])
            if rows:
                row = rows[0]
                metrics['holders_1k_plus'] = row.get('holders_1k_plus')
                metrics['holders_10k_plus'] = row.get('holders_10k_plus')
                if not metrics['total_holders']:
                    metrics['total_holders'] = row.get('total_holders')
                print(f"  {token} $1K+ holders: {row.get('holders_1k_plus')}")
        except Exception as e:
            print(f"  Error fetching {token} 1K holders: {e}")

    # Fetch ETH distributed
    if queries.get(f'{prefix}_eth_distributed'):
        try:
            rows = fetch_query(queries[f'{prefix}_eth_distributed'])
            if rows:
                row = rows[0]
                metrics['total_eth_distributed'] = row.get('total_eth_distributed')
                metrics['unique_claimers'] = row.get('unique_claimers')
                metrics['avg_claim_eth'] = row.get('avg_claim_eth')
                metrics['max_single_claim'] = row.get('max_single_claim')
                print(f"  {token} ETH distributed: {row.get('total_eth_distributed')} ETH to {row.get('unique_claimers')} claimers")
        except Exception as e:
            print(f"  Error fetching {token} ETH distributed: {e}")

    # Fetch LP distributions (separate from Hardstake claims)
    if queries.get(f'{prefix}_lp_distributed'):
        try:
            rows = fetch_query(queries[f'{prefix}_lp_distributed'])
            if rows:
                row = rows[0]
                metrics['lp_total_eth'] = row.get('total_eth_distributed') or row.get('total_eth')
                metrics['lp_total_distributions'] = row.get('total_distributions') or row.get('distribution_count')
                metrics['lp_unique_recipients'] = row.get('unique_recipients') or row.get('unique_lps')
                print(f"  {token} LP distributed: {metrics['lp_total_eth']} ETH across {metrics['lp_total_distributions']} distributions")
        except Exception as e:
            print(f"  Error fetching {token} LP distributions: {e}")

    # Fetch Nakamoto Coefficient (Tier 3)
    if queries.get(f'{prefix}_nakamoto'):
        try:
            rows = fetch_query(queries[f'{prefix}_nakamoto'])
            if rows:
                row = rows[0]
                metrics['nakamoto_coefficient'] = row.get('nakamoto_coefficient')
                print(f"  {token} Nakamoto coefficient: {row.get('nakamoto_coefficient')} wallets control 51%")
        except Exception as e:
            print(f"  Error fetching {token} Nakamoto coefficient: {e}")

    # Calculate diamond hands percentage
    if metrics['diamond_hands'] and metrics['total_stakers']:
        metrics['diamond_hands_pct'] = round(
            100 * metrics['diamond_hands'] / metrics['total_stakers'], 1
        )

    return metrics


def calculate_age_months(launch_date: str) -> int:
    """Calculate token age in months from launch date."""
    try:
        launch = datetime.strptime(launch_date, "%Y-%m-%d")
        now = datetime.now()
        months = (now.year - launch.year) * 12 + (now.month - launch.month)
        return max(0, months)
    except:
        return 0


# =============================================================================
# EXTERNAL MARKET DATA (No API keys required)
# =============================================================================

def fetch_eth_price() -> dict:
    """Fetch ETH price and 24h change from CoinGecko."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "ethereum",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        eth = data.get("ethereum", {})
        return {
            "price_usd": eth.get("usd"),
            "change_24h_pct": round(eth.get("usd_24h_change", 0), 2)
        }
    except Exception as e:
        print(f"  Error fetching ETH price: {e}")
        return {"price_usd": None, "change_24h_pct": None}


def fetch_gas_price() -> dict:
    """Fetch current gas price from public API."""
    try:
        # Using Etherscan public gas oracle (no key needed for basic)
        url = "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", {})

        # Handle rate limit / error response (result is string instead of dict)
        if not isinstance(result, dict):
            print(f"  Gas API returned: {result}")
            return {"safe_gwei": None, "standard_gwei": None, "fast_gwei": None, "level": None}

        safe = int(result.get("SafeGasPrice", 0))
        standard = int(result.get("ProposeGasPrice", 0))
        fast = int(result.get("FastGasPrice", 0))

        # Determine gas level
        if standard <= 15:
            level = "low"
        elif standard <= 40:
            level = "medium"
        else:
            level = "high"

        return {
            "safe_gwei": safe,
            "standard_gwei": standard,
            "fast_gwei": fast,
            "level": level,
            "impact": "Low gas = more trades = more fees" if level == "low" else
                     "High gas = fewer trades = reduced fee generation" if level == "high" else
                     "Normal trading activity expected"
        }
    except Exception as e:
        print(f"  Error fetching gas price: {e}")
        return {"safe_gwei": None, "standard_gwei": None, "fast_gwei": None, "level": None}


def fetch_dex_volume() -> dict:
    """Fetch DEX volume from DeFiLlama."""
    try:
        url = "https://api.llama.fi/overview/dexs?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        total_24h = data.get("total24h", 0)
        change_1d = data.get("change_1d", 0)

        # Determine market sentiment
        if total_24h > 5_000_000_000:  # $5B+
            sentiment = "very_active"
        elif total_24h > 2_000_000_000:  # $2B+
            sentiment = "active"
        elif total_24h > 1_000_000_000:  # $1B+
            sentiment = "normal"
        else:
            sentiment = "quiet"

        return {
            "volume_24h_usd": round(total_24h, 0),
            "volume_24h_formatted": f"${total_24h/1e9:.2f}B",
            "change_1d_pct": round(change_1d, 2),
            "sentiment": sentiment,
            "impact": "High DEX activity = favorable for Ethervista fees"
        }
    except Exception as e:
        print(f"  Error fetching DEX volume: {e}")
        return {"volume_24h_usd": None, "sentiment": None}


def fetch_memecoin_sector() -> dict:
    """Fetch top memecoin prices to gauge sector health."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "pepe,shiba-inu,dogecoin,floki,bonk",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Calculate average sector change
        changes = []
        coins = {}
        for coin_id, values in data.items():
            change = values.get("usd_24h_change", 0)
            changes.append(change)
            coins[coin_id] = {
                "price_usd": values.get("usd"),
                "change_24h_pct": round(change, 2)
            }

        avg_change = sum(changes) / len(changes) if changes else 0

        # Determine sector sentiment
        if avg_change > 5:
            sentiment = "bullish"
        elif avg_change > 0:
            sentiment = "positive"
        elif avg_change > -5:
            sentiment = "neutral"
        else:
            sentiment = "bearish"

        return {
            "coins": coins,
            "sector_avg_change_24h": round(avg_change, 2),
            "sentiment": sentiment,
            "impact": "Memecoin sector strength = tailwind for VISTA/BONZI"
        }
    except Exception as e:
        print(f"  Error fetching memecoin sector: {e}")
        return {"coins": {}, "sentiment": None}


def fetch_btc_dominance() -> dict:
    """Fetch BTC dominance to gauge alt season potential."""
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", {})

        btc_dom = data.get("market_cap_percentage", {}).get("btc", 0)
        eth_dom = data.get("market_cap_percentage", {}).get("eth", 0)

        # Alt season typically when BTC dominance < 50%
        if btc_dom < 45:
            season = "alt_season"
        elif btc_dom < 55:
            season = "mixed"
        else:
            season = "btc_dominant"

        return {
            "btc_dominance_pct": round(btc_dom, 2),
            "eth_dominance_pct": round(eth_dom, 2),
            "season": season,
            "impact": "Alt season = more interest in smaller caps like VISTA/BONZI"
        }
    except Exception as e:
        print(f"  Error fetching BTC dominance: {e}")
        return {"btc_dominance_pct": None, "season": None}


def fetch_market_context() -> dict:
    """Fetch all external market data."""
    print("\n=== MARKET CONTEXT ===")

    context = {
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        "eth": fetch_eth_price(),
        "gas": fetch_gas_price(),
        "dex_volume": fetch_dex_volume(),
        "memecoin_sector": fetch_memecoin_sector(),
        "btc_dominance": fetch_btc_dominance(),
    }

    # Generate overall signal
    signals = []

    # Gas signal
    if context["gas"].get("level") == "low":
        signals.append("✅ Low gas: favorable for trading activity")
    elif context["gas"].get("level") == "high":
        signals.append("⚠️ High gas: may reduce trading volume")

    # DEX volume signal
    if context["dex_volume"].get("sentiment") in ["very_active", "active"]:
        signals.append("✅ DEX activity high: good for fee generation")
    elif context["dex_volume"].get("sentiment") == "quiet":
        signals.append("⚠️ DEX activity low: reduced fee potential")

    # Memecoin sector signal
    if context["memecoin_sector"].get("sentiment") in ["bullish", "positive"]:
        signals.append("✅ Memecoin sector strong: tailwind for VISTA/BONZI")
    elif context["memecoin_sector"].get("sentiment") == "bearish":
        signals.append("⚠️ Memecoin sector weak: headwind for sentiment")

    # BTC dominance signal
    if context["btc_dominance"].get("season") == "alt_season":
        signals.append("✅ Alt season: favorable for smaller caps")
    elif context["btc_dominance"].get("season") == "btc_dominant":
        signals.append("⚠️ BTC dominant: capital concentrated in Bitcoin")

    context["signals"] = signals

    print(f"  ETH: ${context['eth'].get('price_usd')} ({context['eth'].get('change_24h_pct')}%)")
    print(f"  Gas: {context['gas'].get('standard_gwei')} gwei ({context['gas'].get('level')})")
    print(f"  DEX Vol: {context['dex_volume'].get('volume_24h_formatted')}")
    print(f"  Memecoin sector: {context['memecoin_sector'].get('sentiment')}")
    print(f"  BTC dominance: {context['btc_dominance'].get('btc_dominance_pct')}%")

    return context


def main():
    if not API_KEY:
        print("Error: DUNE_API_KEY not set")
        print("Export it: export DUNE_API_KEY=your_key_here")
        return

    print("Fetching VISTA and BONZI metrics from Dune...\n")

    # Load existing data to preserve educational/benchmark sections
    output_path = os.path.join(os.path.dirname(__file__), 'metrics-data.json')
    existing = {}
    try:
        with open(output_path) as f:
            existing = json.load(f)
    except FileNotFoundError:
        pass

    # Initialize metrics structure
    metrics = {
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "vista": {},
        "bonzi": {},
        "dune_queries": QUERIES,
        "contracts": CONTRACTS,
    }

    # Fetch VISTA metrics
    print("=== VISTA ===")
    metrics['vista'] = fetch_token_metrics('vista', QUERIES)

    # Manual overrides for missing queries
    if not metrics['vista'].get('hhi_score'):
        metrics['vista']['hhi_score'] = 691  # Manual value since query was overwritten

    # Fetch BONZI metrics
    print("\n=== BONZI ===")
    metrics['bonzi'] = fetch_token_metrics('bonzi', QUERIES)

    # Fetch external market context
    metrics['market_context'] = fetch_market_context()

    # Preserve educational tooltips and benchmarks from existing file
    if existing.get('educational'):
        metrics['educational'] = existing['educational']
    if existing.get('benchmarks'):
        metrics['benchmarks'] = existing['benchmarks']

    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\nSaved to {output_path}")
    print(f"\n=== SIGNALS ===")
    for signal in metrics['market_context'].get('signals', []):
        print(f"  {signal}")


def update_market_only():
    """Quick update of just market context (no Dune API calls)."""
    print("Updating market context only...\n")

    # Load existing metrics
    output_path = os.path.join(os.path.dirname(__file__), 'metrics-data.json')
    try:
        with open(output_path) as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print("Error: metrics-data.json not found. Run full fetch first.")
        return

    # Update market context
    metrics['market_context'] = fetch_market_context()
    metrics['market_context']['updated'] = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    # Save
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\nMarket context updated in {output_path}")
    print(f"\n=== SIGNALS ===")
    for signal in metrics['market_context'].get('signals', []):
        print(f"  {signal}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--market-only':
        update_market_only()
    else:
        main()
