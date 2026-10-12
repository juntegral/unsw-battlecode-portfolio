cd "~/01. Project/개인 프로젝트/unsw-swarm"
D=data/codex/astra/stuck-opus
nice -n 10 python3 -B $D/detect.py online one14-c1 >> $D/run.log 2>&1
nice -n 10 python3 -B $D/detect.py local h2h_mNps_v13 pc_mNps lc_mNps >> $D/run.log 2>&1
nice -n 10 python3 -B $D/detect.py online one13-c1 one12-c1 one11-c1 one14-k1 one14-p1 one14-c2 one14-q1 >> $D/run.log 2>&1
nice -n 10 python3 -B $D/detect.py online one13-c2 one13-k1 one12-k1 one11-k1 one13-p1 one12-p1 one11-p1 >> $D/run.log 2>&1
nice -n 10 python3 -B $D/detect.py local h2h_mDone13_v5 pc_mDone13 >> $D/run.log 2>&1
nice -n 10 python3 -B $D/detect.py online one13-k2 one13-p2 one13-q1 one10-c1 one8-c1 one5-c1 >> $D/run.log 2>&1
