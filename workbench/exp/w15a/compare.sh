#!/bin/bash
# W15a: dead-branch classes, roots and economy per set (both sides), and the split view, for base and the W15a sets given
cd "$(dirname "$0")/../.."
for set in "$@"; do
  echo "=== $set"
  for side in A B; do
    node exp/w15a/deadclass.js $(ls -d exp/w15a/$set/games/*_${side}_1) $side 2>/dev/null | sed -n '/^TOTAL/,$p' | sed "s/^/  $side /"
  done
  echo "  -- voluntary and escape splits (parent view of the child's region)"
  (node exp/w15a/splitview.js A $(ls -d exp/w15a/$set/games/*_A_1); node exp/w15a/splitview.js B $(ls -d exp/w15a/$set/games/*_B_1)) 2>/dev/null | awk '{n=$1; $1=""; a[$0]+=n} END {for (k in a) printf "  %6d %s\n", a[k], k}' | sort -k2
done
