// Exact decision-time 7x7 crops supplement the required round-start eval/board.js pictures.
'use strict';const {perGame}=require('./ledger');
function crops(R,e){const M=R.match.map,W=M.width,H=M.height,wanted=new Set(Object.values(e.lastDecisions).flat().map(x=>x.r+':'+x.id)),frames=[],wrap=(x,n)=>(x+n)%n;
 function snap(d,r,ctx,when){const h=d.body[0],cells=[];for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++){const x=wrap(h.x+dx,W),y=wrap(h.y+dy,H),k=y*W+x,id=ctx.occ.get(k),o=id===undefined?null:ctx.drag.get(id);cells.push({dx,dy,x,y,id:id??null,team:o?.team??null,head:o?o.body[0].x===x&&o.body[0].y===y:false,len:o?.body.length??0,pearl:ctx.pearls.has(k),drop:ctx.pearls.get(k)>=0,north:M.initialHEdges[y*W+x]|| (y===0?M.initialHEdges[H*W+x]:0),west:M.initialVEdges[y*(W+1)+x]||(x===0?M.initialVEdges[y*(W+1)+W]:0),south:M.initialHEdges[(y+1)*W+x],east:M.initialVEdges[y*(W+1)+x+1]});}frames.push({r,id:d.id,team:d.team,len:d.body.length,head:[h.x,h.y],when,cells});}
 perGame(R,{freePolicy:e.freePolicy,map:e.map,variant:e.layout==='10'?'PD10':e.layout},{turn(d,r,ctx){if(wanted.has(r+':'+d.id))snap(d,r,ctx,'BEFORE');},action(d,ev,r,ctx){if(r===e.end&&e.ids.includes(d.id))snap(d,r,ctx,d.fate?'PRE-DEATH':'AFTER');}});return {game:e.gameId,episode:e.id,frames};
}
module.exports={crops};
