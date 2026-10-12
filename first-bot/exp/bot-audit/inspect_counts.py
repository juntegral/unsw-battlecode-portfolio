#!/usr/bin/env python3
"""Summarise audited turn labels; keep full evidence in the two TSV.gz files."""
import collections
import csv
import gzip
import json
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parent
results = {}
for name, folder in [('W11', OUT), ('W12', OUT/'w12')]:
    rows = gzip.open(folder/'turn-tags.tsv.gz', 'rt')
    h = csv.DictReader(rows, delimiter='\t')
    x = collections.Counter()
    examples = collections.defaultdict(list)
    for r in h:
        text, tags = r['indicator'], set(r['tags'].split(','))
        for goal in ('g','F','kx','gh','ghd'):
            if goal in tags:
                x[goal+'_all'] += 1
                if tags.intersection({'TRADE','PORTAL?'}):
                    x[goal+'_without_dfs_leaf'] += 1
        if r['kind']=='noexit' and 'noexit_spare' in tags:
            x['noexit_spare'] += 1
        if r['kind'] in ('frag','csplit') and r['trueKing']=='1' and int(r['length'])>=8:
            x[r['kind']+'_true_long_king'] += 1
            if len(examples[r['kind']])<8: examples[r['kind']].append(r)
        if tags.intersection({'cov','cl','grab','g','F','kx','ghd'}):
            if len(tags.intersection({'cov','cl','grab','g','F','kx','ghd'}))>=2:x['multiple_goal_labels']+=1
        if 'ghd' in tags and 'grab' in tags:
            x['ghd_grab'] += 1
            a = re.search(r'ghd@(\d+,\d+)',text)
            b = re.search(r'(?:^| )grab@(\d+,\d+)',text)
            x['ghd_grab_same_tile'] += bool(a and b and a[1]==b[1])
        if tags.intersection({'F','g'}) and tags.intersection({'cl','grab','cov'}):x['explicit_goal_plus_other_pull']+=1
        if 'kx' in tags and 'kxm' in tags:x['kx_moving_away_path']+=1
        if int(r['dragonId'])>255:x['turns_from_high_id']+=1
    results[name]={'counts':dict(x),'examples':dict(examples)}
(OUT/'label-interactions.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v['counts'] for k,v in results.items()},indent=2))
