from pathlib import Path
p=Path('exp/map-atlas/extract.js').read_text();p=p[:p.index("if(require.main===module&&process.argv[2]==='worker')")]
p=p.replace("OUT=path.join(__dirname,'cache')", "OUT=path.join(__dirname,'geometry')")
p=p.replace("module.exports", "module.exports")
p=p.replace("const fs=require('fs'),path=require('path')","const zlib=require('zlib');const fs=require('fs'),path=require('path')")
p=p.replace("-${lay.layout}.json`","-${lay.layout}.json.gz`")
p=p.replace("fs.writeFileSync(geoFile,JSON.stringify({map:task.map,layout:lay.layout,M,graphSha:G.sha,cap,tiles,fountains}))","fs.writeFileSync(geoFile,zlib.gzipSync(JSON.stringify({map:task.map,layout:lay.layout,M,graphSha:G.sha,cap,tiles,fountains})))")
p += '\nmodule.exports={reconstruct,graph,bfs,identify};\n'
# Adapt the reused replay-authoritative atlas implementation solely inside general.
p=p.replace("const M=R.match.map,G=graph(M)","const IG=require('../spatial/recount'); const ig=IG.geo(R.match.map,task.map,identify(R,task.map,task.gameId).layout); const M=R.match.map,G=graph(M)")
p=p.replace("T[t].cp[r]={heads:","const mids=ds.filter(d=>ig.bin[t][d.body[0]]===2).length; const pockets=ds.filter(d=>ig.pocket[d.body[0]]).length; T[t].cp[r]={mid:mids,pocket:pockets,heads:")
p=p.replace("return {...task,file:undefined", "return {...task,file:undefined")
Path('exp/general/atlas_recount.js').write_text(p)
Path('exp/general/geometry').mkdir(exist_ok=True)
