# PlasmaBook: notes for Claude

Український підручник «Елементи фізики плазми» (автор С. М. Пономаренко) для студентів прикладної фізики, які вже мають загальну й теоретичну фізику. LaTeX (**LuaLaTeX + biber**, клас `ConspectBook.cls`), СГС (гаусова), $k_B=1$ ($T$ в енергетичних одиницях). Вихід: друкований PDF (`main.pdf`) і HTML-сайт `../online/` (lwarp). Windows, PowerShell, MiKTeX.

Відповідай автору **українською**. Текст книги, зауваження й TeX-коментарі українською; коментарі в Python/PowerShell-скриптах англійською. Коміт і push **лише на прохання**, крім серії рецензування розділів, де це домовлено (див. нижче).

## Читай спочатку
- `STATUS_review.md` — де зупинилась рецензія, що відкрито (оновлюй наприкінці сесії). Інші: `STATUS_student_qa.md` (питання студента Q-NNN; розділ «Педагогічна лінія» читати першим), `STATUS_sims.md`, `STATUS_diagnostics.md`.
- `.claude/rules/conventions.md` — скелет розділу, середовища, навігація, терміни, типографіка (завантажується при роботі з `.tex`/`.cls`).
- `.claude/pitfalls.md` — відомі пастки: де «довірене» джерело помилялось. Прочитай перед фізичною читкою; нові дописуй одним рядком.
- `REVIEW_student.md` (1300 рядків) — архів вихідної рецензії; **не читай цілим**, шукай `grep`-ом.

## Карта проєкту
- `main.tex`: `CoverPage`, `preface`, далі два `\multiinclude`. Порядок розділів: Nature (розд. 0), Basics, Waves, Motion, Collisions, Fluid, LinearWaves, Kinetics, Instability, Confinement, Fusion, Discharge, Scales. Далі `\answers` (розділ «Відповіді»), додатки (`Notation`, `SGStoSI`, `cheatsheet`), `Glossary`, література, покажчик.
- Розділ = `<Розділ>/<Розділ>.tex` + `tikz/` (рисунки `\localinput{ім'я.tikz}`) + згенерований `<Розділ>-Answers.tex`.
- `bibliography/bibliography.bib` — єдина bib. `books/` (у `../`) — довідкові підручники (djvu + TOC), журнал `books/LOOKUPS.md`.
- `sims/*.html` — інтерактивні симуляції; `html/` — джерела HTML-збірки (`build-html.ps1`, `main-html.tex`, `ConspectBookHTML.cls`); `../Syllabus/` — силабуси; `../Presentations2/` — лекції за розділами.
- Згенероване, не джерела: `main.{aux,bbl,bcf,blg,idx,ilg,ind,log,toc,run.xml,fls,fdb_latexmk}`, `lualatex*.fls`, `sieve.txt`, `_chapters/`, `__pycache__`, `*-Answers.tex`. `.ind` вручну не правити.
- `.vscode/` не в git навмисно.

## Збірка (завжди через `build.ps1`, ніколи `pdflatex` / `latexmk -pdf` / `latexmk` напряму)
- **Запускати лише через `pwsh` (PowerShell 7), не `powershell`:** `build.ps1` у UTF-8 без BOM, Windows PowerShell 5.1 ламає кирилицю й скрипт не стартує.
- Один розділ: `pwsh -NoProfile -File build.ps1 -Chapter <Розділ>` → `_chapters/<Розділ>.pdf` (+ `-sieve.txt`). `??` для посилань на інші розділи — норма. **Перевірка й правка розділу — лише так**, не всю книгу.
- Журнал: у книзі стабільно ~100–104 Overfull (фон); дефект лише > 10 пт або в новому місці, дрібні 1–5 пт не лікувати. Попередження `Font shape … undefined` StixTwoMath ігнорувати. `sieve.txt` (texlogsieve) може бути в UTF-16. Помилка `main.toc:NN` — збій змісту (порожній аргумент `	oc@sign`).
- Вся книга: `build.ps1` (`-Clean` спершу чистить допоміжні). Лише наприкінці серії правок або на прохання; після неї завжди дивитись `main.log`/`sieve.txt` на undefined/multiply defined (їх має бути 0). Таймаут ≥ 600000 мс.
- **Не запускати дві збірки одночасно** і не правити джерела під час повної збірки (код 12, «undefined references»).
- Покажчик: після зміни лише `index-uk.ist` видалити `main.ind` і зібрати.
- HTML-версія: `pwsh -NoProfile -File html\build-html.ps1 -Placeholder` (~6 хв, у фоні); див. скіли `html-build`, `html-class`, `html-check`. Усе, що додано в `ConspectBook.cls`, має бути й в `ConspectBookHTML.cls`.
- Lint верстки PDF у проєкті немає; верстку перевіряють скіл `latex-layout-fix` і агент `layout-checker` — **лише на прохання**.

