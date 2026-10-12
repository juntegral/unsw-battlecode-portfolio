# Astra analyst: weak-b1476178

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `weak-b1476178`. The team's standing rule: every game lost to a team rated 100 or
more below us gets its cause found and fixed. Earlier findings on such losses: `data/codex/astra/weak/report.md` (all ten earlier
ones had our queen dead; in six the enemy queen lived), `data/codex/astra/qwq3/report.md`.
Lost games in `data/online/live-one1/b1476178/` (replays `M<game id>.replay`); the bot that played is the submission id below
(21086 = one7 `data/online/smoke/one7-bot/main.cpp`, 21033 = one6, 20980 = one5; a later id is a later version in
`data/online/smoke/one*-bot/`, see `docs/SESSION-STATE.md` grep "라이브 = one"):
- game 1476178, map Trophy, we are side A, our rating 2071 against 1863 (Maccas, team 762), rating change -25, our submission None
For each game: 1. how it was decided and the round it turned for good; dragons, total length, longest and queen length of both
sides every 25 rounds; 2. the single event or habit of ours that lost it (our queen's death: round, cause, her last three turns
drawn; a pin, a pocket, a portal loop, standing still, feeding the enemy, never reaching their queen), with rounds and dragon
ids; 3. which switch of the bot that played was supposed to prevent it and why it did not (read the code; say the condition that
failed); 4. whether the same thing is in other games of the same submission (count over its sets).
Then one card per distinct cause: the rule, the lines, whether an existing switch does it (paste form `CONST:value`), the replay
count that shows it works. Report under 500 words plus tables; first three lines = cause, card, how sure.
