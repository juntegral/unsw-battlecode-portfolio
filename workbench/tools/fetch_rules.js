#!/usr/bin/env node
// Save the public game docs (https://game.battlecode.au/docs/<page>) as light markdown in rules/.
// usage: node tools/fetch_rules.js [--out rules] [--raw <dir>] [--from-raw <dir>] [--delay 2000] [--dry]
//   --out       where <page>.md and ALL.md go (default rules/). Other files there (judge-limits.md, CHANGES-*.md) are left alone.
//   --raw       also keep each fetched HTML page and manifest.json (page order, fetch times) in <dir>.
//   --from-raw  convert a folder saved by --raw instead of fetching. No network.
//   --dry       fetch and convert, print each page's status, write nothing.
// The page list is the site's docs navigation, cross-checked against the search index embedded in the page.
// Public pages only: no API key, no /api/v1. One request at a time, with a pause between requests.
// A page whose converted body is byte-identical to the existing file is not rewritten, so its Source line keeps the
// time the text was first fetched. ALL.md is <page>.md without the Source line, in navigation order, each under "=== <page> ===".
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const SITE = 'https://game.battlecode.au', ENTRY = '/docs/overview';
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const OUT = path.resolve(ROOT, arg('out', 'rules')), RAW = arg('raw', null), FROM_RAW = arg('from-raw', null);
const DELAY = +arg('delay', '2000'), DRY = process.argv.includes('--dry');
const KEEP = /^(judge-limits\.md|ALL\.md|CHANGES-.*\.md)$/; // ours, not docs pages
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------- fetching ----------
let lastRequest = 0;
async function get(url) {
  for (let attempt = 0; ; attempt++) {
    const wait = lastRequest + DELAY - Date.now(); if (wait > 0) await sleep(wait);
    lastRequest = Date.now();
    const r = await fetch(url, { headers: { 'User-Agent': 'unsw-heuristic fetch_rules.js (public docs copy)' }, signal: AbortSignal.timeout(30000) });
    if ((r.status === 429 || r.status >= 500) && attempt < 2) { await sleep(1000 * (+r.headers.get('retry-after') || 30)); continue; }
    if (!r.ok) throw Error(url + ' -> ' + r.status);
    return { html: await r.text(), finalUrl: r.url, fetchedAt: new Date().toISOString() };
  }
}

