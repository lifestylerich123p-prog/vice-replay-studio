"""Highlight clipper: finds the best moments in a long video and cuts them into vertical Shorts.

Used for (1) paid clipping campaigns (Whop Content Rewards etc.) where a streamer allows clipping their
footage, and (2) the owner's own long gameplay recordings.

    python -m studio.clip SOURCE.mp4 --campaign lacy-gta6      # rules + layout from content/campaigns/lacy-gta6.json
    python -m studio.clip SOURCE.mp4 --top 8 --layout full     # own gameplay, centre crop
    python -m studio.clip SOURCE.mp4 --at 754 --len 35         # cut one moment you already know

How moments are found (free, no API): loudness spikes (shouting, explosions, crashes) plus how fast the
picture changes. Every candidate is scored; the best non-overlapping windows win. Original audio is kept
(it's the streamer's voice, or your game sound), so no Vice Replay music is added.
"""
import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from . import brand

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit("Command failed:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-3000:])
    return r.stdout + r.stderr


def probe(src):
    out = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type",
                          "-of", "json", str(src)]))
    v = next(s for s in out["streams"] if s["codec_type"] == "video")
    return float(out["format"]["duration"]), v["width"], v["height"]


def loudness_curve(src):
    """Momentary loudness (LUFS) every 0.1 s."""
    log = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-vn", "-af", "ebur128=peak=none", "-f", "null", "-"])
    pts = []
    for m in re.finditer(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+|-inf)", log):
        pts.append((float(m.group(1)), -70.0 if m.group(2) == "-inf" else float(m.group(2))))
    return pts


def scene_times(src, threshold=0.3):
    log = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-an", "-vf",
               f"scale=320:-2,select='gt(scene,{threshold})',showinfo", "-f", "null", "-"])
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]


def find_moments(src, top, clip_len, total):
    print("  analysing audio...")
    loud = loudness_curve(src)
    print("  analysing picture...")
    cuts = scene_times(src)
    if not loud:
        sys.exit("No audio found in the source; use --at to pick moments by hand.")
    vals = [v for _, v in loud if v > -69]
    base = statistics.median(vals) if vals else -30
    spread = statistics.pstdev(vals) or 1.0
    # score per second: loudness above normal + scene changes nearby
    secs = int(total) + 1
    score = [0.0] * secs
    for t, v in loud:
        i = int(t)
        if i < secs:
            score[i] = max(score[i], (v - base) / spread)
    for c in cuts:
        for i in range(max(0, int(c) - 2), min(secs, int(c) + 3)):
            score[i] += 0.25
    # best windows, peak placed ~60% into the clip (build-up, then payoff)
    order = sorted(range(secs), key=lambda i: score[i], reverse=True)
    picked = []
    for i in order:
        if len(picked) >= top or score[i] < 1.0:
            break
        start = max(0.0, min(total - clip_len, i - clip_len * 0.6))
        if all(abs(start - p[0]) >= clip_len for p in picked):
            picked.append((start, round(score[i], 2)))
    return sorted(picked)


