#!/usr/bin/env node
// Collect replays of battles between strong teams. Read-only GETs: no tickets are spent.
// usage: node tools/collect_top.js [--min-elo 1900 | --top 20] [--extra-teams 328,...] [--all-opponents] [--out top] [--dry]
//   --all-opponents: every battle of the selected teams, whatever the opponent (2026-10-01 user: "극상위권 로그만 대량으로").
//   --out <name>: write to data/<name>/ instead of data/top/ (the elite-only collection uses --top 10 --all-opponents --out elite).
// Output: data/top/<battleId>/{battle.json,<gameId>.replay.gz}, data/top/index.jsonl (one row per game).
// A team profile lists only its six most recent battles and strong teams play in bursts, so this runs every few
// minutes from launchd (docs/launchd/). Read replays with require('./tools/replay.js').load(file).
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'data', (() => { const i = process.argv.indexOf('--out'); return i > 0 ? process.argv[i + 1] : 'top'; })());
const BASE = 'https://game.battlecode.au/api/v1';
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const TOP = arg('top', null), MIN_ELO = +arg('min-elo', '1900'), DRY = process.argv.includes('--dry'), ALL = process.argv.includes('--all-opponents');
const BOARD_MAX_AGE_MS = 55 * 60000, MIN_FREE_BYTES = 20 * 1024 ** 3;
// The key stays inside this process: never printed, written or logged.
const KEY = (fs.readFileSync(path.join(process.env.HOME, 'Downloads', 'api.txt'), 'utf8').match(/bc_[A-Za-z0-9_-]+/) || [])[0];
if (!KEY) { console.error('API key not found'); process.exit(1); }
const sleep = ms => new Promise(r => setTimeout(r, ms));

// About 100 requests a minute, under the documented 120 per key.
let last = 0;
async function api(p, opts = {}) {
  const wait = last + 600 - Date.now(); if (wait > 0) await sleep(wait); last = Date.now();
  const r = await fetch(BASE + p, { headers: { Authorization: 'Bearer ' + KEY }, ...opts });
  if (r.status === 429) { await sleep(1000 * (+r.headers.get('retry-after') || 30)); return api(p, opts); }
  return r;
}
const json = async p => { const r = await api(p); if (!r.ok) throw Error(p + ' -> ' + r.status); return r.json(); };

// /leaderboard is limited to 30 a minute; the team list barely moves within an hour.
async function leaderboard() {
  const file = path.join(OUT, 'leaderboard.json');
  if (fs.existsSync(file) && Date.now() - fs.statSync(file).mtimeMs < BOARD_MAX_AGE_MS) return JSON.parse(fs.readFileSync(file, 'utf8'));
  const board = await json('/leaderboard');
  const slim = board.map(({ rank, ranked, id, name, elo, dev, language }) => ({ rank, ranked, id, name, elo, dev, language }));
  if (!DRY) { fs.writeFileSync(file + '.tmp', JSON.stringify(slim)); fs.renameSync(file + '.tmp', file); }
  return slim;
}

