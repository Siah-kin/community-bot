#!/usr/bin/env python3
"""Frontend consistency audit for the Bonzi marketing + slot site.

Deterministic checks that replace manual page-by-page tracing. Run locally or
on a 24h schedule (GitHub Action). Exits non-zero if any issue is found.

Checks:
  1. Language selector set        - all pages should offer the same N languages.
  2. Theme default consistency    - every page's data-theme-default should match.
  3. Em dash in user-visible text - U+2014 is banned in visible strings.
  4. i18n JSON parity             - pt/zh must not be missing keys or left in English.

Does NOT check rendered layout (nav overlap, margins). That needs a headless
screenshot pass - see README / phase 2.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_LANGS = {"en", "pt", "zh"}          # the 3 flags the mini-app uses
SKIP_HTML = {"nav-test.html"}                  # dev-only pages
issues = []


def add(check, sev, where, msg):
    issues.append((check, sev, where, msg))


def html_pages():
    return sorted(p for p in ROOT.glob("*.html") if p.name not in SKIP_HTML)


def check_lang_set():
    nav = ROOT / "js" / "nav-loader.js"
    if not nav.exists():
        return
    txt = nav.read_text(encoding="utf-8")
    m = re.search(r"langMap\s*=\s*\{([^}]*)\}", txt)
    if not m:
        return
    keys = set(re.findall(r"(\w+)\s*:", m.group(1)))
    offered = keys | {"en"}                    # en is the implicit default
    extra = offered - CANONICAL_LANGS
    if extra:
        add("lang-set", "P2", "js/nav-loader.js",
            f"selector offers {sorted(offered)}; canonical is {sorted(CANONICAL_LANGS)}; drop {sorted(extra)}")


def check_theme_default():
    # nav-loader.js falls back to 'light' when data-theme-default is unset,
    # so an unset page effectively renders light and is consistent. Only an
    # explicit value other than the canonical default is a real inconsistency.
    CANON = "light"
    for p in html_pages():
        txt = p.read_text(encoding="utf-8")
        m = re.search(r'data-theme-default=["\'](\w+)["\']', txt)
        effective = m.group(1) if m else CANON
        if effective != CANON:
            add("theme-default", "P2", p.name,
                f"theme default '{effective}' differs from canonical '{CANON}'")


def check_em_dash():
    for p in list(html_pages()) + sorted(ROOT.glob("js/*.js")):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if s.startswith(("//", "/*", "*", "<!--")) or "*/" in s:
                continue
            if "—" in line or "\\u2014" in line:
                add("em-dash", "P2", f"{p.relative_to(ROOT)}:{i}", s[:80])


def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def check_i18n_parity():
    i18n = ROOT / "i18n"
    en = _load(i18n / "en.json") or _load(ROOT / ".archive" / "i18n" / "en.json")
    if not en:
        return
    flat_en = {k: v for k, v in en.items() if isinstance(v, str)}
    for lang in ("pt", "zh"):
        tgt = _load(i18n / f"{lang}.json")
        if tgt is None:
            add("i18n", "P2", f"i18n/{lang}.json", "file missing")
            continue
        missing = [k for k in flat_en if k not in tgt]
        if missing:
            add("i18n", "P2", f"i18n/{lang}.json", f"{len(missing)} missing keys: {missing[:5]}")
        untranslated = [k for k in flat_en if isinstance(tgt.get(k), str) and tgt[k] == flat_en[k]]
        if untranslated:
            add("i18n", "P3", f"i18n/{lang}.json", f"{len(untranslated)} still in English: {untranslated[:5]}")


def main():
    check_lang_set()
    check_theme_default()
    check_em_dash()
    check_i18n_parity()

    print(f"# Frontend audit - {len(issues)} issue(s)\n")
    if not issues:
        print("clean.")
        return 0
    by_check = {}
    for c, sev, where, msg in issues:
        by_check.setdefault(c, []).append((sev, where, msg))
    for c in sorted(by_check):
        print(f"## {c} ({len(by_check[c])})")
        for sev, where, msg in by_check[c][:40]:
            print(f"  [{sev}] {where}  {msg}")
        if len(by_check[c]) > 40:
            print(f"  ... +{len(by_check[c]) - 40} more")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