def layout_filter(layout, sw, sh, cfg):
    """Video filter producing a 1080x1920 frame from the source."""
    if layout == "stacked":
        # facecam on top (40%), gameplay below (60%); boxes are fractions of the source frame: [x, y, w, h]
        fx, fy, fw, fh = cfg.get("facecam_box", [0.0, 0.0, 0.3, 0.3])
        gx, gy, gw, gh = cfg.get("gameplay_box", [0.1, 0.0, 0.8, 1.0])
        top_h, bot_h = int(H * 0.4), H - int(H * 0.4)
        return (f"[0:v]split=2[a][b];"
                f"[a]crop={int(fw * sw)}:{int(fh * sh)}:{int(fx * sw)}:{int(fy * sh)},"
                f"scale={W}:{top_h}:force_original_aspect_ratio=increase,crop={W}:{top_h}[cam];"
                f"[b]crop={int(gw * sw)}:{int(gh * sh)}:{int(gx * sw)}:{int(gy * sh)},"
                f"scale={W}:{bot_h}:force_original_aspect_ratio=increase,crop={W}:{bot_h}[game];"
                f"[cam][game]vstack[base]")
    if layout == "blur":
        # whole 16:9 frame in the middle, blurred zoomed copy behind it
        return (f"[0:v]split=2[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"boxblur=20:2,eq=brightness=-0.15[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=0:(H-h)/2[base]")
    return f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[base]"  # full: centre crop


def overlay_png(text, out, tag_line=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if text:
        f, lines = brand.fit_lines(text.upper(), brand.HEADLINE_FONT, int(W * 0.86), 92, 50)
        y = int(H * 0.42) - 10
        for ln in lines:
            tw = f.getlength(ln)
            x = (W - tw) / 2
            d.rectangle([x - 22, y - 6, x + tw + 22, y + f.size * 1.12], fill=brand.PINK + (240,))
            d.text((x, y - f.size * 0.06), ln, font=f, fill=brand.WHITE)
            y += int(f.size * 1.2)
    if tag_line:
        f2 = brand.font(brand.BODY_FONT, 38)
        tw = f2.getlength(tag_line)
        d.text(((W - tw) / 2, H - 150), tag_line, font=f2, fill=brand.WHITE, stroke_width=4, stroke_fill=brand.NIGHT)
    im.save(out)
    return out


def transcribe(src, start, length, work):
    """Word timings with faster-whisper if it is installed and its model can download; else None."""
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return None
    wav = work / "speech.wav"
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(start), "-t", str(length), "-i", str(src), "-ac", "1", "-ar", "16000", str(wav)])
    try:
        import soundfile as sf
        audio, _ = sf.read(str(wav), dtype="float32")  # pass samples directly (avoids PyAV version issues)
        model = WhisperModel("small.en", device="cpu", compute_type="int8")
        segs, _ = model.transcribe(audio, word_timestamps=True, vad_filter=True)
        return [(w.start, w.end, w.word.strip()) for s in segs for w in (s.words or [])]
    except Exception as e:
        print(f"  (captions skipped: {type(e).__name__})")
        return None


def caption_ass(words, out):
    """Word-by-word captions in 3-word groups, current word in cyan (same look as the main machine)."""
    size = 78
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
             "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
             "MarginR, MarginV, Encoding",
             f"Style: Cap,Montserrat ExtraBold,{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H8C000000,1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]

    def ts(t):
        return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    for g in range(0, len(words), 3):
        group = words[g:g + 3]
        for j, (s, e, _) in enumerate(group):
            end = group[j + 1][0] if j + 1 < len(group) else e
            txt = " ".join((r"{\c&HD2E500&}" + x.upper() + r"{\c&HFFFFFF&}") if k == j else x.upper()
                           for k, (_, _, x) in enumerate(group))
            lines.append(f"Dialogue: 0,{ts(s)},{ts(max(end, s + 0.05))},Cap,,0,0,0,,{{\\pos({W // 2},{int(H * 0.40)})}}{txt}")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def render(src, start, length, name, layout, cfg, sw, sh, out_dir, headline, tag_line):
    work = out_dir / f"work_{name}"
    work.mkdir(parents=True, exist_ok=True)
    words = transcribe(src, start, length, work) if cfg.get("captions", True) else None
    ov = overlay_png(headline, work / "overlay.png")
    fc = layout_filter(layout, sw, sh, cfg) + f";[base][1:v]overlay=0:0:enable='lt(t,2.5)'[o1]"
    last = "[o1]"
    if tag_line:
        tag_png = overlay_png("", work / "tag.png", tag_line)
        fc += f";[o1][2:v]overlay=0:0[o2]"
        last = "[o2]"
    if words:
        ass = caption_ass(words, work / "captions.ass")
        fc += f";{last}subtitles='{ass}':fontsdir='{brand.FONTS}'[v]"
    else:
        fc += f";{last}null[v]"
    ins = ["-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", str(src), "-loop", "1", "-i", str(ov)]
    if tag_line:
        ins += ["-loop", "1", "-i", str(work / "tag.png")]
    out = out_dir / f"{name}.mp4"
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-t", f"{length:.2f}", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)])
    return out, bool(words)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("--campaign", help="name of content/campaigns/<name>.json")
    ap.add_argument("--top", type=int, default=6, help="how many clips to cut")
    ap.add_argument("--len", type=float, help="clip length in seconds")
    ap.add_argument("--at", type=float, action="append", help="cut at this second instead of auto-finding (repeatable)")
    ap.add_argument("--layout", choices=["stacked", "blur", "full"])
    ap.add_argument("--headline", help="text shown for the first 2.5 s (the hook)")
    a = ap.parse_args()

    src = Path(a.source).resolve()
    cfg = {}
    if a.campaign:
        cfg = json.loads((ROOT / "content" / "campaigns" / f"{a.campaign}.json").read_text())
    layout = a.layout or cfg.get("layout", "full")
    clip_len = a.len or cfg.get("clip_seconds", 30)
    total, sw, sh = probe(src)
    clip_len = min(clip_len, total)
    tag_line = cfg.get("on_screen_credit")  # e.g. "twitch.tv/streamer" when the campaign requires it
    group = a.campaign or re.sub(r"[^a-z0-9]+", "-", src.stem.lower()).strip("-")
    out_dir = ROOT / "output" / "clips" / group
    out_dir.mkdir(parents=True, exist_ok=True)

    if a.at:
        moments = [(max(0.0, t - clip_len * 0.6), None) for t in a.at]
    else:
        print(f"Finding the best {a.top} moments in {src.name} ({total / 60:.1f} min)...")
        moments = find_moments(src, a.top, clip_len, total)
    report = []
    for k, (start, score) in enumerate(moments, 1):
        name = f"{group}-{k:02d}-{int(start // 60):02d}m{int(start % 60):02d}s"
        print(f"[{k}/{len(moments)}] {name} (score {score})")
        out, captioned = render(src, start, clip_len, name, layout, cfg, sw, sh, out_dir, a.headline, tag_line)
        report.append(f"| {out.name} | {int(start // 60)}:{int(start % 60):02d} | {score} | {'yes' if captioned else 'no'} |")
    (out_dir / "clips.md").write_text("| Clip | Starts at | Score | Captions |\n|---|---|---|---|\n" + "\n".join(report) + "\n")
    print(f"\nDone: {len(moments)} clips in {out_dir}")


if __name__ == "__main__":
    main()
