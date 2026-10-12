// kingstat over an online batch (data/online/<dir>): our side (team 583) and the opponent, cache king-online-<dir>.jsonl
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = require('path').resolve(__dirname, '..', '..');
if (process.argv.includes('--ko-worker')) {
  const { analyse } = require('./kingstat.js');
  process.on('message', t => { try { process.send({ t, res: analyse(t.file, t.row) }); } catch (e) { process.send({ t, error: String(e).slice(0, 300) }); } });
  return;
}
const dirName = process.argv[2]; const dir = path.join(ROOT, 'data', 'online', dirName);
const OUT = path.join(__dirname, 'cache', 'king-online-' + dirName + '.jsonl');
const have = new Set(fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
const tasks = [];
for (const f of fs.readdirSync(dir).filter(x => /^game-\d+\.json$/.test(x))) {
  const g = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  const rep = path.join(dir, 'M' + g.id + '.replay'); if (!fs.existsSync(rep) || g.status !== 'completed') continue;
  const side = g.teamAId === 583 ? 'A' : g.teamBId === 583 ? 'B' : null; if (!side || have.has(String(g.id))) continue;
  tasks.push({ key: String(g.id), file: rep, row: { key: String(g.id), map: g.mapName }, side, map: String(g.mapName).toLowerCase().replace(/[^a-z0-9]+/g, '_'), opp: side === 'A' ? g.teamBName : g.teamAName });
}
console.log('tasks', tasks.length);
const q = tasks.slice(); let live = 0;
for (let i = 0; i < Math.min(2, q.length); i++) {
  const c = cp.fork(__filename, ['--ko-worker'], { serialization: 'advanced' }); live++;
  const next = () => { const t = q.shift(); if (!t) { c.kill(); return; } c.send(t); };
  c.on('message', m => { if (!m.error) { const us = m.t.side, th = us === 'A' ? 'B' : 'A'; fs.appendFileSync(OUT, JSON.stringify({ key: m.t.key, map: m.t.map, opp: m.t.opp, side: us, us: m.res[us], them: m.res[th] }) + '\n'); } else console.error(m.t.key, m.error); next(); });
  next();
}
