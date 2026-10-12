def major_lineage(lineage):
    start=0
    for k,a in enumerate(lineage):
        if 2*a['child_length']<a['before']:
            start=k+1
    return lineage[start:]

if __name__=='__main__':
    import json
    from pathlib import Path
    out=Path('data/codex/astra/longest')
    for name in ('games.jsonl','local.jsonl'):
        p=out/name
        rows=[json.loads(l) for l in p.read_text().splitlines()]
        for g in rows:
            for pair in g['snapshots'].values():
                for x in pair:
                    if x['role'] in ('ordinary','inherited-fed') and x['id'] is not None:
                        st=g['all_dragons'][str(x['id'])]
                        x['role']='inherited-fed' if any(a['stop_drop']>0 for a in major_lineage(st['lineage'])) else 'ordinary'
        p.write_text(''.join(json.dumps(g,separators=(',',':'))+'\n' for g in rows))
