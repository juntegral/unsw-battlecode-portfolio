import sys
sys.dont_write_bytecode=True
import json,re,hashlib
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze_fast as a
OUT=a.OUT

def main():
    rows=[json.loads(l) for l in (OUT/'observations-complete.jsonl').read_text().splitlines()];inv=json.loads((OUT/'inventory.json').read_text());expected={r['path'] for r in inv['rows'] if not r['duplicate_of']}
    assert len(rows)==len({r['path'] for r in rows});assert {r['path'] for r in rows}==expected
    checks={}
    for slug in a.TARGETS:
        source=(OUT/'structure'/('ladder_'+slug+'.map')).read_bytes();target=(OUT/('ladder_'+slug+'.map')).read_bytes();old=source.splitlines(keepends=True);new=target.splitlines(keepends=True)
        assert len(old)==len(new)
        births={int(c) for r in rows if r['slug']==slug for c in r['tile_births']};tiles={};changed=0
        for x,y in zip(old,new):
            if not x.startswith(b'TILE '):assert x==y
            else:
                xmatch=re.fullmatch(rb'(TILE\s+\d+\s+\d+\s+)\d+(\s+)\d+(\r?\n?)',x);ymatch=re.fullmatch(rb'(TILE\s+\d+\s+\d+\s+)\d+(\s+)\d+(\r?\n?)',y)
                assert xmatch and ymatch and xmatch.groups()==ymatch.groups()
                q=y.split();xx,yy,lo,hi=map(int,q[1:]);tiles[xx,yy]=(lo,hi);changed+=x!=y
        w,h,sym,*_=a.layout(source.decode())
        for (x,y),p in tiles.items():
            c=y*w+x;assert bool(p[1])==(c in births);assert p==(0,0) or 1<=p[0]<=p[1]
            o=a.orbit(c,w,h,sym);assert p==tiles[o%w,o//w]
        checks[slug]=dict(original_sha256=hashlib.sha256(source).hexdigest(),corrected_sha256=hashlib.sha256(target).hexdigest(),changed_tile_lines=changed,enabled_tiles=len(births),non_TILE_and_all_other_bytes_identical=True,classes={'%d %d'%p:n for p,n in sorted(Counter(tiles.values()).items())})
    (OUT/'validation.json').write_text(json.dumps(dict(snapshot=inv.get('snapshot_local'),examined_replays=inv.get('examined_files'),unique_games=len(rows),maps=checks),indent=2)+'\n')
    print('three maps: only TILE interval numbers changed; all enabled tiles observed; symmetry valid; all snapshot games included')

if __name__=='__main__':main()
