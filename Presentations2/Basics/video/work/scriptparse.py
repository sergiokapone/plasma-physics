# -*- coding: utf-8 -*-
import re, sys
sys.path.insert(0, r'D:\Projects\LaTeX\plasma-physics\Presentations2\Basics\video\work')

SCRIPT = r'D:\Projects\LaTeX\plasma-physics\Presentations2\Basics\Basics_script.md'

def norm_words(text):
    text = text.lower().replace('’', "'").replace('ʼ', "'")
    return re.findall(r"[\w'\-]+", text)

def slide_texts():
    src = open(SCRIPT, encoding='utf-8').read()
    parts = re.split(r'^## Слайд ', src, flags=re.M)[1:]
    out = {}
    for p in parts:
        m = re.match(r'(\d+)', p)
        n = int(m.group(1))
        if '**Текст для читання:**' not in p:
            continue
        body = p.split('**Текст для читання:**', 1)[1].split('🖱', 1)[0]
        lines = [l for l in body.splitlines() if l.strip() and not l.lstrip().startswith('>')]
        out[n] = ' '.join(lines)
    return out

def phrase_index(words, phrase, start=0):
    pw = norm_words(phrase)
    for i in range(start, len(words) - len(pw) + 1):
        if words[i:i + len(pw)] == pw:
            return i
    return None

if __name__ == '__main__':
    from cues import CUES
    T = slide_texts()
    for n in range(1, 14):
        w = norm_words(T[n])
        last = -1
        for ph, pts in CUES[n]:
            i = phrase_index(w, ph, max(last, 0))
            flag = '' if (i is not None and i >= last) else '  <-- ПРОБЛЕМА'
            print(n, len(w), ph, i, flag)
            if i is not None: last = i
