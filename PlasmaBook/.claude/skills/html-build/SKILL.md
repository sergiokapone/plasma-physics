---
name: html-build
description: Як збирати й публікувати HTML-варіант книги через lwarp (досвід ElMagConspect) — конвеєр build-html.ps1 → prepare_html.py → lwarp → publish_html.py, MathJax, картинки, пастки lwarp, що вже є в PlasmaBook, а що ще треба перенести з ElMag. Використовуй, коли треба зібрати, налагодити чи портувати HTML-версію («зроби html», «чому не збирається lwarp», «перенеси конвеєр з ElMag»).
---

# HTML-варіант книги (lwarp)

**Стан у PlasmaBook (2026-11-13): HTML-конвеєра ще немає.** Є лише PDF і лендінг `../index.html` (GitHub Pages у корені репозиторію). Робочий зразок — `D:\Projects\LaTeX\ElMag\ElMagConspect\` (там HTML-версія виходить у `docs/`, її читають онлайн). Нижче — що там зроблено й що з цього переносити. Деталі ElMag: `README-html.md`, `.claude/rules/html-build.md` у тій теці.

## Конвеєр ElMag (7 стадій `tools/build-html.ps1`)

1. **Підготовка.** `mathjax2lwarp.py` (макроси формул → `lwarp-mathjax.tex`), `prepare_html.py` (див. нижче).
2. **Друкований прохід** `lualatex -shell-escape main-html` + `biber`; номери для `\tag{\theequation …}` беруться з `main-html.aux` (`prepare_html.py --tags`). `.bbl` копіюється в `main-html_html.bbl`.
3. **`lwarpmk again` + `lwarpmk html`** — довго (у ElMag ~15 хв на 20 розділів); одна сторінка HTML на розділ (`ch1.html`…), `HTMLFilename={ch}`, `FileDepth=0`.
4. **Перевірки:** `texlogsieve` журналів, `check-mathjax-html.js` (кожна формула сторінки крізь MathJax; потрібен `npm i mathjax-full@3`).
5. **Картинки:** `lwarpmk limages` (усе, що lwarp не вміє, — tikz-малюнки, таблиці — стає зображеннями).
6. **Публікація:** `publish_html.py` переносить сайт у `docs/` (чистить її перед кожним запуском, крім `SITE_OWN`), переписує посилання на `assets/`, додає `book.js`, Pagefind-пошук, `§` у заголовках, `svg_optimize.py` стискає SVG.
7. **Прибирання** тимчасових файлів (`clwarp-clean.ps1`).

Усе запускається однією командою (`python elmag.py html` з прапорцями `-SkipPrepare`, `-NoImages`, `-Placeholder`, `-Full`, `-NoPublish`, `-OutDir`). На помилці скрипт пише першу помилку LaTeX із контекстом у `build-error.txt`.

## Головні принципи

- **Розділи не змінюються.** Усе, що не подобається lwarp, виправляє `prepare_html.py`, записуючи **копії** у `_html/<Розділ>/…`; клас читає копію першою (`\multiinclude`, `\localinput`, `\htmlinput`).
- **Окремий клас** `ConspectBookHTML.cls` (lwarp), друкований клас не чіпати. Шматки друкованого класу (кольори, tikz-стилі, математичні макроси, `\emphx`, biblatex) **вирізаються з `ConspectBook.cls` автоматично** за заголовками-банерами (`build_shared` у `prepare_html.py` → `_html/shared-*.tex`), тож зміни друкованого класу доходять до HTML самі. Звідси правило: **усе, що додано для друку, має існувати й в HTML-класі** (див. скіл `html-class`).
- **Згенероване не правити руками.** `docs/*.html` стираються при кожній публікації. Виправлення — у `publish_html.py` / `prepare_html.py` / `html_patches.py` / `docs/assets/{book.js,conspect.css}`. Правка `docs/` напряму — лише як попередній перегляд тієї самої зміни.
- **Точкові виправлення окремих рисунків** — `html_patches.py` (`IMG_STYLE`, `FIG_CLASS`); застосувати без перезбірки: `python publish_html.py --patch-only`.

## Що робить `prepare_html.py`

- PDF-картинки → SVG (`lwarpmk pdftosvg`).
- `*.tikz` із кодом **перед** `\begin{tikzpicture}` (`\tikzset`, `\def`): у HTML-режимі `$` не є math-shift і lwarp ламається. Файл із однією картинкою стає цілим зображенням; код при `subfigure/minipage/figure` виноситься в `lwarp-tikzdefs.tex` (преамбула).
- Малюнки з `name/.pic={…}` в опціях `tikzpicture` (нові pgf/lwarp падають): збираються **окремо** (`lualatex` → `pdfcrop` → `pdftocairo -svg`) у `_html/ext/pic-<hash>.svg`, вставляються як `\htmlpicture{…}`.
- `tblr`/`longtblr` → `tabularx` у копіях розділів (справжні HTML-таблиці, формули через MathJax); таблиці, яких конвертер не розуміє, лишаються `tblr` і стають зображеннями (скрипт їх перелічує).
- Формули: `\tikzmarknode{n}{x}` → `x`, `\tikzmark` та оверлейні `\tikz[...]` прибираються; `\tag{\theequation x}` отримує номер з `.aux`.
- `\ce` у `\caption` обгортається в `$…$` (lwarp 0.922 інакше падає).

## Пастки (з досвіду ElMag)

- **Ліґатури моноширинного шрифту** (JetBrains Mono `calt`): lwarp друкує HTML-теги моноширинним шрифтом, а `-->`, `</`, `//` стають ліґатурами, і `pdftotext` пише `^` (у тегах і у формулах). Лікується `RawFeature={-calt,-liga}` у `\setmonofont` HTML-класу.
- **MathJax 3**, не 4: lwarp 0.922 жорстко зашитий на `mathjax@3/es5/tex-svg.js`. Перенос формул у MathJax 3 не вміє, тому довгі display-формули розбиває `book.js`.
- **`mathjax-macros.tex`** (генерується окремо) може мовчки втрачати макроси при зміні класу (`\tcbhighmath` так загубився). Те, що MathJax має знати завжди, — у словнику `ALWAYS` у `mathjax2lwarp.py` (`\emf`, `\enquote`, `\allowbreak`, `\mitlambda`, `\tcbhighmath`…). Оператори babel (`\tg`, `\ctg`, `\sh`…) теж додаються там.
- **`\vect` → `\mathbf`** у MathJax (прямий жирний, як у друці).
- **lwarp не вміє `\nameref*`** (зірочка): HTML-клас її відкидає. `\phantomsection` у lwarp — порожній `\section*{}`: у HTML замінюється порожнім.
- **Зірочкова `\chapter*`** відкриває нову сторінку HTML лише після `\ForceHTMLPage` (`\schapterpage`): так зроблено «Відповіді», «Додатки», «Література», «Симуляції».
- **`\emphx{термін}[індекс]`**: необов'язковий `[…]` у HTML проковтується.
- **Кольорові колонки** `Q[…,bg=…]` вимкнено (`KEEP_COLUMN_COLORS`): lwarp пише їх як недійсні `<div>` усередині `<p>`.
- Після зміни класу: `lwarpmk again -p main-html`, інакше `lwarpmk` каже «up to date».
- Деякі SVG виходять величезними (до ~23 МБ: `pdftocairo` розгортає градієнти) — розглянути PNG для них.
- Старі `lwarpmk.conf` і `*.lwarpmkconf` перед першим проходом видаляються, щоб `--shell-escape` записався в конфігурацію.

## Що в PlasmaBook відрізняється від ElMag (треба врахувати при портуванні)

| Що | У PlasmaBook | Що робити в HTML |
|---|---|---|
| Середовища-бокси | `Theory, Attention, Example, Historical, Estimate, Simulation, Summary, Questions, pict, tornpage, answerbox` (tcolorbox) | у ElMag вже є блоки `cb-*`; **додати `Estimate` і `Summary`** (`cb-estimate`, `cb-summary`) у клас і CSS |
| Таблиці | єдине середовище `platbl` (`\NewTblrEnviron{platbl}`) і `longtblr` | `prepare_html.py` розуміє `tblr`/`longtblr`; **навчити його `platbl`** або звести до `tblr` у копіях |
| Рівень задач | `\lvl{1..3}` зірочки FontAwesome | визначити в HTML-класі (символи ★/☆ текстом) |
| Покажчик | `indextools` + `upmendex`, багато `\index{…}` | в HTML покажчика немає: `\printindex` = порожньо (як в ElMag), `\index` ігнорується |
| Симуляції | `ConspectSims.sty`, `\simlink`, `sims/*.html` | у ElMag вже спільний `ConspectSims`; у HTML посилання ведуть на `sims/` на сайті; перевірити шляхи при публікації |
| Розділи | розділ = `\chapter`, підрозділ `\section`; «Задачі» й «Контрольні питання» — `\section*` | `\setcounter{tocdepth}{1}`, перевірити відображення в бічному змісті |
| Відповіді | `\Writetofile{answer}{…}` у розділах, `<Розділ>-Answers.tex`, `\answers` | у ElMag той самий механізм (`answers`, `\schapterpage{Відповіді}`) |
| Іменовані точки PDF | `\hypertarget{ch N}`, `s N.M` у `titleformat` | у HTML не потрібні (lwarp робить власні якорі); посилання з лендінгу ведуть у PDF |
| Графіки | pgfplots зі спільним стилем у `\pgfplotsset` у `ConspectBook.cls` | потрапляє в `shared-tikz.tex`, якщо стоїть у банері «Рисунки: TikZ, PGFPlots, CircuiTikz» |
| Банери класу | `build_shared` шукає заголовки «Кольори», «Рисування» | у PlasmaBook банер називається **«Рисунки: TikZ, PGFPlots, CircuiTikz»** — змінити якір; перевірити решту якорів (`\RequirePackage{emf}`, `\emphx`, `\ifbiblatex`) |

## План портування (коли користувач скаже робити)

1. Скопіювати з ElMag `tools/{build-html.ps1, prepare_html.py, publish_html.py, html_patches.py, mathjax2lwarp.py, check-mathjax-html.js, svg_optimize.py, clwarp-clean.ps1}`, `ConspectBookHTML.cls`, `main-html.tex`, `lwarpmk.conf`, `docs/assets/{book.js, conspect.css}`; усі шляхи й назви (`ElMagConspect`, `elmag-…` у `localStorage`, список розділів, `\nocite`) замінити на PlasmaBook.
2. Побудувати `main-html.tex` зі списком розділів із `main.tex` (Basics … Scales), `\answers`, додатки `Notation`, `SGStoSI`, `cheatsheet`, `Glossary`, бібліографія.
3. Додати в HTML-клас `Estimate`, `Summary`, `\lvl`, `platbl`; адаптувати якорі `build_shared`.
4. Скласти один розділ (найкоротший) і лише потім усю книгу; `-Placeholder` допомагає, коли окремі рисунки не збираються.
5. Куди публікувати: лендінг лежить у корені (`index.html`, `assets/`); HTML-книгу покласти у `docs/` або в `book/` і додати кнопку «Читати онлайн» у `make_site.py`. Рішення за користувачем.

## Правила роботи

- Не запускати дві збірки lwarp одночасно в одній теці; повну збірку лише на прохання (довга).
- Не читати цілком `main-html_html.log` і `main.log`: `texlogsieve` або `grep -n "^!"` + контекст.
- Після змін публікації перевіряти скілом `html-check`.
