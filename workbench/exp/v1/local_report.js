#!/usr/bin/env node
// unsw-swarm v1 local report: the five diagnostic indicators (EVAL.md §2), belief accuracy (versions/v1/VERSION.md §1), safety side effects and
// the v1 tags, for local eval sets (tools/eval.js output: rows.jsonl + games/<key>/game.replay), one set against another on the same keys.
// usage: node exp/v1/local_report.js --a <dir>[,<dir>] --b <dir>[,<dir>] [--names v1,v0] [--jobs 2] [--out report.md]
//   per-game results are cached in <dir>/analysis.jsonl (delete it to recompute).
// Sources per game (the extractors of the research, unchanged):
//   tools/mass_ledger.js perGame   st.units[10] (r100 heads), st.units[25], natural intake (fl nat_*), st.king[50] (final longest), dt (death causes)
//   legacy/exp/endgame-king/extract.js analyse   line sacrifice pearls r300-499 (dec[1..4][1], full games), kd rows (team longest lost from r340)
//   perGame hooks (turn, indicator)   the belief tag " bl<len>@x,y k<0|1>" against the true longest other living ally at that dragon's turn start
// Definitions: our side = rows.jsonl side; families: fortress = autarky, portals, prisoners_dilemma(_10); swarm = the other seven; kinds: r500 = Autarky,
// Portals, Schooltime, Slithery Fight, Trauma; elim = the rest (mass ledger). Elimination = endReason teamEliminated with our units 0.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const NAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', devil_b: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  prisoners_dilemma_10: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', queen_of_spades_b: 'Queen Of Spades', schooltime: 'Schooltime',
  schooltime_b: 'Schooltime', slithery_fight: 'Slithery Fight', slithery_fight_b: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const FORT = new Set(['Autarky', 'Portals', 'Prisoners Dilemma']);
const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
const TAGS = ['sx', 'sxx', 'sxc', 'sr', 'srx', 'src', 'srn', 'sq', 'sc', 'scx', 'sk', 'conv', 'escape-split', 'no-exit', 'no-exit s', 'pocket-eat', 'csplit', 'lsplit', 'frag',
  'kcap', 'floor', 'bsp', 'grab', 'cl', 'tg', 'tgx', 'lntv', 'kx', 'gh', 'feed'];

