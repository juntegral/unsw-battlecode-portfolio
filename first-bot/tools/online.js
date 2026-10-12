#!/usr/bin/env node
// Online operations for game.battlecode.au (API v1): ladder, teams, submissions, battles, replay download and
// battle requests. Commands that spend the hourly game allowance ("tickets") only print a plan unless --confirm is given.
//
// Key: $UNSWBC_KEY if set, else the first bc_... token in ~/Downloads/api.txt ($UNSW_KEY_FILE overrides the path).
// The key is only sent as the Authorization header to game.battlecode.au. It is never printed, never written to a file
// and never passed to a child process; every server text that is printed or saved goes through redact().
// Replay downloads follow the 302 to the signed storage link WITHOUT the key (docs/api: the key must not be sent on).
//
// usage: node tools/online.js help            (full list; docs/online.md has the operating notes)
'use strict';
const fs = require('fs'), path = require('path'), os = require('os'), zlib = require('zlib');

const ROOT = path.resolve(__dirname, '..');
const DATA = path.join(ROOT, 'data', 'online');
const LEDGER = path.join(DATA, 'requests.jsonl');       // one line per POST /battles made by this tool
const REMOTE_LOG = path.join(DATA, 'REMOTE-LOG.md');    // human log required by CLAUDE.md (requests, uploads, downloads)
const BASE = 'https://game.battlecode.au/api/v1/';
const OUR_TEAM = 583;
const HOURLY_GAMES = 60;        // docs 2026-09-29: 60 games an hour by hand, plus a separate 60 against DEV teams
const RANKED_GAMES = 5;         // a ranked battle is a five-game series on maps the server picks
const WINDOW_MS = 60 * 60 * 1000;

const HELP = `node tools/online.js <명령> [옵션]

읽기 (티켓 안 씀)
  leaderboard [--top 20] [--eligible] [--ranked] [--json]
                          순위표. --eligible: 신청 가능한 팀만(기본 비랭크 기준, --ranked면 랭크 기준)
  team [<id>] [--json]    팀 정보와 최근 대전 6건. id 없으면 우리 팀(583)
  tickets [--json]        시간당 허용량(티켓) 추정: 최근 60분 동안 우리가 신청한 게임 수
  submissions [--all] [--json]   제출 목록과 활성 제출
  battles [--limit 20] [--json]  최근 우리 대전(최대 200)
  battle <id> [--json]    대전 1건의 게임 목록, 진행 상태, 대기열 위치, 서버 로그
  maps | queue            현재 지도 풀 | 판정 서버 대기열

기록 받기 (티켓 안 씀, REMOTE-LOG.md에 기록)
  download <id>[,<id>...] [--out <data/online 아래 폴더>] [--only] [--no-events] [--purpose "..."]
                          대전(시리즈)의 모든 게임을 받는다: game-<id>.json, M<id>.replay, events-<id>.jsonl.gz, index.json
                          --only: 준 게임 id 하나만. 다른 팀끼리의 공개 대전도 받을 수 있다.

대전 신청 (티켓 씀, --confirm 없으면 계획과 예상 비용만 출력)
  request <teamId>[,<teamId>...] | --top <N>
          [--ranked] [--maps all|4,7,9|portals,trauma] [--purpose "..."]
          [--confirm --expect-active <제출 id>]
                          비랭크: 지도마다 1게임(--maps 필수). 랭크: 무작위 지도 5게임(--maps 불가).
                          --top N: 순위표 위에서부터 신청 가능한 N팀.
                          --confirm에는 --expect-active가 필수다(다른 봇이 활성일 때 티켓 낭비 방지).`;

// ---------- arguments (parsed only when run as a command, not when required by a test) ----------
const BOOL = new Set(['confirm', 'ranked', 'json', 'eligible', 'only', 'no-events', 'all', 'help']);
const flags = {}, pos = [];
let cmd;
function parseArgs(argv) {
  cmd = argv[0];
  for (let i = 1; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { pos.push(a); continue; }
    const [k, inline] = a.slice(2).split(/=(.*)/s);
    if (BOOL.has(k)) flags[k] = true;
    else if (inline !== undefined) flags[k] = inline;
    else if (i + 1 < argv.length) flags[k] = argv[++i];
    else die(`--${k} 에 값이 필요하다`);
  }
}

// ---------- key, redaction, HTTP ----------
let KEY = null;
function key() {
  if (KEY) return KEY;
  const env = (process.env.UNSWBC_KEY || '').trim();
  if (/^bc_[A-Za-z0-9_-]+$/.test(env)) return (KEY = env);
  const file = process.env.UNSW_KEY_FILE || path.join(os.homedir(), 'Downloads', 'api.txt');
  let text;
  try { text = fs.readFileSync(file, 'utf8'); } catch { die(`API 키 파일을 읽지 못했다: ${file}`); }
  const m = text.match(/bc_[A-Za-z0-9_-]+/);
  if (!m) die(`API 키(bc_...)를 찾지 못했다: ${file}`);
  return (KEY = m[0]);
}
function redact(s) {
  let t = String(s ?? '');
  if (KEY) t = t.split(KEY).join('[REDACTED]');
  return t.replace(/bc_[A-Za-z0-9_-]+/g, 'bc_[REDACTED]');
}
function die(msg) { console.error('오류: ' + redact(msg)); process.exit(1); }
const sleep = ms => new Promise(r => setTimeout(r, ms));

