/* ═══════════════════════════════════════════════════════════════════════════
   AITHERIUM UNIVERSE STRIP — flight paths between the public repos
   @element-universe v1

   Source of truth for the motion layer of the universe strip on every public
   static page. tools/gen_public_pages.py INLINES this file verbatim, the same
   way it inlines .ELEMENT/web/aitherium.css, and check_pages_truth.py asserts
   a published page still carries the current copy.

   WHY THIS IS NOT @aitheros/bead-space
       bead-space is the real thing: a d3-force universe explorer with live
       AitherOS adapters (agents, compute, mesh, platform, work). Using it here
       would mean npm-installing seven d3 packages and running esbuild inside
       four sync workflows, then inlining ~60-80KB into every landing page — to
       lay out SIX fixed navigational nodes that never move and carry no live
       data. That is the wrong trade: it adds a build dependency to a pipeline
       whose whole virtue is that it is pure static generation.
       So this is a purpose-built ~4KB renderer that deliberately speaks
       bead-space's node shape ({id, label, kind, href}), read straight off the
       rendered DOM. If the strip ever needs live fleet data, swap this for the
       real bead-space bundle without touching the markup or the CSS.

   PROGRESSIVE ENHANCEMENT, NOT A DEPENDENCY
       The orbs are real <a> elements emitted in the HTML. Navigation works with
       JavaScript off, with canvas unsupported, and if this file fails to parse.
       Everything below only draws the connective tissue between them. Under
       prefers-reduced-motion it renders the paths once, statically, and stops —
       it never animates.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var stage = document.querySelector('.uni-stage');
  if (!stage) return;

  var canvas = stage.querySelector('.uni-canvas');
  if (!canvas || typeof canvas.getContext !== 'function') return;

  var ctx = canvas.getContext('2d');
  if (!ctx) return;

  var reduced =
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var orbEls = Array.prototype.slice.call(stage.querySelectorAll('.orb'));
  if (orbEls.length < 2) return;

  var accent =
    (getComputedStyle(document.documentElement).getPropertyValue('--accent') || '').trim() ||
    '#2AD7D7';

  var nodes = [];
  var here = null;
  var paths = [];
  var W = 0;
  var H = 0;
  var raf = 0;

  // ── layout ───────────────────────────────────────────────────────────────
  function measure() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var sr = stage.getBoundingClientRect();
    W = sr.width;
    H = sr.height;
    if (W < 2 || H < 2) return false;

    canvas.width = Math.max(1, Math.round(W * dpr));
    canvas.height = Math.max(1, Math.round(H * dpr));
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    nodes = orbEls.map(function (el) {
      var r = el.getBoundingClientRect();
      return {
        el: el,
        // bead-space node shape, read off the DOM rather than a second data blob
        id: el.getAttribute('data-id') || '',
        kind: el.getAttribute('data-kind') || 'repo',
        href: el.getAttribute('href') || '',
        x: r.left - sr.left + r.width / 2,
        y: r.top - sr.top + r.height / 2,
        // Paths anchor to the TOP EDGE, not the centre. A quadratic only reaches
        // half its control-point offset, so centre-anchored arcs peaked inside
        // the orb row and were covered by the cards (which sit at z-index 1).
        ty: r.top - sr.top + 5,
        here: el.classList.contains('here')
      };
    });

    here =
      nodes.filter(function (n) {
        return n.here;
      })[0] || nodes[0];

    // One flight path from the lit node to each sibling. The control point is
    // pushed perpendicular to the chord so paths bow instead of overlapping
    // into a single straight bar when the orbs wrap onto one row.
    paths = nodes
      .filter(function (n) {
        return n !== here;
      })
      .map(function (n, i) {
        var mx = (here.x + n.x) / 2;
        var my = (here.ty + n.ty) / 2;
        var dx = n.x - here.x;
        var dy = n.ty - here.ty;
        var len = Math.sqrt(dx * dx + dy * dy) || 1;
        // Always bow toward the top of the stage (canvas y grows downward), into
        // the padding band .uni-stage reserves. Alternating the sign put half the
        // arcs underneath the orb row where they were invisible.
        var bow = Math.min(78, 26 + len * 0.22) * (dx >= 0 ? -1 : 1);
        return {
          a: here,
          b: n,
          cx: mx + (-dy / len) * bow,
          cy: my + (dx / len) * bow,
          // deterministic offsets: no Math.random, so the strip looks identical
          // on every load and in every screenshot
          seeds: [i * 0.37 % 1, (i * 0.37 + 0.5) % 1]
        };
      });

    return true;
  }

  function pointAt(p, t) {
    var u = 1 - t;
    return {
      x: u * u * p.a.x + 2 * u * t * p.cx + t * t * p.b.x,
      y: u * u * p.a.ty + 2 * u * t * p.cy + t * t * p.b.ty
    };
  }

  // ── paint ────────────────────────────────────────────────────────────────
  function draw(now) {
    ctx.clearRect(0, 0, W, H);

    for (var i = 0; i < paths.length; i++) {
      var p = paths[i];

      ctx.globalAlpha = 0.16;
      ctx.strokeStyle = accent;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(p.a.x, p.a.ty);
      ctx.quadraticCurveTo(p.cx, p.cy, p.b.x, p.b.ty);
      ctx.stroke();

      if (reduced) continue;

      // travellers: small motes drifting out along each path
      for (var s = 0; s < p.seeds.length; s++) {
        var t = (p.seeds[s] + now / 7400) % 1;
        var pt = pointAt(p, t);
        // fade in and out at the endpoints so motes do not pop
        var fade = Math.sin(t * Math.PI);
        ctx.globalAlpha = 0.5 * fade;
        ctx.fillStyle = accent;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 1.9, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // the lit node's halo
    if (here) {
      ctx.globalAlpha = reduced ? 0.13 : 0.1 + 0.045 * Math.sin(now / 1150);
      ctx.fillStyle = accent;
      ctx.beginPath();
      ctx.arc(here.x, here.y, 46, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.globalAlpha = 1;
  }

  function frame(ts) {
    draw(ts || 0);
    raf = window.requestAnimationFrame(frame);
  }

  function start() {
    if (!measure()) return;
    if (raf) window.cancelAnimationFrame(raf);
    // Paint one frame SYNCHRONOUSLY before scheduling the loop. measure() has
    // just resized the canvas, which clears it, and requestAnimationFrame does
    // not fire in a background tab -- so without this the strip renders blank
    // and only appears once the tab is focused. Measured 2026-08-02: a
    // backgrounded tab painted 0 pixels indefinitely.
    draw(0);
    if (reduced || !window.requestAnimationFrame) return;
    raf = window.requestAnimationFrame(frame);
  }

  // Pause when the strip is off-screen or the tab is hidden — a landing page
  // has no business burning a phone battery on a decoration nobody is looking at.
  function stop() {
    if (raf) {
      window.cancelAnimationFrame(raf);
      raf = 0;
    }
  }

  var visible = true;
  if (window.IntersectionObserver) {
    new window.IntersectionObserver(
      function (entries) {
        visible = entries[0].isIntersecting;
        if (visible && !document.hidden) start();
        else stop();
      },
      { threshold: 0.02 }
    ).observe(stage);
  }

  document.addEventListener('visibilitychange', function () {
    if (document.hidden || !visible) stop();
    else start();
  });

  var resizeTimer = 0;
  window.addEventListener('resize', function () {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(start, 140);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
