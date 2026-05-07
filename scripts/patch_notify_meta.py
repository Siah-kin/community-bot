#!/usr/bin/env python3
"""Patch ``bonzi-notify-signup-url`` in ``index.html`` before GitHub Pages deploy.

Usage (HTTPS only; matches front-end guard in ``index.html``):

  export BONZI_NOTIFY_SIGNUP_URL='https://your.hosted-signup.example/...'
  python3 scripts/patch_notify_meta.py

Does not print the URL. Exits 1 if env missing or not https://.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_INDEX = _ROOT / "index.html"
_PATTERN = re.compile(
    r'(<meta\s+name="bonzi-notify-signup-url"\s+content=")([^"]*)("\s*/?>)',
    re.IGNORECASE,
)


def main() -> int:
    raw = (os.environ.get("BONZI_NOTIFY_SIGNUP_URL") or "").strip()
    if not raw:
        print("Set BONZI_NOTIFY_SIGNUP_URL to your hosted signup URL (https only).", file=sys.stderr)
        return 1
    if not raw.lower().startswith("https://"):
        print("Notify URL must start with https://", file=sys.stderr)
        return 1

    text = _INDEX.read_text(encoding="utf-8")
    if not _PATTERN.search(text):
        print("Could not find bonzi-notify-signup-url meta in index.html", file=sys.stderr)
        return 1

    new_text, n = _PATTERN.subn(lambda m: f'{m.group(1)}{raw}{m.group(3)}', text, count=1)
    if n != 1:
        return 1
    _INDEX.write_text(new_text, encoding="utf-8")
    print("Updated index.html notify meta (value not echoed). Commit and push to refresh Pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
