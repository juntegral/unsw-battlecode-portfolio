#!/bin/zsh
cd "${0:A:h}"
for arm in m3b7qk_vh m4qd_vh m5es_vh; do
  (nice -n 10 env PYTHONDONTWRITEBYTECODE=1 python3 dn_scan.py "$arm" > "scan-$arm.log" 2>&1; print $? > "scan-$arm.status") &
done
limit=$((SECONDS + 3600))
until [[ -f scan-m3b7qk_vh.status && -f scan-m4qd_vh.status && -f scan-m5es_vh.status ]] || (( SECONDS >= limit )); do
  sleep 10
done
for arm in m3b7qk_vh m4qd_vh m5es_vh; do
  if [[ -f scan-$arm.status ]]; then
    print "$arm status $(cat scan-$arm.status)"
    cat "scan-$arm.log"
  else
    print "$arm n/a: counting wait reached 60-minute limit; job may still be running"
  fi
done
