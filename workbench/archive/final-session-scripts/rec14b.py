"""Record the weak13-opus final report and the local portal check."""
import time
R = '~/01. Project/개인 프로젝트/unsw-swarm/'
t = time.strftime('%H:%M')
open(R + 'docs/SESSION-STATE.md', 'a').write(f'''- 10:27 **weak13-opus 최종 보고**(폴더 `data/codex/astra/weak13-opus/`: ledger.txt, queen-boards.txt, rammed-battles.txt, look-1513120-d3.txt; 종료시킴). 진 6판: 포털 규칙 버그 2판(Trauma 1513120, Queen Of Spades 1513119) / 상대 퀸이 죽은 뒤 우리 퀸이 2~4 길이로 받혀 죽음 3판(Stripes 1513121, Slithery Fight 1513123, Islands 1508963) / 퀸이 28 길이에서 옆에 붙은 2짜리 머리를 안 떼고 분열해 2만 남기고 죽음 1판(Slithery Fight 1508962). 새로 나온 것 [C]: BIG_ESCAPE의 long_escape(4662-4664)는 threat_at(chosen)이 0이면 그냥 나가는데, map_threats는 적 크기를 **보이는 마디 수**로 셈(4311; 4마디 바닥은 퀸만) → 6짜리 적이 1마디만 보이면 50짜리 우리 용이 안전하다고 읽음. 두 전투에서 8 이상 우리 용이 받힌 33번 중 공격자가 다 보인 건 3, 일부 19, 안 보임 11. 동결이라 손대지 않음(열린 약점으로 기록).
- **{t} 로컬 확인: one13(mDone13) 대 one14(mNps), 상대 옛 main, ladder_portals_1·ladder_australia_1 × 시드 2 × 양 진영 8판**(`solo/runs/pc_*`). r100 자연 진주 one13 → one14: Australia 48/39/23/33 → 88/79/92/113, Portals 51/48/42/50 → 115/124/103/122. 8판 모두 2배 이상. 승 4/8 → 7/8. 버그 수정 효과는 로컬에서도 확인됨.
''')
print(t)
