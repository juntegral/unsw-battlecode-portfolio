#!/usr/bin/env node
// 온라인 대전 기록 관측("당하고 배우기"). 평가·연구 전용이며 봇 입력으로 쓰지 않는다. 네트워크를 쓰지 않는다.
//
// usage (저장소 루트에서):
//   node tools/observe_online.js [--report]            팀별·지도별 집계 표(마크다운)를 표준 출력에 쓴다(기본 동작).
//   node tools/observe_online.js --decode <팀id>        그 팀 음파 메시지의 비트 구역을 발신자 상태와 맞춰 본다.
//   node tools/observe_online.js --story <경기id>       한 경기의 흐름·큰 사망·분열·음파를 요약한다.
//   node tools/observe_online.js --local exp/eval-r1    로컬 평가 리플레이를 같은 정의로 분석해 온라인 묶음과 핵심 지표를 나란히 쓴다
//                                                       (캐시 data/observe_local_<폴더>.json, 우리 진영은 폴더 이름의 _A_/_B_).
//   공통 옵션: --data data/online  --own 583  --focus 231,46,47,378,7,267,922
//              --cache data/online/observe_online.json  --refresh(캐시 무시)  --games id,id(일부만)
//   처음 실행은 273판을 읽는 데 2분 남짓 걸리고, 그 뒤로는 캐시를 쓴다.
//
// 입력: <data>/<세대>/<배치>/index.json(games[]: gameId, map, ourSide, opponentTeam, winner), requests.json(팀 이름),
//       game-<id>.json(teamAId/teamBId), M<id>.replay.
// 방법: 공식 뷰어 해석기(tools/viewer.js와 같은 vsix)의 상태 객체(match.roundAt(0).copy(): map, bodies)에 사건을
//       차례로 적용해 모든 드래곤의 몸을 추적한다. 사망 원인 판정은 ../UNSW/tools/death_audit.js(행동 재현으로 치명 칸과
//       그 주인 찾기), 머리끼리 짝짓기는 headon_miner.js, 라운드 스냅숏·역전 시점은 scrim_report.js 방식을 따랐다.
//
// 사실(이 도구를 만들며 확인):
// - 형식 2 리플레이의 EventSonarPing 자료 구역은 32바이트다. 뷰어 스키마(16바이트)의 value(@8, 32비트)는 늘 0이다.
//   실제 64비트 메시지는 16..23바이트, 에코 종류는 24..27바이트(2 해초, 3 아군 몸, 4 아군 머리, 5 적 몸, 6 적 머리;
//   자기 자신은 아군으로 센다)에 있다. 우리 봇의 로컬 리플레이에서 16..23바이트를 풀면 검사값이 맞고, 표지는
//   MSG_MAGIC(0x2D, 일반 메시지; 발신자 id·라운드가 맞음) 또는 MSG_MAGIC_KING(0x1B, 왕 정보 중계)이다.
//   그래서 이 도구는 뷰어 소스를 고쳐 value64와 echo를 함께 꺼낸다(tools/viewer.js의 value는 쓰지 않는다).
// - "분열로 태어남"은 그 드래곤이 dragonSplit 사건의 자식으로 생겼는지(fromSplit)로 판정한다. 태어난 라운드(born > 0)로
//   판정하면 r0 분열의 자식이 초기 드래곤과 함께 빠진다(2026-09-29 정정, 캐시 형식 v3).
// - sonarPing.direction은 광선의 진행 방향이다. 목 쪽으로 쏜 음파는 꼬리에서 나가므로 origin이 머리가 아니다.
//   의도한 방향(머리→목)은 따로 복원한다(dirIntended).
// - 머리끼리 충돌은 dragonDeath(H) 두 개가 잇달아 나온다(먼저 당한 쪽, 다음 움직인 쪽). 움직인 쪽은 직전 dragonAction의 id다.
// - 행동 불능(A) 사망은 dragonAction.kind === 'suicide'로 기록된다.
// - winner와 ourSide는 대소문자가 섞여 있어 소문자로 비교한다.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process'), vm = require('vm');
const REPO = path.resolve(__dirname, '..');

// ---------- 인자 ----------
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 && i + 1 < argv.length ? argv[i + 1] : d; };
const flag = k => argv.includes(k);
const DATA = path.resolve(REPO, opt('--data', 'data/online'));
const OWN = +opt('--own', 583);
const FOCUS = opt('--focus', '231,46,47,378,7,267,922').split(',').map(Number);
const CACHE = path.resolve(REPO, opt('--cache', 'data/online/observe_online.json'));
const ONLY = opt('--games', '') ? new Set(opt('--games', '').split(',').map(x => /^\d+$/.test(x) ? +x : x)) : null;   // 로컬 경기 id는 폴더 이름
const SMALL = 3;           // 작은 조각: 분열로 태어날 때 길이 <= 3
const BIG = 6;             // 큰 드래곤: 길이 >= 6
const D = 'NESW', DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
const ECHO = { 2: 'kelp', 3: 'ally', 4: 'allyHead', 5: 'enemy', 6: 'enemyHead' };
const FORMAT = 'observe-online-v3';   // v3: fromSplit 열 추가(분열로 태어남 = dragonSplit의 자식)

// ---------- 리플레이 해석기(뷰어 소스 + 음파 64비트 값 패치) ----------
let CTX = null;
function parser() {
  if (CTX) return CTX;
  const root = require('./viewer.js').root;   // 같은 vsix를 쓴다
  const vsix = path.join(root, '.venv-ppo/lib/python3.13/site-packages/unswbc/replay-viewer.vsix');
  let src = cp.execFileSync('unzip', ['-p', vsix, 'extension/dist/webview/webview.js'], { maxBuffer: 8 << 20 }).toString();
  src = src.slice(0, src.indexOf('var Af=B(')).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)');
  const needle = 'value:t.value,origin:_f(t.origin)';
  if (!src.includes(needle) || !src.includes('function ou(')) throw Error('viewer build differs: sonar patch point not found');
  src = src.replace(needle, 'value:t.value,value64:(()=>{const r=ou(t),s=r.segment,o=r.byteOffset;' +
    'return s.getUint32(o+20).toString(16).padStart(8,"0")+s.getUint32(o+16).toString(16).padStart(8,"0")})(),' +
    'echo:(()=>{const r=ou(t);return r.segment.getUint32(r.byteOffset+24)})(),origin:_f(t.origin)');
  src += 'globalThis.parseReplay=kf;})();';
  const ctx = { TextEncoder, TextDecoder }; vm.runInNewContext(src, ctx, { timeout: 5000 });
  return (CTX = ctx);
}

// ---------- 기록 목록 ----------
function listGames() {
  const out = [], names = new Map();
  for (const gen of fs.readdirSync(DATA).filter(x => fs.statSync(path.join(DATA, x)).isDirectory()).sort())
    for (const batch of fs.readdirSync(path.join(DATA, gen)).sort()) {
      const dir = path.join(DATA, gen, batch), idxf = path.join(dir, 'index.json');
      if (!fs.existsSync(idxf)) continue;
      const idx = JSON.parse(fs.readFileSync(idxf));
      const rq = fs.existsSync(path.join(dir, 'requests.json')) ? JSON.parse(fs.readFileSync(path.join(dir, 'requests.json'))) : { sent: [] };
      for (const s of rq.sent || []) if (s.name) names.set(s.teamId, s.name);
      for (const g of idx.games) out.push({ ...g, gen, batch, bot: idx.bot, dir });
    }
  return { games: out, names };
}

