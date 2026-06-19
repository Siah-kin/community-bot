#!/usr/bin/env python3
"""Guard new public pages from inheriting stale stake/nav behavior."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_SUBDIRS = [
    "/page_1/",
    "/page_1",
    "/page_2/",
    "/page_2",
    "/page_3/",
    "/page_3",
    "/page_4/",
    "/page_4",
]

PUBLIC_ROUTES = [
    "/page_1",
    "/page_2",
    "/page_3",
    "/page_4",
    "/specs",
    "/stake.html",
    "/stake",
]

REQUIRED_ROUTE_FILES = [
    "page_1/index.html",
    "page_2/index.html",
    "page_3/index.html",
    "page_4/index.html",
    "specs/index.html",
]

FORBIDDEN_PAGE_COPY = [
    'href="/stake',
    "href='/stake",
    "window.location.href = '/stake",
    'window.location.href = "/stake',
    "window.location.replace('/stake",
    'window.location.replace("/stake',
    "window.open('/stake",
    'window.open("/stake',
    'http-equiv="refresh" content="0; url=/stake',
]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    nav_loader = repo_root / "js" / "nav-loader.js"
    errors: list[str] = []

    nav_text = nav_loader.read_text()

    for subdir in REQUIRED_SUBDIRS:
        if subdir not in nav_text:
            errors.append(f"nav-loader.js missing page prefix: {subdir}")

    required_gate_markers = ["protectedSilverFoxPathKey", "slot=open&gate="]
    for marker in required_gate_markers:
        if marker not in nav_text:
            errors.append(f"nav-loader.js missing Silver Fox route gate marker: {marker}")

    for public_route in PUBLIC_ROUTES:
        quoted = f"['{public_route}'"
        if quoted in nav_text:
            errors.append(f"nav-loader.js must not protect public route: {public_route}")

    for route_file in REQUIRED_ROUTE_FILES:
        if not (repo_root / route_file).exists():
            errors.append(f"missing required route file: {route_file}")

    forbidden_nav_markers = [
        "SF-ALPHA-2026",
        "SILVER-FOX",
        "Access required",
        "This step is visible, but gated",
        "silver-fox-access-panel",
    ]
    for marker in forbidden_nav_markers:
        if marker in nav_text:
            errors.append(f"nav-loader.js contains obsolete client-side gate marker: {marker}")

    shared_nav = (repo_root / "includes" / "nav.html").read_text()
    mobile_nav = (repo_root / "includes" / "mobile-menu.html").read_text()
    if 'href="/stake.html"' not in shared_nav or "Stake $BONZI" not in shared_nav:
        errors.append("shared nav missing Stake $BONZI button to /stake.html")
    for label, text in [("includes/nav.html", shared_nav), ("includes/mobile-menu.html", mobile_nav)]:
        for marker in ["data-silver-fox-nav", "hidden>Why", "hidden>How", "hidden>What", "hidden>When", "hidden>Stake"]:
            if marker in text:
                errors.append(f"{label} contains obsolete public-nav gate marker: {marker}")
    if "Bonzivista_bot?start=apply" in nav_text:
        errors.append("shared nav routes contributor CTA to B2B start=apply")
    if "Apply to contribute" in shared_nav and "start=silverfox" not in nav_text:
        errors.append("Apply to contribute CTA must route through start=silverfox")

    page_paths = [repo_root / "404.html"]
    page_paths.extend(repo_root / route_file for route_file in REQUIRED_ROUTE_FILES)

    for page in page_paths:
        text = page.read_text()
        for phrase in FORBIDDEN_PAGE_COPY:
            if phrase in text:
                errors.append(f"{page.relative_to(repo_root)} contains forbidden stake route: {phrase}")

    if errors:
        print("New page nav guard FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("New page nav guard OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
