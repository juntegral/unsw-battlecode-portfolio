# Behaviour fingerprint: where do the opponents act differently from us, in the same games?

Private, local work. Input: `data/analysis/ladder/dossier/per-game.jsonl` (500 main ladder games, one row per game
and side; `relation` is "us" or "them"; schema is whatever `dossier/count_dossier.py` writes; definitions at the
end of `dossier/summary.md`). Do not recount replays unless a rate below needs a denominator the rows lack; if you
do, say which.

## Job
1. List every per-side measure in the rows that describes a BEHAVIOUR (something a dragon does on its turn), as a
   rate with an honest denominator: deaths by each cause per 1,000 dragon turns; head-on meetings started per
   1,000 dragon turns; splits per pearl eaten and per dragon turn; share of blind turns that keep direction or
   re-tread; share of turns beside a pearl that eat nothing; share of turns on or beside a tile that has spawned
   twice; portal steps per dragon turn; board seen; share of pearls eaten that were dropped by the dead; first
   contact round; queen measures (death round, cause, length); and any other behaviour measure the rows hold.
   Leave out pure OUTCOMES (lengths, dragons alive, pearls eaten, results) except as context columns.
   Use rounds 0-100 and 101-300 separately where the rows allow.
2. For each behaviour rate: ours, theirs (pooled over 500 games); the number of the 19 layouts on which theirs is
   the higher one; the same pooled numbers against opponents rated 2100 and above only (70 games) and under 1900
   only; and, inside our own games, the rate in the games we won against the games we lost, with the layout mean
   removed (so that a layout with many walls does not decide it).
3. Rank by how consistent the gap is: first the rates where the sign is the same on at least 15 of 19 layouts and
   in all three rating bands, ordered by relative gap; then the rest of the top 30.
4. Mark each ranked line with one of: "explained" for these, already traced to a code line today —
   head-on as mover / as the one hit (even trades below the dragon cap), eating and splitting after round 151 on
   layouts above 1200 cells (leader rules), pearls behind portals (pocket rule and portal harvest), the walled
   start room (centre pull); or "open".

## Output: `data/analysis/ladder/dossier/fingerprint.md` (80 lines or fewer), English
The ranked table (rate, window, ours, theirs, layouts where theirs is higher of 19, 2100+ ours/theirs, won/lost
inside our games, explained or open), then a list "Open gaps, largest first" with for each one line: what a
dragon of theirs does more or less often than ours, in plain words, and which per-game fields it comes from.
Counts and rates only; no advice. Also `fingerprint.json` with every rate. Scratch under
`data/analysis/ladder/dossier/work/` (prefix `fp_`). Last step: `data/analysis/ladder/dossier/fingerprint-done.txt`.
Write only those paths. No network, no posts, no games.
