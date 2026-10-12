from pathlib import Path
import re
p=Path('data/analysis/top1/TEAM-BRIEF.md'); s=p.read_text()
def block(a,b,t):
 global s
 i=s.index(a); j=s.index(b,i); s=s[:i]+t.strip()+'\n\n'+s[j:]
block('## 4. Queen and portals','### What the top teams actually do\n\nThe table shows', '''## 4. Queen and portals

### What the data says

- Portal sample: **2,388 unique inputs; 1,947 portal-map games, 3,894 queen-games**, including Schooltime, both sides and 45 added live games. Source: `queen-portals/summary.md`, opening.
- Jumping queens on Portals: ours 45/45, top three 44/108, other 55/141; Prisoners Dilemma 19/19, 34/106, 15/109. On Stripes ours jumped less: 36/49 versus 88/99 and 119/144. Source: `queen-portals/games.json`, map/tag recount below.
- Ours never jumped on Default (0/44), Queen Of Spades (0/40) or Trophy (0/50); top three did in 34/103, 15/89 and 11/104. Maze: 10/42 versus 34/98. Source: `queen-portals/games.json`, recount below.
- Elimination, all tags and unique games: Portals 1/147; Prisoners Dilemma 106/117; Stripes 144/146; Around UNSW 0/143; Slithery Fight 0/144. This means either side wiped out. Source: `queen-portals/games.json`, per-map recount.
- On maps at most 600 cells, death within 10 rounds of any jump affected ours 63/100 jumping queens, top three 53/166, other 86/189. Per individual jump: 70/267, 68/764, 97/703. Repeated jumps can precede the same death. Source: `queen-portals/summary.md` §§3–4, Fate.
- Final survivors among those jumping queens: 9/100, 51/166, 36/189; among non-jumpers: 0/13, 69/147, 75/205. These groups are unmatched. Source: `queen-portals/summary.md` §§3–4.

Recount source: `data/analysis/queen-portals/games.json`, fields `map`, `end`, queen `tag`, `jumps`, `win`. Q = queens; G = distinct games within a tag. Wins use queen-games; elimination uses unique games, even when both queens have the same tag. Tags overlap. “Other” means all remaining teams. A dash means no sample. Wins are shown as counts; jump and elimination columns include shares.

PORTAL_SHORT_TABLE''')
# Keep the requested per-map/tag table; remove redundant all-tag table.
table=Path('data/analysis/top1/brief_scratch/portal_table.md').read_text().split('\nAll tags together')[0].strip()
rows=table.splitlines()
for i in range(2,len(rows)):
 cols=rows[i].split('|')
 for col in (5,6):
  cols[col]=re.sub(r' \([0-9.]+%\)','',cols[col]).replace('— (0 queens)','—')
 rows[i]='|'.join(cols)
