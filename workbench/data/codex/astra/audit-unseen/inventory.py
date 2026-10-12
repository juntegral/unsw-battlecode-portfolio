from pathlib import Path
import datetime
import hashlib
import json
import re

root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
source = root / 'data/online/smoke/one17-bot/main.cpp'
raw = source.read_bytes()
lines = raw.decode().splitlines()
constants = []
for number, line in enumerate(lines, 1):
    match = re.match(r'constexpr\s+\S+\s+(\w+)\s*=\s*(.*);', line)
    if match:
        name, value = match.groups()
        uses = [i for i, text in enumerate(lines, 1)
                if i != number and re.search(r'\b' + name + r'\b', text)]
        constants.append(dict(name=name, value=value, declaration=number, uses=uses))
patterns = {
    'map': r'\b(cells|width|height|center_map|aggressive|home_closed)\b',
    'round': r'\bround\b|_round\b|_rounds\b|_ROUNDS?\b',
    'count': r'get_unit_count|unit_limit|ally_heads\.size|enemy_heads\.size|reports\.size|HERD_MIN|TRADE_MIN|ATTACK_MIN',
    'portal': r'EDGE_PORTAL|PORTAL_|portal_|mouth_fresh|SN_TAIL_MOUTH',
}
hits = {}
for kind, pattern in patterns.items():
    hits[kind] = [dict(line=i, text=text.strip()) for i, text in enumerate(lines, 1)
                  if re.search(pattern, text)]
evidence = dict(timestamp=datetime.datetime.now().astimezone().isoformat(),
                source=str(source.relative_to(root)), sha256=hashlib.sha256(raw).hexdigest(),
                lines=len(lines), constants=constants, search_hits=hits,
                caveat='Lexical index, not a proof of reachability; report.md contains manual call-path analysis.')
(out / 'inventory.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: evidence[k] for k in ('timestamp', 'source', 'sha256', 'lines')}, ensure_ascii=False))