// ---------- 열 이름(캐시는 배열로 저장) ----------
const DEATH_COLS = ['round', 'side', 'id', 'len', 'reason', 'leader', 'actor', 'free', 'fatal', 'fatalStep', 'ownerId', 'ownerLen',
  'moverId', 'moverLen', 'moverSteps', 'moverBorn', 'moverBornLen', 'partnerId', 'partnerSide', 'partnerLen', 'partnerBorn', 'partnerBornLen',
  'born', 'bornLen', 'kind', 'steps', 'exceeded', 'rammerCheb', 'rammerManh', 'rammerSeen', 'fromSplit', 'moverFromSplit', 'partnerFromSplit'];
const SPLIT_COLS = ['round', 'side', 'parentId', 'childId', 'before', 'parent', 'child', 'parentLeader'];
// fromSplit: 1 = dragonSplit 사건의 자식으로 생김, 0 = 초기 드래곤. born은 태어난 라운드라서 r0 분열의 자식도 0이다.
const LIFE_COLS = ['id', 'side', 'born', 'bornLen', 'parent', 'maxLen', 'died', 'reason', 'deathLen', 'turns', 'splitsMade', 'uniqTiles', 'farthest',
  'contactTurns', 'closeTurns', 'nearBigTurns', 'pings', 'eats', 'fromSplit'];
const FLOW_COLS = ['round', 'nUs', 'longUs', 'totUs', 'smallUs', 'nThem', 'longThem', 'totThem', 'smallThem'];
const obj = (cols, a) => { const o = {}; cols.forEach((c, i) => { o[c] = a[i]; }); return o; };

// 로컬 평가 폴더(<dir>/games/<상대>_<지도>_<진영>_<시드>/game.replay)를 같은 형태의 목록으로 만든다.
const LOCAL_MAPS = 'autarky|default|devil|portals|prisoners_dilemma|queen_of_spades|schooltime|slithery_fight|trauma|trophy|arena|big_empty|Colosseum|default_small|dilemma|stronghold';
function listLocal(evalDir) {
  const root = path.join(evalDir, 'games'), re = new RegExp(`^(.*?)_(${LOCAL_MAPS})_([AB])_(\\d+)$`);
  const label = path.basename(evalDir);
  return fs.readdirSync(root).sort().map(k => { const m = re.exec(k); if (!m || !fs.existsSync(path.join(root, k, 'game.replay'))) return null;
    return { gameId: k, dir: path.join(root, k), replay: 'game.replay', ourSide: m[3], opponentTeam: m[1], map: m[2], gen: 'local', batch: label, bot: label }; }).filter(Boolean);
}

