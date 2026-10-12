'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..');
const {makeLoader,viewerSource}=require('../../tools/top_features');
const ML=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource());
const t=JSON.parse(fs.readFileSync(path.join(__dirname,'tables.json'),'utf8'));
const all=t.games;
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'board-selection.json'),'utf8'));
const out=path.join(__dirname,'boards');fs.mkdirSync(out,{recursive:true});
const crcTable=Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
const crc=b=>{let c=0xffffffff;for(const v of b)c=crcTable[(c^v)&255]^(c>>>8);return(c^0xffffffff)>>>0;};
function chunk(k,b){const n=Buffer.alloc(4);n.writeUInt32BE(b.length);const d=Buffer.concat([Buffer.from(k),b]),c=Buffer.alloc(4);c.writeUInt32BE(crc(d));return Buffer.concat([n,d,c]);}
function png(w,h,pixels){const ih=Buffer.alloc(13);ih.writeUInt32BE(w);ih.writeUInt32BE(h,4);ih[8]=8;ih[9]=2;
  const scan=Buffer.alloc(h*(w*3+1));for(let y=0;y<h;y++)pixels.copy(scan,y*(w*3+1)+1,y*w*3,(y+1)*w*3);
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',ih),chunk('IDAT',zlib.deflateSync(scan)),chunk('IEND',Buffer.alloc(0))]);}
const digits=['111101101101111','010110010010111','111001111100111','111001111001111','101101111001001','111100111001111','111100111101111','111001001001001','111101111101111','111101111001111'];
const manifest=[];
for(const c of cfg){
  const g=all[c.dir].find(g=>g.key===c.key);if(!g)throw Error(c.key);
  const R=load(path.join(ROOT,g.file)),snaps=[];let seen=-1;
  ML.perGame(R,{map:g.map,variant:'?',rules:'123'},{turn(d,r,ctx){if(!c.rounds.includes(r)||seen===r)return;seen=r;
    snaps.push({r,W:ctx.W,H:ctx.H,drag:[...ctx.drag.values()].map(d=>({id:d.id,team:d.team,body:d.body.map(x=>({...x}))})),pearls:[...ctx.pearls],
      edges:R.match.map,center:c.center});}});
  const rad=c.radius||5,S=32,n=rad*2+1,pw=n*S+30,ph=n*S+40,w=pw*snaps.length,h=ph;
  const buf=Buffer.alloc(w*h*3,255),svg=[];
  const rect=(x,y,ww,hh,col)=>{for(let yy=Math.max(0,y);yy<Math.min(h,y+hh);yy++)for(let xx=Math.max(0,x);xx<Math.min(w,x+ww);xx++)for(let k=0;k<3;k++)buf[(yy*w+xx)*3+k]=col[k];};
  const color={queen:[147,51,234],ally:[37,99,235],enemy:[220,38,38],bodyQ:[216,180,254],bodyA:[147,197,253],bodyE:[252,165,165],drop:[245,158,11],natural:[22,163,74],wall:[17,24,39],grid:[222,226,233]};
  const label=(s,x,y,col,scale=2)=>{for(const ch of String(s)){const pat=digits[+ch];if(pat)for(let yy=0;yy<5;yy++)for(let xx=0;xx<3;xx++)if(pat[yy*3+xx]==='1')rect(x+xx*scale,y+yy*scale,scale,scale,col);x+=4*scale;}};
  for(let i=0;i<snaps.length;i++){
    const s=snaps[i],ox=i*pw+15,oy=25,wx=x=>(x%s.W+s.W)%s.W,wy=y=>(y%s.H+s.H)%s.H;
    label(s.r,ox,5,color.wall,2);
    const bodies=new Map();for(const d of s.drag)d.body.forEach((b,j)=>bodies.set(b.y*s.W+b.x,{d,j}));
    const pearls=new Map(s.pearls),M=s.edges;
    svg.push(`<text x="${ox}" y="18" font-family="monospace">r${s.r}</text>`);
    for(let yy=0;yy<n;yy++)for(let xx=0;xx<n;xx++){
      const x=wx(c.center[0]+xx-rad),y=wy(c.center[1]+yy-rad),px=ox+xx*S,py=oy+yy*S;
      rect(px,py,S,1,color.grid);rect(px,py,1,S,color.grid);
      svg.push(`<rect x="${px}" y="${py}" width="${S}" height="${S}" fill="white" stroke="#dde2e9"/>`);
      const b=bodies.get(y*s.W+x);
      if(b){const queen=b.d.id===g.Q,enemy=b.d.team!==g.side,col=b.j===0?color[queen?'queen':enemy?'enemy':'ally']:color[queen?'bodyQ':enemy?'bodyE':'bodyA'];
        rect(px+4,py+4,S-8,S-8,col);svg.push(`<rect x="${px+4}" y="${py+4}" width="${S-8}" height="${S-8}" fill="rgb(${col})"/>`);
        if(b.j===0){label(b.d.id,px+6,py+11,[255,255,255],1);svg.push(`<text x="${px+7}" y="${py+22}" fill="white" font-size="11" font-family="monospace">${b.d.id}</text>`);}}
      else if(pearls.has(y*s.W+x)){const col=color[pearls.get(y*s.W+x)>=0?'drop':'natural'];rect(px+13,py+13,6,6,col);svg.push(`<circle cx="${px+16}" cy="${py+16}" r="4" fill="rgb(${col})"/>`);}
      const portalEnds=new Set((M.portals||[]).flatMap(pair=>pair.map(p=>p.side==='S'?`${p.x},${wy(p.y+1)},N`:p.side==='E'?`${wx(p.x+1)},${p.y},W`:`${p.x},${p.y},${p.side}`)));
      const isPortal=e=>portalEnds.has(e==='N'?`${x},${y},N`:e==='S'?`${x},${wy(y+1)},N`:e==='W'?`${x},${y},W`:`${wx(x+1)},${y},W`);
      const hk=ey=>M.initialHEdges[wy(ey)*s.W+x]===1||(wy(ey)===0&&M.initialHEdges[s.H*s.W+x]===1);
      const vk=ex=>M.initialVEdges[y*(s.W+1)+wx(ex)]===1||(wx(ex)===0&&M.initialVEdges[y*(s.W+1)+s.W]===1);
      for(const[e,wall]of Object.entries({N:hk(y),S:hk(y+1),W:vk(x),E:vk(x+1)}))if(wall||isPortal(e)){const horizontal=e==='N'||e==='S';const a=px+(e==='E'?S-2:0),b=py+(e==='S'?S-2:0),col=isPortal(e)?[6,182,212]:color.wall;rect(a,b,horizontal?S:3,horizontal?3:S,col);svg.push(`<rect x="${a}" y="${b}" width="${horizontal?S:3}" height="${horizontal?3:S}" fill="rgb(${col})"/>`);}
    }
  }
  const base=path.join(out,c.name);fs.writeFileSync(base+'.png',png(w,h,buf));
  fs.writeFileSync(base+'.svg',`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${svg.join('')}</svg>\n`);
  fs.writeFileSync(base+'.json',JSON.stringify({selection:c,game:{key:g.key,file:g.file,Q:g.Q,death:g.qDeath},snapshots:snaps},null,2)+'\n');
  const ascii=cp.execFileSync(process.execPath,[path.join(ROOT,'eval/board.js'),path.join(ROOT,g.file),g.map,'a',g.side,c.rounds.join(',')],{cwd:ROOT,env:{...process.env,UNSW_RULES:'123'},maxBuffer:2**22});
  fs.writeFileSync(base+'.txt',ascii);manifest.push({name:c.name,file:g.file,key:g.key,Q:g.Q,rounds:c.rounds,center:c.center,actualSnapshots:snaps.map(s=>s.r),png:'exp/q-analysis/boards/'+c.name+'.png'});
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(manifest);
