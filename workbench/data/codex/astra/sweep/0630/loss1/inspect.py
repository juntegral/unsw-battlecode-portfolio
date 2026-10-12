import json
from pathlib import Path
from collections import deque
from analyze import Geo, OUT, lr

def board(g,tr,attacker):
    w,h=g['w'],g['h'];hx,hy=tr['body'][0]
    edges=lr.canonical_edges(w,h,g['edges'])
    grid=[[' ']*15 for _ in range(15)]
    occ={tuple(c):(int(i),k) for i,b in tr['state'].items() for k,c in enumerate(b)}
    pearls={tuple(c) for c in tr['pearls']}
    for dy in range(-3,4):
        for dx in range(-3,4):
            x,y=(hx+dx)%w,(hy+dy)%h;r,c=2*(dy+3)+1,2*(dx+3)+1
            v='*' if (x,y) in pearls else '.'
            if (x,y) in occ:
                i,k=occ[x,y]
                v=('Qq' if i==g['queens'][0] else 'Xx' if i==attacker else 'Aa' if g['teams'][str(i)]==0 else 'Ee')[bool(k)]
            grid[r][c]=v
            for d,(rr,cc) in enumerate(((-1,0),(0,1),(1,0),(0,-1))):
                kind=edges.get(lr.edge_id(w,h,x,y,d),(0,-1))[0]
                if kind:grid[r+rr][c+cc]='P' if kind==2 else ('-' if d%2==0 else '|')
    return [''.join(row) for row in grid]

def main():
    out=[]
    for gid in (1496845,1496846,1496847):
        g=json.loads((OUT/f'{gid}.json').read_text());q=g['queens'][0]
        death=next(d for d in g['qdeaths'] if d['id']==q);attacker=death['actor']
        geo=Geo(g['w'],g['h'],g['edges']);w=g['w']
        qt=[tr for tr in g['qturns'] if tr['id']==q][-3:]
        print('\n',gid)
        boards=[board(g,tr,attacker) for tr in qt]
        print('     '+(' '*15).join(str(tr['r']) for tr in qt))
        for rows in zip(*boards):print('   '.join(rows))
        for tr in qt:
            hd=tr['body'][0];cell=hd[1]*w+hd[0]
            occ={c[1]*w+c[0]:(i,k) for i,b in tr['state'].items() for k,c in enumerate(b)}
            sides=[]
            for d,n in enumerate(geo.nxt[cell]):
                sides.append(('NESW'[d],(n%w,n//w) if n>=0 else None,occ.get(n)))
            print(tr['r'],sides)
        out.append('| '+str(gid)+' | '+' | '.join('r'+str(tr['r'])+' '+str(tr['body'][0]) for tr in qt)+' |')
        out.append('|---|---|---|---|')
        out.append('| [M] | '+' | '.join('<code>'+'<br>'.join(row.replace(' ','&nbsp;').replace('|','&#124;') for row in bd)+'</code>' for bd in boards)+' |')
        out.append('')
    (OUT/'boards.md').write_text('\n'.join(out))

if __name__=='__main__':main()
