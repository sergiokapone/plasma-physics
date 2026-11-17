#!/usr/bin/env python
"""Оновлює сторінки нашого посібника в рядках «Де вивчати» силабуса за ../PlasmaBook/main.toc.

Книга змінюється (розділи додаються, сторінки пливуть), тому сторінки не вписують руками:
  python update_refs.py Syllabus_plasma_E6.tex            # показати, що зміниться
  python update_refs.py Syllabus_plasma_E6.tex --write    # записати зміни у .tex

Рядок силабуса: \\wherestudy[<ключ розділу>]{\\cite[...]{ponomarenko2026plasma}; ...}.
Заміняється лише перша цитата (наш посібник); Chen і Анісімов (статичні книги) не чіпаються.
Блок «Питання до залікової контрольної роботи» (між % BEGIN/END QUESTIONS) теж генерується тут.
Діапазон сторінок розділу: від сторінки розділу до сторінки перед «Задачі» (у розд. 0 — до «Контрольних питань»).
Ключ розділу -> номер розділу задає CHAPTERS нижче (HTML-ім'я = ключ у \\wherestudy[...]).
"""
import argparse, re, sys
from pathlib import Path

TOC = Path(__file__).resolve().parent.parent / 'PlasmaBook' / 'main.toc'

# ключ у \wherestudy[...] -> номер розділу посібника (розд. 0 — огляд «Плазма довкола нас»)
CHAPTERS = {'basics': 1, 'waves': 2, 'motion': 3, 'collisions': 4, 'fluid': 5, 'linearwaves': 6,
            'kinetics': 7, 'instability': 8, 'confinement': 9, 'fusion': 10, 'discharge': 11, 'scales': 12}
# до розділу 1 додається огляд (розд. 0); текст-пояснення в дужках
EXTRA = {'basics': (0, 'огляд, §~0.1 «Що таке плазма?»')}


def parse_toc():
    """Повертає список (тип, номер або '', сторінка, заголовок) у порядку змісту."""
    out = []
    for ln in TOC.read_text(encoding='utf8').splitlines():
        m = re.match(r'\\contentsline \{(chapter|section)\}\{(?:\\numberline \{([^}]*)\})?(.*)\}\{(\d+)\}\{', ln)
        if m:
            out.append((m.group(1), m.group(2) or '', int(m.group(4)), m.group(3)))
    return out


def chapter_range(toc, n):
    """(перша §, остання §, перша сторінка, остання сторінка) розділу n."""
    i0 = next(i for i, e in enumerate(toc) if e[0] == 'chapter' and e[1] == str(n))
    start = toc[i0][2]
    secs, end = [], None
    for e in toc[i0 + 1:]:
        if e[0] == 'chapter':
            break
        if e[1].startswith('%d.' % n):
            secs.append(e[1])
        elif e[3].startswith('Задачі') and end is None:
            end = e[2] - 1
        elif e[3].startswith('Контрольні питання') and end is None:
            end = e[2]
    return (secs[0] if secs else None), (secs[-1] if secs else None), start, end


def pages(a, b):
    return 'с.~%d' % a if a == b else 'с.~%d--%d' % (a, b)


def book_cite(toc, key):
    n = CHAPTERS[key]
    f, l, s, e = chapter_range(toc, n)
    sec = '§§~%s--%s' % (f, l) if f and f != l else '§~%s' % f
    part = 'розд.~%d, %s, %s' % (n, sec, pages(s, e))
    if key in EXTRA:
        n0, label = EXTRA[key]
        _, _, s0, e0 = chapter_range(toc, n0)
        part = 'розд.~%d (%s), %s; %s' % (n0, label, pages(s0, e0), part)
    return part


def questions_pages(toc):
    """[(номер розділу, сторінка «Контрольних питань»)] у порядку змісту."""
    res, cur = [], None
    for e in toc:
        if e[0] == 'chapter' and e[1].isdigit():
            cur = int(e[1])
        elif e[0] == 'section' and e[3].startswith('Контрольні питання') and cur is not None:
            res.append((cur, e[2]))
            cur = None
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tex')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    p = Path(a.tex)
    s = p.read_text(encoding='utf8')
    toc = parse_toc()
    changed = 0

    def rep(m):
        nonlocal changed
        key = m.group(1)
        if key not in CHAPTERS:
            print('? немає ключа', key); return m.group(0)
        new = book_cite(toc, key)
        old = m.group(2)
        if old != new:
            changed += 1
            print('%-12s %s\n%-12s -> %s' % (key, old, '', new))
        return '\\wherestudy[%s]{\\cite[%s]{ponomarenko2026plasma}' % (key, new)

    s2 = re.sub(r'\\wherestudy\[([^\]]*)\]\{\\cite\[(.*?)\]\{ponomarenko2026plasma\}', rep, s)
    qp = questions_pages(toc)
    text = '; '.join('розд.~%d --- с.~%d' % (n, pg) for n, pg in qp) + '.'
    m = re.search(r'(% BEGIN QUESTIONS[^\n]*\n)(.*?)(% END QUESTIONS)', s2, re.S)
    if m:
        if m.group(2).strip() != text:
            changed += 1
            print('питання ->', text)
        s2 = s2[:m.start(2)] + text + '\n' + s2[m.start(3):]
    else:
        print('? немає блоку BEGIN/END QUESTIONS')
    print('змін: %d' % changed)
    if a.write and s2 != s:
        p.write_text(s2, encoding='utf8', newline='')
        print('записано', p)


if __name__ == '__main__':
    main()