// ---------- 한 경기 분석 ----------
function analyseGame(g) {
  const mf = path.join(g.dir, `game-${g.gameId}.json`), meta = fs.existsSync(mf) ? JSON.parse(fs.readFileSync(mf)) : null;
  const us = g.ourSide.toUpperCase(), them = us === 'A' ? 'B' : 'A';
  if (meta && (us === 'A' ? meta.teamAId : meta.teamBId) !== OWN) throw Error(`game ${g.gameId}: side ${us} is not team ${OWN}`);
  const R = parser().parseReplay(fs.readFileSync(path.join(g.dir, g.replay || `M${g.gameId}.replay`)));
  const st = R.match.roundAt(0).copy(), map = st.map, bodies = st.bodies;
  const W = map.width, H = map.height;
  const mapName = (/MAP_NAME (.+)/.exec(R.map || '') || [])[1] || String(g.map);
  const wrap = (x, y) => ((y % H + H) % H) * W + ((x % W + W) % W);
  const partner = new Map();
  for (const [a, b] of map.portals) { const k = p => `${p.side}:${p.x},${p.y}`; partner.set(k(a), b); partner.set(k(b), a); }
  // 포털을 지나는 한 칸 이동(death_audit.js·headon_miner.js와 같은 규칙). 해초면 -1.
  const step = (p, d) => {
    const x = p % W, y = (p / W | 0); const e = map.edgeAt(x, y, D[d]); if (e === 1) return -1;
    if (e === 2) {
      const key = d === 1 ? `W:${(x + 1) % W},${y}` : d === 3 ? `W:${x},${y}` : d === 2 ? `N:${x},${(y + 1) % H}` : `N:${x},${y}`;
      const q = partner.get(key); if (!q) return -1;
      return q.side === 'W' ? (d === 1 ? wrap(q.x, q.y) : wrap(q.x - 1, q.y)) : (d === 2 ? wrap(q.x, q.y) : wrap(q.x, q.y - 1));
    }
    return wrap(x + DX[d], y + DY[d]);
  };
  const dxy = (a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs((a / W | 0) - (b / W | 0)); return [Math.min(dx, W - dx), Math.min(dy, H - dy)]; };
  const cheb = (a, b) => { const [x, y] = dxy(a, b); return Math.max(x, y); };
  const manh = (a, b) => { const [x, y] = dxy(a, b); return x + y; };
  const cell = s => wrap(s.x, s.y);
  const side = t => t === us ? 0 : 1;               // 0 = 우리, 1 = 상대
  const pearlAt = q => map.tileAt(q % W, q / W | 0) === 2;
  const life = new Map();
  const teamOf = id => bodies.dragons.get(id)?.team ?? life.get(id)?.team;
  const lenOf = id => bodies.dragons.get(id)?.body.length ?? null;
  const newLife = (id, team, born, bornLen, parent, spawn, fromSplit) => life.set(id, {
    id, team, born, bornLen, parent, fromSplit, maxLen: bornLen, died: null, reason: null, deathLen: null, turns: 0, splitsMade: 0,
    tiles: new Set([spawn]), spawn, farthest: 0, contactTurns: 0, closeTurns: 0, nearBigTurns: 0, pings: 0, eats: 0,
  });
  for (const d of bodies.dragons.values()) newLife(d.id, d.team, 0, d.body.length, null, cell(d.body[0]), 0);

  const T = () => ({
    actions: 0, moves: 0, sprints: 0, splits: 0, suicides: 0,
    pings: 0, pingTurns: 0, perTurn: [0, 0, 0, 0, 0], perTurnDistinct: [0, 0, 0, 0, 0], firstPing: null, pingsByPhase: [0, 0, 0, 0, 0],
    dirIntended: { N: 0, E: 0, S: 0, W: 0, '?': 0 }, dirTravel: { N: 0, E: 0, S: 0, W: 0 }, redirected: 0,
    hits: { self: 0, ally: 0, allyHead: 0, enemy: 0, enemyHead: 0, kelp: 0, lost: 0 }, echoMismatch: 0,
    zero: 0, values: new Map(), bit1: new Array(64).fill(0), pingsBySmall: 0, pingsByBig: 0,
    // 먹은 진주: [출처][시기(100라운드)] 출처 = spawn(자연 생성) / own(자기 팀이 죽으며 떨굼) / enemy(상대가 떨굼)
    eats: { spawn: [0, 0, 0, 0, 0], own: [0, 0, 0, 0, 0], enemy: [0, 0, 0, 0, 0] },
    leaderEats: { spawn: [0, 0, 0, 0, 0], own: [0, 0, 0, 0, 0], enemy: [0, 0, 0, 0, 0] },
  });
  const S = { A: T(), B: T() };
  const flow = [], deaths = [], splits = [];
  let round = -1, started = false, pend = null, dropCtx = null, pingTurn = null, actionNo = 0;
  const pearlSrc = new Map();   // 칸 -> 'spawn' | 'A' | 'B'(그 팀 드래곤이 죽으며 떨굼)
  const lastPre = new Map();    // 드래곤 -> 마지막 결정 때 머리 칸(행동 전)
  const leaderOf = t => { let best = null; for (const d of bodies.dragons.values()) if (d.team === t && (!best || d.body.length > best.body.length)) best = d; return best; };
  const phase = r => Math.min(4, Math.max(0, Math.floor(r / 100)));

  const snap = () => {
    const o = { A: [0, 0, 0, 0], B: [0, 0, 0, 0] };
    for (const d of bodies.dragons.values()) { const x = o[d.team]; x[0]++; x[1] = Math.max(x[1], d.body.length); x[2] += d.body.length; if (d.body.length <= SMALL) x[3]++; }
    flow.push([round, ...o[us], ...o[them]]);
  };
  const closePingTurn = () => {
    if (!pingTurn) return;
    const s = S[pingTurn.team]; s.perTurn[Math.min(4, pingTurn.n)]++; s.perTurnDistinct[Math.min(4, pingTurn.vals.size)]++;
    pingTurn = null;
  };
  // 행동 재현: 행동 직전 상태에서 발걸음을 따라가며 처음 치명적인 칸과 그 칸의 주인을 찾는다(death_audit.js 방식).
  const simulate = p => {
    if (p.sim) return p.sim;
    const owner = new Map();
    for (const d of bodies.dragons.values()) { if (d.id === p.id) continue; d.body.forEach((s, i) => owner.set(cell(s), { id: d.id, head: i === 0 })); }
    const body0 = p.body.slice();
    let free = 0; for (let k = 0; k < 4; k++) { const q = step(body0[0], k); if (q >= 0 && !body0.includes(q) && !owner.has(q)) free++; }
    let b = body0.slice(), len = b.length, res = null;
    if (p.kind === 'move') {
      for (let i = 0; i < p.steps.length; i++) {
        if (i > 0 && len <= 2) { res = { step: i + 1, what: 'noPay' }; break; }
        const q = step(b[0], D.indexOf(p.steps[i]));
        if (q < 0) { res = { step: i + 1, what: 'kelp' }; break; }
        if (b.includes(q)) { res = { step: i + 1, what: 'self' }; break; }
        const o = owner.get(q);
        if (o) { res = { step: i + 1, what: (teamOf(o.id) === p.team ? 'ally' : 'enemy') + (o.head ? 'Head' : 'Body'), ownerId: o.id, ownerLen: lenOf(o.id) }; break; }
        b.unshift(q); if (pearlAt(q) || p.eaten.has(q)) len++; else b.pop();
        if (i > 0) { b.pop(); len--; }
      }
    }
    return (p.sim = { fatal: res, free });
  };

  const hGroups = new Map();
  for (const e of R.events) {
    if (e.type === 'roundStart') { closePingTurn(); started = true; round = e.round; dropCtx = null; snap(); continue; }
    if (!started) continue;
    switch (e.type) {
      case 'turnStart': dropCtx = null; break;
      case 'dragonAction': {
        closePingTurn(); dropCtx = null; actionNo++;
        const d = bodies.dragons.get(e.id); if (!d) break;
        const a = e.action || {};
        pend = { no: actionNo, id: e.id, team: d.team, round, kind: a.kind, steps: a.kind === 'move' ? a.steps.slice() : [], body: d.body.map(cell), eaten: new Set(), exceeded: !!e.instructions?.exceeded };
        lastPre.set(e.id, pend.body[0]);
        const s = S[d.team]; s.actions++;
        if (a.kind === 'move') { s.moves++; if (a.steps.length > 1) s.sprints++; } else if (a.kind === 'split') s.splits++; else if (a.kind === 'suicide') s.suicides++;
        const L = life.get(e.id); L.turns++;
        const h = pend.body[0]; let seeEnemy = false, closeHead = false, seeBig = false;
        for (const o of bodies.dragons.values()) {
          if (o.team === d.team) continue;
          if (manh(h, cell(o.body[0])) <= 2) closeHead = true;
          for (const sg of o.body) if (cheb(h, cell(sg)) <= 3) { seeEnemy = true; if (o.body.length >= BIG) seeBig = true; break; }
        }
        if (seeEnemy) L.contactTurns++; if (closeHead) L.closeTurns++; if (seeBig) L.nearBigTurns++;
        break;
      }
      case 'dragonUpdate': {
        bodies.applyEvent(e);
        const d = bodies.dragons.get(e.id), L = life.get(e.id);
        if (d && L) { L.maxLen = Math.max(L.maxLen, d.body.length); const hc = cell(d.body[0]); L.tiles.add(hc); L.farthest = Math.max(L.farthest, manh(hc, L.spawn)); }
        break;
      }
      case 'dragonSplit': {
        const p = bodies.dragons.get(e.parentId); const before = p ? p.body.length : e.parentBody.length + e.childBody.length;
        const lead = leaderOf(e.team);
        splits.push([round, side(e.team), e.parentId, e.childId, before, e.parentBody.length, e.childBody.length, lead && lead.id === e.parentId ? 1 : 0]);
        bodies.applyEvent(e);
        newLife(e.childId, e.team, round, e.childBody.length, e.parentId, cell(e.childBody[0]), 1);
        if (life.get(e.parentId)) life.get(e.parentId).splitsMade++;
        break;
      }
      case 'dragonDeath': {
        const d = bodies.dragons.get(e.id); if (!d) { bodies.applyEvent(e); break; }
        const len = d.body.length, team = d.team;
        let maxAlive = 0; for (const o of bodies.dragons.values()) if (o.team === team) maxAlive = Math.max(maxAlive, o.body.length);
        const L = life.get(e.id);
        const rec = { round, side: side(team), id: e.id, len, reason: e.reason, leader: len >= maxAlive ? 1 : 0, born: L?.born ?? 0, bornLen: L?.bornLen ?? null, fromSplit: L?.fromSplit ?? null };
        const actor = pend && pend.round === round ? pend : null;
        if (actor) {
          const sim = simulate(actor);
          rec.actor = actor.id === e.id ? 'self' : actor.team === team ? 'ally' : 'enemy';
          if (actor.id === e.id) {
            Object.assign(rec, { free: sim.free, fatal: sim.fatal?.what ?? null, fatalStep: sim.fatal?.step ?? null, ownerId: sim.fatal?.ownerId ?? null,
              ownerLen: sim.fatal?.ownerLen ?? null, kind: actor.kind, steps: actor.steps.length, exceeded: actor.exceeded ? 1 : 0 });
          } else {
            const ml = life.get(actor.id);
            Object.assign(rec, { moverId: actor.id, moverLen: actor.body.length, moverSteps: actor.steps.length, moverBorn: ml?.born ?? null, moverBornLen: ml?.bornLen ?? null, moverFromSplit: ml?.fromSplit ?? null });
            // 우리가 마지막으로 결정할 때 들이받은 쪽은 행동 전 칸(actor.body[0])에 있었다(턴은 id 순으로 한 번씩).
            const ourPre = lastPre.get(e.id), ourNow = cell(d.body[0]);
            if (ourPre != null) { rec.rammerCheb = cheb(ourPre, actor.body[0]); rec.rammerSeen = rec.rammerCheb <= 3 ? 1 : 0; }
            rec.rammerManh = manh(actor.body[0], ourNow);
          }
        } else rec.actor = 'none';
        if (e.reason === 'H') { const k = actor ? actor.no : -1; if (!hGroups.has(k)) hGroups.set(k, []); hGroups.get(k).push(rec); rec._grp = hGroups.get(k); }
        deaths.push(rec);
        if (L) { L.died = round; L.reason = e.reason; L.deathLen = len; }
        dropCtx = { team };
        bodies.applyEvent(e);
        break;
      }
      case 'tileChange': {
        const q = cell(e.tile);
        if (e.hasPearl) pearlSrc.set(q, dropCtx ? dropCtx.team : 'spawn');
        else if (pend && pend.round === round) {
          pend.eaten.add(q);
          const src = pearlSrc.get(q) || 'spawn'; pearlSrc.delete(q);
          const kind = src === 'spawn' ? 'spawn' : src === pend.team ? 'own' : 'enemy';
          const s = S[pend.team]; s.eats[kind][phase(round)]++;
          const L = life.get(pend.id); if (L) L.eats++;
          const lead = leaderOf(pend.team);
          if (lead && lead.id === pend.id) s.leaderEats[kind][phase(round)]++;
        }
        map.applyEvent?.(e);
        break;
      }
      case 'sonarPing': {
        const d = bodies.dragons.get(e.senderId); if (!d) break;
        const s = S[d.team], L = life.get(e.senderId);
        s.pings++; if (L) L.pings++;
        if (!pingTurn || pingTurn.no !== pend?.no) { closePingTurn(); pingTurn = { no: pend?.no, team: d.team, n: 0, vals: new Set() }; s.pingTurns++; }
        pingTurn.n++; pingTurn.vals.add(e.value64);
        if (s.firstPing == null) s.firstPing = round;
        s.pingsByPhase[phase(round)]++;
        const head = cell(d.body[0]);
        let intended = e.direction;
        if (cell(e.origin) !== head && d.body.length > 1) {
          s.redirected++; intended = '?';
          const neck = cell(d.body[1]); for (let k = 0; k < 4; k++) if (step(head, k) === neck) intended = D[k];
        }
        s.dirIntended[intended]++; s.dirTravel[e.direction]++;
        let hit;
        if (e.hitId !== undefined) {
          const tgt = bodies.dragons.get(e.hitId);
          hit = e.hitId === e.senderId ? 'self' : tgt ? (tgt.team === d.team ? 'ally' : 'enemy') + (cell(tgt.body[0]) === cell(e.end) ? 'Head' : '') : 'lost';
        } else hit = map.edgeAt(e.end.x, e.end.y, e.direction) === 1 ? 'kelp' : 'lost';
        s.hits[hit]++;
        const ek = ECHO[e.echo] || 'lost', hk = hit === 'self' ? null : hit;   // 자기 자신은 아군으로 메아리친다
        if (hk && ek !== hk) s.echoMismatch++;
        const v = e.value64;
        if (v === '0000000000000000') s.zero++;
        s.values.set(v, (s.values.get(v) || 0) + 1);
        const hi = parseInt(v.slice(0, 8), 16), lo = parseInt(v.slice(8), 16);
        for (let b = 0; b < 32; b++) { if ((lo >>> b) & 1) s.bit1[b]++; if ((hi >>> b) & 1) s.bit1[b + 32]++; }
        if (L && L.fromSplit && L.bornLen <= SMALL) s.pingsBySmall++;
        if (d.body.length >= BIG) s.pingsByBig++;
        break;
      }
      default: break;
    }
  }
  closePingTurn();
  round = Math.max(round, 0); const lastRound = round; snap(); flow[flow.length - 1][0] = 'end';
  for (const x of deaths) {
    if (!x._grp) continue;
    const o = x._grp.find(y => y !== x);
    if (o) Object.assign(x, { partnerId: o.id, partnerSide: o.side, partnerLen: o.len, partnerBorn: o.born, partnerBornLen: o.bornLen, partnerFromSplit: o.fromSplit });
    delete x._grp;
  }
  const packSonar = s => {
    const top = [...s.values.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10);
    const out = { ...s, distinct: s.values.size, topValues: top }; delete out.values; return out;
  };
  const res = R.result;
  return {
    gameId: g.gameId, gen: g.gen, batch: g.batch, bot: g.bot, mapId: g.map, map: mapName, side: us, opp: g.opponentTeam,
    won: (g.winner || res.winner || '').toLowerCase() === us.toLowerCase(), endReason: res.endReason, lastRound,
    final: { us: res['team' + us], them: res['team' + them] }, scores: meta ? { A: meta.scoresA, B: meta.scoresB } : null,
    flow, deaths: deaths.map(x => DEATH_COLS.map(c => x[c] ?? null)), splits,
    lives: [...life.values()].map(L => LIFE_COLS.map(c => c === 'side' ? side(L.team) : c === 'uniqTiles' ? L.tiles.size : L[c] ?? null)),
    sonar: { us: packSonar(S[us]), them: packSonar(S[them]) },
  };
}

