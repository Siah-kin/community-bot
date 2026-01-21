---
name: bonzi-web-design
description: Design system for Bonzi web pages and documents. Black/white/purple palette, musical rhythm (60-70% prose, 20-25% purple boxes, 5-10% accents), section smoothing, Win98 easter egg popups. Red/green only for status accents.
category: design
---

# Bonzi Web Design System

Design rules for Bonzi website pages and documentation. Maintains crypto-native credibility while being accessible. Supports both dark and light modes.

## Color Palette

### Primary Colors (from bonzivista.org)
- **Black**: `#0a0a0a` (dark mode bg)
- **White**: `#ffffff` (light mode bg)
- **Purple**: `#7c3aed` (primary accent - exact brand color)
- **Purple Light**: `#a78bfa` (hover states, secondary)
- **Gold**: `#d4af37` (links, highlights, connect button)

### Status Accents (USE SPARINGLY)
- **Green**: `#27ae60` - Success ONLY (claim complete, bug confirmed, tx success)
- **Red**: `#e74c3c` - Error/warning ONLY (access denied, failed, blocked)

**Rule:** Green and red appear ONLY for status feedback. Never decorative.

## Three-Box System

### Box Type 1: Technical Box (Most Common)
**Visual:** Purple sidebar + light gray bg (light mode) / dark gray bg (dark mode)
**Label:** "HOW IT WORKS"
**Purpose:** Explain processes and mechanics
**Use for:**
- How raids work
- Claim flow steps
- Token gate requirements
- Point calculations
- Technical architecture

### Box Type 2: Feature Box
**Visual:** Purple sidebar + very light purple bg / dark purple-tinted bg
**Label:** "KEY FEATURE"
**Purpose:** Highlight unique capabilities
**Use for:**
- Thanks Protocol mechanics
- DAO Tester Program perks
- Raid verification system
- Wallet linking benefits

### Box Type 3: Advantage Box (RARE - 1-2 per page MAX)
**Visual:** Black/gold sidebar + white/dark bg
**Label:** "ADVANTAGE"
**Purpose:** Strategic benefits, external validation
**Use for:**
- Base mainnet benefits
- On-chain transparency
- Community-driven governance
- Institutional-grade infrastructure

**Scarcity rule:** If you're using Advantage boxes more than twice per page, you're overusing them.

## Musical Rhythm Principle

### The Melody (60-70%): Plain Prose
- Natural narrative flow
- Introductions and transitions
- Context-setting explanations
- Section intros (MANDATORY before boxes)

### The Bass Line (20-25%): Purple Boxes
- Technical explanations
- Feature highlights
- Process breakdowns

### The Crescendo (5-10% MAX): Accents
- Green success states
- Red error states
- Gold highlights
- Win98 popup easter eggs

## Section Smoothing Rule (MANDATORY)

**Every section must:**
1. Start with 2-3 sentences of plain prose
2. Explain WHAT this section covers
3. Connect to previous content
4. THEN add boxes/details

**Never start sections with:**
- Bold statements without context
- Tables or lists
- Boxes
- Technical details without WHY

**Example - Wrong:**
```html
<h3>Token Gate</h3>
<div class="technical-box">
  Requires 100 VISTA or 1M BONZI...
</div>
```

**Example - Correct:**
```html
<h3>Token Gate</h3>
<p>Bug reporting is limited to token holders to prevent spam and ensure quality feedback. Here's what you need to participate.</p>

<div class="technical-box">
  <strong>Requirements:</strong>
  <ul>
    <li>100 VISTA staked, OR</li>
    <li>1,000,000 BONZI staked</li>
  </ul>
</div>
```

## Win98 Easter Eggs

The main UI stays dark/sophisticated. Win98 nostalgia appears ONLY on interaction as popups:

**Trigger moments:**
- Bug submitted → "Bonzi Assistant" dialog
- Claim success → Installer progress bar + "Complete" ✓
- Token gate blocked → System error dialog
- Achievement unlocked → Classic notification sound feeling

**Visual treatment:**
- Slight beveled borders (1-2px)
- Classic title bar with close button
- Works in both dark and light modes
- Appears as modal overlay, not inline

**Rule:** Win98 is seasoning, not the main dish. Users who remember it get the nostalgia. Everyone else sees a clean popup.

## CSS Structure

