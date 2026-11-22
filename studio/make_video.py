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
DEFAULT_VOICE = "af_heart"  # Kokoro grade A (am_michael is C+); config/channel.json "voice" overrides


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit("Command failed:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-3000:])
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).strip())


# ---------- voice ----------

VOICE_DIR = ROOT / "assets" / "voice"
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KOKORO_FILES = ["kokoro-v1.0.int8.onnx", "voices-v1.0.bin"]
_kokoro = None


def kokoro_tts(text, voice, speed, wav):
    """Kokoro: free open-source neural voice that runs locally (no API key, no internet after first run)."""
    global _kokoro
    if _kokoro is None:
        import urllib.request
        from kokoro_onnx import Kokoro
        VOICE_DIR.mkdir(parents=True, exist_ok=True)
        for f in KOKORO_FILES:
            if not (VOICE_DIR / f).exists():
                print(f"  downloading voice model {f} (one time)...")
                urllib.request.urlretrieve(KOKORO_URL + f, VOICE_DIR / (f + ".part"))
                (VOICE_DIR / (f + ".part")).rename(VOICE_DIR / f)
        _kokoro = Kokoro(str(VOICE_DIR / KOKORO_FILES[0]), str(VOICE_DIR / KOKORO_FILES[1]))
    import soundfile as sf
    samples, sr = _kokoro.create(text, voice=voice, speed=speed, lang="es" if voice[:3] in ("ef_", "em_") else "en-us")
    sf.write(str(wav), samples, sr)
    return wav


def http_tts(url, headers, payload, out):
    import os
    import urllib.request
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=120) as r:
        out.write_bytes(r.read())
    return out


def premium_tts(text, voice, out_base):
    """Paid voices. Keys come from env vars, or from the Claude cloud proxy, which injects the saved
    key for the host (the placeholder value is then replaced on the way out)."""
    import os
    engine, _, name = voice.partition(":")
    mp3 = out_base.with_suffix(".mp3")
    if engine == "eleven":
        key = os.environ.get("ELEVENLABS_API_KEY", "set-by-proxy")
        return http_tts(f"https://api.elevenlabs.io/v1/text-to-speech/{name}?output_format=mp3_44100_128",
                        {"xi-api-key": key},
                        {"text": text, "model_id": "eleven_multilingual_v2",
                         "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35}}, mp3)
    if engine == "openai":
        key = os.environ.get("OPENAI_API_KEY", "set-by-proxy")
        return http_tts("https://api.openai.com/v1/audio/speech", {"Authorization": f"Bearer {key}"},
                        {"model": "gpt-4o-mini-tts", "voice": name or "onyx", "input": text, "response_format": "mp3",
                         "instructions": "Energetic, confident YouTube gaming news narrator. Punchy, fast-paced, "
                                         "clear. Slight excitement on big numbers and reveals."}, mp3)
    raise ValueError(f"unknown voice engine: {engine}")


def tts(text, voice, rate, out_base):
    """Voice engines: "eleven:<voice_id>" (ElevenLabs) and "openai:<voice>" (OpenAI) are paid APIs;
    Kokoro voices (am_*, af_*, bm_*, bf_*) run locally for free; en-US-*Neural voices use Microsoft
    edge-tts (needs a normal internet connection). Falls back to robotic espeak-ng."""
    if ":" in voice:
        try:
            return premium_tts(text, voice, out_base)
        except Exception as e:
            print(f"  ! {voice.split(':')[0]} voice failed ({type(e).__name__}: {e}); using free Kokoro voice")
            voice = channel_setting("voice") or DEFAULT_VOICE
    if not voice.endswith("Neural"):
        try:
            speed = 1 + int(rate.strip("%+")) / 100 if rate.strip("%+-").isdigit() else 1.08
            return kokoro_tts(text, voice, speed, out_base.with_suffix(".wav"))
        except Exception as e:
            print(f"  Kokoro voice failed ({type(e).__name__}: {e}); trying fallback")
    mp3 = out_base.with_suffix(".mp3")
    try:
        import edge_tts
        v = voice if voice.endswith("Neural") else "en-US-AndrewNeural"
        asyncio.run(edge_tts.Communicate(text, v, rate=rate).save(str(mp3)))
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


_WHISPER = {}


def _norm_word(w):
    return re.sub(r"[^\w']", "", w.lower()).strip("'")


def align_words(text, audio, lang="en"):
    """Real word timings for our own narration: faster-whisper word timestamps on the TTS audio, matched to the
    script words (difflib). Unmatched script words are interpolated between matched neighbours. Returns a list of
    (start, end) per script word, or None when the match is too weak (then captions fall back to estimates)."""
    try:
        import difflib
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(audio), "-f", "s16le", "-ac", "1", "-ar",
                              "16000", "-"], capture_output=True).stdout
        pcm = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
        if "m" not in _WHISPER:
            _WHISPER["m"] = WhisperModel("base", device="cpu", compute_type="int8")
        segs, _ = _WHISPER["m"].transcribe(pcm, language=lang, word_timestamps=True, vad_filter=False)
        heard = [(w.word, w.start, w.end) for sg in segs for w in (sg.words or [])]
    except Exception as e:  # model download blocked, decode error...
        print(f"  (caption alignment skipped: {type(e).__name__})")
        return None
    script = text.split()
    a = [_norm_word(x) for x in script]
    b = [_norm_word(x[0]) for x in heard]
    times = [None] * len(script)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = (heard[blk.b + k][1], heard[blk.b + k][2])
    matched = sum(t is not None for t in times)
    if not script or matched / len(script) < 0.6:
        return None
    total = len(pcm) / 16000
    i = 0
    while i < len(times):  # fill gaps: spread unmatched words between the matched neighbours by length
        if times[i] is None:
            j = i
            while j < len(times) and times[j] is None:
                j += 1
            t0 = times[i - 1][1] if i > 0 else 0.0
            t1 = times[j][0] if j < len(times) else total
            lens = [len(script[k]) + 1 for k in range(i, j)]
            acc = t0
            for k, ln in zip(range(i, j), lens):
                d = (t1 - t0) * ln / sum(lens)
                times[k] = (acc, acc + d)
                acc += d
            i = j
        else:
            i += 1
    return times