// ---------- 캐시 ----------
function loadAll(refresh, local) {
  const { games, names } = local ? { games: listLocal(local), names: new Map() } : listGames();
  const cachePath = local && !argv.includes('--cache') ? path.join(REPO, 'data', `observe_local_${path.basename(local)}.json`) : CACHE;
  let cache = { format: FORMAT, own: OWN, cols: { deaths: DEATH_COLS, splits: SPLIT_COLS, lives: LIFE_COLS, flow: FLOW_COLS }, games: {} };
  if (!refresh && fs.existsSync(cachePath)) { const c = JSON.parse(fs.readFileSync(cachePath)); if (c.format === FORMAT && c.own === OWN) cache = c; }
  let n = 0;
  for (const g of games) {
    if (ONLY && !ONLY.has(g.gameId)) continue;
    if (cache.games[g.gameId]) continue;
    cache.games[g.gameId] = analyseGame(g); n++;
    if (n % 20 === 0) process.stderr.write(`${n} `);
  }
  if (n) { fs.mkdirSync(path.dirname(cachePath), { recursive: true }); fs.writeFileSync(cachePath, JSON.stringify(cache)); process.stderr.write(`\nanalysed ${n} games -> ${path.relative(REPO, cachePath)}\n`); }
  const list = games.filter(g => !ONLY || ONLY.has(g.gameId)).map(g => hydrate(cache.games[g.gameId]));
  return { list, names };
}
function hydrate(g) {
  return { ...g, deaths: g.deaths.map(a => obj(DEATH_COLS, a)), splits: g.splits.map(a => obj(SPLIT_COLS, a)), lives: g.lives.map(a => obj(LIFE_COLS, a)) };
}

// ---------- 집계 도우미 ----------
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN;
const median = a => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; };
const sum = (a, f = x => x) => a.reduce((s, x) => s + f(x), 0);
const fx = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '-';
const pc = (n, d, k = 0) => d ? (100 * n / d).toFixed(k) : '-';
const at = (g, r) => { const i = FLOW_COLS; const row = g.flow.find(x => x[0] === r) || g.flow[g.flow.length - 1]; return obj(i, row); };
// 우리 드래곤 사망 분류: 머리끼리(적이 들이받음 / 우리가 들이받음 / 아군끼리), 남의 몸(적 / 아군), 해초, 자기 몸, 행동 불능
const CAUSES = ['H-rammed', 'H-weRam', 'H-ally', 'O-enemy', 'O-ally', 'W', 'S', 'A'];
const CAUSE_KO = { 'H-rammed': '머리끼리: 적이 들이받음', 'H-weRam': '머리끼리: 우리가 들이받음', 'H-ally': '머리끼리: 아군끼리', 'O-enemy': '남의 몸: 적 몸',
  'O-ally': '남의 몸: 아군 몸', W: '해초(벽)', S: '자기 몸', A: '행동 불능' };
