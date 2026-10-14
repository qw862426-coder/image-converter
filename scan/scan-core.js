/* PicShifter scan engine: find the paper in a photo, flatten it, and clean it up like a scanner.
   Works on plain pixel objects {width, height, data: RGBA Uint8ClampedArray} so it runs in browsers and Node. */
(function (root) {
'use strict';

function newImg(w, h) { return { width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }; }

function toGray(img) {
  var n = img.width * img.height, g = new Float32Array(n), d = img.data;
  for (var i = 0; i < n; i++) g[i] = 0.299 * d[i * 4] + 0.587 * d[i * 4 + 1] + 0.114 * d[i * 4 + 2];
  return g;
}

/* Area-average resize of a single-channel float image. */
function shrink(src, w, h, nw, nh) {
  var out = new Float32Array(nw * nh), sx = w / nw, sy = h / nh;
  for (var y = 0; y < nh; y++) {
    var y0 = Math.floor(y * sy), y1 = Math.max(y0 + 1, Math.floor((y + 1) * sy));
    for (var x = 0; x < nw; x++) {
      var x0 = Math.floor(x * sx), x1 = Math.max(x0 + 1, Math.floor((x + 1) * sx)), s = 0, c = 0;
      for (var yy = y0; yy < y1 && yy < h; yy++) for (var xx = x0; xx < x1 && xx < w; xx++) { s += src[yy * w + xx]; c++; }
      out[y * nw + x] = c ? s / c : 0;
    }
  }
  return out;
}

function boxBlur(src, w, h, r) {
  var tmp = new Float32Array(w * h), out = new Float32Array(w * h);
  for (var y = 0; y < h; y++) {
    var s = 0, c = 0;
    for (var x = -r; x < w; x++) {
      if (x + r < w) { s += src[y * w + x + r]; c++; }
      if (x - r - 1 >= 0) { s -= src[y * w + x - r - 1]; c--; }
      if (x >= 0) tmp[y * w + x] = s / c;
    }
  }
  for (var x2 = 0; x2 < w; x2++) {
    var s2 = 0, c2 = 0;
    for (var y2 = -r; y2 < h; y2++) {
      if (y2 + r < h) { s2 += tmp[(y2 + r) * w + x2]; c2++; }
      if (y2 - r - 1 >= 0) { s2 -= tmp[(y2 - r - 1) * w + x2]; c2--; }
      if (y2 >= 0) out[y2 * w + x2] = s2 / c2;
    }
  }
  return out;
}

function maxFilter(src, w, h, r) {
  var tmp = new Float32Array(w * h), out = new Float32Array(w * h);
  for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
    var m = -1e9; for (var k = Math.max(0, x - r); k <= Math.min(w - 1, x + r); k++) if (src[y * w + k] > m) m = src[y * w + k];
    tmp[y * w + x] = m;
  }
  for (var x2 = 0; x2 < w; x2++) for (var y2 = 0; y2 < h; y2++) {
    var m2 = -1e9; for (var k2 = Math.max(0, y2 - r); k2 <= Math.min(h - 1, y2 + r); k2++) if (tmp[k2 * w + x2] > m2) m2 = tmp[k2 * w + x2];
    out[y2 * w + x2] = m2;
  }
  return out;
}

function otsu(values, lo, hi) {
  var hist = new Float64Array(256), n = 0;
  for (var i = 0; i < values.length; i++) { var v = values[i]; if (v < lo || v > hi) continue; hist[Math.max(0, Math.min(255, v | 0))]++; n++; }
  var sum = 0; for (var t = 0; t < 256; t++) sum += t * hist[t];
  var sumB = 0, wB = 0, best = 0, th = 128;
  for (var t2 = 0; t2 < 256; t2++) {
    wB += hist[t2]; if (!wB) continue; var wF = n - wB; if (!wF) break;
    sumB += t2 * hist[t2];
    var mB = sumB / wB, mF = (sum - sumB) / wF, between = wB * wF * (mB - mF) * (mB - mF);
    if (between > best) { best = between; th = t2; }
  }
  return th;
}

/* ---------- geometry ---------- */
function hull(pts) {
  pts = pts.slice().sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
  var cross = function (o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); };
  var lower = [], upper = [];
  for (var i = 0; i < pts.length; i++) { while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], pts[i]) <= 0) lower.pop(); lower.push(pts[i]); }
  for (var j = pts.length - 1; j >= 0; j--) { while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], pts[j]) <= 0) upper.pop(); upper.push(pts[j]); }
  upper.pop(); lower.pop(); return lower.concat(upper);
}
function polyArea(p) { var a = 0; for (var i = 0; i < p.length; i++) { var q = p[(i + 1) % p.length]; a += p[i][0] * q[1] - q[0] * p[i][1]; } return Math.abs(a) / 2; }
function triArea(a, b, c) { return Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2; }

