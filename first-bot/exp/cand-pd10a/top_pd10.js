#!/usr/bin/env node
// 상위권끼리의 Prisoners Dilemma 경기(data/top)에서 두 판본(시작 드래곤 6 / 10마리)을 팀·경기 단위로 센다.
// usage (저장소 루트에서): node exp/cand-pd10a/top_pd10.js [--until 2026-09-29T18:00:00Z] [--json out.json]
//   --until: 대전 시각(index.jsonl의 at)이 이 시각 이하인 경기만 쓴다(수집이 계속되므로 수치를 고정한다). 기본 2026-09-29T18:00:00Z.
// 방법: 리플레이 사건만 읽는다(tools/replay.js). 진주가 사라지는 tileChange는 그 턴의 드래곤이 먹은 것이다.
//   진주 출처: 사망 사건 직후의 tileChange(true)는 주검, 그 밖은 자연 생성. 사망 원인은 dragonDeath.reason과 그 턴의 주인으로 나눈다.
// 정의:
//   통로 = 그 팀 시작 드래곤(길이 11)의 x열. 가운데 = x 15·16열. 통로 샘물 = 통로 칸 중 자연 진주가 난 칸.
//   시작 드래곤 처리 = 0–9라운드에 시작 드래곤(과 그 조각)이 한 분열의 자식 길이 목록.
//   박힘 = 상대 드래곤의 턴에 머리끼리 부딪혀 죽음(reason H, 턴 주인이 상대).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const UNTIL = new Date(opt('until', '2026-09-29T18:00:00Z')).toISOString();

function one(file, meta) {
  const R = load(file);
  const init = R.match.map.initialDragons, nd = init.length;
  const team = new Map(init.map(d => [d.id, d.team])), len = new Map(init.map(d => [d.id, d.body.length]));
  const startOf = {}; for (const d of init) if (d.body.length >= 10) startOf[d.team] = d;
  const corrX = { A: startOf.A.body[0].x, B: startOf.B.body[0].x };
  const extras = { A: init.filter(d => d.team === 'A' && d.body.length === 2).map(d => d.id), B: init.filter(d => d.team === 'B' && d.body.length === 2).map(d => d.id) };
  const lineage = { A: new Set([startOf.A.id]), B: new Set([startOf.B.id]) };
  const S = t => ({ corrNat: 0, midNat: 0, otherNat: 0, dropOwn: 0, dropOpp: 0, earlySplits: [], rammedBig: 0, rammedBigLen: 0, linRammed: 0, linRammedFirst: null,
    extraDeath: [], extraRam: 0, kills: 0, maxUnits: 0, unitsAt: {}, totalAt: {} });
  const st = { A: S('A'), B: S('B') };
  const pearlSrc = new Map();   // "x,y" -> 'nat' | team letter of the dead dragon
  let round = -1, cur = -1, dropTeam = null;
  const alive = new Map(init.map(d => [d.id, true]));
  const snap = r => { for (const T of ['A', 'B']) { let u = 0, tot = 0; for (const [id, a] of alive) if (a && team.get(id) === T) { u++; tot += len.get(id); } if ([25, 50, 100, 200].includes(r)) { st[T].unitsAt[r] = u; st[T].totalAt[r] = tot; } st[T].maxUnits = Math.max(st[T].maxUnits, u); } };
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': round = e.round; dropTeam = null; snap(round); break;
      case 'turnStart': cur = e.id; dropTeam = null; break;
      case 'dragonSplit': {
        team.set(e.childId, e.team); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length); alive.set(e.childId, true);
        if (lineage[e.team].has(e.parentId)) { lineage[e.team].add(e.childId); if (round < 10) st[e.team].earlySplits.push(e.childBody.length); }
        break;
      }
      case 'dragonDeath': {
        const T = team.get(e.id), L = len.get(e.id); alive.set(e.id, false); dropTeam = T;
        const byT = team.get(cur);
        if (e.reason === 'H' && cur !== e.id && byT !== T) {
          if (L >= 6) { st[T].rammedBig++; st[T].rammedBigLen += L; }
          if (lineage[T].has(e.id) && L >= 6) { st[T].linRammed++; if (st[T].linRammedFirst === null) st[T].linRammedFirst = round; }
          st[byT].kills++;
        }
        if (extras[T].includes(e.id)) st[T].extraDeath.push({ r: round, reason: e.reason, byEnemy: byT !== T });
        if (extras[byT] && extras[byT].includes(cur) && byT !== T && e.reason === 'H') st[byT].extraRam++;
        break;
      }
      case 'tileChange': {
        const k = e.tile.x + ',' + e.tile.y;
        if (e.hasPearl) { pearlSrc.set(k, dropTeam || 'nat'); break; }
        const src = pearlSrc.get(k); pearlSrc.delete(k);
        const T = team.get(cur); if (!T || src === undefined) break;
        len.set(cur, len.get(cur) + 1);
        if (src === 'nat') { if (e.tile.x === corrX[T]) st[T].corrNat++; else if (e.tile.x === 15 || e.tile.x === 16) st[T].midNat++; else st[T].otherNat++; }
        else if (src === T) st[T].dropOwn++; else st[T].dropOpp++;
        break;
      }
      case 'dragonAction': {
        const a = e.action; if (a && a.kind === 'move' && a.steps.length > 1) len.set(e.id, len.get(e.id) - (a.steps.length - 1));
        break;
      }
      default: break;
    }
  }
  const res = R.result;
  return { gameId: meta.gameId, battleId: meta.battleId, nd, rounds: round + 1, end: res.endReason, winner: res.winner, teams: { A: meta.teamA, B: meta.teamB }, final: { A: res.teamA, B: res.teamB }, st };
}

