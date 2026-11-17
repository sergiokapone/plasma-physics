#!/usr/bin/env python
"""Перевірка силабуса перед здачею (нічого не збирає й не править).

  python check_syllabus.py Syllabus_plasma_E6.tex

Перевіряє:
  1. суми годин у таблицях (лекції, практичні, СРС) = \\AudDistribHours (СРС = кредити*30 - лекції - практичні);
  2. журнал збірки (.log): Overfull > 10 пт, undefined references/citations, помилки;
  3. кожен розділ з ../PlasmaBook/main.tex (\\multiinclude) має рядок \\wherestudy[<розділ>] у таблиці тем;
  4. сторінки «Де вивчати» актуальні (update_refs.py без --write не показує змін);
  5. немає слова «студент» поза коментарями (замість нього «здобувач вищої освіти»).
Код виходу 1, якщо знайдено проблеми.
"""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def uncomment(t):
    return '\n'.join(re.sub(r'(?<!\\)%.*', '', l) for l in t.splitlines())


def main():
    tex = Path(sys.argv[1]) if len(sys.argv) > 1 else next(HERE.glob('Syllabus_*.tex'))
    raw = tex.read_text(encoding='utf8')
    t = uncomment(raw)
    problems = []

    # 1. години
    m = re.search(r'\\AudDistribHours\s*\{([\d.]+)\}\s*\{(\d*)\}\s*\{(\d*)\}\s*\{(\d*)\}', t)
    cr, lec, prac, lab = (float(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0), int(m.group(4) or 0)) if m else (None,) * 4
    if not m:
        problems.append('не знайдено \\AudDistribHours')
    def clsum(name):
        mm = re.search(r'\\clist_const:Nn \\c_syl_%s_clist\s*\{\s*([\d,\s]+)\}' % name, t)
        return sum(int(x) for x in mm.group(1).split(',')) if mm else None
    sl, sp, ss = clsum('lec'), clsum('prac'), clsum('srs')
    if m:
        print('години: шапка лекц.=%s практ.=%s кредити=%s; таблиці лекц.=%s практ.=%s СРС=%s' % (lec, prac, cr, sl, sp, ss))
        if sl is not None and sl != lec: problems.append('лекції: таблиця %s != шапка %s' % (sl, lec))
        if sp is not None and sp != prac: problems.append('практичні: таблиця %s != шапка %s' % (sp, prac))
        want = int(cr * 30) - lec - prac - lab
        if ss is not None and ss != want: problems.append('СРС: таблиця %s != %s (= кредити*30 - ауд.)' % (ss, want))

    # 2. журнал
    log = tex.with_suffix('.log')
    if log.exists():
        txt = log.read_text(encoding='utf8', errors='replace')
        for mm in re.finditer(r'Overfull \\hbox \(([\d.]+)pt too wide\) in paragraph at lines (\d+)', txt):
            srcline = raw.splitlines()[int(mm.group(2)) - 1].strip() if int(mm.group(2)) <= len(raw.splitlines()) else ''
            if srcline == '\\printhead':
                continue  # відомий виступ шапки в Syllabus.cls (~20 пт), на сторінці непомітний
            if float(mm.group(1)) > 10:
                problems.append('Overfull %.1f пт (рядок %s)' % (float(mm.group(1)), mm.group(2)))
        for pat in (r'Citation `[^\']*\' .*undefined', r'Reference `[^\']*\' .*undefined', r'^! '):
            for mm in re.finditer(pat, txt, re.M):
                problems.append('журнал: ' + mm.group(0)[:100])
    else:
        problems.append('немає %s (спершу зберіть)' % log.name)

    # 3. розділи книги
    mt = HERE.parent / 'PlasmaBook' / 'main.tex'
    if mt.exists():
        src = uncomment(mt.read_text(encoding='utf8'))
        blocks = re.findall(r'\\multiinclude\{([^}]*)\}', src)
        chapters = [c.strip() for c in blocks[0].split(',') if c.strip()] if blocks else []
        have = set(x.lower() for x in re.findall(r'\\wherestudy\[([^\]]*)\]', t))
        for c in chapters:
            if c.lower() == 'nature':
                continue  # огляд входить до рядка Basics
            if c.lower() not in have:
                problems.append('розділ книги %s не має рядка \\wherestudy[%s]' % (c, c.lower()))
    else:
        problems.append('немає ../PlasmaBook/main.tex')

    # 4. актуальність сторінок
    r = subprocess.run([sys.executable, '-I', str(HERE / 'update_refs.py'), str(tex)], capture_output=True, text=True, encoding='utf8', errors='replace')
    mm = re.search(r'змін: (\d+)', r.stdout)
    if mm and int(mm.group(1)) > 0:
        problems.append('сторінки «Де вивчати» застарілі (%s): python update_refs.py %s --write' % (mm.group(1), tex.name))

    # 5. термін
    for i, ln in enumerate(raw.splitlines(), 1):
        if not ln.lstrip().startswith('%') and re.search(r'\b[Сс]тудент', uncomment(ln)):
            problems.append('рядок %d: «студент» (треба «здобувач вищої освіти»)' % i)

    if problems:
        print('ПРОБЛЕМИ (%d):' % len(problems))
        for p in problems:
            print(' -', p)
        sys.exit(1)
    print('Усе гаразд.')


if __name__ == '__main__':
    main()