/* Shrink a convex polygon to 4 corners by repeatedly dropping the vertex that removes the least area. */
function toQuad(p) {
  p = p.slice();
  while (p.length > 4) {
    var best = 0, bestA = Infinity;
    for (var i = 0; i < p.length; i++) {
      var a = triArea(p[(i - 1 + p.length) % p.length], p[i], p[(i + 1) % p.length]);
      if (a < bestA) { bestA = a; best = i; }
    }
    p.splice(best, 1);
  }
  return p;
}

/* Order 4 points as top-left, top-right, bottom-right, bottom-left. */
function orderQuad(q) {
  var cx = 0, cy = 0; q.forEach(function (p) { cx += p[0] / 4; cy += p[1] / 4; });
  var s = q.slice().sort(function (a, b) { return Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx); });
  var start = 0, m = Infinity;
  for (var i = 0; i < 4; i++) { var v = s[i][0] + s[i][1]; if (v < m) { m = v; start = i; } }
  return [s[start], s[(start + 1) % 4], s[(start + 2) % 4], s[(start + 3) % 4]];
}

function isConvex(q) {
  var sign = 0;
  for (var i = 0; i < 4; i++) {
    var a = q[i], b = q[(i + 1) % 4], c = q[(i + 2) % 4];
    var z = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]);
    if (z === 0) return false;
    if (!sign) sign = z > 0 ? 1 : -1; else if ((z > 0 ? 1 : -1) !== sign) return false;
  }
  return true;
}

/* Find the paper. Returns {quad:[[x,y]x4], found:boolean} in image pixels. */
function detectPaper(img) {
  var W = img.width, H = img.height, k = Math.min(1, 480 / Math.max(W, H));
  var w = Math.max(16, Math.round(W * k)), h = Math.max(16, Math.round(H * k));
  /* "Paper-ness": paper is light and nearly colourless, tables and floors are darker or more colourful. */
  var n0 = W * H, pv = new Float32Array(n0), d0 = img.data;
  for (var i0 = 0; i0 < n0; i0++) {
    var r0 = d0[i0 * 4], g0 = d0[i0 * 4 + 1], b0 = d0[i0 * 4 + 2];
    var mx = Math.max(r0, g0, b0), mn = Math.min(r0, g0, b0);
    pv[i0] = Math.max(0, Math.min(255, 0.299 * r0 + 0.587 * g0 + 0.114 * b0 - 1.5 * (mx - mn) + 40));
  }
  var g = boxBlur(shrink(pv, W, H, w, h), w, h, 2);
  var full = [[0, 0], [W, 0], [W, H], [0, H]];
  var best = null;
  /* Paper is usually brighter than what it lies on; also try the reverse for white desks. */
  var th = otsu(g, 0, 255);
  [true, false].forEach(function (bright) {
    var mask = new Uint8Array(w * h);
    for (var i = 0; i < w * h; i++) mask[i] = bright ? (g[i] > th ? 1 : 0) : (g[i] <= th ? 1 : 0);
    var label = new Int32Array(w * h).fill(-1), stack = [];
    for (var s = 0; s < w * h; s++) {
      if (!mask[s] || label[s] >= 0) continue;
      var pts = [], touch = 0; stack.push(s); label[s] = s;
      var minx = w, maxx = 0, miny = h, maxy = 0;
      while (stack.length) {
        var p = stack.pop(), x = p % w, y = (p - x) / w;
        pts.push(p);
        if (x < minx) minx = x; if (x > maxx) maxx = x; if (y < miny) miny = y; if (y > maxy) maxy = y;
        if (x > 0 && mask[p - 1] && label[p - 1] < 0) { label[p - 1] = s; stack.push(p - 1); }
        if (x < w - 1 && mask[p + 1] && label[p + 1] < 0) { label[p + 1] = s; stack.push(p + 1); }
        if (y > 0 && mask[p - w] && label[p - w] < 0) { label[p - w] = s; stack.push(p - w); }
        if (y < h - 1 && mask[p + w] && label[p + w] < 0) { label[p + w] = s; stack.push(p + w); }
      }
      if (pts.length < w * h * 0.08) continue;
      touch = (minx === 0) + (maxx === w - 1) + (miny === 0) + (maxy === h - 1);
      if (touch >= 3) continue; /* that's the background, not the paper */
      var border = [];
      for (var q = 0; q < pts.length; q++) {
        var pp = pts[q], px = pp % w, py = (pp - px) / w;
        if (px === 0 || py === 0 || px === w - 1 || py === h - 1 || !mask[pp - 1] || !mask[pp + 1] || !mask[pp - w] || !mask[pp + w]) border.push([px + 0.5, py + 0.5]);
      }
      var hl = hull(border); if (hl.length < 4) continue;
      var quad = orderQuad(toQuad(hl));
      var area = polyArea(quad), fill = pts.length / area;
      if (!isConvex(quad) || fill < 0.85) continue; /* not a clean four-sided sheet */
      var score = area * fill;
      if (!best || score > best.score) best = { score: score, quad: quad };
    }
  });
  if (!best) return { quad: full, found: false };
  return { quad: best.quad.map(function (p) { return [p[0] / k, p[1] / k]; }), found: true };
}