function main() {
  const lines = fs.readFileSync(path.join(ROOT, 'data/top/index.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.map === 'Prisoners Dilemma' && r.at <= UNTIL);
  const games = [];
  for (const r of lines) {
    const f = path.join(ROOT, 'data/top', String(r.battleId), r.gameId + '.replay.gz');
    if (!fs.existsSync(f)) continue;
    try { games.push(one(f, r)); } catch (e) { console.error('skip', r.gameId, String(e).slice(0, 80)); }
  }
  const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
  const med = a => { if (!a.length) return null; const b = [...a].sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; };
  const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '-';
  for (const nd of [6, 10]) {
    const gs = games.filter(g => g.nd === nd);
    const sides = gs.flatMap(g => ['A', 'B'].map(T => ({ g, T, s: g.st[T], win: g.winner === T })));
    const W = sides.filter(x => x.win), L = sides.filter(x => !x.win && x.g.winner);
    const row = (name, f) => `${name}: 승자 ${f1(mean(W.map(f)))} / 패자 ${f1(mean(L.map(f)))}`;
    console.log(`== 판본 ${nd}: ${gs.length}판, 길이 중앙값 ${med(gs.map(g => g.rounds))}, 전멸 종료 ${gs.filter(g => g.end === 'teamEliminated').length}`);
    console.log(row('통로 자연 진주', x => x.s.corrNat));
    console.log(row('가운데 자연 진주', x => x.s.midNat));
    console.log(row('그 밖 자연 진주', x => x.s.otherNat));
    console.log(row('주검(자기/상대)', x => x.s.dropOwn + x.s.dropOpp));
    console.log(row('길이 6+ 박힘', x => x.s.rammedBig));
    console.log(row('시작 계통 6+ 박힘', x => x.s.linRammed));
    console.log(row('박아 죽인 수', x => x.s.kills));
    console.log(row('r50 수', x => x.s.unitsAt[50] ?? 0));
    console.log(row('r100 수', x => x.s.unitsAt[100] ?? 0));
    // early split patterns
    const pat = {}; for (const x of sides) { const k = x.s.earlySplits.slice(0, 5).join('+') || '없음'; pat[k] = (pat[k] || 0) + 1; }
    console.log('시작 드래곤 0–9라운드 분열(자식 길이, 앞 5개) 상위:', Object.entries(pat).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, v]) => `${k}×${v}`).join(', '));
    const firstSplitChildMax = sides.map(x => x.s.earlySplits.length ? Math.max(...x.s.earlySplits) : 0);
    console.log('0–9라운드에 시작 계통이 낸 가장 큰 자식 길이 분포:', Object.entries(firstSplitChildMax.reduce((a, v) => (a[v] = (a[v] || 0) + 1, a), {})).map(([k, v]) => `${k}:${v}`).join(' '));
    if (nd === 10) {
      const ex = sides.flatMap(x => x.s.extraDeath);
      console.log(`덤 드래곤(팀당 2): ${sides.length * 2}마리 중 죽음 ${ex.length}, 적 턴에 죽음 ${ex.filter(d => d.byEnemy).length}, 사망 라운드 중앙값 ${med(ex.map(d => d.r))}; 덤이 적을 박아 죽인 수 합 ${sides.reduce((a, x) => a + x.s.extraRam, 0)}`);
    }
  }
  if (opt('json')) fs.writeFileSync(path.resolve(ROOT, opt('json')), JSON.stringify(games));
}
if (require.main === module) main();
module.exports = { one };
