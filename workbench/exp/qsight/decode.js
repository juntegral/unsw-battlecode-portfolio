'use strict';
const WHITEN=0x9E3779B97F4A7C15n;
function decode(value,round,team,W,H){
 const v=BigInt(value)^WHITEN, get=(s,m)=>Number((v>>BigInt(s))&BigInt(m));
 if(get(58,63)!==0x21||get(8,1))return null;
 let crc=0x93;
 for(let shift=8;shift<64;shift+=8){crc^=get(shift,255);for(let b=0;b<8;b++)crc=((crc<<1)^((crc&128)?7:0))&255;}
 const sender=get(47,2047),enemy=get(36,2047),rnd=get(29,127),x=get(23,63),y=get(17,63),len=get(10,127),tm=get(9,1),age=((round&127)-rnd)&127;
 if(crc!==get(0,255)||tm!==+(team==='B')||sender<=1||sender===enemy||x>=W||y>=H||len<2||age>3||round-age<0)return null;
 return {sender,enemy,round:round-age,t:y*W+x,len};
}
module.exports={decode};
