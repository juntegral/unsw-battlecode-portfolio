# Added current-bot coverage — fixed before any selected replay deep reading

The original lowest-ID selection has 25 unique games, mostly historical by design.
Keep every one of them. To answer where the latest bot stands, add the two lowest
numeric game IDs in W12 per nonempty win, near-miss and lead-loss class. Deduplicate.
For every added W12 win, add a loss against the same map/opponent from the most
recent earlier wave having such a loss; if several, use its lowest game ID. This is
a deterministic era-coverage rule, not a choice based on inspecting replay moves.
No selected replay has been deeply read at the time this rule is written.

The full population and class definitions are unchanged. The combined selection is
frozen in selection-v2.json before the deep reader is run. All resulting replays
receive round/dragon pointers and a narrative. Cases illustrate measured classes;
they are not a representative estimate of their incidence.

Layout sensitivity: the original portal-presence interaction is singular because
every outcome-informative current map contains portals. Report this result. Also
fit an explicitly exploratory interaction of r100 head ratio with continuous kelp
edge fraction, per +10 percentage points. Map main effects stay unidentifiable
under map fixed intercepts. Do not rerun or replace the prespecified main models.
