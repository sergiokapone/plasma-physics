#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Генерує ../index.html (сторінка навчального посібника для GitHub Pages) зі змісту main.toc.

Запуск (після збірки книги):  python -I make_site.py

Посилання у змісті ведуть в іменовані точки призначення PDF (\\hypertarget у ConspectBook.cls):
  розділ N        -> ch<N>
  підрозділ N.M   -> s<N>.<M>
  решта (Передмова, Підсумки, Відповіді, Додатки, Словник, Література) -> фіксовані імена нижче.
Тому зміст сайту завжди збігається з книгою: нумерація й назви беруться з main.toc.
"""
import re
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOC = HERE / "main.toc"
OUT = HERE.parent / "index.html"
PDF = "PlasmaBook/main.pdf"
SITE = "https://sergiokapone.github.io/plasma-physics/"

# Ненумеровані записи змісту -> ім'я точки призначення (див. \hypertarget у .tex/.cls)
NAMED = {
    "Передмова": "preface",
    "Підсумки": "summary",
    "Відповіді": "answers",
    "Словник термінів": "glossary",
    "Література": "bibliography",
}
# Додатки (нумерація літерами) -> ім'я
APPENDIX = {
    "А": "app-notation",
    "Б": "app-sgs-si",
    "В": "app-cheatsheet",
}
SKIP = {"Зміст", "Додатки", "Задачі", "Контрольні питання"}

ENTRY = re.compile(r"\\contentsline \{(\w+)\}\{(.*)\}\{(\d+)\}\{[^}]*\}%?\s*$")


def tex2html(s: str) -> str:
    """Мінімальне перетворення назв із main.toc у HTML."""
    s = s.replace("---", "—").replace("--", "–").replace("~", " ")
    s = s.replace("\\mittheta ", "θ").replace("\\mitomega ", "ω")
    s = re.sub(r"\$([^$]*)\$", lambda m: "<i>%s</i>" % m.group(1).strip(), s)
    return s


def link(dest: str) -> str:
    return "%s#nameddest=%s" % (PDF, dest)


def parse():
    chapters = []   # [{num, title, dest, subs:[(label, title, dest)]}]
    extra = {"front": [], "appendix": [], "back": []}
    cur = None
    for line in TOC.read_text(encoding="utf-8").splitlines():
        m = ENTRY.match(line)
        if not m:
            continue
        kind, body, _page = m.groups()
        nm = re.match(r"\\numberline \{([^}]*)\}(.*)$", body)
        num, title = (nm.group(1), nm.group(2)) if nm else ("", body)
        title = title.strip()
        if title in SKIP:
            continue
        if kind == "chapter" and num:
            cur = {"num": num, "title": title, "dest": "ch%s" % num, "subs": []}
            chapters.append(cur)
        elif kind == "section" and num and re.fullmatch(r"\d+\.\d+", num):
            cur["subs"].append((num, title, "s%s" % num))
        elif kind == "section" and num in APPENDIX:
            extra["appendix"].append((num, title, APPENDIX[num]))
        elif title in NAMED:
            bucket = "front" if title == "Передмова" else "back"
            if title == "Словник термінів" or title == "Література":
                bucket = "back2"
            extra.setdefault(bucket, []).append(("", title, NAMED[title]))
    return chapters, extra


def render_toc(chapters, extra) -> str:
    out = []
    a = out.append
    a('        <div class="section" id="toc-section">')
    a('            <h2 class="section-heading">Зміст</h2>')
    a('            <div class="toc-controls">')
    a('                <button type="button" id="toc-expand-all" class="toc-ctrl-btn">Розгорнути все</button>')
    a('                <button type="button" id="toc-collapse-all" class="toc-ctrl-btn">Згорнути все</button>')
    a("            </div>")
    a('            <ul class="toc-list toc-preamble">')
    for _l, t, d in extra["front"]:
        a('                <li><a href="%s" class="toc-title">%s</a></li>' % (link(d), escape(t)))
    a("            </ul>")
    a("        </div>")
    a("")
    a('        <div class="section">')
    a('            <ul class="toc-list">')
    for ch in chapters:
        a("                <li>")
        a('                    <span class="toc-num">%s</span>' % ch["num"])
        a('                    <a href="%s" class="toc-title">%s</a>' % (link(ch["dest"]), tex2html(ch["title"])))
        if ch["subs"]:
            a('                    <ul class="sub-list">')
            for lab, t, d in ch["subs"]:
                a('                        <li><a href="%s">%s %s</a></li>' % (link(d), lab, tex2html(t)))
            a("                    </ul>")
        a("                </li>")
    a("            </ul>")
    a("        </div>")
    a("")
    tail = extra["back"] + extra["appendix"] + extra.get("back2", [])
    if tail:
        a('        <div class="section section-appendix">')
        a('            <h2 class="section-heading">Підсумки, додатки, словник</h2>')
        a('            <ul class="toc-list">')
        for lab, t, d in tail:
            num = '                    <span class="toc-num">%s</span>\n' % lab if lab else ""
            a("                <li>\n%s                    <a href=\"%s\" class=\"toc-title\">%s</a>\n                </li>"
              % (num, link(d), tex2html(t)))
        a("            </ul>")
        a("        </div>")
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">

    <title>Фізика плазми | Навчальний посібник</title>
    <meta name="description" content="Навчальний посібник з фізики плазми для студентів-прикладних фізиків: від іонізації та дебаївського екранування до хвиль, нестійкостей, магнітного утримання й термоядерного синтезу.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="@SITE@">

    <meta property="og:title" content="Фізика плазми | Навчальний посібник">
    <meta property="og:description" content="Навчальний посібник з фізики плазми: 12 розділів, задачі з відповідями, інтерактивні симуляції.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="@SITE@">

    <!-- Дизайн і тема застосовуються до першого малювання, щоб не мигало -->
    <script>(function(){var r=document.documentElement;try{var d=localStorage.getItem('plasma-design');r.setAttribute('data-design',['field','blueprint','book'].indexOf(d)>-1?d:'field');var t=localStorage.getItem('plasma-theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme: dark)').matches)){r.classList.add('dark');}}catch(e){r.setAttribute('data-design','field');}})();</script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&family=Literata:ital,opsz,wght@0,7..72,400..600;1,7..72,400..600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">

    <link rel="stylesheet" href="assets/styles.css">
    <link rel="stylesheet" href="assets/designs.css">
    <style>
        .hero-actions{display:flex;flex-wrap:wrap;justify-content:center;gap:.8rem;position:relative;z-index:1}
        .pdf-button-primary{background:var(--gold);border-color:var(--gold);color:#1b0e0c}
        .pdf-button-primary .btn-icon{color:inherit}
        .pdf-button-primary:hover{background:var(--gold-bright);border-color:var(--gold-bright);color:#1b0e0c}
    </style>
</head>
<body>
<div class="container">

    <div class="pdf-hero">
        <div class="hero-tools">
            <div class="design-switch" role="group" aria-label="Дизайн сторінки">
                <button type="button" data-design="field" aria-pressed="true">Поле</button>
                <button type="button" data-design="blueprint" aria-pressed="false">Креслення</button>
                <button type="button" data-design="book" aria-pressed="false">Книга</button>
            </div>
            <button class="theme-toggle" id="theme-toggle" type="button" title="Перемкнути тему" aria-label="Перемкнути тему">🌙</button>
        </div>
        <h1>Фізика плазми</h1>
        <div class="subtitle">Навчальний посібник</div>
        <div class="hero-rule"></div>
        <div class="hero-actions">
            <a href="@PDF@" class="pdf-button pdf-button-primary">
                <span class="btn-icon">&#8595;</span> Завантажити посібник (PDF)
            </a>
            <a href="simulations.html" class="pdf-button">
                <span class="btn-icon">&#9657;</span> Інтерактивні симуляції
            </a>
        </div>
        <p class="pdf-note">Повна версія у форматі PDF. Пункти змісту нижче відкривають PDF на потрібному місці.</p>
    </div>

    <div class="content">

        <!-- Автор -->
        <div class="section">
            <h2 class="section-heading">Автор</h2>
            <div class="authors">
                <div class="author-card">
                    <img class="author-photo"
                         src="https://apd.ipt.kpi.ua/wp-content/uploads/2025/01/MyPhoto2.jpg"
                         alt="Сергій Пономаренко" loading="lazy"
                         onerror="this.onerror=null; this.src='https://via.placeholder.com/110x110?text=С.М.+Пономаренко';">
                    <strong>
                        <a href="https://apd.ipt.kpi.ua/kafedra/stuff/ponomarenko/" target="_blank">
                            Пономаренко Сергій Миколайович
                        </a>
                    </strong>
                    <p>Кандидат фізико-математичних наук, доцент кафедри прикладної фізики КПІ ім. Ігоря Сікорського.</p>
                </div>
            </div>
        </div>

        <!-- Про посібник -->
        <div class="preface">
            <h2>Про посібник</h2>
            <p>Навчальний посібник з курсу <strong>«Фізика плазми»</strong> розрахований на студентів-прикладних фізиків, які вже знають загальну й теоретичну фізику. Він веде від умов, за яких іонізований газ стає плазмою (іонізація, дебаївське екранування, колективність), через хвилі, рух частинок, зіткнення, рідинний і кінетичний опис до нестійкостей, магнітного утримання, термоядерного синтезу й газового розряду.</p>
            <p>Викладення спирається на оцінки величин: у розділах є рамки <em>Estimate</em> з числовими прикладами, блоки «Як це вимірюють» про діагностику плазми, задачі з розв'язками й контрольні питання, а також посилання на інтерактивні симуляції. Використано гауссову систему одиниць, температуру подано в енергетичних одиницях ($k_B=1$); у додатку є перехід до СІ.</p>
        </div>

        <!-- ── Зміст ─────────────────────────────────────────────────── -->
@TOC@
        <!-- ── /Зміст ──────────────────────────────────────────────────── -->

        <hr>
        <p class="ref-links">
            <a href="https://apd.ipt.kpi.ua/kafedra/stuff/ponomarenko/" target="_blank">Пономаренко С.М.</a>
        </p>

    </div><!-- /content -->

    <footer>
        Фізика плазми &nbsp;|&nbsp; Навчальний посібник<br>
        Кафедра прикладної фізики, КПІ ім. Ігоря Сікорського
    </footer>

</div><!-- /container -->

<button class="back-to-top" id="back-to-top" type="button" title="Нагору" aria-label="Прогорнути нагору">↑</button>

<script src="assets/script.js"></script>
</body>
</html>
"""


def main() -> int:
    if not TOC.exists():
        print("Немає main.toc — спершу зберіть книгу (build.ps1).")
        return 1
    chapters, extra = parse()
    if not chapters:
        print("У main.toc не знайдено розділів.")
        return 1
    html = (TEMPLATE.replace("@TOC@", render_toc(chapters, extra))
            .replace("@PDF@", PDF).replace("@SITE@", SITE))
    # $k_B=1$ у тексті «Про посібник» — без MathJax виглядає як формула у доларах; прибираємо
    html = html.replace("($k_B=1$)", "(<i>k</i><sub>B</sub> = 1)")
    OUT.write_text(html, encoding="utf-8", newline="\n")
    nsub = sum(len(c["subs"]) for c in chapters)
    print("index.html: %d розділів, %d підрозділів -> %s" % (len(chapters), nsub, OUT))
    sys.path.insert(0, str(HERE))   # python -I не додає теку скрипта до шляху імпорту
    import make_sims_page   # сторінка симуляцій (../simulations.html)
    return make_sims_page.main()


if __name__ == "__main__":
    sys.exit(main())
