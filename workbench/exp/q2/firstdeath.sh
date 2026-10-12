#!/bin/bash
# Q2: the board around our queen's head two rounds before, one round before and at her death, in the first game (rows order) of a set whose
# queen died outside the start-pocket maps. usage: exp/q2/firstdeath.sh <set dir> [map dir for the map files]
cd "$(dirname "$0")/../.."
set=$1; mapdir=${2:-maps/online-20260927}
UNSW_RULES=123 node -e "
const fs=require('fs'),path=require('path');const { makeLoader, viewerSource } = require('./tools/top_features.js');const { perGame, CAUSE } = require('./tools/mass_ledger.js');
const load=makeLoader(viewerSource()); const rows=fs.readFileSync('$set/rows.jsonl','utf8').trim().split('\n').map(JSON.parse);
for (const r of rows) { if (/autarky|dilemma|slithery/i.test(r.map)) continue;
  const f=path.join('$set','games',r.key.replace(/:/g,'_'),'game.replay'); const Q=r.side==='A'?0:1; let out=null, head=null;
  perGame(load(f),{map:r.map,variant:'a'},{ turn(d,round){ if(d.id===Q) head={x:d.body[0].x,y:d.body[0].y,round}; }, death(d,rec,i,o,round){ if(d.id===Q && !out) out={round,cause:CAUSE[rec.cause],x:d.body[0].x,y:d.body[0].y}; } });
  if (out) { console.log(r.key+' '+r.map+' '+r.side+' '+out.round+' '+out.cause+' '+out.x+','+out.y); break; } }
" > /tmp/q2fd.$$ ; read key map side round cause xy < /tmp/q2fd.$$; rm -f /tmp/q2fd.$$
[ -z "$key" ] && { echo "no queen death"; exit 0; }
mf=$(ls $mapdir/$map.map exp/q2/maps-22/$map.map exp/q2/maps-extra/$map.map 2>/dev/null | head -1)
echo "== $set: first queen death $key at r$round ($cause) at $xy"
UNSW_RULES=123 node exp/w7/tunnelpic.js $set/games/${key//:/_}/game.replay $mf $side $xy $((round-2)),$((round-1)),$round --r 4
