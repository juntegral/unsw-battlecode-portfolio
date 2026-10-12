# Scratch (diag-topopen): composes dossier/diag-topopen.md from work/to_tables.md, work/to_mech.md and the prose below.
from pathlib import Path
D = '개인 프로젝트'
DOS = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/'
WORK = DOS + 'work/'
BT = chr(96)

sections = {}
name = None
for line in Path(WORK + 'to_tables.md').read_text().splitlines():
    if line.startswith('@@ '):
        name = line[3:]
        sections[name] = []
    elif name:
        sections[name].append(line)

REN = [('aAah today', 'aAah, today'), ('larp today', 'larp stock zi balls, today'), ('Cutlery today', 'Cutlery, today'), ('chad today', 'chad gdp, today'),
       ('Cutlery old', 'Cutlery, to 5 Oct'), ('SSS old', 'SSS, to 5 Oct'), ('ftm old', 'forgot to mention, to 5 Oct'),
       ('ours B7Q', 'ours, live build B7Q'), ('ours main', 'ours, main')]
SIZES = (('S', '700 or fewer'), ('M', '701-1200'), ('L', 'above 1200'))


def rows_of(sec, labs):
    out = []
    for old, new in labs:
        for line in sections[sec]:
            if line.startswith('| ' + old + ' ') or line.startswith('| ' + old + ' |'):
                out.append((new, line[len('| ' + old):]))
    return out


curve = ['| Cells: side (games; still running at r100, r300). Cell: dragons alive / total length / longest; then pearls eaten / splits / deaths so far | r10 | r20 | r30 | r40 | r60 | r80 | r100 | r150 | r200 | r300 |',
         '|---|' + '---|' * 10]
for sz, nm in SIZES:
    for new, rest in rows_of('curve ' + sz, REN):
        curve.append('| ' + nm + ': ' + new + rest)

x15 = ['| First round with 1.5 times ours for 5 rounds running, their own games: dragons alive (ratio at r40, r100, r300); total length (the same) | 700 or fewer, against B7Q | 700 or fewer, against our three builds, same layouts | 701-1200, against B7Q | 701-1200, three builds, same layouts | above 1200, against B7Q | above 1200, three builds, same layouts |',
       '|---|---|---|---|---|---|---|']
for new, rest in rows_of('x15', REN[:4]):
    x15.append('| ' + new + rest)

h2h = ['| The 30 games of our live build against them: first round they hold 1.5 times ours for 5 rounds running (theirs/ours at r20, r40, r60, r100, r150, r300; n games) | 700 or fewer, alive | 700 or fewer, total length | 701-1200, alive | 701-1200, total length | above 1200, alive | above 1200, total length |',
       '|---|---|---|---|---|---|---|']
for new, rest in rows_of('h2h', [('larp vs us', 'larp stock zi balls'), ('Cutlery vs us', 'Cutlery')]):
    h2h.append('| ' + new + rest)

mech = []
drop = ('| Other dragons r0-60', '| Children r1-60 born')
for line in Path(WORK + 'to_mech.md').read_text().splitlines():
    if any(line.startswith(d) for d in drop):
        continue
    cells = line.split(' | ')
    if line.startswith('|---'):
        mech.append('|---|' + '---|' * 7)
    else:
        mech.append(' | '.join(cells[:8]) + ' |')

