const fs=require('fs'); const E=require('/home/claude/image-converter/image-to-text/engine.js');
const meta=JSON.parse(fs.readFileSync((process.env.MD||'out')+'/ocr-meta.json')); const mb=fs.readFileSync((process.env.MD||'out')+'/ocr-model.bin'); E.load(mb.buffer.slice(mb.byteOffset,mb.byteOffset+mb.length),meta);
if(process.env.NET){const nb=fs.readFileSync((process.env.ND||'out')+'/ocr-net.bin');E.loadNet(nb.buffer.slice(nb.byteOffset,nb.byteOffset+nb.length),JSON.parse(fs.readFileSync((process.env.ND||'out')+'/ocr-net.json')));}
if(process.env.NETDP){E.netDP=1;} if(process.env.NW){E.nw=+process.env.NW;} if(process.env.BINK){E.binK=+process.env.BINK;} if(process.env.BETA){E.beta=+process.env.BETA;} if(process.env.LAMBDA){E.lambda=+process.env.LAMBDA;}
if(process.env.LM){E.loadLM(JSON.parse(fs.readFileSync((process.env.LMF||'out/ocr-lm.json'))));} if(process.env.GAMMA)E.gamma=+process.env.GAMMA; if(process.env.LDAT)E.ldaT=+process.env.LDAT; if(process.env.NETT)E.netT=+process.env.NETT; if(process.env.LATL)E.latLambda=+process.env.LATL; if(process.env.CJKD)E.cjkDelta=+process.env.CJKD; if(process.env.BETA)E.beta=+process.env.BETA;
const T=JSON.parse(fs.readFileSync(process.env.TESTS||'tests.json'));
function ed(a,b){a=[...a];b=[...b];const d=Array.from({length:a.length+1},(_,i)=>[i]);for(let j=1;j<=b.length;j++)d[0][j]=j;for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]===b[j-1]?0:1));return d[a.length][b.length];}
let tot=0,err=0;
for(const c of T.cases){ const b=fs.readFileSync(c.name+'.rgba'); const t0=Date.now(); const out=E.recognize(new Uint8ClampedArray(b.buffer,b.byteOffset,b.length),c.w,c.h); const ms=Date.now()-t0;
  const truth=(c.texts||T.texts).join('\n'); const e=ed(out.replace(/\s+/g,''),truth.replace(/\s+/g,'')), n=[...truth.replace(/\s+/g,'')].length;
  const es=ed(out.replace(/[ \t]+/g,' '),truth); tot+=n; err+=e; console.log(c.name, 'CER', (e/n*100).toFixed(1)+'%', 'with spaces', (es/[...truth].length*100).toFixed(1)+'%', ms+'ms'); if(process.argv[2]) console.log(out); }
console.log('overall CER',(err/tot*100).toFixed(1)+'%');
