#!/usr/bin/env python3
"""Validate the public roadmap source and rendered page agree."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path


REQUIRED_HEADINGS = [
    "Short-term",
    "Mid-term",
    "Long-term",
]

REQUIRED_LINE_PREFIXES = [
    "Phase 1 is done",
    "Phase 2 is done",
    "We move on from",
    "Bonzi opens to more people",
    "You'll know we're at GTM",
]

FORBIDDEN_PHRASES = [
    "fully launched",
    "payout ready",
    "automatic approval",
    "governance power",
    "private threshold",
    "credentials",
    "exploit test",
    "internal prompt",
    "information vacuum",
    "blind trust",
    "plain-spoken",
    "Depth over hype",
    "void between announcements",
    "taboo",
    "announcement flow",
    "patient capital",
    "Investor watchlist",
    "Next investor watch",
    "investor-friendly",
    "Living Roadmap",
    "4/4 proof points",
    "Decision memory",
    "Answer traceability",
    "Partner roles",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=14,
        help="Maximum allowed age for the roadmap review date.",
    )
    parser.add_argument(
        "--today",
        help="Override today's date as YYYY-MM-DD for deterministic validation.",
    )
    return parser.parse_args()


def parse_review_date(markdown_text: str) -> date:
    for line in markdown_text.splitlines():
        if line.startswith("Last reviewed: "):
            raw_date = line.removeprefix("Last reviewed: ").strip()
            return datetime.strptime(raw_date, "%Y-%m-%d").date()
    raise ValueError("Missing docs/ROADMAP.md Last reviewed: YYYY-MM-DD line")


def required_page_phrases(markdown_text: str) -> tuple[list[str], list[str]]:
    phrases: list[str] = []
    errors: list[str] = []
    found_headings: set[str] = set()
    found_prefixes: dict[str, int] = {prefix: 0 for prefix in REQUIRED_LINE_PREFIXES}

    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## ") and not line.startswith("### "):
            heading = line.removeprefix("## ").strip()
            if heading in REQUIRED_HEADINGS:
                found_headings.add(heading)
                phrases.append(heading)
            continue
        for prefix in REQUIRED_LINE_PREFIXES:
            if line.startswith(prefix):
                found_prefixes[prefix] += 1
                phrases.append(line)

    for heading in REQUIRED_HEADINGS:
        if heading not in found_headings:
            errors.append(f"docs/ROADMAP.md missing required heading: {heading}")
    for prefix, count in found_prefixes.items():
        if count == 0:
            errors.append(
                "docs/ROADMAP.md missing required public metric line "
                f"starting with: {prefix}"
            )

    return phrases, errors


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    page_path = repo_root / "page_4" / "index.html"
    roadmap_path = repo_root / "docs" / "ROADMAP.md"

    if not page_path.exists():
        print("ERROR: page_4/index.html is missing")
        return 1
    if not roadmap_path.exists():
        print("ERROR: docs/ROADMAP.md is missing")
        return 1

    html_text = page_path.read_text()
    roadmap_text = roadmap_path.read_text()
    lowered = html_text.lower()
    errors: list[str] = []

    try:
        reviewed = parse_review_date(roadmap_text)
    except ValueError as exc:
        errors.append(str(exc))
        reviewed = None

    required_phrases, phrase_errors = required_page_phrases(roadmap_text)
    errors.extend(phrase_errors)

    today = (
        datetime.strptime(args.today, "%Y-%m-%d").date()
        if args.today
        else date.today()
    )

    if reviewed:
        age_days = (today - reviewed).days
        if age_days < 0:
            errors.append(
                f"Roadmap review date is in the future: {reviewed.isoformat()}"
            )
        elif age_days > args.max_age_days:
            errors.append(
                f"Roadmap review date is stale: {age_days} days old "
                f"(max {args.max_age_days})"
            )

    for phrase in required_phrases:
        if phrase not in html_text:
            errors.append(f"docs/ROADMAP.md phrase missing from page: {phrase}")

    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in lowered:
            errors.append(f"Forbidden public roadmap phrase present: {phrase}")

    if errors:
        print("Specs roadmap validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Specs roadmap validation OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
