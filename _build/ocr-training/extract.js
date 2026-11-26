// Cut generated pages with the real reader and label each cut piece from the recorded character boxes.
const fs=require('fs'); const E=require('/home/claude/image-converter/image-to-text/engine.js');
const meta=JSON.parse(fs.readFileSync((process.env.MD||'out')+'/ocr-meta.json')); const mb=fs.readFileSync((process.env.MD||'out')+'/ocr-model.bin'); E.load(mb.buffer.slice(mb.byteOffset,mb.byteOffset+mb.length),meta);
const M=E._M();
let tot=0,lab=0,ldaOk=0,missed=0; const Xs=[],Gs=[],Ys=[];
for(const pre of process.argv.slice(3)){
  const pages=JSON.parse(fs.readFileSync(pre+'.json')); const fd=fs.readFileSync(pre+'.bin');
  for(const pg of pages){
    const n=pg.w*pg.h*4, rgba=new Uint8ClampedArray(fd.buffer,fd.byteOffset+pg.off,n); const segs=[]; let sc=1;
    E.onSeg=(sg,ch,k)=>{segs.push(sg);sc=k;};
    E.recognize(rgba,pg.w,pg.h);
    const used=new Set();
    for(const sg of segs){
      tot++;
      const x0=sg.x0/sc,x1=sg.x1/sc,y0=sg.y0/sc,y1=sg.y1/sc; let hit=[];
      pg.boxes.forEach((b,i)=>{const cx=(b[0]+b[1])/2, cy=(b[2]+b[3])/2; if(cx>=x0&&cx<=x1&&cy>=y0-2&&cy<=y1+2)hit.push(i);});
      if(hit.length!==1) continue; const b=pg.boxes[hit[0]]; if(b[4]<0) continue;
      const ov=Math.min(x1,b[1])-Math.max(x0,b[0]); if(ov<0.6*(x1-x0)) continue;
      used.add(hit[0]); lab++; if(sg.c===b[4]) ldaOk++;
      const P=E._norm(sg.ink,sg.gw,sg.gh), u=new Uint8Array(1024); for(let k=0;k<1024;k++)u[k]=Math.round(P[k]*255);
      Xs.push(u); Gs.push(Float32Array.from(sg.geo)); Ys.push(b[4]);
    }
    missed+=pg.boxes.length-used.size;
  }
}
const out=process.argv[2]; const N=Ys.length;
const X=Buffer.alloc(N*1024); Xs.forEach((u,i)=>X.set(u,i*1024)); fs.writeFileSync(out+'.x',X);
const G=new Float32Array(N*4); Gs.forEach((g,i)=>G.set(g,i*4)); fs.writeFileSync(out+'.g',Buffer.from(G.buffer));
fs.writeFileSync(out+'.y',Buffer.from(Int16Array.from(Ys).buffer));
console.log(out,'pieces',tot,'labeled',lab,'lda correct',(ldaOk/lab).toFixed(4),'chars without a clean piece',missed);
