/* PicShifter photo editor: colour adjustments, filters, blur, resize and text drawing (all on <canvas>, no upload). */
(function (root) {
'use strict';
var LIST = ['none', 'classic', 'pop', 'film', 'retro', 'aura', 'vintage', 'cinema', 'soft', 'mono', 'noir', 'warm', 'cool'];
var F = {
  none: {},
  classic: { contrast: 1.08, sat: 0.85, warm: 10, fade: 8, vig: 0.25 },
  pop: { contrast: 1.18, sat: 1.55, bright: 6 },
  film: { contrast: 0.95, sat: 0.88, fade: 22, split: [[-4, 6, 10], [12, 6, -8]], grain: 14, vig: 0.15 },
  retro: { sepia: 0.45, contrast: 0.92, fade: 28, tint: [14, -4, 10], vig: 0.45, grain: 8 },
  aura: { glow: 0.55, bright: 10, contrast: 0.92, sat: 1.1, aura: 0.32 },
  vintage: { sepia: 0.7, contrast: 0.88, fade: 18, vig: 0.35, grain: 10, warm: 8 },
  cinema: { contrast: 1.1, sat: 1.05, split: [[-12, 6, 18], [18, 6, -14]] },
  soft: { glow: 0.35, contrast: 0.9, fade: 10, bright: 6 },
  mono: { mono: 1, contrast: 1.12 },
  noir: { mono: 1, contrast: 1.45, vig: 0.5 },
  warm: { warm: 22, sat: 1.05 },
  cool: { warm: -22, tint: [0, 4, 6] }
};
function zeroAdj() { return { bright: 0, contrast: 0, sat: 0, warm: 0, fade: 0, vig: 0, grain: 0 }; }
function isIdentity(a, f, s) {
  for (var k in a) if (a[k]) return false;
  return f === 'none' || !s;
}
function mk(w, h) { var c = document.createElement('canvas'); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h)); return c; }

/* Fast soft blur: shrink, then enlarge with smoothing. radius is in pixels of the source. */
function blur(src, radius) {
  var f = Math.max(1, radius / 2), w = src.width, h = src.height;
  var cur = src, cw = w, ch = h;
  while (cw / 2 >= w / f && ch / 2 >= 1) { var n = mk(cw / 2, ch / 2); n.getContext('2d').drawImage(cur, 0, 0, n.width, n.height); cur = n; cw = n.width; ch = n.height; }
  var s = mk(Math.max(1, w / f), Math.max(1, h / f)); s.getContext('2d').drawImage(cur, 0, 0, s.width, s.height);
  var mid = mk(Math.min(w, s.width * 4), Math.min(h, s.height * 4)); var mx = mid.getContext('2d'); mx.imageSmoothingQuality = 'high'; mx.drawImage(s, 0, 0, mid.width, mid.height);
  var out = mk(w, h); var ox = out.getContext('2d'); ox.imageSmoothingQuality = 'high'; ox.drawImage(mid, 0, 0, w, h);
  return out;
}

/* High-quality resize: halve step by step when shrinking a lot. */
function resize(src, w, h) {
  var cur = src;
  while (cur.width / 2 >= w && cur.height / 2 >= h) { var n = mk(cur.width / 2, cur.height / 2); var nx = n.getContext('2d'); nx.imageSmoothingQuality = 'high'; nx.drawImage(cur, 0, 0, n.width, n.height); cur = n; }
  var out = mk(w, h); var ox = out.getContext('2d'); ox.imageSmoothingQuality = 'high'; ox.drawImage(cur, 0, 0, w, h);
  return out;
}

function hash(x, y) { var n = (x * 374761393 + y * 668265263) | 0; n = (n ^ (n >>> 13)) * 1274126177 | 0; return ((n ^ (n >>> 16)) >>> 0) / 4294967296; }
function c255(v) { return v < 0 ? 0 : v > 255 ? 255 : v; }

