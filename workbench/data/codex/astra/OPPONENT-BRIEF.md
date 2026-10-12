# One opponent, all our games against it (last 25 minutes; first message by 14:42 KST, final by 14:46)

You are a replay analyst for a game-bot team. The deadline is 15:00 KST and the lead's last upload is at 14:50. Read
`ASTRA-COMMON.md` in this folder (the game, the replay readers, [M] measured / [C] code / [E] inferred) and the State section
of `CLAUDE-COMMON.md` (ROOT = `~/01. Project/개인 프로젝트/unsw-swarm`). You build nothing and play no games;
light scripts, one process; this shell refuses long compound commands, so write scripts with the Write tool and run
`python3 <absolute path>` from ROOT. Your folder: `ROOT/data/codex/astra/<your name>/`.

Your opponent is named in the message that started you (team name and id). We are team 1119, rated about 2100. Find every
game against that team on disk: ranked battles `ROOT/data/online/live-one1/b*/game-<id>.json` (fields `teamAId`, `teamBId`,
`teamAName`, `teamBName`, `mapName`, `winner`, `completedAt`, `ranked`, ratings) with `M<id>.replay` beside each, and unranked
sets `ROOT/data/online/smoke/*-old/game-<id>.json`. New battles are downloaded as they finish: poll once a minute for a new
folder with your opponent and include it. Our bot version = bot id in the replay (`ROOT/data/online/smoke/versions.tsv`;
21761 = one18, the live bot now). Tools to reuse instead of writing your own: `ROOT/data/codex/astra/loss15-sonnet/` (`l15.py`,
`qtrace.py`, `r100.py`), `ROOT/data/codex/astra/battle-opus/` (per-battle notes in `battles.md`: read what it already has on
your opponent), `ROOT/data/analysis/ladder/dossier/work/o1_look.py` (boards).

Deliver, measured with the same script on both sides:
1. The table: every game (date, our version, our seat, map, result, how decided, both queens at the end, pearls and dragons
   at r100 both sides), and the win rate overall, by seat, by map where there are 2 or more games.
2. For our losses: the decisive thing in one line each, using these class names so the lead can add them up across opponents:
   queen rammed from a one-way place / queen rammed in the open / queen self-trap (dead end, pocket, own body) / queen boxed
   with a mate / long queen lost / out-eaten from round N / long dragon rammed / other. For our wins: what killed THEIR queen
   or their side.
3. What this opponent does that beats us, in terms a bot can act on (opening and split timing, where their queen lives, how
   they attack our queen: who, from how far, paid steps), and what of ours beats them.
4. Guard against overfitting, which the team insists on: no per-opponent or per-map logic. Offer at most two suggestions, each
   an EXISTING constant with a value (`CONST:value`; live values in `~/.claude/jobs/e2109d93/tmp/one18.switches`,
   source `~/meow-redteam/solo/src/solo/main.cpp`), and only if the same direction would be right against any opponent. If you
   have none, say none.
5. The practical answer: should we request another ranked battle against this team in the next 15 minutes (we are seat A when
   we request; their rating and ours decide the points): yes or no, with the per-game win chance you would put on it from the
   games you have, and how many games that rests on.
First three lines of every message: the answer to 5, the one thing that decides our games against them, and whether any
constant is worth the last upload. Keep each message under 25 lines.
