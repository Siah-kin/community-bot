# Protected Systems - DO NOT MODIFY WITHOUT EXPLICIT USER APPROVAL

These systems have been carefully designed and tested. Any changes require user approval.

## 1. Spatial Audio System (index.html)

**Pattern:** `SPATIAL AUDIO`, `updateVolumeByScroll`, `magicalTrack`, `revolutionPlaylist`

**Design Intent:**
- Music plays in specific "rooms" based on scroll position
- Moby "God Moving Over the Face of the Waters" is the emotional payoff track
- It should trigger at the FEATURES section, not comparison section

**Original Zone Mapping (CORRECT):**
```
ROOM 1 (dark):   Top → solutions = Revolution playlist
ROOM 2 (mellow): features → demo, mission → links = Moby God Moving
SILENCE:         solutions, comparison, pricing
```

**DO NOT:**
- Move the Moby trigger point to a later section
- Remove the spatial audio concept
- Change zone boundaries without testing the emotional journey

**History:**
- 2026-01-18: Commit f6347ac broke this by moving Moby trigger from features to comparison
