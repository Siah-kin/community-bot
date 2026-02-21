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
from typing import Optional

# Expected nav structure (source of truth from includes/nav.html)
EXPECTED_NAV_LINKS = [
    "tools",
    "manual",
    "manifesto",
    "economics",
    "metrics",
    "stake",
    "dao",
    "contact"
]

# Pages that should have consistent nav
HTML_PAGES = [
    "index.html",
    "features.html",
    "manifesto.html",
    "privacy.html",
    "stake.html",
    "vote.html",
    "manual/index.html",
    "economics/index.html",
    "dao/index.html",
    "metrics/index.html"
]


def extract_nav_links(html_content: str, allow_fragment: bool = False) -> list:
    """Extract nav link text from HTML or a nav fragment."""
    nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', html_content, re.DOTALL)
    if nav_match:
        nav_html = nav_match.group(1)
    elif allow_fragment:
        nav_html = html_content
    else:
        return []

    # Extract full link content (including nested elements)
    links = re.findall(r'<a[^>]*>(.*?)</a>', nav_html, re.DOTALL)

    # Normalize: strip HTML tags, lowercase, remove arrows/emojis
    normalized = []
    for link in links:
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', link)
        # Clean up
        text = text.lower().strip()
        text = text.replace('↗', '').replace('→', '').strip()
        # Remove common emoji patterns
        text = re.sub(r'[^\w\s-]', '', text).strip()
        # Skip logo link
        if text in ['bonzi', 'home', '']:
            continue
        normalized.append(text)

    return normalized


def check_nav_style(html_content: str, filename: str, nav_fragment: Optional[str] = None) -> list:
    """Check nav styling consistency."""
    issues = []

    if nav_fragment is not None:
        nav_html = nav_fragment
    else:
        nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', html_content, re.DOTALL)
        if not nav_match:
            issues.append(f"{filename}: No <nav> element found")
            return issues
        nav_html = nav_match.group(1)

    # Remove dropdown menus before checking - their items can be capitalized (proper nouns)
    nav_without_dropdowns = re.sub(r'<div class="nav-dropdown-menu">.*?</div>', '', nav_html, flags=re.DOTALL)

    # Check for capitalized links in main nav only (should be lowercase)
    cap_links = re.findall(r'<a[^>]*>([A-Z][a-z]+)</a>', nav_without_dropdowns)
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
    shared_nav = None
    shared_nav_path = root_dir / "includes" / "nav.html"
    if shared_nav_path.exists():
        shared_nav = shared_nav_path.read_text()

    for page_path in HTML_PAGES:
        full_path = root_dir / page_path
        if not full_path.exists():
            warnings.append(f"Page not found: {page_path}")
            continue

        content = full_path.read_text()

        # Check nav links
        nav_fragment = None
        links = extract_nav_links(content)
        if not links and shared_nav:
            links = extract_nav_links(shared_nav, allow_fragment=True)
            nav_fragment = shared_nav
        if not links:
            errors.append(f"{page_path}: No nav links extracted")
            continue

        # Check style issues
        style_issues = check_nav_style(content, page_path, nav_fragment)
        errors.extend(style_issues)

        # Check for minimum required links
        required = ['tools', 'manual', 'manifesto']
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
        print("   Source of truth: includes/nav.html")
        sys.exit(1)

    print("\n✅ All nav structures consistent")
    sys.exit(0)


if __name__ == "__main__":
    main()
