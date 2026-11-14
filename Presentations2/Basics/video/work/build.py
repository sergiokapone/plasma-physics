# -*- coding: utf-8 -*-
"""Збирає відео лекції: кадри PDF + курсор за підказками + озвучення.
python -X utf8 build.py debug      -> контрольні кадри з позначеними точками
python -X utf8 build.py build N    -> відео для слайдів 1..N
"""
import sys, os, json, math, subprocess, wave
sys.path.insert(0, os.path.dirname(__file__))
import fitz
from PIL import Image, ImageDraw
from cues import CUES
from scriptparse import slide_texts, norm_words, phrase_index

BASE = r'D:\Projects\LaTeX\plasma-physics\Presentations2\Basics'
WORK = os.path.join(BASE, 'video', 'work')
W, H, FPS = 1280, 960, 25
REF_W, REF_H = 503.0, 378.0
SX, SY = W / REF_W, H / REF_H

def render_pages(n):
    d = fitz.open(os.path.join(BASE, 'Basics.pdf'))
    m = fitz.Matrix(W / d[0].rect.width, H / d[0].rect.height)
    out = {}
    for i in range(n):
        pix = d[i].get_pixmap(matrix=m, alpha=False)
        out[i + 1] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).resize((W, H))
    return out

def cue_times(slide):
    """список (час, [точки]) для слайда."""
    T = slide_texts()[slide]
    sw = norm_words(T)
    tr = json.load(open(os.path.join(WORK, 'tr', f'{slide:02d}.json'), encoding='utf-8'))['transcription']
    ww = [seg['offsets']['from'] / 1000.0 for seg in tr if any(c.isalnum() for c in seg['text'])]
    res, last = [], 0
    for ph, pts in CUES[slide]:
        i = phrase_index(sw, ph, last)
        assert i is not None, (slide, ph)
        last = i
        j = min(len(ww) - 1, int(round(i * len(ww) / len(sw))))
        res.append((ww[j], [(x * SX, y * SY) for x, y in pts]))
    return res

def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)

def keyframes(slide, start_pos, dur):
    """[(t, x, y, trace)] trace=True -> повільний рух уздовж лінії всередині підказки."""
    cues = cue_times(slide)
    kf = [(0.0, start_pos[0], start_pos[1], False)]
    for ci, (t, pts) in enumerate(cues):
        nxt = cues[ci + 1][0] if ci + 1 < len(cues) else t + 6.0
        a = max(t - 0.15, kf[-1][0] + 0.35)
        end = max(a + 0.5, min(nxt - 0.35, dur - 0.3))
        k = len(pts)
        step = min(1.8, (end - a) / max(1, k - 1)) if k > 1 else 0
        for j, (x, y) in enumerate(pts):
            kf.append((a + j * step, x, y, j > 0))
    return kf

def pos_at(kf, t):
    if t <= kf[0][0]:
        return kf[0][1], kf[0][2]
    for i in range(1, len(kf)):
        t0, x0, y0, _ = kf[i - 1]
        t1, x1, y1, trace = kf[i]
        if t <= t1:
            d = (t1 - t0) if trace else min(0.7, t1 - t0)
            u = (t - (t1 - d)) / d if d > 0 else 1
            s = u if trace else smooth(u)
            if trace:
                s = smooth(u) * 0.35 + u * 0.65
            return x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
    return kf[-1][1], kf[-1][2]

def make_cursor():
    S = 4
    sz = 64
    im = Image.new('RGBA', (sz * S, sz * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = 24 * S
    d.ellipse([cx - 20 * S, cy - 20 * S, cx + 20 * S, cy + 20 * S], fill=(255, 190, 0, 70), outline=(255, 150, 0, 170), width=2 * S)
    pts = [(0, 0), (0, 17), (4.5, 13), (7.5, 20), (10, 19), (7, 12), (13, 12)]
    poly = [(cx + x * S, cy + y * S) for x, y in pts]
    d.polygon(poly, fill=(20, 20, 20, 255), outline=(255, 255, 255, 255))
    d.line(poly + [poly[0]], fill=(255, 255, 255, 255), width=S)
    return im.resize((sz, sz), Image.LANCZOS), (24, 24)

def prep_audio(n):
    os.makedirs(os.path.join(WORK, 'aud'), exist_ok=True)
    durs = {}
    for i in range(1, n + 1):
        src = os.path.join(BASE, 'audio', f'{i:02d}.wav')
        dst = os.path.join(WORK, 'aud', f'{i:02d}.wav')
        if not os.path.exists(dst):
            af = ('areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.3,areverse,'
                  'loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=0.9')
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-af', af, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', dst], check=True)
        with wave.open(dst) as w:
            durs[i] = w.getnframes() / w.getframerate()
    return durs

def concat_audio(n, path):
    with wave.open(path, 'wb') as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(48000)
        for i in range(1, n + 1):
            with wave.open(os.path.join(WORK, 'aud', f'{i:02d}.wav')) as w:
                out.writeframes(w.readframes(w.getnframes()))

def debug(n):
    pages = render_pages(n)
    os.makedirs(os.path.join(WORK, 'dbg'), exist_ok=True)
    for s in range(1, n + 1):
        im = pages[s].copy()
        d = ImageDraw.Draw(im)
        k = 0
        for ph, pts in CUES[s]:
            for j, (x, y) in enumerate(pts):
                x *= SX; y *= SY; k += 1
                d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(255, 0, 0), width=3)
                d.text((x + 11, y - 8), str(k), fill=(255, 0, 0))
        im.save(os.path.join(WORK, 'dbg', f'{s:02d}.png'))
    # сітки
    for g, rng in enumerate([range(1, 8), range(8, n + 1)]):
        cols, rows = 2, 4
        sheet = Image.new('RGB', (cols * 640, rows * 480), 'white')
        for idx, s in enumerate(rng):
            t = Image.open(os.path.join(WORK, 'dbg', f'{s:02d}.png')).resize((640, 480))
            sheet.paste(t, ((idx % cols) * 640, (idx // cols) * 480))
        sheet.save(os.path.join(WORK, 'dbg', f'sheet{g + 1}.png'))

def build(n, out):
    pages = render_pages(n)
    durs = prep_audio(n)
    audio = os.path.join(WORK, 'all.wav')
    concat_audio(n, audio)
    cur, (hx, hy) = make_cursor()
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-i', audio, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '160k', '-shortest', out], stdin=subprocess.PIPE)
    pos = (W * 0.55, H * 0.95)
    for s in range(1, n + 1):
        dur = durs[s]
        kf = keyframes(s, pos, dur)
        nf = int(round(dur * FPS))
        base = pages[s]
        for f in range(nf):
            x, y = pos_at(kf, f / FPS)
            fr = base.copy()
            fr.paste(cur, (int(x - hx), int(y - hy)), cur)
            ff.stdin.write(fr.tobytes())
        pos = pos_at(kf, dur)
        print('slide', s, round(dur, 1), 's', flush=True)
    ff.stdin.close()
    ff.wait()

if __name__ == '__main__':
    mode = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 13
    if mode == 'debug':
        debug(n)
    else:
        build(n, os.path.join(BASE, 'video', f'Basics_1-{n}.mp4'))
