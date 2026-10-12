#!/bin/zsh
ROOT="~/01. Project/개인 프로젝트/unsw-swarm"
D="$ROOT/data/codex/astra/maps-sonnet"
rm -f "$D/test_portals.map"
mkdir -p "$D/tools" "$D/out"
cp -r "$ROOT/tools/mapgen" "$D/tools/"
cp "$ROOT/tools/replay2map.js" "$ROOT/tools/pearl_layout.js" "$ROOT/tools/top_features.js" "$ROOT/tools/viewer.js" "$D/tools/"
python3 - <<'E'
import re
p="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/maps-sonnet/tools/viewer.js"
s=open(p).read()
new="const viewer='~/01. Project/개인 프로젝트/unsw-swarm/work/bc129/lib/python3.13/site-packages/unswbc/replay-viewer.vsix';"
s2=re.sub(r"const viewer=path\.join\(root,[^;]*;",new,s)
print(s2!=s)
open(p,"w").write(s2)
E
cd "$D"
node tools/replay2map.js "$ROOT/data/online/smoke/one14-c1-old/M1517689.replay" out/test.map 2>&1 | head -8