function cause(d) {
  if (d.reason === 'H') { if (d.partnerSide === d.side) return 'H-ally'; return d.actor === 'self' ? 'H-weRam' : 'H-rammed'; }
  if (d.reason === 'O') return (d.fatal || '').startsWith('enemy') ? 'O-enemy' : 'O-ally';
  return d.reason;
}
function groupsOf(list) {
  const lost = list.filter(g => !g.won), won = list.filter(g => g.won);
  return [...FOCUS.map(t => [String(t), list.filter(g => g.opp === t)]),
    ['중점 7팀', list.filter(g => FOCUS.includes(g.opp))],
    ['그 밖(우리 패)', lost.filter(g => !FOCUS.includes(g.opp))],
    ['그 밖(우리 승)', won.filter(g => !FOCUS.includes(g.opp))],
    ['전체', list]].filter(([, gs]) => gs.length);
}
const table = (head, rows) => ['| ' + head.join(' | ') + ' |', '|' + head.map(() => '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');

// ---------- 보고서 ----------
function report(list, names) {
  const out = [];
  const P = s => out.push(s);
  const nm = t => names.get(+t) ? `${t} (${names.get(+t)})` : t;
  const G = groupsOf(list);
  P(`# 온라인 관측 집계 (자동 생성: node tools/observe_online.js --report)`);
  P('');
  P(`경기 ${list.length}판, 우리 ${list.filter(g => g.won).length}승 ${list.filter(g => !g.won).length}패. 배치: ` +
    [...new Set(list.map(g => g.batch))].map(b => `${b} ${list.filter(g => g.batch === b).length}판(${list.find(g => g.batch === b).bot})`).join(', '));
  P('');

  P('## 1. 결과와 끝 상태');
  P(table(['상대', '판', '승-패', '우리 전멸', '끝 라운드 평균', '최장 우리:상대(끝)', '총길이 우리:상대(끝)', '유닛 우리:상대(끝)', '최장 역전 라운드 중앙값(해당 판)'],
    G.map(([k, gs]) => {
      const behind = gs.map(g => { let b = null; for (const row of g.flow) { const f = obj(FLOW_COLS, row); if (f.longUs < f.longThem) { if (b == null) b = f.round === 'end' ? g.lastRound : f.round; } else b = null; } return b; }).filter(x => x != null);
      return [nm(k), gs.length, `${gs.filter(g => g.won).length}-${gs.filter(g => !g.won).length}`, gs.filter(g => !g.won && g.endReason === 'teamEliminated').length,
        fx(mean(gs.map(g => g.lastRound)), 0), `${fx(mean(gs.map(g => g.final.us.longestDragon)))}:${fx(mean(gs.map(g => g.final.them.longestDragon)))}`,
        `${fx(mean(gs.map(g => g.final.us.totalLength)), 0)}:${fx(mean(gs.map(g => g.final.them.totalLength)), 0)}`,
        `${fx(mean(gs.map(g => g.final.us.dragonCount)))}:${fx(mean(gs.map(g => g.final.them.dragonCount)))}`, `${fx(median(behind), 0)} (${behind.length})`];
    })));
  P('');

  P('## 2. 우리 드래곤 사망 원인 (판당 횟수 / 판당 잃은 길이)');
  P(table(['상대', ...CAUSES.map(c => CAUSE_KO[c]), '합계'], G.map(([k, gs]) => {
    const ds = gs.flatMap(g => g.deaths.filter(d => d.side === 0));
    return [nm(k), ...CAUSES.map(c => { const x = ds.filter(d => cause(d) === c); return `${fx(x.length / gs.length)} / ${fx(sum(x, d => d.len) / gs.length)}`; }),
      `${fx(ds.length / gs.length)} / ${fx(sum(ds, d => d.len) / gs.length)}`];
  })));
  P('');
  P('### 2-1. 길이 6 이상 우리 드래곤의 사망 (판당 횟수)');
  P(table(['상대', ...CAUSES.map(c => CAUSE_KO[c]), '합계', '해초·자기 몸 사망 중 빈 칸 0(갇힘) 비율(모든 길이)'], G.map(([k, gs]) => {
    const ds = gs.flatMap(g => g.deaths.filter(d => d.side === 0));
    const big = ds.filter(d => d.len >= BIG), ws = ds.filter(d => d.reason === 'W' || d.reason === 'S');
    return [nm(k), ...CAUSES.map(c => fx(big.filter(d => cause(d) === c).length / gs.length, 2)), fx(big.length / gs.length, 2), `${pc(ws.filter(d => d.free === 0).length, ws.length)}% (${ws.length})`];
  })));
  P('');
  P('### 2-2. 적이 우리 머리를 들이받은 사망(H-rammed)의 세부');
  P(table(['상대', '횟수', '우리 길이 평균', '우리 길이>=6', '들이받은 적 길이 중앙값', '적 길이<=3', '적이 분열로 태어남', '적이 여러 칸 질주로 들이받음', '우리 직전 결정 때 7x7 안', '그때 체비쇼프 거리 중앙값'],
    G.map(([k, gs]) => {
      const r = gs.flatMap(g => g.deaths.filter(d => d.side === 0 && cause(d) === 'H-rammed'));
      const seen = r.filter(d => d.rammerSeen != null);
      return [nm(k), r.length, fx(mean(r.map(d => d.len))), r.filter(d => d.len >= BIG).length, fx(median(r.map(d => d.moverLen)), 0),
        `${pc(r.filter(d => d.moverLen <= SMALL).length, r.length)}%`, `${pc(r.filter(d => d.moverFromSplit === 1).length, r.length)}%`, `${pc(r.filter(d => d.moverSteps > 1).length, r.length)}%`,
        `${pc(seen.filter(d => d.rammerSeen).length, seen.length)}%`, fx(median(seen.map(d => d.rammerCheb)), 0)];
    })));
  P('');
  P('### 2-3. 머리끼리 맞교환(우리 대 상대 쌍)');
  P(table(['상대', '쌍 수', '우리 잃은 길이', '상대 잃은 길이', '비(우리/상대)', '우리>=6 대 상대<=3', '상대가 움직인 쌍', '우리가 움직인 쌍'], G.map(([k, gs]) => {
    const p = gs.flatMap(g => g.deaths.filter(d => d.side === 0 && d.reason === 'H' && d.partnerSide === 1));
    const ol = sum(p, d => d.len), tl = sum(p, d => d.partnerLen);
    return [nm(k), p.length, ol, tl, fx(ol / tl, 2), p.filter(d => d.len >= BIG && d.partnerLen <= SMALL).length, p.filter(d => d.actor === 'enemy').length, p.filter(d => d.actor === 'self').length];
  })));
  P('');
  P('### 2-4. 우리가 적 몸에 박은 사망(O-enemy)');
  P(table(['상대', '횟수', '몸 주인 길이 중앙값', '주인 길이<=3', '빈 칸 0(갇힘)'], G.map(([k, gs]) => {
    const o = gs.flatMap(g => g.deaths.filter(d => d.side === 0 && cause(d) === 'O-enemy'));
    return [nm(k), o.length, fx(median(o.map(d => d.ownerLen)), 0), o.filter(d => d.ownerLen <= SMALL).length, o.filter(d => d.free === 0).length];
  })));
  P('');

  P('## 3. 라운드별 흐름 (평균; 전멸한 판은 끝 상태를 이어 씀)');
  const RR = [50, 100, 200, 300, 400, 450, 'end'];
  for (const [lab, a, b] of [['최장', 'longUs', 'longThem'], ['총길이', 'totUs', 'totThem'], ['유닛 수', 'nUs', 'nThem'], ['길이<=3 유닛 수', 'smallUs', 'smallThem']]) {
    P(`### ${lab} 우리:상대`);
    P(table(['상대', ...RR.map(r => `r${r}`)], G.map(([k, gs]) => [nm(k), ...RR.map(r => `${fx(mean(gs.map(g => at(g, r)[a])), lab === '총길이' ? 0 : 1)}:${fx(mean(gs.map(g => at(g, r)[b])), lab === '총길이' ? 0 : 1)}`)])));
    P('');
  }

  P('## 4. 분열 (상대; 마지막 줄은 우리)');
  const splitRow = (k, gs, sd) => {
    const sp = gs.map(g => g.splits.filter(s => s.side === sd)), all = sp.flat();
    const first = sp.map(a => a.length ? a[0].round : null).filter(x => x != null);
    const ph = [0, 0, 0, 0, 0]; for (const s of all) ph[Math.min(4, Math.floor(s.round / 100))]++;
    const ch = { 2: 0, 3: 0, 4: 0, '5+': 0 }; for (const s of all) ch[s.child >= 5 ? '5+' : s.child]++;
    return [k, fx(all.length / gs.length, 0), `${fx(median(first), 0)} (${first.length}/${gs.length})`, ph.map(x => fx(x / gs.length, 0)).join('/'),
      Object.values(ch).map(x => pc(x, all.length)).join('/'), `${pc(all.filter(s => s.parent === 2).length, all.length)}%`, fx(median(all.map(s => s.before)), 0),
      `${pc(all.filter(s => s.parentLeader).length, all.length)}%`];
  };
  P(table(['상대', '판당 분열', '첫 분열 라운드 중앙값', '100라운드 구간별 판당 분열(0/100/200/300/400)', '자식 길이 2/3/4/5+ (%)', '분열 뒤 부모 길이 2', '분열 전 길이 중앙값', '최장이 분열'],
    [...G.map(([k, gs]) => splitRow(nm(k), gs, 1)), splitRow('우리(전체)', list, 0)]));
  P('');

  P('## 5. 작은 조각(분열로 태어날 때 길이<=3)의 쓰임');
  const pieceRow = (k, gs, sd) => {
    const P0 = gs.flatMap(g => g.lives.filter(l => l.side === sd && l.fromSplit === 1 && l.bornLen <= SMALL).map(l => ({ ...l, g })));
    const lifeLen = P0.map(l => (l.died ?? l.g.lastRound) - l.born);
    const fate = { alive: 0, 'H-enemy': 0, 'H-ally': 0, O: 0, W: 0, S: 0, A: 0 };
    for (const l of P0) {
      if (l.died == null) { fate.alive++; continue; }
      if (l.reason === 'H') { const d = l.g.deaths.find(x => x.id === l.id && x.reason === 'H'); fate[d && d.partnerSide != null && d.partnerSide !== sd ? 'H-enemy' : 'H-ally']++; }
      else fate[l.reason] = (fate[l.reason] || 0) + 1;
    }
    const turns = sum(P0, l => l.turns);
    return [k, fx(P0.length / gs.length, 0), fx(median(lifeLen), 0), `${pc(P0.filter(l => l.maxLen <= SMALL).length, P0.length)}%`,
      Object.values(fate).map(x => pc(x, P0.length)).join('/'), `${pc(sum(P0, l => l.contactTurns), turns)}% / ${pc(sum(P0, l => l.closeTurns), turns)}% / ${pc(sum(P0, l => l.nearBigTurns), turns)}%`,
      fx(median(P0.map(l => l.farthest)), 0), fx(sum(P0, l => l.eats) / P0.length, 2), fx(sum(P0, l => l.pings) / turns, 2)];
  };
  P(table(['상대', '판당 조각', '수명 중앙값(라운드)', '끝까지 길이<=3', '운명 %: 생존/적과 머리끼리/아군과 머리끼리/남의 몸/해초/자기 몸/행동 불능',
    '턴 비율: 7x7 안 적 / 맨해튼 2 안 적 머리 / 7x7 안 큰 적', '태어난 곳에서 가장 먼 거리 중앙값', '조각당 먹은 진주', '턴당 음파'],
    [...G.map(([k, gs]) => pieceRow(nm(k), gs, 1)), pieceRow('우리(전체)', list, 0)]));
  P('');

  P('## 6. 음파');
  const sonarRow = (k, gs, who) => {
    const s = gs.map(g => g.sonar[who]); const Pn = sum(s, x => x.pings), A = sum(s, x => x.actions), PT = sum(s, x => x.pingTurns);
    const fp = s.map(x => x.firstPing).filter(x => x != null);
    const pt = [1, 2, 3, 4].map(i => sum(s, x => x.perTurn[i])), pd = [1, 2, 3, 4].map(i => sum(s, x => x.perTurnDistinct[i]));
    const di = ['N', 'E', 'S', 'W'].map(c => sum(s, x => x.dirIntended[c]));
    const hk = ['self', 'ally', 'allyHead', 'enemy', 'enemyHead', 'kelp', 'lost'].map(c => sum(s, x => x.hits[c]));
    const bits = new Array(64).fill(0); for (const x of s) x.bit1.forEach((c, i) => { bits[i] += c; });
    const nz = Pn - sum(s, x => x.zero);
    const cons = bits.filter(c => nz && (c === 0 || c === nz)).length, rnd = bits.filter(c => nz && Math.abs(c / nz - 0.5) < 0.03).length;
    return [k, fx(Pn / gs.length, 0), `${pc(PT, A)}%`, `${fx(median(fp), 0)} (${fp.length}/${gs.length})`, pt.map(x => pc(x, PT)).join('/'),
      Pn ? di.map(x => pc(x, Pn)).join('/') : '-', Pn ? hk.map(x => pc(x, Pn)).join('/') : '-', Pn ? `${pc(sum(s, x => x.zero), Pn)}%` : '-',
      fx(mean(s.filter(x => x.pings).map(x => x.distinct / x.pings)), 2), PT ? pd.map(x => pc(x, PT)).join('/') : '-',
      Pn && (/^\d+/.test(k) || k.startsWith('우리')) ? `${cons}/${rnd}` : '-'];   // 여러 팀을 합친 줄의 비트 통계는 뜻이 없다
  };
  P(table(['팀', '판당 음파', '음파 보낸 턴 비율', '첫 음파 라운드 중앙값', '한 턴 음파 수 1/2/3/4 (%)', '의도 방향 N/E/S/W (%)',
    '닿은 곳 자기/아군 몸/아군 머리/적 몸/적 머리/해초/소실 (%)', '값 0', '서로 다른 값/음파', '한 턴 안 서로 다른 값 수 1/2/3/4 (%)', '고정 비트/무작위형 비트(64 중)'],
    [...G.map(([k, gs]) => sonarRow(nm(k), gs, 'them')), sonarRow('우리(전체)', list, 'us')]));
  const allS = list.flatMap(g => [g.sonar.us, g.sonar.them]);
  P('');
  P(`검산: 리플레이 에코 종류(24바이트)와 기하 판정(hitId·해초 모서리)이 어긋난 음파 ${sum(allS, x => x.echoMismatch)}건 / 전체 ${sum(allS, x => x.pings)}건.`);
  P('');
  P('### 6-1. 팀별 가장 흔한 값(64비트, 16진수, 모든 판 합)');
  for (const t of FOCUS) {
    const gs = list.filter(g => g.opp === t); if (!gs.length) continue;
    const m = new Map(); for (const g of gs) for (const [v, c] of g.sonar.them.topValues) m.set(v, (m.get(v) || 0) + c);
    const tot = sum(gs, g => g.sonar.them.pings);
    P(`- ${nm(t)}: ` + [...m].sort((a, b) => b[1] - a[1]).slice(0, 4).map(([v, c]) => `${v} (${pc(c, tot, 1)}%)`).join(', '));
  }
  P('');

  P('## 7. 모이기(후반 길이 집중)와 진주 출처');
  P(table(['상대', '상대 최장/총길이 r200/r300/r400/r450/끝', '상대 최장 r300→r400→끝', '상대 유닛 r400→끝', '상대 최장이 먹은 진주(판당, r300+) 생성/자기 팀 주검/우리 주검',
    '상대가 먹은 진주(판당) 생성/자기 팀 주검/우리 주검', '우리가 먹은 진주(판당) 생성/자기 팀 주검/상대 주검'], G.map(([k, gs]) => {
    const sh = r => fx(mean(gs.map(g => { const f = at(g, r); return f.totThem ? f.longThem / f.totThem : NaN; }).filter(Number.isFinite)), 2);
    const le = c => sum(gs, g => g.sonar.them.leaderEats[c][3] + g.sonar.them.leaderEats[c][4]) / gs.length;
    const e = (who, c) => sum(gs, g => sum(g.sonar[who].eats[c])) / gs.length;
    return [nm(k), [200, 300, 400, 450, 'end'].map(sh).join('/'), [300, 400, 'end'].map(r => fx(mean(gs.map(g => at(g, r).longThem)))).join('→'),
      `${fx(mean(gs.map(g => at(g, 400).nThem)))}→${fx(mean(gs.map(g => at(g, 'end').nThem)))}`, ['spawn', 'own', 'enemy'].map(c => fx(le(c))).join('/'),
      ['spawn', 'own', 'enemy'].map(c => fx(e('them', c), 0)).join('/'), ['spawn', 'own', 'enemy'].map(c => fx(e('us', c), 0)).join('/')];
  })));
  P('');

  P('## 8. 지도별');
  const maps = [...new Set(list.map(g => g.map))].sort();
  P(table(['지도', '판', '승-패', '중점 7팀 상대 승-패', '우리 전멸', '최장 우리:상대(끝)', '상대 유닛 r200', '판당 상대 분열', '판당 우리 큰 드래곤(>=6)이 들이받혀 죽음', '해초·자기 몸으로 죽은 우리 드래곤(판당)'], maps.map(m => {
    const gs = list.filter(g => g.map === m), fg = gs.filter(g => FOCUS.includes(g.opp));
    const ds = gs.flatMap(g => g.deaths.filter(d => d.side === 0));
    return [m, gs.length, `${gs.filter(g => g.won).length}-${gs.filter(g => !g.won).length}`, `${fg.filter(g => g.won).length}-${fg.filter(g => !g.won).length}`,
      gs.filter(g => !g.won && g.endReason === 'teamEliminated').length, `${fx(mean(gs.map(g => g.final.us.longestDragon)))}:${fx(mean(gs.map(g => g.final.them.longestDragon)))}`,
      fx(mean(gs.map(g => at(g, 200).nThem))), fx(mean(gs.map(g => g.splits.filter(s => s.side === 1).length)), 0),
      fx(ds.filter(d => d.len >= BIG && cause(d) === 'H-rammed').length / gs.length, 2), fx(ds.filter(d => d.reason === 'W' || d.reason === 'S').length / gs.length, 1)];
  })));
  P('');
  P('### 8-1. 중점 팀 × 지도 (결과, 끝 최장 우리:상대, 전멸 라운드)');
  for (const t of FOCUS) {
    const gs = list.filter(g => g.opp === t); if (!gs.length) continue;
    P(`- ${nm(t)}: ` + gs.map(g => `${g.map} ${g.won ? '승' : '패'}(${g.final.us.longestDragon}:${g.final.them.longestDragon}${g.endReason === 'teamEliminated' ? `, r${g.lastRound} 전멸` : ''})`).join('; '));
  }
  console.log(out.join('\n'));
}

// ---------- 핵심 지표 비교(온라인 묶음과 로컬 평가를 같은 정의로) ----------
function keyTable(groups) {
  const head = ['묶음', '판', '승-패', '판당 우리 큰(>=6) 드래곤이 적에게 들이받힘', '판당 우리 드래곤이 적에게 들이받힘', '들이받은 적 길이<=3', '들이받은 적 질주(2칸+)',
    '결정 때 7x7 안', '머리끼리 잃은 길이 비(우리/상대)', '판당 해초·자기 몸 사망(우리)', '판당 상대 분열', '상대 유닛 r200', '판당 상대 음파', '상대 음파 턴 비율', '끝 최장 우리:상대'];
  return table(head, groups.map(([k, gs]) => {
    const ds = gs.flatMap(g => g.deaths.filter(d => d.side === 0)), r = ds.filter(d => cause(d) === 'H-rammed'), seen = r.filter(d => d.rammerSeen != null);
    const pr = ds.filter(d => d.reason === 'H' && d.partnerSide === 1);
    const s = gs.map(g => g.sonar.them);
    return [k, gs.length, `${gs.filter(g => g.won).length}-${gs.filter(g => !g.won).length}`, fx(r.filter(d => d.len >= BIG).length / gs.length, 2), fx(r.length / gs.length, 1),
      `${pc(r.filter(d => d.moverLen <= SMALL).length, r.length)}%`, `${pc(r.filter(d => d.moverSteps > 1).length, r.length)}%`, `${pc(seen.filter(d => d.rammerSeen).length, seen.length)}%`,
      fx(sum(pr, d => d.len) / sum(pr, d => d.partnerLen), 2), fx(ds.filter(d => d.reason === 'W' || d.reason === 'S').length / gs.length, 1),
      fx(mean(gs.map(g => g.splits.filter(x => x.side === 1).length)), 0), fx(mean(gs.map(g => at(g, 200).nThem)), 1), fx(sum(s, x => x.pings) / gs.length, 0),
      `${pc(sum(s, x => x.pingTurns), sum(s, x => x.actions))}%`, `${fx(mean(gs.map(g => g.final.us.longestDragon)))}:${fx(mean(gs.map(g => g.final.them.longestDragon)))}`];
  }));
}

// ---------- 음파 비트 구역 해독 시도 ----------
function decode(team, maxSamples = 30000) {
  const { games } = listGames();
  const FEAT = ['round', 'id', 'len', 'headX', 'headY', 'preX', 'preY', 'tailX', 'tailY', 'dirIntended', 'units', 'headIdx', 'preIdx', 'leaderLen', 'leaderX', 'leaderY'];
  const samples = []; let tot = 0, zero = 0, seed = 12345;
  const rand = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };   // 결정적 표본 추출
  for (const g of games.filter(x => x.opponentTeam === team)) {
    const R = parser().parseReplay(fs.readFileSync(path.join(g.dir, `M${g.gameId}.replay`)));
    const st = R.match.roundAt(0).copy(), bodies = st.bodies, W = st.map.width, H = st.map.height;
    const them = g.ourSide.toUpperCase() === 'A' ? 'B' : 'A';
    let started = false, round = -1; const pre = new Map();
    for (const e of R.events) {
      if (e.type === 'roundStart') { started = true; round = e.round; }
      if (!started) continue;
      if (e.type === 'dragonAction') { const x = bodies.dragons.get(e.id); if (x) pre.set(e.id, { ...x.body[0] }); }
      if (e.type === 'sonarPing') {
        const s = bodies.dragons.get(e.senderId); if (!s || s.team !== them) continue;
        tot++; if (e.value64 === '0000000000000000') { zero++; continue; }
        if (samples.length >= maxSamples && rand() > maxSamples / (tot - zero)) continue;
        const h = s.body[0], p = pre.get(e.senderId) || h, t = s.body[s.body.length - 1];
        let units = 0, ld = null; for (const x of bodies.dragons.values()) if (x.team === them) { units++; if (!ld || x.body.length > ld.body.length) ld = x; }
        let dI = D.indexOf(e.direction);
        if (s.body.length > 1 && (e.origin.x !== h.x || e.origin.y !== h.y)) { const nk = s.body[1]; const dx = ((nk.x - h.x) % W + W) % W, dy = ((nk.y - h.y) % H + H) % H; dI = dy === H - 1 ? 0 : dx === 1 ? 1 : dy === 1 ? 2 : dx === W - 1 ? 3 : -1; }
        const f = [round, e.senderId, s.body.length, h.x, h.y, p.x, p.y, t.x, t.y, dI, units, h.y * W + h.x, p.y * W + p.x, ld.body.length, ld.body[0].x, ld.body[0].y];
        const smp = { hi: parseInt(e.value64.slice(0, 8), 16), lo: parseInt(e.value64.slice(8), 16), f };
        if (samples.length < maxSamples) samples.push(smp); else samples[Math.floor(rand() * maxSamples)] = smp;
      }
      if (['dragonUpdate', 'dragonSplit', 'dragonDeath'].includes(e.type)) bodies.applyEvent(e);
    }
  }
  const field = (s, st, w) => { if (st >= 32) return Math.floor(s.hi / 2 ** (st - 32)) % 2 ** w; if (st + w <= 32) return Math.floor(s.lo / 2 ** st) % 2 ** w; const lw = 32 - st; return Math.floor(s.lo / 2 ** st) % 2 ** lw + (s.hi % 2 ** (w - lw)) * 2 ** lw; };
  const bit1 = new Array(64).fill(0); for (const s of samples) for (let b = 0; b < 64; b++) if (field(s, b, 1)) bit1[b]++;
  console.log(`team ${team}: pings ${tot}, value 0: ${zero} (${pc(zero, tot)}%), nonzero samples ${samples.length}`);
  console.log('bit 1-frequency % (row = bits 63..48, 47..32, 31..16, 15..0):');
  for (let r = 0; r < 4; r++) { let line = ''; for (let b = 63 - 16 * r; b > 47 - 16 * r; b--) line += String(Math.round(100 * bit1[b] / Math.max(1, samples.length))).padStart(4); console.log(line); }
  const hits = [], FV = FEAT.map((_, k) => samples.map(s => s.f[k]));
  for (let w = 2; w <= 12; w++) {
    const M = 2 ** w, live = FEAT.map((_, k) => new Set(FV[k].map(v => v % M)).size > 1);   // 표본 안에서 변하는 특징만
    for (let st = 0; st + w <= 64; st++) {
      const vals = samples.map(s => field(s, st, w));
      if (new Set(vals).size <= 1) continue;   // 고정 구역은 건너뜀
      for (let k = 0; k < FEAT.length; k++) {
        if (!live[k]) continue;
        const fv = FV[k]; let c = 0; for (let i = 0; i < samples.length; i++) if (fv[i] >= 0 && fv[i] % M === vals[i]) c++;
        if (c / samples.length >= 0.6) hits.push([c / samples.length, FEAT[k], st, w]);
      }
    }
  }
  hits.sort((a, b) => b[0] - a[0] || b[3] - a[3]);
  const seen = new Set(); let n = 0;
  console.log('bit fields matching the sender state (>= 60%, widest first per feature/start):');
  for (const [r, f, st, w] of hits) { const k = `${f}:${st}`; if (seen.has(k)) continue; seen.add(k); console.log(`  bits ${st}..${st + w - 1} (w${w}) == ${f} mod 2^${w}: ${(100 * r).toFixed(1)}%`); if (++n >= 20) break; }
  if (!n) console.log('  (none)');
}

