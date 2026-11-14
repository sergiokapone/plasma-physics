# -*- coding: utf-8 -*-
"""Озвучення слайдів клонованим голосом (OmniVoice k2-fsa, мова uk, CPU).
Запуск: D:/Programs/Utility/xtts/venv_ov/Scripts/python.exe -X utf8 tts_synth.py 11 12 13
Результат: work/tts/NN.wav (24 кГц) і work/tts/NN.json (речення, час, word_times — час кожного слова
сценарію, 1:1 з norm_words). Зразок голосу: work/tts/ref_*.wav (вирізки з audio/, див. make_refs).
"""
import os, sys, re, json, wave, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('HF_HOME', 'D:/Programs/Utility/xtts/hf_cache')  # кеш моделей на D (портабельність)
from scriptparse import slide_texts, norm_words

WORK = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(WORK))
OUT = os.path.join(WORK, 'tts')
GAP = 0.40     # пауза між реченнями, с
LEAD = 0.50    # тиша на початку слайда, с

def make_refs():
    """3 вирізки по 14 с із різних слайдів: нормалізовані, моно, 24 кГц."""
    refs = []
    for name, ss in (('05', 4), ('09', 6), ('12', 8)):
        dst = os.path.join(OUT, f'ref_{name}.wav')
        if not os.path.exists(dst):
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ss), '-t', '14', '-i', os.path.join(BASE, 'audio', f'{name}.wav'),
                            '-af', 'loudnorm=I=-18:TP=-2', '-ar', '24000', '-ac', '1', dst], check=True)
        refs.append(dst)
    return refs

def split_sentences(text):
    sents = re.split(r'(?<=[.!?…])\s+', text.strip())
    out = []
    for s in sents:
        while len(s) > 230:  # XTTS краще на коротких фрагментах
            cut = max(s.rfind(', ', 0, 230), s.rfind('; ', 0, 230), s.rfind(': ', 0, 230), s.rfind(' — ', 0, 230))
            if cut < 80:
                cut = s.rfind(' ', 0, 230)
            out.append(s[:cut + 1].strip())
            s = s[cut + 1:].strip()
        if s:
            out.append(s)
    return out

def clean(s):
    return s.replace('*', '').replace('«', '').replace('»', '').replace('—', ' - ')

def main(slides):
    os.makedirs(OUT, exist_ok=True)
    refs = make_refs()
    import torch, soundfile as sf
    from omnivoice import OmniVoice
    model = OmniVoice.from_pretrained('k2-fsa/OmniVoice', device_map='cpu', dtype=torch.float32)
    texts = slide_texts()
    for sl in slides:
        sents = split_sentences(texts[sl])
        frames, t, sent_info, word_times = [], LEAD, [], []
        params = None
        pieces = [(b'', LEAD)]
        wavs = []
        for k, s in enumerate(sents):
            f = os.path.join(OUT, f'{sl:02d}_{k:02d}.wav')
            if not os.path.exists(f):
                out = model.generate(text=clean(s), ref_audio=refs[0], language='uk')
                sf.write(f, out[0], 24000, subtype='PCM_16')
                print('slide', sl, 'sentence', k + 1, '/', len(sents), flush=True)
            wavs.append(f)
        out_path = os.path.join(OUT, f'{sl:02d}.wav')
        with wave.open(out_path, 'wb') as out:
            for k, (s, f) in enumerate(zip(sents, wavs)):
                with wave.open(f) as w:
                    if k == 0:
                        out.setnchannels(w.getnchannels()); out.setsampwidth(w.getsampwidth()); out.setframerate(w.getframerate())
                        rate, width = w.getframerate(), w.getsampwidth()
                        out.writeframes(b'\x00' * int(LEAD * rate) * width)
                    data = w.readframes(w.getnframes())
                    d = w.getnframes() / w.getframerate()
                out.writeframes(data)
                out.writeframes(b'\x00' * int(GAP * rate) * width)
                words = norm_words(s)
                lens = [len(x) + 1 for x in words]
                tot = float(sum(lens))
                acc = 0
                for x, ln in zip(words, lens):
                    word_times.append(round(t + d * acc / tot, 3))
                    acc += ln
                sent_info.append({'text': s, 'start': round(t, 3), 'dur': round(d, 3)})
                t += d + GAP
        json.dump({'sentences': sent_info, 'word_times': word_times, 'total': round(t, 3)},
                  open(os.path.join(OUT, f'{sl:02d}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('slide', sl, 'done', round(t, 1), 's', flush=True)

if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]])
