import os, time, torch, soundfile as sf
os.environ.setdefault('HF_HOME', 'D:/Programs/Utility/xtts/hf_cache')
torch.set_num_threads(8)
from omnivoice import OmniVoice
m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
t=time.time()
prompt = m.create_voice_clone_prompt(ref_audio="tts/ref_05.wav")
print('prompt', round(time.time()-t,1), flush=True)
prompt.save("tts/voice_prompt_05.pt") if hasattr(prompt,'save') else None
text = "Оскільки питомий заряд електрона величезний, а іони важкі й повільні, це поле за дуже короткий час змістить електрони."
for ns in (12, 32):
    t=time.time()
    out = m.generate(text=text, voice_clone_prompt=prompt, language="uk", num_step=ns)
    dt=time.time()-t; d=len(out[0])/24000
    print('steps', ns, 'gen', round(dt,1), 'dur', round(d,1), 'RTF', round(dt/d,1), flush=True)
    sf.write(f"tts/ov_steps{ns}.wav", out[0], 24000)
