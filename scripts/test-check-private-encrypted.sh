#!/usr/bin/env bash
# test-check-private-encrypted.sh — self-contained test for check-private-encrypted.sh
# Asserts guard exits 0 on clean repo state, then injects a when.* key and asserts exit 1.
# Leaves repo byte-identical to before.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GUARD="$SCRIPT_DIR/check-private-encrypted.sh"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
EN_JSON="$REPO/i18n/en.json"

echo "=== test-check-private-encrypted.sh ==="

# Test A: guard must exit 0 on clean state
echo "Test A: guard exits 0 on clean repo..."
if bash "$GUARD"; then
    echo "  PASS: guard exited 0"
else
    echo "  FAIL: guard exited non-zero on clean repo"
    exit 1
fi

# Test B: inject when.test key, guard must exit non-zero
echo "Test B: inject when.test key, guard must exit non-zero..."

# Save a backup in a temp file
TMPFILE="$(mktemp)"
cp "$EN_JSON" "$TMPFILE"

# Inject when.test key using python3
python3 - "$EN_JSON" <<'PYEOF'
import json, sys, pathlib
f = pathlib.Path(sys.argv[1])
data = json.loads(f.read_text(encoding='utf-8'))
data['when.test'] = 'private test key - should be caught by guard'
f.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('  Injected when.test into en.json')
PYEOF

# Guard must now exit non-zero
GUARD_EXIT=0
bash "$GUARD" || GUARD_EXIT=$?
if [ "$GUARD_EXIT" -eq 0 ]; then
    echo "  FAIL: guard should have caught the when.test key"
    cp "$TMPFILE" "$EN_JSON"
    rm -f "$TMPFILE"
    exit 1
else
    echo "  PASS: guard correctly detected when.test key (exit $GUARD_EXIT)"
fi

# Restore original byte-for-byte
cp "$TMPFILE" "$EN_JSON"
rm -f "$TMPFILE"
echo "  Restored en.json"

# Test C: guard exits 0 after restore
echo "Test C: guard exits 0 after restore..."
if bash "$GUARD"; then
    echo "  PASS: guard exits 0 — repo byte-identical to before"
else
    echo "  FAIL: guard exits non-zero after restore"
    exit 1
fi

echo "=== All tests PASSED ==="
exit 0
