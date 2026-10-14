import importlib.util, json
from pathlib import Path
spec=importlib.util.spec_from_file_location("measure_audio", Path(".shokunin/audio/corpus/fixtures/measure_audio.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base=Path(".shokunin/audio/corpus/live/round-21/alt")
for tag in ("alt_pass","alt_fail"):
    path=(base/f"{tag}.wav").resolve()
    generic=m.measure(tag,(4.0,100,2000,True),path)
    section=m.section_contrast(path,200)
    failures=list(generic["failures"])
    if section["internal_join_adjacent_delta_full_scale"]>.03: failures.append("gap")
    if section["internal_join_side_slope_mismatch_full_scale_per_sample"]>.001: failures.append("slope")
    print(json.dumps({"tag":tag,"generic_failures":generic["failures"],"section":section,"hypothetical_gated_failures":failures},sort_keys=True))
