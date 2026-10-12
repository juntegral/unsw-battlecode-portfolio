#!/usr/bin/env node
// 온라인 기준점 분석(계획 A단계): 현재 봇(제출 10365 = bot/)이 상위 팀에게 어떻게 지는가.
// usage (저장소 루트에서):
//   node tools/baseline_study.js [--jobs 3] [--out data/online/baseline_study.json] [--reuse] [--games id,id [--write]]
//     --jobs K   리플레이를 읽는 자식 프로세스 수(기본 3, 최대 3: 다른 에이전트가 로컬 경기를 돌린다). 254판에 약 1분.
//     --reuse    출력 JSON에 저장된 경기별 기록을 다시 쓰고 집계만 새로 한다(리플레이를 읽지 않는다, 약 2초)
//     --games    일부 경기만(점검용). 집계 표는 그 경기들로만 만들고, --write가 없으면 출력 JSON을 쓰지 않는다.
// 입력(네트워크 없음):
//   data/online/baseline-r1/   70판: 우리(제출 10365) 대 상위 6팀 + DEV 팀 545, 지도 10개씩
//   data/online/r1-online/     같은 제출의 온라인 경기(대부분 매시 자동 대전). 다른 제출(8899)의 경기는 건너뛴다.
//   data/top/features.jsonl    상위권끼리의 경기 중 data/top/snapshot-20260929a.keys에 있고 SSS가 끼지 않은 경기
// 출력: data/online/baseline_study.json(경기별 기록 games[], 집계 summary), 표준 출력에 집계 표(마크다운).
// 방법:
//   - 리플레이는 tools/replay.js와 같은 로더(tools/top_features.js makeLoader)로 읽는다.
//   - tools/top_features.js의 extract()를 그대로 돌려 검증 기준으로 쓴다. 따로 같은 걸음 시뮬레이션으로 몸을 재구성하며
//     사망 원인, 진주 출처와 먹은 쪽, 시야, 한 걸음 탈출 칸 같은 세부를 더 기록한다. 사망·분열·창별 먹이·10라운드 상태가
//     extract()와 한 건씩 같은지, 질량 항등식(시작 + 먹이 − 질주 비용 − 사망 길이 = 끝)이 맞는지 경기마다 확인한다(checks).
//   - 리플레이 해석은 자식 프로세스 최대 3개(--jobs)로 나눈다.
//   - 정의는 파일 아래쪽 DEFS와 research/experiments/online-baseline-r1.md "자료" 절에 있다.
'use strict';
const fs = require('fs'), path = require('path');
const cp = require('child_process');
const TF = require('./top_features.js');   // 자식 프로세스에서도 주 스레드라서 top_features.js의 워커 코드는 돌지 않는다
const CHILD = process.argv.includes('--child');

const ROOT = path.resolve(__dirname, '..');
const FORMAT = 'baseline-study-v1';
const OWN_TEAM = 583, OWN_SUB = 10365;
const SETS = [
  { set: 'baseline', dir: 'data/online/baseline-r1' },
  { set: 'r1', dir: 'data/online/r1-online' },
];
const TOP_FEATURES = 'data/top/features.jsonl', TOP_KEYS = 'data/top/snapshot-20260929a.keys';
const ELIM_MAPS = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const R500_MAPS = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const MAPS = [...ELIM_MAPS, ...R500_MAPS];
const OPPS = [306, 70, 20, 801, 264, 46, 545];   // 리더보드 순(1–6위) + DEV 545
const mapType = m => ELIM_MAPS.includes(m) ? 'elim' : R500_MAPS.includes(m) ? 'r500' : 'other';
const TYPE_KO = { elim: '전멸형', r500: '500라운드형' };
const BIG = 6, SMALL = 3, VIS = 3, NEAR = 9, WINLEN = 50, NWIN = 10, EAT_SOON = 20;
// 봇의 라운드 관문(bot/params.hpp): 300 음파 공유, 340 모이기(분열 중단·먹이기), 430 왕 먹이기, 450 분열 금지, 495 공격적 교환
const GATES = [[0, 'r0–299'], [300, 'r300–339 음파 공유'], [340, 'r340–429 모이기'], [430, 'r430–449 왕 먹이기'], [450, 'r450–494 분열 금지'], [495, 'r495–499 공격 교환']];
const phaseOf = r => { let p = 0; for (let i = 0; i < GATES.length; i++) if (r >= GATES[i][0]) p = i; return p; };
const win = r => Math.max(0, Math.min(NWIN - 1, Math.floor(r / WINLEN)));
const DIRS = 'NESW';

// ---------------------------------------------------------------------------------------------------------------
// 지도: 칸 번호 t = y*W + x, 이웃 표 nb[t*4+d] (d = N,E,S,W; 해초면 -1). top_features.extract의 across()와 같은 규칙.
function buildGeo(M) {
  const W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const DXa = { N: 0, E: 1, S: 0, W: -1 }, DYa = { N: -1, E: 0, S: 1, W: 0 };
  function across(x, y, d) {
    let ek, kelp;
    if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
    else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
    else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
    else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    const p = portal.get(ek);
    if (p) {
      if (d === 'N') return { x: p.x, y: wy(p.y - 1), portal: true };
      if (d === 'S') return { x: p.x, y: p.y, portal: true };
      if (d === 'W') return { x: wx(p.x - 1), y: p.y, portal: true };
      return { x: p.x, y: p.y, portal: true };
    }
    if (kelp) return null;
    return { x: wx(x + DXa[d]), y: wy(y + DYa[d]) };
  }
  const nb = new Int32Array(W * H * 4).fill(-1), portalEdge = new Uint8Array(W * H * 4);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) for (let d = 0; d < 4; d++) {
    const r = across(x, y, DIRS[d]); nb[(y * W + x) * 4 + d] = r ? r.y * W + r.x : -1; if (r && r.portal) portalEdge[(y * W + x) * 4 + d] = 1;
  }
  return { W, H, N: W * H, nb, portalEdge };
}

// 사망 분류(그 드래곤의 팀 기준). H: 머리끼리(둘 다 죽음), O: 남의 몸, W: 해초, S: 자기 몸, A: 유효 행동 없음.
function classify(rec) {
  if (rec.reason === 'H') {
    if (rec.mover) return rec.hitSide === rec.side ? 'H-ally' : 'H-attack';     // 자기가 움직여 적 머리로(박음)
    return rec.by && rec.by.side === rec.side ? 'H-ally' : 'H-rammed';           // 적이 움직여 자기 머리로(박힘)
  }
  if (rec.reason === 'O') return rec.hitSide === rec.side ? 'O-ally' : 'O-enemy';
  return rec.reason;
}
// 우리 사망의 세부 분류(지표 문자열 = 우리 봇이 그 턴에 남긴 dragonIndicator). 순서가 우선순위다.
const CLS2 = ['stub', 'feed', 'H-rammed', 'H-attack', 'ally', 'trapped', 'O-enemy', 'W/S', 'A'];
const CLS2_KO = { stub: '탈출 분열 뒤 남은 머리(갇힘)', feed: '왕 먹이기(자해)', 'H-rammed': '적이 우리 머리를 박음', 'H-attack': '우리가 적 머리를 박음', ally: '아군과 충돌',
  trapped: '그 밖의 갇힘(빈 이웃 0)', 'O-enemy': '적 몸에 박음', 'W/S': '해초·자기 몸(빈 이웃 있음)', A: '유효 행동 없음' };
const STUB_ROUNDS = 3;   // 탈출 분열 뒤 이 라운드 안에 갇혀 죽은 부모(머리 쪽 2칸 남짓)는 'stub'
function cls2(rec) {
  if (rec.side === 0 && rec.mover && rec.free === 0 && rec.sinceEscape !== undefined && rec.sinceEscape <= STUB_ROUNDS) return 'stub';
  if (rec.side === 0 && rec.tag === 'feed') return 'feed';
  if (rec.cls === 'H-rammed') return 'H-rammed';
  if (rec.cls === 'H-attack') return 'H-attack';
  if (rec.cls === 'H-ally' || rec.cls === 'O-ally') return 'ally';
  if (rec.mover && rec.free === 0) return 'trapped';
  if (rec.cls === 'O-enemy') return 'O-enemy';
  if (rec.cls === 'W' || rec.cls === 'S') return 'W/S';
  return 'A';
}
// 상대 사망 분류: 우리가 잡은 것(박힘·우리 몸) / 박으러 와서 같이 죽음 / 갇힘 / 빈 이웃이 있는데 자해 / 아군 충돌
const THEM_CLS = ['H-rammed', 'H-attack', 'O-enemy', 'trapped', 'self-free', 'ally'];
const THEM_KO = { 'H-rammed': '우리가 박아 죽임', 'H-attack': '우리 머리를 박고 같이 죽음', 'O-enemy': '우리 몸에 박음', trapped: '갇힘(빈 이웃 0)',
  'self-free': '빈 이웃 있는 자해(W/S/A)', ally: '아군과 충돌' };
function themCls(rec) {
  if (rec.cls === 'H-rammed' || rec.cls === 'H-attack') return rec.cls;
  if (rec.cls === 'H-ally' || rec.cls === 'O-ally') return 'ally';
  if (rec.mover && rec.free === 0) return 'trapped';
  if (rec.cls === 'O-enemy') return 'O-enemy';
  return 'self-free';
}
function indTag(ind) {
  const s = ind || '';
  if (s.startsWith('feed')) return 'feed';
  if (s.startsWith('escape-split')) return 'escape';
  if (s.startsWith('split')) return 'split';
  if (s === 'no-exit') return 'noexit';
  if (s === 'last-trade') return 'lasttrade';
  if (s === 'degraded') return 'degraded';
  if (/ TRADE/.test(s)) return 'trade';
  return null;
}
const indValue = ind => { const m = / v(-?\d+(?:\.\d+)?)/.exec(ind || ''); return m ? +m[1] : null; };
const indGather = ind => / g\d+/.test(ind || '');

