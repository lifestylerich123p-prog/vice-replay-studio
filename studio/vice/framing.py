"""Vertical framing for 16:9 streams and gameplay (free, local: OpenCV + ffmpeg).

Layouts (1080x1920):
- stack: streamer webcam on top, gameplay below; each region cropped to fill its panel (no empty bars).
- pip:   gameplay fills the frame (action-tracked crop), webcam as a framed inset at the top.
- blur:  the whole 16:9 frame over a blurred fill of itself (nothing cropped; replaces plain letterboxing).
- fill:  action-tracked 9:16 crop (the crop follows where the motion is, smoothed so it never jitters).

Boxes are normalized [x, y, w, h] of the source frame. Manual boxes always win; otherwise detect_facecam() finds
the webcam: YuNet face detections that stay in the same place across sampled frames (a webcam doesn't move,
gameplay faces do), expanded to a webcam-shaped box and snapped to the overlay's edges when they're visible.
`keep` boxes (e.g. a campaign's required logo overlay) are kept on screen: if a crop would cut one off, it is
composited back as a small inset in the same corner.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

from . import db

W, H = 1080, 1920
MODEL = db.ROOT / "assets" / "models" / "face_detection_yunet_2023mar.onnx"  # OpenCV zoo, MIT licence


def probe(src):
    out = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=width,height:format=duration", "-of", "json", str(src)],
                                    capture_output=True, text=True).stdout)
    return out["streams"][0]["width"], out["streams"][0]["height"], float(out["format"]["duration"])


def sample_frames(src, n=12, width=640, start=0.0, end=None):
    """n evenly spaced frames (RGB uint8, `width` wide) in one ffmpeg call per frame-set."""
    sw, sh, dur = probe(src)
    end = min(end or dur, dur)
    h = int(round(width * sh / sw / 2) * 2)
    frames = []
    for i in range(n):
        t = start + (end - start) * (i + 0.5) / n
        raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
                              "-vf", f"scale={width}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        if len(raw) == width * h * 3:
            frames.append(np.frombuffer(raw, np.uint8).reshape(h, width, 3))
    return frames


def faces(frame):
    import cv2
    try:
        cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
    except AttributeError:
        pass
    h, w = frame.shape[:2]
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (w, h), score_threshold=0.75)
    _, res = det.detect(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    return [] if res is None else [(r[0] / w, r[1] / h, r[2] / w, r[3] / h, float(r[14])) for r in res]


def _persistent_gradients(frames):
    import cv2
    gxs, gys = [], []
    for f in frames[:8]:
        g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32)
        gxs.append(np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)))
        gys.append(np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)))
    return np.min(gxs, axis=0), np.min(gys, axis=0)  # an edge counts only if it is in every frame


def _webcam_from_stillness(frames, cx, cy, fw, fh):
    """A webcam is a region that barely changes while the gameplay around it changes all the time (measured on a
    real Lacy stream: pixel std 2.4 inside the webcam vs 40.7 in gameplay). Grow a box from the face while the
    strip just outside it stays still; stop where gameplay starts or at the frame edge. Returns None if implausible."""
    g = np.stack([f.mean(axis=2) for f in frames[:12]]).astype(np.float32)
    sd = g.std(axis=0)
    h, w = sd.shape
    thr = 0.45 * float(np.median(sd))
    if thr < 4:  # the whole picture is nearly static (menu, paused game): stillness can't separate the webcam
        return None
    x0, x1 = max(0, int((cx - fw / 2) * w)), min(w - 1, int((cx + fw / 2) * w))
    y0, y1 = max(0, int((cy - fh / 2) * h)), min(h - 1, int((cy + fh / 2) * h))
    for _ in range(2 * (w + h)):
        grew = False
        if x0 > 0 and sd[y0:y1 + 1, x0 - 1].mean() < thr:
            x0 -= 1; grew = True
        if x1 < w - 1 and sd[y0:y1 + 1, x1 + 1].mean() < thr:
            x1 += 1; grew = True
        if y0 > 0 and sd[y0 - 1, x0:x1 + 1].mean() < thr:
            y0 -= 1; grew = True
        if y1 < h - 1 and sd[y1 + 1, x0:x1 + 1].mean() < thr:
            y1 += 1; grew = True
        if not grew:
            break
    bw, bh = (x1 - x0 + 1) / w, (y1 - y0 + 1) / h
    if bw * bh < 2.5 * fw * fh or bw * bh > 0.45 or bw < 1.2 * fw or bh < 1.2 * fh:
        return None
    return (x0 / w, y0 / h, bw, bh)


def _webcam_from_face(frames, cx, cy, fw, fh):
    """From the face, search outward on each side for the nearest strong PERSISTENT border (webcam overlays have
    one; gameplay edges move). Sides without a border fall back to head-and-shoulders proportions."""
    gx, gy = _persistent_gradients(frames)
    h, w = gx.shape
    rows = slice(max(0, int((cy - 1.2 * fh) * h)), min(h, int((cy + 1.2 * fh) * h)) or 1)
    cols = slice(max(0, int((cx - 1.5 * fw) * w)), min(w, int((cx + 1.5 * fw) * w)) or 1)
    colprof, rowprof = gx[rows].mean(axis=0), gy[:, cols].mean(axis=1)

    def edge(profile, lo, hi, n, default, nearest_first):
        lo, hi = max(1, int(lo * n)), min(n - 2, int(hi * n))
        if hi <= lo:
            return default, False
        seg = profile[lo:hi]
        base = np.median(profile) + 1e-3
        strong = np.where(seg > max(3 * base, 0.5 * seg.max()))[0]
        if not len(strong) or seg.max() < 3 * base:
            return default, False
        i = strong[-1] if nearest_first else strong[0]  # the border closest to the face
        return (lo + i) / n, True

    left, a = edge(colprof, cx - 2.8 * fw, cx - 0.7 * fw, w, max(0.0, cx - 1.7 * fw), True)
    right, b = edge(colprof, cx + 0.7 * fw, cx + 2.8 * fw, w, min(1.0, cx + 1.7 * fw), False)
    top, c = edge(rowprof, cy - 2.0 * fh, cy - 0.65 * fh, h, max(0.0, cy - 1.1 * fh), True)
    bottom, d = edge(rowprof, cy + 0.65 * fh, cy + 2.0 * fh, h, min(1.0, cy + 1.4 * fh), False)
    return (left, top, right - left, bottom - top), int(a) + int(b) + int(c) + int(d)


def detect_facecam(src, n=12, start=0.0, end=None):
    """Webcam box or None. A face counts as the webcam when it appears in the same spot in most sampled frames."""
    frames = sample_frames(src, n, start=start, end=end)
    hits = []
    for f in frames:
        for fx, fy, fw, fh, score in faces(f):
            hits.append((fx + fw / 2, fy + fh / 2, fw, fh))
    if not hits or not frames:
        return None
    pts = np.array(hits)
    best, members = None, []
    for c in pts:  # densest cluster of face centres (static webcam)
        near = pts[np.hypot(pts[:, 0] - c[0], pts[:, 1] - c[1]) < 0.05]
        if len(near) > len(members):
            best, members = c, near
    if len(members) < max(3, int(0.5 * len(frames))):
        return None
    cx, cy, fw, fh = np.median(members, axis=0)
    still = _webcam_from_stillness(frames, cx, cy, fw, fh)
    if still:
        box, snapped, method = still, 4, "stillness"
    else:
        box, snapped = _webcam_from_face(frames, cx, cy, fw, fh)
        method = "edges"
    return {"box": [round(float(v), 4) for v in box], "face": [round(float(cx), 4), round(float(cy), 4)],
            "frames_with_face": int(len(members)), "frames": len(frames), "edges_snapped": snapped, "method": method,
            "confidence": round(len(members) / len(frames), 2)}


def action_track(src, exclude=None, n=24, start=0.0, end=None, crop_w=0.5625):
    """Smoothed horizontal centre of the action over time: list of (t, cx) (cx normalized).
    Motion energy between consecutive samples, webcam masked out, with a gentle centre prior."""
    sw, sh, dur = probe(src)
    end = min(end or dur, dur)
    frames = sample_frames(src, n, width=320, start=start, end=end)
    if len(frames) < 3:
        return [(0.0, 0.5)]
    h, w = frames[0].shape[:2]
    prior = np.exp(-((np.arange(w) - w / 2) ** 2) / (2 * (0.35 * w) ** 2))
    pts = []
    for i in range(1, len(frames)):
        diff = np.abs(frames[i].astype(np.int16) - frames[i - 1].astype(np.int16)).sum(axis=2).astype(np.float32)
        if exclude:
            ex, ey, ew, eh = exclude
            diff[int(ey * h):int((ey + eh) * h), int(ex * w):int((ex + ew) * w)] = 0
        col = diff.sum(axis=0) * prior
        win = max(3, int(crop_w * sh / sw * w))  # crop window width in sample pixels
        energy = np.convolve(col, np.ones(win), mode="valid")
        cx = (int(np.argmax(energy)) + win / 2) / w if energy.size else 0.5
        if energy.size and energy.max() < 1.15 * energy.mean():  # motion everywhere (camera moving): no clear
            cx = 0.5                                               # subject, so stay centred instead of chasing texture
        t = (end - start) * i / (len(frames) - 1)
        pts.append((t, cx))
    smooth, prev = [], pts[0][1]
    for t, cx in pts:  # exponential smoothing + speed limit (max 8% of width per second of video)
        step = (end - start) / max(1, len(pts))
        prev = prev + max(-0.08 * step, min(0.08 * step, 0.35 * (cx - prev)))
        smooth.append((round(t, 2), round(prev, 4)))
    return smooth


def _piecewise(track, crop_frac):
    """ffmpeg expression for a crop x that follows the track (piecewise linear in t)."""
    xs = [(t, min(max(cx - crop_frac / 2, 0.0), 1 - crop_frac)) for t, cx in track]
    if len(xs) == 1:
        return f"{xs[0][1]:.4f}*iw"
    expr = f"{xs[-1][1]:.4f}"
    for (t0, x0), (t1, x1) in reversed(list(zip(xs[:-1], xs[1:]))):
        expr = f"if(lt(t,{t1}),{x0:.4f}+({x1:.4f}-{x0:.4f})*(t-{t0})/{max(0.01, t1 - t0)},{expr})"
    return f"({expr})*iw"


def crop_expr(box):
    x, y, w, h = box
    return f"crop=trunc(iw*{w}/2)*2:trunc(ih*{h}/2)*2:iw*{x}:ih*{y}"


def fit_box(box, aspect, sw, sh, center=None):
    """Grow/shrink `box` (normalized) to the panel aspect (w/h in pixels), staying inside the frame."""
    x, y, w, h = box
    cx, cy = center or (x + w / 2, y + h / 2)
    pw, ph = w * sw, h * sh
    if pw / ph > aspect:
        pw = ph * aspect
    else:
        ph = pw / aspect
    nw, nh = pw / sw, ph / sh
    nx, ny = min(max(0.0, cx - nw / 2), 1 - nw), min(max(0.0, cy - nh / 2), 1 - nh)
    return [round(nx, 4), round(ny, 4), round(nw, 4), round(nh, 4)]


def build(src, layout, cam=None, game=None, keep=(), cam_height=0.40, start=0.0, end=None, track=None):
    """filter_complex body that reads [0:v] and ends in [vout] (1080x1920), plus a description dict."""
    sw, sh, _ = probe(src)
    info = {"layout": layout, "source": [sw, sh], "cam": cam, "game": game, "keep": list(keep)}
    if layout in ("stack", "pip") and not cam:
        layout = "blur" if layout == "stack" else "fill"
        info["fallback"] = f"no webcam box: used {layout}"
    if layout == "blur":
        fc = (f"[0:v]split=2[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,"
              f"eq=brightness=-0.12[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=0:(H-h)/2[vout]")
    elif layout == "fill":
        frac = (sh * W / H) / sw  # 9:16 window as a fraction of the source width
        track = track or action_track(src, exclude=cam, start=start, end=end, crop_w=frac)
        info["track"] = track
        fc = (f"[0:v]crop=w=trunc(ih*{W}/{H}/2)*2:h=ih:x='{_piecewise(track, frac)}':y=0,scale={W}:{H}[vout]")
    elif layout == "stack":
        top = int(H * cam_height) // 2 * 2
        cam_box = fit_box(cam, W / top, sw, sh)
        bottom = H - top
        if game:
            game_box = fit_box(game, W / bottom, sw, sh)
        else:  # gameplay panel: as tall as the frame allows, centred on the action, webcam excluded
            gh = 1.0
            gw = min(1.0, (W / bottom) * gh * sh / sw)
            track = track or action_track(src, exclude=cam, start=start, end=end, crop_w=gw)
            cx = float(np.median([c for _, c in track]))
            game_box = fit_box([0, 0, 1, 1], W / bottom, sw, sh, center=(cx, 0.5))
            gx0, gwid = game_box[0], game_box[2]
            if gx0 < cam[0] + cam[2] and cam[0] < gx0 + gwid:  # webcam inside the gameplay crop: slide away from it
                right = cam[0] + cam[2]
                left_room, right_room = cam[0], 1 - right
                if right_room >= gwid:
                    game_box[0] = round(max(right, min(gx0, 1 - gwid)), 4)
                elif left_room >= gwid:
                    game_box[0] = round(min(cam[0] - gwid, gx0), 4)
                info["webcam_excluded"] = right_room >= gwid or left_room >= gwid
        for kb in keep:  # a required overlay half-inside the crop: slide the crop to hold all of it if possible
            kx0, kx1 = kb[0], kb[0] + kb[2]
            gx0, gx1 = game_box[0], game_box[0] + game_box[2]
            if kx0 < gx1 and kx1 > gx0 and not (gx0 <= kx0 and kx1 <= gx1) and kb[2] <= game_box[2]:
                nx = kx1 - game_box[2] if kx1 > gx1 else kx0
                nx = min(max(0.0, nx), 1 - game_box[2])
                if abs(nx - gx0) <= 0.10 and not (nx < cam[0] + cam[2] and cam[0] < nx + game_box[2]):
                    game_box[0] = round(nx, 4)  # small slide only; a bigger one would push the action aside
        info.update(cam_box=cam_box, game_box=game_box)
        fc = (f"[0:v]split=2[c][g];[c]{crop_expr(cam_box)},scale={W}:{top}[ct];"
              f"[g]{crop_expr(game_box)},scale={W}:{bottom}[gb];[ct][gb]vstack=2[base];"
              f"[base]drawbox=x=0:y={top - 3}:w={W}:h=6:color=0xFF1F8E@1:t=fill[vout]")
    elif layout == "pip":
        frac = (sh * W / H) / sw
        track = track or action_track(src, exclude=cam, start=start, end=end, crop_w=frac)
        cam_box = fit_box(cam, 16 / 10, sw, sh)
        pw = int(W * 0.46) // 2 * 2
        info.update(cam_box=cam_box, track=track)
        fc = (f"[0:v]split=2[c][g];[g]crop=w=trunc(ih*{W}/{H}/2)*2:h=ih:x='{_piecewise(track, frac)}':y=0,"
              f"scale={W}:{H}[bg];[c]{crop_expr(cam_box)},scale={pw}:-2,pad=iw+12:ih+12:6:6:color=0xFF1F8E[ci];"
              f"[bg][ci]overlay=W-w-36:150[vout]")
    else:
        raise ValueError(f"unknown layout {layout}")
    for i, kb in enumerate(keep):  # required overlays (campaign logos) are always visible
        if layout == "stack":
            gb = info["game_box"]
            if gb[0] <= kb[0] and kb[0] + kb[2] <= gb[0] + gb[2] and gb[1] <= kb[1] and kb[1] + kb[3] <= gb[1] + gb[3]:
                info.setdefault("keep_in_crop", []).append(kb)
                continue  # already fully on screen
        kw = int(W * 0.30) // 2 * 2
        corner_x = "36" if kb[0] < 0.5 else "W-w-36"
        if layout == "pip":
            corner_x = "36"  # the webcam inset owns the top-right
        corner_y = "H-h-420" if kb[1] > 0.5 else (str(int(H * cam_height) + 24) if layout == "stack" else "300")
        fc = fc.replace("[vout]", f"[k{i}in]") + (f";[0:v]{crop_expr(kb)},scale={kw}:-2[k{i}];"
                                                    f"[k{i}in][k{i}]overlay={corner_x}:{corner_y}[vout]")
    info["layout_used"] = layout
    return fc, info


def render(src, out, layout="auto", cam=None, game=None, keep=(), start=0.0, end=None, audio=True):
    """Standalone framing render (no captions): used by tests and previews."""
    if layout == "auto":
        det = None if cam else detect_facecam(src, start=start, end=end)
        cam = cam or (det and det["box"])
        layout = "stack" if cam else "blur"
    fc, info = build(src, layout, cam=cam, game=game, keep=keep, start=start, end=end)
    sw, sh, dur = probe(src)
    end = min(end or dur, dur)
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src),
           "-filter_complex", fc.replace("t,", "t,", 1), "-map", "[vout]"]
    cmd += ["-map", "0:a?", "-c:a", "aac", "-b:a", "160k"] if audio else ["-an"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "30", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    info["output"] = str(out)
    return info


def make_stream_mock(out, game_clip, face_image, seconds=6, cam=(40, 700, 560, 340), logo=True):
    """Test fixture: a 1920x1080 'stream' = gameplay + a webcam inset (a face that moves slightly, framed like an
    OBS overlay) + an optional logo box. Returns the ground-truth boxes (normalized). Never for publishing."""
    from PIL import Image, ImageDraw
    cx, cy, cw, ch = cam
    face = Image.open(face_image).convert("RGB")
    fw, fh = face.size
    fx, fy, fbw, fbh, _ = max(faces(np.array(face.resize((640, int(640 * fh / fw))))), key=lambda f: f[2] * f[3])
    crop_w = fbw * fw * 3.2
    crop_h = crop_w * ch / cw
    left = min(max(0, (fx + fbw / 2) * fw - crop_w / 2), fw - crop_w)
    top = min(max(0, (fy + fbh / 2) * fh - crop_h * 0.42), fh - crop_h)
    tmp = Path(out).with_suffix(".cam.png")
    face.crop((int(left), int(top), int(left + crop_w), int(top + crop_h))).resize((cw, ch)).save(tmp)
    graph = (f"[0:v]scale=1920:1080,setsar=1[g];[1:v]scale={cw + 40}:{ch + 24},"
             f"crop={cw}:{ch}:x='20+12*sin(t*1.7)':y='12+8*sin(t*1.3)'[c];"
             f"[c]pad={cw + 12}:{ch + 12}:6:6:color=0x7A2BFF[cb];[g][cb]overlay={cx - 6}:{cy - 6}[s]")
    if logo:
        lg = Path(out).with_suffix(".logo.png")
        im = Image.new("RGBA", (300, 110), (255, 200, 0, 255))
        ImageDraw.Draw(im).text((20, 30), "SPONSOR LOGO", fill=(0, 0, 0, 255))
        im.save(lg)
        graph += f";[s][2:v]overlay=1580:30[v]"
    else:
        graph += ";[s]null[v]"
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(game_clip), "-loop", "1", "-i", str(tmp)]
    cmd += ["-loop", "1", "-i", str(lg)] if logo else []
    cmd += ["-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000", "-filter_complex", graph, "-map", "[v]",
            "-map", f"{3 if logo else 2}:a", "-t", str(seconds), "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt",
            "yuv420p", "-r", "30", "-c:a", "aac", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    truth = {"cam": [cx / 1920, cy / 1080, cw / 1920, ch / 1080]}
    if logo:
        truth["logo"] = [1580 / 1920, 30 / 1080, 300 / 1920, 110 / 1080]
    return truth


def iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    iy = max(0, min(ay + ah, by + bh) - max(ay, by))
    inter = ix * iy
    return inter / (aw * ah + bw * bh - inter)
