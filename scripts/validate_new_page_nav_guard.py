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

    match = re.search(
        r"function\s+initDemoButton\(\)\s*\{(?P<body>.*?)\n\s*\}",
        nav_text,
        flags=re.DOTALL,
    )
    if not match:
        errors.append("nav-loader.js missing initDemoButton()")
    else:
        body = match.group("body")
        if "Bonzivista_bot?start=silverfox" not in body:
            errors.append("nav-connect-btn no longer opens Silver Fox apply path")
        if "stake" in body.lower():
            errors.append("nav-connect-btn handler references stake")

    page_paths = [
        repo_root / "404.html",
        repo_root / "specs" / "index.html",
    ]
    page_paths.extend(repo_root / page_dir / "index.html" for page_dir in ["page_1", "page_2", "page_3", "page_4"])

    for page in page_paths:
        if not page.exists():
            continue
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
