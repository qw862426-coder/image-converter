/* Image & font codecs. Pixels are {width, height, data: RGBA Uint8ClampedArray}. Errors: E_BAD, E_VARIANT, E_WOFF2 */
(function (root) {
'use strict';

/* ---------- 공통 도우미 ---------- */
class Writer {
  constructor(size = 1024) { this.buf = new Uint8Array(size); this.pos = 0; }
  ensure(n) { if (this.pos + n > this.buf.length) { let s = this.buf.length * 2; while (s < this.pos + n) s *= 2; const b = new Uint8Array(s); b.set(this.buf); this.buf = b; } }
  u8(v) { this.ensure(1); this.buf[this.pos++] = v & 255; }
  u16le(v) { this.u8(v); this.u8(v >> 8); }
  u32le(v) { this.u16le(v & 0xffff); this.u16le(v >>> 16); }
  u16be(v) { this.u8(v >> 8); this.u8(v); }
  u32be(v) { this.u16be(v >>> 16); this.u16be(v & 0xffff); }
  bytes(a) { this.ensure(a.length); this.buf.set(a, this.pos); this.pos += a.length; }
  str(s) { for (let i = 0; i < s.length; i++) this.u8(s.charCodeAt(i)); }
  zeros(n) { this.ensure(n); this.pos += n; }
  result() { return this.buf.slice(0, this.pos); }
}
const ascii = s => { const a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i) & 255; return a; };
const latin1 = (b, s = 0, e = b.length) => { let r = ''; for (let i = s; i < e; i++) r += String.fromCharCode(b[i]); return r; };
const newImage = (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) });
function dv(b) { return new DataView(b.buffer, b.byteOffset, b.byteLength); }

/* 흰 배경에 합성 (투명을 지원하지 않는 형식용) */
function flatten(img, bg = [255, 255, 255]) {
  const out = newImage(img.width, img.height), s = img.data, d = out.data;
  for (let i = 0; i < s.length; i += 4) {
    const a = s[i + 3] / 255;
    d[i] = s[i] * a + bg[0] * (1 - a); d[i + 1] = s[i + 1] * a + bg[1] * (1 - a); d[i + 2] = s[i + 2] * a + bg[2] * (1 - a); d[i + 3] = 255;
  }
  return out;
}

/* ---------- 색 줄이기 (GIF·XPM용, 메디안 컷) ---------- */
function quantize(img, maxColors = 256) {
  const d = img.data, n = img.width * img.height;
  const hist = new Uint32Array(32768);
  let hasAlpha = false;
  for (let i = 0; i < n; i++) {
    const p = i * 4;
    if (d[p + 3] < 128) { hasAlpha = true; continue; }
    hist[((d[p] >> 3) << 10) | ((d[p + 1] >> 3) << 5) | (d[p + 2] >> 3)]++;
  }
  const limit = maxColors - (hasAlpha ? 1 : 0);
  const bins = []; for (let i = 0; i < 32768; i++) if (hist[i]) bins.push(i);
  const comp = (b, c) => c === 0 ? b >> 10 : c === 1 ? (b >> 5) & 31 : b & 31;
  let boxes = [bins];
  while (boxes.length < limit) {
    let best = -1, bestRange = 0, bestC = 0;
    boxes.forEach((box, bi) => {
      if (box.length < 2) return;
      for (let c = 0; c < 3; c++) {
        let lo = 31, hi = 0;
        for (const b of box) { const v = comp(b, c); if (v < lo) lo = v; if (v > hi) hi = v; }
        const r = (hi - lo) * Math.log2(box.length + 1);
        if (r > bestRange) { bestRange = r; best = bi; bestC = c; }
      }
    });
    if (best < 0) break;
    const box = boxes[best].sort((a, b) => comp(a, bestC) - comp(b, bestC));
    let total = 0; for (const b of box) total += hist[b];
    let acc = 0, cut = 1;
    for (let i = 0; i < box.length - 1; i++) { acc += hist[box[i]]; if (acc >= total / 2) { cut = i + 1; break; } cut = i + 1; }
    boxes.splice(best, 1, box.slice(0, cut), box.slice(cut));
  }
  const palette = [], binIndex = new Int16Array(32768).fill(-1);
  boxes.forEach(box => {
    if (!box.length) return;
    let r = 0, g = 0, b = 0, t = 0;
    for (const x of box) { const w = hist[x]; t += w; r += ((x >> 10) * 8 + 4) * w; g += (((x >> 5) & 31) * 8 + 4) * w; b += ((x & 31) * 8 + 4) * w; }
    const idx = palette.length; palette.push([Math.round(r / t), Math.round(g / t), Math.round(b / t)]);
    for (const x of box) binIndex[x] = idx;
  });
  let transparentIndex = -1;
  if (hasAlpha) { transparentIndex = palette.length; palette.push([0, 0, 0]); }
  if (!palette.length) palette.push([0, 0, 0]);
  const indices = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    const p = i * 4;
    indices[i] = d[p + 3] < 128 ? transparentIndex : binIndex[((d[p] >> 3) << 10) | ((d[p + 1] >> 3) << 5) | (d[p + 2] >> 3)];
  }
  return { palette, indices, transparentIndex };
}

/* ---------- GIF ---------- */
function encodeGIF(img) {
  const { palette, indices, transparentIndex } = quantize(img, 256);
  let bits = 1; while ((1 << bits) < palette.length) bits++;
  const tableBits = Math.max(bits, 1), minCode = Math.max(2, bits);
  const w = new Writer(img.width * img.height + 1024);
  w.str('GIF89a'); w.u16le(img.width); w.u16le(img.height);
  w.u8(0x80 | 0x70 | (tableBits - 1)); w.u8(0); w.u8(0);
  for (let i = 0; i < (1 << tableBits); i++) { const c = palette[i] || [0, 0, 0]; w.u8(c[0]); w.u8(c[1]); w.u8(c[2]); }
  if (transparentIndex >= 0) { w.bytes([0x21, 0xF9, 4, 1, 0, 0, transparentIndex, 0]); }
  w.u8(0x2C); w.u16le(0); w.u16le(0); w.u16le(img.width); w.u16le(img.height); w.u8(0);
  w.u8(minCode);
  const data = lzwGIF(indices, minCode);
  for (let i = 0; i < data.length; i += 255) { const c = data.subarray(i, i + 255); w.u8(c.length); w.bytes(c); }
  w.u8(0); w.u8(0x3B);
  return w.result();
}
function lzwGIF(idx, minCode) {
  const clear = 1 << minCode, eoi = clear + 1;
  let size = minCode + 1, next = eoi + 1;
  const dict = new Map();
  const out = new Writer(idx.length + 16);
  let acc = 0, nb = 0;
  const emit = c => { acc |= c << nb; nb += size; while (nb >= 8) { out.u8(acc & 255); acc >>>= 8; nb -= 8; } };
  emit(clear);
  let prefix = idx[0];
  for (let i = 1; i < idx.length; i++) {
    const k = idx[i], key = (prefix << 8) | k;
    const v = dict.get(key);
    if (v !== undefined) { prefix = v; continue; }
    emit(prefix);
    if (next < 4096) { dict.set(key, next++); if (next > (1 << size) && size < 12) size++; }
    else { emit(clear); dict.clear(); size = minCode + 1; next = eoi + 1; }
    prefix = k;
  }
  emit(prefix); emit(eoi);
  if (nb > 0) out.u8(acc & 255);
  return out.result();
}

