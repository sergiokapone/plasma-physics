import time, torch, soundfile as sf
from omnivoice import OmniVoice
t=time.time()
m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
print('load', round(time.time()-t,1), 'threads', torch.get_num_threads(), flush=True)
texts = ["Оскільки питомий заряд електрона величезний, а іони важкі й повільні, це поле за дуже короткий час змістить електрони.",
         "Тому на макроскопічних масштабах густина заряду майже дорівнює нулю."]
for i, text in enumerate(texts):
    t=time.time()
    out = m.generate(text=text, ref_audio="tts/ref_05.wav", language="uk")
    dt=time.time()-t
    d=len(out[0])/24000
    print('sent', i, 'gen', round(dt,1), 'dur', round(d,1), 'RTF', round(dt/d,1), flush=True)
    sf.write(f"tts/ov_speed{i}.wav", out[0], 24000)
