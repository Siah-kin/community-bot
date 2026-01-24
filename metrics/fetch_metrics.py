#!/usr/bin/env python3
"""
Fetch metrics from Dune API and save to JSON.
Run monthly: python fetch_metrics.py

Requires: DUNE_API_KEY environment variable
"""

import os
import json
import requests
from datetime import datetime

API_KEY = os.environ.get('DUNE_API_KEY')
BASE_URL = "https://api.dune.com/api/v1/query"

# Your Dune query IDs
QUERIES = {
    'holders': '6588894',      # Total holders + Top 10%
    # 'hhi': 'XXXXXXX',        # HHI score (add when created)
    # 'stakers': 'XXXXXXX',    # Staker stats (add when created)
    # 'diamond': 'XXXXXXX',    # Diamond hands (add when created)
}

def fetch_query(query_id: str) -> dict:
    """Fetch results from a Dune query."""
    url = f"{BASE_URL}/{query_id}/results"
    headers = {"x-dune-api-key": API_KEY}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data.get('result', {}).get('rows', [])

def main():
    if not API_KEY:
        print("Error: DUNE_API_KEY not set")
        return

    print("Fetching metrics from Dune...")

    # Initialize metrics structure
    metrics = {
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "free": {
            "vista": {
                "token_age_months": 6,
                "total_holders": None,
                "top_10_pct": None,
                "hhi_score": None
            },
            "bonzi": {
                "token_age_months": 6,
                "total_holders": None,
                "top_10_pct": None,
                "hhi_score": None
            },
            "case_study": {
                "wallet": "0xca90d843288e35beeadfce14e5f906e3f1afc7cb",
                "staking_since": "2024-10-03",
                "amount_staked": 15,
                "eth_claimed": 0.086,
                "tokens_sold": 0
            }
        },
        "tier1": {
            "holders_1k_plus": None,
            "staker_retention_pct": None,
            "exit_rate_pct": None,
            "diamond_hands_pct": None,
            "avg_tenure_days": None
        },
        "tier2": {
            "new_wallets_7d": None,
            "exiting_wallets_7d": None,
            "net_flow": None
        }
    }

    # Fetch holder data
    if 'holders' in QUERIES:
        try:
            rows = fetch_query(QUERIES['holders'])
            if rows:
                row = rows[0]
                metrics['free']['vista']['total_holders'] = row.get('total_holders')
                metrics['free']['vista']['top_10_pct'] = round(row.get('top_10_pct', 0), 1)
                print(f"  Holders: {row.get('total_holders')}, Top 10: {row.get('top_10_pct')}%")
        except Exception as e:
            print(f"  Error fetching holders: {e}")

    # Add more query fetches here as you create them
    # if 'hhi' in QUERIES:
    #     rows = fetch_query(QUERIES['hhi'])
    #     ...

    # Save to JSON
    output_path = os.path.join(os.path.dirname(__file__), 'metrics-data.json')
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\nSaved to {output_path}")
    print(json.dumps(metrics, indent=2))

if __name__ == '__main__':
    main()