/* ---------- BMP (24비트) ---------- */
function encodeBMP(img) {
  const f = flatten(img), W = img.width, H = img.height, row = Math.ceil(W * 3 / 4) * 4, size = 54 + row * H;
  const w = new Writer(size);
  w.str('BM'); w.u32le(size); w.u32le(0); w.u32le(54);
  w.u32le(40); w.u32le(W); w.u32le(H); w.u16le(1); w.u16le(24); w.u32le(0); w.u32le(row * H); w.u32le(2835); w.u32le(2835); w.u32le(0); w.u32le(0);
  for (let y = H - 1; y >= 0; y--) {
    for (let x = 0; x < W; x++) { const p = (y * W + x) * 4; w.u8(f.data[p + 2]); w.u8(f.data[p + 1]); w.u8(f.data[p]); }
    w.zeros(row - W * 3);
  }
  return w.result();
}

/* ---------- ICO / CUR (PNG를 담는 방식) ---------- */
function encodeICO(entries, cursor = false) {
  const w = new Writer();
  w.u16le(0); w.u16le(cursor ? 2 : 1); w.u16le(entries.length);
  let off = 6 + 16 * entries.length;
  entries = entries.map(e => e.png ? e : Object.assign({}, e, { png: dibIcon(e.pixels) }));
  for (const e of entries) {
    w.u8(e.width >= 256 ? 0 : e.width); w.u8(e.height >= 256 ? 0 : e.height); w.u8(0); w.u8(0);
    if (cursor) { w.u16le(e.hotX || 0); w.u16le(e.hotY || 0); } else { w.u16le(1); w.u16le(32); }
    w.u32le(e.png.length); w.u32le(off); off += e.png.length;
  }
  for (const e of entries) w.bytes(e.png);
  return w.result();
}
/* 아이콘·커서 안에 들어가는 BMP 방식 그림 (오래된 프로그램도 읽을 수 있음) */
function dibIcon(img) {
  const W = img.width, H = img.height, maskRow = Math.ceil(W / 32) * 4;
  const w = new Writer(40 + W * H * 4 + maskRow * H);
  w.u32le(40); w.u32le(W); w.u32le(H * 2); w.u16le(1); w.u16le(32); w.u32le(0); w.u32le(W * H * 4 + maskRow * H); w.u32le(0); w.u32le(0); w.u32le(0); w.u32le(0);
  for (let y = H - 1; y >= 0; y--) for (let x = 0; x < W; x++) { const p = (y * W + x) * 4; w.u8(img.data[p + 2]); w.u8(img.data[p + 1]); w.u8(img.data[p]); w.u8(img.data[p + 3]); }
  for (let y = H - 1; y >= 0; y--) { const row = new Uint8Array(maskRow); for (let x = 0; x < W; x++) if (img.data[(y * W + x) * 4 + 3] < 128) row[x >> 3] |= 0x80 >> (x & 7); w.bytes(row); }
  return w.result();
}
/* CUR을 브라우저가 읽을 수 있는 ICO로 바꿈 */
function curToIco(b) {
  const c = b.slice(); const v = dv(c);
  v.setUint16(2, 1, true);
  const n = v.getUint16(4, true);
  for (let i = 0; i < n; i++) { v.setUint16(6 + i * 16 + 4, 1, true); v.setUint16(6 + i * 16 + 6, 32, true); }
  return c;
}

