#!/usr/bin/env python3
"""Patch ``bonzi-notify-signup-url`` in ``index.html`` before GitHub Pages deploy.

Usage (HTTPS only; matches front-end guard in ``index.html``):

  export BONZI_NOTIFY_SIGNUP_URL='https://your.hosted-signup.example/...'
  python3 scripts/patch_notify_meta.py

Or supply a readable file containing one non-comment HTTPS line::

  printf '%s\n' 'https://your.hosted-signup.example/...' \\
    > scripts/bonzi_notify_signup_url.local.txt   # gitignored template
  export BONZI_NOTIFY_SIGNUP_FILE=scripts/bonzi_notify_signup_url.local.txt
  python3 scripts/patch_notify_meta.py

Does not print the URL. Exits 1 if env/file missing or not https:// (Telegram / tg: destinations rejected).

"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

_ROOT = Path(__file__).resolve().parents[1]
_INDEX = _ROOT / "index.html"
_PATTERN = re.compile(
    r'(<meta\s+name="bonzi-notify-signup-url"\s+content=")([^"]*)("\s*/?>)',
    re.IGNORECASE,
)


def _is_blocked_telegram_or_tg_scheme(raw: str) -> bool:
    """Reject Telegram web hosts and tg:/telegram: schemes (email-signup meta only)."""
    s = raw.strip()
    low = s.lower()
    if low.startswith("tg:") or low.startswith("telegram:"):
        return True
    if not low.startswith("https://"):
        return False
    try:
        parsed = urlparse(s)
        host = (parsed.hostname or "").lower()
        return host in ("t.me", "telegram.me", "web.telegram.org")
    except ValueError:
        return False


def _resolve_notify_url_raw() -> str:
    raw = (os.environ.get("BONZI_NOTIFY_SIGNUP_URL") or "").strip()
    if raw:
        return raw

    fp = (os.environ.get("BONZI_NOTIFY_SIGNUP_FILE") or "").strip()
    if not fp:
        return ""

    path = Path(fp).expanduser()
    if not path.is_file():
        print(
            "BONZI_NOTIFY_SIGNUP_FILE is not an existing file. "
            "Set BONZI_NOTIFY_SIGNUP_URL or a valid BONZI_NOTIFY_SIGNUP_FILE path.",
            file=sys.stderr,
        )
        sys.exit(1)

    lines = path.read_text(encoding="utf-8").splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if line and not line.startswith("#"):
            return line
    print(
        f"No HTTPS URL found in file (skipped comments/empty lines): {path}",
        file=sys.stderr,
    )
    return ""


def main() -> int:
    raw = _resolve_notify_url_raw()
    if not raw:
        print(
            "Set BONZI_NOTIFY_SIGNUP_URL, or put the URL on one line inside the file pointed to by "
            "BONZI_NOTIFY_SIGNUP_FILE (see script docstring).",
            file=sys.stderr,
        )
        return 1
    if not raw.lower().startswith("https://"):
        print("Notify URL must start with https://", file=sys.stderr)
        return 1

    if _is_blocked_telegram_or_tg_scheme(raw):
        print(
            "Telegram (or tg:) destinations are blocked for this meta "
            "(notify bar is for https email signup only).",
            file=sys.stderr,
        )
        return 1

    text = _INDEX.read_text(encoding="utf-8")
    if not _PATTERN.search(text):
        print("Could not find bonzi-notify-signup-url meta in index.html", file=sys.stderr)
        return 1

    new_text, n = _PATTERN.subn(lambda m: f"{m.group(1)}{raw}{m.group(3)}", text, count=1)
    if n != 1:
        return 1
    _INDEX.write_text(new_text, encoding="utf-8")
    print("Updated index.html notify meta (value not echoed). Commit and push to refresh Pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