```css
/* === BASE COLORS (from bonzivista.org) === */
:root {
  --black: #0a0a0a;
  --white: #ffffff;
  --purple: #7c3aed;
  --purple-light: #a78bfa;
  --gold: #d4af37;
  --green: #27ae60;
  --red: #e74c3c;
}

/* === TECHNICAL BOX === */
.technical-box {
  background-color: var(--box-bg-light, #f8f8f8);
  border-left: 4px solid var(--bonzi-purple);
  padding: 16px 16px 16px 24px;
  margin: 16px 0;
  position: relative;
}

.technical-box::before {
  content: "HOW IT WORKS";
  position: absolute;
  top: -10px;
  left: 16px;
  background: var(--bonzi-purple);
  color: white;
  padding: 4px 12px;
  font-weight: bold;
  font-size: 10px;
  letter-spacing: 1px;
}

/* === FEATURE BOX === */
.feature-box {
  background-color: var(--box-bg-purple, #f5eef8);
  border-left: 4px solid var(--bonzi-purple);
  padding: 16px 16px 16px 24px;
  margin: 16px 0;
  position: relative;
}

.feature-box::before {
  content: "KEY FEATURE";
  position: absolute;
  top: -10px;
  left: 16px;
  background: var(--bonzi-purple);
  color: white;
  padding: 4px 12px;
  font-weight: bold;
  font-size: 10px;
  letter-spacing: 1px;
}

/* === ADVANTAGE BOX (RARE) === */
.advantage-box {
  background-color: var(--box-bg-light, #fafafa);
  border-left: 4px solid var(--bonzi-gold);
  padding: 16px 16px 16px 24px;
  margin: 16px 0;
  position: relative;
}

.advantage-box::before {
  content: "ADVANTAGE";
  position: absolute;
  top: -10px;
  left: 16px;
  background: var(--bonzi-black);
  color: var(--bonzi-gold);
  padding: 4px 12px;
  font-weight: bold;
  font-size: 10px;
  letter-spacing: 1px;
}

/* === SUCCESS/ERROR STATES === */
.success-state {
  color: var(--bonzi-green);
  border-color: var(--bonzi-green);
}

.error-state {
  color: var(--bonzi-red);
  border-color: var(--bonzi-red);
}

/* === WIN98 POPUP (Easter Egg) === */
.win98-popup {
  background: #c0c0c0;
  border: 2px outset #ffffff;
  box-shadow: 2px 2px 0 #808080;
  font-family: 'Segoe UI', Tahoma, sans-serif;
}

.win98-popup .title-bar {
  background: linear-gradient(90deg, #000080, #1084d0);
  color: white;
  padding: 4px 8px;
  font-weight: bold;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.win98-popup .close-btn {
  background: #c0c0c0;
  border: 2px outset #ffffff;
  width: 16px;
  height: 14px;
  font-size: 10px;
  line-height: 1;
  cursor: pointer;
}

/* Dark mode adaptations */
@media (prefers-color-scheme: dark) {
  .technical-box,
  .feature-box,
  .advantage-box {
    background-color: #1a1a1a;
  }

  .win98-popup {
    /* Keep Win98 gray even in dark mode - it's retro */
  }
}
```

## Writing Style

