"""/vice clip: rights-checked clip project from an authorized source (campaign stream footage or owner gameplay).

    python -m studio.vice clip SOURCE --start 12.0 --end 30.5 --campaign lacy-gta6 --headline "..." \
        [--punch 8.2] [--replay 7.5 10.0] [--dest clipcircuit]

Resumable steps (database `projects`): rights -> cut -> transcribe -> render -> cover -> qc -> draft.
Editing rules built in: the real timeline is kept (no reordering, no added sounds or fake reactions), the original
audio is kept and loudness-normalized, captions come from a word-level transcript of that audio, a replay is
always labelled REPLAY, and campaign clips get no Vice Replay branding (campaign rules forbid logos).
"""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from . import channels, db, qc, rights
from .. import brand

W, H, FPS = 1080, 1920, 30


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(map(str, cmd))[:300] + "\n" + r.stderr[-1500:])
    return r


def probe(src):
    out = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type",
                          "-of", "json", src]).stdout)
    v = next(s for s in out["streams"] if s["codec_type"] == "video")
    return float(out["format"]["duration"]), v["width"], v["height"]


def srt_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def write_srt(words, path, group=3):
    lines, n = [], 1
    for i in range(0, len(words), group):
        g = words[i:i + group]
        lines += [str(n), f"{srt_time(g[0]['s'])} --> {srt_time(g[-1]['e'])}", " ".join(w["w"] for w in g), ""]
        n += 1
    Path(path).write_text("\n".join(lines))


def write_ass(words, path, group=3):
    """Word-by-word captions, current word cyan, placed above the Shorts UI (bottom 22% stays clear)."""
    def at(t):
        return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    head = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
            "MarginR, MarginV, Encoding",
            f"Style: Cap,Montserrat ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,2,2,60,60,{int(H * 0.27)},1",
            "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    ev = []
    for i in range(0, len(words), group):
        g = words[i:i + group]
        for j, w in enumerate(g):
            end = g[j + 1]["s"] if j + 1 < len(g) else w["e"]
            txt = " ".join(("{\\c&HD2E500&}" + x["w"].upper() + "{\\c&HFFFFFF&}") if k == j else x["w"].upper()
                           for k, x in enumerate(g))
            ev.append(f"Dialogue: 0,{at(w['s'])},{at(max(end, w['s'] + 0.05))},Cap,,0,0,0,,{txt}")
    Path(path).write_text("\n".join(head + ev), encoding="utf-8")


def headline_png(text, path, branding=False):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f, lines = brand.fit_lines(text.upper(), brand.HEADLINE_FONT, int(W * 0.86), int(H * 0.05), 40)
    y = int(H * 0.08)
    for ln in lines:
        tw = f.getlength(ln)
        d.rectangle([(W - tw) / 2 - 22, y - 8, (W + tw) / 2 + 22, y + f.size * 1.12], fill=brand.PINK + (235,))
        d.text(((W - tw) / 2, y), ln, font=f, fill=brand.WHITE)
        y += int(f.size * 1.3)
    if branding:
        wm = brand.wordmark(int(H * 0.026))
        img.paste(wm, (int(W * 0.03), int(H * 0.03)), wm)
    img.save(path)
    return path