// GET retries on network errors and 429 (Retry-After). POST is retried only after a short 429 (the limiter refused it
// before it was handled); never after a network error, where a lost response must not double-spend.
// The 120/min key limit is shared with every other process using the key (tools/collect_top.js, the plumber daemon).
async function api(method, p, body, { retries = method === 'GET' ? 2 : 0, timeout = 30000 } = {}) {
  let postRetry = method !== 'GET';
  for (let attempt = 0; ; attempt++) {
    const headers = { Authorization: 'Bearer ' + key() };
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    let r;
    try {
      r = await fetch(BASE + p, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), redirect: 'manual', signal: AbortSignal.timeout(timeout) });
    } catch (e) {
      if (attempt < retries) { await sleep(2000 * (attempt + 1)); continue; }
      throw new Error(`${method} ${p}: ${redact(e && e.message || e)}`);
    }
    if (r.status === 429) {
      const ra = Number(r.headers.get('retry-after')) || 30;
      if (method === 'GET' && attempt < retries) { const wait = Math.min(120, ra); console.error(`(429 요청 한도: ${wait}초 뒤 다시)`); await sleep(wait * 1000 + 250); continue; }
      if (postRetry && ra <= 60) { postRetry = false; console.error(`(429 요청 한도: ${ra}초 뒤 한 번 다시)`); await sleep(ra * 1000 + 250); continue; }
    }
    const text = await r.text();
    let json = null; try { json = JSON.parse(text); } catch { /* not JSON */ }
    return { status: r.status, ok: r.ok, json, text: redact(text).slice(0, 400), location: r.headers.get('location') };
  }
}
async function get(p) {
  const r = await api('GET', p);
  if (!r.ok) throw new Error(`GET ${p} -> ${r.status} ${redact(r.json && r.json.error || r.text)}`);
  return r.json;
}

// ---------- small helpers ----------
const iso = t => t ? new Date(t).toISOString().slice(0, 16).replace('T', ' ') + 'Z' : '-';
const sum = a => a.reduce((s, x) => s + x, 0);
const out = v => console.log(JSON.stringify(v, null, 2));
const readJ = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return null; } };
const writeJ = (f, v) => { fs.writeFileSync(f + '.tmp', JSON.stringify(v, null, 2) + '\n'); fs.renameSync(f + '.tmp', f); };
const cell = s => String(s ?? '').replace(/\|/g, '/').replace(/\s+/g, ' ').trim();
const isAutoscrim = m => m.ranked && /T\d\d:00:00\.000Z$/.test(m.requestedAt || '');   // hourly draw is stamped on the UTC hour
const resultStr = b => (b.results || []).map(x => ({ win: 'W', loss: 'L', draw: 'D' })[x] || '.').join('');   // '.' = pending
const outcomeKo = o => ({ win: '승', loss: '패', draw: '무', live: '진행 중' })[o] || (o == null ? '대기' : o);
// A battle is unfinished while its outcome is not final: 'live' (observed 2026-09-29, results hold 'pending'), or empty.
const unfinished = b => !['win', 'loss', 'draw'].includes(b.outcome);
// A finished game's status is 'completed' (a winner) or 'draw' (no winner, still has a replay; seen 2026-09-30 in game 707806).
const FINISHED = new Set(['completed', 'draw']);
const waitStr = w => w ? ` [대기열: 앞 ${w.ahead ?? '?'}게임, ms ${w.ms ?? '?'}]` : '';

function eligibility(us, t, kind) {
  const why = [];
  if (t.id === OUR_TEAM) why.push('우리 팀');
  if (!us || !us.hasBot) why.push('우리 팀 활성 봇 없음');
  if (!t.hasBot) why.push('상대 봇 없음');
  if (kind === 'ranked') {
    if (!(us && us.settings && us.settings.ranked)) why.push('우리 랭크 스위치 꺼짐');
    if (!(t.settings && t.settings.ranked)) why.push('상대 랭크 스위치 꺼짐');
    if (us && t.elo < us.elo - 50) why.push(`상대가 우리보다 50점 넘게 낮음(${t.elo} < ${us.elo - 50})`);
  } else if (t.settings && t.settings.unranked === false) {
    why.push('상대 settings.unranked=false (비랭크 거부로 보임, 검증 전)');
  }
  return { ok: why.length === 0, why };
}

function parseMaps(spec, pool) {
  if (spec === 'all') return pool.map(m => m.id);
  const norm = s => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  const ids = [];
  for (const part of String(spec).split(',').map(s => s.trim()).filter(Boolean)) {
    const m = /^\d+$/.test(part) ? pool.find(x => x.id === +part) : pool.find(x => norm(x.name) === norm(part));
    if (!m) die(`지도 '${part}' 는 현재 풀에 없다. 가능: ${pool.map(x => `${x.id} ${x.name}`).join(', ')}`);
    if (!ids.includes(m.id)) ids.push(m.id);
  }
  return ids;
}

