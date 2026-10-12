#!/usr/bin/env node
// v1.1 local spatial check (versions/v1.1/VERSION.md §3), for local eval sets (tools/eval.js output: rows.jsonl + games/<key>/game.replay):
//   1. our head share by frontier bin (own-deep 0 .. enemy-deep 4; exp/spatial/lib.js geometry(), our team's point of view) at the round starts of
//      r25 / r50 / r100 / r250 (every living dragon of ours at its turn start in that round; games that reached the round), vs the v1.1 target
//      (policy.hpp FRONT_POLICY) - pooled heads, as the study's headShare;
//   2. natural intake us / them (mass ledger nat_*), deaths of ours by cause (trap; head-on with an enemy: rammed = their move, ram = ours; allyHead;
//      enemyBody; sac), king deaths (the mass ledger's rec.king: the team's longest at its death, length >= 8) by cause;
//   3. king exposure: the share of rounds r100-499 in which our longest living dragon (round start; ties: the lower id) is within path distance 6
//      (and 3) of an enemy head (actual positions; kelp, portals, wrap; bodies ignored - the atlas's distance);
//   4. the v1.1 tags per game (sd bins " f<b>", contested " f<b>c", king floor " kf<d>", beacon " kb" / " kbr").
// usage: node exp/v11/fbin.js --sets name=dir[,dir] [--sets name2=dir] [--maps swarm|all] [--opp proxy4_king] [--out file.md] [--jobs 3] [--cache dir]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const NAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', devil_b: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  prisoners_dilemma_10: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', queen_of_spades_b: 'Queen Of Spades', schooltime: 'Schooltime',
  schooltime_b: 'Schooltime', slithery_fight: 'Slithery Fight', slithery_fight_b: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const FORT = new Set(['Autarky', 'Portals', 'Prisoners Dilemma']);
const CPS = [25, 50, 100, 250];
const layoutOf = f => /_b$/.test(f) ? 'b' : /_10$/.test(f) ? '10' : 'a';

function analyseGame(file, row) {
  const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const { geometry } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = makeLoader(viewerSource());
  const R = load(file), M = R.match.map, W = M.width;
  const map = NAME[row.map], us = row.side, them = us === 'A' ? 'B' : 'A';
  // online sets (exp/online-eval) name both layouts by the family: the layout from the natural spawn support (the spatial study's identify())
  let layout = layoutOf(row.map);
  if (layout === 'a' && ['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight'].includes(map) && !/_b$/.test(row.map)) {
    const { identify } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
    try { const id = identify(R, { map, gameId: row.gameId || 0 }); if (id.layout === 'b') layout = 'b'; } catch (e) {}
  }
  const g = geometry(M, 'x', '?'), bin = g.bin[us];
  const heads = {}; for (const c of CPS) heads[c] = null;
  const deaths = {}, kingDeaths = {};
  let lastRound = -1, expo = { n: 0, d6: 0, d3: 0 };
  const tags = { f: [0, 0, 0, 0, 0], fc: 0, sd: 0, kf: 0, kfx: 0, kb: 0, kbr: 0, sk: 0, fr: {} };
  const dist = new Int16Array(g.N), q = new Int32Array(g.N);
  const hooks = {
    turn(d, round, ctx) {
      if (round !== lastRound) {   // the first turn of a round: the round-start snapshot (king exposure)
        lastRound = round;
        if (round >= 100) {
          let king = null;
          for (const o of ctx.drag.values()) if (o.team === us && (!king || o.body.length > king.body.length || (o.body.length === king.body.length && o.id < king.id))) king = o;
          if (king) {
            const enemy = new Set(); for (const o of ctx.drag.values()) if (o.team === them) enemy.add(o.body[0].y * W + o.body[0].x);
            dist.fill(-1); let n = 0; const s = king.body[0].y * W + king.body[0].x; dist[s] = 0; q[n++] = s; let found = 99;
            for (let i = 0; i < n && found === 99; i++) {
              const t = q[i]; if (enemy.has(t)) { found = dist[t]; break; }
              if (dist[t] >= 6) continue;
              for (const v of g.nb[t]) if (dist[v] < 0) { dist[v] = dist[t] + 1; q[n++] = v; }
            }
            expo.n++; if (found <= 6) expo.d6++; if (found <= 3) expo.d3++;
          }
        }
      }
      if (d.team !== us || !(round in heads)) return;
      const h = heads[round] || (heads[round] = [0, 0, 0, 0, 0, 0]);
      const b = bin[d.body[0].y * W + d.body[0].x]; h[b === undefined ? 5 : b]++;
    },
    death(d, rec, idx, other, round, ctx) {
      if (d.team !== us) return;
      const c = ML.CAUSE[rec.cause] || String(rec.cause);
      deaths[c] = (deaths[c] || 0) + 1;
      if (rec.king) kingDeaths[c] = (kingDeaths[c] || 0) + 1;   // the mass ledger's king death: the team's longest now, length >= 8
    },
    indicator(e) {
      const t = e.text || '';
      if (!/ E=S$/.test(t) && !/ E=[FW]$/.test(t)) return;
      const f = / f([0-4])(c?)(\s|$)/.exec(t); if (f) { tags.f[+f[1]]++; if (f[2]) tags.fc++; }
      if (/ sd\d+@/.test(t)) tags.sd++;
      const k = / kf(\d)(x?)(\s|$)/.exec(t); if (k) { tags.kf++; if (k[2]) tags.kfx++; }
      if (/ kb(\s|$)/.test(t)) tags.kb++; if (/ kbr(\s|$)/.test(t)) tags.kbr++; if (/ sk(\s|$)/.test(t)) tags.sk++;
      const g = / fr([0-4])([opn])/.exec(t);   // v1.1 guard diagnostic: with an sd tag the head went to another bin; without one it took no group at all
      if (g) { const o = / sd\d+@/.test(t) ? tags.fr : (tags.frNone || (tags.frNone = {})); o[g[1] + g[2]] = (o[g[1] + g[2]] || 0) + 1; }
    },
  };
  const G = ML.perGame(R, { map }, hooks);
  const nat = X => ['nat_own', 'nat_enemy', 'nat_neutral'].reduce((a, k) => a + X.fl[ML.FI[k]].reduce((p, q2) => p + q2, 0), 0);
  const res = R.result;
  return { key: row.key, map, file: row.map, layout, opp: row.opp, fort: FORT.has(map), won: res.winner === us ? 1 : 0,
    elim: res.endReason === 'teamEliminated' && res['team' + us].dragonCount === 0 ? 1 : 0, heads, nat: [nat(G[us]), nat(G[them])], deaths, kingDeaths, expo, tags,
    final: [res['team' + us].dragonCount > 0 ? res['team' + us].longestDragon : 0, res['team' + them].longestDragon] };
}

