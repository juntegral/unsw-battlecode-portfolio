---
name: known-map-preserving-rule
description: user rule 10-03 for adding universal logic — refactors keep the old 10 ladder maps replay-identical (real fixes: no big regression), change behaviour only where old tuning never reached (size gaps, >2400 cells, new shapes), no orientation dependence
metadata:
  type: feedback
---

When adding or changing universal logic in the meow bot (v61 lineage), behaviour on the old 10-map ladder pool (Default, Devil, Queen of Spades, Trauma, Schooltime, Portals, Autarky, Prisoners Dilemma, Slithery Fight, Trophy) must stay unchanged, while unseen/custom maps must not get weird overfit behaviour.

**Why:** 10-03 the user worried the base code was tuned before the queen-rule renewal and the new maps; we can't reset the bot, so improvements must target new rules + custom maps without losing old-map strength ("기존 맵에서는 행동변화가 없지만 다른 맵에서 과적합으로 인한 이상한 움직임을 하지는 않게… universal한 로직을 추가하는 경우에 지켜야 할 규칙").

**How to apply:**
1. Old-10 maps are calibration points, two tiers (agreed with QWQ and the user 10-03): refactors/generalisations must be replay-identical there (ident, all 10 × several seeds); real fixes (queen, big-map splitting) may change old-map play but must show no big regression there plus a gain in the targeted situation.
2. Change only in uncovered territory: size gaps (512–625, 1152–1701, 1701–2400 cells), beyond 2400 cells / W+H > 100, shapes absent from old-10 (tall maps).
3. Replace size step-functions with continuous rules pinned at calibration points + situation signals for extrapolation.
4. Rules must be rotation/transpose/flip invariant (e.g. center_map used `width >= 2*height` — orientation-dependent).
5. Verify: old-10 identity, metamorphic tests (rotated/transposed old-10 maps), no regression on unseen-style sets, improvement on the 7 new maps as a soft signal. Known old-10 failures (Portals queen r9 deaths) are exceptions to discuss with QWQ.
Findings 10-03: big-map mode (cells > 1200) tuned on only Slithery+Schooltime; queen rules off ≤600 (Devil/Portals/Dilemma 512); fixed FEEDER_APPROACH 15 / ~6.5-step target horizon; generators make no tall maps (blind spot). Related: [[no-fixed-map-optimization]], [[meow-team-repo]].

Size criteria (user 10-03): stop using raw map size as a decision criterion. Replace size-classification step rules (big-map mode 1200/r150, queen rules 600, centre pull 1000/700) with game-state signals that measure the intent directly (first-contact round, distance to the inferred enemy start, open space per unit, pearl income). Distances may scale continuously, preferably with in-game measured distances. Protocol limits (sonar range, 64x64 cap) stay. Replace one gate at a time, biggest first (big-map split stop).
