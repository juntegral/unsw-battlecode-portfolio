"""The final card only rejects a neck cage; other own-body traps stay hypotheses."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import scan

if __name__=='__main__':
    games={g['gid']:g for g in map(json.loads,(scan.OUT/'games.jsonl').read_text().splitlines())}
    rows=list(map(json.loads,(scan.OUT/'audit.jsonl').read_text().splitlines()))
    for a in rows:
        g=games[a['gid']];geo=scan.Geo(scan.lr.agg.sb.load_replay(Path(g['path'])).root().text(0));keep=set()
        for x in a['records']:
            src=tuple(x['src']);dest=tuple(x['dest'])
            x['neck_only']=all(geo.kind(dest,d)==1 or geo.dest(dest,d)==src for d in range(4))
            x['narrow_reject']=x['neck_only'] and (x['queen'] or x['length_after']<4)
            if x['narrow_reject']:keep.add(x['event'])
        for d in a['links']:d['narrow_reject']=d['entry_event'] in keep
    (scan.OUT/'audit-narrow.jsonl').write_text(''.join(json.dumps(a,separators=(',',':'))+'\n' for a in rows))
