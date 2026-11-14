cd /d/Projects/LaTeX/plasma-physics/Presentations2/Basics
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13; do
  whisper-cli -m /d/Programs/Utility/whisper/models/ggml-large-v3-turbo-q5_0.bin -l uk -ml 1 -sow -ojf -of video/work/tr/$i -f audio/$i.wav > video/work/tr/$i.log 2>&1
done
echo done > video/work/tr/ALLDONE
