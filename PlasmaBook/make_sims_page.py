#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Генерує ../simulations.html — сторінку з картками інтерактивних симуляцій (sims/*.html).

Запуск окремо:  python -I make_sims_page.py   (make_site.py викликає її теж)
Прев'ю карток лежать у ../assets/sims/<id>.jpg (скриншоти Playwright, див. скіл sim-check).
Дані карток — у списку SIMS нижче: додаючи симуляцію, додайте запис і прев'ю.
Посилання «у книзі» ведуть у PDF на іменовану точку призначення (ch N, sN.M, див. make_site.py).
Рядки в SIMS — готовий HTML (довіряємо собі): <sub>, <sup>, <i>.
"""
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "simulations.html"
PDF = "PlasmaBook/main.pdf"
SITE = "https://sergiokapone.github.io/plasma-physics/simulations.html"

# Розділи книги, що мають симуляції: ключ -> (підпис фільтра)
CHAPTERS = {
    "1": "Розд. 1 · Плазма",
    "2": "Розд. 2 · Хвилі",
    "3": "Розд. 3 · Рух частинки",
    "6": "Розд. 6 · МГД-хвилі",
}

# id = ім'я файлу без .html (збігається з ../assets/sims/<id>.jpg і якорем сторінки)
SIMS = [
    dict(id="basics_debye", ch="1", sec="§1.5", dest="s1.5", kind="sim",
         title="Дебаївське екранування пробного заряду",
         lead="Заряд у плазмі обростає хмарою електронів, і його поле гасне на відстані кількох λ<sub>D</sub>.",
         watch=["Збільшуйте T: хмара розпливається. Збільшуйте n<sub>0</sub>: стискається.",
                "Уже на 3λ<sub>D</sub> заряд екрановано приблизно на 95 %, а поле спадає до нуля, тоді як у вакуумі було б сталим.",
                "Режим «сильний заряд» (eφ(0)/T &gt; 1): лінеаризація не працює, профіль іде за кривою Больцмана, а не за експонентою.",
                "Мало частинок на λ<sub>D</sub>: профіль шумить, колективне екранування має сенс лише при n<sub>0</sub>λ<sub>D</sub> ≫ 1."],
         formulas=["λ<sub>De</sub> = √(T / 4πn<sub>0</sub>e²)"],
         model="Одновимірна листова модель: N електронних площин на тлі нерухомих іонів, пробна площина в x = 0. Поле листа точне за теоремою Гаусса, рух за схемою «стрибок жаби», температуру тримає термостат Ланжевена."),
    dict(id="basics_debye_sphere", ch="1", sec="§1.6", dest="s1.6", kind="sim",
         title="Сфера Дебая: молекулярна динаміка",
         lead="Тривимірна плазма з кулонівською взаємодією показує, як спадає заряд усередині сфери радіуса r.",
         watch=["Електрони збираються навколо додатного заряду, іони відступають.",
                "Біля r = λ<sub>D</sub> лишається 74 % заряду, на 3λ<sub>D</sub> лише 20 %.",
                "Знижуйте T до N<sub>D</sub> &lt; 1: у сфері менше однієї частинки, колективного екранування немає, профіль розходиться з теорією.",
                "При Γ ≳ 0,6 електрони й іони утворюють зв'язані пари."],
         formulas=["Q(&lt;r) = Q(1 + r/λ<sub>D</sub>)e<sup>−r/λ<sub>D</sub></sup>"],
         model="3D-плазма в кубі з періодичними межами, показано проєкцію на площину. Сила з усіченням на L/2, м'яка сердцевина усуває колапс пар, температуру тримає термостат Ланжевена."),
    dict(id="basics_sheath", ch="1", sec="§1.9", dest="s1.9", kind="sim",
         title="Пристінний шар: критерій Бома",
         lead="Щоб біля стінки існував монотонний шар, іони мусять входити в нього зі швидкістю не меншою за звукову.",
         watch=["Зменшуйте число Маха M = u<sub>0</sub>/c<sub>s</sub> нижче 1: потенціал Сагдеєва F(χ) стає від'ємним, шару немає.",
                "У шарі n<sub>i</sub> &gt; n<sub>e</sub> скрізь: іони розганяються полем, електрони йдуть за Больцманом.",
                "До стінки долітає лише частка e<sup>−χ<sub>w</sub></sup> електронів: вона й задає плаваючий потенціал.",
                "Важчий газ (D, Ar) дає глибший плаваючий потенціал."],
         formulas=["u<sub>0</sub> ≥ c<sub>s</sub>", "eφ<sub>f</sub>/T<sub>e</sub> ∝ ½ ln(m<sub>i</sub>/m<sub>e</sub>)"],
         model="Стаціонарний 1D-шар: холодні іони без зіткнень і больцманівські електрони. Розв'язується перший інтеграл рівняння Пуассона."),
    dict(id="basics_probe", ch="1", sec="§1.9", dest="s1.9", kind="sim",
         title="Зонд Ленгмюра: від ВАХ до T<sub>e</sub> і n",
         lead="Вольт-амперна характеристика зонда і те, що з неї можна дістати: T<sub>e</sub>, V<sub>f</sub>, V<sub>p</sub>, n.",
         watch=["Нахил прямої ln(I + I<sub>is</sub>) дає T<sub>e</sub>, злам графіка потенціал плазми.",
                "Для водню V<sub>f</sub> ≈ −3,3 T<sub>e</sub>/e, для аргону глибше. Порівняйте з формулою книги.",
                "Гарячий хвіст розподілу викривлює графік: T<sub>e</sub> залежить від вікна фіту й завищена.",
                "Подвійний зонд плаває як ціле: струм обмежений величиною ±I<sub>is</sub>."],
         formulas=["I ∝ e<sup>eV/T<sub>e</sub></sup>"],
         model="Плоский зонд, тонкий шар, B = 0. Іонний струм за потоком Бома, електрони максвеллівські з можливим гарячим хвостом."),
    dict(id="basics_probe_lab", ch="1", sec="§1.9", dest="s1.9", kind="lab",
         title="Лабораторна: що вимірює зонд",
         lead="Віртуальний практикум: чорний ящик із невідомими T<sub>e</sub>, n і V<sub>p</sub>, прилади з шумом.",
         watch=["Одиночний або подвійний зонд, ручна й автоматична розгортка.",
                "Обробка: I<sub>is</sub>, V<sub>f</sub>, T<sub>e</sub> з ln(I + I<sub>is</sub>), V<sub>p</sub> зі зламу, n з I<sub>is</sub> і I<sub>es</sub>.",
                "Вікно фіту, перевірка відповіді, таблиця й експорт у CSV.",
                "Навчальний режим із відомими параметрами для самоперевірки."],
         formulas=["n з I<sub>is</sub> і з I<sub>es</sub>"],
         model="Схема лабораторної з електронами в дроті. Ядро перевірене на відомих параметрах: T<sub>e</sub> у межах ±1 %."),
    dict(id="waves_plasma_oscillations", ch="1", sec="§1.4", dest="s1.4", kind="sim",
         title="Плазмові коливання",
         lead="Усі електрони шару зсунуто відносно іонного фону й відпущено: шар коливається з плазмовою частотою.",
         watch=["На краях, де електрони й іони не перекриваються, виникають смуги заряду ±σ, σ = neξ.",
                "Поле цих смуг повертає електрони назад, тому рух гармонічний.",
                "Фазовий портрет — еліпс, енергія переходить між кінетичною й електричною."],
         formulas=["ω<sub>p</sub> = √(4πne²/m)"],
         model="Одновимірна листова модель: 300 заряджених площин, поле з теореми Гаусса, схема «стрибок жаби»."),
    dict(id="waves_incident_wave", ch="2", sec="§2.5", dest="s2.5", kind="sim",
         title="Хвиля на шарі плазми",
         lead="Електромагнітна хвиля падає з вакууму на шар плазми: за ω &gt; ω<sub>p</sub> проходить, за ω &lt; ω<sub>p</sub> відбивається.",
         watch=["Електрони коливаються проти поля, пари «електрон — іон» дають диполі, звідси ε = 1 − ω<sub>p</sub>²/ω².",
                "При ω &lt; ω<sub>p</sub> поле спадає як e<sup>−κx</sup>, у плазмі енергії немає, відбиття повне.",
                "Тонкий шар при ω &lt; ω<sub>p</sub> пропускає хвилю тунелюванням: з'являється пройдена хвиля, R + T = 1.",
                "Зіткнення ν зменшують зміщення електронів і дають запізнення фази arctg(ν/ω)."],
         formulas=["ε = 1 − ω<sub>p</sub>²/ω²", "κ = √(ω<sub>p</sub>² − ω²)/c"],
         model="Одновимірне числове розв'язання рівнянь Максвелла (FDTD) зі струмом електронів, c/ω<sub>p</sub> = 10 комірок, падаюча хвиля вводиться методом повного й розсіяного поля."),
    dict(id="waves_thermal_jitter", ch="2", sec="розд. 2", dest="ch2", kind="sim", draft=True,
         title="Теплове «дрижання» плазми",
         lead="Рівноважна плазма, яку ніхто не збурює, а в ній видно хмару навколо кожної частинки й гул на ω<sub>p</sub>.",
         watch=["Клікніть по частинці, щоб зробити її пробною: навколо неї видно дебаївську хмару.",
                "Просторово-часова карта заряду показує шум, у якому проступає коливання на ω<sub>p</sub>.",
                "Перемикач «без взаємодії» перетворює плазму на газ: хмари й піка у спектрі немає."],
         formulas=["S(k) = k²/(1 + k²)"],
         model="Одновимірна модель заряджених листів у періодичному ящику L = 40λ<sub>D</sub>, N = 40N<sub>D</sub>."),
    dict(id="waves_thermal_jitter_2d", ch="2", sec="розд. 2", dest="ch2", kind="sim", draft=True,
         title="Теплове «дрижання» плазми в площині",
         lead="Те саме, але у справжній площині (x, y): зелена пробна частинка й коло Дебая навколо неї.",
         watch=["Риски показують швидкості, фон показує заряд у комірках.",
                "Лічильник частинок у колі дає дисперсію числа частинок, яку можна звірити з теорією.",
                "Мода (m, 0): ряд у часі й спектр із піком Бома — Гросса."],
         formulas=["N<sub>D</sub> частинок у крузі λ<sub>D</sub>"],
         model="Двовимірна плазма заряджених ліній у періодичному квадраті L = 24λ<sub>D</sub>. Поле рахується методом частинка — сітка (сітка 64², ШПФ)."),
    dict(id="waves_interferometry_lab", ch="2", sec="§2.7", dest="s2.7", kind="lab",
         title="Лабораторна: інтерферометрія і рефлектометрія",
         lead="Мікрохвильова діагностика густини: чорний ящик із шаром плазми, інтерферометр і рефлектометр.",
         watch=["Інтерферометр: вибір довжини хвилі, вібрації дзеркал і їх компенсація, лічильник смуг із перескоками.",
                "Відсічка при n<sub>0</sub> ≥ n<sub>кр</sub>: фаза втрачає зв'язок з густиною.",
                "Рефлектометр: розгортка τ(f), обернення Абеля, екстраполяція ділянки 0…f<sub>1</sub>.",
                "Відновлений профіль порівнюється з еталоном."],
         formulas=["Δφ = r<sub>e</sub>λ ∫n dl", "x<sub>c</sub>(F) = (c/π)∫τ(F sinθ)dθ"],
         model="Плоский шар n = n<sub>0</sub>(1 − s²)<sup>p</sup>. Ядро перевірене: x<sub>c</sub> у межах ±0,5 % при f<sub>1</sub> = 1 ГГц."),
    dict(id="motion_mirror", ch="3", sec="§3.5", dest="s3.5", kind="sim",
         title="Магнітне дзеркало і конус втрат",
         lead="Заряджена частинка рухається в пробкотроні: одні відбиваються від горловин, інші потрапляють у конус втрат.",
         watch=["Частинка відбивається там, де B = B<sub>0</sub>/sin²θ<sub>0</sub>: виміряне z<sub>m</sub> збігається з теорією.",
                "Більше R звужує конус: частка втрат ізотропного розподілу дорівнює 1 − √(1 − 1/R).",
                "Режим «порушення адіабатичності»: μ стрибає в горловинах, пітч-кут блукає."],
         formulas=["sin²θ<sub>c</sub> = 1/R", "μ = m v<sub>⊥</sub>²/2B"],
         model="Схема Боріса: у статичному B енергія зберігається точно, μ лише адіабатично. Поле параксіальне, div B = 0."),
    dict(id="waves_mhd_psim", ch="6", sec="§6.4–6.5", dest="s6.4", kind="sim",
         title="МГД-хвилі: альвенівська й магнітозвукові",
         lead="Переріз плазми з вмерзлими силовими лініями й 3D-пучок: видно, чим відрізняються три моди.",
         watch=["Колір — збурення густини: червоне стиск, синє розрідження.",
                "Зонд (кільце з крапкою) можна перетягти мишею, 3D-вид повертається.",
                "Альвенівська хвиля: густина й |B| не змінюються, v<sub>ф</sub> = v<sub>A</sub> cosθ.",
                "Швидка й повільна магнітозвукові хвилі відрізняються фазою збурень тиску й поля."],
         formulas=["v<sub>A</sub> = B/√(4πρ)", "c<sub>s</sub>² = γp/ρ"],
         model="Ідеальна МГД, лінеаризація над однорідним станом, γ = 5/3."),
]

KIND = {"sim": "Симуляція", "lab": "Лабораторна"}
CHEVRON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>')


def card(s: dict) -> str:
    sid = s["id"]
    kind = s["kind"]
    badges = '<span class="sim-kind%s">%s</span>' % (" lab" if kind == "lab" else "", KIND[kind])
    if s.get("draft"):
        badges += '<span class="sim-kind draft">чернетка</span>'
    watch = "\n".join("                        <li>%s</li>" % w for w in s["watch"])
    formulas = "".join("<code>%s</code>" % f for f in s["formulas"])
    link = "PlasmaBook/sims/%s.html" % sid
    shot = "assets/sims/%s.jpg" % sid
    alt = "Знімок симуляції: " + escape(s["title"].replace("<sub>", "").replace("</sub>", ""))
    return f"""            <article class="sim" id="{sid}" data-ch="{s['ch']}" data-kind="{kind}">
                <button class="sim-head" type="button" aria-expanded="false" aria-controls="{sid}-body">
                    <span class="sim-shot"><img src="{shot}" alt="{alt}" loading="lazy" width="980" height="612">{badges}</span>
                    <span class="sim-meta">
                        <span class="sim-eyebrow">Розд. {s['ch']} <span class="sec">{s['sec']}</span></span>
                        <span class="sim-title">{s['title']}</span>
                        <span class="sim-lead">{s['lead']}</span>
                        <span class="sim-foot"><span class="sim-key">{s['formulas'][0]}</span><span class="sim-more"><span class="t-more">Докладніше</span><span class="t-less">Згорнути</span> {CHEVRON}</span></span>
                    </span>
                </button>
                <div class="sim-body" id="{sid}-body" role="region" aria-label="{alt}">
                    <div class="sim-cols">
                        <a class="sim-big" href="{link}" target="_blank" rel="noopener">
                            <img src="{shot}" alt="" loading="lazy" width="980" height="612">
                            {badges}
                            <span class="play">Відкрити {KIND[kind].lower()} <span aria-hidden="true">↗</span></span>
                        </a>
                        <div class="sim-text">
                            <h3>Що спостерігати</h3>
                            <ul>
{watch}
                            </ul>
                            <h3>Ключові формули</h3>
                            <div class="sim-formulas">{formulas}</div>
                            <h3>Модель</h3>
                            <p class="sim-model">{s['model']}</p>
                            <div class="sim-actions">
                                <a class="sbtn primary" href="{link}" target="_blank" rel="noopener">Відкрити {KIND[kind].lower()} <span aria-hidden="true">↗</span></a>
                                <a class="sbtn" href="{PDF}#nameddest={s['dest']}">У посібнику, {s['sec']}</a>
                            </div>
                        </div>
                    </div>
                </div>
            </article>"""


def render() -> str:
    counts = {k: sum(1 for s in SIMS if s["ch"] == k) for k in CHAPTERS}
    nlab = sum(1 for s in SIMS if s["kind"] == "lab")
    chips = ['<button type="button" class="chip" data-filter="all" aria-pressed="true">Усі<span class="n">%d</span></button>' % len(SIMS)]
    for k, label in CHAPTERS.items():
        chips.append('<button type="button" class="chip" data-filter="%s" aria-pressed="false">%s<span class="n">%d</span></button>' % (k, label, counts[k]))
    chips.append('<button type="button" class="chip" data-filter="lab" aria-pressed="false">Лабораторні<span class="n">%d</span></button>' % nlab)
    cards = "\n".join(card(s) for s in SIMS)
    page = PAGE.replace("@CHIPS@", "\n                ".join(chips)).replace("@CARDS@", cards)
    return page.replace("@SITE@", SITE).replace("@N@", str(len(SIMS)))


PAGE = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Симуляції | Фізика плазми</title>
    <meta name="description" content="Інтерактивні симуляції до навчального посібника з фізики плазми: екранування, зонд Ленгмюра, хвилі, магнітне дзеркало, МГД-хвилі.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="@SITE@">
    <meta property="og:title" content="Симуляції | Фізика плазми">
    <meta property="og:description" content="Інтерактивні симуляції й віртуальні лабораторні до навчального посібника з фізики плазми.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="@SITE@">

    <script>(function(){var r=document.documentElement;r.classList.add('js');try{var d=localStorage.getItem('plasma-design');r.setAttribute('data-design',['field','blueprint','book'].indexOf(d)>-1?d:'field');var t=localStorage.getItem('plasma-theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme: dark)').matches)){r.classList.add('dark');}}catch(e){r.setAttribute('data-design','field');}})();</script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&family=Literata:ital,opsz,wght@0,7..72,400..600;1,7..72,400..600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">
    <link rel="stylesheet" href="assets/styles.css">
    <link rel="stylesheet" href="assets/designs.css">
    <link rel="stylesheet" href="assets/sims.css">
</head>
<body>
<div class="container">

    <header class="sims-hero">
        <div class="hero-tools">
            <div class="design-switch" role="group" aria-label="Дизайн сторінки">
                <button type="button" data-design="field" aria-pressed="true">Поле</button>
                <button type="button" data-design="blueprint" aria-pressed="false">Креслення</button>
                <button type="button" data-design="book" aria-pressed="false">Книга</button>
            </div>
            <button class="theme-toggle" id="theme-toggle" type="button" title="Перемкнути тему" aria-label="Перемкнути тему">🌙</button>
        </div>
        <a class="sims-back" href="index.html">← До навчального посібника</a>
        <h1>Симуляції</h1>
        <p class="sims-lead">@N@ інтерактивних моделей до розділів посібника. Кожна показує одну ідею: змінюйте параметри й дивіться, як змінюється картина. Натисніть картку, щоб побачити, що спостерігати, і відкрити симуляцію.</p>
    </header>

    <div class="sims-bar">
        <div class="sims-filters" role="group" aria-label="Фільтр за розділом">
                @CHIPS@
        </div>
        <span class="sims-count" id="sims-count" aria-live="polite"></span>
    </div>

    <main>
        <div class="sims-grid" id="sims-grid">
@CARDS@
        </div>
    </main>

    <p class="sims-note">Симуляції працюють у браузері без встановлення й без мережі, окрім шрифтів. Деякі моделі позначено як чернетки: фізика в них перевірена, а вигляд ще шліфується.</p>

    <footer>
        Фізика плазми &nbsp;|&nbsp; Навчальний посібник<br>
        Кафедра прикладної фізики, КПІ ім. Ігоря Сікорського
    </footer>

</div>

<button class="back-to-top" id="back-to-top" type="button" title="Нагору" aria-label="Прогорнути нагору">↑</button>

<script src="assets/script.js"></script>
<script src="assets/sims.js"></script>
</body>
</html>
"""


def main() -> int:
    OUT.write_text(render(), encoding="utf-8", newline="\n")
    print("simulations.html: %d карток -> %s" % (len(SIMS), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
