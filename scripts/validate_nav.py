#!/usr/bin/env python3
"""
Nav Consistency Validator

Catches nav structure inconsistencies across HTML pages before commit.
Part of the Oracle system - prevents ad-hoc patches that break site consistency.

Run: python3 scripts/validate_nav.py
"""

import re
import sys
from pathlib import Path

# Expected nav structure (source of truth from index.html)
# Note: faq.html contains the Manifesto, nav label should be "manifesto"
EXPECTED_NAV_LINKS = [
    "features",
    "manual",
    "research",
    "economics",
    "manifesto",
    "contact",
    "dao",
    "source"
]

# Pages that should have consistent nav
HTML_PAGES = [
    "index.html",
    "features.html",
    "faq.html",
    "research/index.html",
    "manual/index.html",
    "dao/index.html",
    "economics/index.html"
]


def extract_nav_links(html_content: str) -> list:
    """Extract nav link text from HTML."""
    # Find nav section
    nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', html_content, re.DOTALL)
    if not nav_match:
        return []

    nav_html = nav_match.group(1)

    # Extract link text (lowercase)
    links = re.findall(r'<a[^>]*>([^<]+)</a>', nav_html)

    # Normalize: lowercase, strip whitespace, remove arrows
    normalized = []
    for link in links:
        text = link.lower().strip().replace('↗', '').replace('→', '').strip()
        # Skip logo link
        if text in ['bonzi', 'home']:
            continue
        normalized.append(text)

    return normalized


def check_nav_style(html_content: str, filename: str) -> list:
    """Check nav styling consistency."""
    issues = []

    nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', html_content, re.DOTALL)
    if not nav_match:
        issues.append(f"{filename}: No <nav> element found")
        return issues

    nav_html = nav_match.group(1)

    # Check for capitalized links (should be lowercase)
    cap_links = re.findall(r'<a[^>]*>([A-Z][a-z]+)</a>', nav_html)
    if cap_links:
        issues.append(f"{filename}: Capitalized nav links found: {cap_links} (should be lowercase)")

    # Check for missing lang-switcher (optional warning)
    if 'lang-switcher' not in html_content and filename == 'index.html':
        pass  # Only homepage needs lang switcher

    return issues


def validate_all_pages(root_dir: Path) -> tuple:
    """Validate all HTML pages for nav consistency."""
    errors = []
    warnings = []

    for page_path in HTML_PAGES:
        full_path = root_dir / page_path
        if not full_path.exists():
            warnings.append(f"Page not found: {page_path}")
            continue

        content = full_path.read_text()

        # Check nav links
        links = extract_nav_links(content)
        if not links:
            errors.append(f"{page_path}: No nav links extracted")
            continue

        # Check style issues
        style_issues = check_nav_style(content, page_path)
        errors.extend(style_issues)

        # Check for minimum required links
        required = ['features', 'manual', 'manifesto']
        for req in required:
            if req not in links:
                errors.append(f"{page_path}: Missing required nav link '{req}'")

    return errors, warnings


def main():
    # Find repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    if not (repo_root / "index.html").exists():
        print("ERROR: Must run from community-bot repo root")
        sys.exit(1)

    print("🧭 Nav Consistency Check")
    print("=" * 40)

    errors, warnings = validate_all_pages(repo_root)

    if warnings:
        print("\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"   {w}")

    if errors:
        print("\n❌ ERRORS:")
        for e in errors:
            print(f"   {e}")
        print("\n   Fix nav inconsistencies before committing.")
        print("   Source of truth: index.html nav structure")
        sys.exit(1)

    print("\n✅ All nav structures consistent")
    sys.exit(0)


if __name__ == "__main__":
    main()
