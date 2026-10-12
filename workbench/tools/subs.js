#!/usr/bin/env node
// subs.js: list our team's submissions with their descriptions (read-only).
// usage: node tools/subs.js list [--last N] [--json]
// Reads the game key the same way submit.js does and never prints it.
const fs = require('fs'), os = require('os'), path = require('path');
const BASE = process.env.UNSWBC_API || 'https://game.battlecode.au/api/v1';
const argv = process.argv.slice(2), cmd = argv[0];
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i > 0 ? argv[i + 1] : d; };
const redact = s => String(s).replace(/bc_[A-Za-z0-9_-]+/g, 'bc_[REDACTED]');
function key() {
  const env = (process.env.UNSWBC_KEY || '').trim(); if (env) return env;
  const t = fs.readFileSync(process.env.UNSW_KEY_FILE || path.join(os.homedir(), 'Downloads', 'api.txt'), 'utf8');
  const k = (t.match(/bc_[A-Za-z0-9_-]+/) || [])[0]; if (!k) throw Error('API key not found'); return k;
}
async function get(p) {
  const r = await fetch(BASE + p, { headers: { Authorization: 'Bearer ' + key() } });
  const text = await r.text();
  if (!r.ok) throw Error(`GET ${p} -> ${r.status} ${redact(text).slice(0, 200)}`);
  return JSON.parse(text);
}
(async () => {
  if (cmd === 'set-desc') {
    // usage: subs.js set-desc <id> <text> : tries the usual REST verbs and says which one the server accepts.
    const id = +argv[1], text = argv[2];
    if (!id || !text) { console.error('usage: subs.js set-desc <id> "<text>"'); process.exit(2); }
    for (const method of ['PATCH', 'PUT']) {
      const r = await fetch(`${BASE}/submissions/${id}`, { method, headers: { Authorization: 'Bearer ' + key(), 'Content-Type': 'application/json' }, body: JSON.stringify({ description: text }) });
      const body = redact(await r.text()).replace(/\s+/g, ' ').slice(0, 160);
      console.log(`${method} /submissions/${id} -> ${r.status} ${body}`);
      if (r.ok) break;
    }
    const s = (await get('/submissions')).find(x => x.id === id);
    console.log(`now: v${s && s.version} ${s && s.name} | ${s && s.description}`);
    return;
  }
  if (cmd !== 'list') { console.error('usage: subs.js list [--last N] [--json] | set-desc <id> <text>'); process.exit(2); }
  const subs = (await get('/submissions')).slice().sort((a, b) => a.id - b.id);
  const last = +opt('last', 12), rows = subs.slice(-last);
  if (argv.includes('--json')) { console.log(redact(JSON.stringify(rows, null, 1))); return; }
  console.log('fields: ' + Object.keys(subs[subs.length - 1] || {}).join(', '));
  console.log(`total ${subs.length}`);
  for (const s of rows) {
    const v = s.version != null ? 'v' + s.version : '';
    const d = s.description ?? s.notes ?? s.desc ?? '';
    console.log(redact(`${v}\t${s.id}\t${s.status}\t${s.name}\t${String(d).replace(/\s+/g, ' ').slice(0, 110)}`));
  }
})().catch(e => { console.error(redact(e.message)); process.exit(1); });
