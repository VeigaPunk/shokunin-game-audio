#!/usr/bin/env python3
"""r68 boundary — txw/smp at their own length gates + early-EOF on fifo at
the fallback boundary + `-t` forcing interaction with the no-match path.

txw (tx16w.c): needs seekable; counts to EOF, -=32; reads 32-B header;
  `LM8953` at 0. Gates: <32 B wrap, header truncation, bad magic, rate switch.
smp (smp.c): needs seekable; HEADERSIZE=112 read; magic@0..16; version@17..20;
  NoOfSamps dword@113; seek to trailer at dataStart + NoOfSamps*2.

Early-EOF: fifo writer closes after N bytes — detection sees len=N; for
no-match members the fallback runs on N<257 too. Does truncated input change
post-table verdict?
"""
import os, re, socket, subprocess, sys, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBES = ROOT / "probes"
LOGS = ROOT / "runs" / "logs"
SOX = "/usr/bin/sox"
DET = re.compile(r"detected file format type `([^']+)'")
SMP = re.compile(r"Samples read:\s+(\d+)")


def verdict(argv, stdin=None, pass_fds=(), timeout=15, data=None):
    kw = {"stdin": stdin} if stdin is not None else ({"input": data} if data is not None else {})
    try:
        p = subprocess.run(argv, capture_output=True, pass_fds=pass_fds,
                           timeout=timeout, **kw)
        out = (p.stderr or b"").decode(errors="replace") + (p.stdout or b"").decode(errors="replace")
        code = p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stderr or b"").decode(errors="replace")
        code = "TIMEOUT"
    det = DET.search(out); smp = SMP.search(out)
    msg = ""
    for line in out.splitlines():
        if "sox FAIL" in line or "sox WARN" in line:
            msg = line.strip(); break
    return code, (det.group(1) if det else ""), (smp.group(1) if smp else ""), msg, out


def fifo_eof_leg(path, nbytes, fifo_name=".fifo_eof"):
    """Writer writes nbytes then closes immediately (early EOF on fifo)."""
    fifo = PROBES / fifo_name
    try: os.unlink(fifo)
    except FileNotFoundError: pass
    os.mkfifo(fifo)
    data = open(path, "rb").read()[:nbytes]
    def writer():
        fd = os.open(fifo, os.O_WRONLY)
        os.write(fd, data)
        os.close(fd)
    t = threading.Thread(target=writer, daemon=True); t.start()
    try:
        return verdict([SOX, "-V4", str(fifo), "-n", "stat"])
    finally:
        t.join(); os.unlink(fifo)


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    tsv = open(ROOT / "runs" / "len_eof_forced.tsv", "w")
    tsv.write("probe\tmember_or_arg\texit\tdetected\tsamples\tmsg\n")

    # --- txw/smp length gates on file / redir / pipe / fifo-earlyeof ---
    print("== txw length gates ==")
    for n in (0,5,6,16,21,22,23,24,25,31,32,33):
        fn = PROBES / f"txw_cut{n}.bin"
        c,d,s,m,o = verdict([SOX,"-V4",str(fn),"-n","stat"])
        (LOGS/f"txw_cut{n}.file.log").write_text(o)
        row=("txw_cut%d"%n,"file",c,d,s,m[:100]); tsv.write("\t".join(map(str,row))+"\n"); print("\t".join(map(str,row)))
        c,d,s,m,o = verdict([SOX,"-V4","-","-n","stat"], data=fn.read_bytes())
        row=("txw_cut%d"%n,"pipe",c,d,s,m[:100]); tsv.write("\t".join(map(str,row))+"\n"); print("\t".join(map(str,row)))
    print("== smp length gates ==")
    for n in (0,16,17,18,21,22,111,112,113,116,117):
        fn = PROBES / f"smp_cut{n}.bin"
        c,d,s,m,o = verdict([SOX,"-V4",str(fn),"-n","stat"])
        (LOGS/f"smp_cut{n}.file.log").write_text(o)
        row=("smp_cut%d"%n,"file",c,d,s,m[:100]); tsv.write("\t".join(map(str,row))+"\n"); print("\t".join(map(str,row)))
        c,d,s,m,o = verdict([SOX,"-V4","-","-n","stat"], data=fn.read_bytes())
        row=("smp_cut%d"%n,"pipe",c,d,s,m[:100]); tsv.write("\t".join(map(str,row))+"\n"); print("\t".join(map(str,row)))

    # --- early-EOF on fifo: no-match member AND detected members ---
    print("== fifo early-EOF: nomatch .wav / detected members ==")
    for member in ("nomatch_txt.wav","g_txw_hcom.bin","p_smp_intact.bin",
                   "nomatch_zeros.snd","pair_dec_act.wav"):
        path = PROBES / member
        if not path.exists():
            alt = Path("../../r67-boundary/probes") / member
            if alt.exists(): path = alt
            else: continue
        for n in (0,1,6,16,17,24,32,64,112,113,128,255,256,257,300):
            name = ".fifo_eof" + (".wav" if member.endswith(".wav") or member.endswith(".snd") else "")
            try:
                c,d,s,m,o = fifo_eof_leg(path, n, fifo_name=name)
            except Exception as e:
                c,d,s,m,o = ("EXC","","",str(e),"")
            row=(member,"fifo_eof@%d"%n,c,d,s,m[:100])
            tsv.write("\t".join(map(str,row))+"\n"); print("\t".join(map(str,row)))

    # --- -t forcing x no-match (pipe + file) ---
    print("== -t forcing on no-match members ==")
    for member in ("nomatch_txt.wav","nomatch_txt.bin","g_txw_hcom.bin","p_smp_intact.bin"):
        path = PROBES/member
        if not path.exists(): continue
        data = path.read_bytes()
        for t in ("wav","txw","smp","sox","au","raw"):
            c,d,s,m,o = verdict([SOX,"-V4","-t",t,"-","-n","stat"], data=data)
            row=(member,"-t %s on -"%t,c,d,s,m[:100])
            tsv.write("\t".join(map(str,row))+"\n"); print("\t".join(map(str,row)))
            c,d,s,m,o = verdict([SOX,"-V4","-t",t,str(path),"-n","stat"])
            row=(member,"-t %s on file"%t,c,d,s,m[:100])
            tsv.write("\t".join(map(str,row))+"\n"); print("\t".join(map(str,row)))
    tsv.close()


if __name__ == "__main__":
    main()
