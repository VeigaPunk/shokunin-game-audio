import numpy as n
from pathlib import Path
import hashlib
p=Path('.shokunin/audio/corpus/live/round-58/alt')
a=n.fromfile(p/'valid14.f32',dtype='<f4'); b=n.fromfile(p/'valid16.f32',dtype='<f4')
for name,x in [('14',a),('16',b)]: print(name,'count',len(x),'sha256',hashlib.sha256((p/f'valid{name}.f32').read_bytes()).hexdigest(),'range',float(x.min()),float(x.max()))
print('equal',n.array_equal(a,b),'max_abs_diff',float(n.max(n.abs(a-b))),'different',int(n.count_nonzero(a!=b)))