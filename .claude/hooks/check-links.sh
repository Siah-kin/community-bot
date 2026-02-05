#!/bin/bash
# Link Policy Enforcement Hook
# Blocks commits containing banned link patterns

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Checking link policy compliance..."

ERRORS=0

# Banned Telegram bot variants
BANNED_TG=(
    "t\.me/Bonzi_Community_bot"
    "t\.me/bonzi_community_bot"
    "t\.me/BonziVistaBot"
    "t\.me/SiahBot"
    "t\.me/bonzi_raider_bot"
    "t\.me/bonzi_raider"
    "t\.me/bonzisiah"
    "t\.me/bonzivista_bot"  # wrong case
)

# Banned X accounts (in body content)
BANNED_X=(
    "x\.com/ethaboringtoshi"
    "x\.com/deabordefiants"
)

# Banned Ethervista patterns
BANNED_EV=(
    "ethervista\.com"
    "docs\.ethervista\.app"
)

# Check HTML files only
HTML_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.html$' || true)

if [ -z "$HTML_FILES" ]; then
    echo -e "${GREEN}No HTML files to check${NC}"
    exit 0
fi

# Check Telegram bans
for pattern in "${BANNED_TG[@]}"; do
    matches=$(grep -l "$pattern" $HTML_FILES 2>/dev/null || true)
    if [ -n "$matches" ]; then
        echo -e "${RED}BLOCKED: Banned Telegram link '$pattern' found in:${NC}"
        echo "$matches" | sed 's/^/  - /'
        echo -e "${YELLOW}Use: https://t.me/Bonzivista_bot${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check X bans
for pattern in "${BANNED_X[@]}"; do
    matches=$(grep -l "$pattern" $HTML_FILES 2>/dev/null || true)
    if [ -n "$matches" ]; then
        echo -e "${RED}BLOCKED: Banned X account '$pattern' found in:${NC}"
        echo "$matches" | sed 's/^/  - /'
        echo -e "${YELLOW}Use: https://x.com/Bonzi_vista${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check Ethervista bans
for pattern in "${BANNED_EV[@]}"; do
    matches=$(grep -l "$pattern" $HTML_FILES 2>/dev/null || true)
    if [ -n "$matches" ]; then
        echo -e "${RED}BLOCKED: Banned Ethervista pattern '$pattern' found in:${NC}"
        echo "$matches" | sed 's/^/  - /'
        echo -e "${YELLOW}Use: https://www.ethervista.app/how-it-works${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo -e "${RED}Link policy violation! $ERRORS issue(s) found.${NC}"
    echo -e "See: .claude/LINK_POLICY.md"
    exit 1
fi

echo -e "${GREEN}Link policy: PASSED${NC}"
exit 0