## Правила правки (критерій автора)
Правити текст лише за п'ятьма пунктами: (1) фактична/числова помилка, (2) суперечність, (3) символ чи термін до означення, (4) прогалина в логіці, (5) дефект збірки/верстки (помилка, undefined ref, overfull > 10 пт, зламана таблиця). Стиль, «для повноти», нові приклади/задачі/підрозділи — лише на явне прохання. **Розділ не довшає** (нове речення замінює старе); без нових прямих посилань уперед і символів без означення; для кожної правки: що лишиться хибним, якщо відкотити. Одна студентська читка на розділ. У звіті розділяй «виправляю за критерієм» і «побажання». Це той самий критерій, що §0 у `textbook-review-chapter`.

## Мапа скілів і агентів
- Загальні (глобальні): `textbook-review-chapter` (протокол огляду розділу), `textbook-physics-review`, `textbook-logic-reread` («перечитай розділ» = застосуй його), `ukrainian-science-language`, `textbook-problem-author`, `textbook-tikz-figures`, `textbook-bib-entry`, `latex-build-check`, `latex-layout-fix`, `latex-toc-style`, `kpi-syllabus`.
- Лише для цієї книги (`.claude/skills`): `html-build`, `html-check`, `html-class`, `book-markup` (макроси `ConspectBook.cls`), `lecture-slides`, `sim-check`, `numeric-check`, `literature-lookup`, `chapter-update`.
- **Старі локальні копії загальних скілів**, що ще лишаються: `physics-review`, `ukrainian-language`, `build-check`, `problem-author`, `syllabus-write`, `syllabus-literature`. Правило вибору: **спершу загальний скіл** (протокол і правила), а локальний підключай лише за **плазмовою специфікою**, якої немає в загальному (більшу частину вже перенесено в `rules/conventions.md`, `pitfalls.md` і сюди). Не запускай обидва повністю: це дублює роботу й контекст. Видалені дублі (є в git): `logic-reread`, `orphan-hunt`, `tikz-figures`, `bib-entry`, `toc-style`, `syllabus-requisites`; їхні заміни: `textbook-logic-reread`, `latex-layout-fix`, `textbook-tikz-figures`, `textbook-bib-entry`, `latex-toc-style`, `kpi-syllabus`.
- Агенти проєкту: `layout-checker`, `typesetter`, `html-typesetter`, `literature-finder`, `physics-reviewer`, `student-reader`, `language-checker`, `sim-tester`, `tikz-figurer`, `git-committer`. Дешеві глобальні: `latex-build-verdict`, `latex-refs-check`, `latex-layout-fixer`.

## Процес огляду розділу
Файла зауважень на розділ у проєкті немає: зауваження за `textbook-review-chapter` подавай у чаті (файл створюй лише якщо автор попросить). Підсумок і відкриті пункти — у `STATUS_review.md` (коротко, без хронології: історія в `git log`). У серії рецензування розділів домовлено: після правок → `layout-checker` на розділ → застосувати знахідки → перезбірка → `git-committer`; перед комітом оновити `STATUS_review.md`; повідомлення коміту українською, у кінці `rebuild main.pdf`, якщо PDF у коміті. Не комітити `main.idx/ilg/ind` і `*-SAVE-ERROR`.
Питання студента (Q-NNN): коротка відповідь у чаті + запис у `STATUS_student_qa.md`; текст книги не змінювати, доки автор не скаже «внось». На питання спершу вкажи, де в книзі відповідь.

## Compact instructions
Під час стиснення зберігай: поточну задачу, домовленості з автором, шляхи й рядки місць, що правляться, перелік незакомічених змін. Викидай: вміст раніше прочитаних файлів, журнали збірки, відхилені варіанти.