/* ---------- TIFF ---------- */
function encodeTIFF(img) {
  const W = img.width, H = img.height, n = W * H * 4;
  const tags = [[256, 4, 1, W], [257, 4, 1, H], [258, 3, 4, 'bps'], [259, 3, 1, 1], [262, 3, 1, 2], [273, 4, 1, 'data'],
    [277, 3, 1, 4], [278, 4, 1, H], [279, 4, 1, n], [282, 5, 1, 'xres'], [283, 5, 1, 'yres'], [284, 3, 1, 1], [296, 3, 1, 2], [338, 3, 1, 2]];
  const ifdSize = 2 + tags.length * 12 + 4, extra = 8 + ifdSize;
  const off = { bps: extra, xres: extra + 8, yres: extra + 16, data: extra + 24 };
  const w = new Writer(off.data + n);
  w.str('II'); w.u16le(42); w.u32le(8);
  w.u16le(tags.length);
  for (const [tag, type, count, val] of tags) {
    w.u16le(tag); w.u16le(type); w.u32le(count);
    const v = typeof val === 'string' ? off[val] : val;
    if (type === 3 && count === 1) { w.u16le(v); w.u16le(0); } else w.u32le(v);
  }
  w.u32le(0);
  w.u16le(8); w.u16le(8); w.u16le(8); w.u16le(8);
  w.u32le(72); w.u32le(1); w.u32le(72); w.u32le(1);
  w.bytes(img.data);
  return w.result();
}
async function inflateZlib(bytes) {
  const ds = new DecompressionStream('deflate');
  const stream = new Blob([bytes]).stream().pipeThrough(ds);
  return new Uint8Array(await new Response(stream).arrayBuffer());
}
async function deflateZlib(bytes) {
  const cs = new CompressionStream('deflate');
  const stream = new Blob([bytes]).stream().pipeThrough(cs);
  return new Uint8Array(await new Response(stream).arrayBuffer());
}
function unpackBits(src, expected) {
  const out = new Uint8Array(expected); let i = 0, o = 0;
  while (i < src.length && o < expected) {
    let n = src[i++]; if (n > 127) n -= 256;
    if (n >= 0) { for (let k = 0; k <= n && o < expected; k++) out[o++] = src[i++]; }
    else if (n !== -128) { const v = src[i++]; for (let k = 0; k < 1 - n && o < expected; k++) out[o++] = v; }
  }
  return out;
}
function lzwTIFF(src, expected) {
  const out = new Uint8Array(expected); let o = 0;
  const prefix = new Int32Array(4096), suffix = new Uint8Array(4096), len = new Uint16Array(4096), first = new Uint8Array(4096);
  for (let i = 0; i < 256; i++) { prefix[i] = -1; suffix[i] = i; len[i] = 1; first[i] = i; }
  let next = 258, size = 9, bitPos = 0, old = -1;
  const total = src.length * 8;
  const read = () => {
    if (bitPos + size > total) return 257;
    let v = 0; for (let i = 0; i < size; i++) { const b = bitPos + i; v = (v << 1) | ((src[b >> 3] >> (7 - (b & 7))) & 1); }
    bitPos += size; return v;
  };
  const write = c => { const l = len[c]; let p = o + l - 1; let x = c; while (x >= 0) { if (p < expected) out[p] = suffix[x]; p--; x = prefix[x]; } o += l; };
  while (o < expected) {
    const code = read();
    if (code === 257) break;
    if (code === 256) { next = 258; size = 9; old = -1; continue; }
    if (old < 0) { write(code); old = code; continue; }
    if (code < next) {
      write(code);
      prefix[next] = old; suffix[next] = first[code]; len[next] = len[old] + 1; first[next] = first[old]; next++;
    } else {
      prefix[next] = old; suffix[next] = first[old]; len[next] = len[old] + 1; first[next] = first[old]; next++;
      write(next - 1);
    }
    old = code;
    if (next + 1 >= (1 << size) && size < 12) size++;
  }
  return out;
}
async function decodeTIFF(b) {
  const v = dv(b);
  const le = b[0] === 0x49;
  const u16 = o => v.getUint16(o, le), u32 = o => v.getUint32(o, le);
  if (u16(2) !== 42) throw new Error('E_BAD');
  const ifd = u32(4), count = u16(ifd), T = {};
  const sizes = { 1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8, 16: 8 };
  for (let i = 0; i < count; i++) {
    const e = ifd + 2 + i * 12, tag = u16(e), type = u16(e + 2), n = u32(e + 4);
    const bytes = (sizes[type] || 1) * n, at = bytes <= 4 ? e + 8 : u32(e + 8);
    const vals = [];
    for (let k = 0; k < n; k++) {
      if (type === 3) vals.push(u16(at + k * 2));
      else if (type === 4) vals.push(u32(at + k * 4));
      else if (type === 5) vals.push(u32(at + k * 8) / (u32(at + k * 8 + 4) || 1));
      else vals.push(b[at + k]);
    }
    T[tag] = vals;
  }
  const W = T[256][0], H = T[257][0], spp = (T[277] || [1])[0], bps = (T[258] || [1])[0];
  const comp = (T[259] || [1])[0], photo = (T[262] || [1])[0], pred = (T[317] || [1])[0];
  if ((T[284] || [1])[0] !== 1) throw new Error('E_VARIANT');
  if (T[322]) throw new Error('E_VARIANT');
  if (![1, 4, 8, 16].includes(bps)) throw new Error('E_VARIANT');
  const offs = T[273], cnts = T[279] || [b.length - offs[0]], rps = (T[278] || [H])[0];
  const rowBytes = Math.ceil(W * spp * bps / 8);
  const raw = new Uint8Array(rowBytes * H);
  for (let s = 0; s < offs.length; s++) {
    const rows = Math.min(rps, H - s * rps); if (rows <= 0) break;
    const exp = rows * rowBytes, src = b.subarray(offs[s], offs[s] + cnts[s]);
    let d;
    if (comp === 1) d = src;
    else if (comp === 5) d = lzwTIFF(src, exp);
    else if (comp === 32773) d = unpackBits(src, exp);
    else if (comp === 8 || comp === 32946) d = await inflateZlib(src);
    else throw new Error('E_VARIANT');
    raw.set(d.subarray(0, exp), s * rps * rowBytes);
  }
  if (pred === 2 && bps === 8) {
    for (let y = 0; y < H; y++) { const r = y * rowBytes; for (let i = spp; i < W * spp; i++) raw[r + i] = (raw[r + i] + raw[r + i - spp]) & 255; }
  }
  const sample = (y, i) => {
    const r = y * rowBytes;
    if (bps === 8) return raw[r + i];
    if (bps === 16) return raw[r + i * 2 + (le ? 1 : 0)];
    if (bps === 4) return ((raw[r + (i >> 1)] >> ((i & 1) ? 0 : 4)) & 15) * 17;
    return ((raw[r + (i >> 3)] >> (7 - (i & 7))) & 1) * 255;
  };
  const img = newImage(W, H), d = img.data, cmap = T[320];
  const extra = T[338] ? T[338][0] : (spp === 4 && photo === 2 ? 2 : spp === 2 ? 2 : 0);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const p = (y * W + x) * 4, s0 = x * spp;
    let r, g, bl, a = 255;
    if (photo === 2) { r = sample(y, s0); g = sample(y, s0 + 1); bl = sample(y, s0 + 2); if (spp > 3 && extra) a = sample(y, s0 + 3); if (extra === 1 && a) { r = Math.min(255, r * 255 / a); g = Math.min(255, g * 255 / a); bl = Math.min(255, bl * 255 / a); } }
    else if (photo === 3 && cmap) { const ix = bps === 8 ? raw[y * rowBytes + s0] : bps === 4 ? sample(y, s0) / 17 : sample(y, s0) / 255; const nC = 1 << bps; r = cmap[ix] >> 8; g = cmap[nC + ix] >> 8; bl = cmap[2 * nC + ix] >> 8; }
    else if (photo === 5) { const c = sample(y, s0), m = sample(y, s0 + 1), yy = sample(y, s0 + 2), k = sample(y, s0 + 3); r = 255 - Math.min(255, c + k); g = 255 - Math.min(255, m + k); bl = 255 - Math.min(255, yy + k); }
    else { let gr = sample(y, s0); if (photo === 0) gr = 255 - gr; r = g = bl = gr; if (spp > 1 && extra) a = sample(y, s0 + 1); }
    d[p] = r; d[p + 1] = g; d[p + 2] = bl; d[p + 3] = a;
  }
  return img;
}

