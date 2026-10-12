'use strict';
// Top-vs-top part of exp/conv-chain/report.js (node exp/conv-chain/report.js top [--all-rounds]).
// Groups: TW / TL = winner / loser of a top-vs-top game on a 500-round map; by default only games that reached round 500.
// Also the elite side of our online sets (X: the top opponents that played our bots) when --x is given.
const fs = require('fs'), path = require('path');
const { grp, tagFree, readJsonl, pct, f1, CACHE, OUR } = require('./report.js');
const { CLS, CI, CPS } = require('./chain.js');
const KC = { id: 0, len: 1, eD: 2, aM8: 3, cen: 4, fr: 5, own: 6, eM8: 7, x: 8, y: 9, anc: 10, fin: 11, dc: 12, dr: 13, fam: 14, famToLine: 15, famAliveLen: 16 };

function groupsOf(allRounds) {
  const seen = new Set(), all = [];
  for (const f of fs.readdirSync(CACHE).filter(f => /^top.*\.jsonl$/.test(f)).sort()) for (const g of readJsonl(path.join(CACHE, f))) { if (seen.has(g.key)) continue; seen.add(g.key); all.push(g); }
  groupsOf.total = all.length;
  const G = all.filter(g => g.kind === 'r500' && (allRounds || g.rounds >= 500) && g.winner);
  return G;
}
function run(argv) {
  const allRounds = argv.includes('--all-rounds');
  const G = groupsOf(allRounds);
  const L = [];
  const W = g => [g.winner], Lo = g => [g.winner === 'A' ? 'B' : 'A'];
  L.push(`## 상위권끼리 500라운드형 ${allRounds ? '모든 판' : '500라운드까지 간 판'}: ${G.length}판 (추출한 500라운드형 판 ${groupsOf.total}) (점검 합: ${JSON.stringify(G.reduce((s, g) => { for (const [k, v] of Object.entries(g.chk)) s[k] = (s[k] || 0) + v; return s; }, {}))})`);
  // 1) sacrifice drops from r300 by class
  for (const [nm, sd] of [['승자', W], ['패자', Lo]]) tagFree(L, G, sd, `${nm}: r300 뒤 희생 사망(최종 왕 제외)의 진주가 간 곳`);
  // by phase for winners (all lengths)
  for (const [nm, sd] of [['승자', W], ['패자', Lo]]) {
    const by = {}; let n = 0;
    for (const g of G) for (const tm of sd(g)) { n++; for (const [k, a] of Object.entries(g[tm].agg)) { const [c, ph, lc] = k.split('|'); if (c !== 'sac' || ph === 'p0' || ph === 'p250') continue; const big = lc === '8-14' || lc === '15+' ? 'L8+' : lc === '5-7' ? 'L5-7' : 'L2-4'; const key = ph + '|' + big; const b = by[key] || (by[key] = new Array(a.length).fill(0)); for (let i = 0; i < a.length; i++) b[i] += a[i]; } }
    L.push(`- ${nm} 희생의 시기(25라운드 단위, 팀·경기당 횟수 / 길이 / 진주 중 계보 몫):`);
    for (const big of ['L2-4', 'L5-7', 'L8+']) {
      const cells = [];
      for (let r = 300; r < 500; r += 25) { const a = by['p' + r + '|' + big]; if (!a) { cells.push(`r${r} –`); continue; } const q = grp(a.slice(6)); cells.push(`r${r} ${f1(a[0] / n)}/${f1(a[1] / n)}/${pct(q.K, a[2])}`); }
      L.push(`  - ${big}: ${cells.join(' · ')}`);
    }
  }
  // 1b) the eaters of sacrifice pearls from r300 by class with the eater's length (s < 8, m >= 8)
  for (const [nm, sd] of [['승자', W], ['패자', Lo]]) {
    const b = new Array(CLS.length).fill(0); let drops = 0, n = 0;
    for (const g of G) for (const tm of sd(g)) { n++; for (const [k, a] of Object.entries(g[tm].agg)) { const [c, ph] = k.split('|'); if (c !== 'sac' || ph === 'p0' || ph === 'p250') continue; drops += a[2]; for (let i = 0; i < CLS.length; i++) b[i] += a[6 + i]; } }
    L.push(`- ${nm} r300 뒤 희생 진주(팀·경기당 ${f1(drops / n)}개)를 먹은 쪽: 최종 왕 자신 ${pct(b[CI.K0], drops)} · 그 순간의 조상 ${pct(b[CI.KA], drops)} · 계보 밖 길이 ≥8 아군 ${pct(b[CI.Mm] + b[CI.S2Km] + b[CI.Sm] + b[CI.Xm], drops)} (가족이 끝까지 삶 ${pct(b[CI.Mm], drops)}, 뒤에 계보에 진주를 줌 ${pct(b[CI.S2Km], drops)}, 다 죽음 ${pct(b[CI.Sm] + b[CI.Xm], drops)}) · 계보 밖 길이 <8 아군 ${pct(b[CI.Ms] + b[CI.S2Ks] + b[CI.Ss] + b[CI.Xs], drops)} (끝까지 삶 ${pct(b[CI.Ms], drops)}, 계보에 줌 ${pct(b[CI.S2Ks], drops)}, 다 죽음 ${pct(b[CI.Ss] + b[CI.Xs], drops)}) · 상대 ${pct(b[CI.E], drops)} · 안 먹힘 ${pct(b[CI.U], drops)}`);
  }
  // 2) line intake of sacrifice pearls after r350 by the sacrificer's length class
  for (const [nm, sd] of [['승자', W], ['패자', Lo]]) {
    const by = {}; let n = 0;
    for (const g of G) for (const tm of sd(g)) { n++; for (const [k, v] of Object.entries(g[tm].lineSac)) by[k] = (by[k] || 0) + v; }
    const sac = Object.entries(by).filter(([k]) => k.startsWith('sac|')).reduce((s, [, v]) => s + v, 0);
    L.push(`- ${nm} 최종 왕 계보가 r350 뒤 먹은 사망 진주(팀·경기당): 우리 희생 ${f1(sac / n)} (${['2', '3', '4', '5-7', '8-14', '15+'].map(c => 'L' + c + ' ' + f1((by['sac|' + c] || 0) / n)).join(', ')}) · 우리 다른 사망 ${f1(Object.entries(by).filter(([k]) => k.startsWith('own-other')).reduce((s, [, v]) => s + v, 0) / n)} · 적 사망 ${f1((by['enemy|-'] || 0) / n)}`);
  }
  // 3) king choice
  for (const [nm, sd] of [['승자', W], ['패자', Lo]]) {
    L.push(`- ${nm}: 최종 왕 계보 드래곤(조상)은 그 시점에 어떤 드래곤이었나`);
    for (const t of CPS) {
      let n = 0, rank1 = 0, ranks = [], ancLen = [], kLen = [], nD = [], n8 = [];
      const cmp = { eD: [0, 0, 0], aM8: [0, 0, 0], cen: [0, 0, 0], fr: [0, 0, 0], own: [0, 0, 0], eM8: [0, 0, 0] }; // ancestor better / equal / worse than the longest
      const fateL = { alive: 0, dead: 0, toLine: 0, fedLine: 0, aliveLen: 0 };
      const top3 = { n: 0, ancIn: 0 };
      for (const g of G) for (const tm of sd(g)) {
        const rows = g[tm].kc[t]; if (!rows || !rows.length) continue;
        const anc = rows.find(r => r[KC.anc] === 1); if (!anc) continue;
        n++;
        const sorted = rows.slice().sort((a, b) => b[KC.len] - a[KC.len] || a[KC.id] - b[KC.id]);
        const rank = sorted.findIndex(r => r === anc) + 1; ranks.push(rank); if (rank === 1) rank1++;
        ancLen.push(anc[KC.len]); kLen.push(sorted[0][KC.len]); nD.push(rows.length); n8.push(rows.filter(r => r[KC.len] >= 8).length);
        if (rank <= 3) top3.ancIn++;
        if (rank !== 1) {
          const k = sorted[0];
          const better = { eD: (a, b) => a > b, aM8: (a, b) => a > b, cen: (a, b) => a >= 0 && (b < 0 || a < b), fr: (a, b) => a > b, own: (a, b) => a > b, eM8: (a, b) => a < b };
          for (const f of Object.keys(cmp)) { const a = anc[KC[f]], b = k[KC[f]]; if (a === b) cmp[f][1]++; else if (better[f](a, b)) cmp[f][0]++; else cmp[f][2]++; }
          if (k[KC.fam] === 'alive') { fateL.alive++; fateL.aliveLen += k[KC.famAliveLen]; } else fateL.dead++;
          if (k[KC.famToLine] > 0) fateL.fedLine++; fateL.toLine += k[KC.famToLine];
        }
      }
      if (!n) continue;
      const med = a => { const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
      const nr = n - rank1;
      L.push(`  - r${t}: 팀·경기 ${n} · 조상이 팀 최장 ${pct(rank1, n)} · 최장 3위 안 ${pct(top3.ancIn, n)} · 조상 길이 평균 ${f1(ancLen.reduce((s, v) => s + v, 0) / n)} (중앙 ${med(ancLen)}) · 팀 최장 평균 ${f1(kLen.reduce((s, v) => s + v, 0) / n)} · 드래곤 수 ${f1(nD.reduce((s, v) => s + v, 0) / n)} (길이 ≥8 ${f1(n8.reduce((s, v) => s + v, 0) / n)}) · 조상 순위 중앙 ${med(ranks)}`);
      L.push(`    - 조상이 최장이 아닌 ${nr}건, 조상 대 최장(조상이 나음/같음/못함): 적 머리 거리 ${cmp.eD.join('/')} · 8칸 안 아군 길이 ${cmp.aM8.join('/')} · 아군과 평균 거리(가까움이 나음) ${cmp.cen.join('/')} · 4걸음 안 빈칸 ${cmp.fr.join('/')} · 자기 영토 ${cmp.own.join('/')} · 8칸 안 적 길이(적음이 나음) ${cmp.eM8.join('/')}`);
      L.push(`    - 그때의 최장 드래곤(가족)의 끝: 끝까지 삶 ${pct(fateL.alive, nr)} (끝 길이 평균 ${f1(fateL.aliveLen / Math.max(1, fateL.alive))}) · 다 죽음 ${pct(fateL.dead, nr)} · 사망 진주를 계보가 먹음 ${pct(fateL.fedLine, nr)} (평균 ${f1(fateL.toLine / Math.max(1, nr))}개)`);
    }
  }
  console.log(L.join('\n'));
}
module.exports = { run, KC };