if (process.argv[2] === '--worker') {
  process.on('message', t => { let r; try { r = analyseGame(t.file, t.row); } catch (e) { r = { key: t.row.key, error: String(e.stack || e).slice(0, 300) }; } process.send(r); });
  return;
}

const args = process.argv.slice(2), get = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const sets = []; for (let i = 0; i < args.length; i++) if (args[i] === '--sets') { const [nm, ds] = args[i + 1].split('='); sets.push({ name: nm, dirs: ds.split(',') }); }
const mapsMode = get('--maps') || 'swarm', oppOnly = get('--opp'), out = get('--out'), jobs = +(get('--jobs') || 3), cacheDir = get('--cache');   // --cache: keep the per-game cache there (sets outside exp/v11)
// the v1.1 targets (policy.hpp FRONT_POLICY)
const TARGET = {};
{ const src = fs.readFileSync(path.join(ROOT, 'versions', 'v1.1', 'bot', 'policy.hpp'), 'utf8');
  for (const m of src.matchAll(/\{"(\w+)", '(.)', \{\{([\d, ]+)\}, \{([\d, ]+)\}, \{([\d, ]+)\}, \{([\d, ]+)\}\}\}/g)) {
    const fam = m[1].replace(/_/g, ' '); TARGET[fam + '/' + m[2]] = [m[3], m[4], m[5], m[6]].map(s => s.split(',').map(Number)); } }
const targetOf = (map, lay) => TARGET[map + '/' + lay] || TARGET[map + '/*'] || null;