function readLedger() {
  try { return fs.readFileSync(LEDGER, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)); } catch { return []; }
}
function remoteLog(action, target, purpose, tickets) {
  fs.mkdirSync(DATA, { recursive: true });
  if (!fs.existsSync(REMOTE_LOG)) fs.writeFileSync(REMOTE_LOG, '# 원격 작업 기록\n\n| 날짜 | 작업 | 대상 | 목적 | 티켓 |\n|---|---|---|---|---|\n');
  const prev = fs.readFileSync(REMOTE_LOG, 'utf8');
  const row = `| ${new Date().toISOString().slice(0, 16)}Z | ${cell(action)} | ${cell(target)} | ${cell(purpose || '-')} | ${tickets} |\n`;
  fs.appendFileSync(REMOTE_LOG, (prev.endsWith('\n') ? '' : '\n') + row);
}

// ---------- allowance ("tickets") estimate ----------
// The official remaining count is only served to a logged-in browser (site route /teams/:id/availability, 401 with the
// API key). Estimate from the API instead: games in battles WE requested (we are team A, not an on-the-hour ranked
// autoscrim draw) whose requestedAt is within the last 60 minutes, per pool (DEV opponents have their own 60), and the
// local ledger of this tool; take the larger. A rolling 60-minute window never under-counts a clock-hour window.
async function allowance(now = Date.now()) {
  const list = await get('battles?limit=200');
  const cand = list.filter(b => unfinished(b) || !b.at || (Date.parse(b.at) >= now - WINDOW_MS - 5 * 60000 && Date.parse(b.at) <= now + 5 * 60000));
  const counted = [], devCache = new Map();
  for (const b of cand) {
    const d = await get(`battles/${b.id}`); const m = d.match;
    if (m.teamAId !== OUR_TEAM || isAutoscrim(m)) continue;
    const age = now - Date.parse(m.requestedAt);
    if (!(age >= 0 && age < WINDOW_MS)) continue;
    const opp = m.teamBId;
    if (!devCache.has(opp)) devCache.set(opp, !!(await get(`teams/${opp}`)).team.dev);
    counted.push({ id: m.id, games: d.games.length, ranked: m.ranked, requestedAt: m.requestedAt, opponent: opp, dev: devCache.get(opp) });
    await sleep(120);
  }
  const ledger = readLedger().filter(r => r.status === 201 && now - Date.parse(r.at) >= 0 && now - Date.parse(r.at) < WINDOW_MS);
  const pool = dev => {
    const s = counted.filter(c => c.dev === dev), l = ledger.filter(r => !!r.dev === dev);
    // 2026-10-01 (user): we never request battles outside this tool, and since 9/28 the scrim team order is random, so
    // "we are team A" no longer means "we requested it": other teams' ranked requests were counted as ours (20 of 60).
    // The local ledger of this tool is the count; the server inference is shown for information only.
    const server = sum(s.map(c => c.games)), local = sum(l.map(r => r.cost || 0)), used = local;
    const times = l.map(r => Date.parse(r.at)).sort((a, b) => a - b);
    return { used, remaining: Math.max(0, HOURLY_GAMES - used), fromServer: server, fromLedger: local,
      nextFreeInMin: times.length ? Math.max(0, Math.ceil((times[0] + WINDOW_MS - now) / 60000)) : 0 };
  };
  return { at: new Date(now).toISOString(), window: 'rolling 60 min', limitPerPool: HOURLY_GAMES, normal: pool(false), dev: pool(true), counted, checkedBattles: cand.length };
}
function printAllowance(a) {
  const line = (label, p) => `${label}: 사용 ${p.used} / ${HOURLY_GAMES}게임 → 남음 약 ${p.remaining} (랭크 ${Math.floor(p.remaining / RANKED_GAMES)}회 분량)` +
    (p.used ? `, 가장 이른 사용분 반환까지 약 ${p.nextFreeInMin}분` : '') + `  [서버 기록 ${p.fromServer}, 로컬 원장 ${p.fromLedger}]`;
  console.log(line('일반 팀 상대', a.normal));
  console.log(line('DEV 팀 상대 ', a.dev));
}

