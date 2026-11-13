/* sims.js — картки симуляцій: розгортання по кліку, фільтр за розділом, відкриття за #якорем. */
(function () {
    'use strict';
    var grid = document.getElementById('sims-grid');
    if (!grid) { return; }
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.sim'));
    var chips = Array.prototype.slice.call(document.querySelectorAll('.sims-filters .chip'));
    var counter = document.getElementById('sims-count');

    function setOpen(card, open) {
        var btn = card.querySelector('.sim-head');
        card.classList.toggle('is-open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    function openOnly(card) {
        cards.forEach(function (c) { if (c !== card) { setOpen(c, false); } });
        setOpen(card, true);
        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        card.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
        try { history.replaceState(null, '', '#' + card.id); } catch (e) { /* ignore */ }
    }

    cards.forEach(function (card) {
        card.querySelector('.sim-head').addEventListener('click', function () {
            if (card.classList.contains('is-open')) {
                setOpen(card, false);
                try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* ignore */ }
            } else {
                openOnly(card);
            }
        });
    });

    function applyFilter(key) {
        var shown = 0;
        cards.forEach(function (c) {
            var ok = key === 'all' || (key === 'lab' ? c.dataset.kind === 'lab' : c.dataset.ch === key);
            c.hidden = !ok;
            if (ok) { shown++; } else { setOpen(c, false); }
        });
        chips.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.filter === key ? 'true' : 'false'); });
        if (counter) { counter.textContent = shown + ' з ' + cards.length; }
    }
    chips.forEach(function (b) { b.addEventListener('click', function () { applyFilter(b.dataset.filter); }); });

    function fromHash() {
        var id = decodeURIComponent((location.hash || '').slice(1));
        var card = id && document.getElementById(id);
        if (card && card.classList.contains('sim')) {
            if (card.hidden) { applyFilter('all'); }
            openOnly(card);
        }
    }
    window.addEventListener('hashchange', fromHash);
    applyFilter('all');
    fromHash();
})();
