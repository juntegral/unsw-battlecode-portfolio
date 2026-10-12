#!/usr/bin/env python3
"""Validate completeness; write the English 20-line completion marker LAST."""
import json,collections,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review';E=R/'exp/outcome-review'
report=R/'research/observations/outcome-review.md'
A=json.load(open(C/'analysis.json'));M=json.load(open(C/'manifest.json'));K=json.load(open(C/'recount-checks.json'))
selection=json.load(open(C/'selection.json'));deep=[json.loads(l) for l in open(C/'deep.jsonl') if l.strip()]
assert K['mismatchCount']==0
assert len(deep)==len(selection['games'])
assert all(not any(z['chk'].values()) for z in deep)
assert report.is_file() and report.stat().st_size>10000
assert sum(z['n'] for z in M['sets'])==M['n']==A['population']['all']['n']
assert all(z['n']==70 for z in M['sets'])
for k,z in A['population'].items():assert z['W']+z['D']+z['L']==z['n']
# A newly arriving requested W12 must be included before the completion marker.
if (R/'data/online/cand-stack11-online/index.json').exists() and not any(z['set']=='cand-stack11-online' for z in M['sets']):
    raise SystemExit('W12 has arrived after freeze; extend the census before SUMMARY.txt')
validation={'games':M['n'],'sets':len(M['sets']),'independentMismatches':K['mismatchCount'],'selected':len(deep),'reportBytes':report.stat().st_size,'reportSha256':hashlib.sha256(report.read_bytes()).hexdigest(),'markerLines':20}
with open(C/'validation.json','x') as f:json.dump(validation,f,indent=2);f.write('\n')
p=A['population'];t=p['top6'];v=p['dev'];classes=A['classes'];pw=A['power'];tr=A['trend']['top6-logistic']
ors=(tr.get('coefficients')or[{}])[0]
num=lambda x:'NA' if x is None else f'{x:.3f}'
base=[z for z in pw['table'] if z['power']==.8 and z['noise']=='measured-with-floor']
last=A['waveNames'][-1]
lines=[
 'Outcome review of team 583 against the seven fixed wave opponents.',
 f'Census: {M["n"]} unique games in {len(M["sets"])} complete sets; no sampling.',
 f'Current waves: {p["waves"]["n"]} games; history: {p["history"]["n"]} games.',
 'All observations use our A seat; seat effects are unidentified.',
 f'Top-six current outcomes: {t["W"]} wins, {t["D"]} draws, {t["L"]} losses in {t["n"]}.',
 f'Top-six win rate: {t["W"]/t["n"]:.3%}; Wilson 95% CI {t["winCI"][0]:.3%} to {t["winCI"][1]:.3%}.',
 f'DEV 545: {v["W"]} wins, {v["D"]} draws, {v["L"]} losses in {v["n"]}.',
 f'Top-six eliminations: {t["eliminated"]}/{t["n"]}; final longest means {t["ownFinal"]["mean"]:.2f} versus {t["enemyFinal"]["mean"]:.2f}.',
 f'Wins anatomized: {p["all"]["W"]} total, including {p["waves"]["W"]} current-wave wins.',
 'Win classes: '+', '.join(f'{k[4:]}={z["n"]}' for k,z in classes.items() if k.startswith('win:'))+'.',
 'Near misses: '+str(sum(z['n'] for k,z in classes.items() if k.startswith('near:')))+' losses with final king ratio at least 0.8.',
 'Lead-loss classes: '+', '.join(f'{k[5:]}={z["n"]}' for k,z in classes.items() if k.startswith('lead:'))+'.',
 f'Map/opponent-adjusted top-six trend OR per wave: {num(ors.get("OR"))}; model convergence {tr.get("converged")}.',
 f'Replicate dispersion: {pw["dispersion"]:.3f}; residual degrees of freedom {pw["residualDF"]}; binomial floor retained.',
 '80% power, games per independent arm for +3/+5/+10 wins per 60: '+', '.join(str(z['gamesPerArm']) for z in base)+'.',
 f'Latest observed wave: {last}; absent requested sets: '+', '.join(z['set'] for z in M['absent'])+'.',
 f'Independent raw-replay recount: {M["n"]} games, {K["mismatchCount"]} mismatches; both values reported.',
 f'Frozen selection deep-read: {len(deep)} replays, with round and dragon pointers.',
 'Associations are not causal effects; final longest and elimination are outcome-defining.',
 'Report: research/observations/outcome-review.md; SUMMARY.txt is the completion marker.'
]
assert len(lines)==20 and all('\n' not in l for l in lines)
with open(E/'SUMMARY.txt','x') as f:f.write('\n'.join(lines)+'\n')
print('Completed:',validation)
