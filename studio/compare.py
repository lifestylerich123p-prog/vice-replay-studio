"""Split-screen comparison clip for "GTA 5 vs GTA 6" Shorts (free, ffmpeg).

    python -m studio.compare gta5.mp4 gta6.mp4 -o media/compare/car-jacking.mp4
    python -m studio.compare a.mp4 b.mp4 --top-label "GTA 5" --bottom-label "GTA 6" --top-start 12 --bottom-start 3 --seconds 6

Makes a silent 1080x1920 clip: the top half shows the first video (pink label), the bottom half the second (cyan
label), each cropped to the centre and played side by side for --seconds. Use it as a Short segment's background:
    {"media": "../media/compare/car-jacking.mp4", "keep_media": true, ...}
Best results: the same action in both games (steal a car, crash, swim, cops, the map), recorded by the owner with
radio and music off. Never use other creators' footage.
"""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "Anton.ttf"
W, HALF = 1080, 960
PINK, CYAN, NIGHT = "0xFF1F8E", "0x00E5D2", "0x0D0717"


def label(text, color, txt_color):
    t = text.replace(":", r"\:").replace("'", "")
    return (f"drawbox=x=36:y=36:w={52 + 34 * len(text)}:h=96:color={color}@1:t=fill,"
            f"drawtext=fontfile='{FONT}':text='{t}':x=60:y=44:fontsize=72:fontcolor={txt_color}")


def build(top, bottom, out, top_label="GTA 5", bottom_label="GTA 6", seconds=6.0, top_start=0.0, bottom_start=0.0):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    half = f"scale={W}:{HALF}:force_original_aspect_ratio=increase,crop={W}:{HALF},fps=30,setsar=1"
    fc = (f"[0:v]{half},{label(top_label, PINK, 'white')}[a];"
          f"[1:v]{half},{label(bottom_label, CYAN, NIGHT)}[b];"
          f"[a][b]vstack=inputs=2,drawbox=x=0:y={HALF - 4}:w={W}:h=8:color=white@0.9:t=fill[v]")
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y",
           "-ss", str(top_start), "-t", str(seconds), "-stream_loop", "-1", "-i", str(top),
           "-ss", str(bottom_start), "-t", str(seconds), "-stream_loop", "-1", "-i", str(bottom),
           "-filter_complex", fc, "-map", "[v]", "-t", str(seconds), "-an",
           "-c:v", "libx264", "-crf", "24", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(f"comparison clip -> {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("top")
    ap.add_argument("bottom")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--top-label", default="GTA 5")
    ap.add_argument("--bottom-label", default="GTA 6")
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--top-start", type=float, default=0.0)
    ap.add_argument("--bottom-start", type=float, default=0.0)
    a = ap.parse_args()
    build(a.top, a.bottom, a.out, a.top_label, a.bottom_label, a.seconds, a.top_start, a.bottom_start)


if __name__ == "__main__":
    main()
