const fs=require("fs");
const FRAC=+process.argv[2]||2;
const src=fs.readFileSync(process.argv[3]||"exp/base-px6/bot/mapdb.hpp","utf8");
const re=/\{"([^"]+)", (\d+), (\d+), (-?\d+),\n\s+"([0-9a-f]+)",\n\s+"([0-9a-f]+)",\n\s+(\d+), P(\d+), (\d+), S(\d+),\n\s+"([^"]*)", (\d+), D(\d+)\}/g;let m;const db=[];
while((m=re.exec(src))){db.push({name:m[1],W:+m[2],H:+m[3],hk:m[5],vk:m[6],np:+m[7],pi:+m[8],di:+m[13]});}
const arr={};const are=/static const int ([PSD]\d+)\[\] = \{([^}]*)\}/g;while((m=are.exec(src)))arr[m[1]]=m[2].split(",").map(Number);
const bit=(h,i)=>(parseInt(h[i>>2],16)>>(i&3))&1;const DX=[0,1,0,-1],DY=[-1,0,1,0];
for(const d of db){const W=d.W,H=d.H,N=W*H;const stepT=(t,k)=>((((t/W|0)+DY[k])%H+H)%H)*W+(((t%W)+DX[k])%W+W)%W;
 const P=arr["P"+d.pi];const isP=(t,s)=>{for(let i=0;i<d.np;i++)for(let e=0;e<2;e++){const q=P.slice(i*6+e*3,i*6+e*3+3);if(q[0]===t%W&&q[1]===(t/W|0)&&q[2]===s)return true;}return false;};
 const md=new Array(N*4).fill(-1);
 for(let t=0;t<N;t++)for(const side of [0,3]){const s1=side===0?0:1;if(bit(side===0?d.hk:d.vk,t)||isP(t,s1))continue;const u=stepT(t,side);md[t*4+side]=u;md[u*4+((side+2)&3)]=t;}
 for(let i=0;i<d.np;i++)for(let e=0;e<2;e++){const a=P.slice(i*6+e*3,i*6+e*3+3),b=P.slice(i*6+(1-e)*3,i*6+(1-e)*3+3);const ta=a[1]*W+a[0],tb=b[1]*W+b[0];if(a[2]===0){md[ta*4]=stepT(tb,0);md[stepT(ta,0)*4+2]=tb;}else{md[ta*4+3]=stepT(tb,3);md[stepT(ta,3)*4+1]=tb;}}
 const bfs=(src,maxd)=>{const dd=new Array(N).fill(-1);const q=[];for(const t of src)if(dd[t]<0){dd[t]=0;q.push(t);}for(let i=0;i<q.length;i++){const t=q[i];if(dd[t]>=maxd)continue;for(let k=0;k<4;k++){const u=md[t*4+k];if(u<0||dd[u]>=0)continue;dd[u]=dd[t]+1;q.push(u);}}return dd;};
 const D=arr["D"+d.di];const out=[];
 for(const me of [0,1]){const ours=[],theirs=[];for(let i=0;i<D.length/3;i++){const t=D[i*3+2]*W+D[i*3+1];(D[i*3]===me?ours:theirs).push(t);}
  const dA=bfs(ours,1e9),dB=bfs(theirs,1e9);let best=-1,bs=-1;
  for(let pass=0;pass<2&&best<0;pass++)for(let t=0;t<N;t++){if(dA[t]<0)continue;if(dB[t]>=0&&(pass===0?dA[t]*FRAC>dB[t]:dA[t]>=dB[t]))continue;const o=bfs([t],5).filter(x=>x>=0).length;const sc=o*100000-dA[t];if(sc>bs){bs=sc;best=t;}}
  out.push((me?"B":"A")+" Z=("+best%W+","+(best/W|0)+") open "+Math.floor(bs/100000)+" dOurs "+dA[best]+" dTheirs "+dB[best]);}
 console.log(d.name.padEnd(18),out.join(" | "));}
