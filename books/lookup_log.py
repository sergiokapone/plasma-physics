#!/usr/bin/env python3
"""Журнал сверок з літературою: books/LOOKUPS.md. Щоб не шукати те саме двічі.

    python -I lookup_log.py find "затухан|Ландау"          # шукати за regex у всьому журналі
    python -I lookup_log.py add "тема" "джерело (книга §, с.)" "що сказано" "вердикт щодо PlasmaBook"
    python -I lookup_log.py add ... --where LinearWaves.tex:155   # необов'язково: де в нашій книзі
    python -I lookup_log.py list                            # весь журнал

Правила запису: одна перевірена річ = один рядок; номери сторінок лише ті, що дивились на зображенні;
для PDF/djvu вказувати, чи це індекс файлу, чи номер у книзі. Чого не знайдено, теж записувати
(вердикт «не знайдено»), щоб наступного разу не витрачати час.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

LOG = Path(__file__).resolve().parent / 'LOOKUPS.md'
HEADER = ('# Журнал сверок з літературою\n\n'
          'Що вже перевірено в підручниках і що знайдено. Перед новим пошуком: '
          '`python -I lookup_log.py find "regex"`. Додавати: `lookup_log.py add ...`.\n\n'
          '| Дата | Тема | Джерело | Що сказано | Вердикт щодо PlasmaBook |\n'
          '|---|---|---|---|---|\n')


def esc(s: str) -> str:
    return re.sub(r'\s+', ' ', s.replace('|', '\\|')).strip()


def rows():
    if not LOG.exists():
        return []
    return [l for l in LOG.read_text(encoding='utf-8').splitlines() if l.startswith('| 20')]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('find'); f.add_argument('pattern')
    sub.add_parser('list')
    a = sub.add_parser('add')
    for n in ('topic', 'source', 'finding', 'verdict'):
        a.add_argument(n)
    a.add_argument('--where', default='')
    a.add_argument('--cite', default='', help='ключ у bibliography.bib, що вже стоїть як \\cite у тексті')
    args = ap.parse_args()
    if args.cmd == 'list':
        print('\n'.join(rows()) or '(порожньо)')
    elif args.cmd == 'find':
        rx = re.compile(args.pattern, re.I)
        hits = [r for r in rows() if rx.search(r)]
        print('\n'.join(hits) if hits else '(нічого не знайдено в журналі)')
    else:
        if not LOG.exists():
            LOG.write_text(HEADER, encoding='utf-8', newline='\n')
        verdict = (esc(args.verdict) + ((' [' + esc(args.where) + ']') if args.where else '')
                   + ((' (cite: ' + esc(args.cite) + ')') if args.cite else ''))
        row = '| %s | %s | %s | %s | %s |\n' % (datetime.date.today().isoformat(), esc(args.topic),
                                                 esc(args.source), esc(args.finding), verdict)
        with LOG.open('a', encoding='utf-8', newline='\n') as fh:
            fh.write(row)
        print('додано:', row.strip()[:160])


if __name__ == '__main__':
    main()
