#!/usr/bin/env node
// Prisoners Dilemma 두 판본(시작 드래곤 6마리 / 10마리)에서 우리 봇이 어떻게 지는지 경기별로 센다.
// usage (저장소 루트에서):
//   node exp/cand-pd10a/pd10_study.js --online                       온라인 기준점 세 세트(baseline-r1, -r1b, -r1c)의 PD 21판
//   node exp/cand-pd10a/pd10_study.js --eval exp/<평가 폴더> [--json out.json]   로컬 평가 폴더(rows.jsonl + games/<key>/game.replay)
//   --games : 경기별 한 줄도 찍는다.
// 방법: tools/baseline_study.js의 analyse()로 리플레이를 걸음 단위로 다시 재현한다(사망 원인, 먹이 출처, 흐름). 점검 값이 모두 0인지 확인한다.
// 정의:
//   판본 = 시작 드래곤 수(6 또는 10). 시작 계통 = 우리 가장 긴 시작 드래곤, 분열할 때마다 더 긴 조각을 따라간다(같으면 자식).
//   고리 위상 = 시작 계통의 탈출 분열 자식 길이의 최빈값(10이면 자식 머리가 옆이 막힌 y=3/12, 9면 옆이 열린 y=4/11에서 태어난다).
//   계통 끝 = 시작 계통의 마지막 조각이 죽은 라운드와 원인. 계통 박힘 = 시작 계통 조각(길이 6 이상)이 적에게 박혀 죽음.
//   덤 드래곤 = 우리 쪽 시작 드래곤 중 길이 2인 것(10마리 판본에만 있다).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const BS = require(path.join(ROOT, 'tools/baseline_study.js'));

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const SETS = ['baseline-r1', 'baseline-r1b', 'baseline-r1c'];