// ---------------------------------------------------------------------------------------------------------------
// 한 경기 분석. R = 해석한 리플레이, g = 색인 행 + 게임 JSON 정보.
function analyse(R, g) {
  const M = R.match.map, { W, H, N, nb, portalEdge } = buildGeo(M);
  const US = String(g.ourSide).toUpperCase();
  const sideOf = team => team === US ? 0 : 1;
  const tor = (a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return [dx, dy]; };
  const cheb = (a, b) => { const [x, y] = tor(a, b); return Math.max(x, y); };
  const man = (a, b) => { const [x, y] = tor(a, b); return x + y; };
  const tileOf = s => s.y * W + s.x;

  const drag = new Map(), occ = new Int32Array(N).fill(-1);
  const pearl = new Int32Array(N).fill(-1);   // -1 없음, -2 시작 배치, -3 자연 생성, >= 0 떨군 사망의 deaths 번호
  const setOcc = d => { for (const t of d.body) occ[t] = d.id; };
  const clrOcc = d => { for (const t of d.body) if (occ[t] === d.id) occ[t] = -1; };
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl[i] = -2;
  let ev = 0, round = -1, cur = -1, dropCtx = -1;
  const lives = [];
  const newDragon = (id, team, body, born, fromSplit, parent) => {
    const d = { id, team, body, born, fromSplit, bornLen: body.length, parent, maxLen: body.length, maxR: Math.max(0, born), created: ev,
      fate: null, expect: [], act: null, tle: false, ind: null, free: null, snap: null, actPre: body[0], actLen: body.length, actSteps: 0, neck: false,
      lastEscape: null, eatNat: 0 };
    drag.set(id, d); setOcc(d); return d;
  };
  for (const d0 of M.initialDragons) newDragon(d0.id, d0.team, d0.body.map(tileOf), 0, 0, null);
  const init = [0, 0], initIds = [[], []];
  for (const d of drag.values()) { init[sideOf(d.team)]++; initIds[sideOf(d.team)].push(d.id); }
  // 우리 시작 영역: 우리 처음 드래곤들의 머리에서 포털을 쓰지 않고 닿는 칸(해초만 막음). 자연 진주가 생긴 칸과 먹은 곳을 이 영역 안팎으로 나눈다.
  const region = new Uint8Array(N);
  { const q = []; for (const d of drag.values()) if (sideOf(d.team) === 0 && !region[d.body[0]]) { region[d.body[0]] = 1; q.push(d.body[0]); }
    while (q.length) { const t = q.pop(); for (let k = 0; k < 4; k++) { if (portalEdge[t * 4 + k]) continue; const u = nb[t * 4 + k]; if (u >= 0 && !region[u]) { region[u] = 1; q.push(u); } } } }
  const spawnCount = new Int32Array(N);
  const reg = { spawnsIn: 0, spawnsOut: 0, eat: [[0, 0], [0, 0]] };   // eat[side][0 = 영역 안, 1 = 밖] (자연 진주)

  const Z = () => new Array(NWIN).fill(0);
  const T = [0, 1].map(() => ({ u: [], t: [], l: [], splits: [], eat: { nat: Z(), own: Z(), opp: Z() }, kingEat: { nat: Z(), own: Z(), opp: Z() },
    paid: Z(), sprints: Z(), turns: 0, eatEvents: 0, portalSteps: 0, portalDragons: new Set() }));
  const ind = { turns: 0, feed: 0, gather: 0, escape: 0, split: 0, noexit: 0, lasttrade: 0, trade: 0, late: 0, degraded: 0 };
  const chk = { updates: 0, deaths: 0, splits: 0, eaten: 0, eatTile: 0, drops: 0 };
  const deaths = [];
  // 탈출 분열 사슬: 탈출 분열로 태어난 자식이 다시 탈출 분열하면 같은 사슬이다(자식 id -> 사슬).
  const chains = [], chainOf = new Map();
  const closeDrop = () => { if (dropCtx >= 0) { const D = deaths[dropCtx]; if (D._got !== D.drop) chk.drops++; delete D._got; dropCtx = -1; } };
  const snapshot = () => {
    const acc = [[0, 0, 0], [0, 0, 0]];
    for (const d of drag.values()) { const a = acc[sideOf(d.team)], L = d.body.length; a[0]++; a[1] += L; if (L > a[2]) a[2] = L; }
    for (const si of [0, 1]) { T[si].u.push(acc[si][0]); T[si].t.push(acc[si][1]); T[si].l.push(acc[si][2]); }
  };
  const longestOther = d => { let m = 0; for (const o of drag.values()) if (o.team === d.team && o.id !== d.id && o.body.length > m) m = o.body.length; return m; };
  const unitsOf = team => { let n = 0; for (const o of drag.values()) if (o.team === team) n++; return n; };
  const freeCount = h => { let f = 0; for (let k = 0; k < 4; k++) { const u = nb[h * 4 + k]; if (u >= 0 && occ[u] === -1) f++; } return f; };
  const countInd = s => {
    ind.turns++;
    const tg = indTag(s);
    if (tg && ind[tg] !== undefined) ind[tg]++;
    if (s && / late/.test(s)) ind.late++;
    if (indGather(s)) ind.gather++;
  };

  // 우리 드래곤의 결정 순간(행동 직전) 스냅숏: 한 걸음 후보 4칸, 근처 적 머리(맨해튼 <= NEAR)에서 빈 칸으로만 가는 BFS 거리.
  // 적의 도달 거리 reach = 길이 - 1(질주는 첫 걸음 뒤 한 걸음마다 한 칸을 치르고, 길이 2는 치를 수 없다. 먹이는 무시).
  const bfsD = new Int16Array(N), bfsS = new Int32Array(N), bq = new Int32Array(N); let stamp = 0;
  const bfs = (src, depth, target) => {
    stamp++; let qh = 0, qt = 0; bq[qt++] = src; bfsS[src] = stamp; bfsD[src] = 0;
    while (qh < qt) {
      const t = bq[qh++], dd = bfsD[t]; if (dd >= depth) continue;
      for (let k = 0; k < 4; k++) {
        const u = nb[t * 4 + k];
        if (u < 0 || bfsS[u] === stamp) continue;
        if (occ[u] !== -1 && u !== target) continue;          // 몸은 지나갈 수 없다. 우리 머리 칸은 도착점으로만 센다.
        bfsS[u] = stamp; bfsD[u] = dd + 1;
        if (occ[u] === -1) bq[qt++] = u;
      }
    }
  };
  const distTo = t => t >= 0 && bfsS[t] === stamp ? bfsD[t] : 99;
  // 후보 칸에서 빈 칸만 지나 닿는 칸 수(상한 cap). 봇의 areaSafety처럼 cap = max(2L+16, 96)이고, 몸은 움직이지 않는다고 본다.
  const area = (src, cap, h0) => {
    stamp++; let qh = 0, qt = 0; bq[qt++] = src; bfsS[src] = stamp; bfsS[h0] = stamp;
    while (qh < qt && qt < cap) {
      const t = bq[qh++];
      for (let k = 0; k < 4 && qt < cap; k++) { const u = nb[t * 4 + k]; if (u < 0 || bfsS[u] === stamp || occ[u] !== -1) continue; bfsS[u] = stamp; bq[qt++] = u; }
    }
    return qt;
  };
  const takeSnap = (d, a) => {
    const h0 = d.body[0];
    let h1 = h0;                                                   // 행동 뒤 머리(충돌은 무시한 예측; 죽으면 나중에 버린다)
    if (a && a.kind === 'move') for (const st of a.steps) { const u = h1 >= 0 ? nb[h1 * 4 + DIRS.indexOf(st)] : -1; h1 = u; if (u < 0) break; }
    const cands = []; for (let k = 0; k < 4; k++) { const u = nb[h0 * 4 + k]; cands.push(u >= 0 && occ[u] === -1 ? u : -1); }
    const L = d.body.length, cap = Math.max(2 * L + 16, 96);
    const areas = cands.map(c => c >= 0 ? area(c, cap, h0) : 0);
    const enemies = [];
    for (const o of drag.values()) {
      if (o.team === d.team) continue;
      const eh = o.body[0], mn = man(eh, h0);
      if (mn > NEAR) continue;
      const len = o.body.length, reach = Math.max(1, len - 1);
      bfs(eh, Math.min(reach, NEAR + 1), h0);
      enemies.push({ id: o.id, len, reach, cheb: cheb(eh, h0), man: mn, dC: cands.map(c => c >= 0 ? distTo(c) : null), dPre: distTo(h0), dPost: distTo(h1) });
    }
    return { r: round, ev, h0, h1, free: d.free, ind: d.ind, kind: a ? a.kind : null, steps: a && a.kind === 'move' ? a.steps.length : 0, cands, enemies, eat: 0, areas, L };
  };
  const finishSnap = (s, died) => {
    let legalN = 0, safeN = 0, viableSafeN = 0, viableN = 0;
    for (let k = 0; k < 4; k++) {
      if (s.cands[k] < 0) continue; legalN++;
      const viable = s.areas[k] >= s.L + 2; if (viable) viableN++;
      if (s.enemies.every(x => x.dC[k] > x.reach)) { safeN++; if (viable) viableSafeN++; }
    }
    s.legalN = legalN; s.safeN = safeN; s.viableN = viableN; s.viableSafeN = viableSafeN;
    if (died) { s.h1 = -1; for (const x of s.enemies) x.dPost = null; }
    s.postSafe = s.h1 >= 0 ? (s.enemies.every(x => x.dPost > x.reach) ? 1 : 0) : null;
  };
  const eatPearl = (d, si, k, lenBefore) => {
    const src = pearl[k]; pearl[k] = -1;
    const w = win(round), t = T[si];
    const kind = src < 0 ? 'nat' : deaths[src].side === si ? 'own' : 'opp';
    t.eat[kind][w]++;
    const king = lenBefore >= longestOther(d);
    if (king) t.kingEat[kind][w]++;
    if (kind === 'nat') { d.eatNat++; reg.eat[si][region[k] ? 0 : 1]++; const c = chainOf.get(d.id); if (c && round <= c.last + 2) c.nat++; }
    if (src >= 0) {
      const D = deaths[src], who = si === 0 ? 'Us' : 'Them';
      D['eat' + who]++; if (round - D.r <= EAT_SOON) D['eat' + who + '20']++; if (king) D['eatKing' + who]++;
    }
  };
  const ourDeathDetail = (rec, d, m) => {
    rec.ind = d.ind || null;
    rec.tag = indTag(d.ind);
    const s = d.snap;
    if (!s) { rec.dec = null; return; }
    rec.dec = { dr: round - s.r, free: s.free, legal: s.legalN, safe: s.safeN, viable: s.viableN, viableSafe: s.viableSafeN, postSafe: s.postSafe, steps: s.steps, kind: s.kind, eat: s.eat,
      nNear: s.enemies.length, nVis: s.enemies.filter(x => x.cheb <= VIS).length };
    if (m && rec.cls === 'H-rammed') {
      const a = s.enemies.find(x => x.id === m.id);
      const present = m.created < s.ev ? 1 : 0;
      rec.att = { present, cheb: cheb(s.h0, m.actPre), man: man(s.h0, m.actPre), inSnap: a ? 1 : 0,
        reach: a ? a.reach : null, dPre: a ? a.dPre : null, dPost: a ? a.dPost : null,
        out: a ? a.dC.filter((x, k) => s.cands[k] >= 0 && x > a.reach).length : null,
      outViable: a ? a.dC.filter((x, k) => s.cands[k] >= 0 && x > a.reach && s.areas[k] >= s.L + 2).length : null };
      rec.att.seen = present && rec.att.cheb <= VIS ? 1 : 0;
    }
  };

  for (const e of R.events) {
    ev++;
    if (dropCtx >= 0 && !(e.type === 'tileChange' && e.hasPearl)) closeDrop();
    switch (e.type) {
      case 'roundStart': round = e.round; snapshot(); break;
      case 'turnStart': {
        cur = e.id; const d = drag.get(cur);
        if (d) { T[sideOf(d.team)].turns++; d.fate = null; d.expect = []; d.act = null; d.tle = false; d.ind = null; }
        break;
      }
      case 'dragonIndicator': { const d = drag.get(e.id); if (d) d.ind = e.text; break; }
      case 'tileChange': {
        const k = tileOf(e.tile);
        if (e.hasPearl) { if (dropCtx >= 0) { pearl[k] = dropCtx; deaths[dropCtx]._got++; } else { pearl[k] = -3; if (round >= 0) { spawnCount[k]++; if (region[k]) reg.spawnsIn++; else reg.spawnsOut++; } } }
        else {
          if (pearl[k] !== -1) { chk.eatTile++; pearl[k] = -1; }
          const d = drag.get(cur); if (d && round >= 0) T[sideOf(d.team)].eatEvents++;
        }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action, si = sideOf(d.team), t = T[si];
        d.act = a ? a.kind : null; d.tle = !!e.tle;
        d.actPre = d.body[0]; d.actLen = d.body.length; d.actSteps = a && a.kind === 'move' ? a.steps.length : 0; d.neck = false;
        d.free = freeCount(d.body[0]);
        let snap = null;
        if (si === 0 && round >= 0) { countInd(d.ind); snap = takeSnap(d, a); }
        if (!a || a.kind !== 'move') { if (snap) { finishSnap(snap, false); d.snap = snap; } break; }
        const w = win(round);
        if (a.steps.length >= 2) t.sprints[w]++;
        clrOcc(d);
        const body = d.body.slice();
        let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i, why: 'sprint' }; break; }
          const h = body[0], di = DIRS.indexOf(a.steps[i]), nx = nb[h * 4 + di];
          if (i === 0 && body.length >= 2 && nx === body[1]) d.neck = true;
          if (nx < 0) { fate = { reason: 'W', step: i }; break; }
          if (body.includes(nx)) { fate = { reason: 'S', step: i }; break; }
          const o = occ[nx];
          if (o !== -1) {
            const od = drag.get(o), isHead = od.body[0] === nx;
            fate = { reason: isHead ? 'H' : 'O', step: i, hit: o, hitTeam: od.team, hitLen: od.body.length };
            break;
          }
          if (portalEdge[h * 4 + di]) { t.portalSteps++; t.portalDragons.add(d.id); }
          body.unshift(nx);
          if (pearl[nx] !== -1) { eatPearl(d, si, nx, body.length - 1); if (snap) snap.eat++; } else body.pop();
          if (i > 0) { body.pop(); t.paid[w]++; }
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate; d.body = body; setOcc(d);
        if (body.length > d.maxLen) { d.maxLen = body.length; d.maxR = round; }
        if (snap) { finishSnap(snap, !!fate); d.snap = snap; }
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id);
        if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        const eh = tileOf(e.head), et = tileOf(e.tail);
        if (x.h !== eh || x.t !== et) {
          chk.updates++;
          clrOcc(d);
          const b = d.body.slice();
          if (b[0] !== eh) b.unshift(eh);
          while (b.length > 1 && b[b.length - 1] !== et) b.pop();
          d.body = b; d.expect = []; setOcc(d);
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        const lenBefore = p.body.length, cl = e.childBody.length;
        if (lenBefore !== e.parentBody.length + cl) chk.splits++;
        const si = sideOf(p.team);
        const leader = lenBefore >= longestOther(p) ? 1 : 0;
        const kind = si === 0 ? (indTag(p.ind) === 'escape' ? 'escape' : indTag(p.ind) === 'split' ? 'policy' : 'other') : null;
        T[si].splits.push([round, lenBefore, cl, unitsOf(p.team), leader, kind, p.id, e.childId]);
        clrOcc(p); p.body = e.parentBody.map(tileOf); setOcc(p);
        newDragon(e.childId, e.team, e.childBody.map(tileOf), round, 1, p.id);
        if (kind === 'escape') {
          p.lastEscape = round;
          let c = chainOf.get(p.id);
          if (!c) { c = { start: round, last: round, count: 0, lens: [], nat: 0, head: p.body[0] }; chains.push(c); }
          c.count++; c.last = round; c.lens.push(lenBefore);
          chainOf.set(p.id, c); chainOf.set(e.childId, c);
        }
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const si = sideOf(d.team), mover = cur === d.id, len = d.body.length, other = longestOther(d);
        const rec = { side: si, r: round, id: d.id, reason: e.reason, len, born: d.born, fromSplit: d.fromSplit, bornLen: d.bornLen, maxLen: d.maxLen,
          leader: len >= other ? 1 : 0, otherLongest: other, units: unitsOf(d.team), mover: mover ? 1 : 0, phase: phaseOf(round),
          drop: Math.ceil(len / 2), eatUs: 0, eatThem: 0, eatUs20: 0, eatThem20: 0, eatKingUs: 0, eatKingThem: 0, _got: 0 };
        if (si === 0 && d.lastEscape !== null) rec.sinceEscape = round - d.lastEscape;
        let m = null;
        if (mover) {
          const f = d.fate;
          rec.kind = d.act; rec.steps = d.actSteps; rec.free = d.free; rec.fatalStep = f ? f.step : null; rec.neck = d.neck ? 1 : 0;
          if (f && f.hit !== undefined) { rec.hitSide = sideOf(f.hitTeam); rec.hitLen = f.hitLen; }
          if (e.reason === 'A') {
            rec.why = d.tle ? 'tle' : f ? f.why : d.act === 'split' ? 'split' : d.act === 'suicide' ? 'suicide' : d.act === null ? 'none' : 'other';
            if (f && f.reason !== 'A') chk.deaths++;
          } else if (!f || f.reason !== e.reason) chk.deaths++;
        } else {
          m = drag.get(cur);
          if (m) rec.by = { id: m.id, side: sideOf(m.team), len: m.actLen, lenAtHit: m.body.length, steps: m.actSteps, hitStep: m.fate ? m.fate.step : null,
            fromSplit: m.fromSplit, bornLen: m.bornLen, born: m.born };
          if (e.reason !== 'H' || !m || !m.fate || m.fate.hit !== d.id) chk.deaths++;
        }
        rec.cls = classify(rec);
        if (si === 0) ourDeathDetail(rec, d, m);
        rec.cls2 = si === 0 ? cls2(rec) : themCls(rec);
        lives.push({ side: si, id: d.id, born: d.born, fromSplit: d.fromSplit, maxLen: d.maxLen, maxR: d.maxR, died: round, len, cls2: rec.cls2 });
        deaths.push(rec);
        clrOcc(d); drag.delete(e.id);
        dropCtx = deaths.length - 1;
        break;
      }
      default: break;
    }
  }
  closeDrop();
  for (const D of deaths) for (const k of ['eatUs', 'eatThem', 'eatUs20', 'eatThem20', 'eatKingUs', 'eatKingThem']) if (!D[k]) delete D[k];
  const rounds = round + 1;
  snapshot();   // 마지막 라운드가 끝난 뒤 = 인덱스 rounds
  for (const d of drag.values()) lives.push({ side: sideOf(d.team), id: d.id, born: d.born, fromSplit: d.fromSplit, maxLen: d.maxLen, maxR: d.maxR, died: null, len: d.body.length, cls2: null });
  for (const si of [0, 1]) { let sim = 0; for (const k of ['nat', 'own', 'opp']) for (const x of T[si].eat[k]) sim += x; chk.eaten += Math.abs(sim - T[si].eatEvents); }

  const res = R.result, sideRes = si => res['team' + (si === 0 ? US : (US === 'A' ? 'B' : 'A'))];
  const final = [0, 1].map(si => ({ units: sideRes(si).dragonCount, total: sideRes(si).totalLength, longest: sideRes(si).longestDragon }));
  const finalMatch = [0, 1].every(si => T[si].u[rounds] === final[si].units && T[si].t[rounds] === final[si].total && T[si].l[rounds] === final[si].longest);
  // 질량 항등식: 시작 몸길이 합 + 먹은 진주 - 질주 비용 - 죽은 몸길이 = 끝 몸길이 합
  const mass = [0, 1].map(si => {
    const eaten = ['nat', 'own', 'opp'].reduce((s, k) => s + T[si].eat[k].reduce((a, b) => a + b, 0), 0);
    const paid = T[si].paid.reduce((a, b) => a + b, 0), dl = deaths.filter(x => x.side === si).reduce((a, x) => a + x.len, 0);
    return { init: T[si].t[0], eaten, paid, deathLen: dl, final: T[si].t[rounds], ok: T[si].t[0] + eaten - paid - dl === T[si].t[rounds] };
  });
  const pearlsLeft = { nat: 0, us: 0, them: 0 };
  for (let k = 0; k < N; k++) { const s = pearl[k]; if (s === -1) continue; if (s < 0) pearlsLeft.nat++; else if (deaths[s].side === 0) pearlsLeft.us++; else pearlsLeft.them++; }
  const peak = si => { let b = null; for (const L of lives) if (L.side === si && (!b || L.maxLen > b.maxLen || (L.maxLen === b.maxLen && L.maxR < b.maxR))) b = L; return b; };
  return {
    gameId: g.gameId, set: g.set, map: g.mapName, type: mapType(g.mapName), opp: g.opponentTeam, oppName: g.oppName, oppElo: g.oppElo, ourElo: g.ourElo,
    side: US, win: !!g.ourWin, ranked: !!g.ranked, sub: g.ourSubmission, seed: R.seed, width: W, height: H, init, winnerSide: res.winner === US ? 0 : res.winner ? 1 : null,
    endReason: res.endReason, rounds, final, finalMatch,
    flow: [0, 1].map(si => ({ u: T[si].u, t: T[si].t, l: T[si].l })),
    deaths, splits: [T[0].splits, T[1].splits],
    eat: [T[0].eat, T[1].eat], kingEat: [T[0].kingEat, T[1].kingEat], paid: [T[0].paid, T[1].paid], sprints: [T[0].sprints, T[1].sprints], turns: [T[0].turns, T[1].turns],
    lives: lives.filter(L => L.maxLen >= BIG), peak: [peak(0), peak(1)], ind, mass, pearlsLeft, checks: chk,
    portals: (M.portals || []).length, portalSteps: [T[0].portalSteps, T[1].portalSteps], portalDragons: [T[0].portalDragons.size, T[1].portalDragons.size],
    region: (() => { let tiles = 0, spawnTiles = 0, narrow = 0, spawnTilesAll = 0;
      for (let t = 0; t < N; t++) { if (spawnCount[t]) spawnTilesAll++; if (!region[t]) continue; tiles++; if (spawnCount[t]) { spawnTiles++; let open = 0; for (let k = 0; k < 4; k++) if (nb[t * 4 + k] >= 0) open++; if (open <= 2) narrow++; } }
      return { tiles, mapTiles: N, spawnTiles, spawnTilesAll, narrowSpawnTiles: narrow, spawnsIn: reg.spawnsIn, spawnsOut: reg.spawnsOut, natEat: reg.eat }; })(),
    chains: chains.map(c => ({ start: c.start, last: c.last, count: c.count, lenMedian: median(c.lens), lenMax: Math.max(...c.lens), nat: c.nat, head: [c.head % W, (c.head / W) | 0] })),
  };
}

