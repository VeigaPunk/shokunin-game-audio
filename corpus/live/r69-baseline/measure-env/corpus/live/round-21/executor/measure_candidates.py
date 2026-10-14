import hashlib, json, subprocess, wave
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[3]
for name in ("join200_pass983","join200_fail984"):
    path=Path(__file__).resolve().parent/(name+".wav")
    dec=subprocess.run(["sox",str(path),"-t","f32","-e","floating-point","-"],capture_output=True,check=True)
    s=np.frombuffer(dec.stdout,dtype="<f4").astype(np.float64)
    with wave.open(str(path),"rb") as w: meta=(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())
    amps=[float(2*abs(np.fft.rfft(h)[400])/len(h)) for h in np.split(s,2)]
    contrast=float(20*np.log10(amps[1]/amps[0]))
    gap=float(abs(s[96000]-s[95999]))
    side=float(abs((s[96001]-s[96000])-(s[95999]-s[95998])))
    endpoint=float(abs(s[0]-s[-1]))
    outer_slope=float(abs((s[-1]-s[-2])-(s[1]-s[0])))
    rms=float(np.sqrt(np.mean(s*s))); peak=float(np.max(np.abs(s)))
    freqs=np.fft.rfftfreq(len(s),1/48000); spec=np.abs(np.fft.rfft(s))
    centroid=float(np.dot(freqs,spec)/spec.sum())
    failures=[]
    if meta[:3]!=(1,2,48000) or meta[3]!=192000: failures.append("format/duration")
    if peak>=.95 or rms<.001: failures.append("level")
    if not 100<=centroid<=2000: failures.append("spectrum")
    if endpoint>.03: failures.append("outer endpoint")
    if outer_slope>.001: failures.append("outer slope")
    if contrast<6: failures.append("section contrast")
    if gap>.03: failures.append("internal gap")
    if side>.001: failures.append("internal side slope")
    print(json.dumps({"name":name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"format_channels_width_rate_frames":meta,"decoded_join_counts":[round(float(s[i]*32768)) for i in range(95998,96002)],"amplitudes_fs":amps,"contrast_db":contrast,"gap_fs":gap,"side_slope_fs_per_sample":side,"outer_endpoint_fs":endpoint,"outer_slope_fs_per_sample":outer_slope,"rms_fs":rms,"peak_fs":peak,"centroid_hz":centroid,"failures":failures},sort_keys=True))
