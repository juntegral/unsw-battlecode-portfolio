#!/usr/bin/env node
// corner_table.js — markdown summary of corner_study.js outputs: node exp/cand-avoid1/corner_table.js <label>=<file> ... [--opp <name>]
const fs = require('fs');
const argv = process.argv.slice(2);
const oi = argv.indexOf('--opp'), oppF = oi >= 0 ? argv[oi + 1] : null;
const sets = argv.filter(a => a.includes('=') && !a.startsWith('--')).map(a => { const [k, f] = a.split('='); const [name, opp] = k.split(':'); let A = JSON.parse(fs.readFileSync(f)); if (opp) A = A.filter(x => x.opp === opp); if (oppF) A = A.filter(x => x.opp === oppF); return [name, A]; });
const pc = (n, d) => d ? (100 * n / d).toFixed(1) + '%' : '-';
const rate = X => `${X.filter(x => x.rammed).length}/${X.length} (${pc(X.filter(x => x.rammed).length, X.length)})`;
const nextAll = X => { const n = X.filter(x => x.nextAllExposed != null); return `${pc(n.filter(x => x.nextAllExposed).length, n.length)}`; };
const rows = sets.map(([k, A]) => {
  const games = new Set(A.map(x => x.game)).size;
  const exp = A.filter(x => x.chExp), cor = A.filter(x => !x.chExp && x.chCorner), nei = A.filter(x => x.chExp === false && !x.chCorner && !x.chNoExit);
  const all = A.filter(x => x.allExposed), s2 = all.filter(x => x.safe2 > 0), s3 = all.filter(x => !x.safe2 && x.safe3 > 0), none = all.filter(x => !x.safe2 && !x.safe3), spr = all.filter(x => x.sprint);
  return [k, games, A.length, rate(exp), `${cor.length} → ${nextAll(cor)}`, `${nei.length} → ${nextAll(nei)}`, rate(all), `${s2.length} (${pc(s2.length, all.length)})`, `${s3.length}`, `${none.length}`, rate(spr), rate(all.filter(x => !x.sprint))];
});
const head = ['자료', '판', 'L≥6 결정(짧은 적 머리 보임)', '고른 수가 노출 → 다음 결정 전 박힘', '고른 수가 몰릴 수 있음 → 다음 결정에 한 걸음 모두 노출', '둘 다 아님 → 같은 비율', '한 걸음 모두 노출 → 박힘', '그중 안전한 2칸 질주 있음', '3칸만', '없음', '모두 노출일 때 질주함 → 박힘', '질주 안 함 → 박힘'];
console.log(['| ' + head.join(' | ') + ' |', '|' + head.map(() => '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n'));