/* ---------- perspective ---------- */
function solve(A, b) {
  var n = b.length;
  for (var i = 0; i < n; i++) {
    var m = i; for (var r = i + 1; r < n; r++) if (Math.abs(A[r][i]) > Math.abs(A[m][i])) m = r;
    var t = A[i]; A[i] = A[m]; A[m] = t; var tb = b[i]; b[i] = b[m]; b[m] = tb;
    for (var r2 = i + 1; r2 < n; r2++) { var f = A[r2][i] / A[i][i]; for (var c = i; c < n; c++) A[r2][c] -= f * A[i][c]; b[r2] -= f * b[i]; }
  }
  var x = new Array(n);
  for (var i2 = n - 1; i2 >= 0; i2--) { var s = b[i2]; for (var c2 = i2 + 1; c2 < n; c2++) s -= A[i2][c2] * x[c2]; x[i2] = s / A[i2][i2]; }
  return x;
}
/* Homography that maps points (x,y) of `from` to `to`. */
function homography(from, to) {
  var A = [], b = [];
  for (var i = 0; i < 4; i++) {
    var x = from[i][0], y = from[i][1], u = to[i][0], v = to[i][1];
    A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
    A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
  }
  var h = solve(A, b); h.push(1); return h;
}
function dist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }

/* Output size for a quad, keeping the sheet's real proportions; long side capped at maxSide. */
function outputSize(q, maxSide) {
  var w = Math.max(dist(q[0], q[1]), dist(q[3], q[2])), h = Math.max(dist(q[0], q[3]), dist(q[1], q[2]));
  var s = Math.min(1, (maxSide || 2400) / Math.max(w, h));
  return { width: Math.max(1, Math.round(w * s)), height: Math.max(1, Math.round(h * s)) };
}

function warp(img, quad, size) {
  size = size || outputSize(quad);
  var W = size.width, H = size.height, out = newImg(W, H), src = img.data, dst = out.data, sw = img.width, sh = img.height;
  var h = homography([[0, 0], [W, 0], [W, H], [0, H]], quad);
  for (var y = 0; y < H; y++) {
    for (var x = 0; x < W; x++) {
      var X = x + 0.5, Y = y + 0.5, d = h[6] * X + h[7] * Y + 1;
      var u = (h[0] * X + h[1] * Y + h[2]) / d - 0.5, v = (h[3] * X + h[4] * Y + h[5]) / d - 0.5;
      var x0 = Math.floor(u), y0 = Math.floor(v), fx = u - x0, fy = v - y0;
      if (x0 < 0) { x0 = 0; fx = 0; } if (y0 < 0) { y0 = 0; fy = 0; }
      if (x0 >= sw - 1) { x0 = sw - 2; fx = 1; } if (y0 >= sh - 1) { y0 = sh - 2; fy = 1; }
      var i00 = (y0 * sw + x0) * 4, i10 = i00 + 4, i01 = i00 + sw * 4, i11 = i01 + 4, o = (y * W + x) * 4;
      for (var c = 0; c < 3; c++) {
        dst[o + c] = (src[i00 + c] * (1 - fx) + src[i10 + c] * fx) * (1 - fy) + (src[i01 + c] * (1 - fx) + src[i11 + c] * fx) * fy;
      }
      dst[o + 3] = 255;
    }
  }
  return out;
}

