/* PicShifter OCR engine (written for PicShifter, no third-party OCR code).
   Steps: grey → local threshold → connected pieces → text lines → candidate characters →
   glyph features (8-direction gradient histograms) → linear projection (LDA) → nearest
   character → best split of each line by dynamic programming → text.
   The character model (ocr-model.bin) was trained from rendered fonts for Korean (KS X 1001 Hangul,
   compatibility jamo), English letters, digits and common symbols. */
(function (root) {
'use strict';

var M = null; /* model */
function load(buf, meta) {
  var dim = meta.dim, D = meta.D, C = meta.classes, o = 0;
  function f32(n) { var a = new Float32Array(buf.slice(o, o + n * 4)); o += n * 4; return a; }
  var mu = f32(dim), W = f32(dim * D), sc = f32(D);
  var q = new Int8Array(buf.slice(o, o + C * D)); o += C * D;
  var P = new Float32Array(C * D), PP = new Float32Array(C);
  for (var c = 0; c < C; c++) { var s = 0; for (var d = 0; d < D; d++) { var v = q[c * D + d] * sc[d]; P[c * D + d] = v; s += v * v; } PP[c] = s; }
  M = { dim: dim, D: D, C: C, mu: mu, W: W, P: P, PP: PP, chars: Array.from(meta.chars), med: meta.medDist };
  M.skip = M.chars.map(function (ch) { return '■●▲★'.indexOf(ch) >= 0; });
}

/* ---------- glyph features (must match feat.py) ---------- */
var S = 32, BOX = 28, SUB = 4, G = 8, CELL = S / G;
function normalize(ink, w, h) {
  var out = new Float32Array(S * S), s = BOX / Math.max(h, w);
  var nw = Math.max(1, Math.round(w * s)), nh = Math.max(1, Math.round(h * s));
  var x0 = (S - nw) >> 1, y0 = (S - nh) >> 1;
  for (var ty = 0; ty < nh; ty++) for (var tx = 0; tx < nw; tx++) {
    var acc = 0;
    for (var a = 0; a < SUB; a++) {
      var yy = Math.min(h - 1, Math.floor((ty + (a + 0.5) / SUB) * (h / nh)));
      for (var b = 0; b < SUB; b++) {
        var xx = Math.min(w - 1, Math.floor((tx + (b + 0.5) / SUB) * (w / nw)));
        acc += ink[yy * w + xx];
      }
    }
    out[(y0 + ty) * S + x0 + tx] = acc / (SUB * SUB);
  }
  return out;
}
function gradFeat(P) {
  var F = new Float32Array(G * G * 8), TWO_PI = Math.PI * 2;
  for (var y = 0; y < S; y++) for (var x = 0; x < S; x++) {
    var r = x + 1 < S ? P[y * S + x + 1] : 0, l = x > 0 ? P[y * S + x - 1] : 0;
    var dn = y + 1 < S ? P[(y + 1) * S + x] : 0, up = y > 0 ? P[(y - 1) * S + x] : 0;
    var gx = r - l, gy = dn - up, mag = Math.sqrt(gx * gx + gy * gy);
    if (!mag) continue;
    var ang = Math.atan2(gy, gx); if (ang < 0) ang += TWO_PI;
    var bf = ang / TWO_PI * 8, b0f = Math.floor(bf), fr = bf - b0f, b0 = ((b0f % 8) + 8) % 8, b1 = (b0 + 1) % 8;
    var cy = (y + 0.5) / CELL - 0.5, cx = (x + 0.5) / CELL - 0.5, y0 = Math.floor(cy), x0 = Math.floor(cx), ty = cy - y0, tx = cx - x0;
    for (var dy = 0; dy < 2; dy++) {
      var yy = y0 + dy, wy = dy ? ty : 1 - ty; if (yy < 0 || yy >= G) continue;
      for (var dx = 0; dx < 2; dx++) {
        var xx = x0 + dx, wx = dx ? tx : 1 - tx; if (xx < 0 || xx >= G) continue;
        var base = (yy * G + xx) * 8, m = mag * wy * wx;
        F[base + b0] += m * (1 - fr); F[base + b1] += m * fr;
      }
    }
  }
  var n = 0; for (var i = 0; i < F.length; i++) { F[i] = Math.sqrt(F[i]); n += F[i] * F[i]; }
  n = Math.sqrt(n) + 1e-6; for (i = 0; i < F.length; i++) F[i] /= n;
  return F;
}
function features(ink, w, h, top, bottom, left, right, T0, H0) {
  var g = gradFeat(normalize(ink, w, h)), f = new Float32Array(g.length + 4);
  f.set(g); f[g.length] = (right - left) / H0; f[g.length + 1] = (bottom - top) / H0; f[g.length + 2] = (top - T0) / H0; f[g.length + 3] = (bottom - T0) / H0;
  return f;
}
/* squared distance to every character prototype */
function ldaAll(f) {
  var D = M.D, dim = M.dim, z = new Float32Array(D), zz = 0, i, k, out = new Float32Array(M.C);
  for (i = 0; i < dim; i++) { var v = f[i] - M.mu[i]; if (!v) continue; var row = i * D; for (k = 0; k < D; k++) z[k] += v * M.W[row + k]; }
  for (k = 0; k < D; k++) zz += z[k] * z[k];
  for (var c = 0; c < M.C; c++) { var dot = 0, p = c * D; for (k = 0; k < D; k++) dot += z[k] * M.P[p + k]; out[c] = Math.max(0, zz - 2 * dot + M.PP[c]); }
  return out;
}
/* returns {c: index, d: distance, d2: second-best distance} */
function classify(f) {
  var D = M.D, dim = M.dim, z = new Float32Array(D), zz = 0, i, k;
  for (i = 0; i < dim; i++) { var v = f[i] - M.mu[i]; if (!v) continue; var row = i * D; for (k = 0; k < D; k++) z[k] += v * M.W[row + k]; }
  for (k = 0; k < D; k++) zz += z[k] * z[k];
  var best = 1e30, bi = 0, second = 1e30;
  for (var c = 0; c < M.C; c++) {
    if (M.skip[c]) continue;
    var dot = 0, p = c * D; for (k = 0; k < D; k++) dot += z[k] * M.P[p + k];
    var d2 = zz - 2 * dot + M.PP[c];
    if (d2 < best) { second = best; best = d2; bi = c; } else if (d2 < second) second = d2;
  }
  return { c: bi, d: Math.sqrt(Math.max(0, best)), d2: Math.sqrt(Math.max(0, second)) };
}

/* ---------- small convolutional network (trained for PicShifter, see _build/ocr-training) ----------
   32×32 glyph + 4 position numbers → conv3×3(16) → pool → conv3×3(32) → pool → conv3×3(64) → pool
   → 256 → one score per character. Weights are stored as 8-bit numbers with one scale per output. */
var N = null, SCALE = 1;
function loadNet(buf, meta) {
  var o = 0, L = {};
  function f32(n) { var a = new Float32Array(buf.slice(o, o + n * 4)); o += n * 4; return a; }
  meta.layers.forEach(function (l) { L[l.name] = { rows: l.rows, cols: l.cols, sc: f32(l.cols), b: f32(l.cols) }; });
  meta.layers.forEach(function (l) {
    var q = new Int8Array(buf.slice(o, o + l.rows * l.cols)); o += l.rows * l.cols;
    var W = new Float32Array(l.rows * l.cols), sc = L[l.name].sc;
    for (var r = 0; r < l.rows; r++) for (var c = 0; c < l.cols; c++) W[r * l.cols + c] = q[r * l.cols + c] * sc[c];
    L[l.name].W = W;
  });
  N = L;
}
/* 3×3 convolution with zero padding, then ReLU and 2×2 max-pool. a: H×W×C (row-major, channels last) */
function convPool(a, H, W, C, layer) {
  var K = layer.W, b = layer.b, O = layer.cols, z = new Float32Array(H * W * O);
  for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
    var zo = (y * W + x) * O;
    for (var o = 0; o < O; o++) z[zo + o] = b[o];
    for (var i = 0; i < 3; i++) {
      var yy = y + i - 1; if (yy < 0 || yy >= H) continue;
      for (var j = 0; j < 3; j++) {
        var xx = x + j - 1; if (xx < 0 || xx >= W) continue;
        var ai = (yy * W + xx) * C, kr = (i * 3 + j) * C;
        for (var c = 0; c < C; c++) {
          var v = a[ai + c]; if (!v) continue;
          var kb = (kr + c) * O;
          for (o = 0; o < O; o++) z[zo + o] += v * K[kb + o];
        }
      }
    }
  }
  var h2 = H >> 1, w2 = W >> 1, out = new Float32Array(h2 * w2 * O);
  for (y = 0; y < h2; y++) for (x = 0; x < w2; x++) for (o = 0; o < O; o++) {
    var m = 0, p;
    p = z[((2 * y) * W + 2 * x) * O + o]; if (p > m) m = p;
    p = z[((2 * y) * W + 2 * x + 1) * O + o]; if (p > m) m = p;
    p = z[((2 * y + 1) * W + 2 * x) * O + o]; if (p > m) m = p;
    p = z[((2 * y + 1) * W + 2 * x + 1) * O + o]; if (p > m) m = p;
    out[(y * w2 + x) * O + o] = m;
  }
  return out;
}
function dense(v, layer, relu) {
  var R = layer.rows, O = layer.cols, K = layer.W, out = new Float32Array(O);
  out.set(layer.b);
  for (var r = 0; r < R; r++) { var x = v[r]; if (!x) continue; var kb = r * O; for (var o = 0; o < O; o++) out[o] += x * K[kb + o]; }
  if (relu) for (o = 0; o < O; o++) if (out[o] < 0) out[o] = 0;
  return out;
}
/* returns {c: index, p: probability, nll: -log probability} */
function netClassify(P, geo) {
  var a = convPool(P, 32, 32, 1, N.k1);
  a = convPool(a, 16, 16, 16, N.k2);
  a = convPool(a, 8, 8, 32, N.k3);
  var flat = new Float32Array(a.length + 4); flat.set(a); flat.set(geo, a.length);
  var s = dense(dense(flat, N.w4, true), N.w5, false), mx = -1e30, bi = 0, c;
  for (c = 0; c < s.length; c++) if (!M.skip[c] && s[c] > mx) { mx = s[c]; bi = c; }
  var sum = 0; for (c = 0; c < s.length; c++) if (!M.skip[c]) sum += Math.exp(s[c] - mx);
  return { c: bi, p: 1 / sum, nll: Math.log(sum), s: s, mx: mx, lse: mx + Math.log(sum) };
}

/* ---------- character counts from PicShifter's own text (which characters are common, which follow which) ---------- */
var L = null, LDAT = 0.5;
function ldaT() { return (root.PicOCR && root.PicOCR.ldaT) || LDAT; }
function loadLM(j) {
  var C = j.uni.length, tot = 0, uni = new Float64Array(C);
  for (var c = 0; c < C; c++) { uni[c] = j.uni[c]; tot += uni[c]; }
  var pu = new Float32Array(C); for (c = 0; c < C; c++) pu[c] = (uni[c] + 0.3) / (tot + 0.3 * C);
  var bi = new Map(); j.bi.forEach(function (p) { bi.set(p[0], p[1]); });
  L = { C: C, uni: uni, pu: pu, bi: bi };
}
/* log P(character c | previous character p); p = -1 means start of a word */
function lmP(p, c) {
  var pu = L.pu[c];
  if (p < 0) return Math.log(pu);
  var n = L.uni[p], k = 20, b = L.bi.get(p * L.C + c) || 0;
  return Math.log((b + k * pu) / (n + k));
}

/* ---------- image → binary ink map ---------- */
function toGray(rgba, w, h) { var g = new Float32Array(w * h); for (var i = 0; i < w * h; i++) g[i] = 0.299 * rgba[i * 4] + 0.587 * rgba[i * 4 + 1] + 0.114 * rgba[i * 4 + 2]; return g; }
function otsu(g) {
  var hist = new Float64Array(256); for (var i = 0; i < g.length; i++) hist[Math.max(0, Math.min(255, g[i] | 0))]++;
  var tot = g.length, sum = 0; for (i = 0; i < 256; i++) sum += i * hist[i];
  var sB = 0, wB = 0, best = 0, th = 128;
  for (i = 0; i < 256; i++) { wB += hist[i]; if (!wB) continue; var wF = tot - wB; if (!wF) break; sB += i * hist[i]; var mB = sB / wB, mF = (sum - sB) / wF, v = wB * wF * (mB - mF) * (mB - mF); if (v > best) { best = v; th = i; } }
  return th;
}
/* Sauvola local threshold with integral images; ink = 1 */
function binarize(g, w, h) {
  var th = otsu(g), dark = 0; for (var i = 0; i < g.length; i++) if (g[i] < th) dark++;
  if (dark > g.length / 2) for (i = 0; i < g.length; i++) g[i] = 255 - g[i]; /* light text on dark background */
  var W1 = w + 1, I = new Float64Array(W1 * (h + 1)), I2 = new Float64Array(W1 * (h + 1));
  for (var y = 0; y < h; y++) { var rs = 0, rs2 = 0; for (var x = 0; x < w; x++) { var v = g[y * w + x]; rs += v; rs2 += v * v; I[(y + 1) * W1 + x + 1] = I[y * W1 + x + 1] + rs; I2[(y + 1) * W1 + x + 1] = I2[y * W1 + x + 1] + rs2; } }
  var r = Math.max(7, Math.round(Math.min(w, h) / 50)), out = new Uint8Array(w * h), k = (root.PicOCR && root.PicOCR.binK) || 0.2, R = 128;
  for (y = 0; y < h; y++) {
    var y0 = Math.max(0, y - r), y1 = Math.min(h, y + r + 1);
    for (x = 0; x < w; x++) {
      var x0 = Math.max(0, x - r), x1 = Math.min(w, x + r + 1), n = (y1 - y0) * (x1 - x0);
      var s = I[y1 * W1 + x1] - I[y0 * W1 + x1] - I[y1 * W1 + x0] + I[y0 * W1 + x0];
      var s2 = I2[y1 * W1 + x1] - I2[y0 * W1 + x1] - I2[y1 * W1 + x0] + I2[y0 * W1 + x0];
      var m = s / n, sd = Math.sqrt(Math.max(0, s2 / n - m * m));
      var t = m * (1 + k * (sd / R - 1));
      out[y * w + x] = (g[y * w + x] < t && g[y * w + x] < th + 40 && sd > 6) ? 1 : 0;
    }
  }
  return out;
}

/* 8-connected components with bounding boxes */
function components(bin, w, h) {
  var lab = new Int32Array(w * h), parent = [0], next = 1;
  function find(a) { while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; } return a; }
  function uni(a, b) { a = find(a); b = find(b); if (a !== b) parent[Math.max(a, b)] = Math.min(a, b); }
  for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
    var i = y * w + x; if (!bin[i]) continue;
    var ls = [];
    if (x > 0 && lab[i - 1]) ls.push(lab[i - 1]);
    if (y > 0) { if (lab[i - w]) ls.push(lab[i - w]); if (x > 0 && lab[i - w - 1]) ls.push(lab[i - w - 1]); if (x < w - 1 && lab[i - w + 1]) ls.push(lab[i - w + 1]); }
    if (!ls.length) { parent.push(next); lab[i] = next++; }
    else { var m = ls[0]; for (var j = 1; j < ls.length; j++) { if (ls[j] < m) m = ls[j]; } lab[i] = m; for (j = 0; j < ls.length; j++) uni(m, ls[j]); }
  }
  var map = new Int32Array(next), comps = [];
  for (var l = 1; l < next; l++) { var rt = find(l); if (!map[rt]) { map[rt] = comps.length + 1; comps.push({ x0: 1e9, y0: 1e9, x1: -1, y1: -1, n: 0 }); } map[l] = map[rt]; }
  for (i = 0; i < w * h; i++) if (lab[i]) { var id = map[lab[i]]; lab[i] = id; var c = comps[id - 1], xx = i % w, yy = (i / w) | 0; c.n++; if (xx < c.x0) c.x0 = xx; if (xx > c.x1) c.x1 = xx; if (yy < c.y0) c.y0 = yy; if (yy > c.y1) c.y1 = yy; }
  comps.forEach(function (c, k) { c.id = k + 1; c.x1++; c.y1++; });
  return { lab: lab, comps: comps };
}

