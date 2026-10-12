// Count final indicators and actual raw actions, independently of movement simulation.
'use strict';
function indicators(R,us){const team=new Map(R.match.map.initialDragons.map(d=>[d.id,d.team])),out={indSelected:0,indSelectedTrade:0};if(!us)return out;let cur=-1,last='',selected=false,victimTeam=null;
 for(const e of R.events){if(e.type==='dragonSplit')team.set(e.childId,e.team);else if(e.type==='turnStart'){cur=e.id;last='';selected=false;victimTeam=null;}else if(e.type==='dragonIndicator'&&e.id===cur)last=e.text||'';else if(e.type==='dragonAction'&&e.id===cur){selected=team.get(cur)===us&&/\bTRADE\b/.test(last)&&e.action?.kind==='move'&&e.action.steps.length>=3;if(selected)out.indSelected++;}else if(e.type==='dragonDeath'&&e.reason==='H'){if(e.id!==cur)victimTeam=team.get(e.id);else if(selected&&victimTeam&&victimTeam!==team.get(cur))out.indSelectedTrade++;}}
 return out;
}
module.exports={indicators};
