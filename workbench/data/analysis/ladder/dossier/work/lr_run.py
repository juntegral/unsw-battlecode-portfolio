import sys,json,time
sys.dont_write_bytecode=True
from pathlib import Path
from lr_scan import scan
P=Path('data/analysis/ladder/dossier');W=P/'work'
main=json.loads((P/'input-snapshot.json').read_text())['rows']
top=[json.loads(x) for x in (P/'target/per-game-top1.jsonl').open()]
other={r['game']:r for r in top if r['relation']=='them'}
top=[r for r in top if r['relation']=='us']
rows=[]
for r in main:
    r=dict(r,replay=f"data/online/ladder/{r['battle']}/M{r['game']}.replay",source='main')
    rows.append(r)
for r in top:
    r=dict(r,map_key=r['layout_key'],source='top1',queens_at_end=None)
    want=other[r['game']]['final_reconstructed'];mine=r['final_reconstructed']
    r['final']={'us':mine,'them':want}
    rows.append(r)
shard=int(sys.argv[1]); n_shards=int(sys.argv[2]);limit=int(sys.argv[3]) if len(sys.argv)>3 else None
rows=rows[shard::n_shards][:limit];geos={};bad=[]
old={}
for p in W.glob('at_scan-[0-4].jsonl'):
    for x in p.open():
        r=json.loads(x);old[r['game']]=r
with (W/f'lr_events-{shard}.jsonl').open('w') as f:
    for n,r in enumerate(rows):
        try:
            out=scan(r,geos)
            z=out['final'];want=r['final']
            assert [z[0],z[1],z[2],z[4],z[5],z[6]]==[want['us']['alive'],want['us']['longest'],want['us']['total'],want['them']['alive'],want['them']['longest'],want['them']['total']]
            if r['source']=='main':
                o=old[r['game']];assert len(out['hos'])==len(o['hos'])
                for a,b in zip(out['hos'],o['hos']):
                    for k in ('r','ms','mid','vid','cross','L0','Ld','Lv','mq','mtop','dm','dv','mm','mv','vm','vv'):
                        assert a[k]==b[k],(r['game'],k,a[k],b[k])
            out['source']=r['source'];out['chs']=[];out['turns']=[]
            out['hos']=[h for h in out['hos'] if 'qalive' in h]
            f.write(json.dumps(out,separators=(',',':'))+'\n');f.flush()
        except Exception as e:
            bad.append([r['source'],r['game'],repr(e)]);print('ERROR',bad[-1],flush=True)
        if n%20==19:print(shard,n+1,len(rows),len(bad),flush=True)
(W/f'lr_status-{shard}.json').write_text(json.dumps({'games':len(rows),'bad':bad}))
print('DONE',shard,len(rows),bad,flush=True)
