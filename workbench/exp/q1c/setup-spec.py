from pathlib import Path
import json
lanes=[]
sets=[('bundled','maps/bundled',['arena','big_empty','Colosseum','default_small','stronghold']),('online','maps/online-20260927',['trauma']),('sprint','maps/sprint',['australia']),('generated','maps/generated',['gen_M_07','gen_L_03']),('flip','exp/v16/q1/maps-flip',['trauma_flip','australia_flip'])]
for variant in ['off','b','c','on']:
 for group,maps,only in sets:
  lanes.append(dict(name=f'{variant}-{group}',bot=f'exp/q1c/bot-{variant}',out=f'exp/q1c/{variant}',maps=maps,only=only,seeds=[1],opps=['proxy4_king','exp/q2/bot-hunter'],sides=['A','B'],cpu=True))
for variant,bot in [('id-off','exp/q1c/bot-off'),('id-base','versions/v1.8/bot')]:
 for group,maps,only in [('online','maps/online-20260927',['trophy']),('sprint','maps/sprint',['around_unsw']),('generated','maps/generated',['gen_M_07'])]:
  lanes.append(dict(name=f'{variant}-{group}',bot=bot,out=f'exp/q1c/{variant}',maps=maps,only=only,seeds=[1],opps=['proxy4_king'],sides=['A','B'],cpu=True))
for maps,only in [('maps/bundled',['big_empty','stronghold']),('maps/generated',['gen_M_07','gen_L_03'])]:
 lanes.append(dict(name='self-'+Path(maps).name,bot='exp/q1c/bot-on',out='exp/q1c/self',maps=maps,only=only,seeds=[1],opps=['versions/v1.8/bot'],sides=['A','B'],cpu=True))
Path('exp/q1c/spec.json').write_text(json.dumps(lanes,indent=2)+'\n')
s=Path('exp/v16/q1/runq.js').read_text().replace("path.resolve(__dirname, '..', '..', '..')","path.resolve(__dirname, '..', '..')")
s=s.replace('node exp/v16/q1/runq.js','node exp/q1c/runq.js')
Path('exp/q1c/runq.js').write_text(s)
