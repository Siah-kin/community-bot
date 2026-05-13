---
title: "Codex audit: public repo representation"
description: "Audit README, scope, terminology, public-safety signals, and drift between public prose and the repository tree."
agent: codex
scope: public-representation-audit
---

# Codex audit: public repo representation (README + scope + drift vs tree)

## Context to fill in before running

- Repo: `community-bot` (or URL + local path)
- Repo root: `<LOCAL_PATH_TO_COMMUNITY_BOT_CHECKOUT>`
- Commit: `<SHA>`
- In-scope surfaces only:
  - slot machine + front end
  - ticket tool
  - staking mini-app (EtherVista router on Base)
- Out of scope:
  - Bonzi_v5
  - backends
  - keys
  - governance
  - OpenBox
  - any non-public API

## Instructions

Treat Codex as review + patch list, not free-form marketing. Use the frozen commit and hard boundaries above; do not infer Bonzi internals.

1. Map the file tree at `<SHA>` to the three in-scope surfaces. List every top-level path and classify each as `in_scope`, `out_of_scope_unclear`, or `should_not_be_public`.
2. Read `README`, pasted GitHub About text if provided, `LICENSE`, and any `CONTRIBUTING`, `SECURITY`, or `CODE_OF_CONDUCT` files.
3. Check alignment: does prose claim features or “full stack” behavior that has no files or only private behavior? Flag each overclaim with `file:line` evidence or `missing evidence`.
4. Check reproducibility: can a stranger run or preview without secrets? If steps are missing or wrong, specify exact README edits.
5. Check safety: perform grep-style review for embedded tokens, internal hostnames, staging URLs, and operator emails that should not be public.
6. Check terminology: flat-fee and onchain wording must be precise; do not invent APR; router means the documented contract address only if present in the repo.

## Output format only

- **Verdict:** `pass`, `pass_with_gaps`, or `fail`
- **Gap table:** columns `severity`, `location`, `issue`, `concrete_fix`
  - `severity` must be one of `blocker`, `should_fix`, or `nice`
  - keep each `concrete_fix` to one sentence
- **Suggested README replacement for §1–3:** markdown block, maximum 40 lines
- **Suggested GitHub About:** one-liner + topics list, comma-separated

## Hard rules

- Use an adversarial reader model.
- Cite paths for every finding.
- If unsure, label the item `needs_operator_confirm` instead of guessing.
- Do not edit private repos.
- Do not propose new features.
- Do not expand scope beyond the three in-scope surfaces.
