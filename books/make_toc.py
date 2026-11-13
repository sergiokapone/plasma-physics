#!/usr/bin/env python3
"""Створює TOC_<ключ>.md з оглавлень підручників (.djvu і .pdf) у цій теці.

Безпечно за замовчуванням: ІСНУЮЧІ TOC_*.md НЕ чіпаються (створюються лише відсутні).
    python -I make_toc.py                 # лише нові книги
    python -I make_toc.py --list          # що є, що буде створено, ключі файлів
    python -I make_toc.py --force         # перезаписати всі (втрачаються ручні приписки!)
    python -I make_toc.py --force --only Chen
    python -I make_toc.py --out C:\\Temp\\toc_test --force   # у іншу теку, для перевірки
    python -I make_toc.py --dir C:\\Temp\\other               # інша тека з книгами (тест)

Джерело оглавлення: закладки файлу (djvu: djvused; pdf: PyMuPDF get_toc). Якщо їх нема,
береться текст сторінок «ОГЛАВЛЕНИЕ/СОДЕРЖАНИЕ/ЗМІСТ/CONTENTS» з текстового шару (як є,
з OCR-огріхами). PDF-скан без тексту: спершу `search_books.py --ocr -b <книга>`, тоді
оглавлення береться з OCR-кешу.
Номер сторінки в TOC = індекс сторінки у файлі (для djvu2png.py / search_books.py --png).
Зміщення «номер у книзі − індекс» береться за колонтитулами; для відомих книг можна
задати перевірене вручну значення в OVERRIDE.
Ключ книги береться з META (за початком імені файлу); для нової книги додай запис у META.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I не додає теку скрипта
import bookslib as bl  # noqa: E402

BOOKS = bl.BOOKS

# початок імені файлу -> (назва для заголовка, ключ у імені TOC_<ключ>.md)
META = {
    'Arcimovich': ('Арцимович Л.А., Сагдеев Р.З. Физика плазмы для физиков (Атомиздат, 1979), рус.', 'Artsimovich-Sagdeev'),
    'Chen, Francis F': ('Chen F.F. Introduction to Plasma Physics and Controlled Fusion (3rd ed., Springer, 2016), англ.', 'Chen-en'),
    'Голант В. Е.': ('Голант В.Е., Жилинский А.П., Сахаров И.Е. Основы физики плазмы (Лань, 2011), рус.', 'Golant-Zhilinsky-Sakharov'),
    'Chen': ('Чен Ф. Введение в физику плазмы (Мир, 1987), рус.', 'Chen'),
    'Frank-Kameneckij D.A. Lekcii': ('Франк-Каменецкий Д.А. Лекции по физике плазмы (3-е изд., Интеллект, 2008)', 'Frank-Kamenetskii'),
    'Frank-Kameneckij D.A. Plazma': ('Франк-Каменецкий Д.А. Плазма — четвёртое состояние вещества (3-е изд., Атомиздат, 1968), рус.', 'Frank-Kamenetskii-4th-state'),
    'PlasmaPhysics': ('Анісімов І.О. Фізика плазми. Конспект лекцій (КНУ ім. Т. Шевченка, 2018), укр.', 'Anisimov'),
    'Zagorodnij': ('Загородній А.Г., Черемних О.К. Введення у фізику плазми (Наукова думка, 2014)', 'Zagorodnij-Cheremnykh'),
    'Axiezer': ('Ахиезер А.И., Ахиезер И.А. Электромагнетизм и электромагнитные волны (Высшая школа, 1985), рус.', 'Akhiezer'),
    'Bittenkort': ('Биттенкорт Ж.А. (Bittencourt J.A.) Основы физики плазмы (Физматлит, 2009), рус. перевод Fundamentals of Plasma Physics', 'Bittencourt'),
    'Ландау Л.Д.': ('Ландау Л.Д., Лифшиц Е.М. Теоретическая физика, т. 8: Электродинамика сплошных сред (2005), рус.', 'Landau-Lifshitz-vol8'),
    'Милантьев': ('Милантьев В.П., Темко С.В. Физика плазмы (Просвещение, 1983), рус.', 'Milantyev-Temko'),
    'И. А. Котельников': ('Котельников И.А. Лекции по физике плазмы (Бином, Лаборатория знаний, 2013), рус.', 'Kotelnikov'),
}
# ключ -> (зміщення «книга = індекс + off», примітка), якщо колонтитули не дали надійного результату
OVERRIDE = {
    'Chen-en': (-12, 'Колонтитули дають дві ділянки (-12 і -11, -8 у частині сторінок): номер у книзі звіряй за зображенням. '
                'Проверено: pdf 102-104 = с. 90-92 книги.'),
    'Kotelnikov': (-1, 'Проверено визуально: djvu 12 = с. 11 книги.'),
}
CONTENTS_RX = re.compile(r'ОГЛАВЛЕНИЕ|СОДЕРЖАНИЕ|ЗМІСТ|CONTENTS', re.I)


def meta_for(path: Path):
    for k, v in META.items():
        if path.name.startswith(k):
            return v
    # невідома книга: ключ із імені файлу, щоб НІЧОГО не перезаписати
    slug = re.sub(r'[^\w\-]+', '_', path.stem, flags=re.UNICODE).strip('_')[:40] or 'book'
    return (path.stem, slug)


def offset_votes(pages):
    votes = collections.Counter()
    for idx, t in enumerate(pages, start=1):
        lines = [l.strip() for l in t.splitlines() if l.strip()]
        for cand in (lines[:1] + lines[-1:]):
            if re.fullmatch(r'\d{1,3}', cand):
                votes[int(cand) - idx] += 1
    return votes.most_common(3)


def text_pages(path: Path, folder: Path):
    """Тексти сторінок; для PDF-скана без тексту беремо OCR-кеш, якщо він є."""
    pages = bl.page_texts(path)
    if bl.is_pdf(path) and not bl.has_text_layer(pages):
        import search_books as sb
        of = folder / '.cache' / (sb.short(path) + '.ocr.txt')
        if of.exists():
            return of.read_text(encoding='utf-8').split('\x0c'), 'OCR-кеш'
        return pages, 'немає текстового шару (скан; потрібен --ocr)'
    return pages, ''


def build(path: Path, folder: Path):
    title, key = meta_for(path)
    n_pages = bl.page_count(path)
    pages, text_note = text_pages(path, folder)
    votes = offset_votes(pages)
    if key in OVERRIDE:
        off, note = OVERRIDE[key]
    else:
        off, note = (votes[0][0] if votes else 0), ''
    kind = 'pdf' if bl.is_pdf(path) else 'djvu'
    L = ['# %s' % title, '',
         'Файл: `%s`; сторінок у %s: %d.' % (path.name, kind, n_pages),
         'Номер у книзі = індекс %s %+d (за колонтитулами; голоси: %s).' % (kind, off, votes)]
    if note:
        L.append(note)
    if text_note:
        L.append('Текст: %s.' % text_note)
    L.append('Номери нижче — індекси сторінок %s (`search_books.py --png N -b <книга>`).' % kind)
    L.append('')
    items = bl.outline(path)
    if items:
        for depth, t, pg in items:
            L.append('%s- %s — с. %s' % ('  ' * depth, t, pg if pg != -1 else '?'))
    else:
        cand = [i for i, t in enumerate(pages, start=1)
                if (i <= 15 or i > len(pages) - 30) and CONTENTS_RX.search(t[:200])]
        if cand:
            start = cand[0]
            L.append('Закладок у файлі нема; оглавлення з текстового шару (%s %d–%d), як є:' % (kind, start, start + 1))
            for p in (start, start + 1):
                if p <= len(pages):
                    L += ['', '```', pages[p - 1].strip(), '```']
        else:
            L.append('Закладок нема і сторінку оглавлення не знайдено: шукай вручну (`search_books.py "оглавлен|зміст"`).')
    return key, '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--force', action='store_true', help='перезаписати існуючі TOC_*.md')
    ap.add_argument('--only', help='лише книги, в імені яких є цей підрядок')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--out', type=Path, default=None, help='тека для TOC (за замовчуванням тека з книгами)')
    ap.add_argument('--dir', type=Path, default=None, help='інша тека з книгами (за замовчуванням тека скрипта)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    folder = a.dir or BOOKS
    out = a.out or folder
    out.mkdir(parents=True, exist_ok=True)
    seen = {}
    for f in bl.list_books(folder):
        title, key = meta_for(f)
        if key in seen:
            print('УВАГА: ключ %s вже зайнято файлом %s; пропускаю %s (додай запис у META)' % (key, seen[key], f.name), file=sys.stderr)
            continue
        seen[key] = f.name
        if a.only and a.only.lower() not in f.name.lower() and a.only.lower() not in key.lower():
            continue
        target = out / ('TOC_%s.md' % key)
        exists = target.exists()
        if a.list:
            print('%-28s %-8s %s' % (key, 'є' if exists else 'НЕМАЄ', f.name))
            continue
        if exists and not a.force:
            print('пропущено (є): %s' % target.name)
            continue
        key, text = build(f, folder)
        target.write_text(text, encoding='utf-8', newline='\n')
        print('записано: %s' % target)


if __name__ == '__main__':
    main()