// ---------- commands ----------
async function cmdLeaderboard() {
  const lb = await get('leaderboard');
  const ladder = lb.filter(t => t.rank != null).sort((a, b) => a.rank - b.rank);
  const us = lb.find(t => t.id === OUR_TEAM);
  const kind = flags.ranked ? 'ranked' : 'unranked';
  let rows = flags.eligible ? ladder.filter(t => eligibility(us, t, kind).ok) : ladder;
  rows = rows.slice(0, Number(flags.top) || 20);
  if (flags.json) return out({ at: new Date().toISOString(), rankedTeams: ladder.length, total: lb.length, us: us && slim(us), rows: rows.map(slim) });
  console.log(`# 리더보드 ${iso(Date.now())} — 순위 있는 팀 ${ladder.length} / 전체 ${lb.length}${flags.eligible ? ` (신청 가능한 팀만, ${kind === 'ranked' ? '랭크' : '비랭크'} 기준)` : ''}`);
  console.log('순위  팀id  레이팅 언어    랭크SW DEV  비랭크/랭크 신청  이름');
  for (const t of rows) {
    const u = eligibility(us, t, 'unranked').ok ? 'O' : 'X', r = eligibility(us, t, 'ranked').ok ? 'O' : 'X';
    console.log(`${String(t.rank).padStart(4)}  ${String(t.id).padStart(4)}  ${String(t.elo).padStart(5)}  ${String(t.language || '-').padEnd(6)} ${(t.settings && t.settings.ranked ? 'on' : 'off').padEnd(6)} ${t.dev ? 'DEV' : '-  '}  ${u}/${r}               ${t.name}`);
  }
  if (us) console.log(`우리 팀 ${us.id} ${us.name}: 순위 ${us.rank ?? '-'} / ${ladder.length}, 레이팅 ${us.elo}, 랭크 스위치 ${us.settings && us.settings.ranked ? 'on' : 'off'}`);
}
const slim = t => ({ rank: t.rank, id: t.id, name: t.name, elo: t.elo, wins: t.wins, hasBot: t.hasBot, language: t.language, dev: t.dev, settings: t.settings });

async function cmdTeam() {
  const id = pos[0];
  const t = await get(id ? `teams/${id}` : 'team');
  if (t.team) delete t.team.code;                 // team join code: not needed and not to be spread
  if (flags.json) return out(t);
  const tm = t.team, s = tm.settings || {};
  console.log(`# 팀 ${tm.id} ${tm.name} — 순위 ${t.rank ?? '-'}, 레이팅 ${tm.elo} (최고 ${t.peak ?? '-'})`);
  console.log(`게임 전적 ${t.record ? `${t.record.wins}승 ${t.record.draws}무 ${t.record.losses}패` : '-'} | 봇 ${tm.hasBot ? '있음' : '없음'} | ${tm.dev ? 'DEV(운영) 팀' : '일반 팀'} | 랭크 스위치 ${s.ranked ? 'on' : 'off'}${s.rankedChangedAt ? ` (바꾼 시각 ${iso(s.rankedChangedAt)})` : ''} | 인원 ${tm.member_count ?? (tm.members || []).length}`);
  if (Array.isArray(t.requests)) console.log(`대기 중 가입 요청 ${t.requests.length}건`);
  console.log('최근 대전:');
  for (const b of t.recent || []) console.log(`  ${b.id}  ${iso(b.at)}  ${b.ranked ? '랭크  ' : '비랭크'}  ${b.wins}-${b.losses} ${outcomeKo(b.outcome)}  ${resultStr(b).padEnd(10)} 레이팅 ${b.eloChange == null ? '-' : (b.eloChange >= 0 ? '+' : '') + b.eloChange}  vs ${b.opponentId} ${b.opponent} (${b.opponentElo})${waitStr(b.wait)}`);
}

async function cmdTickets() {
  const a = await allowance();
  if (flags.json) return out(a);
  console.log(`# 시간당 허용량(티켓) 추정 — ${iso(a.at)} 기준, 최근 60분`);
  printAllowance(a);
  console.log(`근거: 최근 대전 ${a.checkedBattles}건 확인, 우리가 신청한 것으로 센 대전 ${a.counted.length}건${a.counted.length ? ': ' + a.counted.map(c => `${c.id}(${c.games}게임, vs ${c.opponent}, ${iso(c.requestedAt)})`).join(', ') : ''}`);
  console.log('주의: 공식 잔량은 로그인한 브라우저에서만 보인다(API 키로는 401). 이 값은 API 기록과 로컬 원장으로 센 추정이다.');
}

async function cmdSubmissions() {
  const subs = (await get('submissions')).slice().sort((a, b) => b.id - a.id);
  if (flags.json) return out(subs.map(({ storageKey, ...s }) => s));
  const act = subs.find(s => s.status === 'active');
  console.log(`# 제출 ${subs.length}개 — 활성: ${act ? `${act.id} ${act.name} (${iso(act.uploadedAt)} 업로드)` : '없음'}`);
  console.log('   id  상태    언어  업로드            게임 승-무-패  kStart  해시         이름 / 설명');
  for (const s of flags.all ? subs : subs.slice(0, 10)) {
    console.log(`${s.status === 'active' ? '*' : ' '}${String(s.id).padStart(5)}  ${String(s.status).padEnd(7)} ${String(s.language).padEnd(4)}  ${iso(s.uploadedAt)}  ${`${s.wins}-${s.draws}-${s.losses}`.padStart(12)}  ${String(s.kStart ?? '-').padStart(6)}  ${String(s.sourceHash || '-').slice(0, 12).padEnd(12)} ${s.name} / ${(s.description || '').slice(0, 50)}`);
  }
  if (!flags.all && subs.length > 10) console.log(`(${subs.length - 10}개 더: --all)`);
}