/* Apply filter (with strength 0–100) and then the user's adjustments. Returns a new canvas. */
function render(src, a, fid, strength) {
  var w = src.width, h = src.height, P = F[fid] || {}, s = (fid === 'none' ? 0 : strength / 100);
  var out = mk(w, h), ox = out.getContext('2d');
  ox.drawImage(src, 0, 0);
  var img = ox.getImageData(0, 0, w, h), d = img.data;
  var gl = null;
  if (s && P.glow) { var b = blur(src, Math.max(w, h) / 30); gl = b.getContext('2d').getImageData(0, 0, w, h).data; }
  var fc = P.contrast || 1, fs = P.sat === undefined ? 1 : P.sat, fb = P.bright || 0, fw = P.warm || 0, ff = P.fade || 0,
      sep = P.sepia || 0, mono = P.mono || 0, tint = P.tint, split = P.split, aura = P.aura || 0, glow = P.glow || 0;
  var ab = a.bright, ac = a.contrast >= 0 ? 1 + a.contrast / 100 : 1 + a.contrast / 150, as = 1 + a.sat / 100, aw = a.warm * 0.3, af = a.fade * 0.6;
  var vig = (P.vig || 0) * s + a.vig / 100, grain = (P.grain || 0) * s + a.grain * 0.4;
  var cx = w / 2, cy = h / 2, rr = 1 / (cx * cx + cy * cy), gs = Math.max(1, Math.round(Math.max(w, h) / 1200));
  for (var y = 0, i = 0; y < h; y++) {
    for (var x = 0; x < w; x++, i += 4) {
      var r0 = d[i], g0 = d[i + 1], b0 = d[i + 2], r = r0, g = g0, bb = b0, l;
      if (s) {
        if (gl) { var t = glow; r = r0 + (255 - (255 - r0) * (255 - gl[i]) / 255 - r0) * t;
          g = g0 + (255 - (255 - g0) * (255 - gl[i + 1]) / 255 - g0) * t; bb = b0 + (255 - (255 - b0) * (255 - gl[i + 2]) / 255 - b0) * t; }
        if (mono) { l = 0.299 * r + 0.587 * g + 0.114 * bb; r = g = bb = l; }
        if (sep) { var sr = 0.393 * r + 0.769 * g + 0.189 * bb, sg = 0.349 * r + 0.686 * g + 0.168 * bb, sb = 0.272 * r + 0.534 * g + 0.131 * bb;
          r += (sr - r) * sep; g += (sg - g) * sep; bb += (sb - bb) * sep; }
        if (fs !== 1) { l = 0.299 * r + 0.587 * g + 0.114 * bb; r = l + (r - l) * fs; g = l + (g - l) * fs; bb = l + (bb - l) * fs; }
        if (fc !== 1) { r = (r - 128) * fc + 128; g = (g - 128) * fc + 128; bb = (bb - 128) * fc + 128; }
        if (fb) { r += fb; g += fb; bb += fb; }
        if (fw) { r += fw; bb -= fw; }
        if (tint) { r += tint[0]; g += tint[1]; bb += tint[2]; }
        if (split) { l = c255(0.299 * r + 0.587 * g + 0.114 * bb) / 255; var m = 1 - l;
          r += split[0][0] * m + split[1][0] * l; g += split[0][1] * m + split[1][1] * l; bb += split[0][2] * m + split[1][2] * l; }
        if (ff) { r = ff + r * (1 - ff / 255); g = ff + g * (1 - ff / 255); bb = ff + bb * (1 - ff / 255); }
        if (aura) { var u = (x / w + y / h) / 2, cr, cg, cb;
          if (u < 0.5) { var k = u * 2; cr = 255 - 75 * k; cg = 150 + 10 * k; cb = 200 + 55 * k; } else { var k2 = (u - 0.5) * 2; cr = 180 + 75 * k2; cg = 160 + 40 * k2; cb = 255 - 105 * k2; }
          r += (255 - (255 - c255(r)) * (255 - cr) / 255 - r) * aura; g += (255 - (255 - c255(g)) * (255 - cg) / 255 - g) * aura; bb += (255 - (255 - c255(bb)) * (255 - cb) / 255 - bb) * aura; }
        if (s < 1) { r = r0 + (r - r0) * s; g = g0 + (g - g0) * s; bb = b0 + (bb - b0) * s; }
      }
      if (ab) { var kb = 1 + ab / 200; r = r * kb + ab * 0.3; g = g * kb + ab * 0.3; bb = bb * kb + ab * 0.3; }
      if (ac !== 1) { r = (r - 128) * ac + 128; g = (g - 128) * ac + 128; bb = (bb - 128) * ac + 128; }
      if (as !== 1) { l = 0.299 * r + 0.587 * g + 0.114 * bb; r = l + (r - l) * as; g = l + (g - l) * as; bb = l + (bb - l) * as; }
      if (aw) { r += aw; bb -= aw; }
      if (af) { r = af + r * (1 - af / 255); g = af + g * (1 - af / 255); bb = af + bb * (1 - af / 255); }
      if (vig) { var dx = x - cx, dy = y - cy, dd = (dx * dx + dy * dy) * rr, v = 1 - vig * Math.pow(dd, 1.1) * 0.85; r *= v; g *= v; bb *= v; }
      if (grain) { var n = (hash((x / gs) | 0, (y / gs) | 0) - 0.5) * grain * 1.6; r += n; g += n; bb += n; }
      d[i] = c255(r); d[i + 1] = c255(g); d[i + 2] = c255(bb);
    }
  }
  ox.putImageData(img, 0, 0);
  return out;
}

