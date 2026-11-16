"""Vice Replay Studio: turn an episode script (JSON) into a finished YouTube video.

    python -m studio.make_video episodes/launch-week.json            # 16:9 main video
    python -m studio.make_video episodes/launch-week.json --short    # 9:16 YouTube Short
    python -m studio.make_video episodes/launch-week.json --preview  # fast low-res draft

Output lands in output/<slug>/: video, thumbnail.jpg, description.txt.
"""
import argparse
import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from . import brand

ROOT = Path(__file__).resolve().parent.parent
FPS = 30
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_VOICE = "en-US-AndrewNeural"


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit("Command failed:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-3000:])
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).strip())


# ---------- voice ----------

def tts(text, voice, rate, out_base):
    """Neural voice via edge-tts (free, needs internet). Falls back to offline espeak-ng."""
    mp3 = out_base.with_suffix(".mp3")
    try:
        import edge_tts
        asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(str(mp3)))
        if mp3.stat().st_size > 1000:
            return mp3
    except Exception as e:  # network blocked, package missing, ...
        print(f"  edge-tts unavailable ({type(e).__name__}); using offline espeak-ng voice")
    if not shutil.which("espeak-ng"):
        sys.exit("No voice engine: run `pip install edge-tts` (recommended) or install espeak-ng.")
    wav = out_base.with_suffix(".wav")
    run(["espeak-ng", "-v", "en-us+m3", "-s", "168", "-w", str(wav), text])
    return wav


# ---------- captions ----------

def ass_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def caption_file(text, start, total, out, w, h, vertical):
    """Burned-in captions, 3-5 words at a time, timed by character count."""
    words = text.split()
    chunks, cur = [], []
    for wd in words:
        cur.append(wd)
        if len(cur) >= (3 if vertical else 5) or re.search(r"[.,!?;:]$", wd):
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    weights = [len(c) + 4 for c in chunks]
    span = total - start - 0.15
    size = int(h * (0.052 if vertical else 0.058))
    margin_v = int(h * (0.30 if vertical else 0.08))
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,Montserrat ExtraBold,{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H8C1F00FF,1,0,0,0,100,100,0,0,1,{max(4, size // 10)},3,2,60,60,{margin_v},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    t = start
    for c, wt in zip(chunks, weights):
        d = span * wt / sum(weights)
        cap = c.upper()
        # make numbers pop in cyan
        cap = re.sub(r"(\$?\d[\d,.:]*\s?(?:GB|%|K|M)?)", r"{\\c&HD2E500&}\1{\\c&HFFFFFF&}", cap)
        lines.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},Cap,,0,0,0,,{{\\fad(60,40)}}{cap}")
        t += d
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# ---------- visuals ----------

def visual_input(media, dur, w, h, seed, work):
    """ffmpeg input args + filter for the segment background."""
    if media and Path(media).suffix.lower() in VIDEO_EXT:
        args = ["-stream_loop", "-1", "-i", str(media)]
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},eq=brightness=-0.04:saturation=1.15"
        return args, vf
    if media and Path(media).suffix.lower() in IMAGE_EXT:
        src = media
    else:
        src = work / f"bg_{seed}.png"
        if not src.exists():
            brand.neon_background(int(w * 1.2), int(h * 1.2), seed=seed).save(src)
    # slow Ken Burns pan across a 120% image (smooth, unlike zoompan)
    bw, bh = int(w * 1.2) // 2 * 2, int(h * 1.2) // 2 * 2
    dx = "(iw-ow)*t/{d}" if seed % 2 == 0 else "(iw-ow)*(1-t/{d})"
    vf = (f"scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},"
          f"crop={w}:{h}:x='{dx.format(d=dur)}':y='(ih-oh)*0.5'")
    return ["-loop", "1", "-framerate", str(FPS), "-i", str(src)], vf


ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def render_segment(i, seg, audio, w, h, vertical, work, enc):
    voice_dur = duration(audio)
    dur = round(voice_dur + 0.45, 2)
    media = seg.get("media")
    if media and not Path(media).exists():
        print(f"  ! media not found, using generated background: {media}")
        media = None
    vin, vf = visual_input(media, dur, w, h, i, work)
    ov = work / f"ov_{i}.png"
    brand.headline_card(seg.get("headline", ""), w, h, vertical).save(ov)
    subs = caption_file(seg["text"], 0.2, dur, work / f"cap_{i}.ass", w, h, vertical)
    out = work / f"seg_{i:02d}.mp4"
    fc = (f"[0:v]{vf},setsar=1,fps={FPS}[bg];[bg][1:v]overlay=0:0,"
          f"subtitles='{subs}':fontsdir='{brand.FONTS}',"
          f"fade=t=in:st=0:d=0.25,fade=t=out:st={dur - 0.25}:d=0.25[v];"
          f"[2:a]adelay=200|200,apad,atrim=0:{dur},aformat=sample_rates=48000:channel_layouts=stereo[a]")
    run(["ffmpeg", "-y", "-v", "error", *vin, "-loop", "1", "-i", str(ov), "-i", str(audio),
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(dur), *enc, str(out)])
    return out, dur


def render_card(name, img, dur, work, enc, w, h):
    """Still card (intro/outro) with a gentle zoom-in and fades, silent audio."""
    out = work / f"{name}.mp4"
    vf = (f"scale={int(w * 1.08)}:-2,crop={w}:{h}:x='(iw-ow)/2':y='(ih-oh)/2',"
          f"scale={w}:{h},zoompan=z='1+0.04*on/{int(dur * FPS)}':d=1:s={w}x{h}:fps={FPS},"
          f"fade=t=in:st=0:d=0.3,fade=t=out:st={dur - 0.35}:d=0.35")
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", str(img),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-vf", vf, "-t", str(dur), *enc, str(out)])
    return out


