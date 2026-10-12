cd "~/01. Project/개인 프로젝트/unsw-swarm"
D=data/codex/astra/stuck-opus
L=data/analysis/ladder/dossier/work/o1_look.py
S=data/online/smoke/one14-c1-old
{
echo "### 1 forbidden pearl orbit, tip corridor: Around UNSW M1517691 dragon 31 (7x7; o pearl, H head, b body, M/m mate; NESW kelp sides, nesw portal sides)"
nice -n 10 python3 -B $L $S/M1517691.replay 0 31 22 23 | grep -v " eats "
nice -n 10 python3 -B $L $S/M1517691.replay 0 31 80 80 | grep -v " eats "
echo "### 2 forbidden pearl orbit, portal nook: Islands M1517687 dragon 122"
nice -n 10 python3 -B $L $S/M1517687.replay 0 122 300 301 | grep -v " eats "
echo "### 3 forbidden pearl orbit, 2x2 rooms: Trauma M1517697 dragon 40, centred on (33,7)"
nice -n 10 python3 -B $D/board.py $S/M1517697.replay 40 200 4 33 7 w
echo "### 4 idle loop: Around UNSW M1517691 dragon 198 (L6, two steps a round round a 2x4 block, r141-321)"
nice -n 10 python3 -B $L $S/M1517691.replay 0 198 259 260 | grep -v " eats "
nice -n 10 python3 -B $D/board.py $S/M1517691.replay 198 200 9
echo "### 5 idle loop: Schooltime M1517694 dragon 91 (L3, r188-499)"
nice -n 10 python3 -B $D/board.py $S/M1517694.replay 91 300 8
} > $D/boards.txt 2>&1
wc -l $D/boards.txt
tail -4 $D/run.log
date