/* ---------- TGA ---------- */
function encodeTGA(img) {
  const w = new Writer(18 + img.data.length + 26);
  w.bytes([0, 0, 2, 0, 0, 0, 0, 0]); w.u16le(0); w.u16le(0); w.u16le(img.width); w.u16le(img.height); w.u8(32); w.u8(0x28);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) { w.u8(d[i + 2]); w.u8(d[i + 1]); w.u8(d[i]); w.u8(d[i + 3]); }
  w.u32le(0); w.u32le(0); w.str('TRUEVISION-XFILE.'); w.u8(0);
  return w.result();
}
function decodeTGA(b) {
  const v = dv(b);
  const idLen = b[0], cmType = b[1], type = b[2], cmStart = v.getUint16(3, true), cmLen = v.getUint16(5, true), cmDepth = b[7];
  const W = v.getUint16(12, true), H = v.getUint16(14, true), bpp = b[16], desc = b[17];
  const base = type & 7, rle = type & 8;
  if (![1, 2, 3].includes(base) || !W || !H) throw new Error('E_BAD');
  let pos = 18 + idLen;
  const readColor = (depth, at) => {
    if (depth === 32) return [b[at + 2], b[at + 1], b[at], b[at + 3]];
    if (depth === 24) return [b[at + 2], b[at + 1], b[at], 255];
    if (depth === 15 || depth === 16) { const c = b[at] | (b[at + 1] << 8); return [((c >> 10) & 31) * 255 / 31, ((c >> 5) & 31) * 255 / 31, (c & 31) * 255 / 31, 255]; }
    return [b[at], b[at], b[at], 255];
  };
  let pal = null;
  if (cmType === 1) {
    const step = Math.ceil(cmDepth / 8); pal = [];
    for (let i = 0; i < cmLen; i++) pal[cmStart + i] = readColor(cmDepth, pos + i * step);
    pos += cmLen * step;
  }
  const step = Math.ceil(bpp / 8);
  const px = base === 1 ? (at => pal[b[at] | (step === 2 ? b[at + 1] << 8 : 0)] || [0, 0, 0, 255])
    : base === 3 ? (at => [b[at], b[at], b[at], bpp === 16 ? b[at + 1] : 255])
    : (at => readColor(bpp, at));
  const n = W * H, list = new Array(n);
  let i = 0;
  if (!rle) { for (; i < n; i++, pos += step) list[i] = px(pos); }
  else {
    while (i < n && pos < b.length) {
      const h = b[pos++], c = (h & 127) + 1;
      if (h & 128) { const col = px(pos); pos += step; for (let k = 0; k < c && i < n; k++) list[i++] = col; }
      else for (let k = 0; k < c && i < n; k++, pos += step) list[i++] = px(pos);
    }
  }
  const img = newImage(W, H), top = desc & 0x20, rtl = desc & 0x10;
  for (let k = 0; k < n; k++) {
    let x = k % W, y = Math.floor(k / W);
    if (!top) y = H - 1 - y; if (rtl) x = W - 1 - x;
    const c = list[k] || [0, 0, 0, 255], p = (y * W + x) * 4;
    img.data[p] = c[0]; img.data[p + 1] = c[1]; img.data[p + 2] = c[2]; img.data[p + 3] = c[3];
  }
  return img;
}

/* ---------- PSD ---------- */
function encodePSD(img) {
  const W = img.width, H = img.height, n = W * H;
  const w = new Writer(26 + 14 + n * 4);
  w.str('8BPS'); w.u16be(1); w.zeros(6); w.u16be(4); w.u32be(H); w.u32be(W); w.u16be(8); w.u16be(3);
  w.u32be(0); w.u32be(0); w.u32be(0); w.u16be(0);
  for (let c = 0; c < 4; c++) for (let i = 0; i < n; i++) w.u8(img.data[i * 4 + c]);
  return w.result();
}
function decodePSD(b) {
  const v = dv(b);
  if (latin1(b, 0, 4) !== '8BPS') throw new Error('E_BAD');
  if (v.getUint16(4) !== 1) throw new Error('E_VARIANT');
  const ch = v.getUint16(12), H = v.getUint32(14), W = v.getUint32(18), depth = v.getUint16(22), mode = v.getUint16(24);
  if (depth !== 8 && depth !== 16) throw new Error('E_VARIANT');
  let pos = 26;
  const cmLen = v.getUint32(pos), cmAt = pos + 4; pos += 4 + cmLen;
  pos += 4 + v.getUint32(pos);
  pos += 4 + v.getUint32(pos);
  const comp = v.getUint16(pos); pos += 2;
  const bpc = depth / 8, rowBytes = W * bpc, planes = [];
  if (comp === 0) { for (let c = 0; c < ch; c++) { planes.push(b.subarray(pos, pos + rowBytes * H)); pos += rowBytes * H; } }
  else if (comp === 1) {
    const counts = []; for (let i = 0; i < ch * H; i++) { counts.push(v.getUint16(pos)); pos += 2; }
    for (let c = 0; c < ch; c++) {
      const pl = new Uint8Array(rowBytes * H);
      for (let y = 0; y < H; y++) { const len = counts[c * H + y]; pl.set(unpackBits(b.subarray(pos, pos + len), rowBytes), y * rowBytes); pos += len; }
      planes.push(pl);
    }
  } else throw new Error('E_VARIANT');
  const g = (c, i) => planes[c][i * bpc];
  const img = newImage(W, H), d = img.data;
  for (let i = 0; i < W * H; i++) {
    const p = i * 4; let r, gg, bl, a = 255;
    if (mode === 3) { r = g(0, i); gg = g(1, i); bl = g(2, i); if (ch > 3) a = g(3, i); }
    else if (mode === 4) { const C = 255 - g(0, i), M = 255 - g(1, i), Y = 255 - g(2, i), K = 255 - g(3, i); r = 255 - Math.min(255, C + K); gg = 255 - Math.min(255, M + K); bl = 255 - Math.min(255, Y + K); if (ch > 4) a = g(4, i); }
    else if (mode === 2) { const ix = g(0, i); r = b[cmAt + ix]; gg = b[cmAt + 256 + ix]; bl = b[cmAt + 512 + ix]; }
    else { r = gg = bl = g(0, i); if (ch > 1) a = g(1, i); }
    d[p] = r; d[p + 1] = gg; d[p + 2] = bl; d[p + 3] = a;
  }
  return img;
}

