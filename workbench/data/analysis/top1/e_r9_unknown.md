## 9. Things I could not determine from replays

- **What any other bot knows.** A replay shows that forgot, WHQ and Vibing++ keep feeding around a cut and that
  SSS does not; it does not show whether they follow a record, a sighting or nothing at all (SSS's feeders die one
  step from the head, which needs no memory). The same for their clock: unit count or map size give the same table.
- **Our own dragons' beliefs after the "stride" run.** Later builds seal the ping. The key is in the bot source; I
  did not copy it here. Everything said about belief rests on 78 games of the earlier live bot (56 on small maps),
  plus the reading of today's source, in which the record code is as described.
- **Which rule made a given cut.** A replay gives the free cells, the room ahead and the distance of the nearest
  enemy head at a cut; it does not say whether the bot cut because of a pocket (`escape_child_size()`), because it
  was in an enemy's reach (the `cornered` split) or while harvesting. Nor what would have happened without the cut.
- **Why a given feeder died where it did**, in the sealed games: the record it held is not visible. In the readable
  games only its last ping is, one turn old.
- **Whether WHQ's big dragons that die by the suicide order are a rule or an accident.** 312 dragons of 15+ in 159
  games, 11 of them the team's longest at that moment (the 65-long of game 20, the 18-long of game 2), no time-out
  flag on any but 5. Most are eaten by a team-mate; some are not (the 70-long of game 14).
- **Whether the test builds really convert better on small maps** (0.71 against 0.65, no cut contrast) or 25 races
  happen to say so, and if it is real, which change did it.
- **What the earlier trials `rl1` (rally) and `eg1` (`ENDGAME_ROUND` 350 / 450) gave:** queued in the log, no result
  recorded. What cards #14 and #22 tested in detail: not in the log.
- **What the rule does to wins.** Nothing here was played. The size of candidate 5 is inferred from contrasts
  inside our own games, and the one comparison across teams that could have carried it (per-pearl conversion) shows
  no gap to our opponents.
- **The cost of an age rule for the record on big maps**, where news of the true leader is old for most of the team:
  whether far dragons would switch to regional leaders more than they already do (36-41% of our deaths by choice
  there are next to a bigger dragon that is not the longest). Only a played test can say.
- **What a dragon would have done had it not died for a stub**: walked to the true leader, or stood still. The
  count of "dragons that could feed without the belief test" (9.3 against 5.2 in rounds 400-424) is geometry, not
  behaviour.
- **Terrain beyond closed and open.** Completeness by map (Portals 0.85 to Around UNSW 0.35) and cuts by map are
  measured on 15 maps; which property of the ground drives them (corridor width, the size of the home region,
  portals between regions) I did not separate, and the qualifier maps are new.
- **Pearl spawn intervals**, hidden in the replay: whether a pearl left lying in the zone cost the tile a spawn is
  inferred from the rule ("a pearl appears only on an empty tile"), not seen.
