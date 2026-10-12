#!/usr/bin/env node
// Operator-only, read-only local dashboard for the g5 wave loop.
// usage: node scripts/loop-dashboard.js [--port 4747]   then open http://127.0.0.1:4747
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const watch = require('./loop-watch');

const WORKSPACES = '~/orca/workspaces/unsw-arena';
const NAMES = ['g5'];
const WAVE = /^w\d{6}$/;
const TAIL_BYTES = 512 * 1024;

const exists = file => fs.existsSync(file);
function readJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}
const ms = iso => { const t = Date.parse(iso); return Number.isFinite(t) ? t : null; };

// Last complete lines of a large append-only file.
function tailLines(file, bytes = TAIL_BYTES) {
  let fd;
  try {
    fd = fs.openSync(file, 'r');
    const size = fs.fstatSync(fd).size, start = Math.max(0, size - bytes);
    const buffer = Buffer.alloc(size - start);
    fs.readSync(fd, buffer, 0, buffer.length, start);
    const lines = buffer.toString('utf8').split('\n');
    if (start > 0) lines.shift();
    lines.pop();
    return lines;
  } catch { return []; } finally { if (fd !== undefined) fs.closeSync(fd); }
}

// Claude stream-json transcript: final usage summary and the latest progress messages.
const transcriptCache = new Map();
function transcript(file) {
  if (!exists(file)) return null;
  const stat = fs.statSync(file), key = file + ':' + stat.size + ':' + stat.mtimeMs;
  if (transcriptCache.has(key)) return transcriptCache.get(key);
  let summary = null;
  const messages = [];
  for (const line of tailLines(file)) {
    if (!line.startsWith('{')) continue;
    let item;
    try { item = JSON.parse(line); } catch { continue; }
    if (item.type === 'result') {
      summary = { subtype: item.subtype, wallMs: item.duration_ms, apiMs: item.duration_api_ms, turns: item.num_turns,
        costUsd: item.total_cost_usd };
    } else if (item.type === 'assistant') {
      for (const part of item.message?.content || []) {
        if (part.type === 'text' && part.text.trim()) messages.push(part.text.trim().slice(0, 600));
      }
    }
  }
  const value = { summary, recent: messages.slice(-6).reverse(), updated: stat.mtime.toISOString(), bytes: stat.size };
  for (const old of transcriptCache.keys()) if (old.startsWith(file + ':')) transcriptCache.delete(old);
  transcriptCache.set(key, value);
  return value;
}

function countRows(file) {
  if (!exists(file)) return 0;
  const lines = fs.readFileSync(file, 'utf8').split('\n').slice(0, -1);
  return lines.filter(Boolean).length;
}

function checksFor(dir, wave) {
  const folder = path.join(dir, 'checks');
  if (!exists(folder)) return [];
  return fs.readdirSync(folder).filter(name => name.startsWith(wave + '-')).map(name => {
    const base = path.join(folder, name), plan = readJson(path.join(base, 'plan.json')) || {};
    const report = readJson(path.join(base, 'report.json'));
    const result = report?.result || null;
    return {
      id: name, at: plan.at || null, expected: plan.expected || null, seeds: plan.seeds || [],
      maps: (plan.maps || []).length, opponents: Object.keys(plan.opponentHashes || {}).length,
      status: report?.status || null,
      baselineDone: countRows(path.join(base, 'baseline-results/rows.jsonl')),
      candidateDone: countRows(path.join(base, 'candidate-results/rows.jsonl')),
      result: result && { candidate: result.candidate, baseline: result.baseline, byMap: result.byMap,
        byOpponent: result.byOpponent, bySide: result.bySide }
    };
  }).sort((a, b) => String(a.at).localeCompare(String(b.at)));
}