_ONES = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                       "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
_SCALES = {"hundred": 100, "thousand": 1000, "million": 1_000_000, "billion": 1_000_000_000}
_UNITS = {"hours", "hour", "minutes", "minute", "seconds", "percent", "feet", "dollars", "dollar", "million", "billion",
          "thousand", "players", "views", "days", "years", "credits", "fps", "gigabytes", "gb", "cheats", "stars"}


def _num_value(run):
    """Value of a run of English number words ("fifty two", "two hundred fifty thousand"), or None."""
    total, cur = 0, 0
    for w in run:
        # spoken years: "nineteen ninety eight" = 19|98, "twenty thirteen" = 20|13 (a tens word or a teen after a
        # number already in progress starts the next two digits; Nov 22 a caption showed "FROM 117" for 1998)
        if cur % 100 and ((w in _TENS) or (w in _ONES and _ONES[w] >= 10)):
            cur = cur * 100 + (_TENS.get(w) or _ONES[w])
        elif w in _ONES:
            cur += _ONES[w]
        elif w in _TENS:
            cur += _TENS[w]
        elif w == "hundred":
            cur = max(cur, 1) * 100
        elif w in _SCALES:
            total += max(cur, 1) * _SCALES[w]; cur = 0
        else:
            return None
    return total + cur


def display_tokens(words, lang="en"):
    """Caption tokens: runs of spoken number words become digits ("fifty two" -> "52", "ninety eight percent" ->
    "98%"), only when it's clearly a number (2+ words, 10 or more, or followed by a unit), so "number one" and
    "this one floats" stay words. English only: in Spanish "ten cuidado" must not become "10 cuidado".
    Returns [(text, first_word_index, last_word_index, is_number)]."""
    out, i, low = [], 0, [re.sub(r"[^\w]", "", w.lower()) for w in words]
    numw = (set(_ONES) | set(_TENS) | {"hundred"} | set(_SCALES)) if lang == "en" else set()
    while i < len(words):
        j = i
        while j < len(words) and low[j] in numw and not re.search(r"[.,!?;:]$", words[j][:-1] if j > i else ""):
            j += 1
            if re.search(r"[.,!?;:]$", words[j - 1]):
                break
        run = low[i:j]
        val = _num_value(run) if run else None
        nxt = low[j] if j < len(words) else ""
        if val is not None and (len(run) >= 2 or val >= 10 or nxt in _UNITS) and not (len(run) == 1 and run[0] in _SCALES):
            tail = re.search(r"[.,!?;:]+$", words[j - 1])
            year = 1900 <= val <= 2100 or (1000 <= val < 1900 and not any(w in _SCALES for w in run))
            txt = f"{val}" if year else f"{val:,}"  # 1998, not 1,998
            if nxt == "percent":
                txt += "%"; j += 1
                tail = re.search(r"[.,!?;:]+$", words[j - 1])
            out.append((txt + (tail.group(0) if tail else ""), i, j - 1, True))
            i = j
            continue
        if low[i] == "gta" and i + 1 < len(words) and re.fullmatch(r"(5|6|v|vi)s?", low[i + 1]):  # "GTA 6" never splits
            out.append((f"{words[i]} {words[i + 1]}", i, i + 1, False))
            i += 2
            continue
        out.append((words[i], i, i, bool(re.search(r"\d|\$|%", words[i]))))
        i += 1
    return out


def channel_setting(key, default=None):
    """A channel-wide setting from config/channel.json (e.g. "voice", "voice_es", "caption_style")."""
    try:
        return json.loads((ROOT / "config" / "channel.json").read_text()).get(key, default)
    except Exception:  # noqa: BLE001
        return default


def caption_style():
    """"animated" (pop-in groups, bouncing spoken word, numbers as pink digits) or "classic". Set in
    config/channel.json "caption_style" ("animated" since the owner approved it on Nov 21, 2026); the env var
    VR_CAPTIONS overrides it for one render."""
    import os
    if os.environ.get("VR_CAPTIONS"):
        return os.environ["VR_CAPTIONS"]
    try:
        return json.loads((ROOT / "config" / "channel.json").read_text()).get("caption_style", "classic")
    except Exception:  # noqa: BLE001
        return "classic"