/* ---------- cleanup ---------- */
/* Estimate the paper colour under the text (lighting + shadows) at low resolution. */
function background(channel, W, H) {
  var k = Math.min(1, 160 / Math.max(W, H)), w = Math.max(4, Math.round(W * k)), h = Math.max(4, Math.round(H * k));
  var s = shrink(channel, W, H, w, h);
  var r = Math.max(2, Math.round(Math.max(w, h) / 40));
  s = maxFilter(s, w, h, r);       /* drop dark text */
  s = boxBlur(s, w, h, r * 2);     /* smooth lighting */
  return { d: s, w: w, h: h };
}
function sampleBg(bg, x, y, W, H) {
  var u = (x + 0.5) * bg.w / W - 0.5, v = (y + 0.5) * bg.h / H - 0.5;
  var x0 = Math.max(0, Math.min(bg.w - 2, Math.floor(u))), y0 = Math.max(0, Math.min(bg.h - 2, Math.floor(v)));
  var fx = Math.max(0, Math.min(1, u - x0)), fy = Math.max(0, Math.min(1, v - y0)), d = bg.d, w = bg.w;
  return (d[y0 * w + x0] * (1 - fx) + d[y0 * w + x0 + 1] * fx) * (1 - fy) + (d[(y0 + 1) * w + x0] * (1 - fx) + d[(y0 + 1) * w + x0 + 1] * fx) * fy;
}
function levels(v, black, white) { v = (v - black) * 255 / (white - black); return v < 0 ? 0 : v > 255 ? 255 : v; }

/* mode: 'color' | 'gray' | 'bw' | 'original' */
function enhance(img, mode) {
  if (mode === 'original') return img;
  var W = img.width, H = img.height, n = W * H, d = img.data, out = newImg(W, H), o = out.data;
  if (mode === 'color') {
    var ch = [0, 1, 2].map(function (c) { var a = new Float32Array(n); for (var i = 0; i < n; i++) a[i] = d[i * 4 + c]; return a; });
    var bgs = ch.map(function (a) { return background(a, W, H); });
    for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
      var i2 = y * W + x;
      for (var c = 0; c < 3; c++) {
        var b = Math.max(24, sampleBg(bgs[c], x, y, W, H));
        o[i2 * 4 + c] = levels(ch[c][i2] / b * 255, 45, 238);
      }
      o[i2 * 4 + 3] = 255;
    }
    return out;
  }
  var g = toGray(img), bg = background(g, W, H), norm = new Float32Array(n);
  for (var y2 = 0; y2 < H; y2++) for (var x2 = 0; x2 < W; x2++) {
    var j = y2 * W + x2; norm[j] = Math.min(255, g[j] / Math.max(24, sampleBg(bg, x2, y2, W, H)) * 255);
  }
  if (mode === 'gray') {
    for (var k2 = 0; k2 < n; k2++) { var v = levels(norm[k2], 50, 236); o[k2 * 4] = o[k2 * 4 + 1] = o[k2 * 4 + 2] = v; o[k2 * 4 + 3] = 255; }
    return out;
  }
  /* black & white: threshold the lighting-corrected image, nudged toward keeping faint text */
  var th = Math.min(225, otsu(norm, 0, 255) + 12);
  for (var k3 = 0; k3 < n; k3++) { var v2 = norm[k3] > th ? 255 : 0; o[k3 * 4] = o[k3 * 4 + 1] = o[k3 * 4 + 2] = v2; o[k3 * 4 + 3] = 255; }
  return out;
}

function rotate90(img, times) {
  times = ((times % 4) + 4) % 4; if (!times) return img;
  var W = img.width, H = img.height, nw = times % 2 ? H : W, nh = times % 2 ? W : H, out = newImg(nw, nh), s = img.data, o = out.data;
  for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
    var nx, ny;
    if (times === 1) { nx = H - 1 - y; ny = x; } else if (times === 2) { nx = W - 1 - x; ny = H - 1 - y; } else { nx = y; ny = W - 1 - x; }
    var a = (y * W + x) * 4, b = (ny * nw + nx) * 4;
    o[b] = s[a]; o[b + 1] = s[a + 1]; o[b + 2] = s[a + 2]; o[b + 3] = s[a + 3];
  }
  return out;
}

var ScanCore = { detectPaper: detectPaper, warp: warp, outputSize: outputSize, enhance: enhance, rotate90: rotate90, orderQuad: orderQuad, isConvex: isConvex };
if (typeof module !== 'undefined' && module.exports) module.exports = ScanCore; else root.ScanCore = ScanCore;
})(typeof window !== 'undefined' ? window : globalThis);
