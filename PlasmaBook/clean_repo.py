#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Чистить git-історію репозиторію plasma-physics від старих збірок, щоб вона не росла безкінечно.

З УСІЄЇ історії прибираються старі версії файлів зі списку PURGE (зібраний сайт online/ і PlasmaBook/main.pdf:
кожна перезбірка комітиться заново). Поточні версії НЕ втрачаються: після очищення вони повертаються одним комітом,
а дерево нового коміту порівнюється з деревом до очищення (хеш мусить збігтися, інакше нічого не публікується).

Порядок:  звіт -> резервна копія (git clone --mirror поруч із репозиторієм) -> git filter-repo -> повернення поточних
файлів -> звірка дерева -> повернення origin -> force-push -> перевірка свіжим клоном з GitHub.
Потрібен git filter-repo (pip install git-filter-repo).

Запуск:  python -I clean_repo.py --dry-run   лише звіт: що піде й скільки це займає (нічого не змінює)
         python -I clean_repo.py             звіт, питання YES, очищення, force-push
         python -I clean_repo.py --yes       те саме без питання
         python -I clean_repo.py --no-push   очистити локально, force-push не робити (origin буде прибрано; див. звіт)

Після force-push усі хеші комітів змінюються; інші клони репозиторію треба клонувати заново.
Не чіпає Presentations та все поза PURGE."""
import argparse
import datetime
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                        # корінь репозиторію (поруч із index.html)
BRANCH = 'main'
sys.stdout.reconfigure(line_buffering=True)         # повідомлення скрипта й git filter-repo не перемішуються

# Що чистити з історії: звичайний рядок — файл або тека, 'regex:…' — регулярний вираз (як у git filter-repo).
PURGE = ['PlasmaBook/main.pdf', 'regex:^online/']


def git(*args, check=True, cwd=None, binary=False):
    r = subprocess.run(['git', '-c', 'core.quotepath=off', *args], cwd=cwd or ROOT, capture_output=True)
    if check and r.returncode:
        sys.exit('ПОМИЛКА: git %s\n%s' % (' '.join(args), r.stderr.decode('utf-8', 'replace').strip()))
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace')


def matcher():
    lits = [p for p in PURGE if not p.startswith('regex:')]
    rxs = [re.compile(p[6:]) for p in PURGE if p.startswith('regex:')]
    return lambda path: (any(path == l or path.startswith(l.rstrip('/') + '/') for l in lits)
                         or any(r.search(path) for r in rxs))


def mb(n):
    return '%.1f МБ' % (n / 1048576)


def history_report(match):
    """(кількість версій і розмір усіх версій у історії, те саме для поточного коміту)."""
    objs = git('rev-list', '--objects', '--all').splitlines()
    p = subprocess.run(['git', 'cat-file', '--batch-check=%(objecttype) %(objectname) %(objectsize)'],
                       cwd=ROOT, input='\n'.join(l.split(' ', 1)[0] for l in objs).encode(), capture_output=True)
    info = {}
    for line in p.stdout.decode().splitlines():
        t, h, s = line.split()
        info[h] = (t, int(s))
    hist = {}                                      # вміст (хеш blob) -> розмір, усе, що колись було за шляхами PURGE
    for line in objs:
        parts = line.split(' ', 1)
        if len(parts) < 2 or not match(parts[1]): continue
        if info.get(parts[0], ('', 0))[0] == 'blob':
            hist[parts[0]] = info[parts[0]][1]
    cur = {}                                       # те саме для поточного коміту
    for line in git('ls-tree', '-r', '-l', 'HEAD').splitlines():
        meta, path = line.split('\t', 1)
        if match(path):
            m = meta.split()
            cur[m[2]] = int(m[3])
    old = {h: s for h, s in hist.items() if h not in cur}     # старі версії: були в історії, у поточному коміті їх нема
    return len(hist), sum(hist.values()), len(cur), sum(cur.values()), len(old), sum(old.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--dry-run', action='store_true', help='лише звіт')
    ap.add_argument('--yes', action='store_true', help='не питати YES')
    ap.add_argument('--no-push', action='store_true', help='не робити force-push')
    args = ap.parse_args()

    if subprocess.run(['git', 'filter-repo', '--version'], cwd=ROOT, capture_output=True).returncode:
        sys.exit('ПОМИЛКА: немає git filter-repo (pip install git-filter-repo)')
    match = matcher()
    hist_n, hist_b, cur_n, cur_b, old_n, old_b = history_report(match)
    old_head = git('rev-parse', 'HEAD').strip()
    n_commits = int(git('rev-list', '--count', 'HEAD').strip())
    pack = [l for l in git('count-objects', '-vH').splitlines() if l.startswith('size-pack')]
    print('Репозиторій: %s, %d комітів, %s' % (ROOT, n_commits, pack[0] if pack else ''))
    print('Чиститься (PURGE): %s' % ', '.join(PURGE))
    print('  у всій історії: %d різних вмістів, %s' % (hist_n, mb(hist_b)))
    print('  у поточному коміті (лишається): %d, %s' % (cur_n, mb(cur_b)))
    print('  старих версій (підуть з історії): %d, %s' % (old_n, mb(old_b)))
    if not old_n:
        print('Нічого чистити: старих версій немає.')
        return 0
    if args.dry_run:
        return 0

    # --- умови безпеки -------------------------------------------------------------------------------
    if git('rev-parse', '--abbrev-ref', 'HEAD').strip() != BRANCH:
        sys.exit('ПОМИЛКА: потрібна гілка %s' % BRANCH)
    if git('status', '--porcelain', '--untracked-files=no').strip():
        sys.exit('ПОМИЛКА: є незакомічені зміни — спершу закоміть (інакше очищення їх не збереже)')
    untracked = [l[3:] for l in git('status', '--porcelain', '--untracked-files=all').splitlines() if l.startswith('??')]
    if any(match(u) for u in untracked):
        sys.exit('ПОМИЛКА: у теках PURGE є незакомічені нові файли:\n  ' + '\n  '.join(u for u in untracked if match(u))[:600])
    remote = git('remote', 'get-url', 'origin', check=False).strip()
    if not remote:
        sys.exit('ПОМИЛКА: немає origin')
    if not args.no_push:
        git('fetch', '-q', 'origin')
        if git('rev-parse', 'origin/' + BRANCH).strip() != old_head:
            sys.exit('ПОМИЛКА: origin/%s ≠ локальний %s: хтось запушив інше, або локальне відстає. Спершу синхронізуй.' % (BRANCH, BRANCH))
    if not args.yes:
        print('\nЦе ПЕРЕПИШЕ історію%s; хеші всіх комітів зміняться. Резервна копія буде створена.'
              % ('' if args.no_push else ' і зробить force-push у ' + remote))
        if input('Введи YES: ').strip() != 'YES':
            print('Скасовано.'); return 1

    # --- 1. резервна копія -----------------------------------------------------------------------------
    stamp = datetime.date.today().isoformat()
    backup = os.path.join(os.path.dirname(ROOT), '%s-backup-%s.git' % (os.path.basename(ROOT), stamp))
    n = 2
    while os.path.exists(backup):
        backup = os.path.join(os.path.dirname(ROOT), '%s-backup-%s-%d.git' % (os.path.basename(ROOT), stamp, n)); n += 1
    print('\n[1/5] Резервна копія: %s' % backup)
    subprocess.run(['git', 'clone', '-q', '--mirror', ROOT, backup], check=True)
    if git('rev-parse', BRANCH, cwd=backup).strip() != old_head or subprocess.run(
            ['git', 'fsck', '--no-dangling'], cwd=backup, capture_output=True).returncode:
        sys.exit('ПОМИЛКА: резервна копія не пройшла перевірку; нічого не змінено')
    old_tree = git('rev-parse', 'HEAD^{tree}').strip()

    # --- 2. поточні файли (з коміту, байт у байт) ------------------------------------------------------
    print('[2/5] Беру поточні версії файлів з коміту %s' % old_head[:7])
    cur_paths = [l.split('\t', 1)[1] for l in git('ls-tree', '-r', 'HEAD').splitlines() if match(l.split('\t', 1)[1])]
    keep = tempfile.mkdtemp(prefix='purge-keep-')
    tar = git('archive', '--format=tar', 'HEAD', '--', *cur_paths, binary=True)
    with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
        tf.extractall(keep, **({'filter': 'data'} if hasattr(tarfile, 'data_filter') else {}))

    # --- 3. очищення ---------------------------------------------------------------------------------
    print('[3/5] git filter-repo: прибираю старі версії з усієї історії')
    cmd = ['git', 'filter-repo', '--force', '--invert-paths']
    for p in PURGE:
        cmd += ['--path-regex', p[6:]] if p.startswith('regex:') else ['--path', p]
    if subprocess.run(cmd, cwd=ROOT).returncode:
        sys.exit('ПОМИЛКА: filter-repo. Резервна копія: %s' % backup)

    # --- 4. повернення поточних файлів і звірка ------------------------------------------------------
    print('[4/5] Повертаю поточні версії, звіряю дерево')
    for p in cur_paths:
        dst = os.path.join(ROOT, *p.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(keep, *p.split('/')), dst)
    git('add', '--', *cur_paths)
    new_tree = git('write-tree').strip()
    if new_tree != old_tree:
        sys.exit('ПОМИЛКА: дерево після очищення (%s) ≠ колишнє (%s). НЕ публікую.\nРезервна копія: %s' % (new_tree[:10], old_tree[:10], backup))
    git('commit', '-q', '-m', 'Сайт і PDF: поточні версії після очищення історії від старих збірок (clean_repo.py)')
    shutil.rmtree(keep, ignore_errors=True)
    git('remote', 'add', 'origin', remote, check=False)
    pack = [l for l in git('count-objects', '-vH').splitlines() if l.startswith('size-pack')]
    print('      дерево збігається (%s); комітів: %s; %s' % (old_tree[:10], git('rev-list', '--count', 'HEAD').strip(), pack[0] if pack else ''))
    if args.no_push:
        print('--no-push: force-push не робив. Щоб опублікувати: git push --force -u origin %s' % BRANCH)
        return 0

    # --- 5. force-push і перевірка свіжим клоном --------------------------------------------------------
    print('[5/5] force-push і перевірка свіжим клоном')
    if subprocess.run(['git', 'push', '--force', '-u', 'origin', BRANCH], cwd=ROOT).returncode:
        sys.exit('ПОМИЛКА: push. Резервна копія: %s' % backup)
    tmp = tempfile.mkdtemp(prefix='purge-verify-')
    clone = os.path.join(tmp, 'c')
    subprocess.run(['git', 'clone', '-q', remote, clone], check=True)
    ok_tree = git('rev-parse', 'HEAD^{tree}', cwd=clone).strip() == old_tree
    ok_fsck = subprocess.run(['git', 'fsck', '--no-dangling'], cwd=clone, capture_output=True).returncode == 0
    shutil.rmtree(tmp, ignore_errors=True)
    print('      клон з GitHub: дерево %s, fsck %s' % ('збігається' if ok_tree else 'НЕ ЗБІГАЄТЬСЯ', 'чистий' if ok_fsck else 'з помилками'))
    print('\nГотово. Резервна копія (можна видалити, коли все перевірено): %s' % backup)
    print('Інші клони репозиторію треба клонувати заново.')
    return 0 if (ok_tree and ok_fsck) else 1


if __name__ == '__main__':
    sys.exit(main())