async function cmdBattles() {
  const limit = Math.min(200, Math.max(1, Number(flags.limit) || 20));
  const list = await get(`battles?limit=${limit}`);
  if (flags.json) return out(list);
  console.log(`# 최근 대전 ${list.length}건 (팀 ${OUR_TEAM}, 새것부터) — 신청 주체와 진영은 'battle <id>'로 확인`);
  console.log('    id  완료(UTC)          종류     결과        레이팅  게임별      상대');
  for (const b of list) console.log(`${String(b.id).padStart(6)}  ${iso(b.at)}  ${b.ranked ? '랭크  ' : '비랭크'}  ${`${b.wins}-${b.losses} ${outcomeKo(b.outcome)}`.padEnd(8)}  ${String(b.eloChange == null ? '-' : (b.eloChange >= 0 ? '+' : '') + b.eloChange).padStart(5)}  ${resultStr(b).padEnd(10)}  ${b.opponentId} ${b.opponent} (${b.opponentElo})${waitStr(b.wait)}`);
}

async function cmdBattle() {
  const id = Number(pos[0]); if (!(Number.isInteger(id) && id > 0)) die('battle <id>');
  const d = await get(`battles/${id}`);
  if (flags.json) return out(d);
  const m = d.match, us = m.teamAId === OUR_TEAM ? 'A' : m.teamBId === OUR_TEAM ? 'B' : null;
  const origin = isAutoscrim(m) ? '정각 요청 → 자동 대전(autoscrim)으로 보임' : `A측(${m.teamAId})이 신청한 것으로 보임`;
  console.log(`# 대전 ${m.id} — ${m.ranked ? '랭크' : '비랭크'}, 게임 ${d.games.length}개, 시리즈 ${m.seriesId}`);
  console.log(`A ${m.teamAId} ${d.teamAName} (${d.teamAElo}) vs B ${m.teamBId} ${d.teamBName} (${d.teamBElo}) | 우리 진영: ${us ?? '없음(다른 팀끼리)'}`);
  console.log(`요청 ${iso(m.requestedAt)} (${origin}) | 게임 ${m.id} 시작 ${iso(m.startedAt)}, 완료 ${iso(m.completedAt)} | 레이팅 변화 A ${m.eloChangeA ?? '-'} / B ${m.eloChangeB ?? '-'} | 시드 ${m.seed ?? '-'}`);
  for (const g of d.games) console.log(`  게임 ${g.id}  ${String(g.status).padEnd(9)} 승자 ${g.winner ? g.winner.toUpperCase() : '-'}${us && g.winner ? (g.winner.toUpperCase() === us ? ' (우리 승)' : ' (우리 패)') : ''}  리플레이 ${g.hasReplay ? '있음' : '없음'}  ${g.mapName}`);
  if (d.wait) console.log('대기열(wait): ' + redact(JSON.stringify(d.wait)));
  const left = d.games.filter(g => !FINISHED.has(g.status));
  if (left.length) console.log(`안 끝난 게임 ${left.length}개 (${left.map(g => `${g.id}:${g.status}`).join(', ')}). 끝난 뒤 download로 받는다.`);
  if (m.log) console.log('서버 로그(이 게임): ' + redact(m.log).slice(0, 2000));
}

async function cmdMaps() {
  const maps = (await get('maps')).slice().sort((a, b) => a.id - b.id);
  if (flags.json) return out(maps.map(({ mapText, ...m }) => m));
  for (const m of maps) console.log(`${String(m.id).padStart(3)}  ${String(m.sizeLabel).padEnd(6)} ${m.active ? '사용 중' : '미사용'}${m.private ? ' 비공개' : ''}  ${m.name}`);
}

async function cmdQueue() {
  const q = await get('queue');
  if (flags.json) return out(q);
  const slots = sum((q.judges || []).map(j => j.slots)), busy = sum((q.judges || []).map(j => j.busy));
  console.log(`판정 서버 ${(q.judges || []).length}대, 슬롯 ${busy}/${slots} 사용 중, 대기 ${q.pending}, 실행 중 ${q.running}`);
}