// ---------- 한 경기 이야기 ----------
function story(list, names, gid) {
  const g = list.find(x => x.gameId === gid); if (!g) throw Error(`game ${gid} not in data`);
  const L = [];
  L.push(`### ${gid} — ${g.map}, 우리(${g.side}) 대 ${g.opp}${names.get(g.opp) ? ` (${names.get(g.opp)})` : ''}, ${g.won ? '승' : '패'} (${g.endReason}, r${g.lastRound})`);
  L.push(`- 끝: 최장 ${g.final.us.longestDragon}:${g.final.them.longestDragon}, 총길이 ${g.final.us.totalLength}:${g.final.them.totalLength}, 유닛 ${g.final.us.dragonCount}:${g.final.them.dragonCount}`);
  L.push('- 흐름(최장/총길이/유닛, 우리 | 상대): ' + [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 'end'].map(r => { const f = at(g, r); return `r${r} ${f.longUs}/${f.totUs}/${f.nUs} | ${f.longThem}/${f.totThem}/${f.nThem}`; }).join('; '));
  const big = g.deaths.filter(d => d.side === 0 && d.len >= BIG);
  L.push(`- 우리 길이>=6 사망 ${big.length}건: ` + big.map(d => `r${d.round} L${d.len} ${CAUSE_KO[cause(d)]}` + (cause(d) === 'H-rammed' ? `(적 L${d.moverLen}, ${d.moverSteps}칸, 결정 때 거리 ${d.rammerCheb})` : '')).join('; '));
  const sp = g.splits.filter(s => s.side === 1);
  L.push(`- 상대 분열 ${sp.length}회(첫 r${sp[0]?.round ?? '-'}), 우리 분열 ${g.splits.filter(s => s.side === 0).length}회`);
  const s = g.sonar.them; L.push(`- 상대 음파 ${s.pings}회(첫 r${s.firstPing ?? '-'}), 값 0 ${s.zero}회, 서로 다른 값 ${s.distinct}개`);
  console.log(L.join('\n'));
}

