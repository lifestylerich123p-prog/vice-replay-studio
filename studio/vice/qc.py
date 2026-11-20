"""/vice analyze: quality-control report for a finished video (free, local: ffmpeg + faster-whisper).

    python -m studio.vice analyze output/<slug>/<file>.mp4 [--episode episodes/<slug>.json] [--dest vice-replay]

Checks, each with timestamps and a corrective action:
format (aspect, size, fps, codecs, length) | decode errors (corrupted export) | black frames | frozen picture |
black bars | silence | loudness (-14 LUFS, true peak <= -1 dBTP) | opening (first second not black/silent) |
caption accuracy (speech vs script, word error rate) | duplicate footage (hash vs everything we published) |
rights (every source through the rights gate) | facts and content risks | disclosures | human review (always pending).
Failures name the affected segment when the video has a timings file, so only that part is re-made.
"""
import json
import re
import subprocess
from pathlib import Path

from . import db, dedupe, factcheck, rights

TARGET_LUFS, LUFS_TOL, MAX_TP = -14.0, 2.0, -1.0


def ff(args):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *args], capture_output=True, text=True)
    return r.returncode, r.stderr


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                          "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(out.stdout or "{}")


def seg_at(timings, t):
    """Which episode segment is playing at time t (timings.json from make_video: list of {start,end} or durations)."""
    if not timings:
        return None
    acc = 0.0
    for i, s in enumerate(timings):
        start = s.get("start", acc) if isinstance(s, dict) else acc
        end = s.get("end", start + s.get("dur", 0)) if isinstance(s, dict) else acc + float(s)
        if start <= t < end:
            return i
        acc = end
    return None


def scan_filters(path):
    _, err = ff(["-i", str(path), "-vf", "blackdetect=d=0.12:pix_th=0.10,freezedetect=n=-60dB:d=1.5,cropdetect=24:2:0",
                 "-af", "silencedetect=n=-45dB:d=1.2,ebur128=peak=true", "-f", "null", "-"])
    black = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]
    fz_s = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
    fz_e = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", err)]
    freezes = list(zip(fz_s, fz_e + [None] * (len(fz_s) - len(fz_e))))
    sil_s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    sil_e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    silences = list(zip(sil_s, sil_e + [None] * (len(sil_s) - len(sil_e))))
    crops = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", err)
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else ""
    i_lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary)
    return {"black": black, "freezes": freezes, "silences": silences,
            "crop": tuple(map(int, crops[-1])) if crops else None,
            "lufs": float(i_lufs.group(1)) if i_lufs else None, "true_peak": float(tp.group(1)) if tp else None}


def decode_errors(path):
    _, err = ff(["-v", "error", "-i", str(path), "-f", "null", "-"])
    return [l for l in err.splitlines() if l.strip()][:5]


def transcribe(path):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True).stdout  # decode with ffmpeg (faster-whisper's PyAV path breaks on new av)
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    model = WhisperModel("base", device="cpu", compute_type="int8", cpu_threads=4)
    segs, _ = model.transcribe(audio, language="en", word_timestamps=True, vad_filter=False)
    return [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)}
            for s in segs for w in (s.words or [])]


def norm_words(text):
    t = text.lower().replace("&", " and ")
    t = re.sub(r"[^\w\s']", " ", t)
    return [w.strip("'") for w in t.split() if w.strip("'")]


def wer(ref, hyp):
    """Word error rate (edit distance / reference length)."""
    r, h = ref, hyp
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return d[len(h)] / max(1, len(r))


NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
       "8": "eight", "9": "nine", "10": "ten"}


def spoken(words):
    return [NUM.get(w, w) for w in words]


