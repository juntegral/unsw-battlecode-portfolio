#!/bin/zsh
# #31 queen-hunt online pair: starts only after the loop accepts Zhe's look answer; then posts the report.
cd "~/01. Project/개인 프로젝트/unsw-swarm"
ok() { python3 - <<'PY'
import json,os,sys
def rd(p):
    try: return json.load(open(os.path.expanduser(p)))
    except Exception: return {}
r=rd('~/meow-loop-out/card-31/attempt-1/reply.json')
s=rd('~/meow-loop-out/status.json').get('cards',{}).get('31',{})
sys.exit(0 if r.get('decision')=='ok' or s.get('state') in ('testing','tested','candidate') else 1)
PY
}
end=$(( $(date +%s) + 1500 ))
until ok; do
  [ $(date +%s) -ge $end ] && { echo "$(date '+%F %T') not accepted in 25 min; not starting" >> data/online/smoke/at-qh31.log; exit 0; }
  sleep 30
done
echo "$(date '+%F %T') accepted; starting pair" >> data/online/smoke/at-qh31.log
data/online/smoke/run-pair.sh qh31-test "~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/qh31-bot" "#31 queen-hunt"
[ "$(python3 -c "import json;print(json.load(open('data/online/smoke/qh31-test.json')).get('phase'))")" = "rolled-back" ] && python3 tools/pair_report.py qh31-test --post "#31 queen-hunt" > data/online/smoke/qh31-report.log 2>&1
echo "$(date '+%F %T') done" >> data/online/smoke/at-qh31.log
