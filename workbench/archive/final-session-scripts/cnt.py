import sys
S="~/01. Project/개인 프로젝트/unsw-swarm/docs/SESSION-STATE.md"
t=open(S,encoding='utf-8').read()
for k in "team_watch online.js submit.js smoke.py pair_report at-q.sh run-pair cx.sh mkbots run_arms h2h_tally gx_tally sweep.sh o1_scan o1_sweeptab ladder_replay replay2map weak_watch park_watch sweep_games meowbot discord_sync mention_watch jun_dm killtree wait_any cmp -l shasum fingerprint.js play.sh run_game batch.sh collect.sh mapgen stress17 desk-inbox top_collect eval.js decisions h2h17 lcheck replay2map server_bot board.py runner.py nohup pkill PID 92fb69564fbd".split(" "):
    pass
keys=["team_watch","online.js","submit.js","smoke.py","pair_report","at-q.sh","run-pair","cx.sh","mkbots","run_arms","h2h_tally","gx_tally","sweep.sh","o1_scan","o1_sweeptab","ladder_replay","replay2map","weak_watch","park_watch","sweep_games","meowbot","discord_sync","mention_watch","jun_dm","killtree","wait_any","cmp -l","shasum","fingerprint.js","play.sh","run_game","batch.sh","collect.sh","mapgen","stress17","desk-inbox","top_collect","eval.js","h2h","lcheck","server_bot","board.py","runner.py","nohup","pkill","92fb69564fbd","gx_","astra","Astra","sol","engine.log"]
for k in keys: print("%-16s %d"%(k,t.count(k)))