T = []
T.append('# The first 100 rounds against the top teams: in the direct games they reach 1.5 times ours at rounds 67 to 115 above 700 cells, and at round 28 below only to lose it again; what theirs do in the opening that ours does not is split in round 0, the queen included (team 1119; 307 games of four top teams today, 1,330 older, 180 of ours on the ladder, 30 of our live build against larp stock zi balls and Cutlery; written 8 Oct 2026)')
T.append('')
T.append('1. **The finding.** [M] In the 30 games of our live build against larp stock zi balls and Cutlery (6 won) they first hold 1.5 times our total length at round 81 (larp, 701-1200 cells), 88 (larp, above 1200) and 115 (Cutlery, above 1200); at 700 cells or fewer only Cutlery does, from round 30, and we are ahead again by round 100. At round 60 they stand at 1.1 to 1.3 times our length above 700 cells (1.1 to 1.4 in dragons). In their own games on the same layouts aAah reaches 1.5 times the length of our three builds at rounds 50 to 120, larp at 87 and 111, chad gdp at 107 and 143, Cutlery at 43 on medium layouts only; pearls run ahead of that on medium layouts, 1.7 to 2.2 times ours by round 20. Inside rounds 0-60 two things they all do are missing from ours: a starter of 4 or more splits in round 0 (in 96 to 100% of their games that have one; ours in none at 1200 cells or fewer), and the queen splits like any other dragon (aAah, larp and chad gdp above 700 cells: on 74 to 100% of her turns at length 4 or more; our live build on 3 to 15%, with 18 to 24 such turns a game). The other candidates are level or not theirs in common: a pearl beside the head is eaten as often as by larp and Cutlery, a portal mouth is entered as often once a dragon stands beside it, nobody walks to a mouth seen from afar, and paying length for pearls is aAah and chad gdp only.')
T.append('2. **The change.** Two cards, both on the opening split: QS_KEEP_ROUND (the queen keeps 3 segments only from round 40; before it she splits like the others) and SPLIT_ROUND0 (a starter splits in round 0, not round 1).')
T.append('3. **How sure.** Sure of the counts: 1,847 games scanned without an error, the curves of our 60 live-build games equal the shared reader in 121,000 of 121,000 cells, and the two card counts were recounted by separate code with the same result for ours. Fairly sure card 1 buys a dragon through round 40 on medium layouts: B7, the build without the keep rule, holds 5.4 against 4.1 dragons at round 20 and 7.4 against 5.5 at round 40 there. Not sure it moves results: the long queen is why the live build wins more than B7 (14 of 30 against 23 of 60, read from dossier/online/agg7.md), and the card bets that she is 3 long again soon after round 40. Card 2 is certain as a mechanism and worth one dragon-turn per long starter. Neither closes the gap: in the direct games it opens at rounds 67 to 115, from a lead of 1.1 to 1.3 at round 60, and I found no single opening behaviour behind that lead.')
T.append('')
T.append('Labels: [M] measured by my scripts in dossier/work/ (to_scan.py: both sides of every game to r300, state at each round end, turn contexts, splits, sprints, deaths; to_scan2.py: turns with a pearl beside the head, pearl births by distance, children, portal sides; to_scan3.py: which portal mouths each dragon has had in view; to_tab.py and to_mech.py write the tables below to work/to_tables.md and work/to_mech.md, with the rows left out here; to_agg*.py the long forms; to_check.py the recount; to_view.py and to_map.py print turns and walls; to_report.py puts this file together). [C] read from data/online/smoke/agg8-bot/main.cpp, line given. [E] my estimate. Sections 1 and 2 are [M]. Sets: today = data/online/top3 as listed at 16:33 KST, 33 battles, 307 games (to_scan3.py: the first 287; three more battles came in after that listing and are not in); to 5 Oct = the battles filed under five teams in data/top1/index.jsonl, 1,330 games, a studied team counted on either side; ours = agg8-q1 (live B7Q, 30 games), agg7-b1 and b2 (B7, 60), agg7-m1 to m3 (main, 90), top-l1-old (live B7Q against larp and Cutlery, 30; no top-l2 folder had arrived). Autarky and Prisoners Dilemma are left out of every table, as none of our sets has them, so a size class is the same layouts in every row: 6 at 700 cells or fewer, 4 at 701-1200, 5 above 1200. "Same layouts" = the mean of layout means. A game that has ended drops out of the later cells.')
T.append('')
T.append('## 1. Growth curves and where 1.5 times is reached (job 1)')
T += curve
T.append('')
T += x15
T.append('')
T += h2h
T.append('- How to read it: in their own games the top teams play sides rated 2029 to 2597 (25 of 33 battles above 2150) and ours play two sides rated 2034 and 2358 in equal parts, and a row can mislead (Cutlery today is behind us above 1200 cells and beats us there 5 of 5); only the 30 direct games hold layout and opponent equal, at 4 to 6 games a cell. The medium "against B7Q" column (rounds 25 to 45) is the live build alone, 8 games, and partly card 1. Deaths by cause at r60 and r300, horse, the older aAah games, B7 and the direct rows by round: work/to_tables.md.')
T.append('- Where it opens: above 1200 cells against larp, dragons 18.0 to our 15.8 at r20, 35.0 to 27.0 at r60, 53.4 to 34.2 at r100, 59.8 to 34.4 at r150. We stop near 35 to 40 dragons and they fill the limit near 60. By r60 both sides have lost as many dragons (28.3 against 27.4 and 31.2) and by r100 all but 6 to 9% of the natural pearls born are eaten (39% by us, 52 to 55% by them), so from there it is a fight over a fixed supply that the side with more heads wins.')
T.append('## 2. The mechanics of rounds 0-60 (job 2)')
T += mech
T.append('- Differs from all four: the round-0 split and the queen (Cutlery holds its queen only above 1200 cells). Differs on medium layouts only: turns beside a portal mouth in r0-20 (0.2 and 0.4 a game against 3.0 to 3.9), a head within 3 steps of a newborn pearl (13 and 17% against 23 to 28%), the first pearl of a new dragon on the ladder (median 23 rounds against 7 to 15); the four layouts are starts of two to four dragons with the first pearls far off. aAah and chad gdp only: paid sprints above 1200 cells, 12.9 and 18.8 a game, 5.2 and 7.1 of them a free step onto one pearl and a paid step onto the next (two pearls, one length, one turn). Does not differ: the split itself (a child of 2 off a parent of 4; our children of 4 or more above 1200 cells, 26 to 34% against 5 to 10%, are the escape splits of the harvest rule), spread, layout seen, how far the child walks, refusing a pearl beside the head against larp and Cutlery (15% against 12% above 1200 cells; aAah and chad gdp refuse less), dragons lost. Of our children born into under 8 free tiles above 1200 cells (10.7 to 15.7 a game) 87 to 92% are dead within 10 rounds against 28 to 69% of theirs; nearly all had eaten first (harvest runs into a dead end), so I do not count them as waste.')
T.append('## 3. Why, in the code (job 3)')
T.append('- Split and queen. [C] A dragon splits a child of 2 off from length 4 (41, 1048, 1071). harvest_round starts at -1 (5646) and line 758 reads harvest_round == round - 1, true in round 0, so line 1068 returns 0 and every starter moves first; a starter with no free tile splits by 728-733, which I take to be our 75% above 1200 cells [E]. For the queen line 1057 returns 0 while length - 2 is under QS_KEEP_LEN (137, 3), so she splits only from 5; agg7-bot/main.cpp (B7) has no such line. [M] Replay 1421773 (live, 32 by 32): r0 all four starters of 4 move; r1 #3 at (27,30), #5 at (23,30) and #7 at (20,31) split, the queen #1 at (31,30) with three free tiles steps north and has not split by r60. Replay 1431388 (48 by 24, against larp): larp #1 at (43,8) and #3 at (43,21) split in r0 and both children move that round; ours move in r0 and split in r1.')
T.append('- Sprints for pearls. [C] The only steps past the first without an enemy are the stride, free steps only, so from length 5 (785-795, 810-811); paid steps come from the hunt (564), the ram (622) and the escapes (632-660, 736-745, 779). [M] 0.2 to 0.4 paid turns a game and none eats; a dragon of 5 to 8 with a pearl two steps off took it on 0 of 18 turns above 1200 cells in the direct games (theirs 57%, aAah 51 to 72%). No card: ours are 5 or longer on 24 to 29 turns a game, and the paid double-eat of aAah and chad gdp nets one length for two pearls.')
T.append('- Portals and pockets. [C] A mouth with an unknown far side is entered only as a scout step, best step + 88 (5320, 5348-5350, 5476-5478), a known one at the far tile score less 150 (5275-5276); the pull toward a mouth is 0.4 x (260 - 40 x steps), nothing from 6.5 steps, and only while the far side is unknown (3051-3054, 5115-5119); the queen may not enter (3772-3774); the far pull PORTAL_FAR_DECAY exists and is off (298). [M] Beside a mouth ours step through as often where they get there (38 to 42% against 32 to 51%), and with a seen mouth 7 to 26 steps off theirs end the turn nearer on 19 to 62% and ours on 22 to 40%: nobody walks to a far mouth, so the far pull is no card. Theirs are simply near one earlier on medium layouts: replay 1428913 (aAah, 25 by 35) #2 walks from (2,9) through the mouth at (4,3) in r8 and eats in r9 and r12; ours on that start is the side-step of diag-opening2.')
T.append('- Spread, territory, centre. [C] A tile a team mate reaches sooner counts nothing (2978-2982), territory is 1.5 a tile over the whole reachable board (5055-5059), a mate head beside the target tile costs 450 (5166-5168), the centre pull runs to r30 or r60 on 700 cells or fewer and on wide layouts to 1000 (494, 5161-5165). [M] Nearest-mate distance is within a tile of theirs except on medium layouts, where we have fewer dragons. A pearl beside the head in open water is left 0.6 times a game (1.6 above 1200 cells): replay 1421767 r9, #17 at (45,38) leaves the pearl at (46,38), a corner tile, with a mate three tiles south, and eats it from the same tiles in r21 with no mate in view. I did not rebuild the score for it.')
T.append('## 4. The cards (job 4)')
T.append('title: The queen keeps 3 segments only from round 40; before it she splits like any dragon (default-off QS_KEEP_ROUND)')
T.append('slug: queen opening split')
T.append('### Claim')
T.append('[M] In rounds 0-40 the live build queen spends 19.1 turns a game (ladder, 30 games) and 21.5 (against larp and Cutlery, 30) at length 4 or more and splits on 9% and 7% of them; the card changes the first of those turns and every later return to 4. B7, without the rule: 2.8 turns, 79%. The indexed top side today: aAah 2.9 turns and 83%, chad gdp 2.2 and 75%, larp 3.6 and 53%, Cutlery 9.9 and 20% (it holds her above 1200 cells only). [C] Proposal: QS_KEEP_ROUND (0 = as now, test 40); line 1057 applies only from that round on.')
T.append('### Evidence')
T.append('[M] B7 beside B7Q on the same layouts, 16 and 8 games at 701-1200 cells: dragons 5.4 against 4.1 at r20, 7.4 against 5.5 at r40, 9.8 against 8.1 at r60, level at r80; pearls by r40 11.9 against 7.2. Above 1200 cells, 20 and 10 games: 24.2 against 21.7 at r40, 50.1 against 43.0 at r100. At 700 or fewer no deficit (7.5 against 8.8 at r40). In their own games the top teams reach 1.5 times the live build on medium layouts at r25 to r45, and 1.5 times all three builds at r42 to r107. [C] 137, 1057.')
T.append('### Expected signal')
T.append('[E] to_mech.py and to_tab.py name no map and run on any replays of ours. Queen turns at 4 or more in r0-40 from about 20 a game to under 5, split on more than 60% of them; her length at r20 from 3.3 to about 2.5; dragons at r20 and r40 on 701-1200 cells from 4.1 and 5.5 toward 5.4 and 7.4, pearls by r40 there from 7.2 toward 12; above 1200 cells dragons at r40 from 21.7 toward 24.')
T.append("### What would show it's wrong")
T.append('Her length at r100 falls by more than 0.5 (now 2.3 on the ladder and 2.4 direct, dead queens counted 0; 3 or more in 60 and 64% of games; B7 1.5 and 34%); she is dead by r60 more often (now 17 and 14% of games; B7 21%); or games won on queen length drop while dragons at r40 do not rise.')
T.append('title: A starter of 4 or more splits in round 0, not round 1 (default-off SPLIT_ROUND0)')
T.append('slug: round 0 split')
T.append('### Claim')
T.append('[M] Of our games with a starter of 4 or more, a split comes in round 0 in 6 of 18 (live, ladder), 6 of 18 (live, direct), 12 of 36 (B7) and 18 of 54 (main), all of them above 1200 cells (in the one I read, 1431391, a boxed-in starter of 10 sheds its tail); at 1200 cells or fewer 0 of 10, 0 of 10, 0 of 20 and 0 of 30. aAah 64 of 64, larp 48 of 48, chad gdp 44 of 46, Cutlery 36 of 37, larp and Cutlery against us 18 of 18. The card would alter the first turn of 1.2 (live) to 1.7 (B7, main) starters a game. [C] Proposal: SPLIT_ROUND0 starts harvest_round at -2, nothing else.')
T.append('### Evidence')
T.append('[M] Our splits are 0.20 a game in round 0 and 1.20 to 1.67 in round 1; theirs 1.1 to 1.8 in round 0 and 0.3 to 0.5 in round 1. [C] 5646, 758-760, 1068. diag-opening counted the same on the older ladder build (4.6% against 75.9% of length-4 starters) and left it as a lead; today every top team does it in every size class.')
T.append('### Expected signal')
T.append('[E] Games with a starter of 4 or more that split in round 0 from 33% to above 90%; round-1 splits from 1.2 to 1.7 a game to under 0.4. Worth one child-turn per long starter (1.8 a game with card 1); no visible change in the curves past round 5.')
T.append("### What would show it's wrong")
T.append('Round-0 splits stay under 80% of such games (another gate holds the first turn), or deaths in rounds 0-5 with no free tile beside the head rise: on the first turn the trail may be unknown, and line 1076 then splits without the room test. Diff for both cards against data/online/smoke/agg8-bot/main.cpp:')
T.append(BT * 3 + 'diff')
T.append('@@ -42,1 +42,3 @@')
T.append(' constexpr int SPLIT_SOFT_LIMIT = 60;')
T.append('+// Card: a starter may split on its first turn (false = as now).')
T.append('+constexpr bool SPLIT_ROUND0 = false;')
T.append('@@ -137,1 +139,3 @@')
T.append(' constexpr int QS_KEEP_LEN = 3;')
T.append('+// Card: the queen keeps QS_KEEP_LEN only from this round on (0 = as now, test 40).')
T.append('+constexpr int QS_KEEP_ROUND = 0;')
T.append('@@ -1057,1 +1061,1 @@')
T.append('-        if (QS_KEEP_LEN > 0 && real_queen() && length - unswbc::Constants::MIN_SIZE < QS_KEEP_LEN) {')
T.append('+        if (QS_KEEP_LEN > 0 && round >= QS_KEEP_ROUND && real_queen() && length - unswbc::Constants::MIN_SIZE < QS_KEEP_LEN) {')
T.append('@@ -5646,1 +5650,1 @@')
T.append('-    int harvest_round = -1;')
T.append('+    int harvest_round = SPLIT_ROUND0 ? -2 : -1;')
T.append(BT * 3)
T.append('## 5. Against it')
T.append('- [M] Small cells and unequal opponents. The direct evidence is 30 games at 4 to 6 a cell, one hour, two opponents; the 1.5 rounds move by tens of rounds with one game. The B7 against B7Q comparison is not a paired test: other hours and other opponents, 16 against 8 games on medium layouts, and I checked only that B7 lacks line 1057, not what else differs between the two files.')
T.append('- [M; the wins are read from dossier/online/agg7.md] Card 1 gives up in the opening what the live build was made for. It wins 14 of 30 against 23 of 60 with the long queen, and its queen is 3 or longer at r100 in 60% of games against 34%. With the rule back from round 40 she needs one or two pearls to be 3 again; in B7 she is 2.2 long at r40. If she does not regrow, the card trades a deciding rule for a dragon. A queen of 2 may also be handled differently by the safety rules (QW_MIN_LENGTH 4); I did not read those paths.')
T.append('- [M] The largest gap I measured has no card: on the four medium layouts their pearls are 1.7 to 2.2 times ours by r20 and their short dragons stand beside a portal mouth eight or more times as often in r0-20, but a dragon that knows of a far mouth does not walk to it in either camp, so I cannot name the line that puts theirs there; the one known start (diag-opening2) was refused as a one-layout card. They may know these layouts; the qualifier layouts are unseen.')
T.append('- Not checked: no build was made and no game played; that get_round_num() is 0 on the first turn is read from the replays (ours never split in round 0 unless boxed in), not from a log; the "has had in view" model of to_scan3.py is mine (7 by 7 at each turn start, a child starts blank) and theirs may share sight; the older sets are the battles filed under the five teams, 1,330 games, where the brief counts 2,078 for four of them. Housekeeping: the Write tool is refused for this folder (path spelling), so files went through the Python route; scans ran plain, two at a time, about 40 minutes in all. Left in work/: 14 to_ scripts, 22 to_scan jsonl files (about 60 MB), to_tables.md, to_mech.md. Nothing else was written.')
text = '\n'.join(T) + '\n'
Path(DOS + 'diag-topopen.md').write_text(text)
print('lines', len(T), 'chars', len(text))
