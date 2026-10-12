import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/losses/counts']
from count_replays import Geometry
from pathlib import Path
from datetime import datetime
O=Path(__file__).resolve().parent
out=[]
for gid,special in ((1490798,95),(1490799,78),(1490800,185)):
 g=json.loads((O/f'{gid}.json').read_text());w,h=g['width'],g['height'];q=g['queens']['us'];raw=[tuple(map(int,a[1:4])) for l in g['text'].splitlines() if (a:=l.split())[0]=='EDGE'];geo=Geometry(w,h,raw)
 boards=[];labels=[]
 for t in g['qturns'][-3:]:
  cx,cy=t['body'][0]%w,t['body'][0]//w;labels.append(f"r{t['round']} Q({cx},{cy}) L{len(t['body'])}")
  occ={c:('Q' if int(i)==q and n==0 else 'q' if int(i)==q else 'X' if int(i)==special and n==0 else 'F' if g['teams'][i]=='B' and n==0 else 'f' if g['teams'][i]=='B' else 'E' if n==0 else 'e') for i,b in t['frame']['bodies'].items() for n,c in enumerate(b)}
  a=[]
  for dy in range(-3,4):
   top='';mid=''
   for dx in range(-3,4):
    c=((cy+dy)%h)*w+(cx+dx)%w
    top+='+'+('---' if geo.moves[c][0][0]==1 else '@@@' if geo.moves[c][0][0]==2 else '   ')
    mid+=('|' if geo.moves[c][3][0]==1 else '@' if geo.moves[c][3][0]==2 else ' ')+f" {occ.get(c,'o' if c in t['frame']['pearls'] else '.')} "
   top+='+';mid+=('|' if geo.moves[c][1][0]==1 else '@' if geo.moves[c][1][0]==2 else ' ')
   a.extend((top,mid))
  bottom=''
  for dx in range(-3,4):
   c=((cy+3)%h)*w+(cx+dx)%w
   bottom+='+'+('---' if geo.moves[c][2][0]==1 else '@@@' if geo.moves[c][2][0]==2 else '   ')
  a.append(bottom+'+');boards.append(a)
 out.append(f"[M] {gid} {g['map']}; X=#{special}. 각 칸은 7×7 창의 한 타일, Q가 중앙.\n\n| {' | '.join(labels)} |\n|---|---|---|\n| "+' | '.join('<pre>'+ '<br>'.join(b)+'</pre>' for b in boards)+' |\n')
(O/'boards.md').write_text('\n'.join(out))
(O/'DECISIONS.md').write_text(f"# 분석 기록\n\n- {datetime.now().astimezone().isoformat()}: brief 범위의 세 기보만 재집계. 출전 one4(20941), B팀 확인. 최종 길이·머릿수는 replay result와 일치; 독립 o1_scan의 모든 라운드 상태와 일치; ladder_replay anomalies는 세 판 모두 빈 값. 기보 메타 ranked=false로 brief의 ranked 표기와 다름. 새 경기·네트워크·봇 수정 없음. 분석 및 보고 파일만 이 폴더에 기록.\n")
