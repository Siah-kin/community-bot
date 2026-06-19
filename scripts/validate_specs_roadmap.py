#!/usr/bin/env python3
"""Validate the public roadmap freshness and copy boundaries."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path


REQUIRED_PHRASES = [
    "Living Roadmap",
    "Strategic Roadmap",
    "Last refreshed",
    "Refresh after evidence changes",
    "development depth",
    "Review questions",
    "Phase 1",
    "4/4 proof points",
    "Decision memory",
    "Answer traceability",
    "Partner roles",
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
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=14,
        help="Maximum allowed age for the roadmap refresh date.",
    )
    parser.add_argument(
        "--today",
        help="Override today's date as YYYY-MM-DD for deterministic validation.",
    )
    return parser.parse_args()


def parse_roadmap_date(html_text: str) -> date:
    match = re.search(
        r'<meta\s+name="roadmap-refreshed"\s+content="(\d{4}-\d{2}-\d{2})"',
        html_text,
    )
    if not match:
        raise ValueError("Missing <meta name=\"roadmap-refreshed\"> date")
    return datetime.strptime(match.group(1), "%Y-%m-%d").date()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    page_path = repo_root / "page_4" / "index.html"

    if not page_path.exists():
        print("ERROR: page_4/index.html is missing")
        return 1

    html_text = page_path.read_text()
    lowered = html_text.lower()
    errors: list[str] = []

    try:
        refreshed = parse_roadmap_date(html_text)
    except ValueError as exc:
        errors.append(str(exc))
        refreshed = None

    today = (
        datetime.strptime(args.today, "%Y-%m-%d").date()
        if args.today
        else date.today()
    )

    if refreshed:
        visible_phrase = f"Last refreshed {refreshed.isoformat()}"
        if visible_phrase not in html_text:
            errors.append(f"Visible refresh label missing: {visible_phrase}")
        age_days = (today - refreshed).days
        if age_days < 0:
            errors.append(
                f"Roadmap refresh date is in the future: {refreshed.isoformat()}"
            )
        elif age_days > args.max_age_days:
            errors.append(
                f"Roadmap refresh date is stale: {age_days} days old "
                f"(max {args.max_age_days})"
            )

    for phrase in REQUIRED_PHRASES:
        if phrase not in html_text:
            errors.append(f"Missing required roadmap phrase: {phrase}")

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