def tag_png(text, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = brand.font(brand.HEADLINE_FONT, 72)
    tw = f.getlength(text)
    x, y = W - tw - 70, int(H * 0.45)
    d.rectangle([x - 20, y - 6, x + tw + 20, y + 90], fill=brand.CYAN + (230,))
    d.text((x, y), text, font=f, fill=brand.NIGHT)
    img.save(path)
    return path


def punch_in(at, to=1.12, ramp=0.3, w=W, h=H):
    """Smooth punch-in from 1.0 to `to` starting at `at` s: per-frame scale + centered crop (zoompan buffered
    frames without end and exhausted memory)."""
    z = f"if(lt(t,{at}),1,min({to},1+({to}-1)*(t-{at})/{ramp}))"
    return f"scale=w='trunc({w}*{z}/2)*2':h='trunc({h}*{z}/2)*2':eval=frame,crop={w}:{h}"


def loudnorm_2pass(media, target=-14.0, tp=-1.5, lra=11):
    """Two-pass loudness: measure first, then normalize linearly (one pass undershoots short clips: -17.6 LUFS
    measured on a stream clip). Returns the second-pass filter."""
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(media), "-af",
                        f"loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    try:
        m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
        return (f"loudnorm=I={target}:TP={tp}:LRA={lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
                f"linear=true,aresample=48000")
    except (ValueError, KeyError):
        return f"loudnorm=I={target}:TP={tp}:LRA={lra},aresample=48000"


def frame_graph(src, pr, out_label="fr"):
    """filter_complex from [0:v] to [out_label]: vertical sources are just scaled; 16:9 streams go through the
    framing engine (stack = webcam on top, pip, fill = action-tracked crop, blur = whole frame; auto = detect)."""
    from . import framing
    sw, sh, _ = framing.probe(src)
    if sh > sw:
        return f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[{out_label}]", {"layout": "vertical source"}
    layout, cam = pr.get("layout", "auto"), pr.get("cam")
    det = None
    if layout in ("auto", "stack", "pip") and not cam:
        det = framing.detect_facecam(src)
        cam = det and det["box"]
    if layout == "auto":
        layout = "stack" if cam else "blur"
    fc, info = framing.build(src, layout, cam=cam, game=pr.get("game"), keep=pr.get("keep") or ())
    info["detection"] = det
    return fc.replace("[vout]", f"[{out_label}]"), info


def layout_vf(sw, sh):
    if sh > sw:  # already vertical (e.g. a stacked webcam/gameplay export): keep the frame
        return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    # 16:9 stream: whole frame on a blurred 9:16 fill, so webcam and required overlays stay visible
    return (f"split=2[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=20:2[bg];"
            f"[b]scale={W}:-2[fg];[bg][fg]overlay=0:(H-h)/2")


def new_project(pid, source, start, end, campaign=None, dest="clipcircuit", headline="", punch=None, replay=None,
                title_options=None, caption=""):
    con = db.connect()
    p = db.project_get(con, pid) or {"id": pid, "kind": "clip", "series": "A: Moments", "status": "draft",
                                     "destination": dest, "rights_ids": [], "files": {}, "steps": []}
    p.update({"title": headline, "params": {"source": str(source), "start": start, "end": end, "campaign": campaign,
                                            "headline": headline, "punch": punch, "replay": replay,
                                            "title_options": title_options or [], "caption": caption}})
    db.project_save(con, p)
    pdir = db.ROOT / "projects" / pid
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "project.json").write_text(json.dumps({"id": pid, **p["params"]}, indent=1))
    return p