module.exports = { analyseGame, listGames, listLocal, loadAll, hydrate, parser, cause, keyTable, DEATH_COLS, SPLIT_COLS, LIFE_COLS, FLOW_COLS };
if (require.main === module) {
  if (flag('--decode')) decode(+opt('--decode', 0));
  else if (flag('--local')) {
    // 로컬 평가와 온라인 묶음을 같은 정의로 나란히 본다: node tools/observe_online.js --local exp/eval-r1
    const dir = path.resolve(REPO, opt('--local', 'exp/eval-r1'));
    const loc = loadAll(flag('--refresh'), dir).list, on = loadAll(false).list;
    const opps = [...new Set(loc.map(g => g.opp))].sort();
    console.log(`## 핵심 지표: 온라인(옛 봇 g1/g2) 대 로컬 ${path.basename(dir)} (${loc[0]?.bot ?? ''})\n`);
    console.log(keyTable([['온라인: 중점 7팀', on.filter(g => FOCUS.includes(g.opp))], ['온라인: 그 밖(우리 패)', on.filter(g => !g.won && !FOCUS.includes(g.opp))],
      ['온라인: 그 밖(우리 승)', on.filter(g => g.won && !FOCUS.includes(g.opp))], ['온라인: 전체', on],
      ...opps.map(o => [`로컬: ${o}`, loc.filter(g => g.opp === o)]), ['로컬: 전체', loc]]));
  } else {
    const { list, names } = loadAll(flag('--refresh'));
    if (flag('--story')) story(list, names, +opt('--story', 0));
    else report(list, names);
  }
}
