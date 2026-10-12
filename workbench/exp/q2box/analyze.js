#!/usr/bin/env node
// Read-only replay audit; writes the report only under exp/q2box.
'use strict';
process.env.UNSW_RULES = '123';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '../..'), TASK = __dirname;
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const spec = JSON.parse(fs.readFileSync(path.join(TASK, 'spec.json')));
const skip = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
function fingerprint(R) {
  const h = crypto.createHash('sha256');
  for (const e of R.events) {
    if (skip.has(e.type)) continue;
    const o = {};
    for (const [k, v] of Object.entries(e)) if (k !== 'instructions') o[k] = typeof v === 'bigint' ? String(v) : v;
    h.update(JSON.stringify(o));
  }
  return h.digest('hex');
}
const clean = r => r.G !== undefined && r.exit === 0 && !r.error && !r.botProblem;
const sets = {}, missing = [], historyErrors = [];
for (const dir of new Set(spec.map(s => s.out))) {
  const name = path.basename(dir), file = path.join(ROOT, dir, 'rows.jsonl'), rows = new Map();
  if (fs.existsSync(file)) for (const line of fs.readFileSync(file, 'utf8').split('\n').filter(Boolean)) {
    const r = JSON.parse(line);
    if (clean(r)) rows.set(r.key, r); else historyErrors.push({ set: name, row: r });
  }
  const expected = new Set();
  for (const s of spec.filter(s => s.out === dir)) for (const opp of s.opps) for (const map of s.only)
    for (const side of s.sides) for (const seed of s.seeds) expected.add([path.basename(opp), map, side, seed].join(':'));
  sets[name] = {};
  for (const key of expected) {
    const r = rows.get(key), replay = path.join(ROOT, dir, 'games', key.replace(/:/g, '_'), 'game.replay');
    if (!r || !fs.existsSync(replay)) { missing.push({ set: name, key }); continue; }
    sets[name][key] = audit(load(replay), r);
  }
}
function audit(R, row) {
  const queen = Math.min(...R.match.map.initialDragons.filter(d => d.team === row.side).map(d => d.id));
  const a = { key: row.key, side: row.side, map: row.map, hash: fingerprint(R), queen, death: null,
    seals: [], newborns: [], qwChildren: [], tags: { qbs: 0, qbe: 0 }, cpu: row.cpu || [], queenHeads: [] };
  const lastInd = new Map(), births = new Map(), first = new Set(), starts = new Map();
  const ourIds = new Set(R.match.map.initialDragons.filter(d => d.team === row.side).map(d => d.id));
  for (const e of R.events) if (e.type === 'dragonSplit' && e.team === row.side) ourIds.add(e.childId);
  const ledger = perGame(R, { map: '?', variant: 'a', rules: '123' }, {
    indicator(e) {
      lastInd.set(e.id, e.text || '');
      if (ourIds.has(e.id)) {
        for (const tag of ['qbs', 'qbe']) { const m = (e.text || '').match(new RegExp('(?:^| )' + tag + '(\\d+)(?: |$)')); if (m) a.tags[tag] += +m[1]; }
      }
    },
    split(p, child, e, round) {
      births.set(child.id, { round, length: child.body.length, parent: p.id, qw: p.id === queen && /(?:^| )qw(?: |$)/.test(lastInd.get(p.id) || '') });
      if (births.get(child.id).qw) a.qwChildren.push({ id: child.id, round });
    },
    turn(d, round, c) {
      if (d.id === queen) a.queenHeads.push({ round, head: d.body[0], length: d.body.length });
      if (d.team !== row.side || d.id === queen) return;
      const q = c.drag.get(queen);
      if (!q) return;
      const qh = q.body[0], qneck = q.body[1], exits = [];
      for (const dir of 'NESW') {
        const t = c.across(qh.x, qh.y, dir);
        if (!t || (qneck && t.x === qneck.x && t.y === qneck.y)) continue;
        const k = c.key(t.x, t.y); if (!exits.includes(k)) exits.push(k);
      }
      const occ = new Map(c.occ), free = exits.filter(k => !occ.has(k));
      const visible = c.cheb(d.body[0], qh) <= 3;
      const nonseal = [], outward = [], distance = c.tdist(d.body[0], qh);
      for (const dir of 'NESW') {
        const t = c.across(d.body[0].x, d.body[0].y, dir);
        if (!t || occ.has(c.key(t.x, t.y))) continue;
        const body = [t, ...d.body]; if (!c.pearls.has(c.key(t.x, t.y))) body.pop();
        const after = new Map(occ);
        for (const [k, id] of after) if (id === d.id) after.delete(k);
        for (const b of body) after.set(c.key(b.x, b.y), d.id);
        if (free.length && exits.every(k => after.has(k))) continue;
        nonseal.push(dir); if (c.tdist(t, qh) > distance) outward.push(dir);
      }
      starts.set(d.id, { round, qh: { ...qh }, distance, exits, free, visible, nonsealSingles: nonseal, outwardSingles: outward });
    },
    action(d, e, round, c) {
      const s = starts.get(d.id);
      if (d.team !== row.side || d.id === queen || !s || s.round !== round) return;
      const survivedMove = e.action?.kind === 'move' && !d.fate;
      if (survivedMove && s.free.length && s.exits.every(k => c.occ.has(k)) && s.free.some(k => c.occ.get(k) === d.id)) {
        a.seals.push({ id: d.id, round, ...s, action: e.action, indicator: lastInd.get(d.id) || '' });
      }
      const birth = births.get(d.id);
      if (birth && !first.has(d.id)) {
        first.add(d.id);
        a.newborns.push({ id: d.id, round, ...birth, distance: s.distance, visible: s.visible,
          outwardSingles: s.outwardSingles, action: e.action, diedOnMove: !!d.fate,
          afterDistance: c.tdist(d.body[0], s.qh), indicator: lastInd.get(d.id) || '' });
      }
    },
    death(d, rec, i, other, round) {
      if (d.id === queen) a.death = { round, cause: CAUSE[rec.cause], length: d.body.length, head: d.body[0], other: other?.id ?? null };
    },
    end(rounds, c) { a.rounds = rounds; a.queenAliveAtEnd = c.drag.has(queen); a.queenAlive500 = c.drag.has(queen) && rounds >= 500; },
  });
  a.checks = ledger.chk;
  return a;
}
const pairs = [], identity = [];
for (const [key, on] of Object.entries(sets.on || {})) {
  const off = sets.off?.[key]; if (!off) continue;
  pairs.push({ key, onAlive500: on.queenAlive500, offAlive500: off.queenAlive500,
    survivalRegression: off.queenAlive500 && !on.queenAlive500, onDeath: on.death, offDeath: off.death,
    onSeals: on.seals.length, offSeals: off.seals.length, sameEvents: on.hash === off.hash,
    sameQueenHeads: JSON.stringify(on.queenHeads) === JSON.stringify(off.queenHeads) });
}
for (const [key, off] of Object.entries(sets['id-off'] || {})) {
  const base = sets['id-base']?.[key];
  identity.push({ key, same: !!base && off.hash === base.hash });
}
const report = { expectedGames: 180, missing, historyErrors, identity, pairs, sets };
fs.writeFileSync(path.join(TASK, 'analysis.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ missing: missing.length, identity: `${identity.filter(p => p.same).length}/${identity.length}`,
  pairs: pairs.length, survivalRegressions: pairs.filter(p => p.survivalRegression),
  around: pairs.filter(p => p.key.includes(':around_unsw:')),
  onSeals: Object.values(sets.on || {}).flatMap(a => a.seals.map(s => ({ key: a.key, ...s }))) }, null, 2));
if (missing.length || identity.length !== 12 || identity.some(p => !p.same)) process.exitCode = 1;
