# Brief: tools/smoke_pick.py — pick replays where a change kicks in

Repo: unsw-swarm (this dir). Another job is writing tools/smoke.py right now: do NOT touch tools/smoke.py.

Goal: after an online smoke test, a teammate (Zhe) wants a few replay ids to eyeball, namely games where our change actually fired.

`python3 tools/smoke_pick.py <download dir> [--us 1119] [--n 5] [--focus queen|split|feed|all]`
- The input dir is what `node tools/online.js download` writes: game-<id>.json, M<id>.replay, events-<id>.jsonl.gz, index.json. Read those formats from online.js and existing parsers in tools/ (replay.js, export_replay.js) and from the battlecode repo's replay.py at ~/01. Project/개인 프로젝트/battlecode/replay.py (import it via sys.path; do not copy it).
- Per game, for our team, compute cheap facts:
  - win/loss, map;
  - our queen (dragon id 0 or 1 on our side): death round and cause, portal crossings, rounds alive;
  - splits in rounds 150-300;
  - suicides from round 300;
  - longest length at the end.
- Rank games by how strongly the focus behaviour shows up (e.g. queen: survived long or crossed a portal; split: many r150-300 splits; feed: many suicides), with losses first among ties.
- Print the top N as a short table with the game id, map, result and the facts.
- Write the same to <dir>/pick.md.
- No network, no keys, python3 stdlib only, `python3 -m py_compile` must pass.
- Test on any existing download dir under data/online/ (list them; pick one with replays).
- Leave the changes uncommitted.
- Write data/codex/report-smoke-pick.md, under 15 lines.
