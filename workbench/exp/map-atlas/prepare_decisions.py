"""Freeze the inherited decision metadata for the same full replay populations."""
import pathlib,json,collections,sys
R=pathlib.Path(__file__).resolve().parents[2];O=R/'exp/map-atlas/cache'
raw={json.loads(l)['key']:json.loads(l) for l in (O/'raw.jsonl').open()}
sets=sorted({r['set'] for r in raw.values() if r['src']=='online'})
tasks=[];meta=[];missing=[]
online='--online' in sys.argv
for s in sets if online else ['top-all']+sets:
    f=R/'data/decisions'/s/'games.jsonl'
    if not f.exists():missing.append(s);continue
    # Prefer the latest extraction if a file contains metadata revisions.
    rows={}
    for l in f.open():
        a=json.loads(l);k=str(a['key']) if s=='top-all' else s+':'+str(a['key']);a['key']=k;rows[k]=a
    for k,a in rows.items():
        if k not in raw:continue
        p=f.parent/a['out']
        if not p.exists():missing.append(str(p.relative_to(R)));continue
        tasks.append(f"{k}\t{p}\t{a['rows']}")
        meta.append(dict(a,set=s,layout=raw[k]['layout'],src=raw[k]['src']))
suffix='-online' if online else ''
(O/f'decision-manifest{suffix}.tsv').write_text('\n'.join(tasks)+'\n')
(O/f'decision-meta{suffix}.jsonl').write_text(''.join(json.dumps(a,ensure_ascii=False)+'\n' for a in meta))
print(json.dumps({'games':len(tasks),'sets':dict(collections.Counter(a['set'] for a in meta)),
                  'expectedRows':sum(a['rows'] for a in meta),'missing':missing}))
