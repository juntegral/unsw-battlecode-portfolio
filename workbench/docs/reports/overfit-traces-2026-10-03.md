# Overfitting traces in v61 (Oct 3)

**Short version.** Much of v61 was tuned on the old 10-map ladder pool, before the queen rules and the new maps. Several rules switch on raw map size or shape, and their cut-offs sit between those 10 maps. On unseen maps this can change behaviour for no game reason. We can fix most of it without changing play on the old 10 maps at all.

## Signals
- **Placebo test.** Changes that should do nothing come out at −10 and −14 on the official maps, but +5 and −3 on generated maps (160 games each). v61 sits on a peak tuned for the official maps.
- **Earlier gains carried over less.** v55 vs v53 scored 65% on the tuning maps but 51% on generated maps it had never seen (`work/plan.md`).
- **New maps.** When the new maps arrived on Oct 2 we went 0/15 on Australia and Islands. Across 228 meow ladder games we are 21/59 on big maps (over 1,200 cells), against 61/101 on small ones.

## Where the code depends on the known maps

| Rule | What it does now | On the old 10 maps | Risk on unseen maps |
|---|---|---|---|
| Big-map mode | Above 1,200 cells: the leader grows from round 150 instead of 300, with different trade and ram rules | Tuned on only 2 of the 10 (Slithery 1,701 and Schooltime 2,400) | The 1,200 cut sits in an empty gap (1,152–1,701). Nothing above 2,400 cells was ever tuned. Ties in with our big-map record and with splitting half as often as opponents on big maps |
| Queen rules | On only above 600 cells | Off on Devil, Portals and Dilemma (512) | The 600 cut sits in a gap (512–625). On Portals our queen dies at round 9 in 11 of 34 games |
| Centre pull | ≤1,000 cells and (width ≥ 2 × height, or ≤700 cells) | Autarky (54×18) gets it | The same map turned sideways (18×54) would not. Behaviour depends on orientation |
| Fixed distances | Feeder approach 15 tiles; target values fade beyond ~6.5 steps (since v60, FAR_GAIN adds a weak long-range pull) | Largest old map has width + height = 100 | On 64×64 maps (128) everything is proportionally shorter (Zhe's idea #9) |
| Fixed clock | Feeding starts at round 400 (round 300 when our queen is alive, which is rare); queen splitting stops at round 200 | Set on the old map sizes | Big maps need more travel time |
| Room-size rules | Rooms ≤120 cells send spare dragons out through the nearest portal; pocket cap 48 | Tuned on Queen of Spades rooms and one Australia pocket | Could push dragons through a portal into danger on unknown layouts |

**Blind spot in our tests.** The generated map sets (139 maps) contain no tall maps (height ≥ 2 × width), so they can't catch orientation problems.

## Proposed rule for adding general logic
1. **The old 10 maps are calibration points.** Refactors and generalisations must keep play there replay-identical. Real fixes (queen, big-map splitting) may change it but must show no big regression there (QWQ, Oct 3).
2. **Change behaviour only where the old tuning never reached:** the size gaps (512–625, 1,152–1,701 and 1,701–2,400 cells), maps above 2,400 cells, and shapes the old maps don't have, such as tall maps.
3. **Replace size step-functions with smooth rules** that pass through the old values. Outside the old range, use game-state signals such as first-contact round, density and distances.
4. **No orientation dependence.** The same decisions on rotated, transposed and mirrored maps.
5. **Check four things:** identical play on the old 10 maps; rotated and transposed copies of them; no loss on unseen-style maps; and, as a soft signal, gains on the 7 new maps.

## First fixes (old 10 maps unchanged)
- **Centre pull:** use "long side ≥ 2 × short side" instead of "width ≥ 2 × height".
- **Feeder distance (Zhe's #9):** `15 + max(0, width + height − 100) / 4`. That is 15 on every old map and 22 on 64×64.
- **Big-map mode:** blend the two settings inside the 1,152–1,701 gap. Above 2,400 cells, set split and feeding timing from game state.
- **Portals queen deaths:** this is a failure on an old map, so it is an exception to rule 1. It needs QWQ's call.

## A measurement we can run first
Play v61 on the old 10 maps and on rotated and transposed copies of them. They are the same games with a different layout. Any gap between the two results shows how much v61 relies on knowing the layout. This uses CPU only.
