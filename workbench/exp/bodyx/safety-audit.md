# BODYX 전후 판면 감사

실제 차례의 몸·진주·지형 이웃은 review.json, 모든 해당 전후 판면은 boards/에 보존했다. 후속 관측이 달라진 on/off는 같은 입력의 인과 비교로 쓰지 않는다.

| 키 | 증가 원시 원인 Δ | 증가 기제 원인 Δ | 조기/새 여왕 |
|---|---|---|---|
| [proxy4_king:big_empty:A:1](boards/on-proxy4_king_big_empty_A_1.txt) | {'O': 10} | {'trap': 10, 'rammed': 2} | False |
| [proxy4_king:big_empty:B:1](boards/on-proxy4_king_big_empty_B_1.txt) | {'O': 6} | {'trap': 7, 'ram': 1, 'sac': 16} | False |
| [proxy4_king:Colosseum:B:1](boards/on-proxy4_king_Colosseum_B_1.txt) | {} | {'ram': 1} | False |
| [proxy4_king:default_small:A:1](boards/on-proxy4_king_default_small_A_1.txt) | {'W': 3} | {'trap': 3} | False |
| [proxy4_king:default_small:B:1](boards/on-proxy4_king_default_small_B_1.txt) | {} | {'rammed': 3} | True |
| [proxy4_king:stronghold:A:1](boards/on-proxy4_king_stronghold_A_1.txt) | {'O': 7, 'W': 11} | {'trap': 18} | False |
| [bot-hunter:big_empty:A:1](boards/on-bot-hunter_big_empty_A_1.txt) | {'H': 5} | {'rammed': 3, 'ram': 2} | True |
| [bot-hunter:Colosseum:A:1](boards/on-bot-hunter_Colosseum_A_1.txt) | {'H': 22, 'W': 11, 'O': 24} | {'ram': 3, 'trap': 26, 'allyHead': 16, 'rammed': 3, 'sac': 32, 'enemyBody': 1} | False |
| [bot-hunter:Colosseum:B:1](boards/on-bot-hunter_Colosseum_B_1.txt) | {'H': 7, 'O': 5} | {'rammed': 5, 'enemyBody': 5, 'ram': 2} | True |
| [bot-hunter:default_small:A:1](boards/on-bot-hunter_default_small_A_1.txt) | {'H': 2} | {'ram': 2, 'sac': 3} | False |
| [bot-hunter:default_small:B:1](boards/on-bot-hunter_default_small_B_1.txt) | {'H': 4} | {'ram': 2, 'rammed': 2} | True |
| [bot-hunter:stronghold:A:1](boards/on-bot-hunter_stronghold_A_1.txt) | {'H': 2} | {'allyHead': 2, 'sac': 18} | False |
| [bot-hunter:stronghold:B:1](boards/on-bot-hunter_stronghold_B_1.txt) | {'H': 2} | {'sac': 3, 'allyHead': 2} | True |
| [proxy4_king:default:A:1](boards/on-proxy4_king_default_A_1.txt) | {'W': 1} | {'ram': 3, 'trap': 2} | False |
| [proxy4_king:default:B:1](boards/on-proxy4_king_default_B_1.txt) | {} | {'ram': 1} | False |
| [proxy4_king:schooltime:A:1](boards/on-proxy4_king_schooltime_A_1.txt) | {'O': 7, 'H': 11, 'W': 3} | {'trap': 10, 'ram': 6, 'rammed': 7, 'sac': 26} | False |
| [proxy4_king:trophy:B:1](boards/on-proxy4_king_trophy_B_1.txt) | {'W': 3} | {'trap': 3, 'ram': 1} | False |
| [proxy4_king:portals:A:1](boards/on-proxy4_king_portals_A_1.txt) | {'W': 6, 'O': 8} | {'trap': 14} | False |
| [proxy4_king:portals:B:1](boards/on-proxy4_king_portals_B_1.txt) | {'H': 2} | {'allyHead': 2} | False |
| [proxy4_king:slithery_fight:A:1](boards/on-proxy4_king_slithery_fight_A_1.txt) | {'O': 1} | {'trap': 1, 'sac': 2} | False |
| [proxy4_king:slithery_fight:B:1](boards/on-proxy4_king_slithery_fight_B_1.txt) | {'O': 13, 'W': 12, 'H': 13} | {'trap': 25, 'rammed': 11, 'ram': 8} | False |
| [proxy4_king:autarky:A:1](boards/on-proxy4_king_autarky_A_1.txt) | {'H': 2, 'O': 1} | {'allyHead': 2} | False |
| [bot-hunter:default:A:1](boards/on-bot-hunter_default_A_1.txt) | {'A': 1} | {'sprintDeath': 1, 'enemyBody': 1} | False |
| [bot-hunter:default:B:1](boards/on-bot-hunter_default_B_1.txt) | {} | {'allyHead': 2, 'sac': 2} | True |
| [bot-hunter:schooltime:A:1](boards/on-bot-hunter_schooltime_A_1.txt) | {'H': 1} | {'rammed': 2, 'ram': 1, 'enemyBody': 2} | True |
| [bot-hunter:schooltime:B:1](boards/on-bot-hunter_schooltime_B_1.txt) | {'W': 14, 'H': 11} | {'trap': 9, 'rammed': 5, 'allyHead': 6} | False |
| [bot-hunter:trophy:A:1](boards/on-bot-hunter_trophy_A_1.txt) | {'H': 1} | {'allyHead': 2, 'ram': 2, 'sac': 1} | False |
| [bot-hunter:trophy:B:1](boards/on-bot-hunter_trophy_B_1.txt) | {} | {'rammed': 1, 'sac': 1} | False |
| [bot-hunter:portals:A:1](boards/on-bot-hunter_portals_A_1.txt) | {'O': 23} | {'trap': 18, 'sac': 8} | False |
| [bot-hunter:portals:B:1](boards/on-bot-hunter_portals_B_1.txt) | {'H': 8, 'O': 11} | {'trap': 8, 'allyHead': 8} | True |
| [bot-hunter:slithery_fight:A:1](boards/on-bot-hunter_slithery_fight_A_1.txt) | {'O': 40, 'W': 39} | {'trap': 77, 'ram': 3} | False |
| [bot-hunter:slithery_fight:B:1](boards/on-bot-hunter_slithery_fight_B_1.txt) | {'O': 10, 'W': 19} | {'trap': 30, 'allyHead': 4} | False |
| [bot-hunter:autarky:A:1](boards/on-bot-hunter_autarky_A_1.txt) | {'W': 30, 'O': 1} | {'trap': 31} | False |
| [bot-hunter:autarky:B:1](boards/on-bot-hunter_autarky_B_1.txt) | {'W': 3, 'H': 1} | {'trap': 2, 'sac': 2, 'rammed': 1} | False |
| [bot-hunter:prisoners_dilemma:B:1](boards/on-bot-hunter_prisoners_dilemma_B_1.txt) | {} | {'sac': 1} | False |
| [proxy4_king:around_unsw:A:1](boards/on-proxy4_king_around_unsw_A_1.txt) | {'W': 65, 'O': 13, 'H': 6} | {'trap': 80, 'ram': 5, 'rammed': 1, 'sac': 4} | False |
| [proxy4_king:around_unsw:B:1](boards/on-proxy4_king_around_unsw_B_1.txt) | {'O': 1} | {} | False |
| [proxy4_king:australia:A:1](boards/on-proxy4_king_australia_A_1.txt) | {'H': 2} | {'rammed': 1, 'ram': 1, 'sac': 1} | False |
| [proxy4_king:australia:B:1](boards/on-proxy4_king_australia_B_1.txt) | {'W': 9, 'O': 5, 'H': 13} | {'trap': 14, 'ram': 8, 'rammed': 5, 'sac': 2} | False |
| [bot-hunter:around_unsw:A:1](boards/on-bot-hunter_around_unsw_A_1.txt) | {} | {'rammed': 2, 'sac': 20} | True |
| [bot-hunter:around_unsw:B:1](boards/on-bot-hunter_around_unsw_B_1.txt) | {'H': 6} | {'rammed': 3, 'ram': 3} | False |
| [bot-hunter:australia:A:1](boards/on-bot-hunter_australia_A_1.txt) | {'W': 13, 'O': 2} | {'trap': 15, 'sac': 11, 'ram': 1} | False |
| [bot-hunter:australia:B:1](boards/on-bot-hunter_australia_B_1.txt) | {'W': 6} | {'sac': 9, 'rammed': 1} | False |
| [bot-hunter:stripes:B:1](boards/on-bot-hunter_stripes_B_1.txt) | {} | {'ram': 2} | False |
| [proxy4_king:gen_L_03:A:1](boards/on-proxy4_king_gen_L_03_A_1.txt) | {'H': 6} | {'rammed': 5, 'ram': 1, 'sac': 4} | True |
| [proxy4_king:gen_X_07:A:1](boards/on-proxy4_king_gen_X_07_A_1.txt) | {'H': 7} | {'ram': 7} | False |
| [proxy4_king:gen_X_07:B:1](boards/on-proxy4_king_gen_X_07_B_1.txt) | {'O': 9} | {'sac': 3} | True |
| [proxy4_king:gen_S_03:A:1](boards/on-proxy4_king_gen_S_03_A_1.txt) | {'W': 2} | {'trap': 2} | False |
| [bot-hunter:gen_L_03:A:1](boards/on-bot-hunter_gen_L_03_A_1.txt) | {'O': 1} | {'sac': 12, 'trap': 1} | False |
| [bot-hunter:gen_L_03:B:1](boards/on-bot-hunter_gen_L_03_B_1.txt) | {'O': 3, 'H': 2} | {'sac': 26, 'trap': 3, 'rammed': 1, 'ram': 1} | True |
| [bot-hunter:gen_X_07:A:1](boards/on-bot-hunter_gen_X_07_A_1.txt) | {'W': 3, 'H': 11} | {'ram': 3, 'rammed': 8, 'sac': 20} | True |
| [bot-hunter:gen_M_07:A:1](boards/on-bot-hunter_gen_M_07_A_1.txt) | {'W': 22, 'O': 6} | {'trap': 28, 'sac': 2} | False |
| [bot-hunter:gen_M_07:B:1](boards/on-bot-hunter_gen_M_07_B_1.txt) | {} | {'ram': 1, 'sac': 1} | False |

