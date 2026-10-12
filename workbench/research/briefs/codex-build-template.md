# Codex BUILD phase: one v1.8 work item behind a new switch (no games)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §4: pre-registration, mechanism criteria, identity, short comments.
- `docs/WORKQUEUE.md`, section Q: the item named in TASK below.
- `versions/v1.8/VERSION.md`.
- `docs/arch/terms.md`. First-step terms change rankings; static terms repeated in the DFS do not.
- `rules/` (1.2.3).

TASK: see the first line of the prompt that launched you.

## Do
1. **Implement the item in `versions/v1.8/bot`** behind a NEW `constexpr bool` switch in `params.hpp`, default **false**.
   - Use `if constexpr`, so the off build compiles to v1.8's exact instructions. A previous change slowed the search by one ply and broke identity.
   - Comments: one short line, only where something isn't obvious.
2. **Pre-register** in `versions/v1.8/VERSION.md`, as a new section with the real time from `date`, before any game:
   - where it plugs in;
   - its strength next to `terms.md`;
   - the expected board;
   - **mechanism criteria only**: it fires in the intended situations; the intended state change is visible on boards; nothing breaks (identity with the switch off, CPU, errors). No win-count gates.
   - **Measure "no harm elsewhere" causally.** On/off games diverge after the first changed decision, so raw death counts after that point are noise: per-key increases run about 50%. Do not gate on them.
     - **Gate on the changed decisions (same input):** did the new choice survive its move? Would the old choice have died (oracle)? Does the new choice lead to a death within a few rounds that the old one avoids?
     - **Report** raw counts and queen lifetimes per key in both directions (longer vs shorter) as context only.
     - Do not gate on a measurement that exists only in the on arm (for example, prediction tags).
3. **Make the builds:**
   - `exp/<task>/bot-on`: a copy of `versions/v1.8/bot` with the switch on;
   - `exp/<task>/bot-off`: a plain copy.
4. **Write the run spec** `exp/<task>/spec.json` in `exp/v14/runq14.js` format. Look at `exp/q2/` and `exp/v16/q1/spec-*.json` for examples: an array of lanes with name, bot, opponent, maps and seeds.
   - Sets: the item's maps, plus the identity keys below, against `bots/proxy4_king` and `exp/q2/bot-hunter`.
   - Identity keys: 6 or more keys covering an online map, a sprint map (`maps/sprint/`) and a generated map, with the switch off vs `versions/v1.8/bot` behaviour.
   - Keep it at 200 games or fewer.
5. **Write `exp/<task>/ANALYZE.md`:** the exact analysis steps and tools for after the run (`UNSW_RULES=123` for replay tools), mapped to each criterion.

## Do not
- run games (the coordinator runs the spec outside your sandbox);
- commit;
- touch the network;
- change other switches or defaults.

Write scope: `versions/v1.8/bot/**`, `versions/v1.8/VERSION.md`, `exp/<task>/**`.

Finish with `exp/<task>/BUILD.txt` (5 lines):
- switch name;
- files changed;
- spec path and game count;
- what the coordinator should run;
- any risk.
