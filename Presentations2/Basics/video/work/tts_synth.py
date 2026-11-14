# -*- coding: utf-8 -*-
"""Озвучення лекції клонованим голосом автора (OmniVoice k2-fsa, мова uk, GPU).
Запуск (з папки work):
  D:/Programs/Utility/omnivoice/venv/Scripts/python.exe -X utf8 tts_synth.py 01 02 18a      # окремі одиниці
  D:/Programs/Utility/omnivoice/venv/Scripts/python.exe -X utf8 tts_synth.py all            # уся лекція (42 одиниці)
Результат: work/tts/<ід>.wav (24 кГц, моно) і work/tts/<ід>.json (речення, час, word_times — час початку кожного
слова сценарію, 1:1 з norm_words). Проміжні файли речень — work/tts/s/<ід>_kk.wav (кеш: наявні не перераховуються).
Зразок голосу: work/tts/ref_05.wav (14 с із audio/05.wav).
Параметри середовища: OV_STEPS (за замовч. 32), OV_DTYPE (float16|float32).
"""
import os, sys, re, json, wave, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('HF_HOME', 'D:/Programs/Utility/omnivoice/hf_cache')   # кеш моделей поруч із venv (портабельно)
from scriptparse import unit_texts, norm_words

OUT = os.path.join(HERE, 'tts')
SENT = os.path.join(OUT, 's')
REF = os.path.join(OUT, 'ref_05.wav')
GAP = 0.40     # пауза між реченнями, с
LEAD = 0.50    # тиша на початку, с
STEPS = int(os.environ.get('OV_STEPS', '32'))

def split_sentences(text):
    sents = re.split(r'(?<=[.!?…])\s+', text.strip())
    out = []
    for s in sents:
        while len(s) > 230:   # довгі речення краще на коротких фрагментах
            cut = max(s.rfind(', ', 0, 230), s.rfind('; ', 0, 230), s.rfind(': ', 0, 230), s.rfind(' — ', 0, 230))
            if cut < 80:
                cut = s.rfind(' ', 0, 230)
            out.append(s[:cut + 1].strip())
            s = s[cut + 1:].strip()
        if s:
            out.append(s)
    return out

def clean(s):
    s = s.replace('*', '').replace('«', '').replace('»', '').replace('—', ' - ').replace('↔', ' і навпаки ')
    return re.sub(r'\s+', ' ', s).strip()

def main(units):
    import torch, soundfile as sf
    from omnivoice import OmniVoice
    os.makedirs(SENT, exist_ok=True)
    dtype = torch.float16 if os.environ.get('OV_DTYPE', 'float16') == 'float16' else torch.float32
    t0 = time.time()
    model = OmniVoice.from_pretrained('k2-fsa/OmniVoice', device_map='cuda:0', dtype=dtype)
    prompt = model.create_voice_clone_prompt(ref_audio=REF)
    print(f'model+prompt {time.time() - t0:.1f} s, steps={STEPS}, dtype={dtype}', flush=True)
    texts = unit_texts()
    if units == ['all']:
        units = list(texts)
    for u in units:
        tu = time.time()
        sents = split_sentences(texts[u])
        files = []
        for k, s in enumerate(sents):
            f = os.path.join(SENT, f'{u}_{k:02d}.wav')
            if not os.path.exists(f):
                torch.manual_seed(1000 + k)
                out = model.generate(text=clean(s), voice_clone_prompt=prompt, language='uk', num_step=STEPS)
                sf.write(f, out[0], 24000, subtype='PCM_16')
            files.append(f)
        rate = 24000
        t, info, word_times = LEAD, [], []
        with wave.open(os.path.join(OUT, f'{u}.wav'), 'wb') as o:
            o.setnchannels(1); o.setsampwidth(2); o.setframerate(rate)
            o.writeframes(b'\x00' * int(LEAD * rate) * 2)
            for s, f in zip(sents, files):
                with wave.open(f) as w:
                    assert w.getframerate() == rate and w.getnchannels() == 1
                    data = w.readframes(w.getnframes()); d = w.getnframes() / rate
                o.writeframes(data)
                o.writeframes(b'\x00' * int(GAP * rate) * 2)
                words = norm_words(s)
                lens = [len(x) + 1 for x in words]
                tot, acc = float(sum(lens)), 0
                for ln in lens:
                    word_times.append(round(t + d * acc / tot, 3)); acc += ln
                info.append({'text': s, 'start': round(t, 3), 'dur': round(d, 3)})
                t += d + GAP
        json.dump({'sentences': info, 'word_times': word_times, 'total': round(t, 3)},
                  open(os.path.join(OUT, f'{u}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{u}: {len(sents)} реч., {t:.1f} с звуку, обчислення {time.time() - tu:.1f} с', flush=True)

if __name__ == '__main__':
    main(sys.argv[1:] or ['all'])