function median(a) { if (!a.length) return 0; var s = a.slice().sort(function (p, q) { return p - q; }); return s[s.length >> 1]; }

/* group components into text lines */
function lines(comps, w, h) {
  var cs = comps.filter(function (c) { var cw = c.x1 - c.x0, ch = c.y1 - c.y0; return c.n >= 2 && ch < h * 0.6 && cw < w * 0.8 && !(ch > 6 * cw && ch > 80); });
  var big = cs.filter(function (c) { return (c.y1 - c.y0) >= 6; });
  var mh = median(big.map(function (c) { return c.y1 - c.y0; })) || 10;
  var seeds = big.filter(function (c) { return (c.y1 - c.y0) >= mh * 0.45; }).sort(function (a, b) { return (a.y0 + a.y1) - (b.y0 + b.y1); });
  var L = [];
  seeds.forEach(function (c) {
    var cy = (c.y0 + c.y1) / 2, best = null, bo = 0;
    L.forEach(function (l) {
      var ov = Math.min(l.y1, c.y1) - Math.max(l.y0, c.y0), hgt = Math.min(l.y1 - l.y0, c.y1 - c.y0);
      if (ov > 0.5 * hgt && cy > l.y0 - 2 && cy < l.y1 + 2 && ov / hgt > bo) { bo = ov / hgt; best = l; }
    });
    if (best) { best.items.push(c); best.y0 = Math.min(best.y0, c.y0); best.y1 = Math.max(best.y1, c.y1); }
    else L.push({ y0: c.y0, y1: c.y1, items: [c] });
  });
  /* attach small pieces (dots, commas, parts of jamo) to the closest line that contains them vertically */
  cs.forEach(function (c) {
    if (seeds.indexOf(c) >= 0) return;
    var cy = (c.y0 + c.y1) / 2, best = null, bd = 1e9;
    L.forEach(function (l) { var hh = l.y1 - l.y0, d = cy < l.y0 ? l.y0 - cy : cy > l.y1 ? cy - l.y1 : 0; if (d < hh * 0.35 && d < bd) { bd = d; best = l; } });
    if (best) best.items.push(c);
  });
  L.sort(function (a, b) { return a.y0 - b.y0; });
  return L;
}

