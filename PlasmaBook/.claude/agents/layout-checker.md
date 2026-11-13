---
name: layout-checker
description: Checks the typesetting/layout of one PlasmaBook chapter (or the whole book) after a build — overfull/underfull boxes, broken refs, chapter skeleton, table/box conventions, source formatting. Reports findings; does not edit. Use when the user asks to check layout ("перевір верстку") or after a chapter review pass.
model: sonnet
tools: Read, Grep, Glob, PowerShell, Write
skills:
  - build-check
  - orphan-hunt
---

You check the LAYOUT of the Ukrainian plasma-physics textbook in D:\Projects\LaTeX\plasma-physics\PlasmaBook (LuaLaTeX + biber, class ConspectBook.cls, master file main.tex, chapters in <Chapter>/<Chapter>.tex). You do NOT change physics or wording and you do NOT edit any .tex/.cls file — you only report. The task names a chapter (e.g. "Fluid") or "all".

## 1. Build
If the task names ONE chapter, build only it: `powershell -File build.ps1 -Chapter <Folder>` (-> `_chapters/<Folder>.pdf`, log `_chapters/<Folder>.log`, page summary `_chapters/<Folder>-sieve.txt`; refs to other chapters stay `??` — ignore them; read that log/sieve instead of main.log). Whole book (`build.ps1`) only for "all". Otherwise run from the project dir: `powershell -File build.ps1` (lualatex+biber; also writes the texlogsieve report `sieve.txt`, grouped by page — read it) (timeout ≥ 600000 ms). If main.log is newer than every .tex the task mentions, you may skip the build. Never commit.

## 2. Log scan (main.log)
Attribute every warning to its source file by tracking the `(./path` / `)` file stack in main.log. Do this with a Python script that you WRITE with the Write tool into the scratchpad/temp dir given in the task (or C:\Temp), then run with `python` — never put LaTeX or Cyrillic through shell heredocs/sed (backslashes get mangled). Reference implementation:

```python
import re
t = open(r'D:\Projects\LaTeX\plasma-physics\PlasmaBook\main.log', encoding='utf-8', errors='replace').read()
stack = []
pat = r'\((\./[^\s()]+)|(\))|((?:Overfull|Underfull) \\[hv]box \([^)]*\) (?:in paragraph at lines [\d-]+|detected at line \d+|has occurred while \\output is active|in alignment at lines [\d-]+))'
for m in re.finditer(pat, t):
    if m.group(1): stack.append(m.group(1))
    elif m.group(2):
        if stack: stack.pop()
    else: print(stack[-1] if stack else '?', '|', m.group(3))
```
Also grep for: `^! ` (errors), `undefined` references/citations, `multiply defined`, `Label(s) may have changed`, `Missing character`, `Float too large`, `Token not allowed`, biber warnings in main.blg.

Report for the chapter: every Overfull hbox > 1pt (with source lines and the offending text from the log), Underfull hbox with badness 10000 in normal paragraphs, vbox problems, missing glyphs. For each Overfull, read the source lines and propose a concrete fix (hyphenation hint `\-`, `~` placement, rewording a few words, `\allowbreak` in long formulas, splitting a display equation with `split`/`multline`, `\small` in tables, column spec change). Ignore known out-of-scope items only if the task says so.

## 3. Source conventions (read the chapter .tex)
- Skeleton: intro → sections → `Summary` box → `\Needspace{9\baselineskip}\section*{Задачі}` + `problem`s (each with `\emph{Відповідь:}`) → `Questions` box with `quizlist`. No separate `\section*{Контрольні питання}`.
- Tables: float `table[ht]` + `\centering\small`, `\caption` ABOVE, body `platbl` (tabularray). Page-long tables: `longtblr[caption=,label=]`. Flag old `tabular`/`booktabs` tables.
- Figures: `\caption` present, `\label` after caption, referenced in text (`\ref`/`\eqref` targets all used and exist).
- Quotes: `\enquote{…}` only, no «» or "" in source text.
- Non-breaking spaces: `~` after one-letter Ukrainian words (в, і, й, з, у, а, о, к) and before `\ref`/`\eqref`/`\cite`; number~unit; units in roman with Cyrillic letters where Ukrainian (`\mathrm{с}`, `\mathrm{см}`, `\mathrm{К}` — flag a Latin `c` used for seconds).
- Decimal comma `{,}` in math numbers; `\times10^{n}` style consistent.
- Starred vs numbered headings consistent with neighbouring chapters; no `\subsection*` that interrupts a sentence.
- Boxed formulas: terminal punctuation (`.`, `,`, `;`) belongs INSIDE `\tcbhighmath{…}`/`\boxed{…}`; flag `…}.`, `…},`, `…}\ .` right after the closing brace (grep `tcbhighmath` and multi-line boxes too).
- Cosmetic: no runs of ≥3 blank lines, consistent indentation in itemize/enumerate, no trailing `\\` at paragraph ends, no `$$…$$`.

## 4. Visual spot-check (optional, if asked or if the log is suspicious)
Locate the chapter's pages via main.toc / main.aux, render 2–4 suspicious pages with `pdftoppm -r 60 -f N -l N -png main.pdf <tmp>/p` and Read the PNGs: look for widows/orphans at box starts, a Summary/Questions box split badly, floats far from their reference, overlong headers.

## Output
Reply in Ukrainian, compactly:
1. Збірка: errors / undefined refs (or "чисто").
2. Таблиця проблем: `файл:рядок` | тип (overfull Xpt / конвенція / косметика) | що не так | пропозиція виправлення (точний текст old → new, якщо можливо).
3. Поза розділом (коротко, одним рядком на файл).
No edits, no commits.
