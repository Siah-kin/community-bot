#!/bin/bash
#
# Water Prompt enforcement for community-bot
# Checks staged HTML files for banned vocabulary, em dashes, missing OG tags,
# and jargon without tooltip wrappers.
#
# Exit codes: 0 = pass, 1 = violations (block commit), 2 = warnings only
#
# Usage:
#   ./scripts/water_check.sh          # Check staged files only (pre-commit)
#   ./scripts/water_check.sh --all    # Check all HTML files
#   ./scripts/water_check.sh --file path/to/file.html  # Check specific file
#
# Source of truth: Bonzi_v5/src/leadership/judgment/water_rules.json
# Banned words copied inline so community-bot has no dependency on Bonzi_v5.

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# --- Banned vocabulary (from water_rules.json) ---

FIRE_LANGUAGE=(
    "revolutionary" "revolutionaries" "revolutionize"
    "disrupt" "disrupts" "disrupted" "disrupting" "disruptive"
    "paradigm"
    "transform" "transforms" "transformed" "transforming" "transformative"
    "innovate" "innovates" "innovated" "innovating" "innovative"
    "cutting-edge" "cutting edge"
    "game-changer" "game changer"
)

AI_FINGERPRINTS=(
    "leverage" "leverages" "leveraged" "leveraging"
    "utilize" "utilizes" "utilized" "utilizing"
    "unlock" "unlocks" "unlocked" "unlocking"
    "synergy" "synergies"
    "seamlessly"
    "holistic" "holistically"
)

FILLER_ADVERBS=(
    "fundamentally" "essentially" "arguably"
    "notably" "significantly" "inherently"
)

POLITICALLY_LOADED=(
    "mutualistic" "cooperative economics"
    "collective" "decentralized future"
    "next-generation" "next generation"
)

# --- Jargon terms that should have tooltip wrappers ---
JARGON_TERMS=(
    "sybil" "oracle" "DEX" "DeFi" "ERC-8004"
    "CPI" "tokenomics" "on-chain" "LP "
)

# --- Primary pages that must have OG tags ---
PRIMARY_PAGES=(
    "index.html"
    "features.html"
    "manifesto.html"
    "economics/index.html"
    "research/index.html"
    "manual/index.html"
    "dao/index.html"
    "stake.html"
    "baas.html"
    "vetter/index.html"
    "metrics/index.html"
)

# --- Colors ---
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

violations=0
warnings=0

# Determine which files to check
get_files() {
    if [ "$1" = "--all" ]; then
        find "$REPO_ROOT" -name "*.html" \
            -not -path "*/node_modules/*" \
            -not -path "*/.git/*" \
            -not -path "*/drafts/*" \
            -not -path "*/nav-test/*" \
            -not -name "privacy.html"
    elif [ "$1" = "--file" ] && [ -n "$2" ]; then
        echo "$2"
    else
        # Staged HTML files only
        cd "$REPO_ROOT"
        git diff --cached --name-only --diff-filter=ACM | grep '\.html$' || true
    fi
}

FILES=$(get_files "$1" "$2")

if [ -z "$FILES" ]; then
    echo -e "${GREEN}No HTML files to check.${NC}"
    exit 0
fi

echo "=== Water Prompt Check ==="
echo ""

# Check 1: Em dashes (BLOCK)
echo "--- Em Dash Check ---"
em_dash_found=0
while IFS= read -r file; do
    if grep -n $'\xe2\x80\x94' "$file" 2>/dev/null; then
        echo -e "${RED}BLOCK${NC} Em dash found in: $file"
        em_dash_found=1
    fi
done <<< "$FILES"

if [ "$em_dash_found" -eq 1 ]; then
    violations=$((violations + 1))
    echo -e "${RED}Replace all em dashes with hyphens (-).${NC}"
else
    echo -e "${GREEN}No em dashes found.${NC}"
fi
echo ""

# Check 2: Banned vocabulary (BLOCK)
echo "--- Banned Vocabulary Check ---"
ALL_BANNED=("${FIRE_LANGUAGE[@]}" "${AI_FINGERPRINTS[@]}" "${FILLER_ADVERBS[@]}" "${POLITICALLY_LOADED[@]}")
banned_found=0

while IFS= read -r file; do
    for word in "${ALL_BANNED[@]}"; do
        # Case-insensitive word boundary search, skip HTML attributes and CSS
        matches=$(grep -in "\b${word}\b" "$file" 2>/dev/null | grep -v 'class=' | grep -v 'data-tip=' | grep -v '<style' | grep -v '/*' || true)
        if [ -n "$matches" ]; then
            echo -e "${RED}BLOCK${NC} \"$word\" in $file:"
            echo "$matches" | head -3
            banned_found=1
        fi
    done
done <<< "$FILES"

if [ "$banned_found" -eq 1 ]; then
    violations=$((violations + 1))
    echo -e "${RED}Remove banned words or use approved alternatives.${NC}"
else
    echo -e "${GREEN}No banned vocabulary found.${NC}"
fi
echo ""

# Check 3: Missing OG tags on primary pages (WARN)
echo "--- OG Tag Check ---"
og_missing=0
while IFS= read -r file; do
    rel_path="${file#$REPO_ROOT/}"
    for page in "${PRIMARY_PAGES[@]}"; do
        if [ "$rel_path" = "$page" ]; then
            if ! grep -q 'og:title' "$file" 2>/dev/null; then
                echo -e "${YELLOW}WARN${NC} Missing og:title in $rel_path"
                og_missing=1
            fi
            if ! grep -q 'og:description' "$file" 2>/dev/null; then
                echo -e "${YELLOW}WARN${NC} Missing og:description in $rel_path"
                og_missing=1
            fi
            if ! grep -q 'og:image' "$file" 2>/dev/null; then
                echo -e "${YELLOW}WARN${NC} Missing og:image in $rel_path"
                og_missing=1
            fi
        fi
    done
done <<< "$FILES"

if [ "$og_missing" -eq 1 ]; then
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}All primary pages have OG tags.${NC}"
fi
echo ""

# Check 4: Jargon without tooltip wrapper (WARN)
echo "--- Jargon Tooltip Check ---"
jargon_found=0
while IFS= read -r file; do
    for term in "${JARGON_TERMS[@]}"; do
        # Find occurrences NOT inside a data-tip attribute or .term span
        # Look for the term in visible text (not inside tags or attributes)
        bare=$(grep -in "$term" "$file" 2>/dev/null | grep -v 'data-tip=' | grep -v 'class="term"' | grep -v '<style' | grep -v '<script' | grep -v '<!--' | grep -v 'meta ' || true)
        if [ -n "$bare" ]; then
            echo -e "${YELLOW}WARN${NC} \"$term\" without tooltip in $(basename "$file"):"
            echo "$bare" | head -2
            jargon_found=1
        fi
    done
done <<< "$FILES"

if [ "$jargon_found" -eq 1 ]; then
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}No bare jargon found.${NC}"
fi
echo ""

# Summary
echo "=== Summary ==="
if [ "$violations" -gt 0 ]; then
    echo -e "${RED}$violations violation(s) found. Commit blocked.${NC}"
    exit 1
elif [ "$warnings" -gt 0 ]; then
    echo -e "${YELLOW}$warnings warning(s) found. Commit allowed.${NC}"
    exit 0
else
    echo -e "${GREEN}All checks passed.${NC}"
    exit 0
fi