/* split a line into characters with dynamic programming over candidate cuts */
function readLine(line, lab, w) {
  var items = line.items.slice().sort(function (a, b) { return a.x0 - b.x0; });
  /* pieces: components that overlap horizontally belong together */
  var pieces = [];
  items.forEach(function (c) {
    var p = pieces.length ? pieces[pieces.length - 1] : null;
    var cw = c.x1 - c.x0, small = (c.y1 - c.y0) < 0.4 * (line.y1 - line.y0) && cw < 0.3 * (line.y1 - line.y0) && c.y0 > line.y0 + 0.55 * (line.y1 - line.y0);
    var ovl = p ? p.x1 - c.x0 : 0;
    if (p && c.x0 < p.x1 - Math.min(2, cw * 0.3) && (!small || ovl > 0.6 * cw)) { p.x1 = Math.max(p.x1, c.x1); p.y0 = Math.min(p.y0, c.y0); p.y1 = Math.max(p.y1, c.y1); p.cs.push(c); }
    else pieces.push({ x0: c.x0, x1: c.x1, y0: c.y0, y1: c.y1, cs: [c] });
  });
  if (!pieces.length) return '';
  var maxH = Math.max.apply(null, pieces.map(function (p) { return p.y1 - p.y0; }));
  var tall = pieces.filter(function (p) { return (p.y1 - p.y0) >= 0.55 * maxH; });
  var T0 = median(tall.map(function (p) { return p.y0; })), B0 = median(tall.map(function (p) { return p.y1; })), H0 = Math.max(4, B0 - T0);
  /* touching letters (e.g. "ft", "xj"): offer cuts at thin columns inside wide pieces; the DP below can still keep them together */
  var LH = line.y1 - line.y0, split = [];
  pieces.forEach(function (p) {
    var pw = p.x1 - p.x0;
    if (pw < 0.7 * LH) { split.push(p); return; }
    var ids = {}; p.cs.forEach(function (c) { ids[c.id] = 1; });
    var col = new Int32Array(pw);
    for (var yy = p.y0; yy < p.y1; yy++) for (var xx = p.x0; xx < p.x1; xx++) { var l = lab[yy * w + xx]; if (l && ids[l]) col[xx - p.x0]++; }
    var cuts = [], margin = Math.max(2, Math.round(0.18 * LH)), thin = Math.max(1, Math.round(0.1 * LH));
    for (var x = margin; x < pw - margin; x++) {
      if (col[x] <= thin && col[x] <= col[x - 1] && col[x] <= col[x + 1] && (!cuts.length || x - cuts[cuts.length - 1] > margin)) cuts.push(x);
    }
    if (!cuts.length) { split.push(p); return; }
    var start = 0; cuts.concat([pw]).forEach(function (cx) {
      var y0 = 1e9, y1 = -1;
      for (var yy = p.y0; yy < p.y1; yy++) for (var xx = p.x0 + start; xx < p.x0 + cx; xx++) { var l = lab[yy * w + xx]; if (l && ids[l]) { if (yy < y0) y0 = yy; if (yy + 1 > y1) y1 = yy + 1; } }
      if (y1 > y0) split.push({ x0: p.x0 + start, x1: p.x0 + cx, y0: y0, y1: y1, cs: p.cs, cut: start > 0, sub: true });
      start = cx;
    });
  });
  pieces = split;
  var n = pieces.length, cache = {};
  var NETDP = !!(root.PicOCR && root.PicOCR.netDP), NW = (root.PicOCR && root.PicOCR.nw) || 0.5;
  function seg(i, j) {
    var key = i + ',' + j; if (cache[key]) return cache[key];
    var x0 = 1e9, x1 = -1, y0 = 1e9, y1 = -1, ids = {};
    for (var k = i; k <= j; k++) { var p = pieces[k]; x0 = Math.min(x0, p.x0); x1 = Math.max(x1, p.x1); y0 = Math.min(y0, p.y0); y1 = Math.max(y1, p.y1); p.cs.forEach(function (c) { ids[c.id] = 1; }); }
    var gw = x1 - x0, gh = y1 - y0, ink = new Float32Array(gw * gh);
    for (var yy = 0; yy < gh; yy++) for (var xx = 0; xx < gw; xx++) { var l = lab[(y0 + yy) * w + x0 + xx]; if (l && ids[l]) ink[yy * gw + xx] = 1; }
    var fv = features(ink, gw, gh, y0, y1, x0, x1, T0, H0), r = classify(fv); r.f = fv;
    r.x0 = x0; r.x1 = x1; r.y0 = y0; r.y1 = y1;
    r.ink = ink; r.gw = gw; r.gh = gh; r.geo = [(x1 - x0) / H0, (y1 - y0) / H0, (y0 - T0) / H0, (y1 - T0) / H0];
    if (N && NETDP) { var t = netClassify(normalize(ink, gw, gh), r.geo); r.nc = t.c; r.nll = t.nll; }
    cache[key] = r; return r;
  }
  var best = new Float64Array(n + 1).fill(1e30), from = new Int32Array(n + 1).fill(-1); best[0] = 0;
  var LAMBDA = (root.PicOCR && root.PicOCR.lambda) || 0.4, CUT = (root.PicOCR && root.PicOCR.cut != null) ? root.PicOCR.cut : 0.6;
  for (var j = 0; j < n; j++) {
    for (var i = j; i >= 0 && j - i < 4; i--) {
      var width = pieces[j].x1 - pieces[i].x0;
      if (i < j && width > 1.5 * H0) break;
      if (i < j && pieces[i + 1].x0 - pieces[i].x1 > 0.35 * H0) break;
      /* every gap inside the candidate must be small */
      var okGap = true; for (var k = i; k < j; k++) if (pieces[k + 1].x0 - pieces[k].x1 > 0.3 * H0) { okGap = false; break; }
      /* periods and commas (small marks sitting low) are never part of a bigger character */
      if (okGap && i < j) for (k = i; k <= j; k++) { var pk = pieces[k]; if (!pk.sub && (pk.y1 - pk.y0) < 0.42 * H0 && (pk.x1 - pk.x0) < 0.3 * H0 && (pk.y0 > T0 + 0.55 * H0 || pk.y1 < T0 + 0.5 * H0)) { okGap = false; break; } }
      if (!okGap) break;
      if (best[i] >= 1e30) continue;
      var r = seg(i, j), q = r.d / M.med, cost = best[i] + (r.nll != null ? NW * Math.min(r.nll, 6) : q * q) + LAMBDA + (pieces[i].cut ? CUT : 0) + (j + 1 < n && pieces[j + 1].cut ? CUT : 0);
      if (cost < best[j + 1]) { best[j + 1] = cost; from[j + 1] = i; }
    }
  }
  var segs = [], at = n;
  while (at > 0) { var i0 = from[at]; if (i0 < 0) { i0 = at - 1; } segs.push(seg(i0, at - 1)); at = i0; }
  segs.reverse();
  /* score of every character for each chosen piece (log-probability): the network and the prototypes together */
  var BETA = (root.PicOCR && root.PicOCR.beta != null) ? root.PicOCR.beta : 4, med2 = M.med * M.med;
  function scores(sg) {
    if (sg.lp) return sg.lp;
    var d2 = ldaAll(sg.f), t = N ? netClassify(normalize(sg.ink, sg.gw, sg.gh), sg.geo) : null, lp = new Float32Array(M.C), mx = -1e30, c;
    for (c = 0; c < M.C; c++) { lp[c] = M.skip[c] ? -1e9 : (t ? t.s[c] - BETA * d2[c] / med2 : -ldaT() * d2[c] / med2); if (lp[c] > mx) mx = lp[c]; }
    var sum = 0; for (c = 0; c < M.C; c++) sum += Math.exp(lp[c] - mx);
    var z = mx + Math.log(sum); for (c = 0; c < M.C; c++) lp[c] -= z;
    sg.lp = lp; return lp;
  }
  if (N || L) segs.forEach(function (sg) { var lp = scores(sg), b = 0; for (var c = 1; c < M.C; c++) if (lp[c] > lp[b]) b = c; sg.c = b; });
  var gaps = []; for (var s = 1; s < segs.length; s++) gaps.push(segs[s].x0 - segs[s - 1].x1);
  var mg = median(gaps.filter(function (g) { return g >= 0; }));
  /* word spaces: split the gaps into "small" and "large" groups (Otsu on gap sizes) */
  var spaceAt = 0.35 * H0, gs = gaps.filter(function (g) { return g >= 0; }).sort(function (p, q) { return p - q; });
  if (gs.length >= 2) {
    var bestV = -1, cut = -1, tot = gs.reduce(function (a, b) { return a + b; }, 0), acc = 0;
    for (var gi = 0; gi < gs.length - 1; gi++) {
      acc += gs[gi]; var n1 = gi + 1, n2 = gs.length - n1, m1 = acc / n1, m2 = (tot - acc) / n2, v = n1 * n2 * (m2 - m1) * (m2 - m1);
      if (gs[gi + 1] > gs[gi] && v > bestV) { bestV = v; cut = gi; }
    }
    if (cut >= 0) {
      var small = gs.slice(0, cut + 1), large = gs.slice(cut + 1);
      var ms = small.reduce(function (a, b) { return a + b; }, 0) / small.length, ml = large.reduce(function (a, b) { return a + b; }, 0) / large.length;
      if (large[0] >= 0.18 * H0 && ml >= 1.5 * Math.max(1, ms)) spaceAt = (gs[cut] + gs[cut + 1]) / 2;
    }
  }
  /* sentence context: pick the most likely chain of characters (Viterbi over the top guesses of each piece) */
  if (L && segs.length) {
    var GAMMA = (root.PicOCR && root.PicOCR.gamma != null) ? root.PicOCR.gamma : 0.5, K = 6, prevC = null, prevV = null, back = [];
    segs.forEach(function (sg, k) {
      var lp = scores(sg), idx = [];
      for (var c = 0; c < M.C; c++) if (lp[c] > -12) idx.push(c);
      idx.sort(function (a, b) { return lp[b] - lp[a]; }); idx = idx.slice(0, K); if (!idx.length) idx = [sg.c];
      var sp = k && sg.x0 - segs[k - 1].x1 > spaceAt, V = [], B = [];
      idx.forEach(function (c) {
        if (!prevC) { V.push(lp[c] + GAMMA * lmP(-1, c)); B.push(-1); return; }
        var bv = -1e30, bi = 0;
        for (var q = 0; q < prevC.length; q++) { var v = prevV[q] + GAMMA * lmP(sp ? -1 : prevC[q], c); if (v > bv) { bv = v; bi = q; } }
        V.push(lp[c] + bv); B.push(bi);
      });
      back.push({ c: idx, b: B }); prevC = idx; prevV = V;
    });
    var at = 0; for (var q = 1; q < prevV.length; q++) if (prevV[q] > prevV[at]) at = q;
    for (var k2 = segs.length - 1; k2 >= 0; k2--) { segs[k2].c = back[k2].c[at]; at = back[k2].b[at]; }
  }
  var out = '';
  if (root.PicOCR && root.PicOCR.onSeg) segs.forEach(function (sg) { root.PicOCR.onSeg(sg, M.chars[sg.c], SCALE); });
  segs.forEach(function (sgm, k) { if (k && sgm.x0 - segs[k - 1].x1 > spaceAt) out += ' '; out += M.chars[sgm.c]; });
  return out;
}

