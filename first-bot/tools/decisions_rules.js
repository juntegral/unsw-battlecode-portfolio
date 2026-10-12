#!/usr/bin/env node
// Key decision rules learned from top-vs-top play, measured per top team (does the rule hold across teams?) and for
// each of our online groups with a game-clustered bootstrap interval. Reads data/decisions only.
// usage: node tools/decisions_rules.js [--top top-20260929a] [--base <submission id>] [--out data/decisions/rules]
//   Output: <out>.json and <out>.md (Korean table). Rule definitions are in RULES below; the same states as the leaves
//   of tools/decisions_learn.js that carry the largest divergences.
'use strict';
const fs = require('fs'), path = require('path');
const Lb = require('./decisions_lib.js');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const TOPSET = opt('top', 'top-20260929a');
const OUT = path.resolve(Lb.ROOT, opt('out', path.join('data', 'decisions', 'rules')));
const sets = fs.readdirSync(Lb.DEC).filter(s => s !== TOPSET && fs.existsSync(path.join(Lb.DEC, s, 'games.jsonl')) && Lb.readJsonl(path.join(Lb.DEC, s, 'games.jsonl')).some(g => g.ourSide));
let BASE = opt('base', null);
if (BASE === null) { const g = Lb.readJsonl(path.join(Lb.DEC, 'baseline-r1', 'games.jsonl')); BASE = g.length ? String(g[0].ourSubmission) : null; }

const n = (v, C, k) => +v[C[k]];
const SK = new Set(['S', 'W', 'Aq', 'Ax']);
// each rule: state (population) and action; ids refer to the decision types of top-decisions.md
const RULES = [
  { id: 'R1', name: '길이 4 조각이 2+2로 분열', pop: (v, C) => n(v, C, 'L') === 4 && (v[C.act] === 'M' || v[C.act] === 'P'), act: (v, C) => v[C.act] === 'P' },
  { id: 'R2', name: '길이 5–9, 방 ≥6, r≤166에서 분열', pop: (v, C) => n(v, C, 'L') >= 5 && n(v, C, 'L') <= 9 && n(v, C, 'room') >= 6 && n(v, C, 'r') <= 166 && (v[C.act] === 'M' || v[C.act] === 'P'), act: (v, C) => v[C.act] === 'P' },
  { id: 'R3', name: '길이 ≥8 아군이 3칸 안, r≥350, 빈 이웃 있음: 자해', pop: (v, C) => n(v, C, 'free') >= 1 && n(v, C, 'aLg') >= 8 && n(v, C, 'aDg') <= 3 && n(v, C, 'r') >= 350, act: (v, C) => SK.has(v[C.fate]) },
  { id: 'R4', name: '길이 ≤3, 아군 보임, 같거나 긴 적 머리를 이번 턴에 박을 수 있음(적 ≤2): 박음', pop: (v, C) => n(v, C, 'L') <= 3 && n(v, C, 'oppN') >= 1 && n(v, C, 'aN') >= 1 && n(v, C, 'oppL') >= n(v, C, 'L') && n(v, C, 'eN') <= 2 && (v[C.act] === 'M' || v[C.act] === 'P'), act: (v, C) => v[C.ram] === '1' },
  { id: 'R5', name: '길이 ≥6, 안전한 한 걸음과 노출 한 걸음이 함께 있음: 노출 칸에서 끝냄', pop: (v, C) => n(v, C, 'L') >= 6 && n(v, C, 'eNs') >= 1 && v[C.act] === 'M' && v[C.fate] === '' && n(v, C, 'safe1') >= 1 && n(v, C, 'exp1') >= 1, act: (v, C) => v[C.endExp] === '1' },
  { id: 'R6', name: '머리 칸에 포털 변, 4칸 안에 진주 없음, 빈 이웃 ≥2: 포털 통과', pop: (v, C) => v[C.act] === 'M' && n(v, C, 'ptlN') >= 1 && n(v, C, 'pD0') >= 5 && n(v, C, 'free') >= 2, act: (v, C) => n(v, C, 'ptlK') >= 1 },
  { id: 'R7', name: '길이 ≤4, 적 머리 3–8칸(박을 수 없음): 다가감', pop: (v, C) => n(v, C, 'L') <= 4 && n(v, C, 'eN') >= 1 && n(v, C, 'oppN') === 0 && v[C.act] === 'M' && v[C.fate] === '' && n(v, C, 'eD0') >= 3 && n(v, C, 'eD0') <= 8, act: (v, C) => { const a = n(v, C, 'eD0'), b = n(v, C, 'eD1'); return b < a; } },
  { id: 'R8', name: '길이 ≥6, 한 걸음은 모두 노출, 질주 탈출 있음: 질주', pop: (v, C) => n(v, C, 'L') >= 6 && n(v, C, 'eNs') >= 1 && v[C.act] === 'M' && v[C.fate] === '' && n(v, C, 'safe1') === 0 && n(v, C, 'exp1') > 0 && n(v, C, 'safe2') > 0, act: (v, C) => n(v, C, 'k') >= 2 },
];