function listOnline() {
  const out = [];
  for (const set of SETS) {
    const dir = path.join(ROOT, 'data/online', set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
    for (const g of idx.games) {
      if (g.mapName !== 'Prisoners Dilemma') continue;
      out.push({ file: path.join(dir, `M${g.gameId}.replay`), g: { ...g, set }, key: `${set}:${g.gameId}`, opp: String(g.opponentTeam) });
    }
  }
  return out;
}
function listEval(dir) {
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
  const seen = new Set();
  return rows.filter(r => r.map.startsWith('prisoners_dilemma') && !seen.has(r.key) && seen.add(r.key)).map(r => ({
    file: path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'), key: r.key, opp: r.opp, row: r,
    g: { gameId: r.key, set: path.basename(dir), mapName: 'Prisoners Dilemma', ourSide: r.side, opponentTeam: r.opp, ourWin: r.won, ranked: false, ourSubmission: 0 },
  }));
}

const mode = (a) => { const c = {}; for (const x of a) c[x] = (c[x] || 0) + 1; let b = null; for (const [k, v] of Object.entries(c)) if (b === null || v > c[b]) b = k; return b === null ? null : +b; };

function study(t) {
  const R = load(t.file);
  const rec = BS.analyse(R, t.g);
  const US = String(t.g.ourSide).toUpperCase();
  const nd = R.match.map.initialDragons.length;
  const ours = R.match.map.initialDragons.filter(d => d.team === US);
  const start = ours.reduce((b, d) => (!b || d.body.length > b.body.length ? d : b), null);
  const extras = ours.filter(d => d.body.length === 2).map(d => d.id);
  // 시작 계통: 분열마다 더 긴 조각(같으면 자식)
  const lenOf = new Map(ours.map(d => [d.id, d.body.length]));
  let lin = start.id; const linIds = new Set([lin]);
  const escChild = [], escY = [];
  let lastEsc = null, escCount = 0;
  for (const s of rec.splits[0]) {
    const [r, lenBefore, cl, , , kind, pid, cid] = s;
    if (pid !== lin) continue;
    if (kind === 'escape') { escCount++; escChild.push(cl); lastEsc = r; }
    const parentLen = lenBefore - cl;
    if (cl >= parentLen) { lin = cid; }
    linIds.add(cid); linIds.add(pid);
  }
  // 계통 조각의 사망: 시작 계통으로 이어진 모든 id 중 길이 6 이상 사망
  const deaths = rec.deaths.filter(d => d.side === 0);
  const linBig = deaths.filter(d => linIds.has(d.id) && d.len >= 6);
  const linEnd = deaths.find(d => d.id === lin) || null;       // 마지막으로 따라간 조각
  const rammed = deaths.filter(d => d.cls2 === 'H-rammed');
  const rammedBig = rammed.filter(d => d.len >= 6);
  const extraFate = extras.map(id => { const d = deaths.find(x => x.id === id); return d ? { id, r: d.r, len: d.len, cls: d.cls2, byLen: d.by ? d.by.len : null } : { id, r: null }; });
  const flowAt = (si, m, r) => { const a = rec.flow[si][m]; return r < a.length ? a[r] : a[a.length - 1]; };
  const nat = si => rec.eat[si].nat.reduce((a, b) => a + b, 0), own = si => rec.eat[si].own.reduce((a, b) => a + b, 0), opp = si => rec.eat[si].opp.reduce((a, b) => a + b, 0);
  const G = rec.final[0].units > 0 ? rec.final[0].longest : 0;
  const bad = Object.values(rec.checks).reduce((a, b) => a + b, 0) + (rec.mass.every(m => m.ok) ? 0 : 1) + (rec.finalMatch ? 0 : 1);
  // 처음 적에게 박힌 계통 조각(길이 6 이상)
  const firstLinRam = linBig.filter(d => d.cls2 === 'H-rammed').sort((a, b) => a.r - b.r)[0] || null;
  // 계통의 탈출 분열 자식이 태어난 칸: 목 말고 해초가 아닌 변이 2개 이상이면 '열린 칸'(옆에서 박힐 수 있다).
  //   태어난 라운드에 첫 행동 전에 죽으면 '태어나자마자 박힘', 첫 걸음이 바라보는 쪽이 아니면 '옆으로 나감'.
  const geo = BS.buildGeo(R.match.map), escKids = new Set();
  { let l2 = start.id; for (const s of rec.splits[0]) { const [, lenBefore, cl, , , kind, pid, cid] = s; if (pid !== l2) continue; if (kind === 'escape') escKids.add(cid); if (cl >= lenBefore - cl) l2 = cid; } }
  const births = new Map(); let round = -1, pocketEats = 0;
  const DIRS = 'NESW';
  for (const e of R.events) {
    if (e.type === 'roundStart') { round = e.round; continue; }
    if (e.type === 'dragonIndicator' && /^pocket-eat/.test(e.text || '')) { pocketEats++; continue; }
    if (e.type === 'dragonSplit' && escKids.has(e.childId)) {
      const h = e.childBody[0].y * geo.W + e.childBody[0].x, nk = e.childBody[1].y * geo.W + e.childBody[1].x;
      let open = 0; for (let k = 0; k < 4; k++) { const u = geo.nb[h * 4 + k]; if (u >= 0 && u !== nk) open++; }
      births.set(e.childId, { r: round, y: e.childBody[0].y, exposed: open >= 2, facing: e.childFacing, acted: false, diedAtBirth: false, turned: false });
      continue;
    }
    if (e.type === 'dragonAction' && births.has(e.id)) { const b = births.get(e.id); if (!b.acted) { b.acted = true; const a = e.action; if (a && a.kind === 'move' && a.steps[0] !== b.facing) b.turned = true; } continue; }
    if (e.type === 'dragonDeath' && births.has(e.id)) { const b = births.get(e.id); if (!b.acted && round === b.r) b.diedAtBirth = true; continue; }
  }
  const B = [...births.values()];
  return {
    key: t.key, opp: t.opp, nd, ver: t.row ? t.row.map : 'n' + nd, win: !!t.g.ourWin, end: rec.endReason, rounds: rec.rounds, G, total: rec.final[0].total, theirLongest: rec.final[1].longest,
    eliminated: rec.final[0].units === 0,
    escCount, lastEsc, phase: mode(escChild), escChild: escChild.slice(0, 8),
    linEnd: linEnd ? { r: linEnd.r, len: linEnd.len, cls: linEnd.cls2, byLen: linEnd.by ? linEnd.by.len : null, bySteps: linEnd.by ? linEnd.by.steps : null } : null,
    linAliveEnd: !linEnd, firstLinRam: firstLinRam ? { r: firstLinRam.r, len: firstLinRam.len, byLen: firstLinRam.by ? firstLinRam.by.len : null } : null,
    linBigDeaths: linBig.length, linBigRammed: linBig.filter(d => d.cls2 === 'H-rammed').length,
    rammedN: rammed.length, rammedLen: rammed.reduce((a, d) => a + d.len, 0), rammedBigN: rammedBig.length, rammedBigLen: rammedBig.reduce((a, d) => a + d.len, 0),
    deathLen: deaths.reduce((a, d) => a + d.len, 0),
    extraFate,
    births: B.length, exposedBirths: B.filter(b => b.exposed).length, exposedBirthsBefore30: B.filter(b => b.exposed && b.r < 30).length,
    rammedAtBirth: B.filter(b => b.diedAtBirth).length, turnedAtBirth: B.filter(b => b.turned).length, pocketEats,
    flow: [25, 50, 100, 200, 300, 400].map(r => ({ r, us: [flowAt(0, 'u', r), flowAt(0, 't', r), flowAt(0, 'l', r)], them: [flowAt(1, 'u', r), flowAt(1, 't', r), flowAt(1, 'l', r)] })),
    eat: { usNat: nat(0), usOwn: own(0), usOpp: opp(0), themNat: nat(1), themOwn: own(1), themOpp: opp(1) },
    checksBad: bad,
  };
}

const f1 = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '-';
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
function summarise(rows, label) {
  const out = [];
  for (const ver of [...new Set(rows.map(r => r.ver))].sort()) {
    const rs = rows.filter(r => r.ver === ver), nd = rs[0].nd;
    if (!rs.length) continue;
    const ph = {}; for (const r of rs) ph[r.phase] = (ph[r.phase] || 0) + 1;
    const linDead = rs.filter(r => r.linEnd);
    out.push({
      label, ver, nd, n: rs.length, wins: rs.filter(r => r.win).length, alive: rs.filter(r => !r.eliminated).length, G: mean(rs.map(r => r.G)),
      endElim: rs.filter(r => r.end === 'teamEliminated').length,
      phase: ph, escMean: mean(rs.map(r => r.escCount)), loopHeldTo300: rs.filter(r => r.lastEsc !== null && r.lastEsc >= 300).length,
      linRammedGames: rs.filter(r => r.linBigRammed > 0).length, firstLinRamRoundMedian: median(rs.filter(r => r.firstLinRam).map(r => r.firstLinRam.r)),
      rammedBigPerGame: mean(rs.map(r => r.rammedBigN)), rammedBigLenPerGame: mean(rs.map(r => r.rammedBigLen)), rammedLenPerGame: mean(rs.map(r => r.rammedLen)),
      usNat: mean(rs.map(r => r.eat.usNat)), themNat: mean(rs.map(r => r.eat.themNat)),
      extraDeathRoundMedian: median(rs.flatMap(r => r.extraFate.filter(x => x.r !== null).map(x => x.r))),
      extraRammed: rs.flatMap(r => r.extraFate).filter(x => x.cls === 'H-rammed').length, extraN: rs.flatMap(r => r.extraFate).length,
      births: mean(rs.map(r => r.births)), exposedBirths: mean(rs.map(r => r.exposedBirths)), exposedShare: rs.reduce((a, r) => a + r.exposedBirths, 0) / Math.max(1, rs.reduce((a, r) => a + r.births, 0)),
      rammedAtBirthGames: rs.filter(r => r.rammedAtBirth > 0).length, turnedAtBirthGames: rs.filter(r => r.turnedAtBirth > 0).length, pocketEats: mean(rs.map(r => r.pocketEats)),
      checksBad: rs.reduce((a, r) => a + r.checksBad, 0),
    });
  }
  return out;
}
function median(a) { if (!a.length) return null; const b = [...a].sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; }

function main() {
  let tasks, label;
  if (argv.includes('--online')) { tasks = listOnline(); label = 'online'; }
  else if (opt('eval')) { const dir = path.resolve(ROOT, opt('eval')); tasks = listEval(dir); label = path.basename(dir); }
  else { console.error('need --online or --eval <dir>'); process.exit(2); }
  const rows = tasks.map(study);
  if (argv.includes('--games')) {
    for (const r of rows) {
      const le = r.linEnd ? `계통끝 r${r.linEnd.r} L${r.linEnd.len} ${r.linEnd.cls}${r.linEnd.byLen !== null ? ' by L' + r.linEnd.byLen + '/' + r.linEnd.bySteps + '걸음' : ''}` : '계통 생존';
      const ex = r.extraFate.map(x => x.r === null ? `#${x.id} 생존` : `#${x.id} r${x.r} ${x.cls}`).join(', ');
      console.log(`${r.key} opp ${r.opp} n${r.nd} ${r.win ? 'W' : 'L'} ${r.end} r${r.rounds} G${r.G} 상대최장${r.theirLongest} | 탈출분열 ${r.escCount} 위상 ${r.phase} 마지막 r${r.lastEsc} | ${le} | 첫 계통 박힘 ${r.firstLinRam ? 'r' + r.firstLinRam.r + ' L' + r.firstLinRam.len + ' by L' + r.firstLinRam.byLen : '-'} | 박힘 ${r.rammedN}건 ${r.rammedLen}칸 (6+ ${r.rammedBigN}건) | 덤: ${ex || '-'} | 자연 ${r.eat.usNat}:${r.eat.themNat} | 탄생 ${r.births} 열린칸 ${r.exposedBirths} 탄생박힘 ${r.rammedAtBirth} 옆으로 ${r.turnedAtBirth} 주머니먹기 ${r.pocketEats} | 점검 ${r.checksBad}`);
    }
  }
  const S = summarise(rows, label);
  for (const s of S) console.log(JSON.stringify(s));
  if (opt('json')) fs.writeFileSync(path.resolve(ROOT, opt('json')), JSON.stringify({ label, rows, summary: S }, null, 1));
}
if (require.main === module) main();
module.exports = { study, summarise, listEval, listOnline };