/* ---------- DDS ---------- */
function encodeDDS(img) {
  const w = new Writer(128 + img.data.length);
  w.str('DDS '); w.u32le(124); w.u32le(0x100F); w.u32le(img.height); w.u32le(img.width); w.u32le(img.width * 4); w.u32le(0); w.u32le(0); w.zeros(44);
  w.u32le(32); w.u32le(0x41); w.u32le(0); w.u32le(32); w.u32le(0x00ff0000); w.u32le(0x0000ff00); w.u32le(0x000000ff); w.u32le(0xff000000);
  w.u32le(0x1000); w.u32le(0); w.u32le(0); w.u32le(0); w.u32le(0);
  const d = img.data; for (let i = 0; i < d.length; i += 4) { w.u8(d[i + 2]); w.u8(d[i + 1]); w.u8(d[i]); w.u8(d[i + 3]); }
  return w.result();
}
function decodeDDS(b) {
  const v = dv(b);
  if (latin1(b, 0, 4) !== 'DDS ') throw new Error('E_BAD');
  const H = v.getUint32(12, true), W = v.getUint32(16, true), pf = v.getUint32(80, true);
  let four = latin1(b, 84, 88), pos = 128;
  if (four === 'DX10') {
    const f = v.getUint32(128, true); pos = 148;
    four = { 71: 'DXT1', 72: 'DXT1', 74: 'DXT3', 75: 'DXT3', 77: 'DXT5', 78: 'DXT5', 28: 'RGBA', 29: 'RGBA', 87: 'BGRA', 91: 'BGRA' }[f];
    if (!four) throw new Error('E_VARIANT');
  }
  const img = newImage(W, H), d = img.data;
  if (four === 'RGBA' || four === 'BGRA') {
    for (let i = 0; i < W * H; i++) { const s = pos + i * 4, p = i * 4; d[p] = b[s + (four === 'RGBA' ? 0 : 2)]; d[p + 1] = b[s + 1]; d[p + 2] = b[s + (four === 'RGBA' ? 2 : 0)]; d[p + 3] = b[s + 3]; }
    return img;
  }
  if (pf & 0x4) {
    if (!['DXT1', 'DXT3', 'DXT5'].includes(four)) throw new Error('E_VARIANT');
    const bw = Math.ceil(W / 4), bh = Math.ceil(H / 4), bs = four === 'DXT1' ? 8 : 16;
    for (let by = 0; by < bh; by++) for (let bx = 0; bx < bw; bx++) {
      const at = pos + (by * bw + bx) * bs, cAt = four === 'DXT1' ? at : at + 8;
      const c0 = v.getUint16(cAt, true), c1 = v.getUint16(cAt + 2, true);
      const rgb = c => [((c >> 11) & 31) * 255 / 31, ((c >> 5) & 63) * 255 / 63, (c & 31) * 255 / 31];
      const a = rgb(c0), bb = rgb(c1), cols = [[...a, 255], [...bb, 255]];
      if (c0 > c1 || four !== 'DXT1') { cols.push([(2 * a[0] + bb[0]) / 3, (2 * a[1] + bb[1]) / 3, (2 * a[2] + bb[2]) / 3, 255], [(a[0] + 2 * bb[0]) / 3, (a[1] + 2 * bb[1]) / 3, (a[2] + 2 * bb[2]) / 3, 255]); }
      else cols.push([(a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2, (a[2] + bb[2]) / 2, 255], [0, 0, 0, 0]);
      const bits = v.getUint32(cAt + 4, true);
      let alphas = null;
      if (four === 'DXT5') {
        const a0 = b[at], a1 = b[at + 1], t = [a0, a1];
        if (a0 > a1) for (let k = 1; k < 7; k++) t.push(((7 - k) * a0 + k * a1) / 7);
        else { for (let k = 1; k < 5; k++) t.push(((5 - k) * a0 + k * a1) / 5); t.push(0, 255); }
        let ab = 0n; for (let k = 0; k < 6; k++) ab |= BigInt(b[at + 2 + k]) << BigInt(8 * k);
        alphas = []; for (let k = 0; k < 16; k++) alphas.push(t[Number((ab >> BigInt(3 * k)) & 7n)]);
      }
      for (let k = 0; k < 16; k++) {
        const x = bx * 4 + (k & 3), y = by * 4 + (k >> 2); if (x >= W || y >= H) continue;
        const c = cols[(bits >> (2 * k)) & 3], p = (y * W + x) * 4;
        d[p] = c[0]; d[p + 1] = c[1]; d[p + 2] = c[2];
        d[p + 3] = four === 'DXT1' ? c[3] : four === 'DXT3' ? ((b[at + (k >> 1)] >> ((k & 1) * 4)) & 15) * 17 : alphas[k];
      }
    }
    return img;
  }
  const bits = v.getUint32(88, true), bpp = bits / 8, masks = [92, 96, 100, 104].map(o => v.getUint32(o, true));
  const ext = m => { if (!m) return null; let s = 0; while (!((m >>> s) & 1)) s++; let w = 0; while ((m >>> (s + w)) & 1) w++; return [s, (1 << w) - 1]; };
  const ch = masks.map(ext), lum = pf & 0x20000, alphaOnly = (pf & 0x2) && !(pf & 0x40) && !lum;
  for (let i = 0; i < W * H; i++) {
    const s = pos + i * bpp; let val = 0; for (let k = 0; k < bpp; k++) val |= b[s + k] << (8 * k); val >>>= 0;
    const get = c => ch[c] ? Math.round(((val >>> ch[c][0]) & ch[c][1]) * 255 / ch[c][1]) : null;
    const p = i * 4;
    if (alphaOnly) { d[p] = d[p + 1] = d[p + 2] = 0; d[p + 3] = get(3) ?? val; continue; }
    if (lum) { d[p] = d[p + 1] = d[p + 2] = get(0); }
    else { d[p] = get(0); d[p + 1] = get(1); d[p + 2] = get(2); }
    d[p + 3] = (pf & 0x1) && ch[3] ? get(3) : 255;
  }
  return img;
}

/* ---------- SGI (.rgb) ---------- */
function encodeSGI(img) {
  const W = img.width, H = img.height, w = new Writer(512 + W * H * 4);
  w.u16be(474); w.u8(0); w.u8(1); w.u16be(3); w.u16be(W); w.u16be(H); w.u16be(4); w.u32be(0); w.u32be(255); w.zeros(4);
  const name = 'converted'; w.str(name); w.zeros(80 - name.length); w.u32be(0); w.zeros(404);
  for (let c = 0; c < 4; c++) for (let y = H - 1; y >= 0; y--) for (let x = 0; x < W; x++) w.u8(img.data[(y * W + x) * 4 + c]);
  return w.result();
}
function decodeSGI(b) {
  const v = dv(b);
  if (v.getUint16(0) !== 474) throw new Error('E_BAD');
  const rle = b[2], bpc = b[3], W = v.getUint16(6), H = v.getUint16(8), Z = v.getUint16(10) || 1;
  const chans = [];
  for (let z = 0; z < Z; z++) {
    const pl = new Uint8Array(W * H);
    for (let y = 0; y < H; y++) {
      let row;
      if (!rle) { const at = 512 + (z * H + y) * W * bpc; row = new Uint8Array(W); for (let x = 0; x < W; x++) row[x] = b[at + x * bpc]; }
      else {
        const start = v.getUint32(512 + (z * H + y) * 4); row = new Uint8Array(W);
        let p = start, o = 0;
        const rd = () => { const r = bpc === 2 ? b[p] : b[p]; p += bpc; return r; };
        while (o < W) { const c = rd(), n = c & 127; if (!n) break; if (c & 128) for (let k = 0; k < n && o < W; k++) row[o++] = rd(); else { const val = rd(); for (let k = 0; k < n && o < W; k++) row[o++] = val; } }
      }
      pl.set(row, (H - 1 - y) * W);
    }
    chans.push(pl);
  }
  const img = newImage(W, H), d = img.data;
  for (let i = 0; i < W * H; i++) {
    const p = i * 4;
    if (Z >= 3) { d[p] = chans[0][i]; d[p + 1] = chans[1][i]; d[p + 2] = chans[2][i]; d[p + 3] = Z > 3 ? chans[3][i] : 255; }
    else { d[p] = d[p + 1] = d[p + 2] = chans[0][i]; d[p + 3] = Z === 2 ? chans[1][i] : 255; }
  }
  return img;
}

/* ---------- XPM ---------- */
const XPM_CHARS = '.XoO+@#$%&*=-;:>,<1234567890qwertyuipasdfghjklzxcvbnmMNBVCZASDFGHJKLPIUYTREWQ!~^/()_`\'][{}|';
function encodeXPM(img) {
  const { palette, indices, transparentIndex } = quantize(img, 256);
  const cpp = palette.length > XPM_CHARS.length ? 2 : 1;
  const key = i => cpp === 1 ? XPM_CHARS[i] : XPM_CHARS[i % XPM_CHARS.length] + XPM_CHARS[Math.floor(i / XPM_CHARS.length)];
  const hex = n => n.toString(16).padStart(2, '0').toUpperCase();
  const lines = ['/* XPM */', 'static char *image[] = {', `"${img.width} ${img.height} ${palette.length} ${cpp}",`];
  palette.forEach((c, i) => lines.push(`"${key(i)} c ${i === transparentIndex ? 'None' : '#' + hex(c[0]) + hex(c[1]) + hex(c[2])}",`));
  for (let y = 0; y < img.height; y++) {
    let s = ''; for (let x = 0; x < img.width; x++) s += key(indices[y * img.width + x]);
    lines.push(`"${s}"${y === img.height - 1 ? '' : ','}`);
  }
  lines.push('};', '');
  return ascii(lines.join('\n'));
}
const NAMED = { black: '000000', white: 'ffffff', red: 'ff0000', green: '00ff00', blue: '0000ff', yellow: 'ffff00', cyan: '00ffff', magenta: 'ff00ff', gray: 'bebebe', grey: 'bebebe', orange: 'ffa500', purple: 'a020f0', brown: 'a52a2a' };
function decodeXPM(b, resolveName) {
  const text = latin1(b);
  const strs = []; const re = /"((?:[^"\\]|\\.)*)"/g; let m; while ((m = re.exec(text))) strs.push(m[1]);
  if (!strs.length) throw new Error('E_BAD');
  const [W, H, N, cpp] = strs[0].trim().split(/\s+/).map(Number);
  const colors = new Map();
  for (let i = 1; i <= N; i++) {
    const s = strs[i], k = s.slice(0, cpp), toks = s.slice(cpp).trim().split(/\s+/);
    let val = null;
    for (let t = 0; t < toks.length; t++) if (['c', 'g', 'g4', 'm', 's'].includes(toks[t])) {
      let j = t + 1, vv = []; while (j < toks.length && !['c', 'g', 'g4', 'm', 's'].includes(toks[j])) vv.push(toks[j++]);
      if (toks[t] === 'c' || val === null) val = vv.join(' ');
    }
    let rgba = [0, 0, 0, 255];
    if (!val || /^none$/i.test(val)) rgba = [0, 0, 0, 0];
    else if (val[0] === '#') {
      const h = val.slice(1), n = h.length / 3;
      rgba = [0, 1, 2].map(c => parseInt(h.substr(c * n, Math.min(n, 2)), 16) * (n === 1 ? 17 : 1)).concat(255);
    } else {
      const r = resolveName ? resolveName(val) : null;
      const hx = r || NAMED[val.toLowerCase()] || 'bebebe';
      rgba = [parseInt(hx.slice(0, 2), 16), parseInt(hx.slice(2, 4), 16), parseInt(hx.slice(4, 6), 16), 255];
    }
    colors.set(k, rgba);
  }
  const img = newImage(W, H);
  for (let y = 0; y < H; y++) {
    const row = strs[1 + N + y] || '';
    for (let x = 0; x < W; x++) { const c = colors.get(row.substr(x * cpp, cpp)) || [0, 0, 0, 0]; img.data.set(c, (y * W + x) * 4); }
  }
  return img;
}

