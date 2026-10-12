#!/bin/zsh
# usage: run.zsh <jobs file> ; each line: botA botB map seed outdir (relative to ~/meow-redteam)
cd ~/meow-redteam
n=0
while read -r a b m s o; do
  [[ -z "$a" ]] && continue
  mkdir -p "$(dirname "$o")"; rm -f "$o/stdout.txt"; rmdir "$o" 2>/dev/null
  QCTAG="${o:h:t}__${o:t}" ./play.sh "solo/bots/$a" "solo/bots/$b" "$m" "$s" "$o" > "$o.out" 2>&1 &
  n=$((n+1))
  if (( n % 8 == 0 )); then wait; fi
done < "$1"
wait
echo done
