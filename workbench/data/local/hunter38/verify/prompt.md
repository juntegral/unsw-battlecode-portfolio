# Independent check: how our queen dies (card #38 follow-up)

You are checking claims that are about to be told to two teammates as findings. Trust in these numbers matters
more than speed. Recount from the raw replays yourself; do not start from the earlier script's output. Nobody
reads your chat output; only the files you write count.

## Background
- Team "meow" in UNSW Battlecode. Two teams of dragons eat pearls and grow. Dragons 0 and 1 are the queens. At
  round 500 the longer queen wins and a dead queen counts as 0; only when the queens tie does the longest dragon
  decide. A dragon of length L gets ceil(L/4) free steps per turn and can pay length for more. The board wraps.
- Our bot's source: `~/meow-release/mybot2/main.cpp` (read only, about 5,600 lines). "main" below means this bot.
- Replays (local games, our bot on both sides in different variants):
  - Hunter run, 68 games per arm: `data/local/hunter38/replays/` (`base_*` = main, `candidate_*` = main with the
    QUEEN_LOOP switch on; the opponent in both is main with a queen-hunting switch). `data/local/hunter38/README.md`
    and `result.md` say which side is ours in each file.
  - Check run against plain main, 16 games per arm: `~/meow-loop-out/card-38/attempt-1/replays/`.
- A replay parser and the definition of "our queen" and of death causes exist in
  `data/local/hunter38/harness/work/card_38_check.py`. You may reuse its parsing functions (read them first and
  make sure you agree with what they do), but classify and count yourself.
- An earlier script counted these: `data/local/hunter38/deaths/count.py`, results in `deaths/summary.md` and
  `deaths/rows.json`. Do NOT read them until your own count is finished. Then compare and explain every difference.

## Claims to test
A. In the hunter run (both arms together) our queen died 28 times by hitting a wall and 16 times by hitting her own
   body. About two thirds of each were "forced": at the start of the fatal action she had no legal first step
   (every neighbouring tile was a wall or a dragon body). About two thirds of each happened before round 50.
B. In the forced cases she had walked into a pocket in the rounds before (the room reachable from her head shrank).
C. On some maps the early death repeats in every game at nearly the same round (for example autarky_v0 at round 9,
   on both arms, both seeds, both sides), which would mean it is systematic and not bad luck.
D. In the games that ended on the queen rule in the hunter run (5 with the switch off, 6 with it on) and in the
   trauma games (4 per arm), the switch-on queen is already shorter at round 100, eats fewer pearls before round
   300 (trauma: 0 against 21), and after round 300 the enemy queen out-grows ours more than with the switch off.

## What to find out, beyond recounting
1. For A to C: WHY does she die by wall or own body so early? Decide between the candidate explanations with
   evidence, and say which you can rule out:
   - she is boxed in at or near her spawn by our own dragons or by the map (look at the actual board around her in
     the rounds before, for at least 8 of the deaths, including every repeated early case);
   - the bot chooses the fatal step although a legal step exists (find the decision in `main.cpp`: what does the
     queen do when her preferred move is blocked, what is the fallback when no move scores, is there any code that
     moves into a wall or herself on purpose, for example to shed length or because a move list is empty);
   - something else (a split or shed that leaves her head with no exit, a paid multi-step move, the hunting
     opponent closing the exits, a timeout or missing action).
   For the cases classified "had a safe move", check by hand whether the safe move was real.
2. Does the same early wall or own-body queen death show in the check run against plain main (16 + 16 games)? The
   earlier count found almost none there (2 wall, 1 own body). If so, why is the hunter run different: is it the
   opponent, the 17 maps against 4 maps, or the seeds? Name the maps where it happens and those where it never does.
3. For D: are the numbers right, and what can honestly be said with 4 to 7 games per line? Is "the enemy queen
   grows more when ours loops" supported, or is it within what four games give?
4. Anything in the definitions that would mislead a reader (for example "forced" measured at the enemy's action
   start for head-on deaths, dead queens counted as zero in means, rounds labelled 0 to 499).

## Output
- `data/local/hunter38/verify/report.md`. Start with a verdict per claim: `holds`, `holds in part`, `does not hold`,
  one line each. Then "what is safe to tell the team" in at most 12 plain lines, with the numbers and the number
  of games and deaths behind each, measured and inferred kept apart. Then the evidence: your counts next to the
  earlier ones, the boards you looked at (file, round, a small text drawing where it helps), the lines of
  `main.cpp` that explain the behaviour (file line numbers), and what you could not determine.
- `data/local/hunter38/verify/recount.py`: your counting script, runnable from the repo root.
- If you find the cause of the early deaths in the bot's code, describe the smallest change that would test a fix
  (as an idea in the bot's own terms; do not edit any bot code).

## Limits
Write only inside `data/local/hunter38/verify/`. Do not run games. No posts anywhere, no uploads, no server calls.
Do not open `docs/api.txt` or `docs/discord.txt`. Aim to finish within 35 minutes; if time runs short, finish
claims A to C and question 1 properly and say what is left.