/* ---------- PDF (JPEG 이미지를 페이지로) ---------- */
function encodePDF(pages) {
  const chunks = [], offs = []; let len = 0;
  const add = x => { const a = typeof x === 'string' ? ascii(x) : x; chunks.push(a); len += a.length; };
  const obj = (n, body) => { offs[n] = len; add(`${n} 0 obj\n`); body(); add('\nendobj\n'); };
  add('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');
  const kids = pages.map((_, i) => `${3 + i * 3} 0 R`).join(' ');
  obj(1, () => add('<< /Type /Catalog /Pages 2 0 R >>'));
  obj(2, () => add(`<< /Type /Pages /Kids [${kids}] /Count ${pages.length} >>`));
  pages.forEach((p, i) => {
    const n = 3 + i * 3, pw = +(p.ptW || p.width * 0.75).toFixed(2), ph = +(p.ptH || p.height * 0.75).toFixed(2);
    obj(n, () => add(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pw} ${ph}] /Resources << /XObject << /Im${i} ${n + 1} 0 R >> >> /Contents ${n + 2} 0 R >>`));
    obj(n + 1, () => { add(`<< /Type /XObject /Subtype /Image /Width ${p.width} /Height ${p.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${p.jpeg.length} >>\nstream\n`); add(p.jpeg); add('\nendstream'); });
    const content = `q ${pw} 0 0 ${ph} 0 0 cm /Im${i} Do Q`;
    obj(n + 2, () => add(`<< /Length ${content.length} >>\nstream\n${content}\nendstream`));
  });
  const total = 3 + pages.length * 3, xref = len;
  add(`xref\n0 ${total}\n0000000000 65535 f \n`);
  for (let i = 1; i < total; i++) add(String(offs[i]).padStart(10, '0') + ' 00000 n \n');
  add(`trailer\n<< /Size ${total} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`);
  const out = new Uint8Array(len); let o = 0; for (const c of chunks) { out.set(c, o); o += c.length; }
  return out;
}

/* ---------- SVG (그림을 담은 SVG) ---------- */
function encodeSVG(width, height, pngBase64) {
  return ascii(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"><image width="${width}" height="${height}" xlink:href="data:image/png;base64,${pngBase64}"/></svg>`);
}

/* ---------- 선 그림 → SVG (CAD·자수 미리보기용) ---------- */
const STITCH_COLORS = ['#1b1b1b', '#d7263d', '#1b6ec2', '#2e9e44', '#f29e0c', '#8e44ad', '#16a2b8', '#e05297', '#7a5230', '#6c7a89'];
function pathsToSVG(paths, { flipY = false, lineWidth = 1.2, maxSide = 1600 } = {}) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const p of paths) for (const [x, y] of p.pts) { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; }
  if (!isFinite(minX)) throw new Error('E_BAD');
  const bw = Math.max(maxX - minX, 1e-6), bh = Math.max(maxY - minY, 1e-6);
  const s = (maxSide - 40) / Math.max(bw, bh), W = Math.round(bw * s + 40), H = Math.round(bh * s + 40);
  const tx = x => (20 + (x - minX) * s).toFixed(1), ty = y => (flipY ? 20 + (maxY - y) * s : 20 + (y - minY) * s).toFixed(1);
  let body = '';
  for (const p of paths) {
    if (p.pts.length < 2) continue;
    body += `<polyline fill="none" stroke="${p.color || '#111'}" stroke-width="${lineWidth}" stroke-linecap="round" stroke-linejoin="round" points="${p.pts.map(([x, y]) => tx(x) + ',' + ty(y)).join(' ')}"/>`;
  }
  return { svg: `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="100%" height="100%" fill="#fff"/>${body}</svg>`, width: W, height: H };
}
function stitchesToPaths(stitches) {
  const paths = []; let cur = null, color = 0;
  for (const s of stitches) {
    if (s.type === 'color') { color++; cur = null; continue; }
    if (s.type === 'jump') { cur = null; continue; }
    if (!cur) { cur = { color: STITCH_COLORS[color % STITCH_COLORS.length], pts: s.from ? [s.from] : [] }; paths.push(cur); }
    cur.pts.push([s.x, s.y]);
  }
  return paths;
}

