import time, torch, soundfile as sf
from omnivoice import OmniVoice
t=time.time()
m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
print('load', time.time()-t, flush=True)
text = "Переходимо до центральної частини лекції — квазінейтральності. Припустимо, що в плазмі виникло розділення зарядів."
t=time.time()
out = m.generate(text=text, ref_audio="tts/ref_05.wav", language="uk")
print('gen', time.time()-t, flush=True)
sf.write("tts/ov_test.wav", out[0], 24000)
print('dur', len(out[0])/24000)