def intro_image(title, w, h, path):
    img = brand.neon_background(w, h, seed=7).convert("RGBA")
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 110))
    img.alpha_composite(shade)
    wm = brand.wordmark(int(h * 0.13))
    img.alpha_composite(wm, ((w - wm.width) // 2, int(h * 0.30)))
    f, lines = brand.fit_lines(title.upper(), brand.HEADLINE_FONT, int(w * 0.85), int(h * 0.06), 30)
    d = ImageDraw.Draw(img)
    y = int(h * 0.30) + wm.height + int(h * 0.04)
    for ln in lines:
        d.text(((w - f.getlength(ln)) / 2, y), ln, font=f, fill=brand.WHITE, stroke_width=4, stroke_fill=brand.NIGHT)
        y += int(f.size * 1.15)
    img.convert("RGB").save(path)
    return path


def outro_image(text, w, h, path):
    img = brand.neon_background(w, h, seed=11).convert("RGBA")
    img.alpha_composite(Image.new("RGBA", (w, h), (0, 0, 0, 120)))
    d = ImageDraw.Draw(img)
    f = brand.font(brand.HEADLINE_FONT, int(h * 0.13))
    label = "SUBSCRIBE"
    tw = f.getlength(label)
    x, y = (w - tw) / 2, h * 0.33
    d.rounded_rectangle([x - 50, y - 10, x + tw + 50, y + f.size * 1.2], radius=24, fill=brand.PINK)
    d.text((x, y), label, font=f, fill=brand.WHITE)
    f2, lines = brand.fit_lines(text.upper(), brand.HEADLINE_FONT, int(w * 0.8), int(h * 0.055), 28)
    y2 = y + f.size * 1.5
    for ln in lines:
        d.text(((w - f2.getlength(ln)) / 2, y2), ln, font=f2, fill=brand.CYAN, stroke_width=3, stroke_fill=brand.NIGHT)
        y2 += f2.size * 1.2
    wm = brand.wordmark(int(h * 0.06))
    img.alpha_composite(wm, ((w - wm.width) // 2, int(h * 0.08)))
    img.convert("RGB").save(path)
    return path


def mix_music(video, music, out, enc_audio):
    total = duration(video)
    fc = (f"[1:a]volume=0.10,afade=t=in:d=1.5,afade=t=out:st={max(0, total - 3)}:d=3,atrim=0:{total}[m];"
          f"[0:a][m]amix=inputs=2:duration=first:normalize=0[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-stream_loop", "-1", "-i", str(music),
         "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", *enc_audio, str(out)])


def fmt_ts(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode")
    ap.add_argument("--short", action="store_true", help="vertical 1080x1920 YouTube Short")
    ap.add_argument("--preview", action="store_true", help="fast low-res draft")
    ap.add_argument("--voice", help=f"edge-tts voice (default {DEFAULT_VOICE})")
    a = ap.parse_args()

    ep_path = Path(a.episode).resolve()
    ep = json.loads(ep_path.read_text())
    base = ep_path.parent
    slug = ep.get("slug") or re.sub(r"[^a-z0-9]+", "-", ep["title"].lower()).strip("-")
    vertical = a.short
    w, h = (1080, 1920) if vertical else (1920, 1080)
    if a.preview:
        w, h = w // 2, h // 2
    enc = ENC + (["-preset", "veryfast", "-crf", "28"] if a.preview else [])
    voice = a.voice or ep.get("voice", DEFAULT_VOICE)
    rate = ep.get("rate", "+8%")

    out_dir = ROOT / "output" / slug
    work = out_dir / ("work_short" if vertical else "work")
    work.mkdir(parents=True, exist_ok=True)

    segments = ep["short"] if vertical and ep.get("short") else ep["segments"]
    for s in segments:
        if s.get("media"):
            s["media"] = str((base / s["media"]).resolve()) if not Path(s["media"]).is_absolute() else s["media"]

    parts, chapters, t = [], [], 0.0
    if not vertical:
        intro = render_card("intro", intro_image(ep["title"], w, h, work / "intro.png"), 2.6, work, enc, w, h)
        parts.append(intro)
        t += duration(intro)
    for i, seg in enumerate(segments):
        print(f"[{i + 1}/{len(segments)}] {seg.get('headline') or seg['text'][:40]}")
        audio = tts(seg["text"], voice, rate, work / f"vo_{i:02d}")
        clip, d = render_segment(i, seg, audio, w, h, vertical, work, enc)
        if seg.get("chapter") or seg.get("headline"):
            chapters.append((0.0 if i == 0 and vertical else t, seg.get("chapter") or seg["headline"]))
        parts.append(clip)
        t += duration(clip)
    if not vertical:
        outro = render_card("outro", outro_image(ep.get("outro_card", "New GTA 6 videos every week"), w, h,
                                                 work / "outro.png"), 4.0, work, enc, w, h)
        parts.append(outro)

    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    name = f"{slug}{'-short' if vertical else ''}{'-preview' if a.preview else ''}.mp4"
    raw = work / "joined.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(raw)])
    final = out_dir / name
    music = ep.get("music")
    music = (base / music) if music else next(iter(sorted((ROOT / "assets" / "music").glob("*.mp3"))), None)
    if music and Path(music).exists():
        mix_music(raw, music, final, ["-c:a", "aac", "-b:a", "192k"])
    else:
        shutil.copy(raw, final)

    if not vertical:
        th = ep.get("thumbnail", {})
        bg = th.get("image")
        brand.thumbnail(th.get("line1", ep["title"]), th.get("line2", ""), th.get("tag", ""),
                        out_dir / "thumbnail.jpg", bg_image=str(base / bg) if bg else None)
        # YouTube chapters need: first at 0:00, at least 3, each >= 10s
        ch = []
        for s, n in chapters:
            if not ch:
                ch.append((0.0, n))
            elif s - ch[-1][0] >= 10:
                ch.append((s, n))
        desc = [ep.get("description", ep["title"]), ""]
        if len(ch) >= 3:
            desc += ["CHAPTERS"] + [f"{fmt_ts(s)} {n}" for s, n in ch] + [""]
        if ep.get("sources"):
            desc += ["SOURCES"] + ep["sources"] + [""]
        desc += ["Subscribe to Vice Replay for GTA's wildest moments. On replay.", "",
                 "Vice Replay is a fan channel and is not affiliated with Rockstar Games or Take-Two Interactive.", "",
                 " ".join("#" + tg.replace(" ", "") for tg in ep.get("hashtags", ["GTA6", "GTAVI", "ViceCity"]))]
        (out_dir / "description.txt").write_text("\n".join(desc))
        (out_dir / "tags.txt").write_text(", ".join(ep.get("tags", [])))
    print(f"\nDone: {final}  ({fmt_ts(duration(final))})")


if __name__ == "__main__":
    main()