/* main entry: rgba Uint8ClampedArray, w, h → text */
function upscale(rgba, w, h, k) {
  var W = Math.round(w * k), H = Math.round(h * k), o = new Uint8ClampedArray(W * H * 4);
  for (var y = 0; y < H; y++) {
    var fy = Math.max(0, Math.min(h - 1, (y + 0.5) / k - 0.5)), y0 = fy | 0, y1 = Math.min(h - 1, y0 + 1), ty = fy - y0;
    for (var x = 0; x < W; x++) {
      var fx = Math.max(0, Math.min(w - 1, (x + 0.5) / k - 0.5)), x0 = fx | 0, x1 = Math.min(w - 1, x0 + 1), tx = fx - x0;
      for (var c = 0; c < 4; c++) {
        var a = rgba[(y0 * w + x0) * 4 + c], b = rgba[(y0 * w + x1) * 4 + c], d = rgba[(y1 * w + x0) * 4 + c], e = rgba[(y1 * w + x1) * 4 + c];
        o[(y * W + x) * 4 + c] = (a + (b - a) * tx) * (1 - ty) + (d + (e - d) * tx) * ty;
      }
    }
  }
  return { rgba: o, w: W, h: H };
}
function recognize(rgba, w, h, onProgress) {
  if (!M) throw new Error('model');
  /* small text: enlarge first so letters have enough pixels */
  var g0 = toGray(rgba, w, h), cc0 = components(binarize(g0, w, h), w, h), ls0 = lines(cc0.comps, w, h);
  var lh = median(ls0.map(function (l) { return l.y1 - l.y0; }));
  SCALE = 1;
  if (lh && lh < 18 && w * h < 4e6) { var k = Math.min(3, Math.ceil(26 / lh)); var u = upscale(rgba, w, h, k); rgba = u.rgba; w = u.w; h = u.h; SCALE = k; }
  var g = toGray(rgba, w, h);
  var bin = binarize(g, w, h);
  var cc = components(bin, w, h);
  var ls = lines(cc.comps, w, h), out = [];
  for (var i = 0; i < ls.length; i++) { out.push(readLine(ls[i], cc.lab, w)); if (onProgress) onProgress((i + 1) / ls.length); }
  return out.filter(function (s) { return s.trim().length; }).join('\n');
}

root.PicOCR = { load: load, loadNet: loadNet, loadLM: loadLM, recognize: recognize, _features: features, _classify: classify, _net: function (P, g) { return netClassify(P, g); }, _ldaAll: function (f) { return ldaAll(f); }, _M: function () { return M; }, _norm: normalize };
if (typeof module !== 'undefined') module.exports = root.PicOCR;
})(typeof self !== 'undefined' ? self : this);