/* DST (타지마) */
function decodeDST(b) {
  let x = 0, y = 0; const out = [];
  for (let i = 512; i + 2 < b.length; i += 3) {
    const b0 = b[i], b1 = b[i + 1], b2 = b[i + 2];
    if ((b2 & 0xF3) === 0xF3) break;
    let dx = 0, dy = 0;
    if (b2 & 0x04) dx += 81; if (b2 & 0x08) dx -= 81; if (b1 & 0x04) dx += 27; if (b1 & 0x08) dx -= 27;
    if (b0 & 0x04) dx += 9; if (b0 & 0x08) dx -= 9; if (b1 & 0x01) dx += 3; if (b1 & 0x02) dx -= 3; if (b0 & 0x01) dx += 1; if (b0 & 0x02) dx -= 1;
    if (b2 & 0x20) dy += 81; if (b2 & 0x10) dy -= 81; if (b1 & 0x20) dy += 27; if (b1 & 0x10) dy -= 27;
    if (b0 & 0x20) dy += 9; if (b0 & 0x10) dy -= 9; if (b1 & 0x80) dy += 3; if (b1 & 0x40) dy -= 3; if (b0 & 0x80) dy += 1; if (b0 & 0x40) dy -= 1;
    const from = [x, -y]; x += dx; y += dy;
    if ((b2 & 0xC3) === 0xC3) out.push({ type: 'color' });
    else if (b2 & 0x80) out.push({ type: 'jump' });
    else out.push({ type: 'stitch', x, y: -y, from });
  }
  return stitchesToPaths(out);
}
/* EXP (멜코) */
function decodeEXP(b) {
  const s8 = v => v > 127 ? v - 256 : v;
  let x = 0, y = 0; const out = [];
  for (let i = 0; i + 1 < b.length;) {
    let b0 = b[i], b1 = b[i + 1]; i += 2;
    if (b0 !== 0x80) { const from = [x, y]; x += s8(b0); y -= s8(b1); out.push({ type: 'stitch', x, y, from }); continue; }
    const ctl = b1; if (i + 1 >= b.length) break;
    b0 = b[i]; b1 = b[i + 1]; i += 2;
    const from = [x, y]; x += s8(b0); y -= s8(b1);
    if (ctl & 0x01) { out.push({ type: 'color' }); out.push({ type: 'jump' }); }
    else if (ctl === 0x02) out.push({ type: 'stitch', x, y, from });
    else out.push({ type: 'jump' });
  }
  return stitchesToPaths(out);
}
/* PES (브라더) — 안쪽 PEC 바늘 데이터를 읽음 */
function decodePES(b) {
  const v = dv(b);
  let pec;
  if (latin1(b, 0, 4) === '#PES') pec = v.getUint32(8, true);
  else if (latin1(b, 0, 4) === '#PEC') pec = 8;
  else throw new Error('E_BAD');
  const cc = b[pec + 48];
  let i = pec + 49 + (cc + 1) + (0x1D0 - cc) + 3 + 0x0B;
  let x = 0, y = 0; const out = [];
  while (i + 1 < b.length) {
    let v1 = b[i++], v2 = b[i++];
    if (v1 === 0xFF && v2 === 0x00) break;
    if (v1 === 0xFE && v2 === 0xB0) { i++; out.push({ type: 'color' }); continue; }
    let jump = false, dx, dy;
    if (v1 & 0x80) { if (v1 & 0x30) jump = true; dx = ((v1 & 0x0F) << 8) + v2; if (dx > 0x7FF) dx -= 0x1000; v2 = b[i++]; }
    else dx = v1 > 0x3F ? v1 - 0x80 : v1;
    if (v2 & 0x80) { if (v2 & 0x30) jump = true; dy = ((v2 & 0x0F) << 8) + b[i++]; if (dy > 0x7FF) dy -= 0x1000; }
    else dy = v2 > 0x3F ? v2 - 0x80 : v2;
    const from = [x, y]; x += dx; y += dy;
    out.push(jump ? { type: 'jump' } : { type: 'stitch', x, y, from });
  }
  return stitchesToPaths(out);
}
/* PCS (파프 디자인) */
function decodePCS(b) {
  const v = dv(b);
  const nColors = v.getUint16(2, true);
  let i = 4 + nColors * 4 + 2;
  const s24 = (a, c, d) => { let n = a | (c << 8) | (d << 16); if (n & 0x800000) n -= 0x1000000; return n; };
  const out = []; let last = null;
  for (; i + 8 < b.length + 0; i += 9) {
    if (i + 9 > b.length) break;
    const x = s24(b[i + 1], b[i + 2], b[i + 3]) * 0.6, y = -s24(b[i + 5], b[i + 6], b[i + 7]) * 0.6, c = b[i + 8];
    if (c & 0x01) { out.push({ type: 'color' }); continue; }
    if (c & 0x04) { out.push({ type: 'jump' }); last = [x, y]; continue; }
    out.push({ type: 'stitch', x, y, from: last }); last = [x, y];
  }
  return stitchesToPaths(out);
}

/* HPGL (.plt) */
function decodePLT(b) {
  const text = latin1(b).replace(/\x1b[^;]*;?/g, '');
  const paths = []; let x = 0, y = 0, down = false, rel = false, cur = null;
  const pens = ['#111', '#111', '#d7263d', '#2e9e44', '#1b6ec2', '#f29e0c', '#8e44ad', '#16a2b8'];
  let color = '#111';
  const moveTo = (nx, ny) => {
    if (down) { if (!cur) { cur = { color, pts: [[x, y]] }; paths.push(cur); } cur.pts.push([nx, ny]); }
    else cur = null;
    x = nx; y = ny;
  };
  const re = /([A-Z]{2})([^A-Z;]*)/gi; let m;
  while ((m = re.exec(text))) {
    const cmd = m[1].toUpperCase(), nums = (m[2].match(/-?\d+(\.\d+)?/g) || []).map(Number);
    if (cmd === 'PU' || cmd === 'PD') { down = cmd === 'PD'; if (!down) cur = null; }
    else if (cmd === 'PA') rel = false;
    else if (cmd === 'PR') rel = true;
    else if (cmd === 'SP') { color = pens[nums[0] || 1] || '#111'; cur = null; continue; }
    else if (cmd === 'CI' && nums.length) {
      const r = nums[0], pts = []; for (let k = 0; k <= 72; k++) { const a = k / 72 * Math.PI * 2; pts.push([x + r * Math.cos(a), y + r * Math.sin(a)]); }
      paths.push({ color, pts }); continue;
    } else if (cmd === 'IN') { x = y = 0; down = false; rel = false; cur = null; continue; }
    else continue;
    for (let k = 0; k + 1 < nums.length; k += 2) moveTo(rel ? x + nums[k] : nums[k], rel ? y + nums[k + 1] : nums[k + 1]);
  }
  return paths;
}

