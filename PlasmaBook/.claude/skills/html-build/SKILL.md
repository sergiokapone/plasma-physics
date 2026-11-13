---
name: html-build
description: Як збирати й публікувати HTML-варіант PlasmaBook через lwarp (online/) — де що лежить (html/), команда html\build-html.ps1, стадії, пастки lwarp/TeX Live 2026, відомі проблеми. Використовуй, коли треба зібрати, налагодити чи оновити HTML-версію («зроби html», «перезбери online», «чому не збирається lwarp»).
---

# HTML-варіант книги (lwarp) — стан: конвеєр працює (2026-11-13)

Книга публікується як статичний сайт у `D:\Projects\LaTeX\plasma-physics\online\` (поруч з `index.html`, `simulations.html`; GitHub Pages у корені, URL `.../online/`). Кнопка «Читати онлайн» у лендінгу (`make_site.py`, веде на `online/`). Портовано з `D:\Projects\LaTeX\ElMag\ElMagConspect` (його `README-html.md` — довідка про ідеї).

## Де що лежить

Усе джерельне — у **`PlasmaBook\html\`**; корінь PlasmaBook після збірки лишається таким, як був.

| Шлях | Що |
|---|---|
| `html/build-html.ps1` | єдина команда збірки й чистки |
| `html/main-html.tex`, `html/ConspectBookHTML.cls` | HTML-варіант `main.tex` і класу (копіюються в корінь на час збірки) |
| `html/tools/` | `prepare_html.py`, `publish_html.py`, `html_patches.py`, `mathjax2lwarp.py`, `check-mathjax-html.js`, `svg_optimize.py` |
| `html/assets/` | джерела `book.js`, `conspect.css`, `fonts/` (публікація копіює їх в `online/assets/`) |
| `html/lwarpmk.conf` | довідковий (збірка пише власний у корені й видаляє) |
| `html/cache/ext/` | кеш рисунків, зібраних окремо (git-ignored) |
| `html/logs/` | журнали останньої збірки й `build-error.txt` (git-ignored) |
| `html/node_modules/` | `mathjax-full@3` для перевірки формул (`cd html; npm i mathjax-full@3`; git-ignored) |
| `online/` | готова книга: `ch1.html`…, `index.html` (копія `main-html.html`), `assets/`, `main-html-images/`, `pagefind/`, каталоги з рисунками розділів |

`.gitignore` (корінь репозиторію) закриває тимчасове: `PlasmaBook/main-html*`, `_html/`, `lwarp*`, `lateximage*`, `ConspectBookHTML.cls`, `html/logs|cache|node_modules|_test`.

## Команда

```
powershell/pwsh -NoProfile -File PlasmaBook\html\build-html.ps1 [-Placeholder] [-NoImages] [-SkipPrepare] [-NoPublish] [-Keep] [-Full] [-OutDir ..\online] [-Chapters Scales -OutDir html\_test]
```
Повна збірка ~6 хв (12 розділів, ~13,7 тис. формул, ~75 рисунків). Вивід буферизується файлом, тому запускати у фоні (`run_in_background`) і чекати сповіщення; **не** поллити. Дві збірки одночасно — ніколи. `-Chapters X,Y` — швидка проба (решта посилань «undefined» — норма; публікувати в `html\_test`, не в `online`).

Після оновлення лендінгу: `python PlasmaBook\make_site.py` (перегенерує `index.html` і `simulations.html`).

## Стадії build-html.ps1

0. Резерв `<Розділ>/<Розділ>-Answers.tex` (HTML-прохід їх **переписує**, чистка повертає), копіювання `main-html.tex` і класу в корінь, відновлення кешу `_html/ext`.
1. `prepare_html.py --shared` (шматки `ConspectBook.cls` → `_html/shared-*.tex`), `mathjax2lwarp.py _html/shared-mathmacros.tex lwarp-mathjax.tex`, `prepare_html.py` (копії розділів у `_html/`, tikz, таблиці).
2. `lualatex -shell-escape main-html` (друкований прохід) → `prepare_html.py --tags` → `biber` → копія `.bbl` у `main-html_html.bbl`.
3. `lwarpmk again` + `lwarpmk html`.
4. Перевірки: undefined/rerun у логу, «^» (ліґатури), MathJax-перевірка всіх формул.
5. `lwarpmk limages` (+ ремонт порожніх SVG).
6. `publish_html.py --out ..\online` + Pagefind (`npx pagefind`, потрібен інтернет перший раз).
7. **Чистка (блок `finally`, навіть після помилки; вимикає `-Keep`)**: логи → `html/logs`, кеш → `html/cache`, видаляються `main-html*.*`, `lwarp*`, `lateximage*`, `comment_*.cut`, `sample_project.css`, `ConspectBookHTML.cls`, `_html`, `main-html-images`, SVG з `*/Pictures/*.pdf`; `*-Answers.tex` відновлюються. Перевірка: `git status` має показувати лише `html/`, `online/` та задумані зміни.

## Що робить prepare_html.py (відмінності від ElMag)

- Шматки класу вирізаються за банерами: «Кольори», **«Рисування»** (не «Рисунки»), `\RequirePackage{emf}`…`\AtBeginDocument{}`, `\emphx`, гілка `\ifbiblatex`.
- Копії в `_html/` роблять: корені `preface`, `Notation`, `SGStoSI`, `cheatsheet`, `Glossary` і розділи; блок «Підсумки/Висновки/Корисні ресурси» **вирізається з `main.tex`** (`\chapter*{Підсумки}` … `\answers`) у `_html/summary.tex`.
- `platbl` (+`tblr`/`longtblr`) → `tabularx` (шапка на `themecolorlight!28`, сітка); усі 25 таблиць книги конвертуються у справжні `<table>`.
- `(с.~\pageref{…})` вирізається (у HTML сторінок нема; це Словник і Позначення).
- `\texorpdfstring{A}{B}`, де B має `_ ^ \ < >`, → B порожнє (lwarp друкує B у текстовому режимі: `R_m >> 1` дає «Missing $»).
- `\tikzmark*`, `\tag{\theequation}`, `\ce` у підписах — як в ElMag.

## Пастки (нове з PlasmaBook, TeX Live 2026)

- Банер tikz у PlasmaBook називається «Рисування: TikZ, PGFPlots, CircuiTikz».
- **Величезні SVG**: `pdftocairo` розгортає градієнти (4 рисунки 9–44 МБ). `publish_html.py` (крок 2b) заміняє SVG > 3 МБ на PNG 170 dpi: PDF-сторінка береться з `main-html_html.pdf` за номером із `main-html-images.txt` (`pdfseparate` → `pdfcrop` → `pdftocairo -png -transp`), посилання в сторінках переписуються. Без цього публікація вішається на `svg_optimize` (21 МБ SVG) і сайт важить ~100 МБ; з PNG ~11 МБ.
- **alt рисунків**: lwarp дає кожному `lateximage` `alt="(-tikz- diagram)"` (або `(-forest- diagram)` для forest, `(figure)`, `(table)`). `fix_alt` у `publish_html.py` бере підпис (`div.figurecaption`/`tablecaption`), що йде за картинкою до `</figure>`/наступного `<img>` (TeX-формули зводяться до тексту, до 240 знаків), інакше «Рисунок N» (N — порядок на сторінці). Жодного «-tikz-» у `online/` лишатись не повинно (перевірка в `html-check`).
- **`online/index.html`** — копія домашньої сторінки книги (`main-html.html`), рішення користувача: перенаправлення не робити; лендінг веде на `online/`.
- lwarp на Windows пише в `src` зворотні скісні (`main-html-images\image-7.svg`): `publish_html.py` замінює на `/`.
- Символи ★☆ (`\lvl`) відсутні в BookmanOldStyle; lwarp читає текст із PDF, і замість них виходить U+FFFD. Клас бере `DejaVu Sans` (`\lvlfont`).
- `*-Answers.tex` під версіями git: HTML-прохід їх перезаписує, тому резерв/відновлення в скрипті.
- `lwarpmk` лишає `comment_*.cut`, `sample_project.css` у корені — чистка їх бачить.
- Сповіщення Windows: `texlogsieve` каже «got confused» на `main-html.log` — це фон, дивитися `grep "^!"`.
- Помилка «file being read: ./Fluid/tikz/beta.tikz» у `build-error.txt` — лише евристика (останній згаданий файл), реальний рядок дає `l.NNN`.
- Стандартні: ліґатури JetBrains Mono (`RawFeature={-calt,-liga}`), MathJax 3 (не 4), `\nameref*` відкидається, `\chapter*` потребує `\ForceHTMLPage`, після зміни класу — `lwarpmk again` (скрипт робить сам).

## Відомі проблеми / що не перевірено

- Рисунки 5, 7, 9, 13, 19 (tikz/pgfplots із шейдингом) — PNG, а не вектор (дрібний текст на них не масштабується).
- `publish_html.py --patch-only` застосовує лише `IMG_STYLE`/`FIG_CLASS`; `fix_alt` працює тільки в повній публікації.
- Посилання на симуляції (`\simlink`) ведуть на повну адресу `https://sergiokapone.github.io/plasma-physics/PlasmaBook/sims/...`; `\simlink[Назва]` з `\simlist` у книзі не вживано.
- `Questions` у HTML без запису в змісті (`\tocunnum` порожній).
- Перша сторінка (`ch1` = Передмова) входить у нумерацію `chN.html`: розділи книги — `ch2`…`ch13`, Підсумки `ch14`, Відповіді `ch15`, Додатки `ch16`, Словник `ch17`, Література `ch18`.

## Принципи (як в ElMag)

- Розділи, `ConspectBook.cls`, `main.tex`, `.bib` не змінювати. Виправлення: клас → усе; `prepare_html.py` → патерн у розділах; `html_patches.py` + `publish_html.py --patch-only` → один рисунок; CSS/JS → вигляд.
- Згенероване (`online/*.html`, `_html/`) руками не правити.
- Файли з LaTeX/кирилицею правити Edit/Write, не sed/heredoc.
- Після змін публікації — скіл `html-check`.
