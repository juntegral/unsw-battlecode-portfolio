# Codex brief: our IDEA BOOK — everything we learned, organised to pitch to a new team

You work in `~/01. Project/개인 프로젝트/unsw-swarm`.

## Why
The user may join another team soon. They want a ready set of ideas to propose, each backed by evidence: what we found, what works, what failed and why, and what to try next. This is a synthesis of our repository, not a new data study.

The game rules changed on 2026-10-01 (unswbc 1.2.3, "Slay Queen"):
- the longer queen (each team's lowest-id dragon, id 0 or 1) wins at r500;
- a dead queen counts as length 0;
- the first ceil(L/4) steps of a turn are free.

So every idea must be stated for the new rules, with old-rule evidence marked as such.

## Read
- `AGENTS.md`, `DECISIONS.md`, `docs/WORKQUEUE.md`;
- `docs/arch/*.md` (flows, terms, flags, unknown maps);
- every file in `research/observations/`, especially:
  - `general-principles.md`, `small-maps.md`, `observability.md`, `conversion-protocol.md`, `pocket-harvest.md`, `spatial-occupancy.md`, `sprint-commentary.md`;
  - `mapgen.md`, `duels.md` if it exists;
- `research/KNOWLEDGE.md`;
- `versions/*/VERSION.md`: the results and verdict sections;
- `maps/generated/MANIFEST.md`, `maps/sprint/README.md`;
- `rules/structure.md`, `movement.md`, `execution-order.md`, `splitting.md`, `death.md`.

## Write `research/IDEA-BOOK.md` (in Korean)
1. **3-minute pitch:** who we are, what we bring (tools, data, methods, findings), and the 5 ideas we would push first under the new rules.
2. **The new rules and their strategic consequences:**
   - queen survival over queen length (new-rule elite games: both queens dead in 91%);
   - assassination;
   - a hedge between the backup and the queen;
   - free steps.
3. **Idea catalogue.** Group the ideas by theme:
   - queen survival;
   - assassination;
   - conversion and hedging;
   - exploration and observation (small pieces as scouts);
   - intake (eating pearls in enemy reach);
   - duels and trades (ram propensity by length and local balance);
   - cohesion (spacing about 3 tiles);
   - not sealing allies;
   - small boards;
   - dead ends, mazes and portals;
   - map-independent runtime rules;
   - engine choice;
   - sacrifice efficiency (L3 drops 2);
   - free-step use.

   For each idea give:
   - **evidence:** elite online data, local mechanism checks or admin hints, with file paths and N;
   - **status:** mechanism-verified / hypothesis / tried and failed (and why);
   - **how to build it:** the planner term or gate, and its first-step-only caution;
   - **risks and failure cases.**
4. **Assets we can share:**
   - test beds: 35 generated maps, 7 rebuilt sprint maps, held-out bundled maps;
   - proxies;
   - analysis tools: mass_ledger with the 1.2.3 rules flag, reach/boxing/forced/drift scripts, board pictures, replay2map;
   - data: 21k top games, the elite collections, the sprint bracket;
   - the Codex research pipeline.
5. **Method lessons:**
   - local proxy numbers are poison;
   - mechanism checks;
   - pre-registration;
   - identity with switches off;
   - "past verdicts are not direction";
   - the static-threat-per-DFS-step lesson.
6. **Open questions and the next experiments,** ranked.

Also write `research/idea-book/ideas.json`: one object per idea, with theme, title, evidence paths, status, implementation and risk.

## Rules
- **Write scope:** `research/IDEA-BOOK.md` and `research/idea-book/**` only. Do not commit.
- No network, no uploads, no games.
- **Accuracy:** quote numbers exactly as they appear in the sources, with the file path. Never invent results. Label every claim as [사실] (with its source) or [해석].
- **Target:** about 2 hours.