def build(pid, params, rerun=()):
    con = db.connect()
    p = db.project_get(con, pid)
    pr = params
    out = db.ROOT / "projects" / pid
    out.mkdir(parents=True, exist_ok=True)
    (out / "project.json").write_text(json.dumps({"id": pid, **pr}, indent=1))
    dest, camp = p["destination"], pr.get("campaign")
    cfg = json.loads((db.ROOT / "content" / "campaigns" / f"{camp}.json").read_text()) if camp else {}
    branding = dest == "vice-replay"

    def todo(step):
        return step not in p["steps"] or step in rerun

    try:
        if todo("rights"):
            c = rights.check(pr["source"], dest, ai_voice=False, branding=branding)
            (out / "rights.json").write_text(json.dumps(c, indent=1))
            if not c["ok"]:
                p["status"], p["error"] = "blocked", "; ".join(c["reasons"])
                db.project_save(con, p)
                return p
            p["rights_ids"] = [c["record"]]
            p = db.step_done(con, p, "rights", rights=out / "rights.json")
        cut = out / "cut.mp4"
        if todo("cut"):
            run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", pr["start"], "-to", pr["end"], "-i", pr["source"],
                 "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", cut])
            p = db.step_done(con, p, "cut", cut=cut)
        words_f = out / "words.json"
        if todo("transcribe"):
            words = qc.transcribe(cut) or []
            words_f.write_text(json.dumps(words, indent=0))
            write_srt(words, out / "captions.srt")
            write_ass(words, out / "captions.ass")
            unsure = [w for w in words if w.get("p", 1) < 0.6]
            (out / "captions_review.md").write_text(
                f"# Caption review: {pid}\n\nEdit captions.srt if anything is wrong, then run "
                f"`python -m studio.vice approve-captions {pid}` (re-renders with your edits).\n\n"
                f"Uncertain words (model confidence under 60%): {len(unsure)} of {len(words)}\n\n"
                + "".join(f"- {w['s']:.2f} s: \"{w['w']}\" ({int(100 * w['p'])}%)\n" for w in unsure))
            p["captions_reviewed"] = False
            p = db.step_done(con, p, "transcribe", words=words_f, srt=out / "captions.srt")
        final = out / f"{pid}.mp4"
        if todo("render"):
            # Rendered in passes (main, replay, stream-copy join, audio loudness) so memory stays low: one ffmpeg
            # graph with concat decodes both parts at once and buffers raw 1080x1920 frames (it OOM-killed a run).
            dur, sw, sh = probe(cut)
            enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", FPS,
                   "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
            graph, finfo = frame_graph(cut, pr)
            (out / "framing.json").write_text(json.dumps(finfo, indent=1, default=float))
            post = punch_in(pr["punch"]) + "," if pr.get("punch") is not None else ""
            hl = headline_png(pr["headline"], out / "headline.png", branding) if pr.get("headline") else None
            fc = f"{graph};[fr]{post}setsar=1,fps={FPS}[v0];"
            last = "v0"
            if hl:
                fc += "[v0][1:v]overlay=0:0:eof_action=pass[v1];"
                last = "v1"
            fc += f"[{last}]subtitles='{out / 'captions.ass'}':fontsdir='{brand.FONTS}'[vout]"
            part_a = out / "part_main.mp4"
            run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", cut, *(["-loop", "1", "-t", 3, "-i", hl] if hl else []),
                 "-filter_complex", fc, "-map", "[vout]", "-map", "0:a", "-t", round(dur, 3), *enc, part_a])  # -t: zoompan+overlay never signal the end
            parts = [part_a]
            if pr.get("replay"):  # the payoff again at 0.75x, clearly labelled, its own audio slowed with it
                r0, r1 = pr["replay"]
                tag = tag_png("REPLAY", out / "replay.png")
                part_b = out / "part_replay.mp4"
                run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", r0, "-to", r1, "-i", cut,
                     "-loop", "1", "-t", round((r1 - r0) / 0.75, 2), "-i", tag, "-filter_complex",
                     f"{frame_graph(cut, {**pr, 'cam': (finfo.get('cam') or pr.get('cam'))})[0]};[fr]setsar=1,setpts=PTS/0.75,fps={FPS}[r];[r][1:v]overlay=0:0:eof_action=pass[vout];"
                     f"[0:a]atempo=0.75[aout]", "-map", "[vout]", "-map", "[aout]", "-t", round((r1 - r0) / 0.75, 3), *enc, part_b])
                parts.append(part_b)
            lst = out / "parts.txt"
            lst.write_text("".join(f"file '{x}'\n" for x in parts))
            joined = out / "joined.mp4"
            run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
            run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", joined, "-c:v", "copy", "-af",
                 loudnorm_2pass(joined), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                 "-movflags", "+faststart", final])
            p = db.step_done(con, p, "render", video=final)
        cover = out / "cover.jpg"
        if todo("cover"):
            t = pr.get("punch") or 1.0
            run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", t + 0.4, "-i", final, "-frames:v", "1", "-q:v", "3", cover])
            p = db.step_done(con, p, "cover", cover=cover)
        if todo("qc"):
            rep = qc.check(final, dest=dest, project={"id": pid, "rights_sources": [pr["source"]], "branding": branding,
                                                      "ai_voice": False, "transcript": True, "caption": pr.get("caption", "")},
                           campaign=cfg or None)
            p = db.step_done(con, p, "qc", qc=qc.write(rep, out, pid))
            p["qc_passed"] = rep["passed"]
        if todo("draft"):
            ctype = "campaign-clip" if camp else "owner-gameplay"
            val = channels.validate(dest, ctype, check_token=False)
            qcj = json.loads((out / f"{pid}.qc.json").read_text())
            blockers = [f"QC: {c['check']}: {c['detail']}" for c in qcj["checks"] if c["status"] == "fail"] + val["problems"]
            if not (out / "captions.approved").exists():
                blockers.append("captions not reviewed yet: check captions_review.md, then approve-captions")
            draft = {"project": pid, "destination": dest, "channel_check": val, "video": str(final), "cover": str(cover),
                     "title_options": pr.get("title_options", []), "caption": pr.get("caption", ""),
                     "platforms": cfg.get("platforms", ["YouTube Shorts"]),
                     "campaign": camp, "status": "BLOCKED" if blockers else "awaiting owner approval",
                     "blockers": blockers,
                     "after_posting": ["Submit on the campaign page within 30 minutes of posting"] if camp else [],
                     "human_review": "required"}
            (out / "draft.json").write_text(json.dumps(draft, indent=1, ensure_ascii=False))
            p = db.step_done(con, p, "draft", draft=out / "draft.json")
            p["status"] = draft["status"]
        db.project_save(con, p)
    except Exception as e:  # keep finished steps; the next run resumes from the failed one
        p["status"], p["error"] = "error", str(e)[:1500]
        db.project_save(con, p)
        raise
    return p
