#!/bin/zsh
# diagnostic variant k8 (SF_PIECE_BIG_ONLY true) on the post-cleanup keys, after finish2's post-cleanup evals; then its reports
cd "$(dirname "$0")/../.."
X=exp/v1
okres() { while true; do m=$(memory_pressure | awk -F': ' '/free percentage/ {gsub("%","",$2); print $2}'); d=$(df -g . | awk 'NR==2 {print $4}'); if [ "${m:-100}" -ge 10 ] && [ "${d:-100}" -ge 20 ]; then return; fi; sleep 20; done; }
while ! grep -q "post evals done" $X/finish2.log 2>/dev/null; do sleep 10; done
rm -rf $X/bot-k8; cp -R versions/v1/bot $X/bot-k8; rm -rf $X/bot-k8/.unswbc-build
sed -i '' 's/^constexpr bool   SF_PIECE_BIG_ONLY = false;/constexpr bool   SF_PIECE_BIG_ONLY = true;/' $X/bot-k8/params.hpp
grep -q '^constexpr bool   SF_PIECE_BIG_ONLY = true;' $X/bot-k8/params.hpp || { echo "flag edit failed" > $X/k8.err; exit 1; }
okres; nice -n 10 node tools/eval.js --bot $X/bot-k8 --label k8-a-px4 --out $X/k8-a-px4 --opps proxy4_king,proxy4_elim --seeds 1 --maps $X/maps-swarm-a --jobs 3 > $X/eval-k8-a.log 2>&1
okres; nice -n 10 node tools/eval.js --bot $X/bot-k8 --label k8-b-px4 --out $X/k8-b-px4 --opps proxy4_king,proxy4_elim --seeds 2 --maps $X/maps-swarm-b --jobs 3 > $X/eval-k8-b.log 2>&1
while [ ! -f $X/FINISH2-DONE ]; do sleep 5; done
nice -n 10 node $X/local_report.js --a $X/k8-a-px4,$X/k8-b-px4 --b $X/v1post-a-px4,$X/v1post-b-px4 --names k8,v1post --jobs 3 --out $X/report-k8-vs-post.md > /dev/null 2> $X/report-k8.err
echo done > $X/K8-DONE