// The runner's handoff moves finished waves and each wave's working notes into archive/, out of the
// research sandbox's reach. This operator view reads both places.
const archiveOf = dir => path.join(dir, 'archive');
function locate(dir, name) {
  const live = path.join(dir, 'waves', name);
  return exists(live) ? live : path.join(archiveOf(dir), 'waves', name);
}
function waveIds(dir) {
  const ids = new Set();
  for (const folder of [path.join(dir, 'waves'), path.join(archiveOf(dir), 'waves')]) {
    if (exists(folder)) for (const name of fs.readdirSync(folder)) if (WAVE.test(name)) ids.add(name);
  }
  return [...ids].sort();
}
// Archived NOTES.md copies oldest first, then the live file.
function notesText(dir) {
  const folder = path.join(archiveOf(dir), 'notes');
  const archived = exists(folder) ? fs.readdirSync(folder).filter(f => f.endsWith('.md')).map(f => path.join(folder, f))
    .sort((a, b) => fs.statSync(a).mtimeMs - fs.statSync(b).mtimeMs) : [];
  return [...archived, path.join(dir, 'NOTES.md')].filter(exists).map(f => fs.readFileSync(f, 'utf8')).join('\n');
}
function ledgerByWave(dir) {
  const file = path.join(dir, 'LEDGER.md'), out = {};
  if (!exists(file)) return out;
  for (const part of fs.readFileSync(file, 'utf8').split(/^(?=## w\d{6}\b)/m)) {
    const id = part.match(/^## (w\d{6})\b/)?.[1];
    if (id) out[id] = (out[id] ? out[id] + '\n\n' : '') + part.replace(/^## .*\n?/, '').trim();
  }
  return out;
}

// NOTES.md split at headings; a heading without a wave id inherits the enclosing level-2 section's wave.
function notesByWave(dir) {
  const out = {}, text = notesText(dir), ready = [], seenReady = new Set();
  if (!text) return { byWave: out, ready, text: '' };
  let section = null, current = null, block = [];
  const flush = () => {
    const body = block.join('\n').trim();
    if (body) (out[current || '_'] ||= []).push(body);
    block = [];
  };
  for (const line of text.split('\n')) {
    // A level-1 title starts the next archived copy; its preface belongs to no wave.
    if (line.startsWith('# ')) { flush(); section = current = null; continue; }
    const heading = line.match(/^(#{2,6})\s+(.*)$/);
    if (heading) {
      flush();
      // "(w000003에서 원자료로 복원)" names the wave that actually wrote the block.
      const writer = heading[2].match(/\((w\d{6})에서/);
      const id = writer ? writer[1] : (heading[2].match(/w\d{6}/) || [])[0] || null;
      if (heading[1].length === 2) section = id;
      current = id || section;
    }
    const r = line.match(/^\s*[-*]?\s*ready:\s*r(\d+)\s*[—-]?\s*(.*)$/i);
    // Every archived copy repeats the version lines; the first occurrence carries the writing wave.
    if (r && !seenReady.has(r[1])) { seenReady.add(r[1]); ready.push({ version: +r[1], text: r[2].trim(), wave: current }); }
    block.push(line);
  }
  flush();
  return { byWave: out, ready, text };
}

// Per-wave growth record from free-form NOTES: best effort, every field optional and labelled with its source.
const CAND = /\bc\d+[a-z]?\b/;
function clean(line) { return line.replace(/^\s*[-*]\s*/, '').trim(); }
function field(text, label) {
  const m = text.match(new RegExp(label + '\\s*:\\s*([\\s\\S]*?)(?=(?:좋아질 상황|나빠질 가능성|틀렸다면)\\s*:|$)'));
  return m ? m[1].replace(/\s+/g, ' ').replace(/^[-\s]+|[\s.-]+$/g, '').trim() : null;
}
const LABELS = /(?:좋아질 상황|나빠질 가능성|틀렸다면)\s*:/;
// "가설 cN: ..." line, its non-bullet continuation lines, then its "- 좋아질 상황/나빠질 가능성/틀렸다면" bullets.
function hypothesisAt(lines, start) {
  const statement = [clean(lines[start]).replace(/^가설\s+/, '')], bullets = [];
  const inline = LABELS.test(lines[start]);
  for (let i = start + 1; !inline && i < lines.length; i++) {
    const l = lines[i];
    if (/^\s*[-*]\s*/.test(l) && LABELS.test(l.slice(0, 40))) bullets.push(clean(l));
    // A group of sibling "- 가설 cX:" lines shares the label bullets that follow the group.
    else if (!bullets.length && /^\s*[-*]\s*가설\s+c\d/.test(l)) continue;
    else if (!bullets.length && l.trim() && !/^\s*[-*#|]/.test(l) && !/^\s*c\d+[a-z]?\b/.test(l)) statement.push(l.trim());
    else break;
  }
  const text = [statement.join(' '), ...bullets].join('\n');
  return { statement: statement.join(' ').split(LABELS)[0].replace(/\s*[-—]\s*$/, '').trim(),
    better: field(text, '좋아질 상황'), worse: field(text, '나빠질 가능성'), falsify: field(text, '틀렸다면') };
}
function hypothesis(notesText, id, waveText) {
  const lines = notesText.split('\n');
  const find = key => lines.findIndex(l => !/^\s*#/.test(l) && new RegExp('가설\\s+' + key + '(?![0-9a-z])').test(l));
  // exact id, then the base id (c8b -> c8), then the parent named in "cN: cM + ..." definitions.
  let key = id, relation = 'exact';
  for (let depth = 0; key && depth < 6; depth++) {
    const at = find(key);
    if (at >= 0) return { id: key, relation, ...hypothesisAt(lines, at) };
    const base = key.replace(/[a-z]+$/, '');
    if (base !== key && find(base) >= 0) { key = base; relation = 'derived'; continue; }
    const def = lines.find(l => new RegExp('^\\s*(?:[-*]\\s*)?\\|?\\s*' + key + '\\s*(?::|\\|)\\s*(c\\d+[a-z]?)\\s*\\+').test(l));
    const parent = def && def.match(new RegExp(key + '\\s*(?::|\\|)\\s*(c\\d+[a-z]?)'))[1];
    if (!parent || parent === key) break;
    key = parent; relation = 'derived';
  }
  // A variant defined inline in another hypothesis line ("... c15: 경로 12수") inherits that hypothesis.
  if (id) {
    const inl = lines.findIndex(l => !/^\s*#/.test(l) && /가설\s+c\d+[a-z]?\s*:/.test(l) && new RegExp('(^|[\\s.;(])' + id + '\\s*:').test(l.replace(/^.*?가설\s+c\d+[a-z]?\s*:/, '')));
    if (inl >= 0) return { id: lines[inl].match(/가설\s+(c\d+[a-z]?)/)[1], relation: 'derived', ...hypothesisAt(lines, inl) };
  }
  // Fall back to the first hypothesis written in this wave's own notes.
  const own = waveText.split('\n'), at = own.findIndex(l => !/^\s*#/.test(l) && /가설\s+c\d+/.test(l));
  if (at < 0) return null;
  return { id: own[at].match(/가설\s+(c\d+[a-z]?)/)[1], relation: 'wave', ...hypothesisAt(own, at) };
}
function growth(wave, result, blocks, notesText, ready, checks) {
  const text = blocks.join('\n');
  const lines = text.split('\n');
  const judged = lines.filter(l => /판단\s*:/.test(l)).map(l => clean(l).replace(/^판단\s*:\s*/, '').replace(/\s*—[^—]*:\s*$/, ''));
  const final = judged.filter(l => !/확인 후보/.test(l));
  const nomination = judged.find(l => /확인 후보/.test(l)) || null;
  const confirmHeading = lines.find(l => /^#{2,6}\s.*확인/.test(l) && CAND.test(l));
  const nominated = lines.find(l => /확인 후보/.test(l) && CAND.test(l));
  const id = ((result?.reason || '').match(CAND) || (confirmHeading || '').match(CAND) || (nominated || '').match(CAND) || [])[0] || null;
  const prediction = lines.map(clean).find(l => /예측\s*:/.test(l)) || null;
  const logic = result?.outcome === 'adopt' && result.version ? ready.find(r => r.version === result.version) : null;
  const check = checks.find(c => c.status) || null;
  return {
    candidate: id,
    logic: logic ? logic.text.replace(/\s*근거\s+\S+\s*$/, '') : null,
    judgment: final.length ? final[final.length - 1] : null,
    nomination,
    prediction: prediction ? prediction.replace(/^.*?예측\s*:\s*/, '') : null,
    hypothesis: id || /가설\s+c\d/.test(text) ? hypothesis(notesText, id || 'c-none', text) : null,
    gates: check ? {
      seeds: check.seeds.length, perVersion: check.expected, maps: check.maps, opponents: check.opponents,
      valid: check.status === 'valid',
      complete: check.baselineDone === check.expected && check.candidateDone === check.expected
    } : null
  };
}

// index.log can be rewritten by an operator reset; runner.log and initial-runner.log keep the raw start/exit/STOP lines.
function indexLog(dir) {
  const seen = new Set(), lines = [];
  for (const name of ['initial-runner.log', 'runner.log', 'index.log']) {
    const file = path.join(dir, 'waves', name);
    if (!exists(file)) continue;
    for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
      if (!/^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d (wave |exported |STOP:|disk )/.test(line) || seen.has(line)) continue;
      seen.add(line); lines.push(line);
    }
  }
  return lines.sort().slice(-60);
}

function lineage(name, live) {
  const root = path.join(WORKSPACES, name), dir = path.join(root, 'lineages', name), waves = path.join(dir, 'waves');
  if (!exists(dir)) return { name, state: 'missing' };
  const notes = notesByWave(dir), ledger = ledgerByWave(dir);
  const version = notes.ready.length ? Math.max(...notes.ready.map(r => r.version)) : null;
  const active = readJson(path.join(waves, 'active.json'));
  // A wave without result.json is only "running" while its runner is alive; otherwise it is orphaned.
  const loopAlive = ['running', 'queued', 'stopping'].includes(live?.state);
  const list = waveIds(dir).map(id => {
    const work = locate(dir, id);
    const start = readJson(path.join(work, 'start.json')) || {};
    const result = readJson(path.join(work, 'result.json'));
    const main = transcript(locate(dir, id + '.jsonl'));
    const fallback = transcript(locate(dir, id + '-fallback.jsonl'));
    const current = fallback || main;
    const started = start.started || null, ended = result?.at || null;
    const running = !result && active?.id === id && loopAlive;
    const checks = checksFor(dir, id), blocks = notes.byWave[id] || [];
    return {
      id, started, ended, running,
      durationMs: started && ended ? ms(ended) - ms(started) : null,
      readyBefore: start.ready ?? null,
      outcome: result ? result.outcome : running ? 'running' : 'unknown',
      exit: result?.exit ?? null, reason: result?.reason || null,
      version: result?.version ?? null, commit: result?.commit || null,
      model: main?.summary || null, fallbackModel: fallback?.summary || null, fallbackUsed: !!fallback,
      recent: running ? current?.recent || [] : [], transcriptUpdated: current?.updated || null,
      // The ledger section is shown with the notes but kept out of the growth heuristics.
      checks, notes: ledger[id] ? [...blocks, '#### 오답노트 (LEDGER.md)\n\n' + ledger[id]] : blocks,
      growth: growth(id, result, blocks, notes.text, notes.ready, checks)
    };
  }).reverse();
  const done = list.filter(w => w.durationMs != null);
  const currentReady = notes.ready.find(r => r.version === version) || null;
  const adoptedVersion = Math.max(1, ...list.filter(w => w.outcome === 'adopt' && w.version).map(w => w.version));
  return {
    name, state: live?.state || 'unknown', jobs: (live?.jobs || []).filter(j => j.alive),
    version, versionText: currentReady?.text || null, adoptedVersion,
    activeWave: loopAlive ? active?.id || null : null, activeStarted: loopAlive ? active?.started || null : null,
    lastWave: active?.id || null,
    stats: {
      waves: list.length, finished: done.length, running: list.filter(w => w.running).length,
      adopted: list.filter(w => w.outcome === 'adopt').length,
      rejected: list.filter(w => w.outcome === 'reject').length,
      incomplete: list.filter(w => w.outcome === 'incomplete').length,
      totalMs: done.reduce((s, w) => s + w.durationMs, 0)
    },
    waves: list, log: indexLog(dir)
  };
}

function state() {
  const snap = watch.snapshot();
  const live = Object.fromEntries(snap.lineages.map(item => [item.name, item]));
  return { at: new Date().toISOString(), diskFreeGiB: snap.diskFreeGiB, lineages: NAMES.map(n => lineage(n, live[n])) };
}

// The page lives in its own file so it can use any characters; it is read per request.
const PAGE_FILE = path.join(__dirname, "loop-dashboard.html");


// Lineage agents share this machine's network, so every request needs a token kept where their sandbox cannot read.
const OPERATOR = path.join(path.dirname(path.resolve(__dirname, '..')), 'unsw-arena-clean-control', 'operator-only');
function operatorToken() {
  const file = path.join(OPERATOR, 'dashboard-token');
  if (!exists(file)) fs.writeFileSync(file, crypto.randomBytes(24).toString('hex') + '\n', { mode: 0o600, flag: 'wx' });
  return fs.readFileSync(file, 'utf8').trim();
}
function same(a, b) {
  const x = Buffer.from(String(a || '')), y = Buffer.from(b);
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}
function serve(port) {
  const token = operatorToken(), hosts = ['127.0.0.1:' + port, 'localhost:' + port];
  const server = http.createServer((req, res) => {
    const deny = (code, text) => { res.writeHead(code, { 'content-type': 'text/plain; charset=utf-8' }); res.end(text); };
    try {
      if (req.method !== 'GET') return deny(405, 'method not allowed');
      if (!hosts.includes(req.headers.host)) return deny(403, 'forbidden host');
      const url = new URL(req.url, 'http://127.0.0.1');
      const cookie = (req.headers.cookie || '').split(';').map(s => s.trim()).find(s => s.startsWith('lw='))?.slice(3);
      const viaQuery = same(url.searchParams.get('t'), token);
      if (!viaQuery && !same(cookie, token)) return deny(403, 'operator token required: open the URL in operator-only/dashboard.url');
      const headers = { 'cache-control': 'no-store', 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer' };
      if (viaQuery) headers['set-cookie'] = 'lw=' + token + '; HttpOnly; SameSite=Strict; Path=/';
      if (url.pathname === '/') {
        res.writeHead(200, { ...headers, 'content-type': 'text/html; charset=utf-8',
          'content-security-policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:" });
        return res.end(fs.readFileSync(PAGE_FILE));
      }
      if (url.pathname === '/api/state') {
        const body = JSON.stringify(state());
        res.writeHead(200, { ...headers, 'content-type': 'application/json; charset=utf-8' });
        return res.end(body);
      }
      deny(404, 'not found');
    } catch (error) {
      console.error(new Date().toISOString(), error.stack || error);
      if (!res.headersSent) deny(500, 'state error; see server log'); else res.end();
    }
  });
  server.listen(port, '127.0.0.1', () => {
    const link = 'http://127.0.0.1:' + port + '/?t=' + token;
    fs.writeFileSync(path.join(OPERATOR, 'dashboard.url'), link + '\n', { mode: 0o600 });
    console.log('loop dashboard: http://127.0.0.1:' + port + ' (link with token in operator-only/dashboard.url)');
  });
}

if (require.main === module) {
  const i = process.argv.indexOf('--port');
  if (process.argv.includes('--json')) console.log(JSON.stringify(state(), null, 2));
  else serve(i > 0 ? +process.argv[i + 1] : 4747);
}
module.exports = { state, hypothesis };
