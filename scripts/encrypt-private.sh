#!/usr/bin/env bash
# encrypt-private.sh — build step: encrypt all private pages from _private_src/
# Usage: STATICRYPT_PASSWORD=<key> bash scripts/encrypt-private.sh
# Or:    bash scripts/encrypt-private.sh  (reads scripts/.staticrypt_key.local)
# Output: overwrites each <page>/index.html with the encrypted bundle.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/_private_src"
PAGES="page_1 page_2 page_3 page_4 alpha demo specs quest-earn"

# Resolve password
if [ -z "${STATICRYPT_PASSWORD:-}" ]; then
    KEY_FILE="$REPO/scripts/.staticrypt_key.local"
    if [ ! -f "$KEY_FILE" ]; then
        echo "ERROR: STATICRYPT_PASSWORD not set and scripts/.staticrypt_key.local not found"
        exit 1
    fi
    STATICRYPT_PASSWORD="$(tr -d '\n' < "$KEY_FILE")"
fi

if [ -z "$STATICRYPT_PASSWORD" ]; then
    echo "ERROR: empty password"
    exit 1
fi

# staticrypt treats --config and --template as relative to cwd, not as absolute
# paths (it prepends "./" to any path). Run from repo root with relative paths.
cd "$REPO"

echo "Encrypting private pages..."
for PAGE in $PAGES; do
    INPUT="_private_src/${PAGE}.html"
    OUT_DIR="${PAGE}"
    if [ ! -f "$INPUT" ]; then
        echo "  SKIP $PAGE (no source in _private_src/)"
        continue
    fi
    # staticrypt writes <basename>.html into -d directory
    npx staticrypt "$INPUT" -p "$STATICRYPT_PASSWORD" --short --remember false \
        -d "$OUT_DIR" --config ".staticrypt.json" --template "scripts/staticrypt-template.html"
    # Rename output to index.html if needed
    OUT_FILE="${OUT_DIR}/${PAGE}.html"
    if [ -f "$OUT_FILE" ]; then
        mv "$OUT_FILE" "${OUT_DIR}/index.html"
    fi
    echo "  OK  $PAGE/index.html ($(wc -c < "${OUT_DIR}/index.html") bytes)"
done
echo "Done."
