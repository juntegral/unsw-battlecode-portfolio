---
name: slay-queen-rules
description: Game rules changed 2026-10-01 (unswbc 1.2.3 "Slay Queen") — win by the longer queen (lowest-id dragon 0/1, dead = 0), ceil(L/4) free steps; ladder reset; plan v1.8
metadata:
  type: project
---

On 2026-10-01 (right after the sprint bracket) the organisers changed the rules (unswbc 1.2.3; docs re-fetched into unsw-swarm `rules/`):
- **Win at r500: the team whose queen is longer.** The queen is the team's lowest-id dragon (id 0 for one team, id 1 for the other). A dead queen counts 0, so losing the queen loses to any team with a living queen. Tiebreaks: longest living dragon, then total length.
- **Free steps:** a dragon of length L takes its first ceil(L/4) steps per turn free (cost max(0, x − ceil(L/4))). Long dragons are fast; threat reach grows with length.
- Ratings reset (per-submission rating with per-map offsets; first submission 1500); continuous autoscrims 3/hour once a bot is active; all submissions idle. New maps "in the coming days". Teaser: "One smells blood in the depths of the ocean floor..."

**Why:** every "longest = king" assumption in the bot (sf, CONV2, FORTRESS gathering, H3, king safety) is now wrong; the queen must survive and receive all conversion; killing the enemy queen wins outright.
**How to apply:** local games use the 1.2.3 engine (`tools/unswbc123`, later `tools/unswbc`); treat old-rule results as mechanism history only; the qualifier line is v1.8 = v1.7 + queen (Q1 conversion→queen, Q2 queen safety / enemy-queen assassination / free-step reach). First upload only with a complete build ([[upload-only-rule]]). Related: [[qualifier-timeline]].
