#!/usr/bin/env python3
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent
a = json.loads((OUT/'counts.json').read_text())
b = json.loads((OUT/'w12/counts.json').read_text())
p = json.loads((OUT/'parameters.json').read_text())
lines = ['# Generated audit tables', '', 'All tag rates use own dragon turns, not game rounds. Counts are not causal effects.', '']
lines += ['## Tags', '', '| Tag | W11 count | W11/game | W12 count | W12/game | W12 games with tag | W12 turns % |', '|---|---:|---:|---:|---:|---:|---:|']
at = {x['tag']:x for x in a['tagSummary']}
for x in b['tagSummary']:
    y = at[x['tag']]
    lines.append(f"| `{x['tag']}` | {y['n']:,} | {y['perGame']:.2f} | {x['n']:,} | {x['perGame']:.2f} | {x['gamesWithTag']}/70 | {x['turnShare']*100:.3f} |")
lines += ['', '## Split mix', '', '| Rule | W11 | W11 all splits % | W12 | W12 all splits % | W12 non-escape % |', '|---|---:|---:|---:|---:|---:|']
for k in ['escsplit','escsplit2','split','frag','bsplit','csplit','kcap','floor','lsplit']:
    x,y=a['splits'].get(k,0),b['splits'].get(k,0)
    lines.append(f"| `{k}` | {x:,} | {100*x/sum(a['splits'].values()):.3f} | {y:,} | {100*y/sum(b['splits'].values()):.3f} | {'—' if k.startswith('esc') else format(100*y/b['nonEscapeSplits'],'.3f')} |")
lines += ['', '## Explicit goals', '', '| Label state | W11 turns | W11 move % | W12 turns | W12 move % | W12 all turns % |', '|---|---:|---:|---:|---:|---:|']
for k in ['F','g','K','none','early_action']:
    x,y=a['explicitGoals'].get(k,0),b['explicitGoals'].get(k,0)
    lines.append(f"| `{k}` | {x:,} | {'—' if k=='early_action' else format(100*x/a['move'],'.3f')} | {y:,} | {'—' if k=='early_action' else format(100*y/b['move'],'.3f')} | {100*y/b['turns']:.3f} |")
lines += ['', '## Current booleans', '', '| Parameter | Value | params.hpp line | Code uses |', '|---|---|---:|---|']
for x in p:
    if x['type']=='bool':lines.append(f"| `{x['name']}` | `{x['value']}` | {x['line']} | {', '.join(x['uses'])} |")
lines += ['', '## W12 phase counts', '', '| Round window | All turns | F | g | csplit | lsplit | frag | floor | escape-split |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for ph,x in b['phases'].items():
    lines.append('| '+ph+' | '+' | '.join(f'{n:,}' for n in [x['turns'],x['goals'].get('F',0),x['goals'].get('g',0),*[x['splits'].get(k,0) for k in ['csplit','lsplit','frag','floor','escsplit']]])+' |')
(OUT/'tables.md').write_text('\n'.join(lines)+'\n')
print('Wrote exp/bot-audit/tables.md')