// ---------- a small HTML parser (the pages are server-rendered Svelte, well formed) ----------
const VOID = new Set('area base br col embed hr img input link meta source track wbr'.split(' '));
const RAWTEXT = new Set(['script', 'style', 'textarea', 'title']);
function parse(html) {
  const root = { tag: '#root', attrs: {}, children: [] }, stack = [root];
  const re = /<!--[\s\S]*?-->|<!\[CDATA\[[\s\S]*?\]\]>|<![^>]*>|<\/?([A-Za-z][\w:-]*)((?:\s+[^\s"'>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'=<>`]+))?)*)\s*(\/?)>/g;
  let last = 0, m;
  const text = t => { if (t) stack[stack.length - 1].children.push({ text: t }); };
  while ((m = re.exec(html))) {
    text(html.slice(last, m.index)); last = re.lastIndex;
    if (!m[1]) continue; // comment, doctype
    const tag = m[1].toLowerCase(), top = () => stack[stack.length - 1];
    if (m[0][1] === '/') { // closing tag: pop to the matching element, if any is open
      for (let i = stack.length - 1; i > 0; i--) if (stack[i].tag === tag) { stack.length = i; break; }
      continue;
    }
    const attrs = {};
    for (const a of (m[2] || '').matchAll(/([^\s"'>\/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g))
      attrs[a[1].toLowerCase()] = decode(a[2] ?? a[3] ?? a[4] ?? '');
    const el = { tag, attrs, children: [] };
    top().children.push(el);
    if (RAWTEXT.has(tag)) {
      const end = html.toLowerCase().indexOf('</' + tag, last);
      el.children.push({ text: html.slice(last, end < 0 ? html.length : end) });
      last = end < 0 ? html.length : html.indexOf('>', end) + 1; re.lastIndex = last;
    } else if (!VOID.has(tag) && !m[3]) stack.push(el);
  }
  text(html.slice(last));
  return root;
}
const NAMED = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', mdash: '—', ndash: '–', minus: '−', times: '×',
  hellip: '…', middot: '·', rarr: '→', larr: '←', le: '≤', ge: '≥', lsquo: '‘', rsquo: '’', ldquo: '“', rdquo: '”', bull: '•', copy: '©' };
function decode(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => e[0] === '#'
    ? String.fromCodePoint(e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : +e.slice(1))
    : NAMED[e] ?? m);
}
const cls = n => ' ' + (n.attrs?.class || '') + ' ';
const hasClass = (n, c) => !!n.tag && cls(n).includes(' ' + c + ' ');
function find(n, pred) {
  if (pred(n)) return n;
  for (const c of n.children || []) { const r = find(c, pred); if (r) return r; }
  return null;
}
function findAll(n, pred, out = []) {
  if (pred(n)) out.push(n);
  for (const c of n.children || []) findAll(c, pred, out);
  return out;
}
// Cloudflare hides anything that looks like an e-mail address (here: curl's -F zip=@mybot.zip) behind a script.
function cfEmail(hex) {
  const key = parseInt(hex.slice(0, 2), 16); let s = '';
  for (let i = 2; i < hex.length; i += 2) s += String.fromCharCode(parseInt(hex.slice(i, i + 2), 16) ^ key);
  return s;
}
function rawText(n) { // text as written, for code blocks
  if (n.text !== undefined) return decode(n.text);
  if (n.attrs?.['data-cfemail']) return cfEmail(n.attrs['data-cfemail']);
  return (n.children || []).map(rawText).join('');
}

// ---------- HTML -> light markdown ----------
const SKIP = new Set(['script', 'style', 'svg', 'canvas', 'button', 'input', 'nav', 'template', 'noscript']);
const BLOCK = new Set(['p', 'div', 'ul', 'ol', 'li', 'pre', 'table', 'figure', 'figcaption', 'blockquote', 'hr', 'section', 'article',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dl', 'dt', 'dd']);
const BR = '\u0000';
const squash = s => s.replace(/[ \t\r\n\f\v ]+/g, ' ').split(BR).map(l => l.trim()).join('\n').trim();
const ticks = s => { const t = s.includes('`') ? '``' : '`'; return t + (t === '``' ? ' ' + s + ' ' : s) + t; };

function inline(n) {
  if (n.text !== undefined) return decode(n.text);
  const t = n.tag;
  if (SKIP.has(t)) return '';
  if (n.attrs['data-cfemail']) return cfEmail(n.attrs['data-cfemail']);
  const inner = () => (n.children || []).map(inline).join('');
  if (t === 'br') return BR;
  if (t === 'code' || t === 'kbd' || t === 'samp') { const s = rawText(n).replace(/\s+/g, ' ').trim(); return s ? ticks(s) : ''; }
  if (t === 'sub') return '_' + inner().trim();
  if (t === 'sup') { const s = inner().trim(); return /^[\w.]+$/.test(s) ? '^' + s : '^(' + s + ')'; }
  if (t === 'img') return n.attrs.alt ? '[image: ' + n.attrs.alt + ']' : '[image]';
  return inner(); // a, strong, em, span, small, ...: text only, like the 2026-09-27 copy
}
const isBlock = n => n.tag && (BLOCK.has(n.tag) || n.tag === 'figure');

// Returns a list of markdown blocks; the caller joins them with blank lines.
function blocks(n, ctx = {}) {
  const out = [];
  let run = []; // inline nodes between blocks (text directly inside a div, say)
  const flush = () => { const s = squash(run.map(inline).join('')); if (s) out.push(s); run = []; };
  for (const c of n.children || []) {
    if (c.text !== undefined || !isBlock(c)) { if (!SKIP.has(c.tag)) run.push(c); continue; }
    flush();
    out.push(...block(c, ctx));
  }
  flush();
  return out;
}

function block(n, ctx) {
  const t = n.tag;
  if (hasClass(n, 'docs-turn')) return [];              // Previous / Next links
  if (hasClass(n, 'tabs') && n.attrs.role === 'tablist') return []; // helper page language switch (Python shown)
  if (/^h[1-6]$/.test(t)) return ['#'.repeat(+t[1]) + ' ' + squash(n.children.map(inline).join(''))];
  if (t === 'p' || t === 'dt' || t === 'dd') { const s = squash(n.children.map(inline).join('')); return s ? [s] : []; }
  if (t === 'hr') return ['---'];
  if (t === 'pre') return [fence(rawText(n), ctx.lang)];
  if (t === 'ul' || t === 'ol') return [list(n)];
  if (t === 'table') return [table(n)];
  if (t === 'figure') return [figure(n)];
  if (t === 'blockquote') return blocks(n, ctx).map(b => b.replace(/^/gm, '> '));
  if (hasClass(n, 'code-block')) {
    const bar = find(n, x => hasClass(x, 'code-toolbar'));
    const sel = bar && find(bar, x => x.tag === 'button' && x.attrs.role === 'tab' && x.attrs['aria-selected'] === 'true');
    const label = sel ? rawText(sel).trim() : bar ? squash(bar.children.filter(x => x.tag !== 'button').map(inline).join('')) : '';
    const lang = { Python: 'python', C: 'c', 'C++': 'cpp', Raw: 'text' }[label] || '';
    return findAll(n, x => x.tag === 'pre').map(p => fence(rawText(p), lang));
  }
  if (hasClass(n, 'syms')) // helper reference: one entry per call
    return [findAll(n, x => hasClass(x, 'sym')).map(s => '- ' + squash(s.children.map(c => c.tag === 'p' ? ' ' + inline(c) : inline(c)).join(''))).join('\n')];
  return blocks(n, ctx); // div, section, figcaption, ...: containers
}

function fence(code, lang) {
  code = code.replace(/^\n/, '').replace(/\s+$/, '');
  let f = '```'; while (code.includes(f)) f += '`';
  return f + (lang || '') + '\n' + code + '\n' + f;
}

function list(n) {
  const ordered = n.tag === 'ol'; let k = +(n.attrs.start || 1);
  return n.children.filter(c => c.tag === 'li').map(li => {
    const mark = ordered ? (k++) + '. ' : '- ';
    const body = li.children.some(isBlock) ? blocks(li).join('\n\n') : squash(li.children.map(inline).join(''));
    return mark + body.replace(/\n/g, '\n' + ' '.repeat(mark.length));
  }).join('\n');
}

function table(n) {
  const rows = findAll(n, x => x.tag === 'tr').map(tr => ({
    head: tr.children.some(c => c.tag === 'th') && !tr.children.some(c => c.tag === 'td'),
    cells: tr.children.filter(c => c.tag === 'th' || c.tag === 'td').map(c => squash(c.children.map(inline).join('')).replace(/\|/g, '\\|').replace(/\n/g, ' ')),
  }));
  if (!rows.length) return '';
  const width = Math.max(...rows.map(r => r.cells.length));
  const line = cells => '| ' + [...cells, ...Array(width - cells.length).fill('')].join(' | ') + ' |';
  const out = [];
  if (rows[0].head) out.push(line(rows.shift().cells)); else out.push(line(Array(width).fill('')));
  out.push('|' + Array(width).fill('---|').join(''));
  for (const r of rows) out.push(line(r.cells));
  return out.join('\n');
}

function figure(n) { // animated board: keep only the caption
  const cap = find(n, x => x.tag === 'figcaption');
  const textSpan = cap && find(cap, x => hasClass(x, 'text'));
  const s = textSpan ? squash(inline(textSpan)) : cap ? squash(cap.children.filter(c => !hasClass(c, 'bar')).map(inline).join('')) : '';
  return s ? '[figure: ' + s + ']' : '[figure]';
}

function convert(html) {
  const doc = parse(html);
  const article = find(doc, x => x.tag === 'article');
  if (!article) throw Error('no <article> in page');
  const md = blocks(article).join('\n\n').replace(/\n{3,}/g, '\n\n').trim();
  if (!md.startsWith('# ')) throw Error('page body does not start with a title');
  return md;
}

// Navigation order from the docs rail; pages only in the search index are appended with a warning.
function pageList(html) {
  const doc = parse(html);
  const nav = find(doc, x => x.tag === 'nav' && x.attrs.id === 'docs-nav');
  if (!nav) throw Error('docs navigation not found: the site layout changed');
  const slugs = [];
  for (const a of findAll(nav, x => x.tag === 'a')) {
    const m = (a.attrs.href || '').match(/^\/docs\/([\w-]+)$/);
    if (m && !slugs.includes(m[1])) slugs.push(m[1]);
  }
  const indexed = [...html.matchAll(/href:"\/docs\/([\w-]+)[#"]/g)].map(m => m[1]);
  const extra = [...new Set(indexed)].filter(s => !slugs.includes(s));
  if (extra.length) console.error('warning: in the search index but not in the navigation: ' + extra.join(', '));
  if (slugs.length < 5) throw Error('docs navigation has only ' + slugs.length + ' pages');
  return [...slugs, ...extra];
}

(async () => {
  const pages = []; // {slug, url, html, fetchedAt}
  if (FROM_RAW) {
    const man = JSON.parse(fs.readFileSync(path.join(FROM_RAW, 'manifest.json'), 'utf8'));
    for (const p of man.pages) pages.push({ ...p, html: fs.readFileSync(path.join(FROM_RAW, p.slug + '.html'), 'utf8') });
  } else {
    const first = await get(SITE + ENTRY);
    const slugs = pageList(first.html);
    for (const slug of slugs) {
      const url = SITE + '/docs/' + slug;
      const r = slug === ENTRY.split('/').pop() ? first : await get(url);
      if (r.finalUrl.replace(/\/$/, '') !== url) console.error('warning: ' + url + ' redirected to ' + r.finalUrl);
      pages.push({ slug, url, html: r.html, fetchedAt: r.fetchedAt });
    }
    if (RAW) {
      fs.mkdirSync(RAW, { recursive: true });
      for (const p of pages) fs.writeFileSync(path.join(RAW, p.slug + '.html'), p.html);
      fs.writeFileSync(path.join(RAW, 'manifest.json'), JSON.stringify({ site: SITE, pages: pages.map(({ html, ...p }) => p) }, null, 1));
    }
  }

  const results = [];
  for (const p of pages) {
    const body = convert(p.html);
    const file = path.join(OUT, p.slug + '.md');
    const old = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null;
    const oldBody = old === null ? null : old.slice(old.indexOf('\n') + 1).trim();
    const status = old === null ? 'new' : oldBody === body ? 'same' : 'changed';
    const text = status === 'same' ? old : 'Source: ' + p.url + ' (fetched ' + p.fetchedAt + ')\n\n' + body + '\n';
    results.push({ slug: p.slug, status, text });
    console.log(status.padEnd(8) + p.slug);
  }
  const all = results.map(r => '=== ' + r.slug + ' ===\n' + r.text.slice(r.text.indexOf('\n') + 1)).join('\n');
  const known = new Set(results.map(r => r.slug + '.md'));
  if (fs.existsSync(OUT)) for (const f of fs.readdirSync(OUT))
    if (f.endsWith('.md') && !known.has(f) && !KEEP.test(f)) console.error('warning: ' + f + ' is not on the site any more (left in place)');
  if (DRY) return;
  fs.mkdirSync(OUT, { recursive: true });
  for (const r of results) if (r.status !== 'same') fs.writeFileSync(path.join(OUT, r.slug + '.md'), r.text);
  fs.writeFileSync(path.join(OUT, 'ALL.md'), all);
  console.log(`${results.length} pages, ${results.filter(r => r.status !== 'same').length} written, ALL.md regenerated -> ${path.relative(ROOT, OUT) || '.'}`);
})().catch(e => { console.error(e.message); process.exit(1); });
