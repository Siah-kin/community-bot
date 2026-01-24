#!/bin/bash
# Fetch metrics from Dune API and save to JSON
# Run monthly: ./fetch-metrics.sh

API_KEY="${DUNE_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "Error: DUNE_API_KEY not set"
    exit 1
fi

echo "Fetching metrics from Dune..."

# Query IDs (replace with your actual query IDs)
HOLDER_QUERY="6588894"  # Total holders + Top 10%
# HHI_QUERY="XXXXXXX"   # HHI score
# STAKER_QUERY="XXXXXXX" # Staker stats

# Fetch holder data
curl -s -H "x-dune-api-key: $API_KEY" \
    "https://api.dune.com/api/v1/query/$HOLDER_QUERY/results" \
    | jq '.result.rows[0]' > /tmp/holders.json

# Combine into single metrics file
jq -n \
    --slurpfile holders /tmp/holders.json \
    '{
        "updated": now | strftime("%Y-%m-%d"),
        "holders": $holders[0]
    }' > metrics-data.json

echo "Saved to metrics-data.json"
cat metrics-data.json
