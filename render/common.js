/* Shared helpers for the document render frames.
   Each frame defines window.renderDocument(arrayBuffer, name) -> Promise<HTMLCanvasElement[]> (one canvas per PDF page). */
(function () {
  'use strict';
  var A4 = { w: 794, h: 1123 }; // A4 at 96 dpi, in CSS px

  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  /* Wait until fonts and images inside root have loaded (with a time limit). */
  async function settle(root) {
    try { if (document.fonts && document.fonts.ready) await Promise.race([document.fonts.ready, wait(3000)]); } catch (e) {}
    var imgs = Array.prototype.slice.call(root.querySelectorAll('img'));
    await Promise.race([Promise.all(imgs.map(function (im) {
      return im.complete ? null : new Promise(function (r) { im.onload = im.onerror = r; });
    })), wait(5000)]);
    await wait(50);
  }

  /* Draw one element to a canvas. scale 2 keeps text sharp in the PDF. */
  async function snap(el, opts) {
    opts = opts || {};
    return html2canvas(el, {
      scale: opts.scale || 2, backgroundColor: '#ffffff', useCORS: true, logging: false,
      width: opts.width, height: opts.height, windowWidth: opts.windowWidth || Math.max(document.documentElement.scrollWidth, el.scrollWidth + 40)
    });
  }

  /* Cut a tall canvas into pages that keep the given page ratio (height / width). */
  function slice(canvas, ratio) {
    var pageH = Math.round(canvas.width * ratio), out = [];
    if (canvas.height <= pageH * 1.02) {
      if (canvas.height >= pageH * 0.98) return [canvas];
      var p = document.createElement('canvas'); p.width = canvas.width; p.height = pageH;
      var g = p.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, p.width, p.height); g.drawImage(canvas, 0, 0);
      return [p];
    }
    for (var y = 0; y < canvas.height; y += pageH) {
      var h = Math.min(pageH, canvas.height - y);
      if (h < 8) break;
      var c = document.createElement('canvas'); c.width = canvas.width; c.height = pageH;
      var x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height);
      x.drawImage(canvas, 0, y, canvas.width, h, 0, 0, canvas.width, h);
      out.push(c);
    }
    return out;
  }

  window.RenderKit = { A4: A4, wait: wait, settle: settle, snap: snap, slice: slice };
})();