def caption_file(text, start, total, out, w, h, vertical, times=None, lang="en"):
    """Burned-in animated captions, 3 (Shorts) or 5 tokens at a time. Each group pops in (85% -> 100%), the token
    being spoken bounces (124% -> 112%) in cyan, and numbers show as digits in hot pink ("52 HOURS", "98%").
    Timed to the real speech when `times` (one (start, end) per script word, from align_words) is given;
    otherwise estimated from character counts."""
    words = text.split()
    animated = caption_style() == "animated"
    toks = display_tokens(words, lang) if animated else [(wd, k, k, False) for k, wd in enumerate(words)]
    groups, cur = [], []
    for tk in toks:
        cur.append(tk)
        if len(cur) >= (3 if vertical else 5) or re.search(r"[.,!?;:]$", tk[0]):
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    size = int(h * (0.052 if vertical else 0.058))
    margin_v = int(h * (0.30 if vertical else 0.08))
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,Montserrat ExtraBold,{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H8C1F00FF,1,0,0,0,100,100,0,0,1,{max(4, size // 10)},3,2,60,60,{margin_v},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    PINK, CYAN, WHITE = r"&H8E1FFF&", r"&HD2E500&", r"&HFFFFFF&"

    def render(group, j, first):
        # every token carries its own colour + scale tags, so the group pop-in (85% -> 100%) and the spoken token's
        # bounce (-> 124% -> 112%) don't cancel each other
        if not animated:  # classic look: the spoken word in cyan, a little bigger, no motion
            return " ".join((rf"{{\c{CYAN}\fscx112\fscy112}}{tx.upper()}{{\c{WHITE}\fscx100\fscy100}}" if q == j else tx.upper())
                            for q, (tx, _, _, _) in enumerate(group))
        start_scale = r"\fscx85\fscy85" if first else r"\fscx100\fscy100"
        parts = []
        for q, (tx, _, _, is_num) in enumerate(group):
            if q == j:
                hi = PINK if is_num else CYAN
                parts.append(rf"{{\c{hi}{start_scale}\t(0,80,\fscx124\fscy124)\t(80,160,\fscx112\fscy112)}}{tx.upper()}")
            else:
                col = PINK if is_num else WHITE
                grow = r"\t(0,90,\fscx100\fscy100)" if first else ""
                parts.append(rf"{{\c{col}{start_scale}{grow}}}{tx.upper()}")
        return " ".join(parts)

    if times and len(times) == len(words):
        ev = []
        for g in groups:
            for j, (_, i0, i1, _) in enumerate(g):
                s0 = start + times[i0][0]
                nxt = g[j + 1][1] if j + 1 < len(g) else None
                s1 = start + (times[nxt][0] if nxt is not None else times[i1][1] + 0.12)
                ev.append([s0, max(s1, s0 + 0.06), render(g, j, j == 0)])
        for a, b in zip(ev, ev[1:]):  # never two groups on screen at once (they'd overlap)
            a[1] = max(a[0] + 0.04, min(a[1], b[0]))
        lines += [f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{txt}" for a, b, txt in ev]
        out.write_text("\n".join(lines), encoding="utf-8")
        return out
    span = total - start - 0.15
    weights = [sum(len(t[0]) + 2 for t in g) + 4 for g in groups]
    t = start
    for g, wt in zip(groups, weights):
        d = span * wt / sum(weights)
        ww = [len(x[0]) + 2 for x in g]
        wt0 = t
        for j, word_len in enumerate(ww):
            wd = d * word_len / sum(ww)
            lines.append(f"Dialogue: 0,{ass_time(wt0)},{ass_time(wt0 + wd)},Cap,,0,0,0,,{render(g, j, j == 0)}")
            wt0 += wd
        t += d
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# ---------- visuals ----------

def visual_input(media, dur, w, h, seed, work, start=None):
    """ffmpeg input args + filter for the segment background. Clip audio is never used
    (trailer music is what triggers Content ID claims)."""
    if media and Path(media).suffix.lower() in VIDEO_EXT:
        if start is None:  # spread segments across the clip so the same shot isn't reused
            length = duration(media)
            start = (seed * 7.3) % max(1.0, length - dur) if length > dur + 1 else 0
        args = ["-ss", f"{start:.2f}", "-stream_loop", "-1", "-i", str(media)]
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


def callout_png(c, w, h, path):
    """Ring + label marking one detail on screen (Details/Tested formats). c: x, y, r (0-1 of width), label."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = c["x"] * w, c["y"] * h, c.get("r", 0.08) * w
    for grow, col, wid in ((10, brand.CYAN + (110,), 18), (0, brand.PINK + (255,), 10)):
        d.ellipse([cx - r - grow, cy - r - grow, cx + r + grow, cy + r + grow], outline=col, width=wid)
    if c.get("label"):
        f = brand.font(brand.HEADLINE_FONT, int(w * 0.075))
        tw = f.getlength(c["label"])
        tx = min(max(24, cx - tw / 2), w - tw - 24)
        above = cy - r - w * 0.13 > h * 0.30 and not c.get("label_below")
        ty = cy - r - int(w * 0.13) if above else cy + r + int(w * 0.03)
        d.text((tx, ty), c["label"], font=f, fill=brand.WHITE + (255,), stroke_width=6, stroke_fill=brand.NIGHT + (255,))
    img.save(path)
    return path


def seg_effects(seg, vf, w, h, dur):
    """Optional per-segment editing: smart crop ("focus"), freeze frame ("freeze"), punch-in ("zoom")."""
    focus = seg.get("focus")
    if focus is not None and f"crop={w}:{h}" in vf:  # which part of a wide shot a vertical frame keeps (0 left .. 1 right)
        fx, fy = (focus, 0.5) if isinstance(focus, (int, float)) else (focus[0], focus[1])
        vf = vf.replace(f"crop={w}:{h}", f"crop={w}:{h}:x=(iw-ow)*{fx}:y=(ih-oh)*{fy}", 1)
    pre = ""
    fz = seg.get("freeze")
    if fz:  # play up to `at` seconds (source time), then hold that frame
        pre += f"trim=end={fz['at']},setpts=PTS-STARTPTS,"
    if seg.get("speed"):  # honest slow motion for very short clips (0.5-0.8)
        pre += f"setpts=PTS/{seg['speed']},"
    if fz:
        pre += f"tpad=stop_mode=clone:stop_duration={dur + 1},"
    m = seg.get("magnify")
    if m:  # "magnifier": a box of the full-resolution frame shown large over the blurred, darkened shot
        x0, y0, x1, y1 = m["box"]
        mw = int(w * m.get("width", 0.7)) // 2 * 2
        my = int(h * m.get("y", 0.31))
        vf = (f"split=2[ma][mb];[ma]{vf},boxblur=16:2,eq=brightness=-0.22[mbg];"
              f"[mb]crop=iw*{x1 - x0}:ih*{y1 - y0}:iw*{x0}:ih*{y0},scale={mw}:-2:flags=lanczos,"
              f"drawbox=x=0:y=0:w=iw:h=ih:color=0xFF1F8E@1:t=8[mz];[mbg][mz]overlay=(W-w)/2:{my}")
    vf = pre + vf
    z = seg.get("zoom")
    if z:  # smooth punch-in toward (x, y) starting at `at`
        at, ramp, to = z.get("at", 0), max(0.1, z.get("dur", 0.5)), z.get("to", 1.4)
        ze = f"if(lt(t,{at}),1,min({to},1+({to}-1)*(t-{at})/{ramp}))"  # per-frame scale + crop (zoompan buffered)
        vf += (f",scale=w='trunc({w}*{ze}/2)*2':h='trunc({h}*{ze}/2)*2':eval=frame,"
               f"crop={w}:{h}:x='max(0,min(iw-{w},{z['x']}*iw-{w}/2))':y='max(0,min(ih-{h},{z['y']}*ih-{h}/2))'")
    return vf


def shots_background(i, seg, dur, w, h, work, base):
    """Pacing: a segment with "shots" ([{"media", "start", "focus"?, "gamma"?}, ...]) gets a background that cuts between
    them, evenly across the narration (or by each shot's "dur"). Silent; clip audio is never used."""
    shots = seg["shots"]
    fixed = sum(x.get("dur", 0) for x in shots)
    free = [x for x in shots if not x.get("dur")]
    each = max(0.6, (dur + 0.3 - fixed) / max(1, len(free)))
    parts = []
    for k, sh in enumerate(shots):
        d = sh.get("dur") or each
        m = Path(sh["media"])
        m = m if m.is_absolute() else (base / m).resolve()
        fx = sh.get("focus", seg.get("focus", 0.5))
        sp = sh.get("speed", 1.0)
        st = sh.get("start", 0)
        cut = [c for c in scene_cuts(str(m)) if st + 0.05 < c < st + d * sp]
        if cut or any(abs(c - st) < 0.05 for c in scene_cuts(str(m))):
            print(f"  ! segment {i} shot {k}: {m.name} changes shot at {(cut or [st])[0]:.1f}s inside this shot; "
                  f"check the picture matches the narration")
        out = work / f"shot_{i}_{k}.mp4"
        # a still loops with -loop 1 and a finite -t (with -stream_loop its timestamps never advance and ffmpeg never ends)
        src = (["-loop", "1", "-framerate", str(FPS), "-t", f"{d + 0.5:.2f}", "-i", str(m)] if m.suffix.lower() in IMAGE_EXT
               else ["-ss", f"{sh.get('start', 0):.2f}", "-stream_loop", "-1", "-i", str(m)])
        still = m.suffix.lower() in IMAGE_EXT
        # stills drift sideways (~60 px over the shot) so every shot moves, like the single-image Ken Burns
        cx = f"'clip((iw-ow)*{fx}-30+60*t/{d:.2f},0,iw-ow)'" if still else f"(iw-ow)*{fx}"
        run(["ffmpeg", "-y", "-v", "error", *src,
             "-vf", f"setpts=PTS/{sp},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}:x={cx}:y=(ih-oh)/2,"
                    f"eq=brightness=-0.04:saturation=1.15:gamma={sh.get('gamma', 1.0)},setsar=1,fps={FPS}",
             "-t", f"{d:.2f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(out)])
        parts.append(out)
    lst = work / f"shots_{i}.txt"
    lst.write_text("".join(f"file '{x}'\n" for x in parts))
    bg = work / f"shots_{i}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(bg)])
    return bg


_CUTS = {}


def scene_cuts(media):
    """Times (s) where a source clip cuts to a different shot (cached)."""
    if media not in _CUTS:
        r = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(media), "-vf", "select='gt(scene,0.3)',showinfo",
                            "-f", "null", "-"], capture_output=True, text=True)
        _CUTS[media] = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    return _CUTS[media]


def warn_scene_cut(i, seg, dur):
    """A background that runs past a cut inside its clip can show something the narration isn't about."""
    m = seg.get("media")
    if not m or Path(m).suffix.lower() not in VIDEO_EXT or seg.get("freeze") or not Path(m).exists():
        return
    st = seg.get("media_start") or 0
    span = dur * seg.get("speed", 1.0)
    hit = [c for c in scene_cuts(m) if st + 0.3 < c < st + span]
    if hit:
        print(f"  ! segment {i}: background crosses a shot change in {Path(m).name} at {hit[0]:.1f}s; "
              f"check it still shows what the narration says (or use shots/speed)")


def chart_words(chart):
    """The words a chart shows besides names and numbers (label, note, the VS label): what needs a Spanish `chart_es`."""
    return [x for x in (chart.get("label"), chart.get("note"), (chart.get("vs") or {}).get("label"),
                        chart.get("text"), chart.get("who")) if x]


def render_segment(i, seg, audio, w, h, vertical, work, enc):
    voice_dur = duration(audio)
    # "pad": seconds held after the line (default 0.45); "hard_cut": no dip to black between segments. Montage Shorts
    # (Nov 22, "match the energy" of the top GTA 6 montages) use pad ~0.1 + hard cuts so the pictures change on the beat.
    # Shorts default to the montage energy (Nov 22, owner: "match the energy"): 0.2 s after each line and hard cuts;
    # long videos keep 0.45 s and the soft dip between segments. A segment can still set either key itself.
    dur = round(voice_dur + float(seg.get("pad", 0.2 if vertical else 0.45)), 2)
    warn_scene_cut(i, seg, dur)
    if seg.get("chart"):  # our own animated graphic (studio/charts.py): original visuals, not reused footage
        from . import charts
        chart = seg["chart"]
        if seg.get("_lang") == "es":  # Nov 22: Spanish Shorts showed the English labels/notes and 3,790.5-style numbers
            chart = dict(seg.get("chart_es") or chart)
            chart.setdefault("locale", "es")
            if not seg.get("chart_es") and chart_words(chart) and chart.get("locale") == "es" and \
                    not seg["chart"].get("locale") == "es":
                print(f"  ! segment {i}: Spanish render shows the English chart text {chart_words(chart)}; add `chart_es`")
        seg = dict(seg, media=str(charts.render(chart, dur + 0.5, w, h, work / f"chart_{i}.mp4", seed=i)),
                   media_start=0, focus=None)
    if seg.get("shots"):
        seg = dict(seg, media=str(shots_background(i, seg, dur, w, h, work, Path(seg.get("_base", ".")))),
                   media_start=0, focus=None)
    media = seg.get("media")
    if media and not Path(media).exists():
        print(f"  ! media not found, using generated background: {media}")
        media = None
    vin, vf = visual_input(media, dur, w, h, i, work, seg.get("media_start"))
    vf = seg_effects(seg, vf, w, h, dur)
    ov = work / f"ov_{i}.png"
    brand.headline_card(seg.get("headline", ""), w, h, vertical, seg.get("cta")).save(ov)
    lang = seg.get("_lang", "en")
    times = align_words(seg["text"], audio, lang) if seg.get("_align", True) else None
    seg["_aligned"] = bool(times)
    subs = caption_file(seg["text"], 0.2, dur, work / f"cap_{i}.ass", w, h, vertical, times=times, lang=lang)
    out = work / f"seg_{i:02d}.mp4"
    hard = bool(seg.get("hard_cut", vertical))
    fade_in = "" if (vertical and i == 0) or hard else "fade=t=in:st=0:d=0.25,"  # a Short's first frame is its cover
    fade_out = "null" if hard else f"fade=t=out:st={dur - 0.25}:d=0.25"
    extra, co = [], ""
    if seg.get("callout"):
        c = seg["callout"]
        extra = ["-loop", "1", "-i", str(callout_png(c, w, h, work / f"callout_{i}.png"))]
        co = f"[c0];[c0][3:v]overlay=0:0:enable='gte(t,{c.get('at', 0)})'"
    fc = (f"[0:v]{vf},setsar=1,fps={FPS}[bg];[bg][1:v]overlay=0:0{co},"
          f"subtitles='{subs}':fontsdir='{brand.FONTS}',"
          f"{fade_in}{fade_out}[v];"
          f"[2:a]adelay=200|200,apad,atrim=0:{dur},aformat=sample_rates=48000:channel_layouts=stereo[a]")
    run(["ffmpeg", "-y", "-v", "error", *vin, "-loop", "1", "-i", str(ov), "-i", str(audio), *extra,
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


STING = ROOT / "assets" / "intro" / "sting.mp4"  # AI-made neon flythrough (Everygen, Nov 20): graphics only, no text


def intro_overlay(title, w, h, path):
    """Wordmark + title on a transparent layer, for the animated intro."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(Image.new("RGBA", (w, h), (0, 0, 0, 70)))
    wm = brand.wordmark(int(h * 0.13))
    img.alpha_composite(wm, ((w - wm.width) // 2, int(h * 0.26)))
    f, lines = brand.fit_lines(title.upper(), brand.HEADLINE_FONT, int(w * 0.85), int(h * 0.06), 30)
    d = ImageDraw.Draw(img)
    y = int(h * 0.26) + wm.height + int(h * 0.04)
    for ln in lines:
        d.text(((w - f.getlength(ln)) / 2, y), ln, font=f, fill=brand.WHITE, stroke_width=5, stroke_fill=brand.NIGHT)
        y += int(f.size * 1.15)
    img.save(path)
    return path


def render_intro(title, work, enc, w, h, dur=3.0):
    """Long-video intro: the animated neon sting under the wordmark and title (falls back to the still card)."""
    if not STING.exists():
        return render_card("intro", intro_image(title, w, h, work / "intro.png"), 2.6, work, enc, w, h)
    ov = intro_overlay(title, w, h, work / "intro_overlay.png")
    out = work / "intro.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(STING), "-loop", "1", "-t", str(dur), "-i", str(ov),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex",
         f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={FPS}[bg];"
         f"[1:v]format=rgba,fade=t=in:st=0.35:d=0.45:alpha=1[o];[bg][o]overlay=0:0:eof_action=pass,"
         f"fade=t=out:st={dur - 0.35}:d=0.35[v]",
         "-map", "[v]", "-map", "2:a", "-t", str(dur), *enc, str(out)])
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


def mix_audio(video, music, sfx, out, enc_audio, music_level=0.16):
    """Voice + music bed that ducks under the voice (sidechain) + sound effects."""
    total = duration(video)
    ins = ["-i", str(video)]
    fc = "[0:a]asplit=2[v][key];"
    mixin = "[v]"
    n = 1
    if music:
        ins += ["-stream_loop", "-1", "-i", str(music)]
        fc += (f"[{n}:a]volume={music_level},afade=t=in:d=0.8,afade=t=out:st={max(0, total - 2.5)}:d=2.5,"
               f"atrim=0:{total},aformat=sample_rates=48000:channel_layouts=stereo[mraw];"
               f"[mraw][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[m];")
        mixin += "[m]"
        n += 1
    else:
        fc += "[key]anullsink;"
    if sfx:
        ins += ["-i", str(sfx)]
        fc += f"[{n}:a]volume=0.55,aformat=sample_rates=48000:channel_layouts=stereo[s];"
        mixin += "[s]"
        n += 1
    fc += f"{mixin}amix=inputs={n}:duration=first:normalize=0[a]"
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", *enc_audio, str(out)])


def fmt_ts(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def build(ep, base, slug, segments, vertical, preview, enc, w, h, voice, rate, name):
    """Render one video (main or a Short) and return (final_path, chapters, used_footage)."""
    out_dir = ROOT / "output" / slug
    work = out_dir / (f"work_{name}" if vertical else "work")
    work.mkdir(parents=True, exist_ok=True)
    # Footage library: every file in media/ (official screenshots, trailer clips, your gameplay).
    # Segments without their own "media" rotate through it; "media": "none" keeps the neon background.
    library = sorted(p for p in (ROOT / "media").rglob("*")
                     if p.suffix.lower() in VIDEO_EXT | IMAGE_EXT and "raw" not in p.parts)
    # The owner's own gameplay is the best stock footage: Shorts use it for every segment whenever highlights
    # exist (newest first), unless a segment sets "keep_media": true or the episode sets "use_gameplay": false.
    gameplay = sorted((p for p in (ROOT / "media" / "gameplay").glob("*") if p.suffix.lower() in VIDEO_EXT),
                      key=lambda p: p.stat().st_mtime, reverse=True) if (ROOT / "media" / "gameplay").exists() else []
    # YouTube limits ads on graphic violence in a video's first 7 seconds, so the opening segment only uses calm
    # gameplay (Drive folders "Scenery & cars", "Funny & fails", "Glitches"); otherwise it keeps its own picture.
    calm = set()
    done_file = ROOT / "media" / "gameplay" / "processed.json"
    if done_file.exists():
        for hs in json.loads(done_file.read_text()).values():
            for h in hs:
                if h.get("category") in ("Scenery & cars", "Funny & fails", "Glitches"):
                    calm.add(Path(h["file"]).name)
    calm_clips = [p for p in gameplay if p.name in calm]
    if vertical and gameplay and ep.get("use_gameplay", True):
        g = 0
        for idx, s in enumerate(segments):
            if s.get("keep_media") or s.get("media") == "none":
                continue
            if idx == 0:
                if calm_clips:
                    s["media"], s["media_start"] = str(calm_clips[0]), None
                continue
            s["media"] = str(gameplay[g % len(gameplay)])
            s["media_start"] = None
            g += 1
        print(f"  using {min(g, len(gameplay))} of the owner's gameplay clips as Short backgrounds (opening kept calm)")
    elif gameplay:
        library = [p for p in gameplay if p not in calm_clips] + [p for p in library if p not in gameplay]
        if segments and not segments[0].get("media") and calm_clips:
            segments[0]["media"] = str(calm_clips[0])
    k = 0
    for s in segments:
        s["_base"] = str(base)
        if s.get("media") == "none":
            s["media"] = None
        elif s.get("media"):
            s["media"] = str((base / s["media"]).resolve()) if not Path(s["media"]).is_absolute() else s["media"]
        elif library:
            s["media"] = str(library[(k + len(slug)) % len(library)])
            k += 1
    used_footage = any(s.get("media") for s in segments)
    if vertical and segments and ep.get("follow_cta", True):
        es = any(s.get("text") == s.get("text_es") for s in segments if s.get("text_es"))
        segments[-1]["cta"] = "SÍGUENOS: GTA 6 A DIARIO" if es else "FOLLOW FOR DAILY GTA 6"

    parts, chapters, t = [], [], 0.0
    cuts, impacts, timings = [], [0.0], []  # sound effects: impact on the hook, whoosh on every cut
    if not vertical:
        intro = render_intro(ep["title"], work, enc, w, h)
        parts.append(intro)
        t += duration(intro)
    for i, seg in enumerate(segments):
        print(f"[{i + 1}/{len(segments)}] {seg.get('headline') or seg['text'][:40]}")
        audio = tts(seg["text"], voice, rate, work / f"vo_{i:02d}")
        clip, d = render_segment(i, seg, audio, w, h, vertical, work, enc)
        if seg.get("chapter") or seg.get("headline"):
            chapters.append((0.0 if i == 0 and vertical else t, seg.get("chapter") or seg["headline"]))
        if t > 0:
            cuts.append(t)
        timings.append({"start": round(t + 0.2, 2), "end": round(t + d - 0.25, 2), "text": seg["text"],
                        "text_es": seg.get("text_es", "")})
        parts.append(clip)
        t += duration(clip)
    if not vertical:
        cuts.append(t)
        outro = render_card("outro", outro_image(ep.get("outro_card", "New GTA 6 videos every week"), w, h,
                                                 work / "outro.png"), 4.0, work, enc, w, h)
        parts.append(outro)

    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    raw = work / "joined.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(raw)])
    final = out_dir / f"{name}{'-preview' if preview else ''}.mp4"
    # Music: the episode's "music" file, else the first track in assets/music/, else the original theme
    # (generated on first use). "music": "none" turns it off; "sfx": false turns sound effects off.
    from . import sound
    music = ep.get("music")
    if music == "none":
        music = None
    elif music:
        music = base / music
    else:
        # Nov 22 (owner: "better audio that connects"): a track per mood instead of one song on every video.
        # "mood" on the episode, else by format; our own generated synthwave, so no Content ID risk.
        mood = ep.get("mood") or {"news": "hype", "comparison": "tension", "ranking": "tension", "quiz": "bright",
                                  "details": "bright"}.get(ep.get("format"), "night")
        lib_dir = ROOT / "assets" / "music"
        if mood == "night" or mood not in sound.MOODS:
            music = lib_dir / "vice-replay-theme.wav"
            if not music.exists():
                music = sound.theme(music)
        else:
            music = next((p for p in (lib_dir / f"vr-{mood}.m4a", lib_dir / f"vr-{mood}.wav") if p.exists()), None) \
                or sound.theme(lib_dir / f"vr-{mood}.wav", loops=3, seed=11, mood=mood)
        print(f"music: {Path(music).name} (mood {mood})")
    sfx = None
    if ep.get("sfx", True):
        sfx = sound.sfx_track(work / "sfx.wav", duration(raw), cuts, impacts)
    mixed = work / "mixed.mp4"
    mix_audio(raw, music if music and Path(music).exists() else None, sfx, mixed, ["-c:a", "aac", "-b:a", "192k"])
    # YouTube plays back at about -14 LUFS; normalize so the voice isn't quiet next to other videos
    run(["ffmpeg", "-y", "-v", "error", "-i", str(mixed), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", str(final)])  # index at the front: phones and in-app previews open it at once
    # segment timings, so subtitles in other languages can be lined up with the narration
    (out_dir / f"{name}.timings.json").write_text(json.dumps(timings, indent=2))
    return final, chapters, used_footage


def affiliate_block(ep):
    """Amazon affiliate links + required disclosure (content/affiliate.json). Episode `affiliate`: list of set
    names, or [] to leave links out."""
    cfg_path = ROOT / "content" / "affiliate.json"
    if not cfg_path.exists():
        return []
    cfg = json.loads(cfg_path.read_text())
    if not cfg.get("enabled"):
        return []
    names = ep.get("affiliate", cfg.get("default_sets", []))
    items = [it for n in names for it in cfg["sets"].get(n, [])]
    if not items:
        return []
    sep = lambda u: "&" if "?" in u else "?"
    lines = [cfg["heading"]] + [f"{label}: {url}{sep(url)}tag={cfg['tag']}" for label, url in items]
    return lines + [cfg["disclosure"], ""]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode")
    ap.add_argument("--short", action="store_true", help="vertical 1080x1920 YouTube Short")
    ap.add_argument("--preview", action="store_true", help="fast low-res draft")
    ap.add_argument("--voice", help=f"edge-tts voice (default {DEFAULT_VOICE})")
    ap.add_argument("--es", action="store_true", help="Spanish-voiced Shorts (free Kokoro em_alex voice, text_es; files end in -es)")
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
    # Channel voice (config/channel.json "voice", owner Nov 22: "use the best voice rated" = Kokoro af_heart, grade A)
    # wins over the episode's own "voice" (39 old episodes say am_michael, grade C+) unless it sets "voice_override".
    voice = a.voice or ep.get("voice_override") or channel_setting("voice") or ep.get("voice", DEFAULT_VOICE)
    rate = ep.get("rate", "+8%")

    out_dir = ROOT / "output" / slug
    if vertical:
        # "shorts": list of {"id", "title", "description", "segments"}; the legacy "short" is the main-cut Short
        shorts = ([{"id": "", "title": ep.get("short_title", ""), "description": ep.get("short_description", ""),
                    "segments": ep["short"]}] if ep.get("short") else []) + ep.get("shorts", [])
        if not shorts:
            sys.exit("No 'short' or 'shorts' in this episode.")
        if a.es:
            voice = a.voice or ep.get("voice_es") or channel_setting("voice_es") or "em_alex"
            es_shorts = []
            for k, sh in enumerate(shorts):
                es = sh.get("es") or (ep.get("short_es") if k == 0 and not sh.get("id") else None) or {}
                if not all(x.get("text_es") for x in sh["segments"]):
                    print(f"skip Spanish {sh.get('id') or 'short'}: a segment has no text_es")
                    continue
                segs = [dict(x, text=x["text_es"], headline=x.get("headline_es") or x.get("headline"), _lang="es")
                        for x in sh["segments"]]
                es_shorts.append(dict(sh, segments=segs, title=es.get("title") or sh.get("title"),
                                      description=es.get("description") or sh.get("description"), lang_suffix="-es"))
            shorts = es_shorts
        for sh in shorts:
            name = f"{slug}-short" + (f"-{sh['id']}" if sh.get("id") else "") + sh.get("lang_suffix", "")
            print(f"== Short: {name}")
            final, _, used = build(ep, base, slug, sh["segments"], True, a.preview, enc, w, h, voice, rate, name)
            tags = " ".join("#" + t for t in sh.get("hashtags", ["GTA6", "GTAVI", "Shorts"]))
            lines = ["TITLE", sh.get("title") or ep["title"], "", "DESCRIPTION", sh.get("description", ""), ""]
            if used:
                lines += ["Imágenes de GTA VI: Rockstar Games, usadas para noticias y comentario." if a.es else
                          "GTA VI footage/screenshots: Rockstar Games, used for news and commentary.", ""]
            # cross-promotion (Nov 22): every English Short points Spanish speakers to the sister channel
            lines += ["🇺🇸 Vice Replay in English: https://www.youtube.com/@ViceReplayTV-q8s" if a.es else
                      "🇪🇸 Vice Replay en Español: https://www.youtube.com/channel/UCWPnqYqYu9_CLsJ8Bk1MPgQ", ""]
            lines += ["Vice Replay es un canal de fans, no afiliado con Rockstar Games." if a.es else
                      "Vice Replay is a fan channel, not affiliated with Rockstar Games.", "", tags]
            (out_dir / f"{name}.txt").write_text("\n".join(lines))
            print(f"Done: {final}  ({fmt_ts(duration(final))})")
        return
    final, chapters, used_footage = build(ep, base, slug, ep["segments"], False, a.preview, enc, w, h, voice,
                                          rate, slug)
    out_dir = ROOT / "output" / slug
    if not vertical:
        # Thumbnails: 3 versions for YouTube Studio's "Test & Compare" (A/B/C). Same text, different picture:
        # A = thumbnail.image (or the first screenshot used in the video), B = another screenshot, C = neon art.
        th = ep.get("thumbnail", {})
        pics = [str(base / th["image"])] if th.get("image") else []
        pics += [s["media"] for s in ep["segments"] if s.get("media") and Path(s["media"]).suffix.lower() in IMAGE_EXT]
        pics += [str(base / p) for p in th.get("images", [])]
        pics = list(dict.fromkeys(str(Path(x).resolve()) for x in pics))  # same file, different spelling -> once
        backgrounds = (pics[:2] + [None]) if pics else [None]
        for label, bg in zip("abc", backgrounds):
            brand.thumbnail(th.get("line1", ep["title"]), th.get("line2", ""), th.get("tag", ""),
                            out_dir / f"thumbnail-{label}.jpg", bg_image=bg)
        shutil.copy(out_dir / "thumbnail-a.jpg", out_dir / "thumbnail.jpg")
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
        if used_footage:
            desc += ["Grand Theft Auto VI footage and screenshots: Rockstar Games, used for news and commentary.", ""]
        if ep.get("sources"):
            desc += ["SOURCES"] + ep["sources"] + [""]
        desc += affiliate_block(ep)
        desc += ["Subscribe to Vice Replay for GTA's wildest moments. On replay.", "",
                 "Vice Replay is a fan channel and is not affiliated with Rockstar Games or Take-Two Interactive.", "",
                 " ".join("#" + tg.replace(" ", "") for tg in ep.get("hashtags", ["GTA6", "GTAVI", "ViceCity"]))]
        (out_dir / "description.txt").write_text("\n".join(desc))
        (out_dir / "tags.txt").write_text(", ".join(ep.get("tags", [])))
    print(f"\nDone: {final}  ({fmt_ts(duration(final))})")


if __name__ == "__main__":
    main()
