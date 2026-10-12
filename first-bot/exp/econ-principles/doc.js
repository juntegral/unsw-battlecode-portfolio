#!/usr/bin/env node
// Renders research/observations/economy-principles.md from exp/econ-principles/doc-template.md and acc.json
// (written by report.js). Every {{ expression }} in the template is evaluated with the helpers below in scope, so every
// number in the note comes from the same accumulators as exp/econ-principles/report.txt.
// usage: node exp/econ-principles/doc.js [--out research/observations/economy-principles.md]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const { A, D } = JSON.parse(fs.readFileSync(path.join(__dirname, 'acc.json'), 'utf8'));
const MAPS = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma', 'Default', 'Devil', 'Prisoners Dilemma', 'Queen Of Spades', 'Trophy'];
const MAPK = { 'Autarky': 'Autarky', 'Portals': 'Portals', 'Schooltime': 'Schooltime', 'Slithery Fight': 'Slithery', 'Trauma': 'Trauma', 'Default': 'Default', 'Devil': 'Devil', 'Prisoners Dilemma': 'PD', 'Queen Of Spades': 'QoS', 'Trophy': 'Trophy' };
const ok = v => v !== null && v !== undefined && isFinite(v);
const pc = v => ok(v) ? (100 * v).toFixed(0) + '%' : '–';
const f0 = v => ok(v) ? Math.round(v).toLocaleString('en-US') : '–';
const f1 = v => ok(v) ? (Math.round(v * 10) / 10).toFixed(1) : '–';
const f2 = v => ok(v) ? v.toFixed(2) : '–';
const sg = v => ok(v) ? (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(2) : '–';
const sg1 = v => ok(v) ? (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(1) : '–';
const Z = n => new Array(n).fill(0);
const get = (o, k, n = 12) => (o && o[k]) || Z(n);
const sum = (...arrs) => { const n = Math.max(...arrs.map(a => a.length)); const r = Z(n); for (const a of arrs) for (let i = 0; i < a.length; i++) r[i] += a[i]; return r; };
const tbl = (head, rows) => ['| ' + head.join(' | ') + ' |', '|' + head.map((h, i) => i === 0 ? '---' : '---:').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const B8 = ['≤−3', '−2', '−1', '0', '+1', '+2', '≥+3'], B3 = ['≤−2', '−1', '0', '+1', '≥+2'];
const ROLE = { W: '상위권 승자', L: '상위권 패자', U: '우리', X: '우리 상대' };
// contact accumulator a = [n, drops, own20, opp20, net20, own10, opp10, Lm, Lv]
const cRow = a => [f0(a[0]), pc(a[5] / a[1]), pc(a[2] / a[1]), pc(a[3] / a[1]), sg(a[4] / a[0])];
const CH = ['n', '10R 우리 몫', '20R 우리 몫', '20R 상대 몫', 'net20'];
function tC(obj, keyOf, labels, head0) { return tbl([head0, ...CH], labels.map(b => { const a = obj[keyOf(b)]; return a ? [b, ...cRow(a)] : null; }).filter(Boolean)); }
// side-by-side contact table: rows = buckets, groups = roles
function tCroles(obj, keyOf, labels, roles, head0) {
  const head = [head0]; for (const r of roles) head.push(`${ROLE[r]} n`, `${ROLE[r]} 20R 우리/상대`, `${ROLE[r]} net20`);
  return tbl(head, labels.map(b => { const row = [b]; let any = false; for (const r of roles) { const a = obj[keyOf(r, b)]; if (a) any = true; row.push(a ? f0(a[0]) : '–', a ? `${pc(a[2] / a[1])} / ${pc(a[3] / a[1])}` : '–', a ? sg(a[4] / a[0]) : '–'); } return any ? row : null; }).filter(Boolean));
}
// opportunity accumulator o = [n, taken1, takenAny, died10, rammed1]
function tOroles(obj, keyOf, labels, roles, head0) {
  const head = [head0]; for (const r of roles) head.push(`${ROLE[r]} n`, `${ROLE[r]} 박음`, `${ROLE[r]} 10R 사망`);
  return tbl(head, labels.map(b => { const row = [b]; let any = false; for (const r of roles) { const a = obj[keyOf(r, b)]; if (a) any = true; row.push(a ? f0(a[0]) : '–', a ? pc(a[1] / a[0]) : '–', a ? pc(a[3] / a[0]) : '–'); } return any ? row : null; }).filter(Boolean));
}
// B3 payoff accumulator = [n, drops, own20, opp20, net20, Lv>=Lm]
function tBroles(obj, keyOf, labels, roles, head0) {
  const head = [head0]; for (const r of roles) head.push(`${ROLE[r]} n`, `${ROLE[r]} 20R 우리/상대`, `${ROLE[r]} net20`);
  return tbl(head, labels.map(b => { const row = [b]; let any = false; for (const r of roles) { const a = obj[keyOf(r, b)]; if (a) any = true; row.push(a ? f0(a[0]) : '–', a ? `${pc(a[2] / a[1])} / ${pc(a[3] / a[1])}` : '–', a ? sg(a[4] / a[0]) : '–'); } return any ? row : null; }).filter(Boolean));
}
// pooled helpers over keys
const pool = (obj, pred) => { let r = null; for (const [k, a] of Object.entries(obj)) if (pred(k)) r = r ? sum(r, a) : a.slice(); return r || Z(12); };
const setsOf = pred => Object.keys(A.nSet).filter(pred);
const ours = s => s.startsWith('U|') || s.startsWith('X|');
// ---- value helpers
const own20 = a => a[2] / a[1], opp20 = a => a[3] / a[1], net20 = a => a[4] / a[0], own10 = a => a[5] / a[1], opp10 = a => a[6] / a[1];
const take = o => o[1] / o[0], died10 = o => o[3] / o[0], rammed1 = o => o[4] / o[0];
const C8 = k => get(A.C8, k), C3 = k => get(A.C3, k), CD = k => get(A.Cdef, k), CX = k => get(A.C8x3, k), CL = k => get(A.Clen, k), CK = k => get(A.Cking, k);
const O8 = k => get(A.O8, k), O3 = k => get(A.O3, k), OB = k => get(A.Ob3, k), BP3 = k => get(A.B3p3, k), BP8 = k => get(A.B3p8, k), BPX = k => get(A.B3pX, k);
const nC = (obj, pre) => Object.entries(obj).filter(([k]) => k.startsWith(pre)).reduce((q, [, a]) => q + a[0], 0);
const poolC = (obj, pre, labels) => labels.reduce((r, b) => sum(r, get(obj, pre + b)), Z(9));
const topGames = kind => MAPS.filter(m => kind === 'all' || (kind === 'elim') === ['Default', 'Devil', 'Prisoners Dilemma', 'Queen Of Spades', 'Trophy'].includes(m)).reduce((q, m) => q + ((A.split['W|' + m] || {}).n || 0), 0);
const setList = () => Object.entries(A.nSet).map(([s, n]) => `${s.replace('-online', '')} ${n}`).join(', ');
// ---- E1: split curve per 50 rounds for a role|map
function tE1(roles) {
  const head = ['집단 | 지도', '판', 'r0–49', 'r50–99', 'r100–149', 'r150–199', 'r200–249', 'r250–299', 'r300–349', 'r350–399', 'r400–449', 'r450–499', '최고의 25% 이상인 마지막 구간', 'r380–499 ÷ r300–379 (구간당)'];
  const rows = [];
  for (const m of MAPS) for (const rl of roles) {
    const a = A.split[rl + '|' + m]; if (!a) continue;
    const s = []; for (let q = 0; q < 10; q++) { let v = 0; for (let b = q * 5; b < q * 5 + 5; b++) v += a.sp[b]; s.push(f1(v / a.n)); }
    const peak = Math.max(...a.sp.map(v => v / a.n)); let last = -1; for (let b = 0; b < 50; b++) if (a.sp[b] / a.n >= 0.25 * peak) last = b;
    let pre = 0, post = 0; for (let b = 30; b < 38; b++) pre += a.sp[b]; for (let b = 38; b < 50; b++) post += a.sp[b];
    rows.push([`${ROLE[rl]} | ${MAPK[m]}`, f0(a.n), ...s, 'r' + (last * 10), pre ? f2(post / pre * 8 / 12) : '–']);
  }
  return tbl(head, rows);
}
function e1pooled(kind, rl) { const sp = Z(50); let n = 0; for (const m of MAPS) { const isE = ['Default', 'Devil', 'Prisoners Dilemma', 'Queen Of Spades', 'Trophy'].includes(m); if ((kind === 'elim') !== isE) continue; const a = A.split[rl + '|' + m]; if (!a) continue; n += a.n; for (let b = 0; b < 50; b++) sp[b] += a.sp[b]; } return sp.map(v => v / Math.max(1, n)); }
function e1ratio(kind, rl) { const sp = e1pooled(kind, rl); let pre = 0, post = 0; for (let b = 30; b < 38; b++) pre += sp[b]; for (let b = 38; b < 50; b++) post += sp[b]; return post / pre * 8 / 12; }
function e1bins(kind, rl, from, to) { const sp = e1pooled(kind, rl); return sp.slice(from / 10, to / 10).map(v => f1(v)).join(' · '); }
// ---- E2
function tE2track() { return tbl(['지도', 'r50 상관 (판)', 'r100 상관', 'r200 상관'], MAPS.map(m => [MAPK[m], ...[5, 10, 20].map(i => { const a = A.track[m + '|' + i]; if (!a) return '–'; const n = a[0], mx = a[1] / n, my = a[2] / n; const cov = a[3] / n - mx * my, vx = a[4] / n - mx * mx, vy = a[5] / n - my * my; return f2(cov / Math.sqrt(vx * vy)) + (i === 5 ? ` (${f0(n)})` : ''); })])); }
function tE2resp() { const DB = ['≤−5', '−4..−2', '−1..+1', '+2..+4', '≥+5']; return tbl(['집단', '지도형', '우리 − 상대 수(구간 시작)', '10라운드 구간', '초과 분열/구간', '분열/구간'], ['W', 'L'].flatMap(rl => ['r500', 'elim'].flatMap(kind => DB.map(db => { const a = D.e2within[rl + '|' + kind + '|' + db]; return a ? [ROLE[rl], kind === 'r500' ? '500형' : '전멸형', db, f0(a[0]), sg(a[1] / a[0]), f1(a[2] / a[0])] : null; }))).filter(Boolean)); }
const e2corr = (m, i) => { const a = A.track[m + '|' + i]; if (!a) return NaN; const n = a[0], mx = a[1] / n, my = a[2] / n; return (a[3] / n - mx * my) / Math.sqrt((a[4] / n - mx * mx) * (a[5] / n - my * my)); };
const e2corrList = (i, pred) => MAPS.filter(pred).map(m => `${MAPK[m]} ${sg(e2corr(m, i))}`).join(', ');
const e2ex = (rl, kind, db) => { const a = D.e2within[rl + '|' + kind + '|' + db]; return a ? a[1] / a[0] : NaN; };
// ---- E3
function tE3() {
  const rows = D.e3rows.map(x => { const tgt = Math.max(8, Math.min(40, Math.floor(x.area / 45))); const o5 = D.e3ours['cand-stack5-online|' + x.ly] || {}, o6 = D.e3ours['cand-stack6-online|' + x.ly] || {};
    const [m, l] = x.ly.split('/'); return [`${MAPK[m] || m} ${l}`, f0(A.layout[x.ly].n), f0(x.area), f0(x.sp), f0(x.fo), f2(x.flow), f0(x.u50), f0(x.u100), f0(x.u200), f0(tgt), o5.n ? `${f0(o5.u50)} / ${f0(o5.u100)} / ${f0(o5.u200)}` : '–', o6.n ? `${f0(o6.u50)} / ${f0(o6.u100)} / ${f0(o6.u200)}` : '–']; });
  return tbl(['지도 판본', '승자 판', 'W×H', '생성 칸', '샘 칸', '실제 자연 생성/라운드', '승자 r50', '승자 r100', '승자 r200', 'csplit 목표', 'stack5 r50/100/200', 'stack6 r50/100/200'], rows);
}
function tE3corr() { const P = { area: '넓이 W×H', sp: '생성 칸 수', fo: '샘 칸 수', cap: '생성 용량(Σ1/평균 간격)', flow: '실제 자연 생성/라운드' }; return tbl(['설명 변수', 'r50 R²', 'r100 R²', 'r200 R²'], Object.entries(P).map(([k, nm]) => [nm, ...['u50', 'u100', 'u200'].map(y => { const r = D.e3corr[y][k]; return ok(r) ? `${f2(r * r)} (r ${f2(r)})` : '–'; })])); }
const e3r2 = (y, p) => D.e3corr[y][p] * D.e3corr[y][p];
// ---- E5 / E6
function tE5() { const keys = ['W|r500', 'L|r500', 'W|elim', 'L|elim']; const rows = keys.map(k => { const a = A.nat[k]; if (!a) return null; const n = a[0], s = a[1] + a[2] + a[3], s5 = a[4] + a[5] + a[6]; const [rl, kind] = k.split('|'); return [`${ROLE[rl]} ${kind === 'r500' ? '500형' : '전멸형'}`, f0(n), f1(a[1] / n), f1(a[2] / n), f1(a[3] / n), pc(a[3] / s), pc(a[6] / s5)]; }).filter(Boolean);
  for (const kind of ['r500', 'elim']) for (const grp of [['stack1–4', s => /stack[1-4]/.test(s)], ['stack5–6', s => /stack[56]/.test(s)], ['merge2 r1–r3', s => /merge2/.test(s)], ['px 계열', s => /px/.test(s)], ['그 밖(swarm8·avoid6·portal1·baseline)', s => /swarm8|avoid6|portal1|baseline/.test(s)]]) {
    const a = pool(A.nat, k => { const p = k.split('|'); return p[0] === 'U' && p[2] === kind && grp[1](p[1]); }); if (!a[0]) continue; const n = a[0], s = a[1] + a[2] + a[3], s5 = a[4] + a[5] + a[6];
    rows.push([`우리 ${grp[0]} ${kind === 'r500' ? '500형' : '전멸형'}`, f0(n), f1(a[1] / n), f1(a[2] / n), f1(a[3] / n), pc(a[3] / s), pc(a[6] / s5)]); }
  return tbl(['집단', '팀·경기', '자기 영토', '중립', '상대 영토', '상대 영토 몫', 'r0–49 상대 영토 몫'], rows);
}
function tE6() { const rows = []; const put = (label, a) => { if (!a || !a[0]) return; const n = a[0]; rows.push([label, f0(n), `${f1(a[3] / n)} / ${f1(a[6] / n)} / ${f1(a[9] / n)}`, `${f1(a[1] / n)} / ${f1(a[4] / n)} / ${f1(a[7] / n)}`, f1(a[10] / n), f1(a[11] / n), f1(a[13] / n), f1(a[15] / n)]); };
  for (const k of ['W|r500', 'L|r500', 'W|elim', 'L|elim']) { const [rl, kind] = k.split('|'); put(`${ROLE[rl]} ${kind === 'r500' ? '500형' : '전멸형'}`, A.occ[k]); }
  for (const kind of ['r500', 'elim']) for (const grp of [['stack1–6', s => /stack/.test(s)], ['merge2', s => /merge2/.test(s)], ['px 계열', s => /px/.test(s)]]) put(`우리 ${grp[0]} ${kind === 'r500' ? '500형' : '전멸형'}`, pool(A.occ, k => { const p = k.split('|'); return p[0] === 'U' && p[2] === kind && grp[1](p[1]); }));
  return tbl(['집단', '팀·경기', '상대 영토 생성 용량 아래 몸 r0–99 / 100–249 / 250+', '자기 영토 같은 값', '거울로 잡힌 막힘: 우리 몸이 상대 영토에서', '우리 몸이 자기 영토에서', '진주가 상대 영토 생성을 막음', '상대 영토 자연 생성'], rows);
}
// ---- E7
const KX = k => get(A.Kx, k, 9);
function tE7(kind, roles) { const rows = []; for (const rl of roles) for (const L of ['2', '3-4', '5-7', '8-14', '15+']) { const a = A.Kx[`${kind}|${rl}|*|${L}|*|*`]; if (!a) continue; rows.push([ROLE[rl], L, f0(a[0]), f1(a[1] / a[0]), pc(a[3] / a[8]), pc(a[4] / a[8]), sg1(a[5] / a[0]), sg1(a[6] / a[0]), pc(a[7] / a[0])]); } return tbl(['공격한 팀', '공격자 길이', '왕 죽음', '왕 길이', '왕 진주: 공격 팀 20R', '왕 팀 20R', '죽기 전 왕 차(왕 팀 기준)', '20R 뒤 왕 차', '공격 팀이 판을 이김(상위권은 정의상 승자 100%·패자 0%)'], rows); }
function tE7grp(kind, roles) { const rows = []; for (const rl of roles) for (const ph of ['r<250', 'r250-399', 'r400+']) for (const g of ['solo', 'grp']) { const a = A.Kx[`${kind}|${rl}|*|*|${ph}|${g}`]; if (!a) continue; rows.push([ROLE[rl], ph, g === 'grp' ? '무리(3칸 안 동료 ≥1)' : '혼자', f0(a[0]), f1(a[2] / a[0]), pc(a[3] / a[8]), sg1(a[5] / a[0]), sg1(a[6] / a[0]), pc(a[7] / a[0])]); } return tbl(['공격한 팀', '시기', '무리', '왕 죽음', '공격자 길이', '왕 진주: 공격 팀 20R', '죽기 전 왕 차', '20R 뒤 왕 차', '공격 팀이 판을 이김(상위권은 정의상 승자 100%·패자 0%)'], rows); }
function tE7how(kind) { const rows = []; for (const rl of ['W', 'L']) for (const how of ['rammed', 'rammer', 'body', 'trap', 'sac', 'other']) { const a = A.K[`${kind}|${rl}|${how}`]; if (!a) continue; rows.push([ROLE[rl], { rammed: '적이 박음', rammer: '왕이 적 머리로', body: '적 몸에 박음(틈 있음)', trap: '갇힘', sac: '희생', other: '그 밖' }[how], f0(a[0]), f1(a[1] / a[0]), f1(a[2] / a[0]), pc(a[3] / a[8]), pc(a[4] / a[8]), pc(a[7] / a[0])]); } return tbl(['왕의 팀', '어떻게', '건수', '왕 길이', '상대 길이', '진주: 상대 20R', '진주: 자기 팀 20R', '왕의 팀 짐(정의상)'], rows); }
// ---- E8
function tE8S(kind) { const rows = []; for (const rl of ['W', 'L']) for (const b of ['≤1', '2-3', '4-8', '9-16', '17+']) { const a = A.S[`${rl}|${kind}|${b}`]; if (!a) continue; rows.push([ROLE[rl], b, f0(a[0]), f1(a[1] / a[0]), pc(a[2] / a[7]), pc(a[4] / a[7]), pc(a[3] / a[7]), f0(a[5] / a[0])]); } return tbl(['집단', '죽을 때 왕까지 경로 거리', '희생', '길이', '진주: 자기 팀 20R', '그중 그때 왕', '상대 20R', '평균 라운드'], rows); }
const e8share = (rl, kind, pred) => { let n = 0, t = 0; for (const b of ['≤1', '2-3', '4-8', '9-16', '17+']) { const a = A.S[`${rl}|${kind}|${b}`]; if (!a) continue; t += a[0]; if (pred(b)) n += a[0]; } return n / t; };
function tE8near() { const rows = []; for (const rl of ['W', 'L']) for (const cp of [300, 350]) { const x = D[`e8near${rl}${cp}`]; if (!x) continue; rows.push([ROLE[rl], 'r' + cp, f0(x.n), sg(x.slope), ...['≤3', '4-8', '9-16', '17-32', '33+'].map(b => x.by[b] ? `r${f0(x.by[b][1] / x.by[b][0])} (${f0(x.by[b][0])})` : '–')]); } return tbl(['집단', '거리를 잰 때', '왕 곁(≤3) 희생', '기울기(라운드/칸)', '≤3', '4–8', '9–16', '17–32', '33+'], rows); }
function tE8byR(rl) { const x = D['e8byR' + rl]; return tbl(['죽은 라운드', ...Object.keys(x).sort((a, b) => +a - +b).map(b => 'r' + b)], [['희생', ...Object.keys(x).sort((a, b) => +a - +b).map(b => f0(x[b][0]))], ['왕까지 평균 거리', ...Object.keys(x).sort((a, b) => +a - +b).map(b => f1(x[b][1] / x[b][0]))], ['왕 3칸 안', ...Object.keys(x).sort((a, b) => +a - +b).map(b => pc(x[b][2] / x[b][0]))]]); }
function tE8ours() { const TAG = { 0: '표식 없음', 10: 'conv', 11: 'feed', 12: 'k2' }; const agg = {}; for (const [k, a] of Object.entries(D.e8ours)) { const [set, tg] = k.split('|'); const t = +tg.slice(3); const grp = /stack[1-6]/.test(set) ? 'stack1–6' : /merge2/.test(set) ? 'merge2' : 'px·그 밖'; const kk = grp + '|' + (TAG[t] || ('tag' + t)); agg[kk] = agg[kk] ? sum(agg[kk], a) : a.slice(); } return tbl(['우리 봇', '표식', '희생', '평균 라운드', '왕까지 거리', '길이', '진주: 우리 20R(개/건)', '그중 왕'], Object.entries(agg).sort().map(([k, a]) => { const [g, t] = k.split('|'); return [g, t, f0(a[0]), f0(a[1] / a[0]), f1(a[2] / a[0]), f1(a[3] / a[0]), f2(a[4] / a[0]), f2(a[6] / a[0])]; })); }
// ---- E9
function tE9() { const rows = []; const put = (label, a) => { if (!a || !a[0]) return; const n = a[0]; rows.push([label, f0(n), f1(a[1] / n), f2(a[3] / n), f2(a[4] / n), f2(a[5] / n), f2(a[8] / n), (100 * a[4] / a[1]).toFixed(2) + '%']); };
  for (const k of ['W|r500', 'L|r500', 'W|elim', 'L|elim']) { const [rl, kind] = k.split('|'); put(`${ROLE[rl]} ${kind === 'r500' ? '500형' : '전멸형'}`, A.CHdef[k]); }
  for (const kind of ['r500', 'elim']) put(`우리(18세트) ${kind === 'r500' ? '500형' : '전멸형'}`, pool(A.CHdef, k => { const p = k.split('|'); return p[0] === 'U' && p[2] === kind; }));
  return tbl(['쫓기는 팀', '팀·경기', '쫓김(3턴 이상)', '쫓던 적이 쫓기던 드래곤 몸에 죽음', '제3 아군 몸에 죽음(구조)', '쫓기던 드래곤과 박치기', '쫓기던 드래곤이 죽음', '구조 ÷ 쫓김'], rows); }
function tE9bk() { const rows = []; for (const k of ['W|r500', 'L|r500', 'W|elim', 'L|elim']) { const [rl, kind] = k.split('|'); let n = 0; for (const [kk, a] of Object.entries(A.BK)) if (kk.startsWith(k + '|')) n += a[0]; const ch = A.CH[k] ? null : null; void ch; const d = A.CHdef[k]; const g = d ? d[0] : 1; rows.push([`${ROLE[rl]} ${kind === 'r500' ? '500형' : '전멸형'}`, f2(n / g), d ? f2(d[4] / g) : '–', d ? pc(d[4] / Math.max(1, n)) : '–']); } return tbl(['몸으로 죽인 팀', '몸 처치/판', '그중 쫓김 구조/판', '구조 몫'], rows); }
// ---- E4 extra tables
function tCdef(roles) { const DEF = { v3: '시야(박은 머리 체비쇼프 3)', m3: '접촉 칸 맨해튼 3', m8: '접촉 칸 맨해튼 8', c8: '접촉 칸 체비쇼프 8', L8: '맨해튼 8 안 길이 합' }; const rows = [];
  for (const rl of roles) for (const [d, nm] of Object.entries(DEF)) { const m = CD(rl + '|' + d + '|−'), z = CD(rl + '|' + d + '|0'), p = CD(rl + '|' + d + '|+'); rows.push([ROLE[rl], nm, `${f0(m[0])} / ${f0(z[0])} / ${f0(p[0])}`, `${pc(own20(m))} / ${pc(own20(z))} / ${pc(own20(p))}`, `${sg(net20(m))} / ${sg(net20(z))} / ${sg(net20(p))}`, sg1(100 * (own20(p) - own20(m))) + '%p']); }
  return tbl(['집단', '국지 수 정의', 'n (열세 / 같음 /우세)', '20R 우리 몫', 'net20', '우세 − 열세'], rows); }
function tCX(rl) { const rows = []; for (const v of ['v−', 'v0', 'v+']) for (const m of ['m−', 'm0', 'm+']) { const a = CX(rl + '|' + v + '|' + m); if (!a[0]) continue; rows.push([{ 'v−': '열세', v0: '같음', 'v+': '우세' }[v], { 'm−': '열세', m0: '같음', 'm+': '우세' }[m], f0(a[0]), pc(own20(a)), pc(opp20(a)), sg(net20(a))]); } return tbl(['시야 d3', '반경 8 d8', 'n', '20R 우리 몫', '20R 상대 몫', 'net20'], rows); }
function tClen(roles) { const rows = []; for (const rl of roles) for (const rel of ['short→long', 'equal', 'long→short']) { const r = [ROLE[rl], { 'short→long': '짧은 쪽이 박음', equal: '같은 길이', 'long→short': '긴 쪽이 박음' }[rel]]; for (const sgn of ['−', '0', '+']) { const a = CL(rl + '|' + rel + '|' + sgn); r.push(a[0] ? `${pc(own20(a))} · ${sg(net20(a))} (${f0(a[0])})` : '–'); } rows.push(r); } return tbl(['집단', '길이 관계', 'd8 열세: 우리 몫 · net20 (n)', 'd8 같음', 'd8 우세'], rows); }
function tCking(roles) { const NM = { 'moverKing≥8': '박은 쪽이 자기 팀 최장(≥8)', 'victimKing≥8': '당한 쪽이 상대 팀 최장(≥8)', 'king<8': '최장이지만 <8(초반)', none: '최장 아님' }; const rows = []; for (const rl of roles) for (const kk of Object.keys(NM)) { const r = [ROLE[rl], NM[kk]]; for (const sgn of ['−', '0', '+']) { const a = CK(rl + '|' + kk + '|' + sgn); r.push(a[0] ? `${pc(own20(a))} · ${sg(net20(a))} (${f0(a[0])})` : '–'); } rows.push(r); } return tbl(['집단', '최장 드래곤', 'd8 열세: 우리 몫 · net20 (n)', 'd8 같음', 'd8 우세'], rows); }
function tBX(roles) { const rows = []; for (const rl of roles) for (const v of ['v≤−1', 'v0', 'v≥+1']) for (const m of ['m≤−1', 'm0', 'm≥+1']) { const a = BPX(rl + '|' + v + '|' + m); if (!a[0]) continue; rows.push([ROLE[rl], v.slice(1), m.slice(1), f0(a[0]), pc(own20(a)), pc(opp20(a)), sg(net20(a))]); } return tbl(['집단', '시야 d3', '반경 8 d8', 'n', '20R 우리 몫', '20R 상대 몫', 'net20'], rows); }
function tB3map(roles) { const rows = []; for (const rl of roles) for (const m of MAPS) { const r = [ROLE[rl], MAPK[m]]; let any = false; for (const sgn of ['−', '0', '+']) { const o = A.Ob3map[rl + '|' + m + '|' + sgn], b = A.B3pmap[rl + '|' + m + '|' + sgn]; if (o) any = true; r.push(o ? `${pc(take(o))} (${f0(o[0])})` : '–', b ? `${pc(own20(b))} · ${sg(net20(b))}` : '–'); } if (any) rows.push(r); } return tbl(['집단', '지도', 'd3 열세: 박는 비율 (기회)', '열세: 우리 몫 · net20', 'd3 같음: 박는 비율', '같음: 몫 · net20', 'd3 우세: 박는 비율', '우세: 몫 · net20'], rows); }
function tB3ph(roles) { const rows = []; for (const rl of roles) for (const ph of ['r0-99', 'r100-249', 'r250-349', 'r350+']) { const r = [ROLE[rl], ph]; for (const sgn of ['−', '0', '+']) { const o = A.Ob3ph[rl + '|' + ph + '|' + sgn]; r.push(o ? `${pc(take(o))} (${f0(o[0])})` : '–'); } rows.push(r); } return tbl(['집단', '시기', 'd3 열세: 박는 비율 (기회)', 'd3 같음', 'd3 우세'], rows); }
const ram4 = () => A.oursRam4;
const ram4sum = pred => { const xs = A.oursRam4.filter(pred); const dr = xs.reduce((q, x) => q + x.drops, 0); return { n: xs.length, own: xs.reduce((q, x) => q + x.own20, 0), opp: xs.reduce((q, x) => q + x.opp20, 0), drops: dr, net: xs.reduce((q, x) => q + x.net20, 0) }; };
function tRam4() { return tbl(['기보', '지도', '라운드', '길이(우리/적)', 'd3', 'd8', '진주 20R 우리 / 상대 / 전체'], A.oursRam4.map(x => [x.key.replace('cand-stack1-online:', 'stack1:'), MAPK[x.map] || x.map, 'r' + x.r, `${x.Lm} / ${x.Lv}`, sg1(x.d3).replace('.0', ''), sg1(x.d8).replace('.0', ''), `${x.own20} / ${x.opp20} / ${x.drops}`])); }
// opportunities and contacts of our sets grouped
const oursO = (grp, rl, lcl) => pool(A.oursO, k => { const p = k.split('|'); return grp(p[0]) && p[1] === rl && p[2] === lcl; });
const oursC = (grp, rl) => pool(A.oursC, k => { const p = k.split('|'); return grp(p[0]) && p[1] === rl; });
function tUtab() { return tbl(['지도 판본(`mapIs` 이름/판본)', '지금 csplit 목표(넓이/45)', '제안 목표 r<50 (승자 r50 중앙값)', '제안 목표 r50–249 (승자 r100 중앙값)', 'stack6 r100 실제'], D.e3rows.map(x => { const [m, l] = x.ly.split('/'); const o6 = D.e3ours['cand-stack6-online|' + x.ly] || {}; return [`${m} / ${l}`, f0(Math.max(8, Math.min(40, Math.floor(x.area / 45)))), f0(x.u50), f0(x.u100), o6.n ? f0(o6.u100) : '–']; })); }
const floor5 = v => Math.floor(v * 20) / 20;
const kills = (kind, rl) => ['2', '3-4', '5-7', '8-14', '15+'].reduce((q, L) => q + get(A.Kx, `${kind}|${rl}|*|${L}|*|*`, 9)[0], 0);
const teamGames = (rl, kind) => rl === 'U' || rl === 'X' ? pool(A.CHdef, k => k.startsWith('U|') && k.endsWith('|' + kind))[0] : A.CHdef[rl + '|' + kind][0];
// E1: the last 10-round bin with >= 25% of the peak split rate, per role|map
function e1last(rl, m) { const a = A.split[rl + '|' + m]; if (!a) return NaN; const peak = Math.max(...a.sp.map(v => v / a.n)); let last = -1; for (let b = 0; b < 50; b++) if (a.sp[b] / a.n >= 0.25 * peak) last = b; return last * 10; }
const e1lastList = rl => MAPS.filter(m => A.split[rl + '|' + m]).map(m => `${MAPK[m]} r${e1last(rl, m)}`).join(', ');
// E3: layouts where the winners' r100 median is far above / below the area target
const e3tgt = x => Math.max(8, Math.min(40, Math.floor(x.area / 45)));
const e3name = x => { const [m, l] = x.ly.split('/'); return `${MAPK[m] || m} ${l}`; };
const e3raise = () => D.e3rows.filter(x => x.u100 >= 1.5 * e3tgt(x));
const e3lower = () => D.e3rows.filter(x => x.u100 <= e3tgt(x) / 1.5);
const e3list = xs => xs.map(x => `${e3name(x)}(목표 ${e3tgt(x)}, 승자 ${f0(x.u100)})`).join(', ');
const e3oursBelowHalf = set => { const xs = D.e3rows.filter(x => (D.e3ours[set + '|' + x.ly] || {}).n); return [xs.filter(x => D.e3ours[set + '|' + x.ly].u100 < 0.5 * x.u100).length, xs.length]; };
const e3oursBelowTgt = set => { const xs = D.e3rows.filter(x => (D.e3ours[set + '|' + x.ly] || {}).n); return [xs.filter(x => D.e3ours[set + '|' + x.ly].u100 < e3tgt(x)).length, xs.length]; };
// stage 2 classes from cases.txt: "## <class>: class size N; drops eaten <=20R own X% / enemy Y%"
const CASES = (() => { const f = path.join(__dirname, 'cases.txt'); const o = {}; if (!fs.existsSync(f)) return o; let cur = null;
  for (const l of fs.readFileSync(f, 'utf8').split('\n')) { const m = /^## (.+?): class size (\d+)(?:; drops eaten <=20R own (\d+)% \/ enemy (\d+)%)?/.exec(l); if (m) { cur = o[m[1]] = { n: +m[2], own: m[3] ? +m[3] : null, opp: m[4] ? +m[4] : null, picks: [] }; continue; }
    const p = /^\s+node exp\/econ-principles\/film\.js (\S+) (\d+) (\S+)\s+# (.*)$/.exec(l); if (p && cur) cur.picks.push({ key: p[1], r: +p[2], id: p[3], note: p[4] }); }
  return o; })();
const cc = name => CASES[name] || { n: NaN, own: null, opp: null, picks: [] };
const ccLine = name => { const c = cc(name); return `${f0(c.n)}건${c.own !== null ? `, 20R 진주 우리 ${c.own}% / 상대 ${c.opp}%` : ''}`; };
const oB3 = (set, sgn) => get(A.oursB3, set + '|U|' + sgn, 5);
const perGame = (set, sgn) => oB3(set, sgn)[0] / (A.nSet[set] || NaN);
const sacPerGame = (grp, kind) => { if (grp === 'W' || grp === 'L') { let n = 0; for (const [k, a] of Object.entries(A.S)) if (k.startsWith(grp + '|' + kind + '|')) n += a[0]; return n / teamGames(grp, kind); }
  let n = 0, g = 0; for (const [k, a] of Object.entries(A.S)) { const p = k.split('|'); if (p[0] === 'U' && grp(p[1]) && p[2] === kind) n += a[0]; }
  for (const [k, a] of Object.entries(A.nat)) { const p = k.split('|'); if (p[0] === 'U' && grp(p[1]) && p[2] === kind) g += a[0]; } return n / g; };
function tOteam(minN) { const teams = [...new Set(Object.keys(A.Oteam).map(k => k.split('|')[0]))]; const rows = [];
  for (const tm of teams) { const m = get(A.Oteam, tm + '|−', 5), z = get(A.Oteam, tm + '|0', 5), p = get(A.Oteam, tm + '|+', 5); const n = m[0] + z[0] + p[0]; if (n < minN) continue; rows.push([tm, f0(n), pc(take(m)), pc(take(z)), pc(take(p)), pc(p[0] / n)]); }
  rows.sort((a, b) => +b[1].replace(/,/g, '') - +a[1].replace(/,/g, ''));
  return tbl(['팀', 'B3 기회', 'd3 열세 박음', 'd3 같음', 'd3 우세', '기회 중 d3 우세 몫'], rows); }
const teamRule = minN => { const teams = [...new Set(Object.keys(A.Oteam).map(k => k.split('|')[0]))]; let n = 0, ok = 0; for (const tm of teams) { const m = get(A.Oteam, tm + '|−', 5), z = get(A.Oteam, tm + '|0', 5), p = get(A.Oteam, tm + '|+', 5); if (m[0] + z[0] + p[0] < minN) continue; n++; if (take(p) > take(m) + 0.2) ok++; } return [ok, n]; };
const AP = (() => { const f = path.join(__dirname, 'approach-summary.json'); return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : null; })();
function tAP() { if (!AP) return '(접근 분석 작성 중)'; const rows = []; for (const k of ['W|r500', 'L|r500', 'U|r500', 'X|r500']) { const a = AP[k]; if (!a) continue; const [rl, kind] = k.split('|'); rows.push([`${ROLE[rl]} ${kind === 'r500' ? '500형' : '전멸형'}`, f0(a.n), f1(a.lenA), f1(a.lenK), pc(a.moved), a.medD.map(v => v === null ? '–' : v).join(' / '), pc(a.far10), pc(a.near5), a.medB.map(v => v === null ? '–' : v).join(' / '), pc(a.baseFar10), pc(a.young)]); }
  return tbl(['공격한 팀', '왕 죽음', '공격자 길이', '왕 길이', '공격자가 움직여 박음', '공격자–왕 거리 중앙값 r−1/−3/−5/−10/−15', '10라운드 전 ≥8칸(멀리서 옴)', '5라운드 전 ≤3칸(이미 곁)', '다른 공격 팀 머리 중 가장 가까운 것의 거리 중앙값', '그 머리가 10라운드 전 ≥8칸', '공격자가 15라운드 안에 태어남'], rows); }
function tBally(roles) { const rows = []; for (const rl of roles) for (const sgn of ['−', '0', '+']) { const r = [ROLE[rl], { '−': '열세', '0': '같음', '+': '우세' }[sgn]]; for (const ab of ['0', '1-2', '3-5', '6+']) { const a = get(A.B3pAlly, rl + '|' + sgn + '|' + ab, 6); r.push(a[0] ? `${pc(own20(a))} · ${sg(net20(a))} (${f0(a[0])})` : '–'); } rows.push(r); } return tbl(['집단', '시야 d3', '반경 8 아군 머리 0: 우리 몫 · net20 (n)', '1–2', '3–5', '6+'], rows); }
function render(tpl) {
  return tpl.replace(/\{\{([\s\S]+?)\}\}/g, (_, expr) => {
    try { const v = eval(expr); return v === undefined ? '' : String(v); } catch (e) { return `⟦ERROR ${e.message} in ${expr.trim().slice(0, 60)}⟧`; }
  });
}
const V = (() => { const f = path.join(__dirname, 'doc-verdicts.json'); return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : {}; })();
const film = name => { const f = path.join(__dirname, 'doc-films-' + name + '.md'); return fs.existsSync(f) ? render(fs.readFileSync(f, 'utf8')).trim() : '(선별 기보 읽기 작성 중)'; };
const BFILMS = undefined, CFILMS = undefined; void BFILMS; void CFILMS;
const part = name => { const f = path.join(__dirname, 'doc-' + name + '.md'); return fs.existsSync(f) ? render(fs.readFileSync(f, 'utf8')).trim() : '(작성 중)'; };
const tpl = fs.readFileSync(path.join(__dirname, 'doc-template.md'), 'utf8');
// Korean copula after a number: Sino-Korean readings of 0, 1, 3, 6, 7, 8 end in a consonant ("이다"), 2, 4, 5, 9 in a vowel ("다")
const md = render(tpl).replace(/([013678])다(?=[.,\s)|])/g, '$1이다').replace(/([013678])다$/gm, '$1이다').replace(/([036])로(?=[ ,.)])/g, '$1으로')
  .replace(/([013678])가(?=[ ,.)])/g, '$1이').replace(/([013678])는(?=[ ,.)])/g, '$1은').replace(/([013678])를(?=[ ,.)])/g, '$1을').replace(/([013678])와(?=[ ,.)])/g, '$1과');
const outFile = path.resolve(ROOT, opt('out', 'research/observations/economy-principles.md'));
fs.writeFileSync(outFile, md);
const errs = (md.match(/⟦ERROR[^⟧]*⟧/g) || []);
console.log(`wrote ${path.relative(ROOT, outFile)} (${md.length} chars), errors ${errs.length}`); for (const e of errs.slice(0, 20)) console.log('  ' + e);