async function cmdRequest() {
  const ranked = !!flags.ranked, kind = ranked ? 'ranked' : 'unranked', purpose = flags.purpose || '';
  const mine = await get('team');
  const us = { id: mine.team.id, name: mine.team.name, elo: mine.team.elo, hasBot: mine.team.hasBot, settings: mine.team.settings, rank: mine.rank };
  const subs = await get('submissions');
  const active = subs.find(s => s.status === 'active');
  const pool = (await get('maps')).filter(m => m.active && !m.private).sort((a, b) => a.id - b.id);
  let mapIds = [];
  if (ranked) { if (flags.maps) die('랭크 대전은 서버가 지도 5개를 무작위로 고른다. --maps 와 함께 쓸 수 없다.'); }
  else {
    if (!flags.maps) die('비랭크 대전은 --maps 가 필요하다 (예: --maps all, --maps 4,7,9, --maps portals,trauma). 지도마다 1게임 = 티켓 1개.');
    mapIds = parseMaps(flags.maps, pool);
  }
  const cost = ranked ? RANKED_GAMES : mapIds.length;

  let targets;
  if (flags.top) {
    const n = Number(flags.top); if (!(n >= 1)) die('--top 은 1 이상');
    const lb = await get('leaderboard');
    targets = lb.filter(t => t.rank != null).sort((a, b) => a.rank - b.rank).filter(t => eligibility(us, t, kind).ok).slice(0, n).map(t => t.id);
  } else {
    if (!pos[0]) die('대상 팀 id가 필요하다 (예: request 306 --maps all, 또는 request --top 5 --maps all)');
    targets = [...new Set(pos[0].split(',').filter(Boolean).map(Number).filter(n => Number.isInteger(n) && n > 0))];
    if (!targets.length) die('팀 id를 읽지 못했다');
  }

  const recent = await get('battles?limit=200');
  const pendingOpp = new Set(recent.filter(unfinished).map(b => b.opponentId));
  const plan = [];
  for (const id of targets) {
    let t;
    try { t = await get(`teams/${id}`); } catch (e) { plan.push({ teamId: id, name: '?', ok: false, why: [redact(e.message)], cost, mapIds }); continue; }
    const tm = t.team, el = eligibility(us, tm, kind);
    plan.push({ teamId: id, name: tm.name, rank: t.rank, elo: tm.elo, dev: !!tm.dev, ok: el.ok, why: el.why, pending: pendingOpp.has(id), cost, mapIds });
    await sleep(120);
  }
  const al = await allowance();
  const need = { normal: sum(plan.filter(p => p.ok && !p.dev).map(p => p.cost)), dev: sum(plan.filter(p => p.ok && p.dev).map(p => p.cost)) };

  console.log(`# 대전 신청 ${flags.confirm ? '실행' : '계획 (실행 안 함: --confirm 없음)'}`);
  console.log(`우리: ${us.id} ${us.name}, 순위 ${us.rank ?? '-'}, 레이팅 ${us.elo}, 랭크 스위치 ${us.settings && us.settings.ranked ? 'on' : 'off'}, 활성 제출 ${active ? `${active.id} ${active.name}` : '없음'}`);
  console.log(`종류: ${ranked ? '랭크 (무작위 지도 5게임, 레이팅 변동)' : `비랭크 (지도 ${mapIds.length}개: ${mapIds.map(id => pool.find(m => m.id === id).name).join(', ')}; 레이팅 변동 없음)`} → 팀당 ${cost}게임`);
  for (const p of plan) {
    console.log(`  ${p.ok ? '가능' : '불가'}  ${p.rank != null ? `${p.rank}위` : '-'}  ${p.teamId} ${p.name} (${p.elo ?? '-'})  ${p.dev ? 'DEV 허용량' : '일반 허용량'}  비용 ${p.ok ? p.cost : 0}${p.pending ? '  [이 팀과 대기 중인 대전 있음: 과거 409로 거절된 적 있음]' : ''}${p.ok ? '' : '  사유: ' + p.why.join('; ')}`);
  }
  console.log(`필요: 일반 ${need.normal}게임, DEV ${need.dev}게임`);
  printAllowance(al);

  if (!flags.confirm) {
    const ids = flags.top ? `--top ${flags.top}` : targets.join(',');
    console.log(`\n실행하지 않았다. 사용한 티켓 0.\n실행: node tools/online.js request ${ids}${ranked ? ' --ranked' : ` --maps ${flags.maps}`} --purpose "${purpose || '<목적>'}" --expect-active ${active ? active.id : '<제출 id>'} --confirm`);
    return;
  }
  if (!active) die('활성 제출이 없다.');
  if (flags['expect-active'] == null) die(`--confirm 에는 --expect-active <제출 id> 가 필요하다 (지금 활성: ${active.id} ${active.name}).`);
  if (Number(flags['expect-active']) !== active.id) die(`지금 활성 제출은 ${active.id} (${active.name}) 이다. --expect-active ${flags['expect-active']} 와 달라 신청하지 않는다.`);
  const bad = plan.filter(p => !p.ok);
  if (bad.length) die('신청할 수 없는 대상이 있어 아무것도 신청하지 않는다: ' + bad.map(p => `${p.teamId}(${p.why.join('; ')})`).join(', '));
  if (need.normal > al.normal.remaining || need.dev > al.dev.remaining)
    die(`추정 잔량 부족 (일반 필요 ${need.normal}/남음 ${al.normal.remaining}, DEV 필요 ${need.dev}/남음 ${al.dev.remaining}). 약 ${Math.max(al.normal.nextFreeInMin, al.dev.nextFreeInMin)}분 뒤 다시 확인.`);

  let spent = 0;
  for (let i = 0; i < plan.length; i++) {
    const p = plan[i];
    const body = ranked ? { teamId: p.teamId, ranked: true } : { teamId: p.teamId, ranked: false, mapIds: p.mapIds };
    let r;
    try { r = await api('POST', 'battles', body); } catch (e) { r = { status: 0, json: null, text: redact(e.message) }; }
    const ids = (r.json && r.json.ids) || [];
    const okPost = r.status === 201 || (r.status >= 200 && r.status < 300 && ids.length > 0);
    const charged = okPost ? (ranked ? RANKED_GAMES : (ids.length || p.cost)) : 0;
    spent += charged;
    const row = { at: new Date().toISOString(), teamId: p.teamId, name: p.name, rank: p.rank, elo: p.elo, dev: p.dev, ranked, mapIds: p.mapIds,
      cost: charged, status: okPost ? 201 : r.status, ids, error: okPost ? null : redact((r.json && r.json.error) || r.text), activeSubmission: active.id, purpose };
    fs.mkdirSync(DATA, { recursive: true });
    fs.appendFileSync(LEDGER, JSON.stringify(row) + '\n');
    remoteLog(`대전 신청(${ranked ? '랭크' : `비랭크 지도 ${p.mapIds.length}`})${okPost ? ` ids ${ids.join(',')}` : ` 거절 ${r.status}: ${row.error}`}`,
      `${p.teamId} ${p.name} (${p.rank ?? '-'}위, ${p.elo}) / 우리 제출 ${active.id}`, purpose, charged);
    console.log(`${okPost ? '신청됨' : '거절'}  ${p.teamId} ${p.name}: ${r.status} ${okPost ? `ids ${ids.join(',')}` : row.error}`);
    if (!okPost) { console.log('거절되어 나머지 신청을 멈춘다.'); break; }
    if (i < plan.length - 1) await sleep(300);
  }
  console.log(`사용한 티켓(게임) ${spent}. 결과는 'battles' 또는 'battle <id>'로 보고, 끝나면 'download <id>'로 받는다.`);
}

