(function () {
    'use strict';

    /* ═══════════════════════════════════════════════════════════
       Перемикач теми (світла/темна), збереження в localStorage.
       ═══════════════════════════════════════════════════════════ */
    var THEME_KEY = 'plasma-theme';
    var themeToggle = document.getElementById('theme-toggle');

    function applyTheme(theme) {
        document.documentElement.classList.toggle('dark', theme === 'dark');
        if (themeToggle) {
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    var savedTheme = null;
    try { savedTheme = localStorage.getItem(THEME_KEY); } catch (e) { /* localStorage недоступний */ }

    if (!savedTheme && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        savedTheme = 'dark';
    }
    applyTheme(savedTheme === 'dark' ? 'dark' : 'light');

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            var next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
            applyTheme(next);
            try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* ignore */ }
        });
    }

    /* ═══════════════════════════════════════════════════════════
       Зміст у стилі друкованої книги:
       кожен пункт отримує рядок [номер] [назва] [·····крапки·····] [▸],
       де стрілка — це акордеон для підпунктів (якщо вони є).
       Клік по назві, як і раніше, веде у PDF; клік по стрілці —
       розгортає/згортає підрозділи.
       ═══════════════════════════════════════════════════════════ */
    var TOC_STATE_KEY = 'plasma-toc-expanded';
    var chevronSVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" ' +
        'stroke-linecap="round" stroke-linejoin="round"><polyline points="9 6 15 12 9 18"></polyline></svg>';

    function buildToc() {
        var items = document.querySelectorAll('.toc-list > li');
        var accordionItems = [];

        items.forEach(function (li) {
            var num = li.querySelector(':scope > .toc-num');
            var titleLink = li.querySelector(':scope > .toc-title');
            var subList = li.querySelector(':scope > .sub-list');

            if (!titleLink) { return; }

            // Рядок пункту змісту: номер + назва + крапковий "лідер" + (стрілка)
            var row = document.createElement('div');
            row.className = 'toc-row';

            if (num) { row.appendChild(num); }
            row.appendChild(titleLink);

            var dots = document.createElement('span');
            dots.className = 'toc-dots';
            dots.setAttribute('aria-hidden', 'true');
            row.appendChild(dots);

            if (subList) {
                var toggleBtn = document.createElement('button');
                toggleBtn.type = 'button';
                toggleBtn.className = 'toc-toggle';
                toggleBtn.innerHTML = chevronSVG;
                toggleBtn.setAttribute('aria-expanded', 'false');
                toggleBtn.setAttribute('aria-label', 'Розгорнути підрозділи');
                row.appendChild(toggleBtn);

                li.insertBefore(row, subList);

                var wrap = document.createElement('div');
                wrap.className = 'sub-list-wrap';
                li.replaceChild(wrap, subList);
                wrap.appendChild(subList);
                wrap.style.maxHeight = '0px';

                (function (li, wrap, subList, toggleBtn) {
                    function setOpen(open) {
                        li.classList.toggle('toc-open', open);
                        toggleBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
                        toggleBtn.setAttribute('aria-label', open ? 'Згорнути підрозділи' : 'Розгорнути підрозділи');
                        wrap.style.maxHeight = open ? (subList.scrollHeight + 12) + 'px' : '0px';
                    }
                    toggleBtn.addEventListener('click', function () {
                        setOpen(!li.classList.contains('toc-open'));
                    });
                    accordionItems.push({ li: li, setOpen: setOpen });
                })(li, wrap, subList, toggleBtn);
            } else {
                li.classList.add('no-sub');
                li.appendChild(row);
            }
        });

        // Кнопки "Розгорнути все" / "Згорнути все"
        var expandAllBtn = document.getElementById('toc-expand-all');
        var collapseAllBtn = document.getElementById('toc-collapse-all');

        function setAll(open) {
            accordionItems.forEach(function (item) { item.setOpen(open); });
            try { localStorage.setItem(TOC_STATE_KEY, open ? '1' : '0'); } catch (e) { /* ignore */ }
        }

        if (expandAllBtn) {
            expandAllBtn.addEventListener('click', function () { setAll(true); });
        }
        if (collapseAllBtn) {
            collapseAllBtn.addEventListener('click', function () { setAll(false); });
        }

        // Перерахунок max-height при зміні розміру вікна (перенесення рядків тексту)
        window.addEventListener('resize', function () {
            accordionItems.forEach(function (item) {
                if (item.li.classList.contains('toc-open')) {
                    var wrap = item.li.querySelector(':scope > .sub-list-wrap');
                    var subList = wrap.querySelector('.sub-list');
                    wrap.style.maxHeight = (subList.scrollHeight + 12) + 'px';
                }
            });
        });

        // Відновлюємо попередній стан "розгорнуто все", якщо він був збережений
        var savedState = null;
        try { savedState = localStorage.getItem(TOC_STATE_KEY); } catch (e) { /* ignore */ }
        if (savedState === '1') { setAll(true); }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildToc);
    } else {
        buildToc();
    }

    /* ═══════════════════════════════════════════════════════════
       Кнопка "Нагору"
       ═══════════════════════════════════════════════════════════ */
    var backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', function () {
            backToTop.classList.toggle('visible', window.scrollY > 400);
        });
        backToTop.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    /* ═══════════════════════════════════════════════════════════
       Перемикач дизайнів: Поле / Креслення / Книга.
       Вибір зберігається в localStorage (ключ plasma-design).
       ═══════════════════════════════════════════════════════════ */
    var DESIGN_KEY = 'plasma-design';
    var DESIGNS = ['field', 'blueprint', 'book'];
    var root = document.documentElement;
    var designBtns = document.querySelectorAll('.design-switch button');

    function applyDesign(d) {
        if (DESIGNS.indexOf(d) < 0) { d = 'field'; }
        root.setAttribute('data-design', d);
        designBtns.forEach(function (b) {
            b.setAttribute('aria-pressed', b.getAttribute('data-design') === d ? 'true' : 'false');
        });
        // Змінилась геометрія — змісту й полотну треба перерахуватися
        window.dispatchEvent(new Event('resize'));
    }

    var savedDesign = null;
    try { savedDesign = localStorage.getItem(DESIGN_KEY); } catch (e) { /* ignore */ }
    applyDesign(savedDesign);

    designBtns.forEach(function (b) {
        b.addEventListener('click', function () {
            var d = b.getAttribute('data-design');
            applyDesign(d);
            try { localStorage.setItem(DESIGN_KEY, d); } catch (e) { /* ignore */ }
        });
    });

    /* ═══════════════════════════════════════════════════════════
       Магнітне дзеркало в шапці. Іони й електрони дрейфують уздовж
       силових ліній, гвинтом обертаючись у протилежні боки; в зоні
       сильного поля вони відбиваються (збереження магнітного моменту).
       Частинки з малим питч-кутом (конус втрат) вилітають із пастки.
       Курсор по вертикалі змінює пробкове відношення R = B_max/B_min:
       що більше R, то вужчий конус втрат.
       ═══════════════════════════════════════════════════════════ */
    (function initMirror() {
        var hero = document.querySelector('.pdf-hero');
        if (!hero) { return; }

        var cv = document.createElement('canvas');
        cv.className = 'field-canvas';
        cv.setAttribute('aria-hidden', 'true');
        hero.insertBefore(cv, hero.firstChild);

        var ctx = cv.getContext('2d');
        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var w = 0, h = 0, dpr = 1, raf = 0, visible = true;
        var R = 3.2, Rtarget = 3.2;               // пробкове відношення (поточне й цільове)
        var NP = 56, TRAIL = 26;
        var parts = [];

        // Геометрія: вісь пастки горизонтальна, центр — у правій частині шапки
        var cx, cy, L, rho;
        function B(z) { var u = z / L; return 1 + (R - 1) * u * u; }
        function dBdz(z) { return 2 * (R - 1) * z / (L * L); }

        function inject(p, fresh) {
            var ion = p.ion;
            p.z = fresh ? (Math.random() * 2 - 1) * L * 0.9 : (Math.random() * 2 - 1) * L * 0.15;
            // ізотропний розподіл за питч-кутом у центрі пастки
            var c = Math.random() * 2 - 1, s = Math.sqrt(1 - c * c);
            var v0 = ion ? 180 : 420;            // швидкість, px/с (іони повільніші)
            // у точці z початкові компоненти задаємо так, ніби питч-кут заданий при B(z)
            var Bz = B(p.z);
            p.vpar = v0 * c;
            p.mu2 = v0 * v0 * s * s / Bz;          // v_perp0^2 = v_perp^2 / B (стала руху)
            p.y0 = (Math.random() * 2 - 1) * rho * 0.85;   // положення силової лінії при B = 1
            p.phi = Math.random() * 2 * Math.PI;
            p.trail = [];
        }

        function init() {
            parts = [];
            for (var i = 0; i < NP; i++) {
                var p = { ion: i % 3 === 0 };       // 1/3 іони, 2/3 електрони (для наочності)
                inject(p, true);
                parts.push(p);
            }
        }

        function layout() {
            cx = 0.64 * w; cy = 0.34 * h;
            L = Math.min(0.3 * w, 360);
            rho = Math.min(0.2 * h, 120);
        }

        function step(dt) {
            for (var i = 0; i < parts.length; i++) {
                var p = parts[i];
                var n = 4, d = dt / n;
                for (var k = 0; k < n; k++) {
                    // магнітний момент зберігається: v_par' = -(v_perp0^2 / 2) dB/dz
                    p.vpar += -0.5 * p.mu2 * dBdz(p.z) * d;
                    p.z += p.vpar * d;
                }
                var Bz = B(p.z);
                var om = (p.ion ? 6.5 : 22) * Bz * (p.ion ? 1 : -1);   // ларморівська частота ∝ B, знак за зарядом
                p.phi += om * dt;
                if (Math.abs(p.z) > L) { inject(p, false); continue; }
                var vperp = Math.sqrt(p.mu2 * Bz);
                var rl = vperp / Math.abs(om);                          // r_L = v_perp / omega ∝ 1/sqrt(B)
                var y = p.y0 / Math.sqrt(Bz) + rl * Math.cos(p.phi);
                p.trail.push(cx + p.z, cy + y);
                if (p.trail.length > TRAIL * 2) { p.trail.splice(0, 2); }
            }
        }

        function draw() {
            if (!w || !cv.offsetParent) { return; }
            var cs = getComputedStyle(root);
            var line = cs.getPropertyValue('--fl-line');
            var cIon = cs.getPropertyValue('--fl-pos');
            var cEl = cs.getPropertyValue('--fl-neg');

            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            ctx.clearRect(0, 0, w, h);

            // силові лінії поля: радіус труби ∝ 1/sqrt(B)
            ctx.strokeStyle = line; ctx.lineWidth = 1.1;
            var nl = 9;
            for (var i = -nl; i <= nl; i++) {
                var r0 = i / nl * rho * 1.25;
                ctx.beginPath();
                for (var s = -1; s <= 1.0001; s += 0.04) {
                    var z = s * L * 1.12;
                    var u = z / L;
                    var y = r0 / Math.sqrt(1 + (R - 1) * u * u);
                    if (s === -1) { ctx.moveTo(cx + z, cy + y); } else { ctx.lineTo(cx + z, cy + y); }
                }
                ctx.stroke();
            }
            // котушки (де поле сильніше)
            ctx.lineWidth = 2.2; ctx.globalAlpha = 0.7;
            [-1, 1].forEach(function (sg) {
                ctx.beginPath();
                ctx.ellipse(cx + sg * L * 1.05, cy, 6, rho * 1.55 / Math.sqrt(R), 0, 0, 2 * Math.PI);
                ctx.stroke();
            });
            ctx.globalAlpha = 1;

            // сліди й частинки
            ctx.lineWidth = 1.4; ctx.lineCap = 'round';
            parts.forEach(function (p) {
                var t = p.trail, m = t.length / 2;
                if (m < 2) { return; }
                ctx.strokeStyle = p.ion ? cIon : cEl;
                for (var j = 1; j < m; j++) {
                    ctx.globalAlpha = 0.55 * j / m;
                    ctx.beginPath();
                    ctx.moveTo(t[2 * j - 2], t[2 * j - 1]);
                    ctx.lineTo(t[2 * j], t[2 * j + 1]);
                    ctx.stroke();
                }
                ctx.globalAlpha = 0.95;
                ctx.fillStyle = p.ion ? cIon : cEl;
                ctx.beginPath();
                ctx.arc(t[2 * m - 2], t[2 * m - 1], p.ion ? 3.2 : 2.2, 0, 2 * Math.PI);
                ctx.fill();
            });
            ctx.globalAlpha = 1;
        }

        var last = 0;
        function frame(ts) {
            raf = 0;
            var dt = Math.min(0.05, (ts - last) / 1000 || 0.016); last = ts;
            R += (Rtarget - R) * 0.06;
            step(dt);
            draw();
            if (visible && !document.hidden) { raf = requestAnimationFrame(frame); }
        }
        function start() { if (!raf && !reduce) { last = performance.now(); raf = requestAnimationFrame(frame); } }

        function resize() {
            var r = hero.getBoundingClientRect();
            dpr = Math.min(window.devicePixelRatio || 1, 2);
            w = r.width; h = r.height;
            cv.width = Math.round(w * dpr);
            cv.height = Math.round(h * dpr);
            layout();
            init();
            if (reduce) { for (var k = 0; k < 60; k++) { step(0.03); } }
            draw();
        }

        hero.addEventListener('pointermove', function (e) {
            var r = hero.getBoundingClientRect();
            var f = Math.min(1, Math.max(0, (e.clientY - r.top) / r.height));
            Rtarget = 1.5 + 6 * (1 - f);            // вгору — сильніше дзеркало
        });

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (en) {
                visible = en[0].isIntersecting;
                if (visible) { start(); }
            }).observe(hero);
        }
        document.addEventListener('visibilitychange', function () { if (!document.hidden) { start(); } });
        window.addEventListener('resize', resize);
        if (themeToggle) { themeToggle.addEventListener('click', draw); }
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(function () { window.dispatchEvent(new Event('resize')); });
        }
        resize();
        start();
    })();
})();
