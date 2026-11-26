/* PicShifter patch-based fill (written for PicShifter).
   Refines an AI-filled hole by rebuilding it from real texture patches copied from the rest of the
   photo, coarse-to-fine (in the spirit of Wexler et al. 2007 "Space-time completion" with
   PatchMatch nearest-neighbour search, Barnes et al. 2009). The AI result is used as the starting
   guess, so the overall layout comes from the AI and the fine texture comes from the photo itself.

   fill(rgb, w, h, hole, init, opts) -> Float32Array rgb
     rgb  : Float32Array(w*h*3), the photo area (values 0..255)
     hole : Uint8Array(w*h), 1 = pixel to rebuild
     init : Float32Array(w*h*3), starting guess for the hole (e.g. the AI output), same layout
*/
(function (root) {
'use strict';

function rand(seed) { var s = seed >>> 0 || 1; return function () { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return (s >>> 0) / 4294967296; }; }

/* 2× smaller: known pixels averaged from known pixels only; a pixel is a hole if any of its 4 children is. */
function down(img, w, h, hole) {
  var W = Math.max(1, w >> 1), H = Math.max(1, h >> 1), o = new Float32Array(W * H * 3), m = new Uint8Array(W * H);
  for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
    var r = 0, g = 0, b = 0, n = 0, any = 0, r2 = 0, g2 = 0, b2 = 0;
    for (var dy = 0; dy < 2; dy++) for (var dx = 0; dx < 2; dx++) {
      var xx = Math.min(w - 1, 2 * x + dx), yy = Math.min(h - 1, 2 * y + dy), i = yy * w + xx;
      r2 += img[i * 3]; g2 += img[i * 3 + 1]; b2 += img[i * 3 + 2];
      if (hole[i]) any = 1; else { r += img[i * 3]; g += img[i * 3 + 1]; b += img[i * 3 + 2]; n++; }
    }
    var j = y * W + x;
    if (n) { o[j * 3] = r / n; o[j * 3 + 1] = g / n; o[j * 3 + 2] = b / n; } else { o[j * 3] = r2 / 4; o[j * 3 + 1] = g2 / 4; o[j * 3 + 2] = b2 / 4; }
    m[j] = any;
  }
  return { img: o, hole: m, w: W, h: H };
}

/* bilinear resize of an rgb float image */
function resize(src, w, h, W, H) {
  var o = new Float32Array(W * H * 3), sx = w / W, sy = h / H;
  for (var y = 0; y < H; y++) {
    var fy = Math.max(0, Math.min(h - 1, (y + 0.5) * sy - 0.5)), y0 = fy | 0, y1 = Math.min(h - 1, y0 + 1), ty = fy - y0;
    for (var x = 0; x < W; x++) {
      var fx = Math.max(0, Math.min(w - 1, (x + 0.5) * sx - 0.5)), x0 = fx | 0, x1 = Math.min(w - 1, x0 + 1), tx = fx - x0;
      for (var c = 0; c < 3; c++) {
        var a = src[(y0 * w + x0) * 3 + c], b = src[(y0 * w + x1) * 3 + c], d = src[(y1 * w + x0) * 3 + c], e = src[(y1 * w + x1) * 3 + c];
        o[(y * W + x) * 3 + c] = (a + (b - a) * tx) + ((d + (e - d) * tx) - (a + (b - a) * tx)) * ty;
      }
    }
  }
  return o;
}

function level(C, w, h, hole, nnf, iters, R, rnd, last, sharp) {
  var n = w * h, i, x, y;
  /* source centres: whole patch must be real (not hole) pixels */
  var valid = new Uint8Array(n), srcList = [];
  for (y = R; y < h - R; y++) for (x = R; x < w - R; x++) {
    var ok = 1;
    for (var dy = -R; dy <= R && ok; dy++) { var row = (y + dy) * w; for (var dx = -R; dx <= R; dx++) if (hole[row + x + dx]) { ok = 0; break; } }
    if (ok) { valid[y * w + x] = 1; srcList.push(y * w + x); }
  }
  if (!srcList.length) return null;
  var targets = []; for (i = 0; i < n; i++) if (hole[i]) targets.push(i);
  var T = targets.length, best = new Float32Array(n);
  /* fix up NNF entries that point to invalid sources */
  for (var k = 0; k < T; k++) { i = targets[k]; if (nnf[i] < 0 || !valid[nnf[i]]) nnf[i] = srcList[(rnd() * srcList.length) | 0]; }

  function dist(p, s, cut) {
    var px = p % w, py = (p / w) | 0, sx = s % w, sy = (s / w) | 0, d = 0, cnt = 0;
    for (var dy = -R; dy <= R; dy++) {
      var ty = py + dy; if (ty < 0 || ty >= h) continue;
      var srow = (sy + dy) * w, trow = ty * w;
      for (var dx = -R; dx <= R; dx++) {
        var tx = px + dx; if (tx < 0 || tx >= w) continue;
        var a = (trow + tx) * 3, b = (srow + sx + dx) * 3;
        var e0 = C[a] - C[b], e1 = C[a + 1] - C[b + 1], e2 = C[a + 2] - C[b + 2];
        d += e0 * e0 + e1 * e1 + e2 * e2; cnt++;
      }
      if (d > cut) return d;
    }
    return cnt ? d * ((2 * R + 1) * (2 * R + 1) / cnt) : 1e30;
  }
  var maxR = Math.max(w, h);
  for (var it = 0; it < iters; it++) {
    for (k = 0; k < T; k++) { i = targets[k]; best[i] = dist(i, nnf[i], 1e30); }
    for (var pass = 0; pass < 2; pass++) {
      var fwd = pass === 0, step = fwd ? 1 : -1;
      for (var q = 0; q < T; q++) {
        i = targets[fwd ? q : T - 1 - q];
        x = i % w; y = (i / w) | 0;
        /* propagation from the left/right and up/down neighbours */
        var nb = x - step, cand, d;
        if (nb >= 0 && nb < w && hole[i - step]) { cand = nnf[i - step] + step; if (valid[cand]) { d = dist(i, cand, best[i]); if (d < best[i]) { best[i] = d; nnf[i] = cand; } } }
        var nby = y - step;
        if (nby >= 0 && nby < h && hole[i - step * w]) { cand = nnf[i - step * w] + step * w; if (valid[cand]) { d = dist(i, cand, best[i]); if (d < best[i]) { best[i] = d; nnf[i] = cand; } } }
        /* random search around the current match */
        var cx = nnf[i] % w, cy = (nnf[i] / w) | 0;
        for (var rad = maxR; rad >= 1; rad >>= 1) {
          var rx = cx + Math.round((rnd() * 2 - 1) * rad), ry = cy + Math.round((rnd() * 2 - 1) * rad);
          if (rx < R || ry < R || rx >= w - R || ry >= h - R) continue;
          cand = ry * w + rx; if (!valid[cand]) continue;
          d = dist(i, cand, best[i]); if (d < best[i]) { best[i] = d; nnf[i] = cand; cx = rx; cy = ry; }
        }
      }
    }
    /* voting: every hole pixel becomes the weighted average of the patches that cover it */
    var acc = new Float32Array(n * 3), wsum = new Float32Array(n), P = (2 * R + 1) * (2 * R + 1);
    var sig = 0; for (k = 0; k < T; k++) sig += best[targets[k]]; sig = Math.max(1, sig / Math.max(1, T)) / P;
    for (k = 0; k < T; k++) {
      i = targets[k]; x = i % w; y = (i / w) | 0;
      var s = nnf[i], sx = s % w, sy = (s / w) | 0, wt = Math.exp(-best[i] / P / (2 * sig));
      if (last) wt = wt * wt;
      for (var dy2 = -R; dy2 <= R; dy2++) {
        var ty = y + dy2; if (ty < 0 || ty >= h) continue;
        for (var dx2 = -R; dx2 <= R; dx2++) {
          var tx = x + dx2; if (tx < 0 || tx >= w) continue;
          var t = ty * w + tx; if (!hole[t]) continue;
          var sp = ((sy + dy2) * w + sx + dx2) * 3;
          acc[t * 3] += C[sp] * wt; acc[t * 3 + 1] += C[sp + 1] * wt; acc[t * 3 + 2] += C[sp + 2] * wt; wsum[t] += wt;
        }
      }
    }
    for (k = 0; k < T; k++) { i = targets[k]; if (wsum[i] > 0) { C[i * 3] = acc[i * 3] / wsum[i]; C[i * 3 + 1] = acc[i * 3 + 1] / wsum[i]; C[i * 3 + 2] = acc[i * 3 + 2] / wsum[i]; } }
  }
  if (sharp) {
    /* final look-up: one more search on the averaged image, then copy each pixel straight from its best match (keeps texture crisp) */
    for (k = 0; k < T; k++) { i = targets[k]; best[i] = dist(i, nnf[i], 1e30); }
    var copy = new Float32Array(T * 3);
    for (k = 0; k < T; k++) { var s2 = nnf[targets[k]] * 3; copy[k * 3] = C[s2]; copy[k * 3 + 1] = C[s2 + 1]; copy[k * 3 + 2] = C[s2 + 2]; }
    for (k = 0; k < T; k++) { i = targets[k]; C[i * 3] = copy[k * 3]; C[i * 3 + 1] = copy[k * 3 + 1]; C[i * 3 + 2] = copy[k * 3 + 2]; }
  }
  return nnf;
}

function fill(rgb, w, h, hole, init, opts) {
  opts = opts || {};
  var R = opts.radius || 3, rnd = rand(opts.seed || 12345), coarse = opts.coarse || 100;
  if (!opts.coarseRadius) opts.coarseRadius = 6;
  if (!opts.midIters) opts.midIters = 6;
  if (opts.sharp === undefined) opts.sharp = true;
  if (opts.sharpAll === undefined) opts.sharpAll = true;
  /* pyramid of the real photo */
  var pyr = [{ img: rgb, hole: hole, w: w, h: h }];
  /* coarsest level: long side between `coarse` and 2×`coarse` pixels (about 100–200 worked best in tests) */
  while (Math.max(pyr[pyr.length - 1].w, pyr[pyr.length - 1].h) / 2 >= coarse && pyr.length < 8) {
    var t = pyr[pyr.length - 1]; pyr.push(down(t.img, t.w, t.h, t.hole));
  }
  var L = pyr.length - 1, top = pyr[L];
  /* starting guess at the coarsest level: the AI result, shrunk */
  var C = resize(init, w, h, top.w, top.h);
  for (var i = 0; i < top.w * top.h; i++) if (!top.hole[i]) { C[i * 3] = top.img[i * 3]; C[i * 3 + 1] = top.img[i * 3 + 1]; C[i * 3 + 2] = top.img[i * 3 + 2]; }
  var nnf = new Int32Array(top.w * top.h).fill(-1);
  for (var l = L; l >= 0; l--) {
    var cur = pyr[l];
    var iters = l === L ? (opts.coarseIters || 10) : l === 0 ? (opts.fineIters || 2) : (opts.midIters || 4);
    nnf = level(C, cur.w, cur.h, cur.hole, nnf, iters, l === 0 ? R : (opts.coarseRadius || R + 1), rnd, l === 0, l === 0 ? !!opts.sharp : !!opts.sharpAll);
    if (!nnf) return null;
    if (opts.onProgress) opts.onProgress((L - l + 1) / (L + 1));
    if (l > 0) {
      var nx = pyr[l - 1];
      var C2 = resize(C, cur.w, cur.h, nx.w, nx.h), nn2 = new Int32Array(nx.w * nx.h).fill(-1);
      for (var y = 0; y < nx.h; y++) for (var x = 0; x < nx.w; x++) {
        var j = y * nx.w + x;
        if (!nx.hole[j]) { C2[j * 3] = nx.img[j * 3]; C2[j * 3 + 1] = nx.img[j * 3 + 1]; C2[j * 3 + 2] = nx.img[j * 3 + 2]; continue; }
        var px = Math.min(cur.w - 1, x >> 1), py = Math.min(cur.h - 1, y >> 1), s = nnf[py * cur.w + px];
        if (s >= 0) { var sx = (s % cur.w) * 2 + (x & 1), sy = ((s / cur.w) | 0) * 2 + (y & 1); if (sx < nx.w && sy < nx.h) nn2[j] = sy * nx.w + sx; }
      }
      C = C2; nnf = nn2;
    }
  }
  return C;
}

root.PatchFill = { fill: fill };
if (typeof module !== 'undefined') module.exports = root.PatchFill;
})(typeof self !== 'undefined' ? self : this);