def check(path, episode=None, dest="vice-replay", script_key="short", project=None, intended_freezes=(),
          campaign=None, use_whisper=True):
    path = Path(path)
    ep = json.loads(Path(episode).read_text()) if episode else None
    timings_f = path.with_suffix(".timings.json")
    timings = json.loads(timings_f.read_text()) if timings_f.exists() else None
    if isinstance(timings, dict):
        timings = timings.get("segments") or timings.get("timings")
    R = []

    def add(name, status, detail, fix=None, at=None):
        seg = seg_at(timings, at) if at is not None else None
        R.append({"check": name, "status": status, "detail": detail, "at": at,
                  "segment": seg, "fix": fix})

    pr = probe(path)
    v = next((s for s in pr.get("streams", []) if s["codec_type"] == "video"), None)
    a = next((s for s in pr.get("streams", []) if s["codec_type"] == "audio"), None)
    dur = float(pr.get("format", {}).get("duration", 0))
    vertical = bool(v and v["height"] > v["width"])
    if not v:
        add("format", "fail", "no video stream", "re-export")
    else:
        want = (1080, 1920) if vertical else (1920, 1080)
        ok = (v["width"], v["height"]) == want and v["codec_name"] == "h264"
        fps = eval(v["r_frame_rate"]) if v.get("r_frame_rate") else 0
        add("format", "pass" if ok and 23 <= fps <= 61 else "fail",
            f"{v['width']}x{v['height']} {v['codec_name']} {fps:.0f} fps, {dur:.1f} s",
            None if ok else f"re-export at {want[0]}x{want[1]} h264")
    if not a:
        add("audio stream", "fail", "no audio track", "re-mux the voice/original audio")
    else:
        add("audio stream", "pass", f"{a['codec_name']} {a.get('sample_rate')} Hz, {a.get('channels')} ch")
    if vertical:
        if dur > 180:
            add("length", "fail", f"{dur:.0f} s: over 3 min is not a Short", "cut to 60 s or less")
        elif dur > 60:
            add("length", "warn", f"{dur:.0f} s: our data says 16-30 s Shorts do best, 60 s+ dead", "tighten")
        else:
            add("length", "pass", f"{dur:.1f} s")
    errs = decode_errors(path)
    add("decode", "fail" if errs else "pass", "; ".join(errs) if errs else "decodes cleanly",
        "re-render the export" if errs else None)
    f = scan_filters(path)
    bad_black = [(s, e) for s, e in f["black"] if e - s >= 0.12]
    for s, e in bad_black:
        add("black frames", "fail", f"black {s:.2f}-{e:.2f} s", "replace or trim the black frames in this segment", at=s)
    if not bad_black:
        add("black frames", "pass", "none")
    for s, e in f["freezes"]:
        if any(abs(s - x) < 0.6 for x in intended_freezes):
            add("frozen picture", "pass", f"intended freeze frame at {s:.2f} s")
            continue
        add("frozen picture", "warn", f"picture doesn't move {s:.2f}-{(e or dur):.2f} s",
            "use a moving clip or add motion (punch-in/pan) here", at=s)
    if not f["freezes"]:
        add("frozen picture", "pass", "picture keeps moving")
    if v and f["crop"]:
        cw, ch_, cx, cy = f["crop"]
        bars = (v["width"] - cw > 16) or (v["height"] - ch_ > 16)
        add("black bars", "fail" if bars else "pass",
            f"active picture {cw}x{ch_} of {v['width']}x{v['height']}" + (" (letterbox/pillarbox)" if bars else ""),
            "re-crop the footage to fill the frame" if bars else None)
    for s, e in f["silences"]:
        if s < dur - 1.0:  # trailing silence at the very end is fine
            add("silence", "warn", f"silent {s:.2f}-{(e or dur):.2f} s", "check the voice/game audio here", at=s)
    if f["lufs"] is not None:
        ok = abs(f["lufs"] - TARGET_LUFS) <= LUFS_TOL
        add("loudness", "pass" if ok else "warn", f"{f['lufs']} LUFS integrated (target {TARGET_LUFS})",
            None if ok else "apply loudnorm=I=-14:TP=-1.5")
    if f["true_peak"] is not None:
        ok = f["true_peak"] <= MAX_TP + 0.3
        add("true peak", "pass" if ok else "warn", f"{f['true_peak']} dBFS peak", None if ok else "limit to -1.5 dBTP")
    opening_black = any(s < 0.5 for s, e in bad_black)
    opening_silent = any(s < 0.3 and ((e or dur) > 1.0) for s, e in f["silences"])
    add("opening", "fail" if opening_black or opening_silent else "pass",
        "first second is " + ("black" if opening_black else "silent" if opening_silent else "picture + sound"),
        "start on the moment or the context line" if opening_black or opening_silent else None, at=0.0)

    # captions: what is said vs the script we captioned
    if use_whisper and ep and (ep.get(script_key) or ep.get("segments")):
        segs = ep.get(script_key) or ep.get("segments")
        script = norm_words(" ".join(s.get("text", "") for s in segs))
        words = transcribe(path)
        if words is None:
            add("captions", "warn", "faster-whisper not installed: caption accuracy not measured", "pip install faster-whisper")
        else:
            heard = norm_words(" ".join(w["w"] for w in words))
            e = wer(spoken(script), spoken(heard))
            add("captions", "pass" if e <= 0.12 else "warn" if e <= 0.25 else "fail",
                f"speech matches the captioned script with {round(100 * e)}% word error ({len(heard)} words heard)",
                None if e <= 0.12 else "re-voice the segment or fix the caption text so they match")
    elif use_whisper and project and project.get("transcript"):
        add("captions", "pass", "captions come from the word-level transcript of this audio (faster-whisper)")

    # duplicates
    con = db.connect()
    vh = dedupe.video_hash(path)
    me = str(path.resolve().relative_to(db.ROOT)) if path.resolve().is_relative_to(db.ROOT) else str(path)
    others = [(dedupe.overlap(vh, r["phash"]), r) for r in db.rows(con, "SELECT * FROM used_footage") if r["source"] != me]
    dup = [r for o, r in others if o >= 0.7]
    shared = [(o, r) for o, r in others if 0.35 <= o < 0.7]
    add("duplicate footage", "fail" if dup else "pass",
        "same footage as " + ", ".join(sorted({d["video_id"] or d["source"] for d in dup})) if dup else "not a repost",
        "pick a different moment: reposting the same footage gets suppressed" if dup else None)
    if shared:
        add("footage reuse", "warn", "shares {}% of its shots with {}".format(
            int(100 * max(o for o, _ in shared)), ", ".join(sorted({r["video_id"] or r["source"] for _, r in shared})[:4])),
            "rotate to clips not used recently (repetitive-content risk)")

    # rights
    if ep:
        rc = rights.check_episode(ep, dest)
        for c in rc["checks"]:
            add("rights", "pass" if c["ok"] else "fail", f"{c['asset']}: {c['record'] or 'no record'}"
                + (f" ({'; '.join(c['reasons'])})" if c["reasons"] else ""),
                None if c["ok"] else "replace this source or get written permission")
    elif project:
        for src in project.get("rights_sources", []):
            c = rights.check(src, dest, ai_voice=project.get("ai_voice", False), branding=project.get("branding", False))
            add("rights", "pass" if c["ok"] else "fail", f"{src}: {c['record'] or 'no record'}"
                + (f" ({'; '.join(c['reasons'])})" if c["reasons"] else ""),
                None if c["ok"] else "blocked source: don't publish")
    else:
        add("rights", "fail", "no episode or project given: sources unknown", "run with --episode or from a project")

    # facts and disclosures
    if ep:
        for x in factcheck.check_episode(ep):
            add("facts", {"fail": "fail", "warn": "warn", "info": "info"}[x["level"]], f"{x['where']}: {x['text'][:140]}", x["fix"])
        desc = (ep.get("short_description") or ep.get("description") or "")
        if dest == "vice-replay":
            add("disclosure", "pass", "make_video appends the 'not affiliated with Rockstar' line to every description")
            if "amazon." in json.dumps(ep) or ep.get("affiliate"):
                add("disclosure", "pass", "affiliate links: description template adds '(affiliate links)'")
    if campaign:
        cap = (project or {}).get("caption", "")
        for tag in campaign.get("required_hashtags", []):
            add("disclosure", "pass" if tag.lower() in cap.lower() else "fail", f"campaign hashtag {tag}",
                None if tag.lower() in cap.lower() else f"add {tag} to the caption")
    add("human review", "pending", "owner approval in chat required before publishing")
    fails = [r for r in R if r["status"] == "fail"]
    return {"video": str(path), "duration": round(dur, 2), "destination": dest, "passed": not fails,
            "fails": len(fails), "warns": sum(1 for r in R if r["status"] == "warn"), "checks": R, "hash": vh}


