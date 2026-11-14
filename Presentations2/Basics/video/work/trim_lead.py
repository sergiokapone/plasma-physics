# -*- coding: utf-8 -*-
"""Прибирає зайве слово на початку синтезованих речень (витік хвоста зразка голосу: «вольт»).
Запуск: python -X utf8 trim_lead.py [--apply] [01 02 …]   (без --apply — лише звіт)
Для кожного tts/s/<ід>_kk.wav: whisper дає слова з часом; якщо перше розпізнане слово не збігається з першим
словом речення зі сценарію, а друге збігається — різ у найтихішій точці між ними (+ швидке наростання).
Оригінали -> tts/s_orig/. Після --apply перезібрати одиниці: tts_synth.py <ід> (кеш речень не перегенеровується).
"""
import os, re, sys, shutil, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('HF_HOME', 'D:/Programs/Utility/omnivoice/hf_cache')
import numpy as np, soundfile as sf, torch
from transformers import pipeline
from scriptparse import unit_texts, norm_words
from tts_synth import split_sentences

S = os.path.join(HERE, 'tts', 's')
SO = os.path.join(HERE, 'tts', 's_orig')

def nw(t):
    return re.sub(r"[^\w'-]", '', t.lower().replace('ʼ', "'").replace('’', "'")).strip('-')

def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def main():
    apply = '--apply' in sys.argv
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    asr = pipeline('automatic-speech-recognition', model='openai/whisper-large-v3-turbo', device='cuda:0', torch_dtype=torch.float16)
    texts = unit_texts()
    os.makedirs(SO, exist_ok=True)
    stats = {'ok': 0, 'trim': 0, 'unsure': 0}
    for u, t in texts.items():
        if want and u not in want:
            continue
        for k, s in enumerate(split_sentences(t)):
            f = os.path.join(S, f'{u}_{k:02d}.wav')
            if not os.path.exists(f) or os.path.exists(os.path.join(SO, f'{u}_{k:02d}.wav')):
                continue   # нема файла або вже оброблено
            exp = norm_words(s)[0]
            a, sr = sf.read(f)
            r = asr({'raw': a.astype('float32'), 'sampling_rate': sr}, return_timestamps='word',
                    generate_kwargs={'language': 'uk', 'task': 'transcribe'})
            ch = [c for c in r['chunks'] if nw(c['text'])]
            if len(ch) < 2:
                stats['unsure'] += 1; continue
            w0, w1 = nw(ch[0]['text']), nw(ch[1]['text'])
            first_ok = sim(w0, exp) >= 0.6 or w0.isdigit() or exp.isdigit() or any(x.isdigit() for x in (w0, w1))
            if first_ok or sim(w1, exp) < 0.6:
                if not first_ok:
                    print(f'  ? {u}_{k:02d} перше «{w0}», очікувалось «{exp}», друге «{w1}»'); stats['unsure'] += 1
                else:
                    stats['ok'] += 1
                continue
            # зайве перше слово: різ у мінімумі енергії між його кінцем і початком другого
            e0, s1 = ch[0]['timestamp'][1], ch[1]['timestamp'][0]
            lo, hi = max(0.0, e0 - 0.10), max(e0 + 0.10, min(s1 + 0.02, e0 + 0.35))
            win = int(0.01 * sr)
            seg = np.abs(a[int(lo * sr):int(hi * sr)])
            n = max(1, (len(seg) - win) // win)
            en = [seg[i * win:(i + 1) * win].mean() for i in range(n)]
            cut = lo + (int(np.argmin(en)) + 0.5) * 0.01
            print(f'  trim {u}_{k:02d}: «{w0}» до {e0:.2f} с, друге «{w1}» з {s1:.2f} с, різ {cut:.2f} с  [{s[:50]}]')
            stats['trim'] += 1
            if apply:
                shutil.copy2(f, os.path.join(SO, f'{u}_{k:02d}.wav'))
                b = a[int(cut * sr):].copy()
                fade = int(0.012 * sr)
                b[:fade] *= np.linspace(0, 1, fade)
                sf.write(f, b, sr, subtype='PCM_16')
    print(stats)

if __name__ == '__main__':
    main()
