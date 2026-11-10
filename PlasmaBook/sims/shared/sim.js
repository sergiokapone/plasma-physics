/* Спільні хелпери симуляцій PlasmaBook: namespace window.PSim.
   Підключення (після theme.js):  <script src="shared/sim.js"></script>
   Без модулів і зовнішніх залежностей — працює при відкритті file://.

   API:
     PSim.$(sel)                       — document.querySelector
     PSim.css(name)                    — значення CSS-змінної ('--fg' або 'fg')
     PSim.fmt(x, d)                    — число з десятковою комою, d значущих цифр
     PSim.canvas(el, draw)             — полотно з урахуванням DPR, ResizeObserver, перемальовування при зміні теми
     PSim.frame(ctx, box, opt)         — осі/сітка/підписи, повертає відображення {X(x), Y(y), ...}
     PSim.curve(ctx, map, xs, ys, st)  — ламана в координатах map; st = {color, width, dash}
     PSim.controls(el, spec, P, onCh)  — слайдери/прапорці/списки для полів об'єкта параметрів P
     PSim.presets(el, list, apply)     — кнопки пресетів характерних режимів
     PSim.loop(el, h)                  — цикл анімації з кнопками «Старт/Пауза», «Крок», «Скинути»
     PSim.readout(el, items)           — таблиця поточних величин, повертає set(key, text, cls)
     PSim.label(ctx, text, x, y, st)   — підпис із підкладкою кольору фону; st = {color, size, bold, align, base}
     PSim.clip(ctx, map)               — обрізання прямокутником осей (робить ctx.save(); після — ctx.restore())
     PSim.alpha(col, a)                — #rrggbb → rgba(..., a)
     PSim.C, PSim.refreshColors()      — кеш кольорів теми
     PSim.Ring(n, k)                   — кільцевий буфер k паралельних рядів довжини n:
                                         push(a, b, ...), get(j, m) (m-й від найстарішого), len, clear(), minmax(j)
     PSim.trail(ctx, map, ring, jx, jy, st) — ламана за двома рядами кільцевого буфера; st = {color, width, dash} */
