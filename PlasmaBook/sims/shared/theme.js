/* Перемикання світлої/темної теми для симуляцій PlasmaBook.
   Підключати в <head> ПЕРШИМ скриптом (до стилів не обов'язково), щоб не було «спалаху».
   Тема лежить в html[data-theme="light|dark"]; якщо не задана — діє системна.
   При будь-якій зміні теми надсилається подія window 'themechange' {detail:{dark}},
   на яку PSim.canvas перемальовує полотна.
   API: window.PSimTheme = { isDark(), set('light'|'dark') }. */
(function () {
  var KEY = 'plasmabook-sim-theme', root = document.documentElement;
  var sys = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : { matches: false };

  function stored() {
    try { var t = localStorage.getItem(KEY); return t === 'dark' || t === 'light' ? t : null; }
    catch (e) { return null; }
  }
  function isDark() { var t = root.getAttribute('data-theme'); return t ? t === 'dark' : !!sys.matches; }
  function apply(t) { if (t) root.setAttribute('data-theme', t); else root.removeAttribute('data-theme'); }

  apply(stored());

  var btn;
  function label() {
    if (!btn) return;
    btn.textContent = isDark() ? '☀' : '☾';
    btn.title = isDark() ? 'Світла тема' : 'Темна тема';
    btn.setAttribute('aria-label', btn.title);
  }
  function notify() {
    label();
    window.dispatchEvent(new CustomEvent('themechange', { detail: { dark: isDark() } }));
  }
  function set(t) { apply(t); try { localStorage.setItem(KEY, t); } catch (e) {} notify(); }

  if (sys.addEventListener) sys.addEventListener('change', function () { if (!stored()) notify(); });
  window.addEventListener('storage', function (e) { if (e.key === KEY) { apply(stored()); notify(); } });

  // Кнопка: у #theme-slot (шапка сторінки), інакше фіксована в правому верхньому куті.
  function mount() {
    btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'theme-btn';
    btn.onclick = function () { set(isDark() ? 'light' : 'dark'); };
    var slot = document.getElementById('theme-slot');
    if (slot) slot.appendChild(btn);
    else { btn.style.cssText = 'position:fixed;top:6px;right:6px;z-index:9999'; document.body.appendChild(btn); }
    label();
  }
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);

  window.PSimTheme = { isDark: isDark, set: set };
})();
