# Round 7 old-source exception probe

Dependency satisfied before probing: `corpus/live/round-7/odd_sections.wav` and `r7-odd.md` existed. The scratch is 101-frame mono PCM16/48 kHz; SHA-256 `81c7ba97bfc8f68a9ad48403a6b102bf4d5f573963f5d8f74a9697bd09aa72d8`.

## Before-state execution

Extracted `section_contrast` by AST from `3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py`, then executed only that function with NumPy and a `command` helper in an ephemeral Python namespace. No shared source or temporary source file was modified.

First attempted command (exit 1; harness setup error, before function could run):

```sh
python3 -c 'import ast, subprocess, pathlib; source=subprocess.check_output(["git","show","3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py"], text=True); tree=ast.parse(source); node=next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=="section_contrast"); ns={"command": lambda *args: subprocess.run(args, check=True, capture_output=True)}; exec(compile(ast.Module(body=[node], type_ignores=[]), "3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py", "exec"), ns); print(ns["section_contrast"](".shokunin/audio/corpus/live/round-7/odd_sections.wav"))'
```

Exact traceback: `NameError: name 'np' is not defined` at the function's use of NumPy. Corrected the isolated namespace to supply imported NumPy and reran:

```sh
python3 -c 'import ast, subprocess, numpy as np; source=subprocess.check_output(["git","show","3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py"], text=True); tree=ast.parse(source); node=next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=="section_contrast"); ns={"np": np, "command": lambda *args: subprocess.run(args, check=True, capture_output=True)}; exec(compile(ast.Module(body=[node], type_ignores=[]), "3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py", "exec"), ns); print(ns["section_contrast"](".shokunin/audio/corpus/live/round-7/odd_sections.wav"))'
```

Corrected probe exited **1**, as expected for the uncaught old-source exception. Exact exception: `ValueError: array split does not result in an equal division`, from NumPy `split` in `section_contrast` (`measure_audio.py`, old-source line 85). This directly confirms that the odd 101-frame scratch reaches and raises at the old `np.split(samples, 2)` call. This is source-behavior evidence only; it makes no audio/perceptual/security claim and does not establish the current-mode receipt result.