let viewerMod;
function viewer() {
  if (viewerMod === undefined) {
    try { viewerMod = require(path.join(__dirname, 'viewer.js')); }
    catch (e) { viewerMod = null; console.error('(리플레이 해석기를 불러오지 못해 events 파일과 제출 id를 건너뛴다: ' + String(e.message).slice(0, 120) + ')'); }
  }
  return viewerMod;
}

async function fetchReplay(gid) {
  const r = await api('GET', `battles/${gid}/replay`);
  if (!(r.status >= 300 && r.status < 400) || !r.location) throw new Error(`리플레이 ${gid}: ${r.status} ${r.json && r.json.error || r.text}`);
  const url = new URL(r.location, BASE);
  const d = await fetch(url.href, { signal: AbortSignal.timeout(120000) });   // signed link: no Authorization header
  if (!d.ok) throw new Error(`리플레이 ${gid}: 저장소 응답 ${d.status}`);
  return Buffer.from(await d.arrayBuffer());
}

async function cmdDownload() {
  const ids = String(pos[0] || '').split(',').filter(Boolean).map(Number).filter(n => Number.isInteger(n) && n > 0);
  if (!ids.length) die('download <대전 또는 게임 id>[,<id>...]');
  const outName = flags.out || `dl-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}`;
  const dir = path.resolve(DATA, outName);
  if (!dir.startsWith(DATA + path.sep)) die('--out 은 data/online/ 아래 폴더 이름이어야 한다');
  const idxPath = path.join(dir, 'index.json');
  const idx = readJ(idxPath) || { batch: path.relative(DATA, dir), files: 'game-<id>.json, M<id>.replay, events-<id>.jsonl.gz (1행 meta)',
    note: 'ourSide는 대문자 A/B, winner는 서버 값 그대로 소문자 a/b. ourWin은 두 값을 맞춰 계산한 값. 제출 id는 리플레이 teams.<side>.botId에서 읽는다(서버 API는 더 이상 주지 않고, 상대 쪽은 비어 있다).', games: [] };
  const byId = new Map(idx.games.map(g => [g.gameId, g]));
  const seen = new Set(), saved = [], skipped = [], pending = [], failed = [], series = [];
  for (const id of ids) {
    let d;
    try { d = await get(`battles/${id}`); } catch (e) { failed.push(`${id}: ${redact(e.message)}`); continue; }
    const gameIds = flags.only ? [id] : d.games.map(g => g.id);
    series.push(`${d.match.id}(${d.games.length}게임, ${d.match.teamAId} vs ${d.match.teamBId})`);
    for (const gid of gameIds) {
      if (seen.has(gid)) continue; seen.add(gid);
      const gjPath = path.join(dir, `game-${gid}.json`), rpPath = path.join(dir, `M${gid}.replay`);
      if (fs.existsSync(gjPath) && fs.existsSync(rpPath)) { skipped.push(gid); continue; }
      let gd;
      try { gd = gid === d.match.id ? d : await get(`battles/${gid}`); } catch (e) { failed.push(`${gid}: ${redact(e.message)}`); continue; }
      const m = gd.match;
      if (!FINISHED.has(m.status)) { pending.push(`${gid}:${m.status}${gd.wait ? ' ' + JSON.stringify(gd.wait) : ''}`); continue; }
      let buf = null, R = null;
      try { buf = await fetchReplay(gid); } catch (e) { failed.push(redact(e.message)); }
      fs.mkdirSync(dir, { recursive: true });            // created only once there is something to write
      if (buf) {
        fs.writeFileSync(rpPath, buf);
        const v = viewer();
        if (v) { try { R = v.ctx.parseReplay(buf); } catch (e) { failed.push(`${gid}: 리플레이 해석 실패 ${String(e.message).slice(0, 100)}`); } }
      }
      const botA = R && R.teams && R.teams.A && R.teams.A.botId, botB = R && R.teams && R.teams.B && R.teams.B.botId;
      const ourSide = m.teamAId === OUR_TEAM ? 'A' : m.teamBId === OUR_TEAM ? 'B' : null;
      const game = { id: m.id, seriesId: m.seriesId, status: m.status, winner: m.winner, teamAId: m.teamAId, teamBId: m.teamBId,
        submissionAId: botA ? Number(botA) : null, submissionBId: botB ? Number(botB) : null, mapId: m.mapId, mapName: gd.mapName,
        scoresA: m.scoresA, scoresB: m.scoresB, completedAt: m.completedAt, serverLog: m.log ?? null, ranked: m.ranked,
        seed: m.seed, requestedAt: m.requestedAt, startedAt: m.startedAt, eloChangeA: m.eloChangeA, eloChangeB: m.eloChangeB,
        teamAName: gd.teamAName, teamBName: gd.teamBName, teamAElo: gd.teamAElo, teamBElo: gd.teamBElo,
        replay: buf ? { bytes: buf.length, result: R ? R.result : null } : null,
        submissionSource: 'replay teams.<side>.botId', downloadedAt: new Date().toISOString() };
      writeJ(gjPath, game);
      if (R && !flags['no-events']) {
        const meta = { gameId: m.id, map: m.mapId, mapName: gd.mapName, ourSide, teamAId: m.teamAId, teamBId: m.teamBId, submissionAId: game.submissionAId,
          submissionBId: game.submissionBId, ranked: m.ranked, seed: m.seed, completedAt: m.completedAt, result: R.result, note: 'events are raw replay-viewer events; roundStart marks each round' };
        const lines = [JSON.stringify({ meta })]; let round = -1;
        for (const e of R.events) { if (e.type === 'roundStart') round = e.round; lines.push(JSON.stringify({ round, ...e })); }
        fs.writeFileSync(path.join(dir, `events-${gid}.jsonl.gz`), zlib.gzipSync(lines.join('\n') + '\n', { level: 6 }));
      }
      const ourSub = ourSide === 'A' ? game.submissionAId : ourSide === 'B' ? game.submissionBId : null;
      byId.set(gid, { gameId: gid, seriesId: m.seriesId, map: m.mapId, mapName: gd.mapName, ranked: m.ranked, teamAId: m.teamAId, teamBId: m.teamBId,
        ourSide, opponentTeam: ourSide === 'A' ? m.teamBId : ourSide === 'B' ? m.teamAId : null, ourSubmission: ourSub, winner: m.winner,
        ourWin: ourSide && m.winner ? m.winner.toUpperCase() === ourSide : null, requestedAt: m.requestedAt, completedAt: m.completedAt, seed: m.seed, replay: !!buf });
      if (buf) saved.push(gid);          // without a replay the game json is kept and the next run retries the replay
      await sleep(120);
    }
  }
  idx.games = [...byId.values()].sort((a, b) => a.gameId - b.gameId);
  if (byId.size) writeJ(idxPath, idx);
  if (saved.length) {
    remoteLog('다운로드', `대전 ${series.join(', ')} → data/online/${path.relative(DATA, dir)} (게임 ${saved.length}개)`, flags.purpose || '기록 수집', 0);
  }
  console.log(`저장 ${saved.length}개${saved.length ? ` (${saved.join(',')})` : ''} → ${path.relative(ROOT, dir)}`);
  if (skipped.length) console.log(`이미 있음 ${skipped.length}개`);
  if (pending.length) console.log(`아직 안 끝남 ${pending.length}개: ${pending.join(', ')} (나중에 같은 명령으로 다시)`);
  if (failed.length) console.log(`실패 ${failed.length}건: ${failed.join(' | ')}`);
}

// ---------- main ----------
const COMMANDS = { leaderboard: cmdLeaderboard, team: cmdTeam, tickets: cmdTickets, submissions: cmdSubmissions, battles: cmdBattles,
  battle: cmdBattle, maps: cmdMaps, queue: cmdQueue, request: cmdRequest, download: cmdDownload };
module.exports = { allowance, eligibility, isAutoscrim, parseMaps };
if (require.main === module) {
  parseArgs(process.argv.slice(2));
  if (!cmd || cmd === 'help' || flags.help || !COMMANDS[cmd]) { console.log(HELP); process.exit(cmd && cmd !== 'help' && !flags.help ? 1 : 0); }
  COMMANDS[cmd]().catch(e => die(e && e.message || e));
}