/* DXF (오토캐드 도면, 기본 도형만) */
function decodeDXF(b) {
  const lines = latin1(b).split(/\r?\n/);
  const pairs = []; for (let i = 0; i + 1 < lines.length; i += 2) pairs.push([parseInt(lines[i].trim(), 10), lines[i + 1].trim()]);
  let i = pairs.findIndex((p, k) => p[0] === 2 && p[1] === 'ENTITIES' && pairs[k - 1] && pairs[k - 1][1] === 'SECTION');
  if (i < 0) throw new Error('E_BAD');
  const paths = []; i++;
  const arc = (cx, cy, r, a0, a1) => { if (a1 < a0) a1 += 360; const n = Math.max(8, Math.ceil((a1 - a0) / 5)), pts = []; for (let k = 0; k <= n; k++) { const a = (a0 + (a1 - a0) * k / n) * Math.PI / 180; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } return pts; };
  let poly = null;
  while (i < pairs.length) {
    const [code, val] = pairs[i];
    if (code !== 0) { i++; continue; }
    if (val === 'ENDSEC') break;
    const type = val, g = {}; const list = []; i++;
    while (i < pairs.length && pairs[i][0] !== 0) { const [c, vv] = pairs[i]; list.push([c, vv]); if (!(c in g)) g[c] = parseFloat(vv); i++; }
    if (type === 'LINE') paths.push({ pts: [[g[10], g[20]], [g[11], g[21]]] });
    else if (type === 'CIRCLE') paths.push({ pts: arc(g[10], g[20], g[40], 0, 360) });
    else if (type === 'ARC') paths.push({ pts: arc(g[10], g[20], g[40], g[50], g[51]) });
    else if (type === 'LWPOLYLINE' || type === 'SPLINE') {
      const pts = []; let px = null;
      for (const [c, vv] of list) { if (c === 10) px = parseFloat(vv); else if (c === 20 && px !== null) { pts.push([px, parseFloat(vv)]); px = null; } }
      if (type === 'LWPOLYLINE' && (g[70] & 1) && pts.length) pts.push(pts[0]);
      paths.push({ pts });
    }
    else if (type === 'POLYLINE') { poly = { pts: [], closed: g[70] & 1 }; paths.push(poly); }
    else if (type === 'VERTEX' && poly) poly.pts.push([g[10], g[20]]);
    else if (type === 'SEQEND' && poly) { if (poly.closed && poly.pts.length) poly.pts.push(poly.pts[0]); poly = null; }
    else if (type === 'POINT') paths.push({ pts: arc(g[10], g[20], 0.5, 0, 360) });
  }
  return paths;
}

/* ---------- 폰트: TTF/OTF ↔ WOFF ---------- */
async function sfntToWoff(b) {
  const v = dv(b), flavor = v.getUint32(0), n = v.getUint16(4);
  if (flavor !== 0x00010000 && flavor !== 0x4F54544F && flavor !== 0x74727565) throw new Error('E_BAD');
  const tables = [];
  let sfntSize = 12 + 16 * n;
  for (let i = 0; i < n; i++) {
    const e = 12 + i * 16, off = v.getUint32(e + 8), len = v.getUint32(e + 12);
    const data = b.subarray(off, off + len), comp = await deflateZlib(data);
    tables.push({ tag: v.getUint32(e), sum: v.getUint32(e + 4), len, data: comp.length < len ? comp : data });
    sfntSize += (len + 3) & ~3;
  }
  let off = 44 + 20 * n; tables.forEach(t => { t.off = off; off += (t.data.length + 3) & ~3; });
  const w = new Writer(off);
  w.str('wOFF'); w.u32be(flavor); w.u32be(off); w.u16be(n); w.u16be(0); w.u32be(sfntSize); w.u16be(1); w.u16be(0);
  w.u32be(0); w.u32be(0); w.u32be(0); w.u32be(0); w.u32be(0);
  for (const t of tables) { w.u32be(t.tag); w.u32be(t.off); w.u32be(t.data.length); w.u32be(t.len); w.u32be(t.sum); }
  for (const t of tables) { w.bytes(t.data); w.zeros(((t.data.length + 3) & ~3) - t.data.length); }
  return w.result();
}
async function woffToSfnt(b) {
  const v = dv(b);
  if (latin1(b, 0, 4) === 'wOF2') throw new Error('E_WOFF2');
  if (latin1(b, 0, 4) !== 'wOFF') throw new Error('E_BAD');
  const flavor = v.getUint32(4), n = v.getUint16(12), tables = [];
  for (let i = 0; i < n; i++) {
    const e = 44 + i * 20, off = v.getUint32(e + 4), clen = v.getUint32(e + 8), olen = v.getUint32(e + 12);
    const src = b.subarray(off, off + clen);
    tables.push({ tag: v.getUint32(e), sum: v.getUint32(e + 16), data: clen < olen ? await inflateZlib(src) : src });
  }
  let es = 0; while ((1 << (es + 1)) <= n) es++;
  const sr = (1 << es) * 16;
  let off = 12 + 16 * n; tables.forEach(t => { t.off = off; off += (t.data.length + 3) & ~3; });
  const w = new Writer(off);
  w.u32be(flavor); w.u16be(n); w.u16be(sr); w.u16be(es); w.u16be(n * 16 - sr);
  for (const t of tables) { w.u32be(t.tag); w.u32be(t.sum); w.u32be(t.off); w.u32be(t.data.length); }
  for (const t of tables) { w.bytes(t.data); w.zeros(((t.data.length + 3) & ~3) - t.data.length); }
  return { bytes: w.result(), ext: flavor === 0x4F54544F ? 'otf' : 'ttf' };
}

const Codecs = { flatten, quantize, encodeGIF, encodeBMP, encodeICO, curToIco, encodeTIFF, decodeTIFF, encodeTGA, decodeTGA,
  encodePSD, decodePSD, encodeDDS, decodeDDS, encodeSGI, decodeSGI, encodeXPM, decodeXPM, encodePDF, encodeSVG,
  pathsToSVG, decodeDST, decodeEXP, decodePES, decodePCS, decodePLT, decodeDXF, sfntToWoff, woffToSfnt };
if (typeof module !== 'undefined' && module.exports) module.exports = Codecs; else root.Codecs = Codecs;
})(typeof window !== 'undefined' ? window : globalThis);