s=s.replace('PORTAL_SHORT_TABLE','\n'.join(rows))
block('### What the top teams actually do\n\nThe table shows','### Replays to open\n\nSources: `queen-portals', '''### What the top teams actually do

On Stripes, forgot crossed into a fountain pocket at round 8 and ate at 10–11. Ours stood beside the door at 7, crossed at 18 in one read game and never in the other. The initial explanation blamed a queen ban; the read corrected this because that ban was off. Source: `deep-read-3.md`, question b, point 5.

Portals has disconnected homes; survival there does not require reaching the opponent. Conversely, in Australia game 1053773 a portal was the only roomy safe escape from a ram. Source: `deep-read-4.md` §§4.1, 5e.''')
block('### Not known\n\nFrequent jumpers','## 5. Hunting', '''### Not known

Frequent jumpers have more opportunities for a jump near death; one death can appear after several jumps. No matching by map, opponent, build or lifespan was done. The round-100 subset uses eventual jumping, even after that round. These are not causal estimates. Source: `queen-portals/summary.md`, Input checks and limits.

The detector misses ordinary-distance-one crossings and fatal entries without a landing update. Necessity, actual visibility and usefulness were not measured; distances ignore walls and portal shortcuts. The data settle neither a universal ban nor a need for every small-map queen to cross. Source: `queen-portals/summary.md`, Input checks and limits.''')
block('## 5. Hunting','### Replays to open\n\nSources: `hypotheses', '''## 5. Hunting the enemy queen

Card #31 chases and pings. The study's runner-up takes an immediate visible ram at any attacker length, without adding a chase.

### What the data says

- Visible chances taken, later recount: **ours 99/435, opponents 197/228, Vibing++ 265/266, SSS 250/252, forgot 253/451**. Earlier: 99/446, 197/230, 266/267, 250/254, 254/457. Samples: 401 ours and 502 / 503 / 632 top-team games. The later path test keeps the attacker's body blocked. Sources: `REPORT.md` §4; `hypotheses.md`, Candidate 1 §2; `redteam.md`, Candidate 1 A.
- Ours by attacker length: 2–3 took 87/231, length 4 took 5/39, longer took 7/165. Forgot's short dragons took 136/139 after round 100. Source: `REPORT.md` §4.
- Six of seven Vibing++ close-read kills used length 5–11 and 4–6-step sprints. Three killers were fresh split children that ate nothing on approach. Source: `deep-read.md` §a.
- First scout trial, qh31: wins 10/30 versus live 8/30; queen rams 11 versus 10. Of 338 hunters, 8 rammed her and 36 died in head-ons with other enemies. Source: `hypotheses.md`, Candidate 1 §2, Trials.
- Portal-fix qh31b against test4+WHQ: short-dragon kills 8/30→13/30, wins 8/30→8/30; new killers length 2 / 3 / 4 numbered 5 / 6 / 2. Against dev test 1: kills 1/15→4/15, wins 3/15→1/15. Source: `qh31b-analysis/summary.md`, both opponent sections.
- Pooled test4+WHQ trials, excluding Schooltime: short-dragon chances 15/49→19/20; enemy queens alive 19→16; only-their-queen-alive losses 16→15; wins 16→17, in 56 games per side. Source: `redteam.md`, Candidate 1 F.

### What the top teams actually do

Vibing++ and SSS take visible queen rams with longer dragons too. Forgot differs: before round 100 its short dragons took 47/51 non-outnumbered chances versus 38/127 outnumbered ones. Source: `deep-read-2.md` §1.

Fresh split children walking straight toward a queen suggest dispatched hunters, but intent is inference. The shared observed behaviour is the final visible attack. Source: `deep-read.md` §§a–b.

The report's runner-up estimate was +0.5 to +2 percentage points, most likely +1. Of 75 games with an unused chance, 25 ended in a round-limit loss with their queen alive; the read estimated about 6 flips, 3 needing length-6 or length-8 attackers. This is arithmetic, not a tested gain or a recommendation here. Source: `REPORT.md` §4.''')
block('### Not known\n\nThe sources identify two hunt','## 6. Guards', '''### Not known

The sources name two variants and three opponent runs: qh31 test4+WHQ, qh31b test4+WHQ, qh31b dev test 1. A third distinct build is not identified. The newer summary includes Schooltime; the pooled study excludes it. Sources: `redteam.md`, Candidate 1 F; `qh31b-analysis/summary.md`, opening.

The red team found 99 additional pearl-funded opportunities, none taken by us; opponents took 52/65. The reviewed hunt path omitted this extra reach. We also won 0/49 races with their queen dead before 300 but our length below two thirds of theirs. Longer unrestricted immediate attackers were not tested online. Sources: `redteam.md`, Candidate 1 A; `REPORT.md` §4.''')
block('## 6. Guards','### Replays to open\n\nSources: `deep-read-2.md`, game 6;', '''## 6. Guards and intruders near our queen

### What the data says

- Intruders at most length 4 entering within four path steps were rammed by our team **3.7%**, opponents 13.6%, forgot 13.5%, SSS 16.6%, Vibing++ 12.1%. Samples: 401 / 401 / 632 / 503 / 502 games; intruders/game 3.0 / 4.7 / 3.5 / 2.8 / 3.4. Source: `deep-read-4.md` §5f.
- With at least three allies within six steps, the same rates were 9.4 / 26.9 / 26.0 / 30.4 / 23.5%. Yet in 39 close SSS turns, allies moved nearer the intruder 40 times and away 44 times. Sources: `deep-read-4.md` §5f; `deep-read-2.md`, Corrections, item 8.
- Guard-build mean allies in view after 200 rose 0.473→1.141; empty-view rounds fell 830/1,274→647/1,331. Queen deaths stayed 26/30 per build against test4+WHQ. Source: `kg34b-analysis/summary.md`, test4 + WeHaveQuizzes.
- Guard rams: live 1 versus new 0 in 30 games each against test4+WHQ; 2 versus 0 in 15 each against dev test 1. Wins: 8/30→5/30 and 3/15→2/15. Source: `kg34b-analysis/summary.md`, both opponent sections and §6.
- Deaths before 100 / at 100–200 / after 200 were live 13 / 8 / 5 and guard build 16 / 8 / 2, each in 30 test4+WHQ games. Median death rounds: 87 versus 73. Source: `kg34b-analysis/summary.md`, test4 + WeHaveQuizzes.

### What the top teams actually do

No escort was observed. Ordinary nearby dragons ram reachable intruders. In 1067641 an SSS dragon killed a follower at 158, but a longer attacker killed the queen at 166. Source: `deep-read-2.md`, game 6 and §4.''')
block('### Not known\n\nThe guard count','## 7. Small dragons', '''### Not known

“Guard” is a geometric action count, not a named role; nearby suicides do not prove the queen received their pearls. Source: `kg34b-analysis/summary.md`, Measurement limits.

Conditioned on an enemy within three steps, our short queen's same-round ram rate was 10 / 12 / 13 / 19% with 0 / 1 / 2 / 3+ allies within six steps. The later red team therefore rejected the broad company-survival correlation as proof that escorts protect her. Source: `redteam.md`, Candidate 2 B/C.''')
p.write_text(s);print(len(s))
