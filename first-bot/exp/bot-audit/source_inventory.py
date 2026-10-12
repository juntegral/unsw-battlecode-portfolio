#!/usr/bin/env python3
"""Read-only source audit. All generated files stay beside this new script."""
import difflib
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
CURRENT = ROOT / 'exp/cand-stack11/bot'


def clean_cpp(s):
    # Preserve positions/newlines, so comments and strings cannot confuse braces.
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern, lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), s)


def main():
    dirs = [ROOT / 'bot'] + [ROOT / f'exp/cand-stack{i}/bot' for i in range(1, 12)]
    reads = []
    for d in dirs:
        if d.exists():
            reads += [p for p in d.iterdir() if p.is_file() and p.suffix in ('.cpp', '.hpp', '.toml')]
    reads += [ROOT / 'CLAUDE.md', ROOT / 'research/experiments/STACK-BACKLOG.md', ROOT / 'research/experiments/VERSIONS.md']
    reads += list((ROOT / 'research/experiments').glob('cand-stack*.md'))
    reads += [ROOT / 'research/experiments/cand-mapid.md']
    reads += [p for p in (ROOT / 'research/observations').glob('*.md') if p.name in (
        'intake-gap.md', 'supply-chain.md', 'endgame-king.md', 'conversion-chain.md',
        'economy-principles.md', 'our-eliminations.md', 'top-territory.md')]
    reads += [ROOT / f'tools/{n}.js' for n in ('mech_check', 'replay', 'top_features', 'mass_ledger')]
    reads += list((ROOT.parent / 'unsw-arena/rules').glob('*.md'))
    reads += [p for d in dirs[1:] for p in (d.parent / 'bot.diff', d.parent / 'apply.js') if p.exists()]
    manifest = []
    for p in sorted(set(reads)):
        raw = p.read_bytes()
        manifest.append({'path': str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                         'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
                         'lines': len(raw.splitlines())})
    (OUT / 'source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

    sources = {p.name: p.read_text() for p in CURRENT.iterdir() if p.suffix in ('.cpp', '.hpp')}
    constants = []
    for i, l in enumerate(sources['params.hpp'].splitlines(), 1):
        m = re.search(r'constexpr\s+(bool|int|double|long long)\s+(\w+)\s*=\s*([^;]+);', l)
        if not m:
            continue
        typ = m[1]
        decl = l.split(typ, 1)[1].split(';', 1)[0]
        for item in re.finditer(r'(\w+)\s*=\s*(.*?)(?=,\s*\w+\s*=|$)', decl):
            name, val = item.groups()
            usage = []
            for f, s in sources.items():
                if f == 'params.hpp':
                    continue
                for j, line in enumerate(clean_cpp(s).splitlines(), 1):
                    if re.search(r'\bP::' + name + r'\b', line):
                        usage.append(f'{f}:{j}')
            constants.append({'name': name, 'type': typ, 'value': val.strip(), 'line': i, 'uses': usage})
    (OUT / 'parameters.json').write_text(json.dumps(constants, indent=2) + '\n')
    (OUT / 'parameters.tsv').write_text('name\ttype\tvalue\tline\tuses\n' + ''.join(
        f"{x['name']}\t{x['type']}\t{x['value']}\t{x['line']}\t{','.join(x['uses'])}\n" for x in constants))

    functions = []
    for f, s in sources.items():
        if not f.endswith('.cpp'):
            continue
        c = clean_cpp(s)
        pat = r'^(?:[\w:<>&*]+\s+)+((?:Planner|World|Reader|Writer)::\w+|\w+)\([^;{}]*\)\s*(?:const\s*)?\{'
        for m in re.finditer(pat, c, re.M):
            a = c.find('{', m.start(), m.end())
            depth, b = 1, a + 1
            while b < len(c) and depth:
                depth += (c[b] == '{') - (c[b] == '}')
                b += 1
            start, end = c.count('\n', 0, m.start()) + 1, c.count('\n', 0, b) + 1
            functions.append({'file': f, 'name': m[1], 'start': start, 'end': end,
                              'raw_lines': end-start+1,
                              'nonempty_code_lines': sum(bool(l.strip()) for l in c[m.start():b].splitlines())})
    (OUT / 'functions.json').write_text(json.dumps(functions, indent=2) + '\n')

    diffs, stats = [], []
    for i in range(1, len(dirs)):
        old, new = dirs[i-1], dirs[i]
        if not old.exists() or not new.exists():
            stats.append({'stack': i, 'missing': str(old if not old.exists() else new)})
            continue
        names = sorted(set(p.name for p in old.iterdir() if p.suffix in ('.cpp', '.hpp')) |
                       set(p.name for p in new.iterdir() if p.suffix in ('.cpp', '.hpp')))
        row = {'stack': i, 'from': str(old.relative_to(ROOT)), 'to': str(new.relative_to(ROOT)), 'files': []}
        for n in names:
            a = (old/n).read_text().splitlines(True) if (old/n).exists() else []
            b = (new/n).read_text().splitlines(True) if (new/n).exists() else []
            d = list(difflib.unified_diff(a, b, fromfile=str(old.relative_to(ROOT)/n), tofile=str(new.relative_to(ROOT)/n)))
            if d:
                diffs += d
                row['files'].append({'name': n, 'added': sum(x.startswith('+') and not x.startswith('+++') for x in d),
                                     'removed': sum(x.startswith('-') and not x.startswith('---') for x in d)})
        stats.append(row)
    (OUT/'stack-history.diff').write_text(''.join(diffs))
    (OUT/'stack-history.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')
    report = {'current_files': {n: len(s.splitlines()) for n,s in sources.items()},
              'functions': len(functions), 'constants': len(constants),
              'booleans': [x for x in constants if x['type']=='bool'],
              'unreferenced': [x for x in constants if not x['uses']], 'history': stats}
    (OUT/'source-inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'files': report['current_files'], 'constants': len(constants), 'functions': len(functions),
                      'unused': [x['name'] for x in report['unreferenced']],
                      'diff_totals': [{'stack':x['stack'], 'added':sum(y['added'] for y in x.get('files',[])),
                                       'removed':sum(y['removed'] for y in x.get('files',[]))} for x in stats]}, indent=2))


if __name__ == '__main__':
    main()