(function () {
  var PSim = window.PSim = window.PSim || {};

  PSim.$ = function (sel) { return document.querySelector(sel); };

  // ---------- кольори з CSS ----------
  PSim.css = function (name) {
    if (name.charAt(0) !== '-') name = '--' + name;
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || '#888';
  };
  // Колір із прозорістю: працює для #rgb/#rrggbb.
  PSim.alpha = function (col, a) {
    var m = /^#([0-9a-f]{3,8})$/i.exec(col);
    if (!m) return col;
    var h = m[1];
    if (h.length === 3 || h.length === 4) h = h.replace(/./g, '$&$&');
    var r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
    return 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
  };

  // ---------- форматування чисел (українська: десяткова кома, мінус U+2212) ----------
  var SUP = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' };
  PSim.fmt = function (x, d) {
    if (d === undefined) d = 3;
    if (!isFinite(x)) return x > 0 ? '∞' : (x < 0 ? '−∞' : '—');
    if (x === 0) return '0';
    var ax = Math.abs(x), s;
    if (ax >= 1e5 || ax < 1e-3) {
      var e = Math.floor(Math.log10(ax)), m = x / Math.pow(10, e);
      if (Math.abs(m) >= 9.9995) { m /= 10; e += 1; }
      s = m.toFixed(Math.max(0, d - 1)).replace(/\.?0+$/, '') + '·10' + String(e).replace(/./g, function (c) { return SUP[c]; });
    } else {
      s = Number(x.toPrecision(d)).toString();
    }
    return s.replace('.', ',').replace(/^-/, '−');
  };

  // ---------- полотно ----------
  // draw(ctx, w, h) викликається при зміні розміру, теми та за запитом redraw().
  PSim.canvas = function (el, draw) {
    if (typeof el === 'string') el = PSim.$(el);
    var cv = el.tagName === 'CANVAS' ? el : el.appendChild(document.createElement('canvas'));
    var ctx = cv.getContext('2d');
    var obj = { cv: cv, ctx: ctx, w: 1, h: 1, draw: draw };
    function fit() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2.5);
      var r = cv.getBoundingClientRect();
      obj.w = Math.max(1, r.width); obj.h = Math.max(1, r.height);
      cv.width = Math.round(obj.w * dpr); cv.height = Math.round(obj.h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    obj.redraw = function () {
      ctx.clearRect(0, 0, obj.w, obj.h);
      if (obj.draw) obj.draw(ctx, obj.w, obj.h);
    };
    fit();
    if (window.ResizeObserver) new ResizeObserver(function () { fit(); obj.redraw(); }).observe(cv);
    else window.addEventListener('resize', function () { fit(); obj.redraw(); });
    window.addEventListener('themechange', function () { PSim.refreshColors(); obj.redraw(); });
    return obj;
  };

  // Кеш кольорів (читаються один раз на зміну теми, а не щокадру).
  PSim.C = {};
  PSim.refreshColors = function () {
    ['bg', 'fg', 'muted', 'panel', 'line', 'ax', 'gr', 'accent', 'c1', 'c2', 'c3', 'c4', 'c5', 'ion', 'ele', 'warn', 'ok']
      .forEach(function (k) { PSim.C[k] = PSim.css(k); });
  };

  // ---------- осі ----------
  function niceStep(span, n) {
    var raw = span / Math.max(1, n), p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p;
    return (f < 1.5 ? 1 : f < 3.5 ? 2 : f < 7.5 ? 5 : 10) * p;
  }
  PSim.niceStep = niceStep;

  /* box = {x, y, w, h} у пікселях полотна; opt = {x0, x1, y0, y1, xlabel, ylabel, logx, logy,
     grid (true), title, nx, ny, xfmt, yfmt}. Повертає map = {X, Y, invX, invY, l, r, t, b}. */
  PSim.frame = function (ctx, box, opt) {
    var C = PSim.C, fs = opt.font || 13;
    var padL = opt.padL !== undefined ? opt.padL : 52, padB = opt.padB !== undefined ? opt.padB : 38;
    var padT = opt.title ? 24 : 10, padR = opt.padR !== undefined ? opt.padR : 12;
    var l = box.x + padL, r = box.x + box.w - padR, t = box.y + padT, b = box.y + box.h - padB;
    var lx = opt.logx, ly = opt.logy;
    var fx = lx ? Math.log10 : function (v) { return v; }, fy = ly ? Math.log10 : function (v) { return v; };
    var ax0 = fx(opt.x0), ax1 = fx(opt.x1), ay0 = fy(opt.y0), ay1 = fy(opt.y1);
    var map = {
      l: l, r: r, t: t, b: b,
      X: function (v) { return l + (fx(v) - ax0) / (ax1 - ax0) * (r - l); },
      Y: function (v) { return b - (fy(v) - ay0) / (ay1 - ay0) * (b - t); },
      invX: function (px) { var a = ax0 + (px - l) / (r - l) * (ax1 - ax0); return lx ? Math.pow(10, a) : a; },
      invY: function (py) { var a = ay0 + (b - py) / (b - t) * (ay1 - ay0); return ly ? Math.pow(10, a) : a; }
    };
    ctx.save();
    ctx.font = fs + 'px system-ui, sans-serif';
    ctx.lineWidth = 1;
    // сітка й підписи поділок
    function ticks(a0, a1, log, n) {
      var out = [];
      if (log) {
        for (var e = Math.floor(a0); e <= Math.ceil(a1); e++) if (e >= a0 - 1e-9 && e <= a1 + 1e-9) out.push(Math.pow(10, e));
      } else {
        var st = niceStep(a1 - a0, n), s0 = Math.ceil(a0 / st - 1e-9) * st;
        for (var v = s0; v <= a1 + st * 1e-6; v += st) out.push(Math.abs(v) < st * 1e-9 ? 0 : v);
      }
      return out;
    }
    var xt = ticks(ax0, ax1, lx, opt.nx || Math.max(2, Math.round((r - l) / 90)));
    var yt = ticks(ay0, ay1, ly, opt.ny || Math.max(2, Math.round((b - t) / 55)));
    var xf = opt.xfmt || function (v) { return PSim.fmt(v, 3); }, yf = opt.yfmt || function (v) { return PSim.fmt(v, 3); };
    ctx.strokeStyle = C.gr; ctx.fillStyle = C.ax;
    ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    xt.forEach(function (v) {
      var px = map.X(v);
      if (opt.grid !== false) { ctx.beginPath(); ctx.moveTo(px, t); ctx.lineTo(px, b); ctx.stroke(); }
      ctx.fillText(xf(v), px, b + 4);
    });
    ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
    yt.forEach(function (v) {
      var py = map.Y(v);
      if (opt.grid !== false) { ctx.beginPath(); ctx.moveTo(l, py); ctx.lineTo(r, py); ctx.stroke(); }
      ctx.fillText(yf(v), l - 5, py);
    });
    ctx.strokeStyle = C.ax; ctx.strokeRect(l, t, r - l, b - t);
    ctx.fillStyle = C.fg;
    if (opt.xlabel) { ctx.textAlign = 'center'; ctx.textBaseline = 'bottom'; ctx.fillText(opt.xlabel, (l + r) / 2, box.y + box.h - 2); }
    if (opt.ylabel) {
      ctx.save(); ctx.translate(box.x + 4, (t + b) / 2); ctx.rotate(-Math.PI / 2);
      ctx.textAlign = 'center'; ctx.textBaseline = 'top'; ctx.fillText(opt.ylabel, 0, 0); ctx.restore();
    }
    if (opt.title) { ctx.textAlign = 'left'; ctx.textBaseline = 'top'; ctx.font = '600 ' + fs + 'px system-ui, sans-serif'; ctx.fillText(opt.title, l, box.y + 4); }
    ctx.restore();
    return map;
  };

  // Обрізання малювання прямокутником осей.
  PSim.clip = function (ctx, map) {
    ctx.save(); ctx.beginPath(); ctx.rect(map.l, map.t, map.r - map.l, map.b - map.t); ctx.clip();
  };

  // Ламана y(x); NaN/нескінченні значення розривають лінію.
  PSim.curve = function (ctx, map, xs, ys, st) {
    st = st || {};
    ctx.save();
    ctx.strokeStyle = st.color || PSim.C.fg; ctx.lineWidth = st.width || 2;
    ctx.setLineDash(st.dash || []);
    ctx.beginPath();
    var pen = false;
    for (var i = 0; i < xs.length; i++) {
      var y = ys[i];
      if (!isFinite(y) || !isFinite(xs[i])) { pen = false; continue; }
      var px = map.X(xs[i]), py = map.Y(y);
      if (py < -1e4) py = -1e4; else if (py > 1e4) py = 1e4;
      if (pen) ctx.lineTo(px, py); else { ctx.moveTo(px, py); pen = true; }
    }
    ctx.stroke(); ctx.restore();
  };

  // Підпис біля кривої/точки з підкладкою кольору фону (читабельно на будь-якій темі).
  PSim.label = function (ctx, text, x, y, st) {
    st = st || {};
    ctx.save();
    ctx.font = (st.bold ? '600 ' : '') + (st.size || 13) + 'px system-ui, sans-serif';
    ctx.textAlign = st.align || 'left'; ctx.textBaseline = st.base || 'middle';
    ctx.lineWidth = 4; ctx.strokeStyle = PSim.C.bg; ctx.lineJoin = 'round';
    ctx.strokeText(text, x, y);
    ctx.fillStyle = st.color || PSim.C.fg; ctx.fillText(text, x, y);
    ctx.restore();
  };

  // ---------- кільцевий буфер історії (траєкторії, часові ряди) ----------
  PSim.Ring = function (n, k) {
    var data = [];
    for (var j = 0; j < k; j++) data.push(new Float64Array(n));
    var r = { len: 0, head: 0, n: n, data: data };
    r.push = function () {
      for (var j = 0; j < k; j++) data[j][r.head] = arguments[j];
      r.head = (r.head + 1) % n;
      if (r.len < n) r.len++;
    };
    r.get = function (j, m) { return data[j][(r.head - r.len + m + n) % n]; };
    r.clear = function () { r.len = 0; r.head = 0; };
    r.minmax = function (j) {
      var lo = Infinity, hi = -Infinity;
      for (var m = 0; m < r.len; m++) { var v = r.get(j, m); if (v < lo) lo = v; if (v > hi) hi = v; }
      return [lo, hi];
    };
    return r;
  };

  PSim.trail = function (ctx, map, ring, jx, jy, st) {
    st = st || {};
    if (ring.len < 2) return;
    ctx.save();
    ctx.strokeStyle = st.color || PSim.C.fg; ctx.lineWidth = st.width || 1.5;
    ctx.setLineDash(st.dash || []); ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(map.X(ring.get(jx, 0)), map.Y(ring.get(jy, 0)));
    for (var m = 1; m < ring.len; m++) ctx.lineTo(map.X(ring.get(jx, m)), map.Y(ring.get(jy, m)));
    ctx.stroke(); ctx.restore();
  };

  // ---------- елементи керування ----------
  /* spec: масив {key, label, min, max, step, log, fmt(v), hint} — слайдер;
           {key, label, type:'check'} — прапорець;
           {key, label, type:'select', options:[[value, text], ...]} — список.
     Значення читаються з P і записуються в P; onChange(key, value) після кожної зміни.
     Повертає {sync()} — оновити віджети після програмної зміни P (наприклад, пресетом). */
  PSim.controls = function (el, spec, P, onChange) {
    if (typeof el === 'string') el = PSim.$(el);
    var items = [];
    spec.forEach(function (s) {
      var wrap = document.createElement('div'), id = 'ctl-' + s.key;
      wrap.className = 'ctl' + (s.type === 'check' ? ' check' : '');
      var inp, out;
      if (s.type === 'check') {
        inp = document.createElement('input'); inp.type = 'checkbox'; inp.id = id;
        var lb = document.createElement('label'); lb.htmlFor = id; lb.innerHTML = s.label;
        wrap.appendChild(inp); wrap.appendChild(lb);
        inp.onchange = function () { P[s.key] = inp.checked; if (onChange) onChange(s.key, P[s.key]); };
      } else if (s.type === 'select') {
        var lb2 = document.createElement('label'); lb2.htmlFor = id; lb2.innerHTML = s.label;
        inp = document.createElement('select'); inp.id = id;
        s.options.forEach(function (o) { var op = document.createElement('option'); op.value = o[0]; op.textContent = o[1]; inp.appendChild(op); });
        wrap.appendChild(lb2); wrap.appendChild(inp);
        inp.onchange = function () { P[s.key] = inp.value; if (onChange) onChange(s.key, P[s.key]); };
      } else {
        var row = document.createElement('div'); row.className = 'row';
        var lb3 = document.createElement('label'); lb3.htmlFor = id; lb3.innerHTML = s.label;
        out = document.createElement('output'); out.htmlFor = id;
        row.appendChild(lb3); row.appendChild(out);
        inp = document.createElement('input'); inp.type = 'range'; inp.id = id;
        if (s.log) { inp.min = 0; inp.max = 1000; inp.step = 1; }
        else { inp.min = s.min; inp.max = s.max; inp.step = s.step || (s.max - s.min) / 200; }
        wrap.appendChild(row); wrap.appendChild(inp);
        inp.oninput = function () {
          var v = s.log ? s.min * Math.pow(s.max / s.min, inp.value / 1000) : parseFloat(inp.value);
          if (s.log && s.step) v = Math.round(v / s.step) * s.step;
          P[s.key] = v; show();
          if (onChange) onChange(s.key, v);
        };
      }
      if (s.hint) { var h = document.createElement('p'); h.className = 'hint'; h.innerHTML = s.hint; wrap.appendChild(h); }
      function show() { if (out) out.textContent = s.fmt ? s.fmt(P[s.key]) : PSim.fmt(P[s.key], 3); }
      function sync() {
        if (s.type === 'check') inp.checked = !!P[s.key];
        else if (s.type === 'select') inp.value = P[s.key];
        else {
          inp.value = s.log ? 1000 * Math.log(P[s.key] / s.min) / Math.log(s.max / s.min) : P[s.key];
          show();
        }
      }
      sync();
      items.push(sync);
      el.appendChild(wrap);
    });
    return { sync: function () { items.forEach(function (f) { f(); }); } };
  };

  /* list: масив {name, values:{...}, note}. apply(values, preset) викликається при натисканні.
     Повертає {mark(i)} — підсвітити пресет (−1 знімає підсвітку). */
  PSim.presets = function (el, list, apply) {
    if (typeof el === 'string') el = PSim.$(el);
    var box = document.createElement('div'); box.className = 'presets';
    var btns = list.map(function (p, i) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'b'; b.innerHTML = p.name;
      if (p.note) b.title = p.note;
      b.onclick = function () { mark(i); apply(p.values, p); };
      box.appendChild(b); return b;
    });
    function mark(i) { btns.forEach(function (b, j) { b.classList.toggle('on', j === i); b.setAttribute('aria-pressed', j === i); }); }
    el.appendChild(box);
    return { mark: mark };
  };

  /* h = {step(nSteps), draw(), reset(), steps: () => кроків за кадр, autostart}.
     step викликається з кількістю кроків інтегрування на кадр; draw — після кроку.
     Повертає {running(), start(), pause(), reset(), toggle()}. */
  PSim.loop = function (el, h) {
    if (typeof el === 'string') el = PSim.$(el);
    var box = document.createElement('div'); box.className = 'buttons';
    function mk(txt, cls, fn) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'b' + (cls ? ' ' + cls : '');
      b.textContent = txt; b.onclick = fn; box.appendChild(b); return b;
    }
    var run = false, raf = 0;
    var bRun = mk('▶ Старт', 'primary', function () { toggle(); });
    mk('⏭ Крок', '', function () { pause(); h.step(1); h.draw(); });
    mk('↺ Скинути', '', function () { reset(); });
    el.appendChild(box);
    function label() { bRun.textContent = run ? '⏸ Пауза' : '▶ Старт'; }
    function frame() {
      if (!run) return;
      h.step(h.steps ? h.steps() : 1);
      h.draw();
      raf = requestAnimationFrame(frame);
    }
    function start() { if (run) return; run = true; label(); raf = requestAnimationFrame(frame); }
    function pause() { run = false; cancelAnimationFrame(raf); label(); }
    function toggle() { if (run) pause(); else start(); }
    function reset() { if (h.reset) h.reset(); h.draw(); }
    // Пробіл — старт/пауза (якщо фокус не в полі вводу).
    window.addEventListener('keydown', function (e) {
      if (e.code === 'Space' && !/INPUT|SELECT|BUTTON|TEXTAREA/.test(document.activeElement.tagName)) { e.preventDefault(); toggle(); }
    });
    document.addEventListener('visibilitychange', function () { if (document.hidden) pause(); });
    if (h.autostart) setTimeout(start, 0);
    return { running: function () { return run; }, start: start, pause: pause, reset: reset, toggle: toggle };
  };

  /* items: масив [key, html-підпис]. Повертає set(key, text, cls), де cls = 'good'|'bad'|''. */
  PSim.readout = function (el, items) {
    if (typeof el === 'string') el = PSim.$(el);
    var dl = document.createElement('dl'); dl.className = 'readout';
    var dd = {};
    items.forEach(function (it) {
      var dt = document.createElement('dt'); dt.innerHTML = it[1];
      var d = document.createElement('dd'); d.textContent = '—';
      dl.appendChild(dt); dl.appendChild(d); dd[it[0]] = d;
    });
    el.appendChild(dl);
    return function set(key, text, cls) { var d = dd[key]; if (!d) return; d.textContent = text; d.className = cls || ''; };
  };

  PSim.refreshColors();
})();
