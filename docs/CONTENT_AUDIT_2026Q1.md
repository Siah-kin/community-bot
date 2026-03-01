# Community-Bot Content Audit: Voice & Personality Analysis
**Date:** 2026-03-01 | **Scope:** research/index.html, research/openbox-proof.html, ecosystem scan

---

## Page 1: `/research/index.html` — The Three Flagship Models

### Current Voice
**Tone:** Academic-formal mixed with casual explainers. Shifts between:
- Rigorous economic framing ("exit liquidity", "Ethervista Euler model")
- Accessible storytelling ("A farmer in Nakivale... offers 2,000 UGX/kg")
- Technical jargon (CPI, ACF, DEX, RWA) followed by plain definitions

**Personality:** Researcher-as-educator. Transparent about stage ("planning stage", "not validated findings"). Defensive against skepticism (acknowledges crypto's reputation problem). Confident but not hype-y.

### Content Map: What Exists & What Changes

| Section | Purpose | Data Type | Updates? |
|---------|---------|-----------|----------|
| Hero ("Three flagship models...") | Hook: thesis statement | Static framework | No |
| Status Update | "planning stage", "exploratory data" | Episodic | Yes (needs quarterly refresh) |
| What We're Researching | Core questions + rationale for three models | Evergreen | No |
| Shared Oracle Infrastructure | CPI mechanics, ACF, ERC-8004 | Reference | No |
| BONZI section | Memecoin mechanics, flat fees, hardstake | Partially live | Yes (needs fee dashboard link) |
| IMOBX section | RWA housing, SINAPI integration, Q3 2026 pilot | Pre-revenue | Yes (pilot updates quarterly) |
| UNIDOS section | NGO data-for-credit, 500 farmers, revenue model | Pilot stage | Yes (monthly metrics needed) |
| Glossary | 15 definitions | Reference | No |

### Questions Visitors Actually Ask
1. **"What's the difference between these three?"**
   → Answered but requires reading 3x 2KB sections; no comparison table

2. **"Which one can I use now?"**
   → BONZI live, IMOBX/UNIDOS pre-revenue (scattered across text, not highlighted)

3. **"How do I join/get involved?"**
   → NOT answered (no CTA, no community links)

4. **"Where's the proof this works?"**
   → Pointed elsewhere ("Deep research lives on project-specific sites")

5. **"What's the current status?"**
   → Buried in status paragraph; no live metric indicators

### Content Health: Dead vs Alive

**Dead (never changes):**
- Glossary (reference layer)
- Architecture diagrams (32 signals, 10 dimensions)
- Competitor analysis (Nansen/Arkham/CPI positioning)
- Economic thesis paragraphs

**Alive (needs quarterly updates):**
- Status: "planning stage" → should show current phase with dates
- BONZI metrics: fee revenue, hardstake TVL, CPI distribution (missing dashboard link)
- IMOBX pilot: Q3 2026 target, legal status, site selection (no recent updates visible)
- UNIDOS metrics: farmers trained (501), produce (4,800 kg mushrooms), wage dependency (67% casual labor)

### Ideal Page-Agent Personality

**Name:** The Transparentist

**Traits:**
- Rigorous but defensive: "Here's what we don't know yet"
- Educator-first: Defines jargon then uses it
- Jargon-aware: Glossary exists but doesn't slow reading
- Honest-about-stage: "Pilot data is exploratory — not validated findings"

**Activation triggers:**
- Monthly: Update UNIDOS numbers (farmers trained, produce volume)
- Quarterly: Update IMOBX pilot progress (legal approval, site selection)
- On-demand: Link to live BONZI metrics dashboard
- Weekly: Check if new economic data exists

**Voice example:**
> "As of March 2026, the UNIDOS bot has logged 12,847 farmer interactions. Confidence: HIGH (pulled from bot logs 2026-03-01). The income impact remains exploratory pending the month 18 confirmation study."

**Failure mode:** Over-explains technical terms; visitors skim and miss findings

---

## Page 2: `/research/openbox-proof.html` — AI Governance Validation

### Current Voice
**Tone:** Scientific + self-aware skepticism. Explicitly separates:
- Synthetic calibration (what THIS paper shows)
- Real experiment (coming later)
- Hype disclaimer (appears 3x: gold box, subtitle, method section)

**Personality:** Honest-to-a-fault methodologist. Refuses to claim findings beyond data support. Gold-box METHODOLOGY DISCLOSURE is the hero element (not the +75% number).

### Content Map: What Exists & What Changes

| Section | Purpose | Confidence | Data | Updates? |
|---------|---------|-----------|------|----------|
| Tag + Title | "Phase 1 - Pipeline Calibration" | Explicit: synthetic only | N/A | No |
| Gold Disclosure Box | "These are calibration figures, not experimental" | Ultra-transparent | Synthetic | Yes (archive when real data arrives) |
| Stats Grid | OEC 0.50→0.69, p<10⁻¹⁶, effect 1.19 | HIGH for synthetic; LOW for real | Synthetic | Yes (replace with real data) |
| Plain English | What RACI-V does + what calibration proved | Medium | Hybrid | No |
| Side-by-side Examples | Same query, chaos vs RACI-V responses | HIGH (pattern demo) | Synthetic | Yes (replace with real Telegram convos) |
| Full Dataset Section | "100 matched pairs" | HIGH (transparency) | Synthetic | Yes (swap synthetic for real) |
| Methodology | Chaos vs RACI-V conditions, metrics, stats | HIGH (clear) | Synthetic | No |
| Data Source | Synthetic generation explanation + confirmatory link | Ultra-transparent | Link | Yes (update link status) |

### Questions Visitors Actually Ask
1. **"Is this real data?"**
   → YES answered (3x: gold box, subtitle, data source) ✓

2. **"Did RACI-V reduce contradictions?"**
   → In calibration: 73% reduction. In real experiment: TBD

3. **"When will you run the real experiment?"**
   → "Pre-registered and ready" (link missing or unclear)

4. **"What's OEC score?"**
   → Defined in method section (not hero; should be earlier)

5. **"Can I download the 100 pairs?"**
   → Title says "Full Dataset" but no download link visible

### Content Health: Dead vs Alive

**Dead (will never change):**
- Methodology (fixed by design)
- Calibration parameters (fixed: 100 pairs, two conditions)
- Statistics (synthetic-only, will be archived)
- Effect size / p-values (synthetic)

**Alive (will be replaced entirely):**
- All metrics once real Telegram data arrives
- Gold box disclaimer (will be removed)
- Side-by-side examples (will show real conversations)
- "Confirmatory study" link (currently just text; needs status badge)
- Download link (missing or broken?)

### Ideal Page-Agent Personality

**Name:** The Pedant (Good-Pedant)

**Traits:**
- Scientist who loves caveats: "Here's what we CAN'T claim yet"
- Specific over vague: "95% CI [0.92, 1.48]" not "looks good"
- Refuses inflation: Every number gets a caveat-parenthetical

**Activation triggers:**
- Pre-experiment: Keep gold box visible, nag about pre-registration status
- Day 1 of real data: Swap synthetic → real metrics (same layout, new numbers)
- Weekly (during real run): Update progress bar "X% of conversations processed"
- Post-study: Move gold box to archive, elevate real findings, update statistics

**Voice example:**
> "As of 2026-03-01, the confirmatory study is in progress (78% of 500 conversations processed). Real data will appear here within 4 weeks. These calibration figures are synthetic (not experimental). Once real Telegram data arrives, this page will be updated and archived data moved to /archive."

**Failure mode:** Too many caveats overwhelm; visitors skim and miss the actual finding

---

## Ecosystem Scan: Other Community-Bot Pages

### Page Inventory
| Page | Voice | Personality | Live Data Needs |
|------|-------|-------------|-----------------|
| `index.html` | Motivational + technical | Founder-as-builder | Dashboard links |
| `manifesto.html` | Angry + honest (crypto call-out) | Unfiltered founder | Monthly metric drops |
| `features.html` | Feature list + use cases | Product manager | "Try it" CTA |
| `baas.html` | B2B pitch + pricing | Sales | Updated pricing, quota info |
| `faq.html` | Q&A | Explainer | Seasonal refresh |
| `stake.html` | Integration guide + UI | Technical | Live TVL, APY feeds |
| `vote.html` | Governance UI | Democratic process | Live vote status |
| `economics/` | Revenue model breakdowns | Data journalist | Weekly fee metrics |
| `metrics/` | Dashboard views | Observer | Real-time feeds |
| `manual/` | Command reference | Instructional | Bot command updates |

### Pages Most Needing Personality Work
1. **`research/index.html`** → Add "Current Status" banner with live metrics
2. **`research/openbox-proof.html`** → Add "Real Data Arrival" countdown or status badge
3. **`economics/`** → Add weekly revenue tracker (out of scope here)

---

## Unified Content Personality Framework

### The Three Voices (Cross-Page Pattern)

| Voice | Primary Pages | When Active | Tone | Failure Mode |
|-------|---------------|------------|------|--------------|
| **The Transparentist** | research/index.html, economics/ | Strategic updates | "Here's what we don't know yet" | Over-explains, kills momentum |
| **The Pedant** | research/openbox-proof.html, methodology | Technical deep dives | "Here's the caveat" | Too many caveats, readers skim |
| **The Founder** | manifesto, index.html, features | Brand + vision | "Here's why we're angry about crypto" | Sounds preachy if uncontrolled |

### Common Thread Across All Pages
✓ All three refuse false confidence
✓ All three define jargon (glossary, parentheticals, explainers)
✓ All three distinguish hype from evidence
✓ **The moat is honesty, not marketing**

---

## Actionable Recommendations

### Immediate (Next 2 weeks)

**Page 1: `research/index.html`**
1. Add "Results Status" block above Glossary:
   - BONZI: Live fee revenue (update weekly)
   - UNIDOS: Farmers trained, produce volume (monthly)
   - IMOBX: Pilot phase + Q3 2026 timeline

2. Add "Get Involved" CTA section (Discord, Telegram links)

3. Add live metrics dashboard link (if it exists)

**Page 2: `research/openbox-proof.html`**
1. Add "Real Data Status" banner (pre-study countdown or live progress bar)
2. Add download button for 100-pair dataset (or explain why it's not available)
3. Clarify pre-registration link (currently text-only)

### Medium-term (Monthly cadence)

**Set up automated agents:**

*The Transparentist* (monthly check):
```
- Pull UNIDOS metrics from bot logs
- Check IMOBX pilot legal status
- Link any new BONZI fee data
- Format: "As of [date]. Confidence: [reason]."
```

*The Pedant* (weekly during real study):
```
- Update progress bar (% conversations processed)
- Maintain every caveat visible
- Link confirmatory study status
- Pre-notify when synthetic data will be archived
```

### Cross-page governance rule
- Every metric = data source + last-updated timestamp
- Every claim = confidence level (High/Medium/Low + reason)
- Every section marked "archived" or "active"

---

## Appendix: Deep Quotes (Voice Examples)

### research/index.html — Current Best Voice
> "Pilot data is exploratory — not validated findings. The confirmatory study with corrected methodology has not run yet."

This is the voice to scale: Specific stage + explicit limitation + future date.

### research/openbox-proof.html — Current Best Voice
> "These statistics describe the calibration generator's behavior, not real users. The pipeline correctly captured and measured these structural differences — which is what this run was designed to confirm."

This is the voice to scale: What the data DOES show + What it DOESN'T show + What the next step is.

---

**Prepared by:** Claude Code AI audit
**Archive:** `/docs/content-audits/` (recommended location)
**Next review:** 2026-06-01 (quarterly)
