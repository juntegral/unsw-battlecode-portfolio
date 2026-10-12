'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto'),{Transform,Writable}=require('stream'),{pipeline}=require('stream/promises'),OUT=__dirname;
async function run(){
 const r=require('./extract').resource();if(r.memory===null||r.memory<10||r.diskGB<20)throw Error('Resource pause '+JSON.stringify(r));
 const source=path.join(OUT,'episodes.jsonl'),target=source+'.gz',hash=crypto.createHash('sha256');
 await pipeline(fs.createReadStream(source),new Transform({transform(chunk,encoding,cb){hash.update(chunk);cb(null,chunk);}}),zlib.createGzip({level:4}),fs.createWriteStream(target));
 const expected=hash.digest('hex'),ind=crypto.createHash('sha256');let bytes=0;
 await pipeline(fs.createReadStream(target),zlib.createGunzip(),new Writable({write(chunk,encoding,cb){ind.update(chunk);bytes+=chunk.length;cb();}}));
 const actual=ind.digest('hex'),sourceBytes=fs.statSync(source).size;if(actual!==expected||bytes!==sourceBytes)throw Error('Archive mismatch');
 const result={file:'episodes.jsonl.gz',source:'episodes.jsonl',sourceBytes,compressedBytes:fs.statSync(target).size,sha256:expected,decompressedSha256:actual,verified:true};
 fs.writeFileSync(path.join(OUT,'archive.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}run().catch(e=>{console.error(e);process.exitCode=1;});
