"""assemble.py — joins the hand-written narrative (narrative-*.md) with the generated tables (tables.md, cache/eras.md,
cache/fortress.md) into research/observations/map-atlas.md. Markers: {{TABLES:<map>/<layout>}}, {{GLOBAL:<name>}}, {{ERAS}},
{{FORTRESS}}. Fails if a marker is left unresolved."""
import pathlib, re
H = pathlib.Path(__file__).resolve().parent; ROOT = H.parents[1]
tables = (H / 'tables.md').read_text()
def block(tag):
    m = re.search(r'<!-- ' + re.escape(tag) + r' -->\n(.*?)\n?<!-- /' + re.escape(tag) + r' -->', tables, re.S)
    if not m: raise SystemExit('missing block ' + tag)
    return m.group(1).strip() + '\n'
parts = [(H / f'narrative-{p}.md').read_text() for p in ['head', 'mid', 'maps', 'tail']]
doc = '\n'.join(parts)
doc = re.sub(r'\{\{TABLES:([^}]+)\}\}', lambda m: block('lay:' + m.group(1)), doc)
doc = re.sub(r'\{\{GLOBAL:([^}]+)\}\}', lambda m: block('global:' + m.group(1)), doc)
doc = doc.replace('{{ERAS}}', (H / 'cache' / 'eras.md').read_text().strip() + '\n')
doc = doc.replace('{{TEAMS}}', (H / 'cache' / 'teams.md').read_text().strip() + '\n')
doc = doc.replace('{{FORTRESS}}', (H / 'cache' / 'fortress.md').read_text().strip() + '\n')
left = re.findall(r'\{\{[^}]*\}\}', doc)
if left: raise SystemExit('unresolved ' + ', '.join(left))
out = ROOT / 'research' / 'observations' / 'map-atlas.md'
out.parent.mkdir(parents=True, exist_ok=True); out.write_text(doc)
print(out, len(doc.splitlines()), 'lines', len(doc), 'chars')