| 조기/새 여왕 키 | OFF r/원시/기제 | ON r/원시/기제 |
|---|---|---|
| proxy4_king:default_small:B:1 | 167/H/rammed | 58/H/rammed |
| bot-hunter:big_empty:A:1 | 258/H/rammed | 85/H/rammed |
| bot-hunter:Colosseum:B:1 | 60/H/rammed | 37/H/rammed |
| bot-hunter:default_small:B:1 | 128/S/sac | 123/W/trap |
| bot-hunter:stronghold:B:1 | 생존 | 246/S/trap |
| bot-hunter:default:B:1 | 315/H/rammed | 202/O/trap |
| bot-hunter:schooltime:A:1 | 192/H/rammed | 190/H/rammed |
| bot-hunter:portals:B:1 | 생존 | 253/W/trap |
| bot-hunter:around_unsw:A:1 | 생존 | 281/H/rammed |
| proxy4_king:gen_L_03:A:1 | 생존 | 349/H/rammed |
| proxy4_king:gen_X_07:B:1 | 196/S/sac | 160/H/rammed |
| bot-hunter:gen_L_03:B:1 | 생존 | 421/H/rammed |
| bot-hunter:gen_X_07:A:1 | 127/W/trap | 126/W/trap |

원시 S 전수 확인: ON1574/OFF1543건은 실제 한 걸음 MOVE가 자기 몸에 충돌하는 feed; ON17/OFF25건은 시작 차례 지형·몸 이웃에 빈 출구0인 no-exit. OFF 나머지20건은 다중19, 단일1. 집계에서 제외하지 않았다.

기억 drift122건: 시작 해시121건, 완료 해시104건(겹침), 길이1건. 시작이 맞고 끝만 틀린 Colosseum B #49 r124 WS는 실제 무진주2걸음/끝L2인데 미관측2칸 예측은 L4.

지급 실패: default A/hunter #14 r188 L2 NW; 시작 [775,774], 첫 걸음 포털 도착891에 실제 진주가 없어서 L2, 두 번째 유료 걸음에서 A. 표식은 unseen2/예측L3으로 진주를 과대 추정했다.

완전 입력 C++/oracle drift0은 실제 기억 drift122와 지급 실패1을 상쇄하지 않는다.
