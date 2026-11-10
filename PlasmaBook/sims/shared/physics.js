/* Чисельні інструменти симуляцій PlasmaBook: namespace PSim.phys.
   Підключення після sim.js:  <script src="shared/physics.js"></script>

   API:
     phys.randn()                        — стандартна нормальна величина (Бокс–Мюллер)
     phys.rng(seed)                      — відтворюваний генератор U(0,1) (mulberry32)
     phys.erf(x)                         — функція помилок (Абрамовіц–Стіган 7.1.26, похибка < 1,5·10⁻⁷)
     phys.linspace(a, b, n)              — масив n рівновіддалених точок
     phys.cross(a, b)                    — векторний добуток тривимірних масивів
     phys.boris(x, v, qm, E, B, dt)      — крок Боріса (на місці змінює x, v); E, B — масиви [3]
     phys.rk4(f, t, y, dt)               — крок Рунге–Кутти 4-го порядку для y' = f(t, y)
     phys.maxwellian(n, vT)              — масив n швидкостей з розподілу exp(−v²/2vT²)
     phys.bisect(f, a, b, tol)           — корінь f на [a, b] (f(a)·f(b) < 0) */
(function () {
  var phys = (window.PSim = window.PSim || {}).phys = {};

  var spare = null;
  phys.randn = function () {
    if (spare !== null) { var s = spare; spare = null; return s; }
    var u, v, r;
    do { u = 2 * Math.random() - 1; v = 2 * Math.random() - 1; r = u * u + v * v; } while (r >= 1 || r === 0);
    var k = Math.sqrt(-2 * Math.log(r) / r);
    spare = v * k; return u * k;
  };

  phys.rng = function (seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  phys.erf = function (x) {
    var s = x < 0 ? -1 : 1; x = Math.abs(x);
    var t = 1 / (1 + 0.3275911 * x);
    var y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return s * y;
  };

  phys.linspace = function (a, b, n) {
    var out = new Array(n);
    for (var i = 0; i < n; i++) out[i] = a + (b - a) * i / (n - 1);
    return out;
  };

  phys.cross = function (a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  };

  /* Схема Боріса: півкрок E, точний за модулем поворот у B, півкрок E, дрейф.
     Зберігає |v| у чистому магнітному полі точно (до округлення); фазова похибка O(dt²). */
  phys.boris = function (x, v, qm, E, B, dt) {
    var h = 0.5 * qm * dt;
    var vx = v[0] + h * E[0], vy = v[1] + h * E[1], vz = v[2] + h * E[2];
    var tx = h * B[0], ty = h * B[1], tz = h * B[2];
    var t2 = tx * tx + ty * ty + tz * tz, k = 2 / (1 + t2);
    var px = vx + (vy * tz - vz * ty), py = vy + (vz * tx - vx * tz), pz = vz + (vx * ty - vy * tx);
    vx += k * (py * tz - pz * ty); vy += k * (pz * tx - px * tz); vz += k * (px * ty - py * tx);
    v[0] = vx + h * E[0]; v[1] = vy + h * E[1]; v[2] = vz + h * E[2];
    x[0] += v[0] * dt; x[1] += v[1] * dt; x[2] += v[2] * dt;
  };

  phys.rk4 = function (f, t, y, dt) {
    var n = y.length, i, tmp = new Array(n);
    var k1 = f(t, y);
    for (i = 0; i < n; i++) tmp[i] = y[i] + 0.5 * dt * k1[i];
    var k2 = f(t + 0.5 * dt, tmp);
    for (i = 0; i < n; i++) tmp[i] = y[i] + 0.5 * dt * k2[i];
    var k3 = f(t + 0.5 * dt, tmp);
    for (i = 0; i < n; i++) tmp[i] = y[i] + dt * k3[i];
    var k4 = f(t + dt, tmp), out = new Array(n);
    for (i = 0; i < n; i++) out[i] = y[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    return out;
  };

  phys.maxwellian = function (n, vT) {
    var out = new Float64Array(n);
    for (var i = 0; i < n; i++) out[i] = vT * phys.randn();
    return out;
  };

  phys.bisect = function (f, a, b, tol) {
    var fa = f(a);
    tol = tol || 1e-10;
    for (var i = 0; i < 200 && b - a > tol; i++) {
      var m = 0.5 * (a + b), fm = f(m);
      if ((fm < 0) === (fa < 0)) { a = m; fa = fm; } else b = m;
    }
    return 0.5 * (a + b);
  };
})();
