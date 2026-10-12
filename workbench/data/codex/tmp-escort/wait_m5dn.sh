#!/bin/zsh
cd "${0:A:h}"
limit=$((SECONDS + 3600))
count_results() { ls ~/meow-redteam/solo/runs/m5dn_vh/*/result.txt 2>/dev/null | wc -l; }
until (( $(count_results) >= 8 )) || (( SECONDS >= limit )); do
  count_results > wait-m5dn-count.log
  sleep 10
done
count_results > wait-m5dn-count.log
if (( $(count_results) < 8 )); then
  print "60-minute limit reached; using completed games" > wait-m5dn.log
else
  print "All 8 result files present" > wait-m5dn.log
fi
nice -n 10 env PYTHONDONTWRITEBYTECODE=1 python3 dn_scan.py m5dn_vh >> wait-m5dn.log 2>&1
print $? > scan-m5dn_vh.status
cat wait-m5dn.log
