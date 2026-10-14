#!/usr/bin/env python3
"""Per-flag wiring census of measure_audio.py: each probe flag must appear as
add_argument (kebab), args.<attr> in: sum() mutex list, build_artifacts
forwarding chain, a measurement-block guard, the mode chain, the suffix chain.
Last-in-chain members are ternary fallthroughs -> one fewer args.* use."""
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
flags = re.findall(r'add_argument\("--([a-z0-9-]+)"', src)
attrs = [f.replace('-', '_') for f in flags]
lines = src.splitlines()
# locate the sum() list span and the mode/suffix chains
sum_start = next(i for i, l in enumerate(lines) if 'sum([' in l)
sum_end = next(i for i in range(sum_start, len(lines)) if 'parser.error' in lines[i])
sum_block = '\n'.join(lines[sum_start:sum_end])
fwd_start = next(i for i, l in enumerate(lines) if 'command(sys.executable' in l and 'with_name' in l)
fwd_end = next(i for i in range(fwd_start, len(lines)) if lines[i].strip().endswith(')')) 
# forward chain ends at line ~ with -hcom-132 close paren before measurements
fwd_block = '\n'.join(lines[fwd_start:fwd_start+120])
mode_line = next(l for l in lines if l.strip().startswith('mode = '))
sfx_line = next(l for l in lines if l.strip().startswith('suffix = '))
bad = []
for f, a in zip(flags, attrs):
    uses = len(re.findall(rf'args\.{a}\b', src))
    in_sum = f'args.{a}' in sum_block
    in_fwd = f'args.{a}' in fwd_block
    in_mode = a in mode_line
    in_sfx = a in sfx_line
    # measurement guard: an `if` bearing the attr outside sum/fwd/mode/suffix
    guard = len(re.findall(rf'args\.{a}\b', src)) 
    status = []
    if uses < 4: status.append(f'uses={uses}')
    for tag, ok in (('sum', in_sum), ('fwd', in_fwd), ('mode', in_mode), ('suffix', in_sfx)):
        if not ok: status.append(f'missing:{tag}')
    if status: bad.append((f, status))
print(f'{len(flags)} flags; sum-block lines {sum_start+1}-{sum_end}; '
      f'{len(bad)} anomalies')
for f, s in bad: print(' ', f, s)
