#!/usr/bin/env python3
"""Повнотекстовий пошук по підручниках (.djvu і .pdf) у цій теці.

Приклади (запускати: python -I search_books.py ...):
    search_books.py "Клеммов|Клэммов"                 # regex, усі книги
    search_books.py "затухан\\w+ Ландау" -b Chen -C 1 # лише книга, що містить 'Chen' в імені
    search_books.py "амбиполярн" -m 5                 # не більше 5 збігів на книгу
    search_books.py --page 146 -b Chen                # вивести текст сторінки
    search_books.py --png 146 -b Chen -o C:\\Temp\\p  # сторінка як PNG (подивитись формули)
    search_books.py --rebuild                         # перебудувати кеш
    search_books.py --ocr -b MyScan                   # OCR для PDF без текстового шару (повільно)
    search_books.py "..." --dir C:\\Temp\\other       # інша тека з книгами (тест)

Номер сторінки = індекс сторінки у файлі (для Котельникова номер у книзі = індекс - 1).
Кеш: <тека з книгами>/.cache/<ім'я>.txt (сторінки розділено \\f). Не в git.
PDF-скан без тексту пошуком не знаходиться, поки не зроблено --ocr (rus+ukr+eng, ~секунди/сторінку).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I не додає теку скрипта
import bookslib as bl  # noqa: E402

BOOKS = bl.BOOKS


def short(p: Path) -> str:
    n = p.stem
    if 'Plazma - chetvertoe' in n:
        name = 'Frank1968'
    else:
        # підрядок імені файлу -> коротке ім'я книги (для -b і кешу); нову книгу додай сюди
        names = {'Chen, Francis': 'ChenEN', 'Голант': 'Golant', 'Chen': 'Chen', 'Zagorodnij': 'Zagorodnij', 'Frank': 'Frank', 'Arcimovich': 'Arcimovich',
                 'PlasmaPhysics': 'Anisimov', 'Котельников': 'Kotelnikov', 'Ландау': 'Landau',
                 'Милантьев': 'Milantyev', 'Axiezer': 'Akhiezer', 'Bittenkort': 'Bittencourt'}
        name = None
        for key, short_name in names.items():
            if key in n:
                name = short_name
                break
        if name is None:
            name = re.sub(r'[^\w\-]+', '_', n, flags=re.UNICODE)[:20] or 'book'
    return name + '_pdf' if bl.is_pdf(p) else name


def load(p: Path, rebuild=False, ocr=False, folder: Path = None):
    cache = (folder or BOOKS) / '.cache'
    cache.mkdir(exist_ok=True)
    cf = cache / (short(p) + '.txt')
    if rebuild or not cf.exists() or cf.stat().st_mtime < p.stat().st_mtime:
        pages = bl.page_texts(p)
        cf.write_text('\x0c'.join(pages), encoding='utf-8')
    pages = cf.read_text(encoding='utf-8').split('\x0c')
    if bl.is_pdf(p) and not bl.has_text_layer(pages):
        of = cache / (short(p) + '.ocr.txt')
        if of.exists() and of.stat().st_mtime >= p.stat().st_mtime and not rebuild:
            return of.read_text(encoding='utf-8').split('\x0c')
        if ocr:
            print('OCR %s (%d сторінок)...' % (p.name, len(pages)), file=sys.stderr)
            texts = bl.ocr_pdf(p)
            of.write_text('\x0c'.join(texts), encoding='utf-8')
            return texts
        print('УВАГА: %s без текстового шару (скан); пошук порожній. Запусти --ocr -b %s'
              % (p.name, short(p)), file=sys.stderr)
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pattern', nargs='?')
    ap.add_argument('-b', '--book', help='підрядок імені файлу/скорочення (Chen, Zagorodnij, Frank, Arcimovich, Anisimov, Kotelnikov, Landau, Milantyev, Akhiezer, Bittencourt)')
    ap.add_argument('-C', '--context', type=int, default=0, help='рядків контексту навколо збігу')
    ap.add_argument('-m', '--max', type=int, default=20, help='макс. збігів на книгу')
    ap.add_argument('--page', type=int, help='вивести текст сторінки')
    ap.add_argument('--png', type=int, help='зберегти сторінку як PNG (потрібен -b; -o тека, -s масштаб %%)')
    ap.add_argument('-o', '--outdir', type=Path, default=Path('.'), help='тека для PNG')
    ap.add_argument('-s', '--scale', type=int, default=100, help='масштаб PNG у %%')
    ap.add_argument('--rebuild', action='store_true')
    ap.add_argument('--ocr', action='store_true', help='OCR для PDF без текстового шару')
    ap.add_argument('--dir', type=Path, default=None, help='інша тека з книгами (за замовчуванням тека скрипта)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    folder = a.dir or BOOKS

    allfiles = bl.list_books(folder)
    files = allfiles
    if a.book:
        files = [f for f in allfiles if a.book.lower() in short(f).lower() or a.book.lower() in f.name.lower()]
    if a.rebuild:
        for f in allfiles:
            load(f, True, a.ocr, folder)
            print('rebuilt', short(f))
        if not a.pattern and not a.page and not a.png:
            return
    if a.ocr and not (a.pattern or a.page or a.png or a.rebuild):
        for f in files:
            if bl.is_pdf(f):
                load(f, False, True, folder)
                print('ocr', short(f))
        return
    if a.png:
        if not a.book:
            ap.error('--png потребує -b')
        for f in files:
            out = bl.render_png(f, a.png, a.outdir, a.scale)
            print('%s p.%d -> %s' % (short(f), a.png, out))
        return
    if a.page:
        for f in files:
            pages = load(f, False, a.ocr, folder)
            print('=== %s, p.%d ===' % (short(f), a.page))
            print(pages[a.page - 1] if 0 < a.page <= len(pages) else '(нема такої сторінки)')
        return
    if not a.pattern:
        ap.error('потрібен pattern, --page, --png, --ocr або --rebuild')
    rx = re.compile(a.pattern, re.I)
    for f in files:
        pages = load(f, False, a.ocr, folder)
        n = 0
        for i, t in enumerate(pages, start=1):
            lines = t.splitlines()
            for j, line in enumerate(lines):
                if rx.search(line):
                    lo, hi = max(0, j - a.context), min(len(lines), j + a.context + 1)
                    snippet = ' | '.join(l.strip() for l in lines[lo:hi])
                    print('%s p.%d: %s' % (short(f), i, snippet[:300]))
                    n += 1
                    if n >= a.max:
                        break
            if n >= a.max:
                print('%s: ... (ліміт %d)' % (short(f), a.max))
                break


if __name__ == '__main__':
    main()