// extract()와 한 건씩 맞춰 본다. 틀린 건수를 rec.checks.vsExtract에 남긴다(모두 0이어야 한다).
function verify(rec, f) {
  const US = rec.side, letters = US === 'A' ? ['A', 'B'] : ['B', 'A'];
  const v = { extractSim: f.meta.simMismatches, extractChecks: 0, deaths: 0, splits: 0, eaten: 0, timeline: 0, winner: 0 };
  for (const [k, x] of Object.entries(f.meta.checks)) if ((typeof x === 'number' && k !== 'format' && x) || x === false) v.extractChecks++;
  for (const si of [0, 1]) {
    const F = f[letters[si]];
    const mine = rec.deaths.filter(x => x.side === si);
    if (mine.length !== F.deaths.length) v.deaths += Math.abs(mine.length - F.deaths.length) || 1;
    F.deaths.forEach((x, i) => { const y = mine[i]; if (!y || y.r !== x.r || y.id !== x.id || y.reason !== x.reason || y.len !== x.len) v.deaths++; });
    const sp = rec.splits[si];
    if (sp.length !== F.splits.length) v.splits += Math.abs(sp.length - F.splits.length) || 1;
    F.splits.forEach((x, i) => { const y = sp[i]; if (!y || y[0] !== x[0] || y[1] !== x[1] || y[2] !== x[2] || y[3] !== x[3]) v.splits++; });
    for (let w = 0; w < NWIN; w++) { const s = rec.eat[si].nat[w] + rec.eat[si].own[w] + rec.eat[si].opp[w]; if (s !== F.eaten[w]) v.eaten++; }
    for (const p of F.timeline) {
      const fl = rec.flow[si], at = a => p.r < a.length ? a[p.r] : a[a.length - 1];
      if (at(fl.u) !== p.units || at(fl.t) !== p.total || at(fl.l) !== p.longest) v.timeline++;
    }
  }
  if ((rec.win ? 0 : 1) !== rec.winnerSide) v.winner++;
  rec.checks.vsExtract = v;
}

