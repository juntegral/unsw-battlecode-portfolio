"""Independent event counts and validation of saved avoidance witnesses."""
import sys
sys.dont_write_bytecode=True
import json
from collections import Counter
from pathlib import Path
import analyze as a
sys.path.insert(0,str(a.ROOT/'data/analysis/ladder/dossier/work'))
import o1_scan

def main():
    result=[]
    for p in sorted(a.OUT.glob('g*.json')):
        game=json.loads(p.read_text());assert game['schema']==a.SCHEMA
        path=a.ROOT/game['path'];meta=json.loads(path.with_name(f'game-{game["gid"]}.json').read_text())
        check=o1_scan.scan(game['label'],path,meta)
        expected=Counter((d[0],'us' if d[1]==0 else 'them',d[2]) for d in check['deaths'] if d[4]=='rammed' and not d[6] and d[0]<=200)
        actual=Counter((r['round'],r['side'],r['victim_impact_length']) for r in game['rows'])
        assert expected==actual,(game['gid'],expected-actual,actual-expected)
        root=a.lr.replay.load(path).root();g=a.Geo(root.text(0))
        expected_bot='20910' if game['label']=='one3-w1' else '20980'
        assert root.text(1 if meta['teamAId']==1119 else 2)==expected_bot
        checked=0;strong=0
        for row in game['rows']:
            at=row['attacking_turn'];assert at['id']==row['attacker'] and at['kind']==0
            if row['last_event'] is None: continue
            turn=row['turn'];assert row['last_round'] in (row['round'],row['round']-1)
            assert row['round']-row['last_round']==int(row['attacker']<row['victim'])
            if row['status']=='not seen': continue
            bs={i:tuple(tuple(c) for c in b) for i,s,b in row['start_bodies']}
            teams={i:s for i,s,b in row['start_bodies']};v=row['victim'];enemy=row['attacker']
            pearls=set(tuple(c) for c in row['start_pearls'])
            row['terrain_safe_all']=[]
            row['view_certified_all']=[]
            for op in row['safe']:
                body=bs[v];ps=set(pearls);ate=0
                others={c for i,b in bs.items() if i!=v for c in b}
                assert 1<=len(op['path'])<=(len(body)+3)//4
                for d in op['path']:
                    n=g.moves[body[0]][d];assert n is not None and n not in body and n not in others
                    eating=n in ps;body=(n,)+body if eating else (n,)+body[:-1];ps.discard(n);ate+=eating
                assert list(body)==[tuple(c) for c in op['body']] and ate==op['ate']
                assert a.good_room(g,body,others)
                assert not a.hits(g,bs,enemy,v,body,ps)
                checked+=1
            for op in row['safe_all']:
                target=tuple(op['body'][0]);ds=g.distances_to(target)
                threatening=[i for i,b in bs.items() if teams[i]!=row['side'] and g.visible(b[0],bs[v][0]) and len(b)>=row['victim_length']]
                upper_safe=all(ds.get(bs[i][0],99999)>(len(bs[i])+3)//4+len(bs[i])-2 for i in threatening)
                if upper_safe:
                    row['terrain_safe_all'].append(op);strong+=1
                whole=all(all(g.visible(c,bs[v][0]) for c in bs[i]) for i in bs if teams[i]!=row['side'] and g.visible(bs[i][0],bs[v][0]))
                if upper_safe and whole and op['known_room'] and op['path_seen']:
                    row['view_certified_all'].append(op)
            row['card_strong']=bool(row.get('card_geometry') and row['terrain_safe_all'] and turn['kind']==0)
            row['card_observable']=bool(row.get('card_geometry') and row['view_certified_all'] and turn['kind']==0)
            row['attacker_pearl_extended']=at['used']+1>(at['length']+3)//4+at['length']-2
        (a.OUT/f'verified-{game["gid"]}.json').write_text(json.dumps(game,ensure_ascii=False,separators=(',',':')))
        result.append(dict(gid=game['gid'],rows=len(game['rows']),witnesses=checked,terrain_witnesses=strong,independent_death_counts=True,id_order=True,bot_id=True))
        print('verified',game['gid'],len(game['rows']),checked,flush=True)
    (a.OUT/'verification.json').write_text(json.dumps(result,indent=2))

if __name__=='__main__':main()
