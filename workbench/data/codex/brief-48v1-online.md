# What changed in 30 online games: live bot against live bot + card 48 first build

Two sets of 15 online games against the same opponent (Big Bobs Bots, team 946), the same 15 maps, same hour:
- old (live bot v47): `data/online/smoke/qn48v1-bob1-old/` (`M<id>.replay`, `game-<id>.json`)
- new (v47 + QUEEN_NO_FEED on: our queen takes no feeding role): `data/online/smoke/qn48v1-bob1-new/`
State and pairing by map: `data/online/smoke/qn48v1-bob1.json`, summary `qn48v1-bob1-result.txt`.
We are team 1119; find our side per game yourself. Replay parsing and every definition below already exist for
ladder replays in `data/analysis/ladder/dossier/count_dossier.py` (same format); reuse its definitions, write your
own short script.

## Count, per game, ours and theirs
1. map, result, how it ended (elimination / longer queen / longest dragon / total length), last round.
2. our queen (lowest starting id of the side): alive at the end; if dead, the round and the cause exactly as the
   replay records it (head-on as the mover, head-on as the one hit, wall, own body, another body, no action, ...);
   and for a queen that died from round 300 on: was the dragon she ran into, or the dragon nearest to her head when
   she died, our own longest dragon (yes/no, with its length). Queen length at r100, r200, r300, r400 and at the end
   (0 when dead).
3. our longest dragon at r300, r400 and the end; dragons alive at r300, r400, end; total length at the end.
4. pearls eaten by r100 and by r300; splits by r100; number of turns the queen split.

## Output: `data/local/card48/online-v1/table.md` (60 lines or fewer), English
- A. per set (old, new): games, wins, how the games ended, and the means of everything above.
- B. queen deaths by cause and by round band (0-100, 101-300, 301-499), old against new, as counts.
- C. one line per map: old result -> new result; queen (death round and cause, or alive with length) old -> new;
  our longest at the end old -> new; dragons alive at r400 old -> new.
- D. three or four plain sentences: what is different between the sets beyond the queen no longer dying into our
  leader, and what is the same. Counts only, no opinion on whether to ship. 15 games a side: say where a difference
  is one or two games.
Also `rows.jsonl` (one row per game). Write `data/local/card48/online-v1/done.txt` (one line) last.
Write only under `data/local/card48/online-v1/`. No network, no posts.