### Human Voice (Not Bot)
- Use contractions (you're, don't, we'll)
- Vary sentence length. Short punchy ones. Then longer explanatory ones.
- Add pauses... like this
- Keep language simple - explaining over coffee, not defending a thesis

### Avoid AI Fingerprints
- No em-dashes cramming ideas together
- No "validated," "leverage," "utilize"
- No "with [benefit] and [benefit]" stacking
- Specific numbers, not "greater impact"
- Break up long sentences into multiple shorter ones

### Crypto-Native but Accessible
- Explain jargon when first used
- Numbers > vague promises
- Show technical competence without gatekeeping
- Honest about limitations

## Dark/Light Mode

Both modes must work. Key considerations:

**Dark mode:**
- Purple accents pop against black
- Gold for links/highlights
- Slightly elevated card backgrounds (#1a1a1a)
- White text

**Light mode:**
- Purple accents on white
- Gold for links/highlights
- Light gray cards (#f5f5f5)
- Black text

**Win98 popups:** Keep the classic gray in both modes - it's the nostalgic contrast.

## Quality Checklist

Before shipping:

- [ ] **Section flow:** Every heading has 2-3 sentence intro
- [ ] **Musical rhythm:** 60-70% prose, 20-25% purple boxes, 5-10% accents
- [ ] **Box accuracy:** Technical/Feature/Advantage used correctly
- [ ] **Color discipline:** Red/green only for status, never decorative
- [ ] **Human voice:** No AI fingerprints
- [ ] **Both modes:** Works in dark and light
- [ ] **Win98 easter eggs:** Popups only, not inline styling

## Page Types by Journey Stage

Pages serve different purposes depending on WHERE the user is in their journey and WHO they are. The design toolkit stays the same, but application changes.

---

## ACQUISITION PAGES (AIDA Framework)

These pages convert strangers into users. AIDA (Attention → Interest → Desire → Action) is the guiding principle. Human design inputs steer the creative direction.

### Landing Page (Homepage)

**AIDA stage:** Attention → Interest
**Purpose:** Answer "what is this?" in 5 seconds. Convert to next step.
**Target audience:** First-time visitors, crypto-curious, potential community managers

**Framework:**
- Hero = Attention (one sentence, one CTA)
- Problem/Solution = Interest (why this matters to YOU)
- Social proof = Desire (others trust us)
- CTA = Action (clear next step)

**Rhythm:** 80% prose, 15% boxes, 5% accents
- Hero is ALL prose - no boxes above the fold
- Maximum 2-3 boxes on entire page
- Feature boxes only (no Technical - too much friction)
- 1 Advantage box maximum

**Tone:** Confident but not salesy. Numbers > adjectives. Show, don't tell.

**Win98:** None. Clean first impressions.

**Anti-patterns:**
- Don't explain HOW (save for features page)
- Don't list every feature (pick 3)
- Don't use Technical boxes
- Don't start with "Welcome to..."

---

### Features Page

**AIDA stage:** Interest → Desire
**Purpose:** Educate interested visitors. Answer "how does this actually work?"
**Target audience:** Visitors evaluating the product, comparing alternatives

**Framework:**
- Brief intro hooks interest
- Each feature section builds desire through understanding
- Comparison validates choice
- CTA converts desire to action

**Rhythm:** 60% prose, 30% boxes, 10% accents
- Each feature: prose intro → Technical/Feature box → details
- Technical boxes are primary
- 1-2 Advantage boxes for validation

**Tone:** Educational. Teacher explaining to smart student.

**Win98:** Light touch on interactions.

**Anti-patterns:**
- Don't dump features in a list
- Don't skip prose intros
- Don't use Advantage for basic features

---

### Token/DAO Page (Investor-Facing)

**AIDA stage:** Desire → Action (high-stakes)
**Purpose:** Build trust. Answer "is this legit? Should I put money in?"
**Target audience:** Retail investors, speculators, potential token holders

**Framework:**
- What it is (no hype, just facts)
- Proof (on-chain, verifiable)
- Mechanics (how it works, tokenomics)
- Risks (honest about downside)
- Action (how to participate)

**Rhythm:** 70% prose, 20% boxes, 10% accents
- Advantage boxes primary (external validation)
- Technical boxes for tokenomics
- On-chain proof links throughout

**Tone:** Institutional credibility. No moon talk. Proof > promises.

**Win98:** Never. Serious money territory.

**Anti-patterns:**
- No hype language ("revolutionary," "game-changing")
- Don't hide contract addresses
- Don't skip risk disclosures
- Don't promise returns

---

## PLATFORM PAGES (Existing Users)

These pages serve people already in the ecosystem. AIDA doesn't apply. They need utility, clarity, and respect for their time.

### Bot User Dashboard/Help

**Purpose:** Help bot users accomplish tasks. Answer "how do I do X?"
**Target audience:** Telegram bot users, community members using Bonzi daily

**User mindset:** Task-oriented. They came to DO something, not learn about us.

**Rhythm:** 55% prose, 35% boxes, 10% accents
- Short prose intros (1 sentence)
- Technical boxes for step-by-step
- Feature boxes when they unlock something new

**Structure:**
1. What this page helps with (1 sentence)
2. Quick actions (most common tasks, prominent)
3. Detailed guides (Technical boxes)
4. Troubleshooting (collapsed/expandable)

**Tone:** Helpful friend. Assume they know basics. Don't waste their time.

**Win98:** Yes for achievements, completions, rewards claimed.

**Anti-patterns:**
- Don't re-explain what Bonzi is
- Don't market to them (they're already here)
- Don't bury common actions
- Don't assume they read previous docs

---

### DAO Member Pages

**Purpose:** Governance participation. Answer "what's happening? How do I vote?"
**Target audience:** Active DAO participants, token holders engaged in governance

**User mindset:** Stakeholder. They have skin in the game and want influence.

**Rhythm:** 60% prose, 30% boxes, 10% accents
- Technical boxes for proposal mechanics
- Advantage boxes for governance wins/milestones
- Clear voting CTAs

**Structure:**
1. Active proposals (most important, top)
2. Your voting power / status
3. How governance works (Technical box, collapsed for veterans)
4. Past decisions / transparency log

**Tone:** Peer-to-peer. They're owners, not users. Respect their stake.

**Win98:** Light touch. Vote confirmed popup.

**Anti-patterns:**
- Don't hide proposals
- Don't make voting confusing
- Don't talk down to them
- Don't skip the "why" on proposals

---

### Documentation (Reference)

**Purpose:** Look up specifics quickly. Answer precise technical questions.
**Target audience:** Power users, developers, anyone needing exact details

**User mindset:** Reference mode. They have a specific question, want answer fast.

**Rhythm:** 50% prose, 40% boxes, 10% accents
- Shortest prose intros (1 sentence max)
- Technical boxes dominate
- Code examples welcome

**Structure:**
1. What this doc covers (1 sentence)
2. Prerequisites (Technical box if needed)
3. Content (short intro → Technical box → examples)
4. Related links

**Tone:** Precise, scannable. Assume expertise. No fluff.

**Win98:** Never. Frictionless reference.

**Anti-patterns:**
- No marketing language
- Don't over-explain basics
- Don't use Feature/Advantage boxes
- Don't write long prose

---

### Ethervista Community Pages

**Purpose:** Serve the OG Bonzi community. Answer "what's happening with our project?"
**Target audience:** Ethervista community members, long-term BONZI/VISTA holders, Discord/TG regulars

**User mindset:** Community member first, user second. They care about the project's success, not just their own tasks. Want transparency, updates, and to feel heard.

**Rhythm:** 65% prose, 25% boxes, 10% accents
- More narrative than bot users (they want the story)
- Technical boxes for tokenomics updates, mechanics
- Advantage boxes for community wins, milestones

**Structure:**
1. What's new (latest updates, top)
2. Community metrics (holder count, activity, treasury)
3. Upcoming (roadmap items, votes, events)
4. How to participate deeper

**Tone:** Insider. They're family, not customers. Honest about challenges, celebratory about wins. Use "we" freely.

**Win98:** Yes - especially for community milestones:
- Holder milestone → Celebration popup
- Community vote passed → "Update installed" dialog
- OG recognition → Achievement badge

**Anti-patterns:**
- Don't talk to them like new users
- Don't hide bad news (they'll find out anyway)
- Don't over-formalize (they know the vibe)
- Don't forget to celebrate community contributions

---

## UTILITY PAGES (System States)

These pages handle edge cases and system communication.

### Onboarding/Tutorial

**Purpose:** Guide first actions. Answer "what do I do first?"
**Target audience:** New users who just converted, need hand-holding

**User mindset:** Eager but uncertain. They said yes, now show them the path.

**Rhythm:** 65% prose, 25% boxes, 10% accents
- Numbered steps in prose
- Technical boxes for details
- Green success states common

**Structure:**
1. What you'll accomplish (1 sentence)
2. Steps (numbered prose → Technical boxes)
3. Success confirmation
4. What's next

**Tone:** Encouraging friend. Patient. Celebrate progress.

**Win98:** YES - perfect place:
- Step completed → Progress popup
- Tutorial done → Achievement unlocked
- First action → "Bonzi Assistant" welcome

**Anti-patterns:**
- Don't assume knowledge
- Don't skip steps
- Don't overwhelm with options
- Don't forget success confirmation

---

### Error/Status Pages

**Purpose:** Communicate system state. Answer "what happened?"
**Target audience:** Anyone who hit an error, gate, or unusual state

**User mindset:** Confused or frustrated. Need clarity and path forward.

**Rhythm:** 80% prose, 10% boxes, 10% accents
- Red/green status colors appropriate here
- Minimal boxes

**Structure:**
1. What happened (1 clear sentence)
2. Why (brief, if helpful)
3. What to do (clear action)
4. Help link

**Tone:** Calm, helpful. Facts and solutions. Not apologetic.

**Win98:** Yes for certain states:
- Access denied → System error dialog
- Maintenance → "Please wait..." installer

**Anti-patterns:**
- Don't blame user
- Don't be vague
- Don't hide support options
- Don't over-explain

---

## Page Type Quick Reference

### Acquisition (AIDA)
| Page | Stage | Prose | Boxes | Primary Box | Win98 |
|------|-------|-------|-------|-------------|-------|
| Landing | Attention→Interest | 80% | 15% | Feature | No |
| Features | Interest→Desire | 60% | 30% | Technical | Light |
| Token/DAO | Desire→Action | 70% | 20% | Advantage | No |

### Platform (Existing Users)
| Page | Audience | Prose | Boxes | Primary Box | Win98 |
|------|----------|-------|-------|-------------|-------|
| Bot Help | Bot users | 55% | 35% | Technical | Yes |
| DAO Member | Governance | 60% | 30% | Technical | Light |
| Ethervista Community | OG holders | 65% | 25% | Advantage | Yes |
| Documentation | Power users | 50% | 40% | Technical | No |

### Utility
| Page | Purpose | Prose | Boxes | Primary Box | Win98 |
|------|---------|-------|-------|-------------|-------|
| Onboarding | First steps | 65% | 25% | Technical | Yes |
| Error/Status | System state | 80% | 10% | Technical | Yes |

---

## When to Use This Skill

Activate when working on:
- bonzivista.org pages
- DAO page design
- Documentation pages
- Landing pages
- Feature explanations
- Any Bonzi web content

**First step:** Identify page type, then apply that type's rules.

## Integration Notes

- **Domain:** Bonzi web pages and documents only
- **Conflicts:** None
- **Dependencies:** None
- **Related:** imobx-whitepaper-design.skill (inspiration source)
