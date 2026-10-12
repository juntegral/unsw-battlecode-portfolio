"""Read-only source catalogue and per-map mechanism report extraction."""
import pathlib, re, json, hashlib, collections
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'exp/map-atlas/cache'
MAPS=['Autarky','Default','Devil','Portals','Prisoners Dilemma','Queen Of Spades','Schooltime','Slithery Fight','Trauma','Trophy']
def main():
    sources=[]; mechanisms=[]; tables=[]; digest=['# Inherited source digest (offline)\n']
    files=list((ROOT/'legacy/research/observations').glob('*.md'))
    files+=list((ROOT/'legacy/research/experiments').glob('cand-*.md'))
    files+=list((ROOT/'legacy/research/experiments').glob('mech-*.md'))
    files+=list((ROOT/'legacy/research/experiments').glob('triage-cand-stack*.md'))
    files+=list((ROOT/'legacy/research/external').rglob('*.md'))
    files+=[ROOT/'legacy/research/experiments/verification-2026-09-30.md']
    files += [ROOT/'data/decisions'/f for f in ['scale.md','scale-20260930.md','hypotheses.md','hypotheses-stack.md','hypotheses-20260930.md','rules.md','report.md']]
    files += [ROOT/f for f in ['CLAUDE.md','ENGINE.md','EVAL.md','DECISIONS.md','research/KNOWLEDGE.md','research/CHECKPOINT-2026-10-01.md']]
    files+=list((ROOT/'rules').glob('*.md'))
    for p in sorted(set(files)):
        if not p.exists(): continue
        txt=p.read_text(); rel=str(p.relative_to(ROOT));lines=txt.splitlines()
        sources.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(txt.encode()).hexdigest(),'headings':[l for l in lines if l.startswith('#')]})
        digest+=['\n## '+rel+'\n']
        heading=''; section=[]
        for i,l in enumerate(lines):
            if l.startswith('#'):heading=l;section=[]
            if l.startswith('- 지도별:'):
                for part in l.removeprefix('- 지도별:').split(' · '):
                    m=re.match(r'(.+?)\s+(\d+)회\s+(\d+%|–)',part.strip())
                    if m: mechanisms.append({'source':rel,'line':i+1,'section':heading,'map':m[1],'n':int(m[2]),'rate':None if m[3]=='–' else int(m[3][:-1])/100})
            if l.startswith('|') and any(m in l for m in MAPS):
                tables.append({'source':rel,'line':i+1,'section':heading,'text':l})
            if (l.startswith('#') or l.startswith('- [사실]') or l.startswith('- [해석]') or l.startswith('- [추정]') or l.startswith('**판정') or l.startswith('|') and any(m in l for m in MAPS)):
                digest.append(l)
    (OUT/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
    (OUT/'mechanism-reports.json').write_text(json.dumps(mechanisms,ensure_ascii=False,indent=2))
    (OUT/'inherited-tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2))
    (OUT/'source-digest.md').write_text('\n'.join(digest)+'\n')
    local=[]; names={m.lower().replace(' ','_'):m for m in MAPS}
    for d in sorted((ROOT/'legacy/exp').glob('stack12*')):
        f=d/'rows.jsonl'
        if not f.exists(): continue
        for l in f.read_text().splitlines():
            r=json.loads(l); opp,mp,side,seed=r['key'].split(':');rp=d/'games'/f'{opp}_{mp}_{side}_{seed}'/'game.replay'
            if not rp.exists():continue
            local.append({'key':d.name+':'+r['key'],'src':'local','set':d.name,'map':names[re.sub(r'_(b|10)$','',mp)],'us':side,'oppId':None,'file':str(rp),'pfOn':not d.name.startswith('stack12off'),'seed':seed,'localMap':mp})
    (OUT/'local-tasks.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in local))
    print(json.dumps({'sources':len(sources),'map-mechanism-rows':len(mechanisms),'inherited-map-tables':len(tables),'local-pf-replays':len(local),'local-sets':dict(collections.Counter(x['set'] for x in local))}))
if __name__=='__main__':main()
