#!/bin/sh
# v1.6g reports (versions/v1.6/VERSION.md §8.5). The off arms of (b) and (c) are W1's replays (exp/gen v1.2, event-identical to v1.3 and to this copy's
# CONV2_ON = false builds off stronghold: exp/v16/identity-g.txt) with stronghold from exp/gen's v1.3 grid. Caches of sets outside exp/v16 go to cache-gen.
cd "$(dirname "$0")/../.."
case "$1" in
b) nice -n 10 node exp/v16/conv_report.js --sets 'on=exp/v16/gS-H,exp/v16/gS-K' --sets 'off=exp/gen/v12-S-H!stronghold,exp/gen/id-v13-S-H?stronghold,exp/gen/v12-S-K' --cache-dir exp/v16/cache-gen --out exp/v16/report-v16g-b.md ;;
c) nice -n 10 node exp/v16/conv_report.js --sets 'on=exp/v16/gF-H,exp/v16/gF-K' --sets 'off=exp/gen/v12-F-H!stronghold,exp/gen/id-v13-F-H?stronghold,exp/gen/v12-F-K' --cache-dir exp/v16/cache-gen --out exp/v16/report-v16g-c.md ;;
a) nice -n 10 node exp/v16/conv_report.js --sets 'v16g=exp/v16/p16g-a,exp/v16/p16g-b' --sets 'v13=exp/v16/p13-a,exp/v16/p13-b' --out exp/v16/report-v16g-a.md
   nice -n 10 node exp/v16/conv_report.js --sets 'v16g=exp/v16/p16g-a,exp/v16/p16g-b' --sets 'v16b=exp/v16/p16b-a,exp/v16/p16b-b' --out exp/v16/report-v16g-vs-v16b.md ;;
esac
