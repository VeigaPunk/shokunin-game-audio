# r23-guard — baseline hashes, variant records, and source/threshold inventory

## Scope and result

This is a guard/inventory check only. I did not edit shared source, thresholds, fixtures, or other reports; create scratch files; or commit/push. I made no listening, engine, rights, or publishing assessment. Declared before commit is `64e6088794371769e31e0a6fc9ae0f2f2e0c91dd`; round-22 receipt provenance is the named non-author `r22-verifier` report and its restored-normal receipt. Current HEAD is that declared baseline. Working-tree status at inspection showed only the parent’s modified `.shokunin/audio/LOG.md` and this round’s untracked report directory; I do not claim those changes.

## 13 canonical WAV SHA-256 values

I computed Git-blob hashes from declared before commit `64e6088794371769e31e0a6fc9ae0f2f2e0c91dd` and compared each with the working artifact. All 13 current files matched (command exit 0); values agree with `r22-verifier.md`’s comparison to round-22 source-before `14cf986`.

| Canonical WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

## Five variant records in round-22 non-author normal receipt

Source: `.shokunin/audio/corpus/live/runs/20261013T010825350561Z-normal/measurements.json`, the restored normal receipt cited in `reports/round-22/r22-verifier.md`. It records 13 measurements and exactly these five passing `_alt` distinctness records. This is receipt verification, not an independent rerun in this lane.

| Variant | Comparator | Measured value | Pass |
|---|---|---:|---|
| `ui_alt` | `ui` | duration delta `0.04000000000000001 s` | yes |
| `impact_alt` | `impact` | centroid relative delta `0.9563048992406177` | yes |
| `movement_alt` | `movement` | duration delta `0.12 s` | yes |
| `ambience_alt` | `ambience` | centroid relative delta `0.5845136323520758` | yes |
| `stem_layer_alt` | `stem_layer` | centroid relative delta `0.46179931396667484` | yes |

The existing rule is duration delta >=0.020 s **or** relative centroid delta >=0.1; records do not imply perceptual difference.

## Source and threshold baseline

HEAD equals declared clean before `64e6088`. `git diff --quiet 64e6088 -- measure_audio.py build_artifacts.py artifacts` returned 0: current runner, builder and canonical artifacts have no working-tree changes from this baseline. Round-22 verifier documents its source change from `14cf986`: `format_failures(stream)` checks 48,000 Hz mono and `codec_name == pcm_s16le` plus `bits_per_sample == 16`; it is applied by measurement and format controls. This is an encoded PCM16 fixture gate, not general codec or valid-bit validation.

The before-source decision constants, also present unchanged in the cited round-22 normal receipt’s `thresholds`, are: rate 48,000 Hz; duration tolerance 0.001 s; peak must be <0.95; RMS must be >=0.001 in executed code (`rms < .001` fails; legacy receipt label says `rms_min_exclusive`); centroid bands per named fixture; loop endpoint <=0.03 and side-slope <=0.001 FS/sample; section component contrast >=6 dB, component amplitude >=0.01 FS and section RMS >=0.001 FS; internal join adjacent delta <=0.03 and side-slope mismatch <=0.001 FS/sample; distinctness duration >=0.020 s or relative centroid >=0.1. The section contrast uses 20log10 of component-amplitude ratio. These are existing local fixture predicates, not calibrated perceptual standards. LUFS has no acceptance window; the runner treats ebur128 gated-floor readings <=-70 LUFS as null, not as an actual level target.

## Shell commands and exits

1. `git rev-parse HEAD && git status --short && git diff -- .shokunin/audio/corpus/fixtures/measure_audio.py && git diff 64e6088794371769e31e0a6fc9ae0f2f2e0c91dd -- .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**. HEAD was `64e6088`; source diff was empty.
2. `git show --stat --oneline 64e6088794371769e31e0a6fc9ae0f2f2e0c91dd && git diff --quiet 14cf9861ca19041ddb25c322facc5ace9271a146 64e6088794371769e31e0a6fc9ae0f2f2e0c91dd -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures/measure_audio.py; echo diff_exit:$? && git show 64e6088794371769e31e0a6fc9ae0f2f2e0c91dd:.shokunin/audio/corpus/fixtures/measure_audio.py | grep -nE 'THRESH|threshold|0\.03|0\.001|0\.95|0\.01|6\.0|48000|pcm_s16le|bits_per_sample'` — shell exit **0**; the inner before-commit diff returned **1** (expected: round 22 changed source from `14cf986`). The source listing confirmed the format predicate and threshold code.
3. `git status --short; git rev-parse HEAD; git diff --quiet 64e6088794371769e31e0a6fc9ae0f2f2e0c91dd -- .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/artifacts; rc=$?; echo 'head_source_artifact_diff_exit:'$rc; git diff --quiet 14cf9861ca19041ddb25c322facc5ace9271a146 64e6088794371769e31e0a6fc9ae0f2f2e0c91dd -- .shokunin/audio/corpus/fixtures/measure_audio.py .shokhun/audio/corpus/fixtures/build_artifacts.py; rc=$?; echo 'round22_before_source_diff_exit:'$rc` — shell exit **0**; HEAD-to-working-source/artifacts diff **0**; second comparison used a mistyped `.shokhun` path and returned **1**, so that comparison is invalid and is not relied on. The correctly scoped round-22 source change is established by the verifier report/source inspection above.
4. `python3 -c 'import hashlib,subprocess; rev="14cf9861ca19041ddb25c322facc5ace9271a146"; paths=subprocess.check_output(["git","ls-tree","-r","--name-only",rev,"--",".shokunin/audio/corpus/artifacts"],text=True).splitlines(); bad=[]; print("baseline_blob_sha256:"); [(lambda p,b: (print(hashlib.sha256(b).hexdigest(),p), bad.append(p) if hashlib.sha256(b).hexdigest()!=hashlib.sha256(open(p,"rb").read()).hexdigest() else None))(p,subprocess.check_output(["git","show",rev+":"+p])) for p in paths]; print("count",len(paths),"current_file_mismatches",bad); raise SystemExit(bool(bad) or len(paths)!=13)'` — exit **0**, 13 files, no hash mismatches. This directly hashes the round-22 before blobs; those values match the declaration baseline.

No measurement runner, audio decoder, or playback command was invoked by this guard lane. The 13-file and five-record checks are bounded to the specified before state and cited raw non-author receipt; no new replay pass is claimed.
