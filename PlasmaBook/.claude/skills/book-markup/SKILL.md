---
name: book-markup
description: Шпаргалка з розмітки .tex для PlasmaBook — які середовища й макроси є в ConspectBook.cls і коли який брати (Theory, Attention, Example, Historical, Estimate, Simulation, Summary, Questions, problem/solution, platbl/longtblr, \emphx, \index, \vect, \tcbhighmath), префікси міток, рисунки TikZ/PNG, скелет розділу, пастки Windows/Bash при правці. Використовуй, коли пишеш або правиш будь-який фрагмент .tex книги, щоб одразу дотримуватись конвенцій, а не виправляти після layout-checker.
---

# Розмітка PlasmaBook

Клас `ConspectBook.cls` (LuaLaTeX + biber), головний файл `main.tex`, розділи `<Розділ>/<Розділ>.tex`. Перед використанням рідкісного середовища відкрий його визначення в `.cls` (`grep -n "newtcolorbox" ConspectBook.cls`) і взірець у наявному розділі.

## Скелет розділу

Зразок — `Waves/Waves.tex`. Порядок:
1. На початку файлу, **перед** `\chapter`: `\Opensolutionfile{answer}[\currfilebase/\currfilebase-Answers]` і `\Writetofile{answer}{\protect\section*{Розділ~\ref*{sec:X}. \nameref*{sec:X}}}`.
2. `\chapter{…}\label{sec:X}`, вступ, `\section{…}` з `\index` і `\label{sec:…}`.
3. Наприкінці теорії блок «Як це вимірюють: …» (`STATUS_diagnostics.md`).
4. За потреби `Simulation`.
5. `\Needspace{8\baselineskip}` і `Summary`.
6. `\Needspace{9\baselineskip}\tocunnum{Задачі}\section*{Задачі}` і `problem`.
7. `Questions` з `quizlist`.
8. В кінці файлу `\Closesolutionfile{answer}`.

Новий розділ підключається через `\multiinclude` у `main.tex`; файл `…-Answers.tex` генерує збірка (потрібен другий прохід).

## Врізки й виділення

| Що | Коли | Примітка |
|---|---|---|
| `Theory[Заголовок]` | «Нагадаємо з …»: відомий матеріал, потрібний для виводу | заголовок в необов'язковому аргументі, автономер |
| `Attention[...]` | попередження про типову помилку, парадокс | жовта врізка |
| `Example{Заголовок}` | розв'язаний приклад (другий аргумент обов'язковий) | |
| `Historical` | історична довідка | пергаментна |
| `Estimate[Числова оцінка]` | підстановка типових чисел; **не кожен** приклад (однорядкову ілюстрацію в аргументі лишай у тексті) | числа через `numeric-check`; висновок звичайним текстом **після** боксу |
| `Simulation` | абзац із `\simlink[Назва][опис]{файл.html}{текст}` | `\SimBaseURL` у `ConspectSims.sty`; додавати `\simlink` — рішення автора |
| `Summary` | «Головне в розділі» перед «Задачі» | |
| `Questions` + `quizlist` | питання; окремого `\section*` нема | |
| `\emphx{термін}` | означення терміна (малиновий курсив) | **не** додає в покажчик: одразу після нього `\index{…\|textbf}` |
| `\vect{E}` | вектор (жирний прямий) | також `\Efield`, `\Bfield`, `\rot`, `\divg`, `\grad`, `\diff{f}{x}` |
| `\tcbhighmath{…}` | ключова формула всередині `equation` | один `\label{eq:…}` на рівняння; не `$$…$$`; розділовий знак у кінці формули ставимо **всередині** рамки (`\tcbhighmath{a=b.}`), а не після неї |
| `\enquote{…}` | лапки | не «» і не "" |

## Таблиці

Плаваюча `table[ht]` + `\centering\small` + `\caption` **згори** + `\begin{platbl}{colspec={X[l,m]…}}…\end{platbl}`; висока таблиця — `longtblr[caption=,label=]`. Старих `tabular`/`booktabs` не додавай.

## Задачі

`\begin{problem}\label{prb:Name}\lvl{N} … \begin{solution}…\end{solution}\end{problem}`; деталі — скіл `problem-author`.

## Рисунки

- **TikZ**: файл `<Розділ>/tikz/name.tikz`; у тексті `\begin{figure}[ht]\centering\localinput{name.tikz}\caption{…}\label{tikz:name}\end{figure}`. Функції TikZ унікальні в межах файлу.
- **PNG**: у `<Розділ>/Pictures/`, `\includegraphics[width=…\linewidth]{file}`, `\label{pic:name}`.
- Кожен рисунок має `\caption`, мітку **після** підпису й посилання в тексті (`рис.~\ref{…}`).

## Мітки

Префікси: `sec:` розділи й §, `eq:` формули, `prb:` задачі, `tikz:`/`pic:`/`fig:` рисунки, `tab:` таблиці, `asm:` пронумеровані припущення. Мітка унікальна по всій книзі: перед уживанням `grep -rn "label{name}" --include=*.tex .`. Посилання: `розд.~\ref{}`, `§\,\ref{}`, `рис.~\ref{}`, `табл.~\ref{}`, формули `\eqref{}`; «див. вище/нижче» заміняй на `\ref`/`\eqref`.

## Покажчик, глосарій, позначення

- `\index{Термін|textbf}` на місці означення (жирна сторінка); форма: іменні з прізвища (`Бома критерій`), решта з іменника (`Довжина!дебаївська`), підзаписи через `!`. Сортування — `index-uk.ist` (upmendex).
- Новий термін — у `Glossary.tex` (формат сусідніх, з посиланням на § і сторінку); новий або розширений символ — у `Notation.tex`; ключові формули — у `cheatsheet.tex` (їх небагато).
- Не комітити згенеровані `main.idx`, `main.ilg`, `main.ind`, `*-SAVE-ERROR`.

## Типографіка

`~` після однолітерних слів (в, і, й, з, у, а, о, к) і перед `\ref`/`\eqref`/`\cite`; число~одиниця; довге тире `~---`; десяткова кома `{,}` у математиці; `\times10^{n}`; одиниці `\mathrm{с}`, `\mathrm{см}` кирилицею; діапазони словами («від … до»). Докладно — скіл `ukrainian-language`.

**Текст після формули.** Якщо речення продовжується під формулою («є середнім числом…», «де $x$ — …», «тут…», «тобто…»), не лишай порожнього рядка між `\end{equation}`/`\]` і текстом: порожній рядок дає абзацний відступ. Став на порожньому рядку самотній `%` — абзацу не буде. Порожній рядок лишається лише там, де починається справді новий абзац (з великої літери).

## Правка файлів (пастки)

- **Bash/heredoc/sed ламають зворотні скісні й кирилицю**: правити через `Edit`/`Write`; багаторядкові заміни — скриптом Python, створеним через `Write` (`D:\Programs\Programming\WPy64\python\python.exe -I`).
- Багаторядкові `Edit` іноді не збігаються через `~`; тоді заміна за номерами рядків у скрипті.
- Збірка: `powershell -File build.ps1` (скіл `build-check`); **не запускати дві збірки одночасно** (код 12, «undefined references»). Не `pdflatex` і не `latexmk -pdf`.
- Не комітити без прохання (агент `git-committer`).
- Після правки — `layout-checker`: таблиці, підписи, мітки, `~`, `\enquote`, відсутність `$$` і рядків-сиріт.
