#!/usr/bin/env python3
"""
Create VISTA metrics queries in Dune via API.
Run once: python setup_queries.py

After running, update QUERIES dict in fetch_metrics.py with the IDs.
"""

import os
import json
import requests
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
BASE_URL = "https://api.dune.com/api/v1"

# All VISTA metrics queries
VISTA_QUERIES = {
    'staker_retention': {
        'name': 'VISTA Staker Retention',
        'sql': '''
SELECT
    action,
    COUNT(DISTINCT wallet) as wallets
FROM (
    SELECT
        "from" as wallet,
        CASE WHEN bytearray_substring(data,1,4) = 0x666da64f THEN 'staking' ELSE 'exited' END as action,
        ROW_NUMBER() OVER (PARTITION BY "from" ORDER BY block_time DESC) as rn
    FROM ethereum.transactions
    WHERE "to" = 0xee5a6f8a55b02689138c195031d09bafdc7d278f
        AND success = true
        AND block_time > DATE '2024-09-01'
        AND bytearray_substring(data,1,4) IN (0x666da64f, 0x2e1a7d4d)
)
WHERE rn = 1
GROUP BY action
'''
    },
    'diamond_hands': {
        'name': 'VISTA Diamond Hands',
        'sql': '''
SELECT COUNT(DISTINCT "from") as diamond_hands
FROM ethereum.transactions t1
WHERE "to" = 0xee5a6f8a55b02689138c195031d09bafdc7d278f
    AND success = true
    AND block_time > DATE '2024-09-01'
    AND bytearray_substring(data,1,4) = 0x666da64f
    AND NOT EXISTS (
        SELECT 1 FROM ethereum.transactions t2
        WHERE t2."from" = t1."from"
            AND t2."to" = 0xee5a6f8a55b02689138c195031d09bafdc7d278f
            AND t2.block_time > DATE '2024-09-01'
            AND bytearray_substring(t2.data,1,4) = 0x2e1a7d4d
    )
'''
    },
    'tenure': {
        'name': 'VISTA Tenure',
        'sql': '''
SELECT
    ROUND(AVG(DATE_DIFF('day', first_stake, NOW()))) as avg_tenure_days,
    MAX(DATE_DIFF('day', first_stake, NOW())) as max_tenure_days
FROM (
    SELECT "from" as wallet, MIN(block_time) as first_stake
    FROM ethereum.transactions
    WHERE "to" = 0xee5a6f8a55b02689138c195031d09bafdc7d278f
        AND success = true
        AND bytearray_substring(data,1,4) = 0x666da64f
        AND block_time > DATE '2024-09-01'
    GROUP BY 1
)
'''
    },
    'weekly_trend': {
        'name': 'VISTA Weekly Trend',
        'sql': '''
SELECT
    DATE_TRUNC('week', block_time) as week,
    COUNT(*) FILTER (WHERE bytearray_substring(data,1,4) = 0x666da64f) as stakes,
    COUNT(*) FILTER (WHERE bytearray_substring(data,1,4) = 0x2e1a7d4d) as unstakes
FROM ethereum.transactions
WHERE "to" = 0xee5a6f8a55b02689138c195031d09bafdc7d278f
    AND success = true
    AND block_time > DATE '2024-09-01'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 12
'''
    },
    'total_stakers': {
        'name': 'VISTA Total Stakers',
        'sql': '''
SELECT COUNT(DISTINCT "from") as total_stakers
FROM ethereum.transactions
WHERE "to" = 0xee5a6f8a55b02689138c195031d09bafdc7d278f
    AND success = true
    AND block_time > DATE '2024-09-01'
    AND bytearray_substring(data,1,4) = 0x666da64f
'''
    }
}


def create_query(name: str, sql: str) -> dict:
    """Create a new query in Dune."""
    url = f"{BASE_URL}/query"
    headers = {
        "x-dune-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "name": name,
        "query_sql": sql.strip(),
        "is_private": False
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def execute_query(query_id: str) -> dict:
    """Execute a query to cache results."""
    url = f"{BASE_URL}/query/{query_id}/execute"
    headers = {"x-dune-api-key": API_KEY}

    response = requests.post(url, headers=headers)
    return response.json()


def main():
    if not API_KEY:
        print("Error: DUNE_API_KEY not set")
        print("Create .env file with: DUNE_API_KEY=your_key")
        return

    print("Creating VISTA metrics queries in Dune...\n")

    query_ids = {}

    for key, config in VISTA_QUERIES.items():
        print(f"Creating: {config['name']}")

        result = create_query(config['name'], config['sql'])

        if 'query_id' in result:
            query_id = result['query_id']
            query_ids[key] = query_id
            print(f"  Created: {query_id}")

            # Execute to cache results
            print(f"  Executing...")
            exec_result = execute_query(str(query_id))
            if 'execution_id' in exec_result:
                print(f"  Execution started: {exec_result['execution_id']}")
            else:
                print(f"  Exec response: {exec_result}")
        else:
            print(f"  Error: {result}")

    print("\n" + "="*50)
    print("QUERY IDS - Add these to fetch_metrics.py:")
    print("="*50)
    print("\nQUERIES = {")
    print("    'hhi': '6588894',")
    for key, qid in query_ids.items():
        print(f"    '{key}': '{qid}',")
    print("}")

    # Save to file for reference
    output = Path(__file__).parent / 'query_ids.json'
    with open(output, 'w') as f:
        json.dump(query_ids, f, indent=2)
    print(f"\nAlso saved to: {output}")


if __name__ == '__main__':
    main()
