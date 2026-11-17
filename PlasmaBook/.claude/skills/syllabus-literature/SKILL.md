---
name: syllabus-literature
description: Як оформлювати літературу силабуса — джерело bib (PlasmaBook/bibliography/bibliography.bib, не MyBase.bib), категорії Main/Additional, ініціали замість повних імен, наша книга першою, що робити з ISBN-попередженнями. Використовуй при додаванні/зміні списку літератури в силабусі.
---

# Література силабуса

## Джерело

- Брати записи з `D:\Projects\LaTeX\plasma-physics\PlasmaBook\bibliography\bibliography.bib`. **Не** використовувати `D:\Projects\LaTeX\MyPackages\bib\MyBase.bib` для курсу фізики плазми і нічого туди не дописувати (там чужі незакомічені правки).
- У преамбулі силабуса: `\addbibresource{../PlasmaBook/bibliography/bibliography.bib}` (шлях відносно папки `Syllabus`).
- Новий запис додавати в цей `bib` (за скілом `textbook-bib-entry`), а не в силабус.

## Нормалізація

- Автори — ініціали: `Пономаренко, С. М.`, `Ситенко, О. Г. and Мальнєв, В. М.` (повні імена в записах скорочувати).
- Наша книга — `ponomarenko2026plasma` («Елементи фізики плазми», КПІ, 2026, `url` на `https://sergiokapone.github.io/plasma-physics/`), завжди перша в основній літературі.

## Розподіл

- **Main** («Підручники та посібники»): наша книга + україномовні підручники (`anisimov2018`, `sitenko1996`, `zagorodny2006kinetic`).
- **Additional** («Додаткова»): усі англомовні `@book` з цього bib (Chen, Gurnett, Bellan, Freidberg, Stix, Krall, Kulsrud, Hazeltine, Priest, Goldston, Boyd, Bittencourt, Nicholson, Lieberman, Raizer, Chen–Chang).
- Статті (`@article`) у силабус не входять.
- Не додавати російськомовних книг (використовувати англомовні аналоги).

## Код

```
\nocite{ключі всіх}
\printbibliography[category=Main, heading=subbibliography, title={Підручники та посібники}]
\addtocategory{Main}{ключі,}
\printbibliography[category=Additional, heading=subbibliography, title={Додаткова}]
\addtocategory{Additional}{ключі,}
```

Список ключів Additional можна брати скриптом: усі `@book{ключ,` з bib, крім тих, що в Main (Python із `re.findall(r'^@book\{([^,]+),', text, re.M)`).

## Перевірка

- Збірка: xelatex → biber → xelatex ×2; у виводі biber має бути 0 помилок.
- Попередження «ISBN ... is invalid» для старих українських ISBN (`978-966-439-030-5`, `5-12-003664-9`, `966-360-043-1`) — це контрольна сума, друкується як є, не виправляти без звірки з книгою.
- Довгий список може дати майже порожню останню сторінку розділу — це на `typesetter`.
