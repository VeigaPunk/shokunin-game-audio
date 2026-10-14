import importlib.util, json, sys
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[4] / 'corpus/fixtures/measure_audio.py'
s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for name in ('candidate_pcm8.wav','control_pcm16.wav'):
 r=m.measure('ui',m.SPECS['ui'],Path(__file__).parent/name)
 print(json.dumps(r,sort_keys=True))
