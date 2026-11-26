const fs=require('fs'); const E=require('/home/claude/image-converter/image-to-text/engine.js');
const meta=JSON.parse(fs.readFileSync('out/ocr-meta.json')); const mb=fs.readFileSync('out/ocr-model.bin'); E.load(mb.buffer.slice(mb.byteOffset,mb.byteOffset+mb.length),meta);
const nb=fs.readFileSync('out/ocr-net.bin');E.loadNet(nb.buffer.slice(nb.byteOffset,nb.byteOffset+nb.length),JSON.parse(fs.readFileSync('out/ocr-net.json')));
const M=E._M(), med2=M.med*M.med;
const X=fs.readFileSync('vx.bin'),G=new Float32Array(fs.readFileSync('vg.bin').buffer.slice(0)),Y=new Int32Array(fs.readFileSync('vy.bin').buffer.slice(0));
const betas=[0,0.25,0.5,1,2,4,8,1e9]; const ok=betas.map(()=>0); const n=Y.length;
for(let i=0;i<n;i++){const ink=new Float32Array(1024);for(let k=0;k<1024;k++)ink[k]=X[i*1024+k]/255;
 let x0=32,x1=0,y0=32,y1=0;for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(ink[y*32+x]>0.05){x0=Math.min(x0,x);x1=Math.max(x1,x+1);y0=Math.min(y0,y);y1=Math.max(y1,y+1);}
 const w=x1-x0,h=y1-y0,c=new Float32Array(w*h);for(let y=0;y<h;y++)for(let x=0;x<w;x++)c[y*w+x]=ink[(y0+y)*32+x0+x];
 const g=G.slice(i*4,i*4+4); const f=E._features(c,w,h,0,1,0,1,0,1); f.set(g,f.length-4);
 const d2=E._ldaAll(f), r=E._net(ink,g);
 betas.forEach((b,bi)=>{let best=-1e30,arg=0;for(let k=0;k<d2.length;k++){if(M.skip[k])continue;const sc=(b>=1e9?0:r.s[k])-(b>=1e9?1:b)*d2[k]/med2;if(sc>best){best=sc;arg=k;}} if(arg===Y[i])ok[bi]++;});}
betas.forEach((b,bi)=>console.log('beta',b,'acc',(ok[bi]/n).toFixed(4)));
