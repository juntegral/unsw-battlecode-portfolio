from pathlib import Path
import difflib
import hashlib
import re
from datetime import datetime

root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
old = root / 'data/online/smoke/one5-bot/main.cpp'
live = root / 'data/online/smoke/one17-bot/main.cpp'
a, b = old.read_text().splitlines(), live.read_text().splitlines()

def functions(lines):
    starts = []
    for i, line in enumerate(lines):
        if line == '    unswbc::Controller& ct;':
            break
        m = re.match(r'^    (?:[\w:<>,*&]+\s+)*([A-Za-z_]\w*)\(', line)
        if m and m[1] not in ('if', 'while', 'for', 'switch', 'return'):
            starts.append((i, m[1]))
    result = {}
    for i, name in starts:
        j = i
        while j < len(lines) and '{' not in lines[j]:
            j += 1
        depth = 0
        for k in range(j, len(lines)):
            s = re.sub(r'"(?:\\.|[^"\\])*"', '""', lines[k].split('//')[0])
            depth += s.count('{') - s.count('}')
            if depth == 0:
                result[name] = (i + 1, k + 1, lines[i:k + 1])
                break
    return result

fa, fb = functions(a), functions(b)
rows = []
for name, (start, end, body) in fb.items():
    oldf = fa.get(name)
    kind = 'NEW' if oldf is None else 'SAME' if body == oldf[2] else 'CHANGED'
    relevant = [(start + i, s.strip()) for i, s in enumerate(body)
                if re.search(r'\b(for|while)\s*\(|std::(find|any_of|none_of|count_if|sort|remove_if|min_element)|\.(assign|resize|insert)\(', s)]
    rows.append(f'{name}: live {start}-{end}; one5 {oldf[0] if oldf else "absent"}; {kind}')
    rows.extend(f'  {n}: {s}' for n, s in relevant)
out.joinpath('function-inventory.txt').write_text('\n'.join(rows) + '\n')
out.joinpath('one5-to-one17.diff').write_text('\n'.join(difflib.unified_diff(a, b, fromfile=str(old), tofile=str(live))) + '\n')
metadata = [f'Generated {datetime.now().astimezone().isoformat()}']
for p in (old, live, live.with_name('helper.hpp'), live.with_name('sonar_codec.hpp')):
    metadata.append(f'{p.relative_to(root)} sha256={hashlib.sha256(p.read_bytes()).hexdigest()} lines={len(p.read_text().splitlines())}')
metadata.extend([
    'Static upper-bound arithmetic (not measured bot executions):',
    f'256 * 256 = {256 * 256}',
    f'four survey traversals, allowing two queue entries per cell = {4 * 2 * 256 * 256}',
    f'depth-6 four-way tree, including root = {sum(4 ** k for k in range(7))}',
    f'depth-8 look_gain, first cell fixed, four-way upper bound = {sum(4 ** k for k in range(8))}',
    f'vision cells = {7 * 7}',
])
out.joinpath('evidence.txt').write_text('\n'.join(metadata) + '\n')
print('\n'.join(metadata))
print(f'Indexed {len(fb)} live functions; manual reachability review is required.')
