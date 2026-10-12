// Ally head-on events (both dragons ours, same turn) in an eval.js label: mover kind (blindDesp = PORTAL? with value < -20, blindVol = PORTAL? otherwise, move = other single/sprint moves; /jump = the hit head was not next to the mover), per-map deaths per side (2 x events / games).
// usage: node exp/cand-swarm9/hon.js <label> [map] [-v] [--keys-from <label>]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-heuristic';
const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
const loader = tf.makeLoader(tf.viewerSource());
const label = process.argv[2], mf = process.argv[3] && !process.argv[3].startsWith('-') ? process.argv[3] : null, dir = path.join(ROOT, 'exp', label), verbose = process.argv.includes('-v');
const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && (!mf || r.map === mf));
const kf = process.argv.indexOf('--keys-from'); if (kf > 0) { const ks = new Set(fs.readFileSync(path.join(ROOT, 'exp', process.argv[kf + 1], 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined).map(r => r.key)); for (let i = rows.length - 1; i >= 0; i--) if (!ks.has(rows[i].key)) rows.splice(i, 1); }
let games = 0; const cnt = {}; const perMap = {};
for (const r of rows) {
  const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
  const R = loader(file), M = R.match.map, side = r.side; games++; perMap[r.map] = perMap[r.map] || { g: 0, e: 0 }; perMap[r.map].g++;
  const team = new Map(); for (const d of M.initialDragons) team.set(d.id, d.team);
  const head = new Map(); for (const d of M.initialDragons) head.set(d.id, d.body[0].x + ',' + d.body[0].y);
  let cur = -1, round = 0, turnDeaths = [], startHead = null; const last = new Map();
  const flush = () => {
    const H = turnDeaths.filter(d => d.reason === 'H');
    if (H.length >= 2 && team.get(cur) === side) { const other = H.find(d => d.id !== cur); if (other && team.get(other.id) === side) {
      const t = last.get(cur) || ''; const vv = parseFloat((t.match(/ v(-?[0-9.]+)/) || [0, 0])[1]); const k = t.includes('PORTAL?') ? (vv < -20 ? 'blindDesp' : 'blindVol') : (/^[NESW]+ /.test(t) ? 'move' : t.split(' ')[0]);
      const [x0, y0] = (startHead || '0,0').split(',').map(Number), [x1, y1] = (head.get(other.id) || '0,0').split(',').map(Number);
      const adj = (Math.min(Math.abs(x0 - x1), M.width - Math.abs(x0 - x1)) + Math.min(Math.abs(y0 - y1), M.height - Math.abs(y0 - y1))) === 1;
      const kk = k + (adj ? '/adj' : '/jump'); cnt[kk] = (cnt[kk] || 0) + 1; perMap[r.map].e++;
      if (verbose) console.log(r.key, 'r' + round, 'mover', cur, 'from', startHead, 'into', other.id, 'at', head.get(other.id), '|', t, '| other:', last.get(other.id));
    } }
    turnDeaths = [];
  };
  for (const e of R.events) {
    if (e.type === 'turnStart') { flush(); cur = e.id; startHead = head.get(cur); if (e.round !== undefined) round = e.round; }
    else if (e.type === 'roundStart' && e.round !== undefined) round = e.round;
    else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); head.set(e.childId, e.childBody[0].x + ',' + e.childBody[0].y); }
    else if (e.type === 'dragonIndicator') last.set(e.id, e.text);
    else if (e.type === 'dragonUpdate') head.set(e.id, e.head.x + ',' + e.head.y);
    else if (e.type === 'dragonDeath') turnDeaths.push({ id: e.id, reason: e.reason });
  }
  flush();
}
console.log(label, mf || 'all', games, 'games; ally head-on by mover kind (total):', JSON.stringify(cnt), 'per game', (Object.values(cnt).reduce((a, b) => a + b, 0) / games).toFixed(2));
console.log('ally head-on DEATHS per side by map (2 x events / games):', Object.entries(perMap).map(([m, o]) => m + ' ' + (2 * o.e / o.g).toFixed(2)).join(', '));
