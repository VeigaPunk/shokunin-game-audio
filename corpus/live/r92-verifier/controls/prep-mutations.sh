#!/usr/bin/env bash
# r92 verifier — mutation/negative-control tree prep (run AFTER the reference
# run so the family lock inode is not shared).  Hardlink copies: instant,
# space-free; the fixture is replaced by rename so no shared inode is written.
set -eu
ROOT=/home/vgpnk/r92-verifier
for d in tree-mutarm tree-mutir tree-mutnoop; do
  rm -rf "$ROOT/$d"
  cp -al "$ROOT/tree-r92" "$ROOT/$d"
  rm -f "$ROOT/$d/corpus/live/measure_audio-filterchain-r92.lock"
done
python3 - <<'EOF'
import os
ROOT = '/home/vgpnk/r92-verifier'
def patch(tree, old, new, count=1):
    p = f'{ROOT}/{tree}/corpus/fixtures/measure_audio.py'
    src = open(p).read()
    assert src.count(old) == count, (tree, old, src.count(old))
    tmp = p + '.tmp'
    open(tmp, 'w').write(src.replace(old, new))
    os.replace(tmp, p)                      # rename: breaks the hardlink
    print(f'{tree}: replaced {count} occurrence(s) of {old[:60]!r}')
# M1 armed-constant mutation: the d_gneg140 clamp witness centre
patch('tree-mutarm', 'abs(g140["200"] - (-46.362)) > 1.5',
      'abs(g140["200"] - (-40.000)) > 1.5')
# M2 fixture/stimulus mutation: the 2-tap IR's second tap moves 64 -> 70
patch('tree-mutir', '[(0, 1.0), (64, 0.5)]', '[(0, 1.0), (70, 0.5)]')
# M3 no-op control: a comment-only insertion inside the r92 block
patch('tree-mutnoop',
      'FILTERCHAIN_R92_PID = os.getpid()',
      '# r92 verifier no-op control: comment-only edit, zero behaviour\n'
      'FILTERCHAIN_R92_PID = os.getpid()')
EOF
mkdir -p "$ROOT/pathfarm-nopwpx"
python3 - <<'EOF'
import os, glob
farm = '/home/vgpnk/r92-verifier/pathfarm-nopwpx'
n = 0
for src in glob.glob('/usr/bin/*') + glob.glob('/bin/*'):
    dst = os.path.join(farm, os.path.basename(src))
    if os.path.islink(src):
        src = os.path.realpath(src)
    if not os.path.isfile(src) or os.path.basename(src) == 'wpexec':
        continue
    if not os.path.exists(dst):
        os.symlink(src, dst)
        n += 1
print('pathfarm entries:', n, 'wpexec present:',
      os.path.exists(os.path.join(farm, 'wpexec')))
EOF
for d in tree-mutarm tree-mutir tree-mutnoop; do
  python3 -m py_compile "$ROOT/$d/corpus/fixtures/measure_audio.py" && echo "$d py_compile ok"
done