(async () => {
  const results = {};
  for (const S of sets) {
    const tasks = [];
    for (const dir of S.dirs) {
      const cache = cacheDir ? path.join(cacheDir, path.basename(dir) + '.fbin.jsonl') : path.join(dir, 'fbin.jsonl');
      const have = new Map(fs.existsSync(cache) ? fs.readFileSync(cache, 'utf8').trim().split('\n').filter(Boolean).map(l => { const o = JSON.parse(l); return [o.key, o]; }) : []);
      const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && (!oppOnly || r.opp === oppOnly));
      const seen = new Set();
      for (const r of rows) {
        if (seen.has(r.key)) continue; seen.add(r.key);
        const map = NAME[r.map]; if (mapsMode === 'swarm' && FORT.has(map)) continue;
        const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
        tasks.push({ file, row: r, cache, have: have.get(r.key) });
      }
    }
    const res = [];
    const todo = tasks.filter(t => !t.have); for (const t of tasks) if (t.have) res.push(t.have);
    await new Promise(done => {
      if (!todo.length) return done();
      let next = 0, live = 0;
      const spawn = () => {
        if (next >= todo.length) { if (!live) done(); return; }
        const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'ignore', 'inherit', 'ipc'] }); live++;
        const feed = () => { if (next >= todo.length) { w.kill(); live--; if (!live) done(); return; } const t = todo[next++]; w.once('message', r => { res.push(r); if (!r.error) fs.appendFileSync(t.cache, JSON.stringify(r) + '\n'); else console.error(t.row.key, r.error); feed(); }); w.send(t); };
        feed();
      };
      for (let j = 0; j < Math.min(jobs, todo.length); j++) spawn();
    });
    results[S.name] = res.filter(r => !r.error);
  }
  const names = sets.map(s => s.name);
  const keysOf = n => new Set(results[n].map(r => r.key));
  const unpaired = args.includes('--unpaired');   // sets of different games (online waves): every game of each set
  const common = unpaired ? names.flatMap(n => [...keysOf(n)].map(k => n + '|' + k)) : names.length > 1 ? [...keysOf(names[0])].filter(k => names.every(n => keysOf(n).has(k))) : [...keysOf(names[0])];
  const C0 = new Set(common);
  const C = { has: k => unpaired || C0.has(k) };
  const pc = (a, n) => n ? Math.round(100 * a / n) + '' : '–';
  const L = [`# v1.1 spatial check: ${names.join(' vs ')}`, '', `${unpaired ? 'Unpaired sets; games: ' + names.map(n => n + ' ' + results[n].length).join(', ') : 'Paired games (same key in every set): ' + common.length}. Sets: ${sets.map(s => s.name + ' = ' + s.dirs.join(', ')).join('; ')}. Opponents: those of each set (local proxies: sanity only, not a filter).`, ''];
  // 1. head share by bin
  L.push('## 1. Our head share by frontier bin (own-deep 0 .. enemy-deep 4), % of our heads at the round start; target = v1.1 FRONT_POLICY (elite winners)', '');
  L.push('| map / layout | r | target | ' + names.map(n => `${n} share (heads/game, N)`).join(' | ') + ' |', '|---|---:|---|' + names.map(() => '---|').join(''));
  const groups = {};
  for (const n of names) for (const r of results[n]) if (C.has(r.key)) { const k = r.map + '/' + (['Default', 'Trauma', 'Trophy'].includes(r.map) ? 'a' : r.layout); (groups[k] || (groups[k] = {}))[n] = (groups[k][n] || []).concat([r]); }
  const cellFor = (rs, c) => { const s = [0, 0, 0, 0, 0, 0]; let N = 0; for (const r of rs) { const h = r.heads[c]; if (!h) continue; N++; h.forEach((v, i) => s[i] += v); } const t = s.reduce((a, b) => a + b, 0); return { s, t, N }; };
  const pooled = {};
  for (const k of Object.keys(groups).sort()) {
    const [map, lay] = k.split('/'); const tgt = targetOf(map, lay);
    for (const [ci, c] of CPS.entries()) {
      const cells = names.map(n => { const x = cellFor(groups[k][n] || [], c); const P = pooled[n + c] || (pooled[n + c] = { s: [0, 0, 0, 0, 0, 0], t: 0, N: 0 }); x.s.forEach((v, i) => P.s[i] += v); P.t += x.t; P.N += x.N;
        return x.t ? `${x.s.slice(0, 5).map(v => pc(v, x.t)).join('·')} (${(x.t / x.N).toFixed(1)}, ${x.N})` : '–'; });
      L.push(`| ${k} | ${c} | ${tgt ? tgt[ci].join('·') : '–'} | ${cells.join(' | ')} |`);
    }
  }
  for (const c of CPS) L.push(`| **all swarm** | ${c} | – | ${names.map(n => { const P = pooled[n + c]; return P && P.t ? `${P.s.slice(0, 5).map(v => pc(v, P.t)).join('·')} (${(P.t / P.N).toFixed(1)}, ${P.N})` : '–'; }).join(' | ')} |`);
  // 2. outcome, intake, deaths
  L.push('', '## 2. Outcome, natural intake, deaths of ours (per game), king deaths (length >= 8, team longest at death), king exposure (r100-499)', '');
  L.push('| map / layout | set | games | wins | eliminated | final longest us / them | natural intake us / them | trap | rammed | ram | allyHead | enemyBody | sac | king deaths (cause) | king within 6 / 3 |', '|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|');
  const row2 = (label, n, rs) => {
    if (!rs.length) return;
    const m = f => (rs.reduce((a, r) => a + f(r), 0) / rs.length);
    const kd = {}; for (const r of rs) for (const [c, v] of Object.entries(r.kingDeaths)) kd[c] = (kd[c] || 0) + v;
    const ex = rs.reduce((a, r) => ({ n: a.n + r.expo.n, d6: a.d6 + r.expo.d6, d3: a.d3 + r.expo.d3 }), { n: 0, d6: 0, d3: 0 });
    L.push(`| ${label} | ${n} | ${rs.length} | ${rs.reduce((a, r) => a + r.won, 0)} | ${rs.reduce((a, r) => a + r.elim, 0)} | ${m(r => r.final[0]).toFixed(1)} / ${m(r => r.final[1]).toFixed(1)} | ${m(r => r.nat[0]).toFixed(0)} / ${m(r => r.nat[1]).toFixed(0)} (${pc(rs.reduce((a, r) => a + r.nat[0], 0), rs.reduce((a, r) => a + r.nat[1], 0))}%) | ` +
      ['trap', 'rammed', 'ram', 'allyHead', 'enemyBody', 'sac'].map(c => m(r => r.deaths[c] || 0).toFixed(1)).join(' | ') + ` | ${Object.entries(kd).map(([c, v]) => c + ' ' + v).join(', ') || '0'} | ${pc(ex.d6, ex.n)}% / ${pc(ex.d3, ex.n)}% (${ex.n}) |`);
  };
  for (const k of Object.keys(groups).sort()) for (const n of names) row2(k, n, groups[k][n] || []);
  for (const n of names) row2('**all swarm**', n, results[n].filter(r => C.has(r.key)));
  // 3. tags
  L.push('', '## 3. v1.1 tags per game (sd turns; share of sd turns by target bin; contested; king floor turns / breaking the floor; beacon / relay)', '');
  L.push('| set | games | sd turns | target bin 0·1·2·3·4 (%) | contested (%) | sk turns | kf turns | kfx | kb | kbr |', '|---|---:|---:|---|---:|---:|---:|---:|---:|---:|');
  for (const n of names) {
    const rs = results[n].filter(r => C.has(r.key)); if (!rs.length) continue;
    const s = k => rs.reduce((a, r) => a + r.tags[k], 0); const fb = [0, 1, 2, 3, 4].map(i => rs.reduce((a, r) => a + r.tags.f[i], 0)), ft = fb.reduce((a, b) => a + b, 0);
    L.push(`| ${n} | ${rs.length} | ${(s('sd') / rs.length).toFixed(0)} | ${fb.map(v => pc(v, ft)).join('·')} | ${pc(s('fc'), ft)} | ${(s('sk') / rs.length).toFixed(0)} | ${(s('kf') / rs.length).toFixed(0)} | ${(s('kfx') / rs.length).toFixed(1)} | ${(s('kb') / rs.length).toFixed(1)} | ${(s('kbr') / rs.length).toFixed(1)} |`);
  }
  // 4. the guard (v1.1 VERSION.md §8): sd turns whose top-deficit bin held no group we may take, per map (" fr<b><o|p|n>")
  L.push('', '## 4. Guard: sd turns whose top-deficit bin held no group we may take, so the head went to another bin (" fr<b><why>")', '');
  L.push('o = that bin has 2-core food in reach (owned by an ally, contested, vetoed or too poor); p = only pocket food in reach; n = no food of that bin in reach.', '');
  L.push('Redirected = the turn has an sd target in another bin; no group = the dragon could take no group at all (it follows the pearl field).', '');
  L.push('| map / layout | set | sd turns | redirected (% of sd turns) | o · p · n | top bins redirected from (0·1·2·3·4) | no group at all: o · p · n |', '|---|---|---:|---:|---|---|---|');
  for (const k of Object.keys(groups).sort()) for (const n of names) {
    const rs = groups[k][n] || []; if (!rs.length) continue;
    const sd = rs.reduce((a, r) => a + r.tags.sd, 0), fr = {}; for (const r of rs) for (const [x, v] of Object.entries(r.tags.fr || {})) fr[x] = (fr[x] || 0) + v;
    const tot = Object.values(fr).reduce((a, b) => a + b, 0); if (!tot && !sd) continue;
    const by = c => Object.entries(fr).filter(([x]) => x[1] === c).reduce((a, [, v]) => a + v, 0), bin = b => Object.entries(fr).filter(([x]) => x[0] === String(b)).reduce((a, [, v]) => a + v, 0);
    const fn = {}; for (const r of rs) for (const [x, v] of Object.entries(r.tags.frNone || {})) fn[x] = (fn[x] || 0) + v;
    const byN = c => Object.entries(fn).filter(([x]) => x[1] === c).reduce((a, [, v]) => a + v, 0);
    L.push(`| ${k} | ${n} | ${sd} | ${tot} (${pc(tot, sd)}%) | ${['o', 'p', 'n'].map(by).join(' · ')} | ${[0, 1, 2, 3, 4].map(bin).join(' · ')} | ${['o', 'p', 'n'].map(byN).join(' · ')} |`);
  }
  const text = L.join('\n') + '\n';
  if (out) fs.writeFileSync(out, text); else process.stdout.write(text);
})();