async function download(gameId, file) {
  // The replay endpoint redirects to a signed link that must not receive our key.
  const r = await api('/battles/' + gameId + '/replay', { redirect: 'manual' });
  const loc = r.headers.get('location');
  if (!loc) throw Error('no replay redirect for ' + gameId + ' (' + r.status + ')');
  const f = await fetch(loc);
  if (!f.ok) throw Error('replay download ' + gameId + ' -> ' + f.status);
  fs.writeFileSync(file + '.tmp', zlib.gzipSync(Buffer.from(await f.arrayBuffer()), { level: 6 }));
  fs.renameSync(file + '.tmp', file);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const disk = fs.statfsSync(ROOT);
  if (disk.bavail * disk.bsize < MIN_FREE_BYTES) { console.log(JSON.stringify({ skipped: 'disk free < 20 GiB' })); return; }
  const board = (await leaderboard()).filter(t => t.ranked && !t.dev).sort((a, b) => a.rank - b.rank);
  const teams = TOP ? board.slice(0, +TOP) : board.filter(t => t.elo >= MIN_ELO);
  // --extra-teams 328,...: also follow these teams whatever their rank (2026-10-01 user: watch UnderTheC, R16 in the sprint bracket).
  for (const id of String(arg('extra-teams', '')).split(',').filter(Boolean).map(Number)) {
    const t = board.find(x => x.id === id); if (t && !teams.some(x => x.id === id)) teams.push(t);
  }
  const strong = new Set(teams.map(t => t.id)), byName = new Map(board.map(t => [t.name, t]));
  const wanted = b => ALL ? true : TOP ? strong.has(b.opponentId) : strong.has(b.opponentId) || b.opponentElo >= MIN_ELO;
  const battles = new Map();
  for (const t of teams) {
    const prof = await json('/teams/' + t.id);
    for (const b of prof.recent || []) if (wanted(b) && !battles.has(b.id)) battles.set(b.id, b);
  }
  const indexFile = path.join(OUT, 'index.jsonl');
  const seen = new Set(fs.existsSync(indexFile) ? fs.readFileSync(indexFile, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l).gameId) : []);
  let newGames = 0, newBattles = 0;
  for (const [id, b] of battles) {
    const dir = path.join(OUT, String(id));
    // A battle already fully collected needs no detail request.
    if (fs.existsSync(path.join(dir, 'battle.json')) && JSON.parse(fs.readFileSync(path.join(dir, 'battle.json'), 'utf8')).complete) continue;
    const detail = await json('/battles/' + id);
    const games = (detail.games || []).filter(g => g.status === 'completed' && g.hasReplay && !seen.has(g.id));
    const complete = (detail.games || []).every(g => g.status === 'completed');
    if (DRY) { if (games.length) console.log('would fetch', id, detail.teamAName, 'vs', detail.teamBName, games.length, 'games'); continue; }
    fs.mkdirSync(dir, { recursive: true });
    const a = byName.get(detail.teamAName), bt = byName.get(detail.teamBName);
    fs.writeFileSync(path.join(dir, 'battle.json'), JSON.stringify({ ...detail, complete, ranked: b.ranked, at: b.at, collectedAt: new Date().toISOString(),
      ranks: { a: a && { id: a.id, rank: a.rank, elo: a.elo }, b: bt && { id: bt.id, rank: bt.rank, elo: bt.elo } } }, null, 2));
    if (games.length) newBattles++;
    for (const g of games) {
      await download(g.id, path.join(dir, g.id + '.replay.gz'));
      fs.appendFileSync(indexFile, JSON.stringify({ battleId: id, gameId: g.id, map: g.mapName, winner: g.winner, ranked: b.ranked, at: b.at,
        teamA: detail.teamAName, teamB: detail.teamBName, eloA: detail.teamAElo, eloB: detail.teamBElo,
        rankA: a?.rank ?? null, rankB: bt?.rank ?? null }) + '\n');
      seen.add(g.id); newGames++;
    }
  }
  const scope = (TOP ? `상위 ${TOP}팀` : `레이팅 ${MIN_ELO} 이상`) + (ALL ? '의 모든 대전' : ' 팀끼리');
  if (!DRY && newGames) fs.appendFileSync(path.join(ROOT, 'data', 'online', 'REMOTE-LOG.md'),
    `| ${new Date().toISOString().slice(0, 16)} | 다운로드 | ${scope} 대전 ${newBattles}건, 경기 ${newGames}판 | 상위권 전략 관측 | 0 |\n`);
  console.log(JSON.stringify({ at: new Date().toISOString(), teams: teams.length, battles: battles.size, newBattles, newGames, dry: DRY }));
})().catch(e => { console.error(new Date().toISOString(), String(e.message || e)); process.exit(1); });
