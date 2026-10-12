maps = ['gx_open_64x16_910902', 'gx_rooms_64x16_911002', 'gx_corridors_64x16_911102', 'gx_islands_64x16_911202',
        'gx_ring_64x16_911302', 'gx_rotation_64x16_911402', 'gx_poor_64x16_911502', 'gx_rich_64x16_911602',
        'gx_open_24x12_910901', 'gx_rooms_24x12_911001', 'gx_islands_24x12_911201', 'gx_rich_24x12_911601']
out = []
for m in maps:
    for side in '01':
        out.append(f'qd_nf {m} 1 {side}')
open('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qdead-opus/jobs3.txt', 'w').write('\n'.join(out) + '\n')
