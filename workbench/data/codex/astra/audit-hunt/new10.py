import json
from concurrent.futures import ProcessPoolExecutor,as_completed
import analyze as a

def main():
 jobs=[]
 for p in a.Path('data/online/smoke/one10-k1-old').glob('game-*.json'):
  j=json.loads(p.read_text());rp=p.with_name(f"M{j['id']}.replay");r=a.load_replay(rp).root();own=int(j['teamAId']!=1119);bot=r.text(1+own)
  if bot=='21200':jobs.append(dict(path=str(rp),meta=j,version='one10',bot=bot,gid=j['id']))
 with ProcessPoolExecutor(max_workers=2) as pool:
  for f in as_completed([pool.submit(a.work,j) for j in jobs]):print(f.result(),flush=True)
if __name__=='__main__':main()
