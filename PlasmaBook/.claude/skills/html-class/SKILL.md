---
name: html-class
description: Як вести ConspectBookHTML.cls і prepare_html.py — відповідність друкованих середовищ і макросів HTML-блокам, наслідування шматків ConspectBook.cls, макроси MathJax, CSS-класи cb-*. Використовуй, коли в друкований клас додано нове середовище, макрос чи пакет і треба, щоб воно працювало в HTML, або коли HTML-сторінка виглядає інакше, ніж PDF.
---

# HTML-клас і відповідність друку

Принцип ElMag: **друкований клас `ConspectBook.cls` не чіпаємо, розділи не чіпаємо.** Усе, що HTML потрібне інакше, — у `html/ConspectBookHTML.cls`, `html/tools/prepare_html.py` (копії розділів у `_html/`) і `html/assets/conspect.css`. Клас, `main-html.tex` і CSS уже портовано (2026-11-13); збірка й розкладка тек — скіл `html-build`. Усі шляхи нижче відносно `PlasmaBook/html/`.

## Правило синхронності

Будь-що нове в `ConspectBook.cls` (середовище, макрос, пакет) **має мати відповідник у HTML-класі** — інакше lwarp падає з «Undefined control sequence» на першому ж розділі, де це вжито. Тому, додаючи в друкований клас, одразу питати: чи це потрапить у HTML само (через `shared-*.tex`) чи треба окреме визначення?

### Що наслідується автоматично (`build_shared` вирізає з `ConspectBook.cls` за банерами)

| Частина | Якір у друкованому класі |
|---|---|
| кольори | банер «Кольори…» |
| tikz, pgfplots, circuitikz і всі стилі малюнків | банер «Рисування: TikZ, PGFPlots, CircuiTikz» (код шукає за префіксом `Рисування`; так само в ElMag) |
| математичні макроси | від `\RequirePackage{emf}` до кінця наступного `\AtBeginDocument{…}` |
| `\emphx` | активне `\NewDocumentCommand{\emphx}` |
| biblatex | гілка `\ifbiblatex … \else` |

Якорі — крихкі: якщо назву банера змінено, у `_html/shared-<частина>.tex` буде «NOT FOUND» і попередження в консолі. Після правки банера запускати `python tools/prepare_html.py` і дивитись на WARNING.

Банер = п'ять рядків: `%=====…` / `%` / `%<таби>Назва` / `%` / `%=====…` (довжина лінії ≥ 20 `=`).

### Що визначається окремо в `ConspectBookHTML.cls` (простіші HTML-версії)

| Друк | HTML |
|---|---|
| `Theory`, `Attention`, `Example`, `Historical`, `Simulation`, `Questions`, `pict`, `tornpage`, `answerbox` (tcolorbox) | `\newenvironment{…}{\begin{BlockClass}{cb-…}…}{\end{BlockClass}}`; стилі `cb-*` у `conspect.css` |
| **`Estimate`, `Summary`** (є лише в PlasmaBook) | **зроблено**: `cb-estimate` (зелена), `cb-summary` (синя смуга) у класі й `conspect.css`. Нове tcolorbox-середовище в друці → додати так само (`grep -n "newtcolorbox" ConspectBook.cls`) |
| `problem`, `Solution` | ntheorem + `answers`; задача має `\hypertarget{problem:N}`, відповідь — `\hyperlink`; посилання «[відповідь]» і назад (перевірено: 0 битих якорів) |
| `\lvl{N}` | **зроблено**: ★☆ текстом шрифтом `DejaVu Sans` (`\lvlfont`); у книжному шрифті гліфів нема, lwarp читає текст із PDF → U+FFFD |
| `\glossbadge` (Словник) | **зроблено**: простий заголовок літери (у друці визначено в класі) |
| `\FloatBarrier` | порожній `\providecommand` |
| alt рисунків (lateximage) | не в класі: `fix_alt` у `publish_html.py` (підпис або «Рисунок N») |
| `\texorpdfstring{A}{B}` | у копіях розділів B із `_ ^ \ < >` стає порожнім (`strip_texorpdf` у prepare_html.py) |
| `(с.~\pageref{…})` | вирізається в копіях (Словник, Позначення) |
| `wrapstuff` | звичайний `figure` |
| `\Needspace`, `\tcbset` | порожні (`\providecommand`) |
| `\tcbhighmath` | `\boxed` у LaTeX; для MathJax — у `ALWAYS` |
| `platbl` / `tblr` / `longtblr` | `prepare_html.py` → `tabularx` у копіях; лишок → `lateximage[table]` |
| `\printindex`, `\index` | порожньо (покажчика в HTML немає) |
| `\simlink`, `\simlist` | `ConspectSims.sty` спільний; база адрес — одне місце |
| `\chapter*` (Відповіді, Додатки, Література) | `\schapterpage{…}` (власна сторінка + запис у змісті) |
| `\nameref*` | зірочка відкидається |
| `\phantomsection` | порожній (lwarp робить із нього `\section*{}`) |

## Макроси для MathJax

Ланцюжок: `mathjax-macros.tex` (генерується TSS Workflow) → `tools/mathjax2lwarp.py` → `lwarp-mathjax.tex` (`\CustomizeMathJax`).

- Нове формульне визначення в друкованому класі: після `build-html` запустити `check-mathjax-html.js` — він покаже невизначені макроси.
- Макрос, який MathJax має знати завжди, або який генератор губить, — у словник `ALWAYS` у `mathjax2lwarp.py`; макрос, що в MathJax виглядає інакше, ніж у друці, — в `OVERRIDES`.
- Шрифти й `\mathcal`: `\emf` у друці — BOONDOX-cal, у MathJax `\mathcal{E}` (близько, не ідентично); на сторінці символ U+2130 малюється веб-шрифтом STIX Two Math (`fix_emf` у `publish_html.py`).
- У PlasmaBook немає окремого `mathjax-macros.tex`: `mathjax2lwarp.py` читає `_html/shared-mathmacros.tex` (шматок `ConspectBook.cls`), приводить `\def`/`\let` до `\newcommand`, `\symbf` → `\mathbf`. `\mitomega`, `\mittheta`, `\mitphi`, `\mitlambda` додано в `ALWAYS`. Перевірка: `check-mathjax-html.js` — 13755 формул, 0 помилок.
- Нове формульне визначення в друці автоматично потрапляє в MathJax, якщо стоїть між `\RequirePackage{emf}` і першим `\AtBeginDocument{…}` класу; інакше додати в `ALWAYS`.

## Що робити, коли HTML виглядає інакше, ніж PDF

1. Зрозуміти, чи це дефект класу/конвертера (виправляти тут) чи властивість HTML (немає сторінок, `\Needspace`, `wrapstuff`). Властивості HTML — не дефект.
2. Одне місце виправлення: клас (для всього), `prepare_html.py` (для патерну в розділах), `html_patches.py` (для одного рисунка), `conspect.css`/`book.js` (вигляд).
3. Розділи й друкований клас не правити заради HTML. Якщо без цього ніяк (наприклад, розділ містить код, який lwarp не переварює), домовитися з користувачем: краще змінити розділ так, щоб і друк, і HTML були чисті, але це рішення користувача.
4. Перевірити скілом `html-check`.
