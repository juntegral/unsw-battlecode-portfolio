#!/bin/bash
# Regenerates every table of research/experiments/cand-swarm1.md from the eval outputs (no games are played).
# usage (repo root): bash exp/cand-swarm1/report.sh > exp/cand-swarm1/report.txt
# Needs: exp/<label>/rows.jsonl for every label below, and sides.jsonl from `node tools/proxy_check.js measure --label <label>`.
set -e
cd "$(dirname "$0")/../.."
echo "# paired results (candidate vs baseline, same opponent:map:side:seed)"
for v in 1 2 3 4 6 7; do
  [ -f exp/cand-swarm$v-proxies/rows.jsonl ] && { echo; echo "## cand-swarm$v vs proxies (baseline r1-vs-proxies-v1)"; node exp/cand-swarm1/pair.js cand-swarm$v-proxies r1-vs-proxies-v1; }
  [ -f exp/cand-swarm$v/rows.jsonl ] && { echo; echo "## cand-swarm$v vs the 4 local opponents (baseline eval-r1)"; node exp/cand-swarm1/pair.js cand-swarm$v eval-r1; }
done
echo; echo "## cand-swarm5 (v4 rules on bot/ = g4-r4 + avoid6) vs proxies (baseline cand-avoid6-proxies)"; node exp/cand-swarm1/pair.js cand-swarm5-proxies cand-avoid6-proxies
[ -f exp/cand-swarm5/rows.jsonl ] && { echo; echo "## cand-swarm5 partial vs 4 local opponents (baseline cand-avoid6)"; node exp/cand-swarm1/pair.js cand-swarm5 cand-avoid6 | sed -n 1,6p; }
echo; echo "## variant steps (proxies): v2 vs v1, v3 vs v1, v4 vs v3, v4 vs v1, v6 vs v4, v7 vs v6"
node exp/cand-swarm1/pair.js cand-swarm2-proxies cand-swarm1-proxies | sed -n 1,6p
[ -f exp/cand-swarm3-proxies/rows.jsonl ] && node exp/cand-swarm1/pair.js cand-swarm3-proxies cand-swarm1-proxies | sed -n 1,6p
[ -f exp/cand-swarm4-proxies/rows.jsonl ] && [ -f exp/cand-swarm3-proxies/rows.jsonl ] && node exp/cand-swarm1/pair.js cand-swarm4-proxies cand-swarm3-proxies | sed -n 1,6p
node exp/cand-swarm1/pair.js cand-swarm4-proxies cand-swarm1-proxies | sed -n 1,6p
[ -f exp/cand-swarm6-proxies/rows.jsonl ] && node exp/cand-swarm1/pair.js cand-swarm6-proxies cand-swarm4-proxies | sed -n 1,6p
[ -f exp/cand-swarm7-proxies/rows.jsonl ] && node exp/cand-swarm1/pair.js cand-swarm7-proxies cand-swarm6-proxies | sed -n 1,6p
[ -f exp/cand-swarm6/rows.jsonl ] && node exp/cand-swarm1/pair.js cand-swarm6 cand-swarm4 | sed -n 1,6p
echo; echo "# style (our side; top = data/top snapshot via tools/proxy_check.js)"
L="cand-swarm-base-r1"; for v in 1 2 3 4 6; do [ -f exp/cand-swarm$v/sides.jsonl ] && L="$L cand-swarm$v"; done
P="r1-vs-proxies-v1"; for v in 1 2 3 4 5 6 7; do [ -f exp/cand-swarm$v-proxies/sides.jsonl ] && P="$P cand-swarm$v-proxies"; done
for m in all r500 elim; do
  if [ $m = all ]; then node exp/cand-swarm1/style.js $L $P; else node exp/cand-swarm1/style.js $L $P --maps $m; fi
done
echo; echo "# deaths and splits (our side)"
for l in $P $L; do node exp/cand-swarm1/diag.js $l | sed -n 1,5p; done
echo; echo "# collisions between our own dragons"
for l in $P; do node exp/cand-swarm1/ownhits.js $l; done
echo; echo "# late king growth on 500-round maps"; node exp/cand-swarm1/kinggrowth.js $L $P
echo; echo "# mechanism"; node exp/cand-swarm1/mech.js $P $L
echo; echo "# key decision rules of research/observations/top-decisions.md on our side (vs proxies)"; node exp/cand-swarm1/rules.js $P --jobs 2
echo; echo "# king origin on autarky"; node exp/cand-swarm1/kingorigin.js autarky eval-r1 cand-swarm1 cand-swarm4; node exp/cand-swarm1/kingorigin.js autarky r1-vs-proxies-v1 cand-swarm1-proxies cand-swarm4-proxies
echo; echo "# cand-swarm8 (cand-swarm4 rules on exp/cand-merge2/bot = avoid6 + portal1 + pd10e)"
echo; echo "## vs proxies, baseline cand-avoid6-proxies (no merge2 proxies baseline exists)"; node exp/cand-swarm1/pair.js cand-swarm8-proxies cand-avoid6-proxies
echo; echo "## same keys vs cand-swarm5 (the portal1 + pd10e share)"; node exp/cand-swarm1/pair.js cand-swarm8-proxies cand-swarm5-proxies | sed -n 1,6p
echo; echo "## h2 only, baseline cand-merge2"; node exp/cand-swarm1/pair.js cand-swarm8 cand-merge2
echo; node exp/cand-swarm1/style.js cand-swarm8-proxies; node exp/cand-swarm1/kinggrowth.js cand-swarm8-proxies; node exp/cand-swarm1/mech.js cand-swarm8-proxies; node exp/cand-swarm1/ownhits.js cand-swarm8-proxies; node exp/cand-swarm1/rules.js cand-swarm8-proxies --jobs 2
echo; echo "## v7 vs v4 (same keys)"; node exp/cand-swarm1/pair.js cand-swarm7-proxies cand-swarm4-proxies | sed -n 1,6p
