#!/usr/bin/env python3
"""
Public Content Guard

Blocks risky copy/links from legal/public trust surfaces.
Current scope:
- privacy redirect page
- canonical legal privacy page
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    ROOT / "privacy.html",
    ROOT / "legal" / "privacy.html",
]

FORBIDDEN_PATTERNS = [
    r"closed alpha",
    r"stealth",
    r"sponsored by",
    r"co-founder",
    r"profits fund",
    r"etherfun\.app",
    r"defiants\.org",
    r"unidosprojects\.org",
]


def main() -> int:
    failures: list[str] = []

    for path in TARGETS:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(ROOT)}")
            continue

        content = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT))

        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, content, flags=re.IGNORECASE):
                failures.append(f"{rel}: forbidden pattern found -> {pattern}")

    # Privacy redirect must route to canonical legal page.
    redirect_page = (ROOT / "privacy.html").read_text(encoding="utf-8")
    if "/legal/privacy.html" not in redirect_page:
        failures.append("privacy.html: redirect target must be /legal/privacy.html")

    # Canonical legal page should declare legal URL.
    legal_page = (ROOT / "legal" / "privacy.html").read_text(encoding="utf-8")
    if 'href="https://bonzivista.org/legal/privacy.html"' not in legal_page:
        failures.append("legal/privacy.html: canonical URL must be /legal/privacy.html")

    if failures:
        print("PUBLIC CONTENT GUARD: FAIL")
        for f in failures:
            print(f" - {f}")
        return 1

    print("PUBLIC CONTENT GUARD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