// per team (top) and per game (our groups): weighted state count and action count
const team = new Map();   // teamName -> rule -> {w, a, games:Set}
const games = [];         // {grp, rule -> [w, a]}
function add(map, key, rid, w, aw, rows) {
  let t = map.get(key); if (!t) { t = {}; map.set(key, t); }
  const e = t[rid] || (t[rid] = { w: 0, a: 0, n: 0 }); e.w += w; e.a += aw; e.n += rows;
}
for (const s of [TOPSET, ...sets]) for (const { g, C, rows } of Lb.gamesOf(s)) {
  const isTop = s === TOPSET;
  if (isTop && (Lb.EXCLUDE_TEAMS.has(g.teamName.A) || Lb.EXCLUDE_TEAMS.has(g.teamName.B))) continue;
  const per = { A: {}, B: {} };
  for (const v of rows) {
    const tm = v[C.tm], w = +v[C.w];
    for (const R of RULES) if (R.pop(v, C)) { const a = R.act(v, C); const e = per[tm][R.id] || (per[tm][R.id] = [0, 0, 0]); e[0] += w; if (a) e[1] += w; e[2]++; }
  }
  for (const tm of ['A', 'B']) {
    let grp;
    if (isTop) grp = 'T';
    else grp = tm === g.ourSide ? (String(g.ourSubmission) === BASE ? 'O' : 'C' + g.ourSubmission) : 'X';
    games.push({ grp, tm: g.teamName[tm], win: g.winner === tm, per: per[tm] });
    if (isTop) for (const R of RULES) { const e = per[tm][R.id]; if (e) add(team, g.teamName[tm], R.id, e[0], e[1], e[2]); }
  }
}
// game-clustered bootstrap of the pooled rate sum(a)/sum(w)
let seed = 7; const rnd = () => { seed = (Math.imul(seed, 1103515245) + 12345) >>> 0; return seed / 4294967296; };
function boot(list, rid, B = 1000) {
  const xs = list.map(x => x.per[rid] || [0, 0, 0]);
  const tw = xs.reduce((s, x) => s + x[0], 0), ta = xs.reduce((s, x) => s + x[1], 0);
  if (!tw) return { p: NaN, lo: NaN, hi: NaN, w: 0, games: list.length };
  const ps = [];
  for (let b = 0; b < B; b++) { let w = 0, a = 0; for (let i = 0; i < xs.length; i++) { const x = xs[Math.floor(rnd() * xs.length)]; w += x[0]; a += x[1]; } if (w) ps.push(a / w); }
  ps.sort((p, q) => p - q);
  return { p: ta / tw, lo: ps[Math.floor(0.025 * ps.length)], hi: ps[Math.floor(0.975 * ps.length)], w: tw, games: list.length };
}
const groups = [...new Set(games.map(x => x.grp))].sort((a, b) => ['T', 'O', 'X'].indexOf(a) - ['T', 'O', 'X'].indexOf(b));
const res = { base: BASE, rules: RULES.map(R => ({ id: R.id, name: R.name })), groups: {}, teams: {} };
for (const gr of groups) {
  const list = games.filter(x => x.grp === gr);
  res.groups[gr] = {};
  for (const R of RULES) res.groups[gr][R.id] = boot(list, R.id);
  if (gr === 'T') { res.groups.TW = {}; res.groups.TL = {}; for (const R of RULES) { res.groups.TW[R.id] = boot(list.filter(x => x.win), R.id); res.groups.TL[R.id] = boot(list.filter(x => !x.win), R.id); } }
}
const tg = {}; for (const x of games) if (x.grp === 'T') tg[x.tm] = (tg[x.tm] || 0) + 1;
for (const [nm, t] of team) if (tg[nm] >= 10) res.teams[nm] = Object.fromEntries(RULES.map(R => [R.id, t[R.id] ? { p: t[R.id].a / t[R.id].w, w: t[R.id].w, n: t[R.id].n } : null]));
fs.writeFileSync(OUT + '.json', JSON.stringify(res, null, 1));

const f = x => Number.isFinite(x) ? (100 * x).toFixed(1) : '–';
const md = ['# 핵심 결정 규칙: 팀별 일관성과 우리 봇 (자동 생성)', '',
  `- 명령: \`node tools/decisions_rules.js\`. 상위끼리 \`${TOPSET}\`(SSS 제외), 우리 기준 제출 ${BASE}. 괄호는 경기 단위 붓스트랩 95% 구간이다.`, ''];
const gname = g => ({ T: '상위끼리', TW: '상위 승자', TL: '상위 패자', O: `우리(${BASE})`, X: '우리 경기의 상위 상대' }[g] || `후보 ${g.slice(1)}`);
const G2 = ['T', 'TW', 'TL', ...groups.filter(g => g !== 'T')];
md.push(Lb.mdTable(['규칙', ...G2.map(gname)], RULES.map(R => [`${R.id} ${R.name}`, ...G2.map(g => { const e = res.groups[g] && res.groups[g][R.id]; return e && e.w ? `${f(e.p)}% [${f(e.lo)}–${f(e.hi)}]` : '–'; })])));
md.push('');
const teams = Object.keys(res.teams).sort((a, b) => tg[b] - tg[a]);
md.push('### 상위 팀별 (10판 이상)');
md.push(Lb.mdTable(['팀', '판', ...RULES.map(R => R.id)], teams.map(nm => [nm, String(tg[nm]), ...RULES.map(R => { const e = res.teams[nm][R.id]; return e && e.n >= 30 ? f(e.p) : '–'; })])));
md.push('');
const spread = RULES.map(R => { const ps = teams.map(nm => res.teams[nm][R.id]).filter(e => e && e.n >= 30).map(e => e.p).sort((a, b) => a - b); return `${R.id} 팀 ${ps.length}개: 최소 ${f(ps[0])}, 중앙 ${f(ps[ps.length >> 1])}, 최대 ${f(ps[ps.length - 1])}`; });
md.push('- 팀별 분포(행 30개 이상인 팀): ' + spread.join('; ') + '.');
fs.writeFileSync(OUT + '.md', md.join('\n') + '\n');
console.log(md.join('\n'));
