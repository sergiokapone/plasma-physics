#!/usr/bin/env python
"""Копіює зібраний PDF силабуса під ім'ям для здачі.

Ім'я: <курс>к_<рівень>_<код спец.>_<Дисципліна>_(<статус>)_<Прізвище>_<рік>.pdf
Усе береться з самого .tex (і з protocols.tex, якщо він підключений):
  \\course, \\level, \\speciality, \\disciplinename, \\status, \\lecturer, \\kafyear.

Використання (з папки силабуса):
  python release_syllabus.py Syllabus_plasma_E6.tex            # лише копіювати
  python release_syllabus.py Syllabus_plasma_E6.tex --build    # спершу зібрати
  python release_syllabus.py Syllabus_plasma_E6.tex --out ../Submit
Без аргументів: єдиний *.tex у папці з \\documentclass{Syllabus}.
"""
import argparse, re, shutil, subprocess, sys
from pathlib import Path

LEVELS = {'бакалавр': 'бак', 'магістер': 'маг', 'доктор': 'PhD', 'філософ': 'PhD'}


def read(path):
    return Path(path).read_text(encoding='utf8')


def uncomment(text):
    return '\n'.join(re.sub(r'(?<!\\)%.*', '', ln) for ln in text.splitlines())


def field(text, name):
    m = re.search(r'\\' + name + r'(?:\[[^\]]*\])?\s*\{((?:[^{}]|\{[^{}]*\})*)\}', text)
    return m.group(1).strip() if m else None


def find_tex(arg):
    if arg:
        return Path(arg)
    found = [p for p in Path('.').glob('*.tex') if re.search(r'\\documentclass(\[.*?\])?\{Syllabus\}', read(p))]
    if len(found) != 1:
        sys.exit('Вкажіть .tex явно, знайдено: %s' % [str(p) for p in found])
    return found[0]


def collect(tex):
    """Текст силабуса з підключеним protocols.tex (\\input)."""
    text = uncomment(read(tex))
    for m in re.finditer(r'\\input\{([^}]+)\}', text):
        f = tex.parent / (m.group(1) if m.group(1).endswith('.tex') else m.group(1) + '.tex')
        if f.exists():
            text += '\n' + uncomment(read(f))
    return text


def build(tex):
    d = tex.parent
    name = tex.stem
    run = lambda *c: subprocess.run(c, cwd=d, check=True, stdout=subprocess.DEVNULL)
    run('xelatex', '-interaction=nonstopmode', tex.name)
    run('biber', name)
    run('xelatex', '-interaction=nonstopmode', tex.name)
    run('xelatex', '-interaction=nonstopmode', tex.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tex', nargs='?')
    ap.add_argument('--build', action='store_true', help='зібрати xelatex+biber перед копіюванням')
    ap.add_argument('--out', help='куди класти (за замовчуванням — поруч із .tex)')
    ap.add_argument('--author', help='прізвище, якщо автоматично визначилось неправильно')
    a = ap.parse_args()

    tex = find_tex(a.tex)
    if a.build:
        build(tex)
    pdf = tex.with_suffix('.pdf')
    if not pdf.exists():
        sys.exit('Немає %s (збирайте або --build)' % pdf)

    t = collect(tex)
    course = field(t, 'course')
    level = field(t, 'level') or ''
    spec = (field(t, 'speciality') or '').split()[0]
    disc = field(t, 'disciplinename')
    status = (field(t, 'status') or '').lower()
    year = field(t, 'kafyear')
    lecturer = field(t, 'lecturer') or ''
    fio = lecturer.replace(',', ' ').split()
    surname = a.author or (fio[-3] if len(fio) >= 3 else (fio[-1] if fio else ''))
    lvl = next((v for k, v in LEVELS.items() if k in level.lower()), level.split()[0] if level else '')

    missing = [n for n, v in [('course', course), ('speciality', spec), ('disciplinename', disc), ('kafyear', year)] if not v]
    if missing:
        sys.exit('Не знайдено в .tex: ' + ', '.join(missing))

    parts = ['%sк' % course, lvl, spec, disc.replace(' ', '_'), '(%s)' % status if status else '', surname, year]
    out_name = '_'.join(p for p in parts if p) + '.pdf'
    out = Path(a.out) if a.out else tex.parent
    out.mkdir(parents=True, exist_ok=True)
    dest = out / out_name
    shutil.copyfile(pdf, dest)
    print(dest)


if __name__ == '__main__':
    main()
