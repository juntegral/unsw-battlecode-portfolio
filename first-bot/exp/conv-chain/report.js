#!/usr/bin/env node
// Tables for research/observations/conversion-chain.md from .cache/conv-chain/*.jsonl (exp/conv-chain/chain.js).
// usage: node exp/conv-chain/report.js ours [--sets a,b,...]      our labelled conversions (conv, feed) and gathering episodes
//        node exp/conv-chain/report.js top                         top winners / losers (500-round maps)
//        node exp/conv-chain/report.js cases [--n 3]               selected events per class (selection rule in the doc)
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'conv-chain');
const { CLS, CI } = require('./chain.js');
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l)) : [];
const pct = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
const f1 = x => (Math.round(x * 10) / 10).toFixed(1);
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const CAUSE_KO = ['희생', '갇힘', '박힘', '박음', '적 몸', '아군 머리', '시간 초과', '질주 사망'];
// pearl class groups: to the line, eaten by an own dragon that stayed alive (not the king), that later died, enemy, uneaten
const grp = c => ({ K: c[CI.K0] + c[CI.KA], K0: c[CI.K0], KA: c[CI.KA], M: c[CI.Ms] + c[CI.Mm], S2K: c[CI.S2Ks] + c[CI.S2Km], D: c[CI.Ss] + c[CI.Sm] + c[CI.Xs] + c[CI.Xm], E: c[CI.E], U: c[CI.U] });
const OUR = { stack: ['cand-stack1-online', 'cand-stack2-online', 'cand-stack3-online', 'cand-stack4-online', 'cand-stack5-online'],
  merge2: ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'] };

function ours() {
  const sets = opt('sets', null) ? opt('sets').split(',') : [...OUR.stack, ...OUR.merge2];
  const L = [];
  const groups = {};
  for (const s of sets) {
    const G = readJsonl(path.join(CACHE, 'online-' + s + '.jsonl')); if (!G.length) continue;
    const gname = OUR.merge2.includes(s) ? 'merge2 (3 sets)' : s.startsWith('cand-stack') ? 'stack1-5' : s;
    (groups[gname] = groups[gname] || []).push(...G.map(g => ({ ...g, setName: s })));
  }
  for (const [gname, G] of Object.entries(groups)) {
    const n500 = G.filter(g => g.kind === 'r500').length;
    L.push(`\n### ${gname}: ${G.length}판 (500라운드형 ${n500}판)`);
    for (const kind of ['conv', 'feed']) {
      for (const scope of ['all', 'r500']) {
        const ev = []; for (const g of G) { if (scope === 'r500' && g.kind !== 'r500') continue; for (const v of g[g.us].conv || []) if (v.k === kind) ev.push({ ...v, g }); }
        const ex = ev.filter(v => v.died && v.c);
        if (!ev.length) continue;
        const sum = { K: 0, K0: 0, KA: 0, M: 0, S2K: 0, D: 0, E: 0, U: 0 }; let drops = 0, eff = 0;
        for (const v of ex) { const q = grp(v.c); for (const k in sum) sum[k] += q[k]; drops += v.drops; eff += v.eff; }
        // the target's family after the event (it and every descendant born later): on the final king's line at that moment,
        // some member alive at the end (off the line), or all died (cause of the last death)
        const tf = { line: 0, alive: 0, died: {} }; let tToLine = 0, tMass = 0;
        for (const v of ev) { if (v.tFam === 'line') tf.line++; else if (v.tFam === 'alive') tf.alive++; else { const c = +v.tFam.split(':')[1]; tf.died[CAUSE_KO[c] || c] = (tf.died[CAUSE_KO[c] || c] || 0) + 1; tToLine += v.tFamToLine || 0; tMass += v.tFamMass || 0; } }
        const nDied = ev.length - tf.line - tf.alive;
        L.push(`- ${kind} (${scope === 'all' ? '모든 지도' : '500라운드형'}): 사건 ${ev.length} (죽음 ${ex.length}), 진주 ${drops}개 → 최종 왕 계보 ${pct(sum.K, drops)} (왕 자신 ${pct(sum.K0, drops)}, 조상 ${pct(sum.KA, drops)}) · 끝까지 산 다른 아군(가족) ${pct(sum.M, drops)} · 가족이 다 죽은 아군 ${pct(sum.D + sum.S2K, drops)} (그 가족이 뒤에 계보에 진주를 줌 ${pct(sum.S2K, drops)}) · 상대 ${pct(sum.E, drops)} · 안 먹힘 ${pct(sum.U, drops)} · 실효 계보 몫 ${pct(eff, drops)}`);
        L.push(`  - 지목 아군(가족 기준): 그 순간 최종 왕 계보 ${pct(tf.line, ev.length)} · 계보 아님, 끝까지 가족이 삶 ${pct(tf.alive, ev.length)} · 계보 아님, 가족이 다 죽음 ${pct(nDied, ev.length)} (마지막 죽음: ${Object.entries(tf.died).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + v).join(', ')}; 그 가족의 사망 진주 중 계보로 ${tToLine}개, 가족 질량 ${tMass}) · 그 순간 팀 최장 ${pct(ev.filter(v => v.tRank === 1).length, ev.length)} · 지목 아군 평균 길이 ${f1(ev.reduce((s, v) => s + v.tLen, 0) / ev.length)} (팀 최장 ${f1(ev.reduce((s, v) => s + v.teamLongest, 0) / ev.length)})`);
        const nl = ev.filter(v => !v.tOnLine), nlK = nl.filter(v => v.tRank === 1), lk = ev.filter(v => v.tOnLine);
        L.push(`  - 계보가 아닌 지목 ${nl.length}건 중 그 순간 팀 최장이던 것 ${nlK.length} · 계보인 지목 ${lk.length}건 중 그 순간 팀 최장 ${lk.filter(v => v.tRank === 1).length} · 계보 드래곤이 그 순간 팀 최장이 아닌 사건 ${ev.filter(v => v.lineAt >= 0 && v.lineAt !== v.target).length}`);
      }
    }
    // gathering episodes
    for (const scope of ['all', 'r500']) {
      const E = []; for (const g of G) { if (scope === 'r500' && g.kind !== 'r500') continue; for (const q of g[g.us].gath || []) E.push({ ...q, g }); }
      if (!E.length) continue;
      // family fate from the first g turn: on the line then (the king's line passes through it), some member alive at the end,
      // or all died; the family's labelled sacrifices (feed/conv of it or a descendant)
      const onl = E.filter(q => q.fam === 'line'), al = E.filter(q => q.fam === 'alive'), dd = E.filter(q => q.fam && q.fam.startsWith('dead'));
      const fedF = E.filter(q => q.famFed > 0);
      const dc = {}; for (const q of dd) { const c = +q.fam.split(':')[1]; dc[CAUSE_KO[c]] = (dc[CAUSE_KO[c]] || 0) + 1; }
      const tl = dd.reduce((s, q) => s + q.famToLine, 0), tm = dd.reduce((s, q) => s + q.famMass, 0);
      L.push(`- 모이기(g) 드래곤 (${scope === 'all' ? '모든 지도' : '500라운드형'}): ${E.length}마리(시작 길이 평균 ${f1(E.reduce((s, q) => s + q.L0, 0) / E.length)}) · 그 순간 최종 왕 계보 ${pct(onl.length, E.length)} · 가족이 끝까지 삶(계보 아님) ${pct(al.length, E.length)} (끝 길이 평균 ${f1(al.reduce((s, q) => s + q.famAliveLen, 0) / Math.max(1, al.length))}) · 가족이 다 죽음 ${pct(dd.length, E.length)} (마지막 죽음: ${Object.entries(dc).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + v).join(', ')}; 가족 질량 ${tm} 중 계보가 먹은 사망 진주 ${tl}) · 가족이 표식 희생(feed/conv)을 한 드래곤 ${pct(fedF.length, E.length)}`);
    }
    // tag-independent: own sacrifice deaths from r300 on 500-round maps (not the final king), drop classes
    tagFree(L, G.filter(g => g.kind === 'r500'), g => [g.us]);
  }
  console.log(L.join('\n'));
}

// own-team deaths from r300 (sac) on the given games, drop classes by sacrificer length class
function tagFree(L, G, sides, label = '태그와 무관: r300 뒤 우리 희생 사망(500라운드형, 최종 왕 제외)') {
  const by = {}; let games = 0;
  for (const g of G) for (const tm of sides(g)) {
    games++;
    for (const [k, a] of Object.entries(g[tm].agg || {})) {
      const [cause, ph, lc] = k.split('|'); if (cause !== 'sac' || ph === 'p0' || ph === 'p250') continue;
      const lc2 = lc === '2' || lc === '3' || lc === '4' ? 'L2-4' : lc === '5-7' ? 'L5-7' : 'L8+';
      for (const key of [lc2, 'all']) { const b = by[key] || (by[key] = new Array(a.length).fill(0)); for (let i = 0; i < a.length; i++) b[i] += a[i]; }
    }
  }
  L.push(`- ${label}, 팀·경기 ${games}:`);
  for (const key of ['all', 'L2-4', 'L5-7', 'L8+']) {
    const a = by[key]; if (!a) continue;
    const c = a.slice(6), q = grp(c), drops = a[2];
    L.push(`  - ${key}: 판당 ${f1(a[0] / games)}회 · 길이 ${f1(a[1] / games)} · 진주 ${f1(drops / games)} → 계보 ${pct(q.K, drops)} (왕 자신 ${pct(q.K0, drops)}) · 산 다른 아군 ${pct(q.M, drops)} · 죽은 아군 ${pct(q.D + q.S2K, drops)} (뒤에 계보에 희생 ${pct(q.S2K, drops)}) · 상대 ${pct(q.E, drops)} · 안 먹힘 ${pct(q.U, drops)} · 실효 계보 ${pct(a[3], drops)} · 계보 드래곤이 3칸 안 ${pct(a[5], a[0])} · 그 순간 왕이 먹음 ${pct(a[4], drops)}`);
  }
}

module.exports = { grp, tagFree, readJsonl, pct, f1, CACHE, OUR };
if (require.main === module) {
  if (argv[0] === 'ours') ours();
  else if (argv[0] === 'top') require('./top_report.js').run(argv);
  else console.error('usage: see the header');
}
