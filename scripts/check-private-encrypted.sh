#!/usr/bin/env bash
# check-private-encrypted.sh — guard: fails if any served private page contains
# readable plaintext or if _private_src/ is tracked by git.
# Run in pre-commit or CI. Exit 0 = all encrypted. Exit 1 = plaintext found.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PAGES="page_1 page_2 page_3 page_4 alpha demo specs quest-earn"

FAIL=0

# Check 1: _private_src must not be git-tracked
if git -C "$REPO" ls-files _private_src/ 2>/dev/null | grep -q .; then
    echo "FAIL: _private_src/ files are tracked by git — plaintext would be public"
    FAIL=1
fi

# Check 2: served pages must not contain data-i18n or <h1 (plaintext marker)
# StatiCrypt output contains neither; they appear only in unencrypted HTML.
for PAGE in $PAGES; do
    IDX="$REPO/$PAGE/index.html"
    if [ ! -f "$IDX" ]; then
        echo "WARN: $PAGE/index.html missing"
        continue
    fi
    if grep -qE 'data-i18n=|<h1' "$IDX"; then
        echo "FAIL: $PAGE/index.html contains plaintext markers (not encrypted)"
        FAIL=1
    fi
    # Also check staticrypt signature is present
    if ! grep -q 'staticrypt' "$IDX"; then
        echo "FAIL: $PAGE/index.html has no staticrypt signature"
        FAIL=1
    fi
done

# Check 3: served pages must not contain data-i18n or <h1 (plaintext marker)
# (already covered above in Check 2 loop — this comment preserved for numbering)

# Check 4: i18n/*.json must not contain keys starting with "when"
# (private roadmap namespace — must not leak into public files)
if python3 -c "
import json, pathlib, sys
repo = pathlib.Path('$REPO')
langs = ['en', 'fr', 'pt', 'ru', 'tr', 'zh']
found = []
for lang in langs:
    f = repo / 'i18n' / f'{lang}.json'
    if not f.exists():
        continue
    data = json.loads(f.read_text(encoding='utf-8'))
    when_keys = [k for k in data if k.startswith('when')]
    if when_keys:
        found.append(f'{lang}.json: {when_keys[:3]}')
if found:
    print('FAIL: private when.* keys found in i18n JSON:', found)
    sys.exit(1)
"; then
    : # check passed
else
    echo "FAIL: i18n JSON files contain private when.* roadmap keys"
    FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
    echo "OK: all private pages encrypted, _private_src not tracked"
fi
exit "$FAIL"