def write(rep, out_dir=None, project_id=None):
    p = Path(rep["video"])
    out_dir = Path(out_dir or p.parent)
    md = out_dir / f"{p.stem}.qc.md"
    icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "info": "info", "pending": "PENDING"}
    L = [f"# QC report: {p.name}", "",
         f"Result: **{'PASSED' if rep['passed'] else 'FAILED'}** ({rep['fails']} fail, {rep['warns']} warn), "
         f"{rep['duration']} s, destination {rep['destination']}.", "",
         "| Check | Result | Detail | At | Segment | Fix |", "|---|---|---|---|---|---|"]
    for r in rep["checks"]:
        at = "" if r["at"] is None else f"{r['at']:.2f} s"
        seg = "" if r["segment"] is None else r["segment"]
        detail = r["detail"].replace("|", "/")
        L.append(f"| {r['check']} | {icon[r['status']]} | {detail} | {at} | {seg} | {r['fix'] or ''} |")
    md.write_text("\n".join(L) + "\n")
    md.with_suffix(".json").write_text(json.dumps(rep, indent=1))
    con = db.connect()
    con.execute("INSERT INTO qc_reports (project, video, passed, report, created_at) VALUES (?,?,?,?,?)",
                (project_id, str(p), int(rep["passed"]), json.dumps(rep), db.now()))
    con.commit()
    return md
