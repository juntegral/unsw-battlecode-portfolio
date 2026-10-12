# Codex brief: architecture diagrams of the bot (decision flow, scoring terms, overrides)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. This is our UNSW Battlecode 2026 bot (deep-sea dragon game; team 583). Read `CLAUDE.md` and `ENGINE.md` first.

## Why
The user decided (2026-10-01) that from now on we develop **diagram-first**. Several mechanisms did not behave as intended:
- A rule "fired" but heads did not move, because its pull was weaker than other scoring terms.
- An older rule overrode a new one after a hand-off.
- A tie rule ceded the whole centre on symmetric maps.

We need an accurate map of how one dragon's turn is decided, so new rules can be placed and weighted correctly.

## Subject
`versions/v1.3/bot` is the current qualifier candidate base. Also note where the modules in `versions/v1.4/bot` (opening: `opmod.cpp`, `opdb.hpp`) and in the Portals module (`ptmod.cpp`, `ptmap.hpp`, already in v1.3) hook in. Read the code; do not change it.

## Deliverables (all in `docs/arch/`, Korean prose, English identifiers)
1. **`flow-turn.md`.** A Mermaid flowchart of one dragon process's turn, from reading input to printing the action:
   - world update: vision, sonar, beliefs, the C2 length memory, map recognition, `kingClass`;
   - engine dispatch: policy row → FORTRESS / SWARM / the Portals mode, and the `decideImpl<...>` instantiations;
   - every early-return gate in order: doom / escape split, splits (sx, sr, harvest split, frag…), harvest script, the Portals module, the opening module;
   - goal selection: sd / claims / frontier allocation / harvest target / gathering / conversion;
   - move scoring and search;
   - tie-breaks and the final action plus its indicator tag.
   - Every node cites `file:line`. Every branch names its gate (the flag or condition).
2. **`flow-swarm.md` and `flow-fortress.md`.** The same flow at finer detail for each engine. Mark which branches are compiled out (`if constexpr`) and which are runtime-gated.
3. **`terms.md`.** A table of every term added into a move's or candidate's value. Columns:
   - name, `file:line` and formula;
   - parameters, with their values from `params.hpp` / `engcfg.hpp` / `policy.hpp`;
   - sign;
   - which engine/rows it applies to;
   - a **static scale estimate**: the typical magnitude in common situations, worked from the formula. Example: "pearl adjacent: +50; goal pull 0.4/tile → +2.8 at 7 tiles".
   - Group the terms: food, goal, safety/threat, splitting, conversion, king, module-specific.
4. **`overrides.md`.** Every place where one rule pre-empts, cancels or overrides another, with `file:line`. For example:
   - harvest preempts the opening split;
   - the trade veto ends a hold;
   - FORTRESS is used before recognition;
   - which goal wins when several are set.
   Note the known failure each one caused, where our docs record it (`versions/*/VERSION.md`, `DECISIONS.md`).
5. **`flags.md`.** Every `constexpr bool` / config switch: its value in v1.3, what it gates, and the files that read it.
6. **`unknown-maps.md`.** Exactly what the bot does on a map it does not recognise, turn by turn: which engine, which tables are skipped, and which code paths become no-ops (`mapFountAt` / `mapTerrAt` / `frontdb` / `ptmap` / `opdb` fall back to …). This matters most: the qualifier is played on unseen maps.

## Rules
- **Read-only on code.** Write only `docs/arch/**`. Do not write in `bot/`, `versions/`, `exp/`, `eval/`, `legacy/`, `data/` or `.cache/`. Do not commit; the coordinator commits.
- **Accuracy over completeness.** Every claim cites `file:line`. When unsure, say so. Before finishing, cross-check by grepping each function's call sites.
- No network and no uploads. Do not read opponent bot sources.
- **Target:** by 14:30 KST. Write `docs/arch/SUMMARY.txt` last: 10 lines naming the biggest override risks and the terms that dominate typical decisions.
