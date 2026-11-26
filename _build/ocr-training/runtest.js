const fs=require('fs'); const E=require('/home/claude/image-converter/image-to-text/engine.js');
const meta=JSON.parse(fs.readFileSync('out/ocr-meta.json')); const mb=fs.readFileSync('out/ocr-model.bin'); E.load(mb.buffer.slice(mb.byteOffset,mb.byteOffset+mb.length),meta);
const T=JSON.parse(fs.readFileSync('tests.json'));
function ed(a,b){a=[...a];b=[...b];const d=Array.from({length:a.length+1},(_,i)=>[i]);for(let j=1;j<=b.length;j++)d[0][j]=j;for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]===b[j-1]?0:1));return d[a.length][b.length];}
let tot=0,err=0;
for(const c of T.cases){ const b=fs.readFileSync(c.name+'.rgba'); const t0=Date.now(); const out=E.recognize(new Uint8ClampedArray(b.buffer,b.byteOffset,b.length),c.w,c.h); const ms=Date.now()-t0;
  const truth=T.texts.join('\n'); const e=ed(out.replace(/\s+/g,''),truth.replace(/\s+/g,'')), n=[...truth.replace(/\s+/g,'')].length;
  const es=ed(out.replace(/[ \t]+/g,' '),truth); tot+=n; err+=e; console.log(c.name, 'CER', (e/n*100).toFixed(1)+'%', 'with spaces', (es/[...truth].length*100).toFixed(1)+'%', ms+'ms'); if(process.argv[2]) console.log(out); }
console.log('overall CER',(err/tot*100).toFixed(1)+'%');
