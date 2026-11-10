# Статус інтерактивних симуляцій (sims/) — оновлено 2026-11-10

Мета: одна симуляція = одна центральна ідея на розділ; ванільний JS, file://, тема світла/темна,
українська, `\simlink` з розділів. Повні вимоги й дизайни — у підсумку сесії 2b386da1 (транскрипт).

## Каркас сторінки
head: shared/theme.js → shared/sim.css → shared/sim.js → shared/physics.js.
`header.top` (h1, .ref, #theme-slot); `#app` = `#panel` (loop, presets, controls, readout,
`.observe` «Що спостерігати», `.note` — наближення схеми + розділ/формула) + `#stage` (rows2|cols2|grid3|grid4, `.view`).
Колір не єдиний носій інформації (штрихи + PSim.label).

## shared/ — ГОТОВО
theme.js, sim.css, sim.js (у т.ч. Ring, trail), physics.js (boris, rk4, maxwellian, rng, erf, bisect).
sim.css: стилі розгортних блоків `#panel details/summary` (2026-11-10). Поки застосовано лише у
waves_incident_wave.html; інші симуляції можна перевести так само (`<section class="observe">` → `<details class="observe" id=… open><summary><h2>…</h2></summary>`).

## Симуляції
| Розділ | Файл | Ідея | Стан |
|---|---|---|---|
| Motion | motion_mirror.html | магнітне дзеркало, конус втрат, μ | готово (тест: Δμ/μ~1e-4, z_m = теорія) |
| Basics | basics_debye.html | 1D листова модель екранування | готово (тест: λ_eff, частка заряду, T = теорія ±4 %) |
| Basics | basics_sheath.html | критерій Бома, F(χ), плаваючий потенціал (§1.7) | готово (тест: φ_f = (1.12) для H/D/Ar, інваріант ~1e-9, n_i з маркерів ±5 %, частка e⁻ = e^{−Δχ}) |
| Basics | basics_probe.html | ВАХ зонда Ленгмюра, витягнути T_e, V_f, V_p; подвійний зонд | готово (тест: V_f = (1.12) для H/D/Ar ±0.001 T_e, T_e фіт ±0.2 %, n_is/n_es ±1 %, подвійний = I_is·th(eV/2T_e) до 1e-11, лічильник частинок = I/I_is ±3 %, гарячий хвіст завищує T_e) |
| Basics | basics_gouy.html | нелінійне екранування Гуї–Чепмена | черга 3 |
| Basics | basics_saha.html | ступінь іонізації x(T,n) | черга 4 |
| Basics | basics_coupling.html | MD однокомпонентної плазми, Γ → g(r) | черга 5 |
| Basics | basics_debye_sphere.html | дебаївська сфера, N_D, колективність (§1.9) | є файл (не закінчено, статус уточнити) |
| Waves | waves_plasma_oscillations.html | ленгмюрівські коливання | є файл (статус уточнити) |
| Waves | waves_incident_wave.html | падіння ЕМ-хвилі на шар плазми (рис. 2.2), відсічка, тунелювання | майже готово: вигляд як рис. 2.2; FDTD 1D + TF/SF; прапорці «розклад (падна + відбита)», «тепловий рух (зменшено)» (лише малювання, розв'язувач не чіпає); запізнення фази при зіткненнях ν; підпис тунелювання для тонкого шару; блоки тексту панелі — розгортні `<details>` (стан у localStorage). `node --check` ОК, у браузері НЕ тестовано |
| Collisions | collisions_runaway.html | втікаючі електрони Драйсера | — |
| Waves | waves_cutoff.html | відсічка й відбиття | можливо, покрито waves_incident_wave |
| Fluid | fluid_frozen.html | вмороженість vs дифузія, R_m | — |
| LinearWaves | linearwaves_dispersion.html | дисперсія МГД/замагнічена | — |
| Kinetics | kinetics_landau.html | загасання Ландау у фазовому просторі | — |
| Instability | instability_twostream.html | двопотокова PIC | — |
| Confinement | confinement_banana.html | бананові орбіти | — |
| Fusion | fusion_gamow.html | пік Гамова / Лоусон | — |
| Discharge | discharge_paschen.html | крива Пашена | — |
| Scales | scales_map.html | карта параметрів плазми | — |

## Після симуляцій
1. Портувати ConspectSims.sty з ElMag; у ConspectBook.cls: колір simmain, `\SimLinkMark`, tcolorbox `Simulation`,
   `\RequirePackage{ConspectSims}` після hyperref. `\SimBaseURL` = https://sergiokapone.github.io/plasma-physics/PlasmaBook/sims (припущення — сказати користувачу).
2. `\simlink` у кожному розділі (читати розділи чанками). 3. latexmk ×2. Не комітити без запиту.
