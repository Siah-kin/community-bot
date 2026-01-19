# Variant F: User Journey Paths

Focus: Three entry points for three user types. Self-selection before commitment.

---

## Core Insight

**Current problem:** We ask for wallet connection too early. Hesitant users bounce.

**Solution:** Let users self-select their journey. Wallet connection is LAST step, not first.

---

## NEW SECTION: After Hero, Before Pain Points

### "Start Your Way" Section

**Label:** "three paths, one destination"
**Title:** "choose how you want to begin"

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  [CARD 1: SAVVY]           [CARD 2: CURIOUS]      [CARD 3: CAREFUL]│
│                                                                     │
│  "I'm ready to launch"     "Show me how it works" "Let me watch    │
│                                                    first"           │
│  → Launch Token            → Try the Bot          → Read the Docs  │
│    (connect wallet)          (no wallet needed)     (no commitment)│
│                                                                     │
│  5 min to live token       Join demo Telegram     Whitepaper, FAQ, │
│  Free via EtherFun         Earn points today      see it working   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Card Copy

### Card 1: Savvy User
**Header:** "Launch Now"
**Subhead:** "I know what I'm doing"
**Body:** "Connect wallet → configure token → live in 5 minutes. Free via EtherFun (~$0.05 gas)."
**CTA:** "Launch Token →"
**Note:** "Requires wallet connection"

### Card 2: Curious User
**Header:** "Try First"
**Subhead:** "Show me how it works"
**Body:** "Join our Telegram. Earn points by helping others. See raids, tips, and leaderboards in action. No wallet needed."
**CTA:** "Join Demo →"
**Note:** "No signup required"

### Card 3: Careful User
**Header:** "Learn More"
**Subhead:** "I want to understand first"
**Body:** "Read the whitepaper. Check the FAQ. Watch the bot work in public channels. Take your time."
**CTA:** "Read Docs →"
**Note:** "Zero commitment"

---

## User Journey Maps (for reference)

### Savvy Path
```
Hero → "Launch Token" → Connect Wallet → Configure (name, symbol, fees)
→ Sign tx → Token live on EtherFun → Bot auto-deployed → Share link → Done
```

### Curious Path
```
Hero → "Try the Bot" → Click Telegram link → Join channel → Watch activity
→ Ask a question (earn points) → Help someone (earn points) → See leaderboard
→ Eventually: "Claim rewards" → NOW connect wallet → Hooked
```

### Careful Path
```
Hero → "Read Docs" → Whitepaper / FAQ → Understand the model
→ Watch public Telegram (lurk) → See real activity → Build trust over days
→ Eventually: "Try the bot" → Curious path begins
```

---

## Changes to Existing Sections

### Reveal Section (ATTENTION)
**Current:**
```
"launch your brand with a token and an ambassador engine."
```

**New:**
```
"free token launch"
"bot that earns for your community"
"tips funded by"
"trading fees." (purple)
```

### Statement Section (INTEREST)
**Current:**
```
"free token launch. AI-verified raids. real ETH payouts..."
```

**New:**
```
"launch free. bot deploys automatically. community earns from every trade.
no wallet needed to start. try the bot first. launch when ready."
```

### Demo Section (DESIRE)
**Add above chat demo:**
```
Label: "see it working"
Title: "real community, real activity, real tips"
Subtitle: "this isn't a demo. it's our actual telegram. join and earn."
```

### CTAs Throughout
**Primary:** "Launch Free" (for savvy)
**Secondary:** "Try the Bot" (for curious)
**Tertiary:** "Learn More" (for careful)

---

## Comparison Table Addition

Add row to existing comparison:

| | Bonzi | Galxe | Zealy | Mava |
|---|---|---|---|---|
| **Try before wallet** | ✓ earn points first | ✗ | ✗ | ✗ |

---

## Key Principle

```
ATTENTION  → No wallet needed (all 3 paths visible)
INTEREST   → No wallet needed (pain points, solutions)
DESIRE     → No wallet needed (demo, try bot)
ACTION     → Wallet for savvy, delayed for others
```

The hesitant user can spend **weeks** in the ecosystem before ever connecting a wallet. By then, trust is built.

---

## Mobile Considerations

On mobile, the 3-card grid becomes:
1. Stacked cards (swipeable)
2. Or: Single question "What brings you here?" with 3 options
3. Each option leads to appropriate path

---

## Implementation Notes

This is **additive** - we're adding a section, not replacing existing structure.

Insert after hero, before pain points. Rest of page stays the same.

The three CTAs should also appear in:
- Nav (subtle)
- Footer
- After pricing section