function analyseGame(file, row) {
  const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const EK = require(path.join(ROOT, 'legacy', 'exp', 'endgame-king', 'extract.js'));
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = makeLoader(viewerSource());
  const R = load(file);
  const map = NAME[row.map], us = row.side, them = us === 'A' ? 'B' : 'A';
  const info = { map };
  if (map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  // belief accuracy: snapshot the truth at each of our dragons' turn start, compare at its indicator
  const snap = new Map();
  const B = { all: newAcc(), late: newAcc(), big: newAcc() };   // late: r >= 300; big: our length >= 8
  const tags = {}; let labelled = 0, eS = 0, eF = 0;
  const sfRecips = [];   // (round, recipient length) of sf feeds
  const chain = { pieces100_430: 0, births100_430: 0, sac: 0, sac300: 0, sacDrops300: 0, sfMain: 0, sfLate: 0 };
  const dup = { n: 0, exact: 0, group: 0 }; let tgRound = -1, tg = [];
  const flushTargets = (W, H) => {
    for (let i = 0; i < tg.length; i++) {
      dup.n++; let ex = 0, gr = 0;
      for (let j = 0; j < tg.length; j++) { if (i === j) continue; const dx = Math.abs(tg[i][0] - tg[j][0]), dy = Math.abs(tg[i][1] - tg[j][1]);
        const m = Math.min(dx, W - dx) + Math.min(dy, H - dy); if (m === 0) ex = 1; if (m <= 3) gr = 1; }
      dup.exact += ex; dup.group += gr;
    }
    tg = [];
  };
  const hooks = {
    split(p, ch, e, round, ctx) {
      if (p.team !== us || round < 100 || round > 430) return;
      chain.births100_430++; if (ch.body.length <= 3) chain.pieces100_430++;
    },
    death(d, rec, idx, other, round, ctx) {
      if (d.team !== us || MLC[rec.cause] !== 'sac') return;
      chain.sac++; if (round >= 300) { chain.sac300++; chain.sacDrops300 += rec.drops; }
    },
    turn(d, round, ctx) {
      if (d.team !== us) return;
      let mx = 0; const heads = [];
      for (const o of ctx.drag.values()) {
        if (o.team !== us || o.id === d.id) continue;
        const L = o.body.length;
        if (L > mx) { mx = L; heads.length = 0; heads.push(o.body[0]); } else if (L === mx) heads.push(o.body[0]);
      }
      snap.set(d.id, { round, my: d.body.length, mx, heads, W: ctx.W, H: ctx.H });
    },
    indicator(e, round, ctx) {
      const s = snap.get(e.id); if (!s || s.round !== round) return;
      const text = e.text || '';
      if (round !== tgRound) { flushTargets(s.W, s.H); tgRound = round; }
      { const m = / (?:sd|F)\d+@(\d+),(\d+)/.exec(text); if (m) tg.push([+m[1], +m[2]]); }
      if (/sf#\d+ a\d+ late/.test(text)) chain.sfLate++; else if (/sf#\d+/.test(text)) chain.sfMain++;
      labelled++;
      if (/ E=S$/.test(text)) eS++; else if (/ E=F$/.test(text)) eF++;
      for (const t of TAGS) if (new RegExp('(^|\\s)' + t + '(\\d|\\s|$|@|#)').test(text)) tags[t] = (tags[t] || 0) + 1;
      if (/ sd\d+@/.test(text)) tags.sd = (tags.sd || 0) + 1;
      const f = /sf#\d+ a(\d+)/.exec(text); if (f) { tags.sf = (tags.sf || 0) + 1; sfRecips.push(+f[1]); }
      const m = / bl(\d+)@(-|(\d+),(\d+)) k([01])/.exec(text);
      if (!m) return;
      const bl = +m[1], k = +m[5], hasPos = m[2] !== '-';
      const trueKing = s.my >= s.mx ? 1 : 0;
      let pos = 0;
      if (hasPos && s.mx > 0) {
        const bx = +m[3], by = +m[4];
        for (const h of s.heads) { const dx = Math.abs(h.x - bx), dy = Math.abs(h.y - by); if (Math.min(dx, s.W - dx) + Math.min(dy, s.H - dy) <= 3) { pos = 1; break; } }
      }
      const r = { k: k === trueKing ? 1 : 0, len: Math.abs(bl - s.mx) <= 1 ? 1 : 0, pos, over: bl > s.mx + 1 ? 1 : 0, under: bl < s.mx - 1 ? 1 : 0,
        falseKing: k === 1 && trueKing === 0 ? 1 : 0, missKing: k === 0 && trueKing === 1 ? 1 : 0, mx: s.mx > 0 ? 1 : 0, tk: trueKing };
      add(B.all, r); if (round >= 300) add(B.late, r); if (s.my >= 8) add(B.big, r);
    },
  };
  const MLC = ML.CAUSE;
  const g = ML.perGame(R, info, hooks);
  flushTargets(R.match.map.width, R.match.map.height);
  const T = g[us], O = g[them];
  const nat = X => ['nat_own', 'nat_enemy', 'nat_neutral'].reduce((a, k) => a + X.fl[ML.FI[k]].reduce((p, q) => p + q, 0), 0);
  const dt = {};
  for (const [k, v] of Object.entries(T.dt)) { const c = k.split('|')[0]; dt[c] = (dt[c] || 0) + v[0]; }
  let eg = null;
  try {
    const X = EK.analyse(R, { key: row.key, map, us, set: 'local', src: 'local', opp: row.opp, oppId: 0 }, ML.perGame);
    const full = side => X.rounds === 500 && X[side] && X[side].kid >= 0;
    const lineSac = side => full(side) ? [1, 2, 3, 4].reduce((a, b) => a + X[side].dec[b][1], 0) : null;
    const kd = X[us] && X[us].kd || [];
    eg = { rounds: X.rounds, lineSac: lineSac(us), lineSacT: lineSac(them), kingLost340: kd.some(q => q[0] >= 340 && q[3] && (q[2] === 2 || q[2] === 3)) ? 1 : 0,
      kingDeaths300: kd.filter(q => q[0] >= 300 && q[3]).length };
  } catch (err) { eg = { error: String(err).slice(0, 160) }; }
  const res = R.result, ro = res['team' + us], rt = res['team' + them];
  return { key: row.key, map, file: row.map, opp: row.opp, fam: FORT.has(map) ? 'fortress' : 'swarm', kind: R500.has(map) ? 'r500' : 'elim',
    won: res.winner === us ? 1 : 0, elim: res.endReason === 'teamEliminated' && ro.dragonCount === 0 ? 1 : 0,
    u100: [T.st.units[10], O.st.units[10]], u250: [T.st.units[25], O.st.units[25]], nat: [nat(T), nat(O)], king: [T.st.king[50], O.st.king[50]],
    total: [T.st.total[50], O.st.total[50]], dt, eg, belief: B, tags, labelled, eS, eF, sfRecips,
    u50: [T.st.units[5], O.st.units[5]], chain, dup };
}
function newAcc() { return { n: 0, k: 0, len: 0, pos: 0, over: 0, under: 0, falseKing: 0, missKing: 0, mx: 0, tk: 0 }; }
function add(a, r) { a.n++; for (const k of Object.keys(r)) a[k] += r[k]; }

// ---- worker mode
if (process.argv[2] === '--worker') {
  process.on('message', t => {
    try { process.send({ key: t.key, dir: t.dir, line: JSON.stringify(analyseGame(t.file, t.row)) }); }
    catch (err) { process.send({ key: t.key, dir: t.dir, error: String((err && err.stack) || err).split('\n').slice(0, 3).join(' | ') }); }
  });
  return;
}

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const setA = arg('a', '').split(',').filter(Boolean), setB = arg('b', '').split(',').filter(Boolean);
const names = arg('names', 'A,B').split(','), jobs = +arg('jobs', '2');
async function collect(dirs) {
  const out = [];
  const tasks = [];
  for (const dir of dirs) {
    const rowsFile = path.join(dir, 'rows.jsonl');
    if (!fs.existsSync(rowsFile)) continue;
    const rows = fs.readFileSync(rowsFile, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)).filter(r => r.G !== undefined);
    const cacheFile = path.join(dir, 'analysis.jsonl');
    const cache = new Map(fs.existsSync(cacheFile) ? fs.readFileSync(cacheFile, 'utf8').trim().split('\n').filter(Boolean).map(l => { const x = JSON.parse(l); return [x.key, x]; }) : []);
    for (const row of rows) {
      if (cache.has(row.key)) { out.push(cache.get(row.key)); continue; }
      const file = path.join(dir, 'games', row.key.replace(/:/g, '_'), 'game.replay');
      if (fs.existsSync(file)) tasks.push({ key: row.key, dir, file, row });
    }
  }
  if (tasks.length) {
    let i = 0;
    await Promise.all(Array.from({ length: Math.min(jobs, tasks.length) }, () => new Promise(res => {
      const w = cp.fork(__filename, ['--worker'], { execArgv: ['--max-old-space-size=3072'] });
      const next = () => { if (i >= tasks.length) { w.kill(); return res(); } w.send(tasks[i++]); };
      w.on('message', m => {
        if (m.line) { fs.appendFileSync(path.join(m.dir, 'analysis.jsonl'), m.line + '\n'); out.push(JSON.parse(m.line)); }
        else process.stderr.write(`${m.key}: ${m.error}\n`);
        next();
      });
      next();
    })));
  }
  return out;
}
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
const f1 = v => v === null || v === undefined || Number.isNaN(v) ? '–' : (Math.round(v * 10) / 10).toFixed(1);
const pc = (k, n) => n ? `${Math.round(100 * k / n)}% (${k}/${n})` : '–';
function cell(G) {
  const n = G.length;
  const natO = G.reduce((s, g) => s + g.nat[0], 0), natT = G.reduce((s, g) => s + g.nat[1], 0);
  const ls = G.filter(g => g.eg && g.eg.lineSac !== null && g.eg.lineSac !== undefined);
  return { n, win: G.filter(g => g.won).length, u100: mean(G.map(g => g.u100[0])), u100T: mean(G.map(g => g.u100[1])), u250: mean(G.map(g => g.u250[0])),
    nat: mean(G.map(g => g.nat[0])), natT: mean(G.map(g => g.nat[1])), ratio: natT ? natO / natT : null,
    line: mean(ls.map(g => g.eg.lineSac)), lineN: ls.length, king: mean(G.map(g => g.king[0])), kingT: mean(G.map(g => g.king[1])),
    elim: G.filter(g => g.elim).length, trap: mean(G.map(g => g.dt.trap || 0)), rammed: mean(G.map(g => g.dt.rammed || 0)), ram: mean(G.map(g => g.dt.ram || 0)),
    allyHead: mean(G.map(g => g.dt.allyHead || 0)), sac: mean(G.map(g => g.dt.sac || 0)),
    kingLost: G.filter(g => g.eg && g.eg.kingLost340).length, kingN: G.filter(g => g.eg && g.eg.rounds > 340).length };
}
function beliefSum(G, part) {
  const a = newAcc();
  for (const g of G) for (const k of Object.keys(a)) a[k] += g.belief[part][k];
  return a;
}
(async () => {
  const A = await collect(setA), Bs = await collect(setB);
  const keysB = new Set(Bs.map(g => g.key)), keysA = new Set(A.map(g => g.key));
  const Ap = A.filter(g => keysB.has(g.key)), Bp = Bs.filter(g => keysA.has(g.key));
  const L = [];
  L.push(`# v1 local report: ${names[0]} (${setA.join(', ')}) vs ${names[1]} (${setB.join(', ')})`, '');
  L.push(`Paired games (same key): ${Ap.length}. ${names[0]} games ${A.length}, ${names[1]} games ${Bs.length}. Opponents: proxy4 (local mimics; sanity only, not a filter).`, '');
  const cells = [['all maps', g => true], ['fortress', g => g.fam === 'fortress'], ['swarm', g => g.fam === 'swarm'], ['swarm · r500', g => g.fam === 'swarm' && g.kind === 'r500'],
    ['swarm · elim', g => g.fam === 'swarm' && g.kind === 'elim'], ['fortress · r500', g => g.fam === 'fortress' && g.kind === 'r500'], ['fortress · elim (PD)', g => g.fam === 'fortress' && g.kind === 'elim']];
  L.push('## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games', '');
  L.push(`| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |`);
  L.push('|---|---|---:|---:|---|---:|---|---|---|---|');
  for (const [name, f] of cells) for (const [bn, G] of [[names[0], Ap], [names[1], Bp]]) {
    const c = cell(G.filter(f)); if (!c.n) continue;
    L.push(`| ${name} | ${bn} | ${c.n} | ${c.win} | ${f1(c.u100)} / ${f1(c.u100T)} | ${f1(c.u250)} | ${f1(c.nat)} / ${f1(c.natT)} (${c.ratio === null ? '–' : Math.round(100 * c.ratio) + '%'}) | ${f1(c.line)} (${c.lineN}) | ${f1(c.king)} / ${f1(c.kingT)} | ${pc(c.elim, c.n)} |`);
  }
  L.push('', '## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)', '');
  L.push('| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |', '|---|---|---:|---:|---:|---:|---:|---|');
  for (const [name, f] of cells.slice(0, 5)) for (const [bn, G] of [[names[0], Ap], [names[1], Bp]]) {
    const c = cell(G.filter(f)); if (!c.n) continue;
    L.push(`| ${name} | ${bn} | ${f1(c.trap)} | ${f1(c.rammed)} | ${f1(c.ram)} | ${f1(c.allyHead)} | ${f1(c.sac)} | ${pc(c.kingLost, c.kingN)} |`);
  }
  L.push('', '## 2b. The chain, link by link (paired games; per game means)', '');
  L.push('Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.', '');
  L.push('| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |');
  L.push('|---|---|---|---:|---|---|---:|---:|---:|---:|---|');
  for (const [name, f] of cells.slice(0, 5)) for (const [bn, G] of [[names[0], Ap], [names[1], Bp]]) {
    const H = G.filter(f); if (!H.length) continue;
    const C = H.filter(g => g.chain);
    const m = fn => mean(C.map(fn));
    const ls = H.filter(g => g.eg && g.eg.lineSac !== null && g.eg.lineSac !== undefined);
    const lineSum = ls.reduce((a, g) => a + g.eg.lineSac, 0), dropSum = ls.reduce((a, g) => a + (g.chain ? g.chain.sacDrops300 : 0), 0);
    L.push(`| ${name} | ${bn} | ${f1(m(g => g.u50[0]))} · ${f1(m(g => g.u100[0]))} | ${f1(m(g => g.nat[0]))} | ${f1(m(g => g.chain.pieces100_430))} (${f1(m(g => g.chain.births100_430))}) | ${f1(m(g => g.chain.sac))} (${f1(m(g => g.chain.sac300))}) | ${f1(m(g => g.chain.sacDrops300))} | ${f1(ls.length ? lineSum / ls.length : null)} | ${dropSum ? Math.round(100 * lineSum / dropSum) + '%' : '–'} | ${f1(m(g => g.king[0]))} | ${f1(m(g => g.chain.sfMain))} · ${f1(m(g => g.chain.sfLate))} |`);
  }
  L.push('', '## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round', '');
  L.push('| family | bot | target turns / game | same tile | within 3 |', '|---|---|---:|---:|---:|');
  for (const fam of ['fortress', 'swarm']) for (const [bn, G] of [[names[0], Ap], [names[1], Bp]]) {
    const H = G.filter(g => g.fam === fam && g.dup); if (!H.length) continue;
    const n = H.reduce((a, g) => a + g.dup.n, 0), ex = H.reduce((a, g) => a + g.dup.exact, 0), gr = H.reduce((a, g) => a + g.dup.group, 0);
    L.push(`| ${fam} | ${bn} | ${f1(n / H.length)} | ${n ? (100 * ex / n).toFixed(1) + '%' : '–'} | ${n ? (100 * gr / n).toFixed(1) + '%' : '–'} |`);
  }
  L.push('', '## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)', '');
  L.push('| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |');
  L.push('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|');
  for (const [name, f] of cells.slice(0, 3)) for (const part of ['all', 'late', 'big']) for (const [bn, G] of [[names[0], Ap], [names[1], Bp]]) {
    const a = beliefSum(G.filter(f), part); if (!a.n) continue;
    const lab = `${name} · ${part === 'all' ? 'all turns' : part === 'late' ? 'r300+' : 'our length >= 8'}`;
    L.push(`| ${lab} | ${bn} | ${a.n} | ${pc(a.k, a.n)} | ${pc(a.tk - a.missKing, a.tk)} | ${pc(a.n - a.tk - a.falseKing, a.n - a.tk)} | ${pc(a.len, a.n)} | ${pc(a.pos, a.mx)} | ${pc(a.over, a.n)} | ${pc(a.under, a.n)} |`);
  }
  L.push('', '## 4. Tags per game (our indicator labels), paired games', '');
  const allTags = [...new Set([...Ap, ...Bp].flatMap(g => Object.keys(g.tags)))].sort();
  L.push(`| family | bot | ${allTags.join(' | ')} |`, `|---|---|${allTags.map(() => '---:').join('|')}|`);
  for (const fam of ['fortress', 'swarm']) for (const [bn, G] of [[names[0], Ap], [names[1], Bp]]) {
    const H = G.filter(g => g.fam === fam); if (!H.length) continue;
    L.push(`| ${fam} | ${bn} | ${allTags.map(t => f1(mean(H.map(g => g.tags[t] || 0)))).join(' | ')} |`);
  }
  const rec = Ap.filter(g => g.fam === 'swarm').flatMap(g => g.sfRecips);
  if (rec.length) {
    const b = [0, 0, 0, 0]; for (const x of rec) b[x <= 4 ? 0 : x <= 7 ? 1 : x <= 15 ? 2 : 3]++;
    L.push('', `sf recipients (${names[0]}, swarm maps): ${rec.length} feeds; recipient length 3-4: ${pc(b[0], rec.length)}, 5-7: ${pc(b[1], rec.length)}, 8-15: ${pc(b[2], rec.length)}, 16+: ${pc(b[3], rec.length)}.`);
  }
  L.push('', '## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated', '');
  L.push(`| map | ${names[0]} W · u100 · nat · longest · elim | ${names[1]} W · u100 · nat · longest · elim |`, '|---|---|---|');
  for (const m of [...new Set(Ap.map(g => g.file))].sort()) {
    const s = G => { const c = cell(G.filter(g => g.file === m)); return `${c.win}/${c.n} · ${f1(c.u100)} · ${f1(c.nat)} · ${f1(c.king)} · ${c.elim}`; };
    L.push(`| ${m} | ${s(Ap)} | ${s(Bp)} |`);
  }
  const text = L.join('\n') + '\n';
  const out = arg('out'); if (out) fs.writeFileSync(out, text); console.log(text);
})();
