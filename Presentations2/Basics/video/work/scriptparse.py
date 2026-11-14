# -*- coding: utf-8 -*-
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'Basics_script.md')

def norm_words(text):
    text = text.lower().replace('’', "'").replace('ʼ', "'")
    return re.findall(r"[\w'\-]+", text)

def _read_text(block):
    body = block.split('**Текст для читання:**', 1)[1].split('🖱', 1)[0]
    lines = [l for l in body.splitlines() if l.strip() and not l.lstrip().startswith('>')]
    return ' '.join(lines)

def slide_texts():
    src = open(SCRIPT, encoding='utf-8').read()
    parts = re.split(r'^## Слайд ', src, flags=re.M)[1:]
    out = {}
    for p in parts:
        m = re.match(r'(\d+)', p)
        n = int(m.group(1))
        if '**Текст для читання:**' not in p:
            continue
        out[n] = _read_text(p)
    return out

def unit_texts():
    """Одиниці озвучення: '01'…'39', але слайд 18 → '18a'…'18d' (чотири кроки; файли audio/18a.wav…)."""
    src = open(SCRIPT, encoding='utf-8').read()
    parts = re.split(r'^## Слайд ', src, flags=re.M)[1:]
    out = {}
    for p in parts:
        n = int(re.match(r'(\d+)', p).group(1))
        if n == 18:
            steps = re.split(r'^### Крок ', p, flags=re.M)[1:]
            for k, st in enumerate(steps):
                out['18' + 'abcd'[k]] = _read_text(st)
        elif '**Текст для читання:**' in p:
            out[f'{n:02d}'] = _read_text(p)
    return out

def phrase_index(words, phrase, start=0):
    pw = norm_words(phrase)
    for i in range(start, len(words) - len(pw) + 1):
        if words[i:i + len(pw)] == pw:
            return i
    return None

if __name__ == '__main__':
    U = unit_texts()
    print(len(U), 'одиниць:', ' '.join(U))
    print('слів усього:', sum(len(norm_words(t)) for t in U.values()))
