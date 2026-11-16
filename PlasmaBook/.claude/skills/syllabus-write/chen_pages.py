import re, glob, sys
from collections import Counter
import fitz
sys.stdout.reconfigure(encoding='utf8')
B = r'D:\Projects\LaTeX\plasma-physics\books'
pdf = glob.glob(B + r'\Chen, Francis*.pdf')[0]
doc = fitz.open(pdf)
N = len(doc)

# 1. друкований номер для кожного індексу pdf
cand = {}
for i in range(1, N + 1):
    lines = [l.strip() for l in doc[i - 1].get_text().splitlines() if l.strip()]
    for l in lines[:3] + lines[-3:]:
        if re.fullmatch(r'\d{1,3}', l) and 0 < int(l) < 500:
            cand.setdefault(i, []).append(int(l))
offs = {i: [i - n for n in v] for i, v in cand.items()}

def printed(i):
    c = Counter()
    for j in range(i - 8, i + 9):
        for o in offs.get(j, []):
            c[o] += 1 if j != i else 2
    o = c.most_common(1)[0][0]
    return i - o

# 2. зміст
toc = {}
for ln in open(B + r'\TOC_Chen-en.md', encoding='utf8'):
    m = re.match(r'\s*-\s+(?:Chapter (\d+):|(\d+(?:\.\d+)*)\s)', ln)
    n = re.search(r'—\s*с\.\s*(\d+)\s*$', ln.strip())
    if m and n:
        key = ('ch' + m.group(1)) if m.group(1) else m.group(2)
        toc.setdefault(key, int(n.group(1)))

def top_of_page(idx, key):
    t = [l.strip() for l in doc[idx - 1].get_text().splitlines() if l.strip()]
    return bool(t) and (t[0].startswith(key) or t[0].startswith('Chapter'))

def rng(a, b):
    """сторінки від початку розділу a до кінця перед b (друковані)"""
    ia, ib = toc[a], toc[b]
    end = ib - 1 if top_of_page(ib, b.replace('ch', '')) else ib
    return printed(ia), printed(end)

def fmt(a, b, label, many):
    x, y = rng(a, b)
    pg = 'с.~%d' % x if x == y else 'с.~%d--%d' % (x, y)
    return '%s, %s' % (label, pg)

SPEC = [
 [("1.2", "1.7", "§§~1.2--1.6"), ("8.2", "8.3", "§~8.2 (шар, зонд)")],
 [("4.3", "4.5", "§§~4.3--4.4"), ("4.12", "4.14", "§§~4.12--4.13")],
 [("2.2", "ch3", "§§~2.2--2.8")],
 [("5.2.1", "5.2.2", "§~5.2.1"), ("5.5", "5.6", "§~5.5"), ("5.6", "5.7", "§~5.6")],
 [("ch3", "ch4", "гл.~3"), ("5.7", "5.10", "§§~5.7--5.9"), ("6.2", "6.5", "§§~6.2--6.4"), ("8.9", "8.10", "§~8.9 (пересполучення)")],
 [("4.5", "4.7", "§§~4.5--4.6"), ("4.14", "ch5", "§§~4.14--4.21")],
 [("7.1", "7.7", "§§~7.1--7.6")],
 [("6.5", "ch7", "§§~6.5--6.9")],
 [("10.2.1", "10.3", "§~10.2.1"), ("5.10", "ch6", "§~5.10"), ("6.3", "6.4", "§~6.3")],
 [("1.7.2", "1.7.3", "§~1.7.2"), ("10.2", "10.2.1", "§~10.2"), ("10.4", "10.5", "§~10.4")],
 [("1.7.1", "1.7.2", "§~1.7.1"), ("8.2", "8.3", "§~8.2"), ("10.5", "10.6", "§~10.5"), ("9.5", "9.6", "§~9.5")],
 [("1.5", "1.7", "§§~1.5--1.6"), ("3.6", "ch4", "§~3.6"), ("4.7", "4.8", "§~4.7")],
]
for i, row in enumerate(SPEC, 1):
    print(i, '; '.join(fmt(a, b, l, 0) for a, b, l in row))
print('offsets sample:', {i: i - printed(i) for i in (14, 32, 63, 101, 147, 157, 222, 280, 333, 365, 402)})
