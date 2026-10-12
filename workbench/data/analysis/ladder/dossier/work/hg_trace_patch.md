# Scratch (diag-hungry): the tracing copy that could not be built in this session

Not compiled, not played: the session's tool guard (tools/ladder_guard.py) allows no compiler, no play.sh and no
write outside data/analysis/ladder. This note is what the tracing copy should contain, for whoever has the bench.
Line numbers are solo/bots/m3b7/main.cpp.

## Where a bot can write under play.sh
- stdout is the protocol (helper.hpp 363-367: a LOG line goes into the replay and costs points), so not there.
- engine/run_game.py line 107 starts the binary with cwd = the bot's own folder. Safest sink: append to a file in
  that folder (std::fopen("hg_trace.log", "a"), one std::fprintf per line, std::fflush after each turn).
  Every dragon is its own process (main() builds one Bot, 5758-5760), so lines must carry id and round.
- Check that play does not change: same map, seed and side, traced against m3b7: the "line" and "events" fields of
  result.json and the bytes of game.replay must be equal (the trace only reads values and writes the file).

## What to log (for length 2 or 3, round <= 300, 26+ rounds since the last meal or birth)
- Hunger clock: last_growth_round (1394-1396) is 0 in a new process, so keep hg_born (first round seen in
  observe()) and use round - std::max(last_growth_round, hg_born) >= 26.
- In score_step (5017-5224) fill a member struct after each term:
  room, territory (5032-5033), tight / trapped / no_tail (5042-5052), the five target bonuses apart
  (5084-5095: pearl, soon, hot, unseen, portal) with survey.dist_pearl / dist_soon / dist_hot / dist_unseen,
  explore and far gain (5097-5110), pocket (5116-5119), eat bonus (5120-5124), spawn clear (5125-5133),
  zone pearl (5134-5136), centre pull (5137-5141), mate head beside (5142-5144), threat (5145-5168).
- In pick_direction: after 5336-5339 copy the struct into terms[k] and add look_gain (5338); after 5414 note
  route overrides; in the last loop (5449-5479) log, per direction: edge, enter_time, every term, the tie noise
  of 5459 and the final score; then one line with the chosen direction, head, ct.get_dir(), ally_heads.size(),
  enemy_heads.size(), route_target, escape_through, is_feeder(), zone_active.
- stride_value (795-803) calls score_step again after the choice; copy the struct before that.

## What the offline rebuild already says the log should confirm or break (hg_scan3.py, hg_agg3.py, hg_agg3b.py)
- the rebuilt score names the step taken in 83.1% of 95,236 hungry turns; the 17% it misses are the first place to read
- with 1-2 team mates in view and nothing in view, territory differs by 27 points (median) between the best and the
  worst step, the target bonus by 8 and far gain by 4
- with no mate in view and nothing in view, two or more steps are within 1 point of the best on 44.2% of turns
