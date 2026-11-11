# Діагностика плазми: статус і план робіт

План: `PlasmaBook_diagnostics_recommendations.md`. Цей файл — робочий статус для виконавця.

## Стан на 2026-11-09

- [x] **Розд. 4 Waves — пілот готовий**. Збірка: 165 с., без нових overfull.
- [x] **Розд. 7 Kinetics — томсонівське розсіяння готово** (167 с., +2 с.). Мітки: `sec:thomson`, `eq:scattering-parameter`, `eq:thomson-width`, `pic:thomson`, `prb:ThomsonTe`, `prb:ThomsonCollective`. TikZ: `Kinetics/tikz/thomson_incoherent.tikz`, `thomson_collective.tikz`. Секція стоїть після «Коли потрібен кінетичний опис?», перед Summary.
- [x] **Розд. 5 Fluid — магнітні виміри готово** (169 с. загалом). Мітки: `sec:magnetic-diagnostics`, `eq:rogowski`, `eq:diamagnetic-loop`, `pic:magnetic-diagnostics`, `prb:DiamagneticLoop`, `prb:Rogowski`. TikZ: `Fluid/tikz/magnetic-loops.tikz`, `diamagnetic-profile.tikz`. Секція стоїть наприкінці теорії, перед Summary.
- [x] **Розд. 1 Basics — подвійний зонд готово** (171 с.). Мітки: `eq:double-probe`, `prb:DoubleProbe`. Вставка `\subsection*{Подвійний зонд і межі застосовності}` у розділі про зонд Ленгмюра. Не перевірено, чи нові Overfull у `main.log` належать саме Basics, а не іншим розділам.
- [x] **Розд. 2 Motion — аналізатор енергій і ЕЦЕ готово** (172 с.). Мітки: `sec:motion-diagnostics`, `eq:ece-frequency`, `prb:ECERadius`, `prb:RetardingAnalyzer`.
- [x] **Розд. 3 Collisions — T_e з опору, допплерівське/штарківське розширення готово** (173 с.). Мітки: `sec:collision-diagnostics`, `eq:spitzer-temperature`, `eq:doppler-width`, `prb:SpitzerTe`.
- [x] **Розд. 6 LinearWaves — обертання Фарадея готово** (170 с.). Мітки: `sec:faraday-diagnostics`, `eq:faraday-rotation`; задача `prb:FaradayRotation` уже була.
- [x] **Розд. 8 Instability — котушки Мірнова, м'який рентген готово** (174 с.). Мітки: `sec:instability-diagnostics`, `eq:mirnov`, `prb:MirnovCoil`. Секція — §8.15, наприкінці теорії перед Summary.
- [x] **Розд. 9 Confinement — магнітна реконструкція рівноваги готово** (174 с.). Мітки: `sec:equilibrium-diagnostics`, `eq:shafranov-diagnostic`, `prb:ShafranovShift`. Візуально сторінки не перевірено.
- [x] **Розд. 10 Fusion — нейтронна діагностика готово** (175 с.). Мітки: `sec:fusion-diagnostics`, `eq:neutron-yield`, `prb:NeutronYield`. Візуально не перевірено.
- [x] **Розд. 11 Scales — таблиця «масштаб – метод» готово** (176 с.). Мітки: `sec:scales-diagnostics`, `tab:scales-methods`. Візуально не перевірено (pdftotext/pdftoppm недоступні в оболонці).

**Усі розділи пройдені. Далі: візуальна перевірка нових сторінок (розд. 9–11), рев'ю, коміт за запитом автора.**

Пріоритет: 7 → 5 → 6 → 1 → решта. Загальний бюджет: +7–9 с. на всю книжку (пілот уже +5 с. разом із задачами).

## Еталон: що зроблено в пілоті (розд. 4)

Дивись `Waves/Waves.tex`, `\section{Як це вимірюють: інтерферометрія і~рефлектометрія}\label{sec:wave-diagnostics}`.

Структура повного параграфа:
1. Вступний абзац: який фізичний ефект розділу лежить в основі методу.
2. `\subsection*{<Метод>}` — ключова формула в `\tcbhighmath` з `\label{eq:...}`, числова оцінка (`\emph{Оцінка.}`) з реальними параметрами.
3. Один рисунок TikZ (`subfigure` якщо два методи), файли в `<Chapter>/tikz/*.tikz`, підключення `\localinput{...}`, мітка `pic:...`.
4. `\subsection*{Межі застосовності ...}` — `itemize`, 3–4 пункти, з посиланнями «розд.~\ref{...}» на інші розділи.
5. Завершальний абзац, що пов'язує методи з фізикою розділу.
6. Додатково: 1 пункт у Summary-боксі, 1 контрольне питання, 1–2 задачі на оцінку з відповіддю `\emph{Відповідь:}` inline.

Коротка вставка: 0,5–1 с., одна формула, без рисунка, 1 задача.

Нові мітки пілоту: `sec:wave-diagnostics`, `eq:interferometer-phase`, `pic:wave-diagnostics`,
`prb:InterferometerWavelength`, `prb:ReflectometerLinear`, `sec:reflection`, `sec:ionosphere`.

## Обов'язкові конвенції

- Заголовок: «Як це вимірюють: …». Розміщення — наприкінці теорії розділу, перед «Задачами».
- СГС (гаусова), $k_B = 1$ (T в енергетичних одиницях).
- Десяткова кома `{,}`, лапки `\enquote{}`, наголос `\emphx{}`, «розд.~\ref{}».
- Мітки без префікса `new-`, унікальні по всій книжці (перевіряти Grep-ом).
- Назви функцій у TikZ унікальні в межах файлу (PGF "function already exists").
- Таблиці — лише `platbl`/`longtblr`.
- Редагувати тільки Edit/Write; **не** bash heredoc/sed (ламає зворотні слеші).
- Кожну числову оцінку перерахувати (краще скриптом), перш ніж вписувати.

## Перевірка після кожного розділу

1. `latexmk -lualatex main.tex` у `PlasmaBook/` (за потреби двічі).
2. У `main.log`: немає `undefined`, немає нових `Overfull \hbox` > 1pt у зміненому розділі.
3. Відрендерити змінені сторінки (`pdftoppm -r 80 -f N -l M -png main.pdf`) і переглянути рисунок: підписи не перекриваються, ширина влазить.
4. Оновити чекбокс у цьому файлі. Не комітити без запиту автора.

## Верстка (2026-11-09, після діагностичних вставок)

- [x] Колонтитул: `\hdrnum`/`\hdrtitle` (ConspectBook.cls) замість `\thechapter.\ \chaptertitle` — без «0.» у `\chapter*`; зміст (с. 3–6) без колонтитула (`\clearpage` перед `\pagestyle{main}`).
- [x] Toc: без лінійки під «Література»; `\l@section` з numwidth 3,3em (нема накладання «10.10»).
- [x] Література: прибрано 5 російських джерел, додано Goldston–Rutherford, Boyd–Sanderson, Bittencourt, Nicholson (дані з пам'яті — звірити ISBN).
