#!/usr/bin/env python3
"""Validate the public WHAT product-definition page posture."""

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_PHRASES = [
    "proof-based governance ledger",
    "who contributed, who verified, who was affected, and what happened next",
    "Online trust breaks when decisions stay informal",
    "A shared record for contribution, verification, gratitude, and outcomes",
    "Bonzi helps communities govern with proof",
    "People and agents propose work",
    "Claims require proof",
    "No actor should be the only source for its own approval",
    "Governance ledger",
    "Contribution ledger",
    "Gratitude ledger",
    "Ostrom-compliant governance",
    "No unchecked authority",
    "DAOs",
    "Token communities",
    "Not just a chatbot",
    "Not just a voting tool",
    "Not just analytics",
    "important claims need evidence",
    "Specs carry the depth; this page defines the product",
]

FORBIDDEN_PHRASES = [
    "fully launched",
    "payout ready",
    "automatic approval",
    "governance power",
    "private threshold",
    "credentials",
    "Access required",
    "This step is visible, but gated",
    "SF-ALPHA-2026",
    "SILVER-FOX",
    "Knowledge / RAG memory",
    "RACI governance",
    "Live ops / deploy validation",
    "Formal mistakes logged",
    "Escalated tickets",
]


def validate_page(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text()
    lowered = text.lower()
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"{path.relative_to(root)} missing required phrase: {phrase}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in lowered:
            errors.append(f"{path.relative_to(root)} contains forbidden phrase: {phrase}")
    if "<footer" not in lowered:
        errors.append(f"{path.relative_to(root)} missing footer")
    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    pages = [repo_root / "page_3" / "index.html"]
    errors: list[str] = []
    for page in pages:
        if not page.exists():
            errors.append(f"missing required What page: {page.relative_to(repo_root)}")
            continue
        errors.extend(validate_page(page, repo_root))

    specs_alias = repo_root / "specs" / "index.html"
    if not specs_alias.exists():
        errors.append("missing specs compatibility alias: specs/index.html")
    else:
        alias_text = specs_alias.read_text()
        if 'href="https://bonzivista.org/page_3/"' not in alias_text:
            errors.append("specs/index.html missing canonical link to /page_3/")
        if "window.location.replace('/page_3/')" not in alias_text:
            errors.append("specs/index.html must redirect to /page_3/")

    if errors:
        print("What page validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("What page validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
