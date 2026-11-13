# Фізика плазми

Матеріали курсу «Фізика плазми» (КПІ): український навчальний посібник **PlasmaBook**, інтерактивні симуляції, слайди лекцій, силабус і довідкові підручники для звірки.

Посібник розрахований на студентів-прикладних фізиків, які вже знають загальну й теоретичну фізику. Одиниці: СГС, температура в енергетичних одиницях ($k_B=1$).

## Структура репозиторію

| Тека | Вміст |
|---|---|
| `PlasmaBook/` | навчальний посібник (LuaLaTeX + biber), клас `ConspectBook.cls`, симуляції `sims/`, готовий `main.pdf` |
| `Presentations/` | слайди лекцій 1–9 |
| `Syllabus/` | силабус курсу |
| `Control/` | контрольна робота |
| `Notes/` | робочі нотатки, формули, переведення СІ ↔ СГС |
| `books/` | довідкові підручники зі змістом і пошуком (див. `books/README.md`) |

## PlasmaBook

Розділи за порядком у книзі: Basics, Waves, Motion, Collisions, Fluid, LinearWaves (МГД і хвилі), Kinetics, Instability, Confinement, Fusion, Scales. У кінці: позначення, СГС↔СІ, шпаргалка, глосарій, покажчик, відповіді до задач.

Кожен розділ лежить у власній теці `<Розділ>/<Розділ>.tex`, рисунки TikZ — у `<Розділ>/tikz/`. Рисунки pgfplots мають єдиний стиль, заданий у `ConspectBook.cls`: криві `very thick`, кольори `blue!70!black`, `red!70!black`, `green!50!black`, допоміжні лінії `dashed gray`.

### Збірка

```powershell
cd PlasmaBook
.\build.ps1                      # уся книга -> main.pdf
.\build.ps1 -Chapter Collisions  # лише один розділ -> _chapters\Collisions.pdf
.\build.ps1 -Clean               # спершу прибрати допоміжні файли
```

Потрібні TeX Live з `lualatex`, `latexmk`, `biber`, `upmendex`. `pdflatex` не підходить.

### Сайт посібника

`index.html` у корені репозиторію (з `assets/`) — сторінка для GitHub Pages: кнопка завантаження PDF і зміст, де кожен розділ і підрозділ відкриває `PlasmaBook/main.pdf` на потрібному місці (`#nameddest=ch3`, `#nameddest=s3.2`). Точки призначення створює `ConspectBook.cls` (`\hypertarget` у заголовках розділів і підрозділів), а ще вручну задані: `preface`, `summary`, `answers`, `app-notation`, `app-sgs-si`, `app-cheatsheet`, `glossary`, `bibliography`.

Після кожної збірки книги, що змінила розділи чи їхні назви, перегенеруйте сторінку, бо зміст береться з `main.toc`:

```powershell
cd PlasmaBook
python -I make_site.py
```

`simulations.html` — підсторінка з картками інтерактивних симуляцій (по кліку картка розгортається: що спостерігати, формули, модель, посилання на симуляцію й на місце в PDF). Її теж будує `make_site.py` (дані карток у `PlasmaBook/make_sims_page.py`, прев'ю в `assets/sims/`). Додаючи симуляцію в `sims/`, додайте запис у `SIMS` і знімок.

Онлайн-версії (HTML) книги поки немає.

### Симуляції

Інтерактивні HTML-симуляції лежать у `PlasmaBook/sims/` (Дебаївське екранування, зонд Ленгмюра, шар, магнітне дзеркало, плазмові коливання, інтерферометрія, МГД-хвилі та ін.). Відкриваються просто в браузері. У книзі на них є посилання (`\simlink`).

### Службові файли

`STATUS_*.md` і `REVIEW_student.md` у `PlasmaBook/` фіксують стан читок, діагностик, симуляцій і питань студентів.

## Література

Основні джерела (повний список — у `PlasmaBook/bibliography/bibliography.bib`): Ф. Чен, *Introduction to Plasma Physics and Controlled Fusion*; Bittencourt, *Fundamentals of Plasma Physics*; Анісімов, *Фізика плазми* (КНУ, 2018); MIT OCW 22.611J.
