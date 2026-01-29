#!/usr/bin/env python3
"""
Footer Validation Script
Ensures all HTML pages follow the OG footer pattern.

Rules:
1. NO "Ready to Join" or CTA banners before footer
2. Footer must contain required sponsor links
3. NO purple gradient sections before footer

Usage:
    python3 scripts/validate_footer.py

Returns exit code 1 if violations found.
"""

import os
import re
import sys
from pathlib import Path

# Patterns that should NOT appear before footer
FORBIDDEN_PATTERNS = [
    r'Ready to Join',
    r'Buy \$BONZI',  # CTA button text
    r'background:\s*linear-gradient.*#1a0a2a',  # Purple gradient
    r'Stake & Earn.*</a>.*</div>.*</section>.*<footer',  # CTA section before footer
]

# Required elements in footer
REQUIRED_FOOTER_ELEMENTS = [
    r'etherfun\.app',  # Ethervista link
    r'defiants\.org',  # Defiants link
    r'unidosprojects\.org',  # Unidos link
    r'privacy',  # Privacy policy reference
    r'mit license|MIT license',  # License mention
]

# Files to skip (templates, variants, etc.)
SKIP_FILES = [
    'OG_FOOTER_TEMPLATE.html',
    'nav-test.html',
    'terms.html',  # Legal page, different format
    'qr.html',  # Minimal widget
    'faq.html',  # Redirect to manifesto.html
]

# Directories to skip entirely (drafts, embedded widgets)
SKIP_DIRS = [
    'homepage-variants',  # Draft pages, not production
]

# Directories to check
CHECK_DIRS = [
    '.',
    'metrics',
    'dao',
]


def get_html_files(base_path: Path) -> list:
    """Get all HTML files to validate."""
    files = []
    for dir_name in CHECK_DIRS:
        dir_path = base_path / dir_name
        if dir_path.exists():
            for f in dir_path.glob('*.html'):
                if f.name not in SKIP_FILES:
                    files.append(f)
    return files


def check_forbidden_before_footer(content: str, filepath: str) -> list:
    """Check for forbidden patterns before footer."""
    violations = []

    # Find footer position
    footer_match = re.search(r'<footer', content, re.IGNORECASE)
    if not footer_match:
        return violations  # No footer to check

    before_footer = content[:footer_match.start()]

    # Only check the last 2000 chars before footer (where CTA would be)
    check_region = before_footer[-2000:] if len(before_footer) > 2000 else before_footer

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, check_region, re.IGNORECASE | re.DOTALL):
            violations.append(f"  - Forbidden pattern '{pattern}' found before footer")

    return violations


def check_required_footer_elements(content: str, filepath: str) -> list:
    """Check that footer contains required elements."""
    violations = []

    # Find ALL footers in the document
    all_footers = re.findall(r'<footer[^>]*>.*?</footer>', content, re.IGNORECASE | re.DOTALL)

    if not all_footers:
        violations.append("  - No footer found")
        return violations

    # Warn about multiple footers (should consolidate)
    if len(all_footers) > 1:
        violations.append(f"  - Multiple footers found ({len(all_footers)}) - consolidate into single OG footer")

    # Check the LAST footer (typically the main one at page bottom)
    footer_content = all_footers[-1]

    for pattern in REQUIRED_FOOTER_ELEMENTS:
        if not re.search(pattern, footer_content, re.IGNORECASE):
            violations.append(f"  - Missing required element: {pattern}")

    return violations


def validate_file(filepath: Path) -> list:
    """Validate a single HTML file."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return [f"  - Could not read file: {e}"]

    violations = []
    violations.extend(check_forbidden_before_footer(content, str(filepath)))
    violations.extend(check_required_footer_elements(content, str(filepath)))

    return violations


def main():
    """Main validation function."""
    base_path = Path(__file__).parent.parent
    html_files = get_html_files(base_path)

    print(f"Validating {len(html_files)} HTML files for footer compliance...")
    print(f"Reference: .claude/OG_FOOTER_TEMPLATE.html\n")

    total_violations = 0
    files_with_issues = []

    for filepath in html_files:
        violations = validate_file(filepath)
        if violations:
            rel_path = filepath.relative_to(base_path)
            files_with_issues.append((rel_path, violations))
            total_violations += len(violations)

    if files_with_issues:
        print("FOOTER VIOLATIONS FOUND:\n")
        for filepath, violations in files_with_issues:
            print(f"{filepath}:")
            for v in violations:
                print(v)
            print()

        print(f"Total: {total_violations} violations in {len(files_with_issues)} files")
        print("\nFix these issues or update .claude/OG_FOOTER_TEMPLATE.html if pattern changed.")
        return 1
    else:
        print("All files pass footer validation.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