/* Draw text (or a repeated watermark) onto a 2D context of size W×H. size is a fraction of the shorter side. */
function drawText(ctx, W, H, o) {
  var px = Math.max(8, Math.round(o.size * Math.min(W, H)));
  ctx.save();
  ctx.globalAlpha = o.alpha;
  ctx.font = (o.bold ? '700 ' : '400 ') + px + 'px ' + o.font;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  var light = (function (hex) { var n = parseInt(hex.slice(1), 16); return (0.299 * (n >> 16) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) > 140; })(o.color);
  function one(x, y) {
    var tw = ctx.measureText(o.text).width;
    if (o.style === 'box') { var p = px * 0.35; ctx.fillStyle = light ? 'rgba(0,0,0,.55)' : 'rgba(255,255,255,.75)'; ctx.fillRect(x - tw / 2 - p, y - px * 0.62 - p / 2, tw + p * 2, px * 1.24 + p); }
    if (o.style === 'shadow') { ctx.shadowColor = 'rgba(0,0,0,.6)'; ctx.shadowBlur = px * 0.25; ctx.shadowOffsetY = px * 0.06; }
    if (o.style === 'outline') { ctx.lineJoin = 'round'; ctx.lineWidth = Math.max(2, px * 0.12); ctx.strokeStyle = light ? '#000' : '#fff'; ctx.strokeText(o.text, x, y); }
    ctx.fillStyle = o.color; ctx.fillText(o.text, x, y);
    ctx.shadowColor = 'transparent';
  }
  if (o.tile) {
    var tw = ctx.measureText(o.text).width, sx = tw + px * 2.5, sy = px * 3.2, diag = Math.sqrt(W * W + H * H);
    ctx.translate(W / 2, H / 2); ctx.rotate(-Math.PI / 6);
    for (var yy = -diag / 2, row = 0; yy < diag / 2; yy += sy, row++)
      for (var xx = -diag / 2 + (row % 2) * sx / 2; xx < diag / 2; xx += sx) one(xx, yy);
  } else {
    one(o.x * W, o.y * H);
  }
  ctx.restore();
}

root.Fx = { LIST: LIST, zeroAdj: zeroAdj, isIdentity: isIdentity, render: render, blur: blur, resize: resize, drawText: drawText };
})(window);
