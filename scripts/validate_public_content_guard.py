#!/usr/bin/env python3
"""
Public Content Guard

Blocks risky copy/links from legal/public trust surfaces.
Also enforces a link allowlist on public pages: any internal href not in the
approved set fails the check. Coverage derived deterministically from the
public page list below.

Current scope:
- privacy redirect page
- canonical legal privacy page
- href allowlist on all public pages
"""

from __future__ import annotations

import re
import subprocess
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

# Public pages that carry the link allowlist check.
PUBLIC_PAGES: list[Path] = [
    ROOT / "index.html",
    ROOT / "about.html",
    ROOT / "page_1" / "index.html",
    ROOT / "page_2" / "index.html",
    ROOT / "page_3" / "index.html",
    ROOT / "page_4" / "index.html",
    ROOT / "research" / "index.html",
    ROOT / "research" / "program.html",
    ROOT / "stake.html",
]

# Internal hrefs allowed on public pages. Anything not in this set is a violation.
# External URLs (http/https) and fragment-only (#) are always allowed.
ALLOWED_INTERNAL_HREFS: frozenset[str] = frozenset([
    "/",
    "/about.html",
    "/page_1/",
    "/page_2/",
    "/page_3/",
    "/page_4/",
    "/research/",
    "/research/program.html",
    "/research/ablation-proof.html",
    "/research/adversarial-proof.html",
    "/research/openbox-proof.html",
    "/research/openbox-proof-pt.html",
    "/research/contribution-paper.html",
    "/research/contribution-paper-pt.html",
    "/research/contribution-summary.html",
    "/research/contribution-summary-pt.html",
    "/research/openbox-results.csv",
    "/stake.html",
    "/privacy.html",
    "/legal/privacy.html",
    # Relative equivalents used inside subdirectory pages
    "../page_2/",
    "../stake.html",
    "../privacy.html",
    "../research/",
    "../research/program.html",
    "ablation-proof.html",
    "adversarial-proof.html",
    "openbox-proof.html",
    "openbox-proof-pt.html",
    "contribution-paper.html",
    "contribution-paper-pt.html",
    "contribution-summary.html",
    "contribution-summary-pt.html",
    "openbox-results.csv",
    "program.html",
    # Root index self-references
    "/?slot=open",
    "/page_2/",
    "/page_2/?access=entered",
    "page_2/?access=entered",
    "legal/privacy.html",
    # External always allowed - matched by prefix check below
])

_ANCHOR_RE = re.compile(r'<a\b[^>]*\bhref=["\']([^"\']*)["\']', re.IGNORECASE)


def _is_violation(href: str) -> bool:
    """Return True if this href is an internal link outside the allowlist."""
    if href.startswith("http://") or href.startswith("https://"):
        return False
    if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
        return False
    if href.startswith("#"):
        return False
    # Strip query string for matching
    bare = href.split("?")[0].rstrip("/")
    bare_slash = bare + "/" if not bare.endswith("/") else bare
    # Check allowlist (both with and without trailing slash)
    for allowed in ALLOWED_INTERNAL_HREFS:
        bare_allowed = allowed.split("?")[0].rstrip("/")
        if bare == bare_allowed or bare_slash == bare_allowed + "/":
            return False
        if allowed == href:
            return False
    return True


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
    if "nav-loader.js" in legal_page:
        failures.append("legal/privacy.html: must not depend on nav-loader.js")

    # Href allowlist check on public pages.
    for page_path in PUBLIC_PAGES:
        if not page_path.exists():
            failures.append(f"public page missing: {page_path.relative_to(ROOT)}")
            continue
        content = page_path.read_text(encoding="utf-8")
        rel = str(page_path.relative_to(ROOT))
        for match in _ANCHOR_RE.finditer(content):
            href = match.group(1)
            if _is_violation(href):
                failures.append(f"{rel}: disallowed internal link -> {href}")

    if failures:
        print("PUBLIC CONTENT GUARD: FAIL")
        for f in failures:
            print(f" - {f}")
        return 1

    print("PUBLIC CONTENT GUARD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
