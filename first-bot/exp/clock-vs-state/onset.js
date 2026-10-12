// Is the elite late-sacrifice onset clock-like (same round everywhere) or state-like (varies with the game's state)?
// Input: .cache/mass-ledger/top-sample.jsonl (1,482 stratified top-vs-top games) + our online sets.
const fs = require('fs'), path = require('path'), readline = require('readline');
const H = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { FL } = require(path.join(H, 'tools/mass_ledger.js'));
const SAC = FL.indexOf('dl_sac');
const med = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const q = (a, p) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
const sd = a => { const m = a.reduce((s, x) => s + x, 0) / a.length; return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / a.length); };
function corr(x, y) { const n = x.length; if (n < 5) return null; const mx = x.reduce((s, v) => s + v, 0) / n, my = y.reduce((s, v) => s + v, 0) / n; let a = 0, b = 0, c = 0; for (let i = 0; i < n; i++) { a += (x[i] - mx) * (y[i] - my); b += (x[i] - mx) ** 2; c += (y[i] - my) ** 2; } return a / Math.sqrt(b * c); }
(async () => {
  const rows = [];
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(H, '.cache/mass-ledger/top-sample.jsonl')) });
  for await (const line of rl) {
    const g = JSON.parse(line);
    if (g.rounds < 500) continue;                       // the endgame exists only in games that reach round 500
    for (const side of ['A', 'B']) {
      const t = g[side], team = side === 'A' ? g.teamA : g.teamB, other = g[side === 'A' ? 'B' : 'A'];
      const sac = t.fl[SAC];                              // length sacrificed per 10-round bin
      const late = sac.slice(20, 50), S = late.reduce((s, v) => s + v, 0);
      if (S < 10) continue;
      let cum = 0, on10 = null, on50 = null;
      for (let b = 20; b < 50; b++) { cum += sac[b]; if (on10 === null && cum >= 0.1 * S) on10 = b * 10; if (on50 === null && cum >= 0.5 * S) on50 = b * 10; }
      const st = t.st, i = 25;                              // state before r250
      rows.push({ map: g.map, team, win: g.winner === side ? 1 : 0, S, on10, on50,
        units250: st.units[i], total250: st.total[i], king250: st.king[i], lead250: st.king[i] - other.st.king[i], small250: st.small[i] });
    }
  }
  console.log('team-games with >=10 length sacrificed after r200 (games reaching r500):', rows.length);
  // 1. by map
  const by = (k) => { const m = new Map(); for (const r of rows) { const v = r[k]; if (!m.has(v)) m.set(v, []); m.get(v).push(r); } return m; };
  console.log('\nby map: n | onset10 median [q25,q75] | onset50 median [q25,q75]');
  for (const [mp, rs] of [...by('map')].sort()) { const a = rs.map(r => r.on10), b = rs.map(r => r.on50); console.log(`${mp.padEnd(18)} ${String(rs.length).padStart(4)} | ${med(a)} [${q(a, .25)},${q(a, .75)}] | ${med(b)} [${q(b, .25)},${q(b, .75)}]`); }
  // 2. by team (teams with >= 40 team-games): spread of onset50 across all maps, and within-map spread
  console.log('\nby team: n | onset50 median, SD across all | mean within-map SD | map medians');
  for (const [tm, rs] of [...by('team')].filter(([, rs]) => rs.length >= 40).sort((a, b) => b[1].length - a[1].length)) {
    const b = rs.map(r => r.on50); const mm = new Map(); for (const r of rs) { if (!mm.has(r.map)) mm.set(r.map, []); mm.get(r.map).push(r.on50); }
    const wsd = [...mm.values()].filter(v => v.length >= 4).map(sd); const mmed = [...mm].filter(([, v]) => v.length >= 4).map(([k, v]) => `${k.split(' ')[0]}:${med(v)}`).join(' ');
    console.log(`${tm.slice(0, 22).padEnd(22)} ${String(rs.length).padStart(4)} | ${med(b)}, SD ${sd(b).toFixed(0)} | ${wsd.length ? (wsd.reduce((s, v) => s + v, 0) / wsd.length).toFixed(0) : '-'} | ${mmed}`);
  }
  // 3. within-map correlation of onset50 with state at r250
  console.log('\nwithin-map correlation of onset50 with state at r250 (pooled after subtracting map means):');
  const feats = ['units250', 'total250', 'king250', 'lead250', 'small250', 'S'];
  const mm = by('map'), X = {}, Y = [];
  for (const f of feats) X[f] = [];
  for (const [, rs] of mm) { if (rs.length < 10) continue; const my = rs.reduce((s, r) => s + r.on50, 0) / rs.length; const mx = {}; for (const f of feats) mx[f] = rs.reduce((s, r) => s + r[f], 0) / rs.length; for (const r of rs) { Y.push(r.on50 - my); for (const f of feats) X[f].push(r[f] - mx[f]); } }
  for (const f of feats) console.log(`  ${f.padEnd(9)} r = ${corr(X[f], Y).toFixed(2)}`);
  // 4. share of variance of onset50 explained by map vs team vs residual
  const all = rows.map(r => r.on50), tot = sd(all) ** 2;
  const within = (k) => { let s = 0; for (const [, rs] of by(k)) { const v = rs.map(r => r.on50); const m = v.reduce((a, b) => a + b, 0) / v.length; s += v.reduce((a, b) => a + (b - m) ** 2, 0); } return s / all.length; };
  console.log(`\nonset50 SD overall ${Math.sqrt(tot).toFixed(0)} rounds; within-map SD ${Math.sqrt(within('map')).toFixed(0)}; within-team SD ${Math.sqrt(within('team')).toFixed(0)}`);
  const keyTM = r => r.team + '|' + r.map; const m2 = new Map(); for (const r of rows) { const k = keyTM(r); if (!m2.has(k)) m2.set(k, []); m2.get(k).push(r.on50); }
  let s2 = 0; for (const v of m2.values()) { const m = v.reduce((a, b) => a + b, 0) / v.length; s2 += v.reduce((a, b) => a + (b - m) ** 2, 0); }
  console.log(`within team×map SD ${Math.sqrt(s2 / all.length).toFixed(0)} rounds`);
})();
