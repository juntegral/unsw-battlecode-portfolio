# Builder: ptarget

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) and `data/codex/astra/qwq3/report.md` section 1 with its `details.md`
first. Write only under `data/codex/build/ptarget/`.

Case: game 1477042 (Stripes, `data/online/live-one1/b1477038/M1477042.replay`), our dragon id 6, length 3, spends r15 to r159, 145
turns, beside one portal mouth without eating. The approach survey takes the pearl in the one-cell room behind the portal as its
target (lines about 3144-3173 of `one5-bot/main.cpp`; find the same code in this file) and pulls the dragon to the mouth, but the
step through the portal is then rejected by the dead-end terms (tight -27000, pocket -4000), so it turns back and is pulled again.
Three pearls it could see on the other side were never eaten. Over 90 games our dragons spend 224 turns a game like this.

Task: in `main.cpp` (working source, every switch OFF by default; `main.base.cpp` is the same file untouched) add
`constexpr bool TARGET_REACHABLE = false;`. When on, a pearl (or a soon-to-bear or hot tile) is not used as an approach target,
by any of the terms that pull a dragon toward pearls it is not adjacent to, when the only known way onto its cell is a step the
bot's own entry check rejects for this dragon as things stand this turn (a known one-cell room behind a portal or a kelp pocket
that is not harvestable by the bot's own harvest rules, for this dragon's length). Use the bot's existing predicates for
"would be rejected" (dead end, room, pocket, harvestable, portal_dead); do not write a second opinion of what a dead end is.
The pearl stays a target for a dragon that the rules do allow in (a harvester, POCKET_LOOP, HARVEST_PORTAL cases).
Requirements:
- switch false = same program as `main.base.cpp` (guard every statement with the constant; no state updated when off): compile
  both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it. `main.on.cpp` with the switch true compiles.
- CPU: no extra flood per pearl; decide per target cell from its four edges and what the survey already knows.
- No comments beyond one short line, no map names, no size tables.
- `diff -u main.base.cpp main.cpp > ptarget.diff` and `done.txt`: lines changed, sha1 result, exactly which targets are dropped,
  whether the rule would have dropped the (17,9) pearl for dragon 6 at r17, r21 and r61 of game 1477042 (work it out from the
  replay), and what would show it is wrong (pearls in harvestable rooms no longer fetched).
You cannot play games on this machine; do not try.