// ---------------------------------------------------------------------------------------------------------------
// 자식 프로세스(--child): 리플레이 한 판을 읽어 기록을 돌려준다. worker_threads를 쓰면 top_features.js의 워커 코드가
// 같은 메시지에 함께 응답하므로 child_process.fork를 쓴다.
if (CHILD) {
  const load = TF.makeLoader(TF.viewerSource());
  process.on('message', task => {
    if (task === 'exit') { process.exit(0); return; }
    try {
      const R = load(task.file);
      const f = TF.extract(R, task.row);
      const rec = analyse(R, task.g);
      verify(rec, f);
      process.send({ i: task.i, rec });
    } catch (err) { process.send({ i: task.i, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}

// ---------------------------------------------------------------------------------------------------------------
// 집계 도우미
const sum = (a, f = x => x) => a.reduce((s, x) => s + f(x), 0);
const mean = a => a.length ? sum(a) / a.length : NaN;
const quant = (a, p) => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y), i = (b.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return b[lo] + (b[hi] - b[lo]) * (i - lo); };
const median = a => quant(a, 0.5);
const st = a => ({ n: a.length, mean: r3(mean(a)), median: r3(median(a)), q1: r3(quant(a, 0.25)), q3: r3(quant(a, 0.75)), min: a.length ? Math.min(...a) : null, max: a.length ? Math.max(...a) : null });
const r3 = x => Number.isFinite(x) ? Math.round(x * 1000) / 1000 : null;
const fx = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '-';
const pc = (a, b, d = 0) => b ? (100 * a / b).toFixed(d) + '%' : '-';
const table = (head, rows) => ['| ' + head.join(' | ') + ' |', '|' + head.map(() => '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const flowAt = (g, si, m, r) => { const a = g.flow[si][m]; return r < a.length ? a[r] : a[a.length - 1]; };
const inProg = (rounds, r) => rounds > r || (r === 500 && rounds === 500);
const CHECK_R = [0, 10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 340, 350, 400, 430, 450, 500];
const MEAS = [['u', 'units', '수'], ['t', 'total', '몸길이 합'], ['l', 'longest', '최장']];

// 상위권 경기(features.jsonl): 스냅숏 키, SSS 제외. 행마다 {type, W: 승자 팀 객체, L: 패자 팀 객체, rounds, names}
function loadTop() {
  const keys = new Set(fs.readFileSync(path.join(ROOT, TOP_KEYS), 'utf8').trim().split('\n'));
  const out = [];
  for (const line of fs.readFileSync(path.join(ROOT, TOP_FEATURES), 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const f = JSON.parse(line), m = f.meta;
    if (!keys.has(m.battleId + ':' + m.gameId)) continue;
    if (m.teams.A.name === 'SSS' || m.teams.B.name === 'SSS') continue;
    const wl = m.winner === 'A' ? ['A', 'B'] : ['B', 'A'];
    out.push({ key: m.battleId + ':' + m.gameId, map: m.map, type: mapType(m.map), rounds: m.rounds, endReason: m.endReason, W: f[wl[0]], L: f[wl[1]], names: [m.teams[wl[0]].name, m.teams[wl[1]].name], A: f.A, B: f.B, teams: m.teams, winner: m.winner });
  }
  return out;
}
const tlAt = (team, r) => team.timeline[Math.min(team.timeline.length - 1, r / 10)];
const topMeasure = (team, m, r) => { const p = tlAt(team, r); return m === 'u' ? p.units : m === 't' ? p.total : p.longest; };

// 마지막으로 앞섰던 라운드: 우리(a) > 상대(b)인 가장 늦은 상태 인덱스. 없으면 null. step 10이면 0,10,..,500만 본다.
function lastLed(get, rounds, step) {
  let last = null;
  const end = step === 1 ? rounds : 500;
  for (let r = 0; r <= end; r += step) { const [a, b] = get(r); if (a > b) last = r; }
  return last;
}
// 끝까지 뒤진 첫 라운드: 그 뒤 모든 상태에서 우리 < 상대. 끝 상태에서 뒤지지 않으면 null.
function behindFrom(get, rounds) {
  let first = null;
  for (let r = rounds; r >= 0; r--) { const [a, b] = get(r); if (a < b) first = r; else break; }
  return first;
}

// ---------------------------------------------------------------------------------------------------------------
function aggregate(games, top) {
  const S = {};
  const B = games.filter(g => g.set === 'baseline'), O = games.filter(g => g.set === 'r1');
  const us = g => g.deaths.filter(d => d.side === 0), them = g => g.deaths.filter(d => d.side === 1);
  const byType = (gs, t) => gs.filter(g => g.type === t);
  const oppName = id => (B.find(g => g.opp === id) || O.find(g => g.opp === id) || {}).oppName || String(id);

  // ---- 검증
  const checkSum = {};
  for (const g of games) {
    for (const [k, v] of Object.entries(g.checks)) if (typeof v === 'number') checkSum[k] = (checkSum[k] || 0) + v;
    for (const [k, v] of Object.entries(g.checks.vsExtract || {})) checkSum['vsExtract.' + k] = (checkSum['vsExtract.' + k] || 0) + v;
    if (!g.finalMatch) checkSum.finalMismatch = (checkSum.finalMismatch || 0) + 1;
    for (const m of g.mass) if (!m.ok) checkSum.massMismatch = (checkSum.massMismatch || 0) + 1;
  }
  S.checks = checkSum;
  const indSum = gs => { const o = {}; for (const g of gs) for (const [k, v] of Object.entries(g.ind)) o[k] = (o[k] || 0) + v; for (const k of Object.keys(o)) o[k] = r3(o[k] / gs.length); return o; };
  S.indicators = { baseline: indSum(B), elim: indSum(byType(B, 'elim')), r500: indSum(byType(B, 'r500')), r1win: indSum(O.filter(g => g.win)), r1loss: indSum(O.filter(g => !g.win)) };
  S.sets = { baseline: { games: B.length, wins: B.filter(g => g.win).length }, r1: { games: O.length, wins: O.filter(g => g.win).length }, top: { games: top.length } };

  // ---- Q1 끝나는 모습
  const endRow = gs => {
    const elimUs = gs.filter(g => !g.win && g.endReason === 'teamEliminated'), elimThem = gs.filter(g => g.win && g.endReason === 'teamEliminated');
    const lim = gs.filter(g => g.endReason === 'roundLimit');
    return { n: gs.length, wins: gs.filter(g => g.win).length, elimUs: elimUs.length, elimThem: elimThem.length, roundLimit: lim.length, roundLimitWins: lim.filter(g => g.win).length,
      elimRound: st(elimUs.map(g => g.rounds - 1)),
      final: { us: { units: r3(mean(gs.map(g => g.final[0].units))), total: r3(mean(gs.map(g => g.final[0].total))), longest: r3(mean(gs.map(g => g.final[0].longest))) },
        them: { units: r3(mean(gs.map(g => g.final[1].units))), total: r3(mean(gs.map(g => g.final[1].total))), longest: r3(mean(gs.map(g => g.final[1].longest))) } },
      finalLimit: { us: r3(median(lim.map(g => g.final[0].longest))), them: r3(median(lim.map(g => g.final[1].longest))), usTotal: r3(median(lim.map(g => g.final[0].total))), themTotal: r3(median(lim.map(g => g.final[1].total))) } };
  };
  S.q1 = {
    byOpp: Object.fromEntries(OPPS.map(o => [o, { name: oppName(o), ...endRow(B.filter(g => g.opp === o)) }])),
    byMap: Object.fromEntries(MAPS.map(m => [m, endRow(B.filter(g => g.map === m))])),
    byType: { elim: endRow(byType(B, 'elim')), r500: endRow(byType(B, 'r500')) }, all: endRow(B),
    grid: B.map(g => ({ gameId: g.gameId, opp: g.opp, map: g.map, win: g.win, endReason: g.endReason, rounds: g.rounds, init: g.init, final: g.final })),
    pdVariants: B.filter(g => g.map === 'Prisoners Dilemma').map(g => ({ gameId: g.gameId, opp: g.opp, init: g.init, win: g.win })),
    pdTally: [3, 5].map(n => { const gs = B.filter(g => g.map === 'Prisoners Dilemma' && g.init[0] === n); return { init: n, games: gs.length, wins: gs.filter(g => g.win).length, elim: gs.filter(g => !g.win && g.endReason === 'teamEliminated').length }; }),
  };

  // ---- Q2 뒤지는 시점
  const curve = (gs, tg, t) => Object.fromEntries(MEAS.map(([m]) => [m, CHECK_R.map(r => {
    const g2 = gs.filter(g => inProg(g.rounds, r)), tp = tg.filter(x => x.type === t && inProg(x.rounds, r));
    return { r, n: g2.length, us: r3(median(g2.map(g => flowAt(g, 0, m, r)))), them: r3(median(g2.map(g => flowAt(g, 1, m, r)))),
      usMean: r3(mean(g2.map(g => flowAt(g, 0, m, r)))), themMean: r3(mean(g2.map(g => flowAt(g, 1, m, r)))),
      nTop: r % 10 === 0 ? tp.length : null, topW: r % 10 === 0 ? r3(median(tp.map(x => topMeasure(x.W, m, r)))) : null, topL: r % 10 === 0 ? r3(median(tp.map(x => topMeasure(x.L, m, r)))) : null };
  })]));
  S.q2 = { curves: {}, lastLed: {}, behind: {}, r1Curves: {} };
  for (const t of ['elim', 'r500']) {
    S.q2.curves[t] = curve(byType(B, t), top, t);
    S.q2.r1Curves[t] = { win: curve(byType(O, t).filter(g => g.win), [], t), loss: curve(byType(O, t).filter(g => !g.win), [], t) };
    const lost = byType(B, t).filter(g => !g.win), topT = top.filter(x => x.type === t);
    S.q2.lastLed[t] = {}; S.q2.behind[t] = {};
    for (const [m] of MEAS) {
      const per = lost.map(g => lastLed(r => [flowAt(g, 0, m, r), flowAt(g, 1, m, r)], g.rounds, 1));
      const p10 = lost.map(g => lastLed(r => [flowAt(g, 0, m, r), flowAt(g, 1, m, r)], g.rounds, 10));
      const tp = topT.map(x => lastLed(r => [topMeasure(x.L, m, r), topMeasure(x.W, m, r)], x.rounds, 10));
      S.q2.lastLed[t][m] = { n: lost.length, perRound: st(per.filter(x => x !== null)), neverPerRound: per.filter(x => x === null).length,
        step10: st(p10.filter(x => x !== null)), never10: p10.filter(x => x === null).length,
        top: st(tp.filter(x => x !== null)), topNever: tp.filter(x => x === null).length, topN: tp.length };
      const bf = lost.map(g => behindFrom(r => [flowAt(g, 0, m, r), flowAt(g, 1, m, r)], g.rounds));
      S.q2.behind[t][m] = st(bf.filter(x => x !== null));
    }
  }
  S.q2.peak = Object.fromEntries(['elim', 'r500'].map(t => [t, (() => {
    const gs = byType(B, t);
    return { usPeak: st(gs.map(g => Math.max(...g.flow[0].l))), usPeakRound: st(gs.map(g => g.flow[0].l.indexOf(Math.max(...g.flow[0].l)))),
      themPeak: st(gs.map(g => Math.max(...g.flow[1].l))), usUnitsMax: st(gs.map(g => Math.max(...g.flow[0].u))), themUnitsMax: st(gs.map(g => Math.max(...g.flow[1].u))) };
  })()]));

  // ---- Q3 질량을 잃는 방식
  const deathTable = (gs, side, classes, key) => {
    const n = gs.length, ds = gs.flatMap(side === 0 ? us : them);
    const row = {};
    for (const c of classes) {
      const x = ds.filter(d => d[key] === c);
      row[c] = { perGame: r3(x.length / n), lenPerGame: r3(sum(x, d => d.len) / n), big: x.filter(d => d.len >= BIG).length, bigPerGame: r3(x.filter(d => d.len >= BIG).length / n),
        bigLenPerGame: r3(sum(x.filter(d => d.len >= BIG), d => d.len) / n), n: x.length, len: sum(x, d => d.len) };
    }
    row.total = { perGame: r3(ds.length / n), lenPerGame: r3(sum(ds, d => d.len) / n), bigPerGame: r3(ds.filter(d => d.len >= BIG).length / n), bigLenPerGame: r3(sum(ds.filter(d => d.len >= BIG), d => d.len) / n), n: ds.length, len: sum(ds, d => d.len) };
    return row;
  };
  const groupsB = { all: B, elim: byType(B, 'elim'), r500: byType(B, 'r500'), loss: B.filter(g => !g.win), win: B.filter(g => g.win) };
  S.q3 = { ourDeaths: {}, theirDeaths: {} };
  for (const [k, gs] of Object.entries(groupsB)) { S.q3.ourDeaths[k] = deathTable(gs, 0, CLS2, 'cls2'); S.q3.theirDeaths[k] = deathTable(gs, 1, THEM_CLS, 'cls2'); }
  for (const [k, gs] of [['r1win', O.filter(g => g.win)], ['r1loss', O.filter(g => !g.win)]]) { S.q3.ourDeaths[k] = deathTable(gs, 0, CLS2, 'cls2'); S.q3.theirDeaths[k] = deathTable(gs, 1, THEM_CLS, 'cls2'); }

  // 적이 우리 머리를 박은 사망의 세부
  const rammed = (gs, pred) => {
    const ds = gs.flatMap(us).filter(d => d.cls === 'H-rammed' && pred(d));
    const dec = ds.filter(d => d.dec), att = ds.filter(d => d.att), pres = att.filter(d => d.att.present);
    const bl = d => d.by ? d.by.len : null;
    return {
      n: ds.length, perGame: r3(ds.length / gs.length), lenPerGame: r3(sum(ds, d => d.len) / gs.length), ourLen: st(ds.map(d => d.len)), leader: ds.filter(d => d.leader).length,
      attLen: { le2: ds.filter(d => bl(d) <= 2).length, l3: ds.filter(d => bl(d) === 3).length, l45: ds.filter(d => bl(d) >= 4 && bl(d) <= 5).length, ge6: ds.filter(d => bl(d) >= 6).length, median: r3(median(ds.map(bl))) },
      attFromSplit: ds.filter(d => d.by && d.by.fromSplit).length, attBornLe3: ds.filter(d => d.by && d.by.fromSplit && d.by.bornLen <= SMALL).length,
      attSteps: { s1: ds.filter(d => d.by && d.by.steps === 1).length, s2: ds.filter(d => d.by && d.by.steps === 2).length, s3: ds.filter(d => d.by && d.by.steps >= 3).length },
      attHitStep: { first: ds.filter(d => d.by && d.by.hitStep === 0).length, later: ds.filter(d => d.by && d.by.hitStep > 0).length },
      withDecision: dec.length, present: pres.length, seen: pres.filter(d => d.att.seen).length,
      cheb: { le1: pres.filter(d => d.att.cheb <= 1).length, c2: pres.filter(d => d.att.cheb === 2).length, c3: pres.filter(d => d.att.cheb === 3).length, c45: pres.filter(d => d.att.cheb >= 4 && d.att.cheb <= 5).length, ge6: pres.filter(d => d.att.cheb >= 6).length, median: r3(median(pres.map(d => d.att.cheb))) },
      inSnap: pres.filter(d => d.att.inSnap).length,
      postInReach: pres.filter(d => d.att.inSnap && d.att.dPost !== null && d.att.dPost <= d.att.reach).length,
      preInReach: pres.filter(d => d.att.inSnap && d.att.dPre <= d.att.reach).length,
      entered: pres.filter(d => d.att.inSnap && d.att.dPre > d.att.reach && d.att.dPost !== null && d.att.dPost <= d.att.reach).length,
      stayed: pres.filter(d => d.att.inSnap && d.att.dPre <= d.att.reach && d.att.dPost !== null && d.att.dPost <= d.att.reach).length,
      decEat: dec.filter(d => d.dec.eat > 0).length,
      outStep: pres.filter(d => d.att.inSnap && d.att.out > 0).length,
      safeStep: dec.filter(d => d.dec.safe > 0).length, postSafe: dec.filter(d => d.dec.postSafe === 1).length,
      viableSafe: dec.filter(d => d.dec.viableSafe > 0).length, outViable: pres.filter(d => d.att.inSnap && d.att.outViable > 0).length,
      dPost: { d1: pres.filter(d => d.att.dPost === 1).length, d2: pres.filter(d => d.att.dPost === 2).length, d3: pres.filter(d => d.att.dPost === 3).length, d4: pres.filter(d => d.att.dPost === 4).length,
        d5: pres.filter(d => d.att.dPost !== null && d.att.dPost >= 5 && d.att.dPost < 99).length, none: pres.filter(d => d.att.dPost === null || d.att.dPost >= 99).length },
      decFree0: dec.filter(d => d.dec.free === 0).length, decFree1: dec.filter(d => d.dec.free === 1).length, decSprint: dec.filter(d => d.dec.steps >= 2).length,
      decSplit: dec.filter(d => d.dec.kind === 'split').length, dr0: dec.filter(d => d.dec.dr === 0).length,
      gather: ds.filter(d => indGather(d.ind)).length, trade: ds.filter(d => indTag(d.ind) === 'trade').length,
      value: st(ds.map(d => indValue(d.ind)).filter(x => x !== null)),
      phase: GATES.map((_, i) => ds.filter(d => d.phase === i).length),
      nVis: st(dec.map(d => d.dec.nVis)), nNear: st(dec.map(d => d.dec.nNear)),
    };
  };
  S.q3.rammed = {};
  for (const [k, gs] of [['all', B], ['elim', byType(B, 'elim')], ['r500', byType(B, 'r500')], ['r1', O]]) {
    S.q3.rammed[k] = { big: rammed(gs, d => d.len >= BIG), small: rammed(gs, d => d.len < BIG), all: rammed(gs, () => true) };
  }
  // 갇힘: 우리가 움직여 죽을 때 빈 이웃 0
  const trapped = gs => {
    const ds = gs.flatMap(us).filter(d => d.mover && d.free === 0 && d.cls2 === 'trapped'), stubs = gs.flatMap(us).filter(d => d.cls2 === 'stub');
    const esc = gs.flatMap(g => g.splits[0].filter(s => s[5] === 'escape'));
    return { n: ds.length, perGame: r3(ds.length / gs.length), lenPerGame: r3(sum(ds, d => d.len) / gs.length), big: ds.filter(d => d.len >= BIG).length, len: st(ds.map(d => d.len)),
      stubs: stubs.length, stubLen: st(stubs.map(d => d.len)), stubDrop: sum(stubs, d => d.drop), stubEatUs: sum(stubs, d => d.eatUs || 0),
      reasons: ['W', 'S', 'O', 'A', 'H'].map(r => [r, ds.filter(d => d.reason === r).length]), noexit: ds.filter(d => d.tag === 'noexit').length,
      escapeSplits: esc.length, escapePerGame: r3(esc.length / gs.length), escapeParentLen: st(esc.map(s => s[1])) };
  };
  S.q3.trapped = { all: trapped(B), elim: trapped(byType(B, 'elim')), r500: trapped(byType(B, 'r500')), r1: trapped(O) };
  // 관문 구간별 우리 사망(판당 길이), 구간 시작 때 우리 유닛·최장
  S.q3.phases = Object.fromEntries([['all', B], ['r500', byType(B, 'r500')], ['r1', O]].map(([k, gs]) => [k, GATES.map(([r0, lab], i) => {
    const ds = gs.flatMap(us).filter(d => d.phase === i), live = gs.filter(g => g.rounds > r0);
    return { label: lab, games: live.length, deaths: ds.length, len: sum(ds, d => d.len), lenPerLiveGame: r3(live.length ? sum(ds, d => d.len) / live.length : NaN),
      byCls: Object.fromEntries(CLS2.map(c => [c, sum(ds.filter(d => d.cls2 === c), d => d.len)])),
      unitsAtStart: r3(mean(live.map(g => flowAt(g, 0, 'u', r0)))), longestAtStart: r3(mean(live.map(g => flowAt(g, 0, 'l', r0)))),
      theirLongestAtStart: r3(mean(live.map(g => flowAt(g, 1, 'l', r0)))), gatherTurnDeaths: ds.filter(d => indGather(d.ind)).length };
  })]));
  // 왕 먹이기(자해)와 떨군 진주의 행방
  const dropFate = (ds) => ({ n: ds.length, len: sum(ds, d => d.len), drop: sum(ds, d => d.drop), eatUs: sum(ds, d => d.eatUs || 0), eatThem: sum(ds, d => d.eatThem || 0),
    eatUs20: sum(ds, d => d.eatUs20 || 0), eatThem20: sum(ds, d => d.eatThem20 || 0), eatKingUs: sum(ds, d => d.eatKingUs || 0), eatKingThem: sum(ds, d => d.eatKingThem || 0) });
  S.q3.drops = {};
  for (const [k, gs] of [['all', B], ['elim', byType(B, 'elim')], ['r500', byType(B, 'r500')], ['r1win', O.filter(g => g.win)], ['r1loss', O.filter(g => !g.win)]]) {
    S.q3.drops[k] = { games: gs.length, ours: Object.fromEntries([...CLS2, 'total'].map(c => [c, dropFate(gs.flatMap(us).filter(d => c === 'total' || d.cls2 === c))])),
      theirs: Object.fromEntries([...THEM_CLS, 'total'].map(c => [c, dropFate(gs.flatMap(them).filter(d => c === 'total' || d.cls2 === c))])) };
  }
  // 먹은 진주 출처(판당): 자연(시작 배치 + 생성) / 자기 팀 주검 / 상대 주검, 그리고 질량 수지
  const eatSrc = (gs, si) => Object.fromEntries(['nat', 'own', 'opp'].map(k => [k, r3(mean(gs.map(g => sum(g.eat[si][k]))))]));
  const massRow = (gs, si) => ({ init: r3(mean(gs.map(g => g.mass[si].init))), ...eatSrc(gs, si), paid: r3(mean(gs.map(g => g.mass[si].paid))),
    deathLen: r3(mean(gs.map(g => g.mass[si].deathLen))), final: r3(mean(gs.map(g => g.mass[si].final))),
    deathByCls: Object.fromEntries((si === 0 ? CLS2 : THEM_CLS).map(c => [c, r3(mean(gs.map(g => sum(g.deaths.filter(d => d.side === si && d.cls2 === c), d => d.len))))])) });
  S.q3.mass = Object.fromEntries([['all', B], ['elim', byType(B, 'elim')], ['r500', byType(B, 'r500')], ['loss', B.filter(g => !g.win)], ['win', B.filter(g => g.win)],
    ['r1win', O.filter(g => g.win)], ['r1loss', O.filter(g => !g.win)]].map(([k, gs]) => [k, { games: gs.length, us: massRow(gs, 0), them: massRow(gs, 1) }]));
  // 상위권 참고: 팀·경기당 길이 6 이상 드래곤이 적에게 박혀 죽은 수, 박은 적 길이
  S.q3.topRammed = Object.fromEntries(['elim', 'r500'].map(t => [t, Object.fromEntries(['W', 'L'].map(wl => {
    const rows = top.filter(x => x.type === t), teams = rows.map(x => ({ team: x[wl], letter: x.winner === 'A' ? (wl === 'W' ? 'A' : 'B') : (wl === 'W' ? 'B' : 'A') }));
    const ds = teams.flatMap(({ team, letter }) => team.deaths.filter(d => d.reason === 'H' && !d.mover && d.byTeam !== letter));
    const big = ds.filter(d => d.len >= BIG);
    return [wl, { teamGames: teams.length, rammedPerGame: r3(ds.length / teams.length), bigPerGame: r3(big.length / teams.length), bigLenPerGame: r3(sum(big, d => d.len) / teams.length),
      bigAttLe3: big.filter(d => d.byLen <= SMALL).length, big: big.length,
      deathLenPerGame: r3(sum(teams, ({ team }) => sum(team.deaths, d => d.len)) / teams.length) }];
  }))]));

  // 탈출 분열 사슬: 탈출 분열로 태어난 자식이 다시 탈출 분열하면 같은 사슬. LOOP_MIN번 이상이면 '고리'.
  const LOOP_MIN = 5;
  const loopStats = gs => {
    const ch = gs.flatMap(g => g.chains.map(c => ({ ...c, gameId: g.gameId })));
    const loops = ch.filter(c => c.count >= LOOP_MIN), short = ch.filter(c => c.count < LOOP_MIN);
    const natAll = sum(gs, g => sum(g.eat[0].nat));
    return { games: gs.length, chains: ch.length, escapeSplits: sum(ch, c => c.count), loops: loops.length, gamesWithLoop: new Set(loops.map(c => c.gameId)).size,
      loopSplits: sum(loops, c => c.count), loopRoundsPerGame: r3(sum(loops, c => c.last - c.start + 2) / gs.length), loopNatPerGame: r3(sum(loops, c => c.nat) / gs.length),
      natPerGame: r3(natAll / gs.length), loopNatShare: natAll ? r3(sum(loops, c => c.nat) / natAll) : null,
      loopLen: st(loops.map(c => c.lenMedian)), loopStart: st(loops.map(c => c.start)), loopRounds: st(loops.map(c => c.last - c.start + 2)),
      shortChains: short.length, shortSplits: sum(short, c => c.count), shortLen: st(short.map(c => c.lenMedian)) };
  };
  const ex = B.find(g => g.gameId === 599313);
  S.loopExample = ex ? { gameId: ex.gameId, escapes: ex.splits[0].filter(x => x[5] === 'escape').slice(0, 4).map(x => ({ r: x[0], before: x[1], child: x[2], parent: x[6], childId: x[7] })),
    stubs: ex.deaths.filter(d => d.side === 0 && d.cls2 === 'stub').slice(0, 4).map(d => ({ r: d.r, id: d.id, len: d.len, bornLen: d.bornLen, drop: d.drop, eatUs: d.eatUs || 0, sinceEscape: d.sinceEscape })) } : null;
  S.loops = { all: loopStats(B), elim: loopStats(byType(B, 'elim')), r500: loopStats(byType(B, 'r500')), r1: loopStats(O),
    byMap: Object.fromEntries(MAPS.map(m => [m, loopStats(B.filter(g => g.map === m))])), r1ByMap: Object.fromEntries(MAPS.map(m => [m, loopStats(O.filter(g => g.map === m))])),
    list: B.flatMap(g => g.chains.filter(c => c.count >= LOOP_MIN).map(c => ({ gameId: g.gameId, map: g.map, opp: g.opp, win: g.win, init: g.init, ...c }))) };

  // ---- Q4 경제
  const eatWin = (gs, si) => Array.from({ length: NWIN }, (_, w) => { const live = gs.filter(g => g.rounds > w * WINLEN); return { n: live.length, mean: r3(mean(live.map(g => g.eat[si].nat[w] + g.eat[si].own[w] + g.eat[si].opp[w]))), nat: r3(mean(live.map(g => g.eat[si].nat[w]))) }; });
  const eatWinTop = (rows, wl) => Array.from({ length: NWIN }, (_, w) => { const live = rows.filter(x => x.rounds > w * WINLEN); return { n: live.length, mean: r3(mean(live.map(x => x[wl].eaten[w]))) }; });
  S.q4 = { eat: {}, splits: {} };
  for (const t of ['elim', 'r500']) {
    const gs = byType(B, t), rows = top.filter(x => x.type === t);
    S.q4.eat[t] = { us: eatWin(gs, 0), them: eatWin(gs, 1), topW: eatWinTop(rows, 'W'), topL: eatWinTop(rows, 'L'),
      r1win: eatWin(byType(O, t).filter(g => g.win), 0), r1loss: eatWin(byType(O, t).filter(g => !g.win), 0) };
  }
  const splitStats = sps => {
    const n = sps.length, ch = c => sps.filter(s => s[2] === c).length;
    return { n, child2: ch(2), child3: ch(3), child4: ch(4), child5p: sps.filter(s => s[2] >= 5).length, childMedian: r3(median(sps.map(s => s[2]))),
      parentBefore: r3(median(sps.map(s => s[1]))), byWin: Array.from({ length: NWIN }, (_, w) => sps.filter(s => win(s[0]) === w).length),
      fourTo22: sps.filter(s => s[1] === 4 && s[2] === 2).length, leader: sps.filter(s => s[4]).length };
  };
  for (const [k, gs] of [['all', B], ['elim', byType(B, 'elim')], ['r500', byType(B, 'r500')], ['r1', O]]) {
    const u = gs.flatMap(g => g.splits[0]), th = gs.flatMap(g => g.splits[1]);
    S.q4.splits[k] = { games: gs.length, us: { ...splitStats(u), perGame: r3(u.length / gs.length), policy: u.filter(s => s[5] === 'policy').length, escape: u.filter(s => s[5] === 'escape').length,
      firstSplit: st(gs.map(g => g.splits[0].length ? g.splits[0][0][0] : null).filter(x => x !== null)), noSplitGames: gs.filter(g => !g.splits[0].length).length },
      them: { ...splitStats(th), perGame: r3(th.length / gs.length), firstSplit: st(gs.map(g => g.splits[1].length ? g.splits[1][0][0] : null).filter(x => x !== null)) } };
  }
  for (const t of ['elim', 'r500']) {
    const rows = top.filter(x => x.type === t);
    for (const wl of ['W', 'L']) { const sp = rows.flatMap(x => x[wl].splits); S.q4.splits['top' + t + wl] = { games: rows.length, ...splitStats(sp), perGame: r3(sp.length / rows.length) }; }
  }
  // 지도별 경제: 먹은 진주(자연/전체), 드래곤 턴 100번당 먹이, 최대 수, r100 수, r300 몸길이 합, 정책 분열
  const allEat = (g, si) => sum(['nat', 'own', 'opp'], k => sum(g.eat[si][k]));
  const econ = gs => ({ n: gs.length, wins: gs.filter(g => g.win).length,
    natUs: r3(mean(gs.map(g => sum(g.eat[0].nat)))), natThem: r3(mean(gs.map(g => sum(g.eat[1].nat)))), allUs: r3(mean(gs.map(g => allEat(g, 0)))), allThem: r3(mean(gs.map(g => allEat(g, 1)))),
    turnsUs: r3(mean(gs.map(g => g.turns[0]))), turnsThem: r3(mean(gs.map(g => g.turns[1]))),
    natPer100Us: r3(100 * sum(gs, g => sum(g.eat[0].nat)) / sum(gs, g => g.turns[0])), natPer100Them: r3(100 * sum(gs, g => sum(g.eat[1].nat)) / sum(gs, g => g.turns[1])),
    allPer100Us: r3(100 * sum(gs, g => allEat(g, 0)) / sum(gs, g => g.turns[0])), allPer100Them: r3(100 * sum(gs, g => allEat(g, 1)) / sum(gs, g => g.turns[1])),
    unitsMaxUs: r3(median(gs.map(g => Math.max(...g.flow[0].u)))), unitsMaxThem: r3(median(gs.map(g => Math.max(...g.flow[1].u)))),
    units100: [r3(median(gs.filter(g => g.rounds > 100).map(g => flowAt(g, 0, 'u', 100)))), r3(median(gs.filter(g => g.rounds > 100).map(g => flowAt(g, 1, 'u', 100))))],
    total300: [r3(median(gs.filter(g => g.rounds > 300).map(g => flowAt(g, 0, 't', 300)))), r3(median(gs.filter(g => g.rounds > 300).map(g => flowAt(g, 1, 't', 300))))],
    policySplits: r3(mean(gs.map(g => g.splits[0].filter(x => x[5] === 'policy').length))), loopNat: r3(mean(gs.map(g => sum(g.chains.filter(c => c.count >= LOOP_MIN), c => c.nat)))),
    portalSteps: [r3(mean(gs.map(g => g.portalSteps[0]))), r3(mean(gs.map(g => g.portalSteps[1])))], portalDragons: [r3(mean(gs.map(g => g.portalDragons[0]))), r3(mean(gs.map(g => g.portalDragons[1])))] });
  S.q4.econ = { byMap: Object.fromEntries(MAPS.map(m => [m, econ(B.filter(g => g.map === m))])), elim: econ(byType(B, 'elim')), r500: econ(byType(B, 'r500')), all: econ(B),
    r1win: econ(O.filter(g => g.win)), r1loss: econ(O.filter(g => !g.win)), r1ByMap: Object.fromEntries(MAPS.map(m => [m, econ(O.filter(g => g.map === m))])) };
 // 시작 직후(0–9라운드) 길이 8 이상 드래곤의 분열: 판당 횟수와 자식 길이 2 비율(우리 / 상대)
  S.q4.earlyBig = Object.fromEntries(MAPS.map(m => { const gs = B.filter(g => g.map === m); const f = si => gs.flatMap(g => g.splits[si].filter(x => x[0] <= 9 && x[1] >= 8));
    const u = f(0), t = f(1); return [m, { games: gs.length, us: r3(u.length / gs.length), usEscape: u.filter(x => x[5] === 'escape').length, them: r3(t.length / gs.length), themChild2: t.filter(x => x[2] === 2).length, themN: t.length,
      themFirst: gs.map(g => g.splits[1].filter(x => x[0] <= 9 && x[1] >= 8).map(x => `${x[0]}/${x[1]}/${x[2]}`).join(' ')) }]; }));
 S.q4.region = Object.fromEntries(MAPS.map(m => { const gs = B.filter(g => g.map === m), x = f => r3(mean(gs.map(f)));
    return [m, { tiles: x(g => g.region.tiles), mapTiles: x(g => g.region.mapTiles), spawnTiles: x(g => g.region.spawnTiles), spawnTilesAll: x(g => g.region.spawnTilesAll), narrow: x(g => g.region.narrowSpawnTiles),
      spawnsIn: x(g => g.region.spawnsIn), spawnsOut: x(g => g.region.spawnsOut), usIn: x(g => g.region.natEat[0][0]), usOut: x(g => g.region.natEat[0][1]), themIn: x(g => g.region.natEat[1][0]), themOut: x(g => g.region.natEat[1][1]) }]; }));
  const ratio = gs => ({ turns: r3(sum(gs, g => g.turns[1]) / sum(gs, g => g.turns[0])), nat: r3(sum(gs, g => sum(g.eat[1].nat)) / sum(gs, g => sum(g.eat[0].nat))) });
  S.q4.ratios = { all: ratio(B), loss: ratio(B.filter(g => !g.win)), elim: ratio(byType(B, 'elim')), r500: ratio(byType(B, 'r500')) };
  S.q4.topEff = Object.fromEntries(['elim', 'r500'].map(t => [t, Object.fromEntries(['W', 'L'].map(wl => { const rows = top.filter(x => x.type === t);
    return [wl, { allPer100: r3(100 * sum(rows, x => sum(x[wl].eaten)) / sum(rows, x => x[wl].sonar.dragonRounds)), allPerGame: r3(mean(rows.map(x => sum(x[wl].eaten)))) }]; }))]));
  // 상대의 빈 이웃 자해(희생)와 우리 왕 먹이기: 100라운드 구간별 판당 건수·길이, 자기 팀·왕이 먹은 비율
  const sacr = (gs, si, pick) => [0, 1, 2, 3, 4].map(p => {
    const live = gs.filter(g => g.rounds > p * 100), ds = gs.flatMap(g => g.deaths.filter(d => d.side === si && pick(d) && Math.floor(d.r / 100) === p));
    const drop = sum(ds, d => d.drop), own = sum(ds, d => (si === 0 ? d.eatUs : d.eatThem) || 0), king = sum(ds, d => (si === 0 ? d.eatKingUs : d.eatKingThem) || 0), other = sum(ds, d => (si === 0 ? d.eatThem : d.eatUs) || 0);
    return { phase: `${p * 100}–${p * 100 + 99}`, games: live.length, perGame: r3(live.length ? ds.length / live.length : NaN), lenPerGame: r3(live.length ? sum(ds, d => d.len) / live.length : NaN), drop, own, king, other };
  });
  S.q3.sacrifice = { them: sacr(B, 1, d => d.cls2 === 'self-free'), themR500: sacr(byType(B, 'r500'), 1, d => d.cls2 === 'self-free'), usFeed: sacr(B, 0, d => d.cls2 === 'feed') };

  // ---- Q5 잘된 경기
  const story = g => {
    const cp = [20, 50, 100, 200, 300, 400, 450, 500].map(r => ({ r, us: [flowAt(g, 0, 'u', r), flowAt(g, 0, 't', r), flowAt(g, 0, 'l', r)], them: [flowAt(g, 1, 'u', r), flowAt(g, 1, 't', r), flowAt(g, 1, 'l', r)] }));
    const td = them(g), od = us(g);
    return { gameId: g.gameId, map: g.map, opp: g.opp, oppName: g.oppName, win: g.win, endReason: g.endReason, rounds: g.rounds, init: g.init, final: g.final, cp,
      ourDeaths: Object.fromEntries(CLS2.map(c => [c, [od.filter(d => d.cls2 === c).length, sum(od.filter(d => d.cls2 === c), d => d.len)]])),
      theirDeaths: Object.fromEntries(THEM_CLS.map(c => [c, [td.filter(d => d.cls2 === c).length, sum(td.filter(d => d.cls2 === c), d => d.len)]])),
      theirBig: td.filter(d => d.len >= BIG).map(d => [d.r, d.len, d.cls2]), ourBig: od.filter(d => d.len >= BIG).map(d => [d.r, d.len, d.cls2]),
      eat: [0, 1].map(si => sum(['nat', 'own', 'opp'], k => sum(g.eat[si][k]))), peak: g.peak, splits: [g.splits[0].length, g.splits[1].length], ind: g.ind,
      lastLed: Object.fromEntries(MEAS.map(([m]) => [m, lastLed(r => [flowAt(g, 0, m, r), flowAt(g, 1, m, r)], g.rounds, 1)])),
      theirLastLed: Object.fromEntries(MEAS.map(([m]) => [m, lastLed(r => [flowAt(g, 1, m, r), flowAt(g, 0, m, r)], g.rounds, 1)])) };
  };
  S.q5 = { wins: B.filter(g => g.win).map(story), autarky: B.filter(g => g.map === 'Autarky').map(story), pd: B.filter(g => g.map === 'Prisoners Dilemma').map(story) };
  const r1Profile = gs => ({ n: gs.length, oppElo: st(gs.map(g => g.oppElo).filter(Number.isFinite)), elimUs: gs.filter(g => !g.win && g.endReason === 'teamEliminated').length,
    elimThem: gs.filter(g => g.win && g.endReason === 'teamEliminated').length, roundLimit: gs.filter(g => g.endReason === 'roundLimit').length,
    maps: Object.fromEntries(MAPS.map(m => [m, gs.filter(g => g.map === m).length])),
    themUnits100: r3(median(gs.filter(g => g.rounds > 100).map(g => flowAt(g, 1, 'u', 100)))), themSplits: r3(mean(gs.map(g => g.splits[1].length))),
    finalLongest: [r3(median(gs.map(g => g.final[0].longest))), r3(median(gs.map(g => g.final[1].longest)))], eat: [r3(mean(gs.map(g => sum(['nat', 'own', 'opp'], k => sum(g.eat[0][k]))))), r3(mean(gs.map(g => sum(['nat', 'own', 'opp'], k => sum(g.eat[1][k])))))],
    ourBigRammedPerGame: r3(gs.flatMap(us).filter(d => d.cls2 === 'H-rammed' && d.len >= BIG).length / gs.length),
    theirKilledByUsPerGame: r3(gs.flatMap(them).filter(d => d.cls2 === 'H-rammed' || d.cls2 === 'O-enemy').length / gs.length),
    theirBigKilledByUs: r3(gs.flatMap(them).filter(d => (d.cls2 === 'H-rammed' || d.cls2 === 'O-enemy') && d.len >= BIG).length / gs.length) });
  S.q5.r1 = { win: r1Profile(O.filter(g => g.win)), loss: r1Profile(O.filter(g => !g.win)), winMaps: Object.fromEntries(MAPS.map(m => [m, [O.filter(g => g.map === m && g.win).length, O.filter(g => g.map === m).length]])) };
  // r1: 상대 Elo 구간별 승률
  const bands = [[0, 1500], [1500, 1600], [1600, 1700], [1700, 1800], [1800, 3000]];
  S.q5.r1.eloBands = bands.map(([a, b]) => { const gs = O.filter(g => g.oppElo >= a && g.oppElo < b); return { band: `${a}–${b - 1}`, n: gs.length, wins: gs.filter(g => g.win).length }; });

  // ---- Q6 상대별
  const topTeam = name => { // 그 팀이 상위권 경기에서 보인 모습
    const rows = top.filter(x => x.teams.A.name === name || x.teams.B.name === name);
    const mine = rows.map(x => ({ row: x, t: x.teams.A.name === name ? x.A : x.B, won: (x.teams.A.name === name) === (x.winner === 'A') }));
    const u = r => r3(median(mine.filter(m => m.row.rounds > r).map(m => tlAt(m.t, r).units)));
    return { games: rows.length, wins: mine.filter(m => m.won).length, units50: u(50), units100: u(100), units200: u(200), splitsPerGame: r3(mean(mine.map(m => m.t.splits.length))),
      child2: pc(sum(mine, m => m.t.splits.filter(s => s[2] === 2).length), sum(mine, m => m.t.splits.length)),
      eat100: r3(mean(mine.map(m => m.t.eaten[0] + m.t.eaten[1]))), elimWins: mine.filter(m => m.won && m.row.endReason === 'teamEliminated').length };
  };
  S.q6 = OPPS.map(o => {
    const gs = B.filter(g => g.opp === o), name = oppName(o);
    const elim = gs.filter(g => !g.win && g.endReason === 'teamEliminated');
    const lastDeaths = elim.map(g => { const od = us(g); const last = od.filter(d => d.r === g.rounds - 1); return last.map(d => d.cls2); }).flat();
    const rm = gs.flatMap(us).filter(d => d.cls === 'H-rammed');
    const u = r => r3(median(gs.filter(g => g.rounds > r).map(g => flowAt(g, 1, 'u', r))));
    const uu = r => r3(median(gs.filter(g => g.rounds > r).map(g => flowAt(g, 0, 'u', r))));
    const drops = gs.flatMap(us);
    return { opp: o, name, n: gs.length, wins: gs.filter(g => g.win).length, elim: elim.length, elimRound: st(elim.map(g => g.rounds - 1)), roundLimit: gs.filter(g => g.endReason === 'roundLimit').length,
      themUnits: [u(20), u(50), u(100), u(200)], usUnits: [uu(20), uu(50), uu(100), uu(200)], themSplitsPerGame: r3(mean(gs.map(g => g.splits[1].length))),
      themChild2: pc(gs.flatMap(g => g.splits[1]).filter(s => s[2] === 2).length, gs.flatMap(g => g.splits[1]).length),
      rammedPerGame: r3(rm.length / gs.length), rammedBigPerGame: r3(rm.filter(d => d.len >= BIG).length / gs.length),
      rammedLenPerGame: r3(sum(rm, d => d.len) / gs.length), attLe3: pc(rm.filter(d => d.by && d.by.len <= SMALL).length, rm.length), attSprint: pc(rm.filter(d => d.by && d.by.steps >= 2).length, rm.length),
      ourLenByCls: Object.fromEntries(CLS2.map(c => [c, r3(sum(gs.flatMap(us).filter(d => d.cls2 === c), d => d.len) / gs.length)])),
      theirLenByCls: Object.fromEntries(THEM_CLS.map(c => [c, r3(sum(gs.flatMap(them).filter(d => d.cls2 === c), d => d.len) / gs.length)])),
      ourDropsEatenByThem: pc(sum(drops, d => d.eatThem || 0), sum(drops, d => d.drop)), ourDropsEatenByUs: pc(sum(drops, d => d.eatUs || 0), sum(drops, d => d.drop)),
      eat: [r3(mean(gs.map(g => sum(['nat', 'own', 'opp'], k => sum(g.eat[0][k]))))), r3(mean(gs.map(g => sum(['nat', 'own', 'opp'], k => sum(g.eat[1][k])))))],
      themSelfFreePerGame: r3(gs.flatMap(them).filter(d => d.cls2 === 'self-free').length / gs.length),
      lastDeathCls: Object.fromEntries(CLS2.map(c => [c, lastDeaths.filter(x => x === c).length])),
      finalLimit: gs.filter(g => g.endReason === 'roundLimit').map(g => [g.map, g.final[0].longest, g.final[1].longest, g.win]),
      topRef: topTeam(name) };
  });

  // ---- Q7 손실원 순위(진 64판, 판당)
  const lost = B.filter(g => !g.win);
  const lossLen = CLS2.map(c => ({ src: c, lenPerGame: r3(sum(lost.flatMap(us).filter(d => d.cls2 === c), d => d.len) / lost.length),
    lenPerGameBig: r3(sum(lost.flatMap(us).filter(d => d.cls2 === c && d.len >= BIG), d => d.len) / lost.length),
    games: lost.filter(g => us(g).some(d => d.cls2 === c)).length }));
  const eatGap = { us: r3(mean(lost.map(g => sum(['nat', 'own', 'opp'], k => sum(g.eat[0][k]))))), them: r3(mean(lost.map(g => sum(['nat', 'own', 'opp'], k => sum(g.eat[1][k]))))),
    usNat: r3(mean(lost.map(g => sum(g.eat[0].nat)))), themNat: r3(mean(lost.map(g => sum(g.eat[1].nat)))) };
  // 500라운드 판정으로 진 판: 우리 최장 드래곤(생애 최고)의 운명
  const limLost = lost.filter(g => g.endReason === 'roundLimit');
  // 팀 최장 곡선의 최고점(탈출 분열로 id가 바뀌어도 이어진다)과 길이 6 이상 우리 사망
  const peakFate = limLost.map(g => { const l = g.flow[0].l, pk = Math.max(...l), lt = g.flow[1].l;
    return { gameId: g.gameId, map: g.map, opp: g.opp, peak: pk, peakR: l.indexOf(pk), finalUs: g.final[0].longest, finalThem: g.final[1].longest, themPeak: Math.max(...lt),
      us300: flowAt(g, 0, 'l', 300), them300: flowAt(g, 1, 'l', 300), tot300: [flowAt(g, 0, 't', 300), flowAt(g, 1, 't', 300)],
      big: us(g).filter(d => d.len >= BIG).map(d => [d.r, d.len, d.cls2]) }; });
  // 전멸로 진 판: 우리 사망(탈출 조각 제외) 순서
  const elimSeq = lost.filter(g => g.endReason === 'teamEliminated').map(g => ({ gameId: g.gameId, map: g.map, opp: g.opp, end: g.rounds - 1, init: g.init[0],
    seq: us(g).filter(d => d.cls2 !== 'stub').map(d => [d.r, d.len, d.cls2, d.by ? d.by.len : null, d.by ? d.by.steps : null]) }));
  S.q7 = { lossLen, eatGap, sprintPaid: r3(mean(lost.map(g => g.mass[0].paid))), sprintPaidThem: r3(mean(lost.map(g => g.mass[1].paid))), peakFate, elimSeq,
    elimLastCls: Object.fromEntries(CLS2.map(c => [c, elimSeq.filter(x => x.seq.length && x.seq[x.seq.length - 1][2] === c).length])),
    elimRammedShare: { rammed: sum(elimSeq, x => x.seq.filter(d => d[2] === 'H-rammed').length), all: sum(elimSeq, x => x.seq.length),
      rammedLen: sum(elimSeq, x => sum(x.seq.filter(d => d[2] === 'H-rammed'), d => d[1])), allLen: sum(elimSeq, x => sum(x.seq, d => d[1])) },
    elimLost: lost.filter(g => g.endReason === 'teamEliminated').length, limLost: limLost.length };
  return S;
}

// ---------------------------------------------------------------------------------------------------------------
// 보고서(표준 출력). research/experiments/online-baseline-r1.md의 수치는 모두 여기서 나온다.
function report(S) {
  const out = [], P = s => out.push(s);
  P(`# baseline_study 집계 (node tools/baseline_study.js)`);
  P(`기준점 ${S.sets.baseline.games}판 ${S.sets.baseline.wins}승, r1-online(제출 ${OWN_SUB}) ${S.sets.r1.games}판 ${S.sets.r1.wins}승, 상위권끼리 ${S.sets.top.games}판.`);
  P('검증(모두 0이어야 함): ' + JSON.stringify(S.checks));
  P('');
  P('우리 봇 지표(판당 턴 수): ' + Object.entries(S.indicators).map(([k, x]) => `${k} ` + Object.entries(x).map(([a, b]) => `${a} ${fx(b, 1)}`).join(', ')).join(' / '));
  P('');
  P('## Q1 끝나는 모습');
  const endHead = ['묶음', '판', '승', '우리 전멸', '상대 전멸', '500라운드(승)', '우리 전멸 라운드 중앙값 [사분위] (최소–최대)', '끝 최장 우리:상대', '끝 몸길이 합', '끝 수', '500라운드 판 끝 최장 중앙값 우리:상대'];
  const endLine = (k, x) => [k, x.n, x.wins, x.elimUs, x.elimThem, `${x.roundLimit}(${x.roundLimitWins})`, x.elimRound.n ? `${fx(x.elimRound.median, 0)} [${fx(x.elimRound.q1, 0)}–${fx(x.elimRound.q3, 0)}] (${x.elimRound.min}–${x.elimRound.max})` : '-',
    `${fx(x.final.us.longest)}:${fx(x.final.them.longest)}`, `${fx(x.final.us.total, 0)}:${fx(x.final.them.total, 0)}`, `${fx(x.final.us.units)}:${fx(x.final.them.units)}`,
    x.roundLimit ? `${fx(x.finalLimit.us, 0)}:${fx(x.finalLimit.them, 0)}` : '-'];
  P(table(endHead, [...OPPS.map(o => endLine(`${o} ${S.q1.byOpp[o].name}`, S.q1.byOpp[o])), endLine('전멸형 지도', S.q1.byType.elim), endLine('500라운드형 지도', S.q1.byType.r500), endLine('전체', S.q1.all)]));
  P('');
  P(table(endHead, MAPS.map(m => endLine(m, S.q1.byMap[m]))));
  P('');
  P('### 상대 × 지도 (W/L, 전멸이면 끝 라운드, 500이면 끝 최장 우리:상대)');
  P(table(['상대', ...MAPS], OPPS.map(o => [`${o}`, ...MAPS.map(m => { const g = S.q1.grid.find(x => x.opp === o && x.map === m); if (!g) return '-'; return (g.win ? 'W ' : 'L ') + (g.endReason === 'teamEliminated' ? `r${g.rounds - 1}` : `${g.final[0].longest}:${g.final[1].longest}`); })])));
  P('');
  P('Prisoners Dilemma 시작 드래곤 수(우리/상대): ' + S.q1.pdVariants.map(x => `${x.opp} ${x.init[0]}/${x.init[1]}${x.win ? ' W' : ''}`).join(', '));
  P('Prisoners Dilemma 판본별: ' + S.q1.pdTally.map(x => `${x.init}마리 ${x.games}판 ${x.wins}승 (전멸 ${x.elim})`).join(', '));
  P('');

  P('## Q2 뒤지는 시점 (중앙값; 그 라운드에 진행 중인 판만. 상위권은 10라운드 간격)');
  for (const t of ['elim', 'r500']) for (const [m, , ko] of MEAS) {
    P(`### ${TYPE_KO[t]} — ${ko}`);
    P(table(['라운드', '기준점 판', '우리', '상대', '우리 평균', '상대 평균', '상위 판', '상위 승자', '상위 패자'], S.q2.curves[t][m].map(x => [x.r, x.n, fx(x.us), fx(x.them), fx(x.usMean), fx(x.themMean), x.nTop ?? '-', fx(x.topW), fx(x.topL)])));
    P('');
  }
  P('### 진 판에서 우리가 마지막으로 앞선 라운드 (중앙값 [사분위], 한 번도 앞서지 못한 판) / 상위권 패자(10라운드 간격)');
  P(table(['지도 종류', '척도', '진 판', '매 라운드', '10라운드 간격', '상위권 패자', '끝까지 뒤진 첫 라운드(매 라운드)'], ['elim', 'r500'].flatMap(t => MEAS.map(([m, , ko]) => {
    const x = S.q2.lastLed[t][m], b = S.q2.behind[t][m];
    return [TYPE_KO[t], ko, x.n, `${fx(x.perRound.median, 0)} [${fx(x.perRound.q1, 0)}–${fx(x.perRound.q3, 0)}], 없음 ${x.neverPerRound}`, `${fx(x.step10.median, 0)} [${fx(x.step10.q1, 0)}–${fx(x.step10.q3, 0)}], 없음 ${x.never10}`,
      `${fx(x.top.median, 0)} [${fx(x.top.q1, 0)}–${fx(x.top.q3, 0)}], 없음 ${x.topNever}/${x.topN}`, `${fx(b.median, 0)} [${fx(b.q1, 0)}–${fx(b.q3, 0)}] (${b.n})`];
  }))));
  P('');
  P('최고점: ' + ['elim', 'r500'].map(t => { const x = S.q2.peak[t]; return `${TYPE_KO[t]} 우리 최장 최고 중앙값 ${fx(x.usPeak.median, 0)}(그 라운드 중앙값 ${fx(x.usPeakRound.median, 0)}), 상대 최장 최고 ${fx(x.themPeak.median, 0)}, 우리 최대 수 ${fx(x.usUnitsMax.median, 0)}, 상대 최대 수 ${fx(x.themUnitsMax.median, 0)}`; }).join(' / '));
  P('');
  for (const t of ['elim', 'r500']) {
    P(`### r1-online ${TYPE_KO[t]}: 이긴 판 / 진 판 (우리:상대 중앙값)`);
    P(table(['라운드', '승 판', '승: 수', '승: 합', '승: 최장', '패 판', '패: 수', '패: 합', '패: 최장'], CHECK_R.filter(r => [20, 50, 100, 200, 300, 400, 450, 500].includes(r)).map(r => {
      const f = (wl, m) => S.q2.r1Curves[t][wl][m].find(x => x.r === r);
      return [r, f('win', 'u').n, `${fx(f('win', 'u').us)}:${fx(f('win', 'u').them)}`, `${fx(f('win', 't').us, 0)}:${fx(f('win', 't').them, 0)}`, `${fx(f('win', 'l').us)}:${fx(f('win', 'l').them)}`,
        f('loss', 'u').n, `${fx(f('loss', 'u').us)}:${fx(f('loss', 'u').them)}`, `${fx(f('loss', 't').us, 0)}:${fx(f('loss', 't').them, 0)}`, `${fx(f('loss', 'l').us)}:${fx(f('loss', 'l').them)}`];
    })));
    P('');
  }

  P('## Q3 질량을 잃는 방식');
  P('### 우리 사망 분류 (판당 횟수 / 판당 잃은 길이 / 길이 6 이상 판당 횟수)');
  const grp = ['all', 'elim', 'r500', 'loss', 'win', 'r1win', 'r1loss'], grpKo = { all: '기준점 전체', elim: '기준점 전멸형', r500: '기준점 500형', loss: '기준점 진 판', win: '기준점 이긴 판', r1win: 'r1 이긴 판', r1loss: 'r1 진 판' };
  P(table(['분류', ...grp.map(k => grpKo[k])], [...CLS2, 'total'].map(c => [c === 'total' ? '합계' : `${CLS2_KO[c]}`, ...grp.map(k => { const x = S.q3.ourDeaths[k][c]; return `${fx(x.perGame)} / ${fx(x.lenPerGame)} / ${fx(x.bigPerGame, 2)}`; })])));
  P('');
  P('### 상대 사망 분류 (판당 횟수 / 판당 잃은 길이 / 길이 6 이상 판당 횟수)');
  P(table(['분류', ...grp.map(k => grpKo[k])], [...THEM_CLS, 'total'].map(c => [c === 'total' ? '합계' : THEM_KO[c], ...grp.map(k => { const x = S.q3.theirDeaths[k][c]; return `${fx(x.perGame)} / ${fx(x.lenPerGame)} / ${fx(x.bigPerGame, 2)}`; })])));
  P('');
  P('### 질량 수지 (판당 평균): 시작 + 먹이(자연/자기 팀 주검/상대 주검) − 질주 비용 − 사망 = 끝');
  P(table(['묶음', '판', '쪽', '시작', '+자연', '+자기 주검', '+상대 주검', '−질주', '−사망', '=끝', '사망 길이 분류별'], Object.entries(S.q3.mass).flatMap(([k, x]) => [0, 1].map(si => {
    const r = si === 0 ? x.us : x.them;
    return [grpKo[k] || k, x.games, si === 0 ? '우리' : '상대', fx(r.init), fx(r.nat), fx(r.own), fx(r.opp), fx(r.paid), fx(r.deathLen), fx(r.final),
      Object.entries(r.deathByCls).filter(([, v]) => v >= 0.5).map(([c, v]) => `${c} ${fx(v)}`).join(', ')];
  }))));
  P('');
  P('### 적이 우리 머리를 박은 사망 (H-rammed) 세부');
  const rh = ['묶음', '건', '판당', '판당 길이', '우리 길이 중앙값', '우리 최장이었음', '박은 적 길이 <=2/3/4–5/6+', '적이 분열 조각(태어날 때 <=3)', '적 걸음 1/2/3+', '결정 기록 있음', '결정 때 적 존재', '결정 때 7x7 안', '체비쇼프 <=1/2/3/4–5/6+',
    '결정 전 머리가 적 도달 안', '행동 뒤 머리가 적 도달 안', '도달 밖→안으로 들어감', '도달 안에 머묾', '적 도달 밖 한 걸음 있었음', '그중 넓은 칸(>=L+2)', '모든 적 도달 밖 한 걸음 있었음', '그중 넓은 칸', '행동 뒤 모든 적 도달 밖',
    '행동 뒤 적까지 BFS 1/2/3/4/5+/닿지 않음', '결정 때 빈 이웃 0/1', '결정 때 우리 질주', '결정 때 진주 먹음', '모이기(g) 중', '지표 v 중앙값'];
  const rrow = (k, x) => [k, x.n, fx(x.perGame, 2), fx(x.lenPerGame, 1), fx(x.ourLen.median, 0), x.leader, `${x.attLen.le2}/${x.attLen.l3}/${x.attLen.l45}/${x.attLen.ge6} (<=3 ${pc(x.attLen.le2 + x.attLen.l3, x.n)})`, `${x.attFromSplit} (${x.attBornLe3}) ${pc(x.attFromSplit, x.n)}`,
    `${x.attSteps.s1}/${x.attSteps.s2}/${x.attSteps.s3} (2+ ${pc(x.attSteps.s2 + x.attSteps.s3, x.n)})`, x.withDecision, x.present, `${x.seen} (${pc(x.seen, x.present)})`, `${x.cheb.le1}/${x.cheb.c2}/${x.cheb.c3}/${x.cheb.c45}/${x.cheb.ge6}`,
    `${x.preInReach}/${x.inSnap}`, `${x.postInReach}/${x.inSnap}`, x.entered, x.stayed, `${x.outStep} (${pc(x.outStep, x.inSnap)})`, `${x.outViable} (${pc(x.outViable, x.inSnap)})`, `${x.safeStep} (${pc(x.safeStep, x.withDecision)})`, `${x.viableSafe} (${pc(x.viableSafe, x.withDecision)})`, `${x.postSafe}`,
    `${x.dPost.d1}/${x.dPost.d2}/${x.dPost.d3}/${x.dPost.d4}/${x.dPost.d5}/${x.dPost.none}`, `${x.decFree0}/${x.decFree1}`, x.decSprint, x.decEat, x.gather, fx(x.value.median, 1)];
  P(table(rh, ['all', 'elim', 'r500', 'r1'].flatMap(k => [['big', '길이>=6'], ['small', '길이<6']].map(([s, ko]) => rrow(`${k} ${ko}`, S.q3.rammed[k][s])))));
  P('');
  P('H-rammed 길이>=6, 관문 구간별 건수: ' + ['all', 'r1'].map(k => `${k} ` + S.q3.rammed[k].big.phase.map((n, i) => `${GATES[i][1]} ${n}`).join(', ')).join(' / '));
  P('');
  P('### 상위권 참고: 팀·경기당 적에게 머리를 박혀 죽은 수');
  P(table(['지도 종류', '쪽', '팀·경기', '박혀 죽음/판', '길이>=6 박혀 죽음/판', '그 길이/판', '길이>=6 중 박은 적 <=3', '전체 사망 길이/판'], ['elim', 'r500'].flatMap(t => ['W', 'L'].map(wl => {
    const x = S.q3.topRammed[t][wl]; return [TYPE_KO[t], wl === 'W' ? '승자' : '패자', x.teamGames, fx(x.rammedPerGame, 1), fx(x.bigPerGame, 2), fx(x.bigLenPerGame, 1), `${x.bigAttLe3}/${x.big}`, fx(x.deathLenPerGame, 1)];
  }))));
  P('');
  P('### 갇힘(움직여 죽을 때 빈 이웃 0)과 탈출 분열');
  P(table(['묶음', '탈출 조각 사망', '조각 길이 중앙값', '조각 진주 떨굼/우리가 먹음', '그 밖의 갇힘 건', '판당', '판당 길이', '길이>=6', '원인 W/S/O/A/H', 'no-exit 지표', '탈출 분열 판당', '탈출 분열 전 길이 중앙값'], ['all', 'elim', 'r500', 'r1'].map(k => {
    const x = S.q3.trapped[k]; return [k, x.stubs, fx(x.stubLen.median, 0), `${x.stubDrop}/${x.stubEatUs}`, x.n, fx(x.perGame, 2), fx(x.lenPerGame, 1), x.big, x.reasons.map(r => r[1]).join('/'), x.noexit, fx(x.escapePerGame, 2), fx(x.escapeParentLen.median, 0)];
  })));
  P('');
  P('### 탈출 분열 사슬 (자식이 다시 탈출 분열하면 같은 사슬, 5번 이상이면 고리)');
  const lp = (k, x) => [k, x.games, x.escapeSplits, x.chains, x.loops, x.gamesWithLoop, x.loopSplits, fx(x.loopRoundsPerGame, 0), `${fx(x.loopRounds.median, 0)} [${x.loopRounds.min ?? '-'}–${x.loopRounds.max ?? '-'}]`,
    fx(x.loopStart.median, 0), fx(x.loopLen.median, 0), fx(x.loopNatPerGame, 1), fx(x.natPerGame, 1), x.loopNatShare !== null ? pc(x.loopNatShare, 1) : '-', x.shortChains, x.shortSplits];
  P(table(['묶음', '판', '탈출 분열', '사슬', '고리', '고리 있는 판', '고리 속 분열', '판당 고리 라운드', '고리 길이(라운드) 중앙값 [최소–최대]', '고리 시작 라운드 중앙값', '고리 드래곤 길이 중앙값', '판당 고리가 먹은 자연 진주', '판당 우리 자연 진주', '고리 비중', '짧은 사슬', '짧은 사슬 분열'],
    [lp('기준점', S.loops.all), lp('전멸형', S.loops.elim), lp('500형', S.loops.r500), lp('r1', S.loops.r1), ...MAPS.map(m => lp(m, S.loops.byMap[m])), ...MAPS.map(m => lp('r1 ' + m, S.loops.r1ByMap[m]))]));
  if (S.loopExample) P(`고리 예(${S.loopExample.gameId}): 탈출 분열 ` + S.loopExample.escapes.map(x => `r${x.r} 부모 ${x.parent} ${x.before}→자식 ${x.childId} ${x.child}`).join(', ') +
    ' / 탈출 조각 사망 ' + S.loopExample.stubs.map(x => `r${x.r} id ${x.id} 길이 ${x.len} 떨굼 ${x.drop} 우리가 먹음 ${x.eatUs} (탈출 분열 뒤 ${x.sinceEscape}라운드)`).join(', '));
  P('고리 목록(기준점): ' + S.loops.list.map(c => `${c.gameId} ${c.map} ${c.opp}${c.win ? 'W' : ''} 시작수${c.init[0]} r${c.start}–${c.last} ${c.count}회 L${c.lenMedian} 자연${c.nat} 머리(${c.head.join(',')})`).join('; '));
  P('');
  P('### 관문 구간별 우리 사망 길이 (구간에 살아 있던 판 기준)');
  for (const k of ['all', 'r500', 'r1']) {
    P(`#### ${k}`);
    P(table(['구간', '판', '사망', '길이', '판당 길이', '분류별 길이', '구간 시작 우리 수', '구간 시작 우리 최장', '구간 시작 상대 최장', '모이기(g) 중 사망'], S.q3.phases[k].map(x => [x.label, x.games, x.deaths, x.len, fx(x.lenPerLiveGame, 1),
      Object.entries(x.byCls).filter(([, v]) => v).map(([c, v]) => `${c} ${v}`).join(', '), fx(x.unitsAtStart, 1), fx(x.longestAtStart, 1), fx(x.theirLongestAtStart, 1), x.gatherTurnDeaths])));
    P('');
  }
  P('### 떨어진 진주의 행방 (합계): 떨어짐 / 우리가 먹음(20라운드 안) / 상대가 먹음(20라운드 안) / 우리 최장이 먹음');
  for (const k of ['all', 'elim', 'r500', 'r1win', 'r1loss']) {
    const x = S.q3.drops[k];
    P(`#### ${k} (${x.games}판)`);
    P(table(['죽은 쪽', '분류', '사망', '길이', '떨어진 진주', '우리 먹음(20라운드 안) 비율', '상대 먹음(20라운드 안) 비율', '안 먹힘', '우리 최장이 먹음'], [
      ...[...CLS2, 'total'].map(c => { const y = x.ours[c]; return ['우리', c, y.n, y.len, y.drop, `${y.eatUs} (${y.eatUs20}) ${pc(y.eatUs, y.drop)}`, `${y.eatThem} (${y.eatThem20}) ${pc(y.eatThem, y.drop)}`, y.drop - y.eatUs - y.eatThem, `${y.eatKingUs} ${pc(y.eatKingUs, y.drop)}`]; }).filter(r => r[2]),
      ...[...THEM_CLS, 'total'].map(c => { const y = x.theirs[c]; return ['상대', c, y.n, y.len, y.drop, `${y.eatUs} (${y.eatUs20}) ${pc(y.eatUs, y.drop)}`, `${y.eatThem} (${y.eatThem20}) ${pc(y.eatThem, y.drop)}`, y.drop - y.eatUs - y.eatThem, y.eatKingUs]; }).filter(r => r[2])]));
    P('');
  }

  P('### 상대의 빈 이웃 자해(희생)와 우리 왕 먹이기 (100라운드 구간, 판당, 떨어진 진주 중 자기 팀/왕/상대가 먹은 수)');
  const sr = (k, xs) => xs.map(x => [k, x.phase, x.games, fx(x.perGame, 1), fx(x.lenPerGame, 1), x.drop, `${x.own} (${pc(x.own, x.drop)})`, `${x.king} (${pc(x.king, x.drop)})`, `${x.other} (${pc(x.other, x.drop)})`]);
  P(table(['쪽', '구간', '판', '판당 건', '판당 길이', '떨어진 진주', '자기 팀이 먹음', '자기 팀 최장이 먹음', '상대가 먹음'], [...sr('상대 자해(전체)', S.q3.sacrifice.them), ...sr('상대 자해(500형)', S.q3.sacrifice.themR500), ...sr('우리 왕 먹이기', S.q3.sacrifice.usFeed)]));
  P('');

  P('## Q4 경제');
  P('### 지도별 먹이와 수 (기준점 판당; 턴당은 드래곤 턴 100번당)');
  const ec = (k, x) => [k, x.n, x.wins, `${fx(x.natUs, 0)}:${fx(x.natThem, 0)}`, `${fx(x.allUs, 0)}:${fx(x.allThem, 0)}`, `${fx(x.turnsUs, 0)}:${fx(x.turnsThem, 0)}`, `${fx(x.natPer100Us, 1)}:${fx(x.natPer100Them, 1)}`,
    `${fx(x.allPer100Us, 1)}:${fx(x.allPer100Them, 1)}`, `${fx(x.unitsMaxUs, 0)}:${fx(x.unitsMaxThem, 0)}`, `${fx(x.units100[0], 0)}:${fx(x.units100[1], 0)}`, `${fx(x.total300[0], 0)}:${fx(x.total300[1], 0)}`, fx(x.policySplits, 1), fx(x.loopNat, 0),
    `${fx(x.portalSteps[0], 1)}:${fx(x.portalSteps[1], 0)}`, `${fx(x.portalDragons[0], 1)}:${fx(x.portalDragons[1], 0)}`];
  const ecHead = ['묶음', '판', '승', '자연 진주 우리:상대', '전체 먹이', '드래곤 턴', '자연/100턴', '전체/100턴', '최대 수', 'r100 수', 'r300 몸길이 합', '우리 정책 분열/판', '고리가 먹은 자연', '포털 통과 걸음', '포털 지난 드래곤'];
  P(table(ecHead, [...MAPS.map(m => ec(m, S.q4.econ.byMap[m])), ec('전멸형', S.q4.econ.elim), ec('500형', S.q4.econ.r500), ec('전체', S.q4.econ.all), ec('r1 이긴 판', S.q4.econ.r1win), ec('r1 진 판', S.q4.econ.r1loss)]));
  P('');
  P(table(ecHead, MAPS.map(m => ec('r1 ' + m, S.q4.econ.r1ByMap[m]))));
  P('시작 직후(r0–9) 길이 8 이상 드래곤의 분열(판당, 우리 중 탈출 / 상대 중 자식 2): ' + MAPS.filter(m => S.q4.earlyBig[m].us || S.q4.earlyBig[m].them).map(m => { const x = S.q4.earlyBig[m]; return `${m} 우리 ${fx(x.us, 1)}(탈출 ${x.usEscape}) 상대 ${fx(x.them, 1)}(자식 2 ${x.themChild2}/${x.themN})`; }).join(', '));
  P('Autarky 상대의 r0–9 긴 드래곤 분열(라운드/부모/자식): ' + S.q4.earlyBig.Autarky.themFirst.map((x, i) => `[${x}]`).join(' '));
  P('Prisoners Dilemma 상대의 r0–9 긴 드래곤 분열: ' + S.q4.earlyBig['Prisoners Dilemma'].themFirst.map(x => `[${x}]`).join(' '));
  P('드래곤 턴 비(상대/우리), 자연 진주 비(상대/우리): ' + Object.entries(S.q4.ratios).map(([k, x]) => `${k} ${fx(x.turns, 1)}, ${fx(x.nat, 1)}`).join(' / '));
  P('');
  P('### 우리 시작 영역(포털 없이 닿는 칸)과 자연 진주 (판당 평균)');
  P(table(['지도', '영역 칸/지도 칸', '영역 안 진주 칸(열린 이웃 2 이하)/지도 전체 진주 칸', '생성 영역 안/밖', '우리가 먹은 자연 안/밖', '상대가 먹은 자연 안/밖'], MAPS.map(m => { const x = S.q4.region[m];
    return [m, `${fx(x.tiles, 0)}/${fx(x.mapTiles, 0)}`, `${fx(x.spawnTiles, 1)}(${fx(x.narrow, 1)})/${fx(x.spawnTilesAll, 1)}`, `${fx(x.spawnsIn, 0)}/${fx(x.spawnsOut, 0)}`, `${fx(x.usIn, 1)}/${fx(x.usOut, 1)}`, `${fx(x.themIn, 1)}/${fx(x.themOut, 1)}`]; })));
  P('');
  P('상위권 먹이(전체/100턴, 판당): ' + ['elim', 'r500'].map(t => `${TYPE_KO[t]} 승자 ${fx(S.q4.topEff[t].W.allPer100, 1)} (${fx(S.q4.topEff[t].W.allPerGame, 0)}), 패자 ${fx(S.q4.topEff[t].L.allPer100, 1)} (${fx(S.q4.topEff[t].L.allPerGame, 0)})`).join(' / '));
  P('');
  for (const t of ['elim', 'r500']) {
    const x = S.q4.eat[t];
    P(`### ${TYPE_KO[t]}: 50라운드 창별 먹은 진주 (판당 평균, 창 시작에 진행 중인 판)`);
    P(table(['창', '기준점 판', '우리', '우리 중 자연', '상대', '상대 중 자연', '상위 판', '상위 승자', '상위 패자', 'r1 이긴 판 우리', 'r1 진 판 우리'], x.us.map((u, w) => [`${w * 50}–${w * 50 + 49}`, u.n, fx(u.mean), fx(u.nat), fx(x.them[w].mean), fx(x.them[w].nat), x.topW[w].n, fx(x.topW[w].mean), fx(x.topL[w].mean), fx(x.r1win[w].mean), fx(x.r1loss[w].mean)])));
    P('');
  }
  P('### 분열');
  const spRow = (k, x) => [k, x.games, fx(x.perGame, 1), x.n, `${pc(x.child2, x.n)}/${pc(x.child3, x.n)}/${pc(x.child4, x.n)}/${pc(x.child5p, x.n)}`, fx(x.childMedian, 0), fx(x.parentBefore, 0), pc(x.fourTo22, x.n), pc(x.leader, x.n), x.byWin.map(v => fx(v / x.games, 1)).join(' ')];
  P(table(['묶음', '판', '판당 분열', '분열', '자식 길이 2/3/4/5+', '자식 중앙값', '분열 전 부모 중앙값', '4→2+2', '최장이 분열', '창별 판당 분열(0..9)'], [
    ...['all', 'elim', 'r500', 'r1'].flatMap(k => [spRow(`${k} 우리`, S.q4.splits[k].us && { ...S.q4.splits[k].us, games: S.q4.splits[k].games }), spRow(`${k} 상대`, { ...S.q4.splits[k].them, games: S.q4.splits[k].games })]),
    ...['topelimW', 'topelimL', 'topr500W', 'topr500L'].map(k => spRow(k, S.q4.splits[k]))]));
  P('');
  P('우리 분열 종류(정책/탈출), 첫 분열, 분열 없는 판: ' + ['all', 'elim', 'r500', 'r1'].map(k => { const x = S.q4.splits[k].us; return `${k} ${x.policy}/${x.escape}, 첫 분열 중앙값 ${fx(x.firstSplit.median, 0)}, 분열 0인 판 ${x.noSplitGames}`; }).join(' / '));
  P('상대 첫 분열 라운드 중앙값: ' + ['all', 'r1'].map(k => `${k} ${fx(S.q4.splits[k].them.firstSplit.median, 0)}`).join(', '));
  P('');

  P('## Q5 잘된 경기');
  const storyRow = x => [x.gameId, x.map, `${x.opp}`, x.win ? 'W' : 'L', x.endReason === 'teamEliminated' ? `전멸 r${x.rounds - 1}` : '500', `${x.init[0]}/${x.init[1]}`,
    `${x.final[0].longest}:${x.final[1].longest}`, `${x.final[0].total}:${x.final[1].total}`, `${x.final[0].units}:${x.final[1].units}`,
    x.cp.filter(c => [100, 300, 400].includes(c.r)).map(c => `r${c.r} ${c.us[2]}:${c.them[2]}`).join(' '), `${x.peak[0] ? x.peak[0].maxLen + '@' + x.peak[0].maxR + (x.peak[0].died !== null ? '†' + x.peak[0].died : '') : '-'}`,
    `${x.peak[1] ? x.peak[1].maxLen + '@' + x.peak[1].maxR + (x.peak[1].died !== null ? '†' + x.peak[1].died : '') : '-'}`, `${x.eat[0]}:${x.eat[1]}`, `${x.splits[0]}:${x.splits[1]}`,
    Object.entries(x.theirDeaths).filter(([, v]) => v[0]).map(([c, v]) => `${c} ${v[0]}/${v[1]}`).join(', '), Object.entries(x.ourDeaths).filter(([, v]) => v[0]).map(([c, v]) => `${c} ${v[0]}/${v[1]}`).join(', ')];
  const storyHead = ['경기', '지도', '상대', '결과', '끝', '시작 수', '끝 최장', '끝 합', '끝 수', '최장 r100/r300/r400', '우리 최고(길이@라운드†사망)', '상대 최고', '먹이 우리:상대', '분열 우리:상대', '상대 사망 분류(건/길이)', '우리 사망 분류(건/길이)'];
  P('### 이긴 6판'); P(table(storyHead, S.q5.wins.map(storyRow))); P('');
  P('### Autarky 7판'); P(table(storyHead, S.q5.autarky.map(storyRow))); P('');
  P('### Prisoners Dilemma 7판'); P(table(storyHead, S.q5.pd.map(storyRow))); P('');
  P('### r1-online 이긴 판 / 진 판');
  const r1r = (k, x) => [k, x.n, `${fx(x.oppElo.median, 0)} [${fx(x.oppElo.q1, 0)}–${fx(x.oppElo.q3, 0)}]`, x.elimUs, x.elimThem, x.roundLimit, fx(x.themUnits100, 0), fx(x.themSplits, 0), `${fx(x.finalLongest[0], 0)}:${fx(x.finalLongest[1], 0)}`, `${fx(x.eat[0], 0)}:${fx(x.eat[1], 0)}`, fx(x.ourBigRammedPerGame, 2), fx(x.theirKilledByUsPerGame, 1), fx(x.theirBigKilledByUs, 2)];
  P(table(['묶음', '판', '상대 Elo 중앙값', '우리 전멸', '상대 전멸', '500라운드', '상대 수 r100', '상대 분열/판', '끝 최장 우리:상대', '먹이 우리:상대', '우리 길이>=6 박힘/판', '우리가 잡은 상대/판', '그중 길이>=6/판'], [r1r('이긴 판', S.q5.r1.win), r1r('진 판', S.q5.r1.loss)]));
  P('r1 지도별 승/판: ' + MAPS.map(m => `${m} ${S.q5.r1.winMaps[m][0]}/${S.q5.r1.winMaps[m][1]}`).join(', '));
  P('r1 상대 Elo 구간별 승/판: ' + S.q5.r1.eloBands.map(b => `${b.band} ${b.wins}/${b.n}`).join(', '));
  P('');

  P('## Q6 상대별');
  P(table(['상대', '승', '전멸(라운드 중앙값)', '상대 수 r20/50/100/200', '우리 수 r20/50/100/200', '상대 분열/판(자식 2)', '박힘/판(길이>=6)', '박힘 길이/판', '박은 적 <=3', '박은 적 질주', '우리 주검 진주 상대/우리', '먹이 우리:상대', '상대 빈 이웃 자해/판', '우리 마지막 드래곤 사인', '상위권 경기에서: 판(승), 수 r50/100/200, 분열/판, 자식 2'],
    S.q6.map(x => [`${x.opp} ${x.name}`, `${x.wins}/${x.n}`, `${x.elim} (${fx(x.elimRound.median, 0)})`, x.themUnits.map(v => fx(v, 0)).join('/'), x.usUnits.map(v => fx(v, 0)).join('/'), `${fx(x.themSplitsPerGame, 0)} (${x.themChild2})`,
      `${fx(x.rammedPerGame, 1)} (${fx(x.rammedBigPerGame, 2)})`, fx(x.rammedLenPerGame, 1), x.attLe3, x.attSprint, `${x.ourDropsEatenByThem}/${x.ourDropsEatenByUs}`, `${fx(x.eat[0], 0)}:${fx(x.eat[1], 0)}`, fx(x.themSelfFreePerGame, 1),
      Object.entries(x.lastDeathCls).filter(([, v]) => v).map(([c, v]) => `${c} ${v}`).join(', '),
      `${x.topRef.games}(${x.topRef.wins}, 전멸승 ${x.topRef.elimWins}), ${fx(x.topRef.units50, 0)}/${fx(x.topRef.units100, 0)}/${fx(x.topRef.units200, 0)}, ${fx(x.topRef.splitsPerGame, 0)}, ${x.topRef.child2}`])));
  P('');
  P('상대별 우리 잃은 길이/판(분류): ' + S.q6.map(x => `${x.opp} ` + Object.entries(x.ourLenByCls).filter(([, v]) => v >= 0.5).map(([c, v]) => `${c} ${fx(v)}`).join(', ')).join(' | '));
  P('상대별 상대 잃은 길이/판(분류): ' + S.q6.map(x => `${x.opp} ` + Object.entries(x.theirLenByCls).filter(([, v]) => v >= 0.5).map(([c, v]) => `${c} ${fx(v)}`).join(', ')).join(' | '));
  P('상대별 500라운드 판(지도, 끝 최장 우리:상대): ' + S.q6.map(x => `${x.opp} ` + x.finalLimit.map(f => `${f[0]} ${f[1]}:${f[2]}${f[3] ? 'W' : ''}`).join(', ')).join(' | '));
  P('');

  P('## Q7 손실원 (진 판, 판당)');
  P(table(['분류', '판당 잃은 길이', '그중 길이>=6', '이 사망이 있던 진 판'], S.q7.lossLen.sort((a, b) => b.lenPerGame - a.lenPerGame).map(x => [CLS2_KO[x.src], fx(x.lenPerGame, 1), fx(x.lenPerGameBig, 1), x.games])));
  P(`먹이(진 판 판당): 우리 ${fx(S.q7.eatGap.us)} (자연 ${fx(S.q7.eatGap.usNat)}), 상대 ${fx(S.q7.eatGap.them)} (자연 ${fx(S.q7.eatGap.themNat)}). 질주 비용 우리 ${fx(S.q7.sprintPaid)}, 상대 ${fx(S.q7.sprintPaidThem)}.`);
  P(`진 판 ${S.q7.elimLost + S.q7.limLost}: 전멸 ${S.q7.elimLost}, 500라운드 판정 ${S.q7.limLost}.`);
  P('### 500라운드 판정으로 진 판: 우리 팀 최장 곡선의 최고점, r300 최장·합, 끝, 길이 6 이상 우리 사망(라운드:길이:분류)');
  P(table(['경기', '지도', '상대', '우리 최장 최고@라운드', 'r300 최장 우리:상대', 'r300 합 우리:상대', '끝 최장 우리:상대', '상대 최장 최고', '길이>=6 사망'], S.q7.peakFate.map(p => [p.gameId, p.map, p.opp, `${p.peak}@${p.peakR}`, `${p.us300}:${p.them300}`, `${p.tot300[0]}:${p.tot300[1]}`, `${p.finalUs}:${p.finalThem}`, p.themPeak, p.big.map(b => b.join(':')).join(' ')])));
  P('');
  P(`전멸로 진 판 ${S.q7.elimSeq.length}: 마지막 사망 분류 ` + Object.entries(S.q7.elimLastCls).filter(([, v]) => v).map(([c, v]) => `${c} ${v}`).join(', ') +
    `. 탈출 조각을 뺀 우리 사망 ${S.q7.elimRammedShare.all}건 중 H-rammed ${S.q7.elimRammedShare.rammed}건, 길이 ${S.q7.elimRammedShare.allLen} 중 ${S.q7.elimRammedShare.rammedLen}.`);
  P('');
  P('### 전멸로 진 판의 우리 사망 순서 (탈출 조각 제외; 라운드:길이:분류:박은 적 길이:걸음)');
  for (const x of S.q7.elimSeq) P(`- ${x.gameId} ${x.map} ${x.opp} (시작 ${x.init}, 끝 r${x.end}): ` + x.seq.map(d => `${d[0]}:${d[1]}:${d[2]}${d[3] !== null ? ':' + d[3] + ':' + d[4] : ''}`).join(' '));
  console.log(out.join('\n'));
}

// ---------------------------------------------------------------------------------------------------------------
function listGames(only) {
  const tasks = [], skipped = [];
  for (const { set, dir } of SETS) {
    const abs = path.join(ROOT, dir), idx = JSON.parse(fs.readFileSync(path.join(abs, 'index.json'), 'utf8'));
    for (const g of idx.games) {
      if (only && !only.has(g.gameId)) continue;
      if (g.ourSubmission !== OWN_SUB) { skipped.push({ set, gameId: g.gameId, sub: g.ourSubmission }); continue; }
      const meta = JSON.parse(fs.readFileSync(path.join(abs, `game-${g.gameId}.json`), 'utf8'));
      const us = String(g.ourSide).toUpperCase(), them = us === 'A' ? 'B' : 'A';
      if (meta['team' + us + 'Id'] !== OWN_TEAM) throw Error(`game ${g.gameId}: side ${us} is not team ${OWN_TEAM}`);
      const gg = { ...g, set, oppName: meta['team' + them + 'Name'], oppElo: meta['team' + them + 'Elo'], ourElo: meta['team' + us + 'Elo'] };
      const row = { battleId: g.seriesId, gameId: g.gameId, map: g.mapName, teamA: meta.teamAName, teamB: meta.teamBName, eloA: meta.teamAElo, eloB: meta.teamBElo, winner: g.winner, ranked: g.ranked, at: g.requestedAt };
      tasks.push({ file: path.join(abs, `M${g.gameId}.replay`), g: gg, row });
    }
  }
  return { tasks, skipped };
}

async function runWorkers(tasks, jobs) {
  const results = new Array(tasks.length), errors = [];
  let next = 0, done = 0;
  await new Promise((resolve, reject) => {
    const nw = Math.min(jobs, tasks.length); let live = nw;
    if (!nw) return resolve();
    for (let k = 0; k < nw; k++) {
      const w = cp.fork(__filename, ['--child'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      let finished = false;
      const feed = () => {
        if (next >= tasks.length) { finished = true; w.send('exit'); if (--live === 0) resolve(); return; }
        const i = next++; w.send({ i, file: tasks[i].file, g: tasks[i].g, row: tasks[i].row });
      };
      w.on('message', m => {
        if (m.error) errors.push(tasks[m.i].g.gameId + ' ' + m.error); else results[m.i] = m.rec;
        if (++done % 25 === 0) process.stderr.write(`${done}/${tasks.length} `);
        feed();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('child exited with code ' + code)); });
      feed();
    }
  });
  process.stderr.write('\n');
  if (errors.length) { console.error(errors.join('\n')); throw Error(errors.length + ' games failed'); }
  return results;
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.min(3, Math.max(1, +opt('jobs', 3))), out = path.resolve(ROOT, opt('out', 'data/online/baseline_study.json'));
  const only = opt('games', null) ? new Set(opt('games').split(',').map(Number)) : null;
  const t0 = Date.now();
  let games, skipped;
  if (argv.includes('--reuse')) {
    const prev = JSON.parse(fs.readFileSync(out, 'utf8'));
    if (prev.format !== FORMAT) throw Error('--reuse: output has format ' + prev.format + ', expected ' + FORMAT);
    games = prev.games.filter(g => !only || only.has(g.gameId)); skipped = prev.inputs.skipped;
  } else {
    const L = listGames(only); skipped = L.skipped;
    process.stderr.write(`analysing ${L.tasks.length} games with ${jobs} workers (skipped ${skipped.length} of other submissions)\n`);
    games = await runWorkers(L.tasks, jobs);
  }
  const top = loadTop();
  const summary = aggregate(games, top);
  const doc = { format: FORMAT, generatedAt: new Date().toISOString(), inputs: { sets: SETS, top: { features: TOP_FEATURES, keys: TOP_KEYS, games: top.length, excluded: 'SSS' }, ownTeam: OWN_TEAM, ownSubmission: OWN_SUB, skipped },
    definitions: DEFS, summary, games };
  if (!only || argv.includes('--write')) fs.writeFileSync(out, JSON.stringify(doc));
  report(summary);
  process.stderr.write(`done in ${((Date.now() - t0) / 1000).toFixed(1)}s -> ${path.relative(ROOT, out)}${only && !argv.includes('--write') ? ' (not written: --games)' : ''}\n`);
}

const DEFS = {
  state: 'flow[side].u/t/l[r] = 라운드 r이 시작하기 직전(r-1라운드가 끝난 뒤)의 살아 있는 수/몸길이 합/최장. 마지막 원소는 끝난 뒤 상태. side 0 = 우리, 1 = 상대.',
  inProgress: '라운드별 통계는 그 라운드에 진행 중인 판(rounds > r, r = 500이면 500라운드까지 간 판)만 넣는다.',
  lastLed: '우리 > 상대인 가장 늦은 상태 인덱스(끝 상태 포함). 상위권은 10라운드 간격 timeline으로 같은 정의.',
  cls2: CLS2_KO, themCls: THEM_KO,
  trapped: '자기 차례 시작(행동 직전)에 머리의 네 이웃이 모두 해초이거나 몸(자기 꼬리 포함)',
  rammed: '적이 움직여 우리 머리 칸으로 들어와 둘 다 죽음. 박은 적 길이는 행동 시작 때 길이, 걸음은 그 행동의 걸음 수.',
  decision: '우리 드래곤의 마지막 행동 직전 상태. 7x7 안 = 그때 우리 머리와 박은 적의 행동 전 머리의 체비쇼프 거리 <= 3(토러스, 해초·포털 무시). 턴은 id 순이라 적의 행동 전 위치가 곧 우리가 결정할 때의 위치다.',
  reach: '적 도달 = 적 머리에서 빈 칸만 지나는 BFS 거리 <= 길이-1(먹이·다른 드래곤의 움직임 무시). "모든 적 도달 밖 한 걸음"은 우리의 합법 한 걸음 후보 중 맨해튼 9 안의 모든 적 머리에 대해 도달 밖인 칸.',
  feed: '우리 봇 지표가 "feed"로 시작하는 턴의 사망(자기 목으로 들어가 죽어 진주를 왕에게 남김, 340/430 관문).',
  pearls: '자연 = 시작 배치 + 라운드 시작 생성. 주검 = 사망 직후 생긴 진주, 죽은 드래곤의 팀으로 나눈다. 먹음 = 이동 시뮬레이션에서 머리가 진주 칸에 들어감. 20라운드 안 = 사망 라운드부터 +20.',
  king: '먹는 순간(먹기 전 길이) 팀의 다른 모든 드래곤 이상인 드래곤.',
  top: 'data/top/features.jsonl 중 스냅숏 키 472판에서 SSS가 낀 19판을 뺀 453판. 지도 종류는 지도 이름으로 나눈다.',
};

module.exports = { analyse, aggregate, buildGeo, classify };
if (!CHILD && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
