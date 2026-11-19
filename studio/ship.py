"""One command from episode JSON to finished files (and optionally YouTube), so runs spend tokens on writing, not steps.

    python -m studio.ship episodes/<slug>.json                 # gameplay pull + render everything + check sheet
    python -m studio.ship episodes/<slug>.json --upload all    # ...then upload/schedule (owner approval only!)
    python -m studio.ship episodes/<slug>.json --upload short --now
    python -m studio.ship episodes/<slug>.json --tiktok        # (main chat only) push Shorts to the tiktok-files branch

What it does, skipping anything already up to date:
1. `python -m studio.gameplay` (owner's newest gameplay = Short backgrounds; failures are ignored).
2. Renders the main video (if the episode has segments), every Short, and the Spanish-voice Shorts.
3. Writes output/<slug>/check.jpg: 4 frames from each video on one sheet, so ONE image read checks everything
   (captions readable, headlines not clipped, no black bars or black frames).
4. Prints a short summary: files, durations, titles, and the TikTok captions.
5. With --upload: runs studio.youtube_upload with the same flags and prints the "COMMENTS TO POST" command.
6. Runs studio.tidy.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(args, check=False):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"failed: {' '.join(args)}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    return r


def duration(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def stale(out, src):
    return not out.exists() or out.stat().st_mtime < src.stat().st_mtime


def check_sheet(videos, dest):
    rows = []
    for v in videos:
        d = duration(v)
        frames = []
        for k, t in enumerate([0.5, d * 0.35, d * 0.65, max(0.5, d - 1.5)]):
            f = dest.parent / f"_f{k}.jpg"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1",
                 "-vf", "scale=-2:270", str(f)])
            if f.exists():
                frames.append(Image.open(f).convert("RGB"))
                f.unlink()
        if frames:
            w = sum(i.width for i in frames)
            row = Image.new("RGB", (w, 290), "black")
            x = 0
            for i in frames:
                row.paste(i, (x, 20))
                x += i.width
            ImageDraw.Draw(row).text((4, 3), f"{v.name}  {d:.0f}s", fill="yellow")
            rows.append(row)
    if rows:
        sheet = Image.new("RGB", (max(r.width for r in rows), 290 * len(rows)), "black")
        for k, r in enumerate(rows):
            sheet.paste(r, (0, 290 * k))
        sheet.save(dest, quality=80)


def queue_reels(ep_path, upload_txt, date=None):
    """Every uploaded Short also goes to Instagram Reels (owner approved Nov 19): add it to
    content/learn/reels_queue.json 5 minutes after its YouTube time and print the wake-ups to schedule."""
    import datetime as dt
    import json
    import re
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")
    day = dt.date.fromisoformat(date) if date else dt.datetime.now(et).date()
    qf = ROOT / "content" / "learn" / "reels_queue.json"
    q = json.loads(qf.read_text()) if qf.exists() else []
    added = []
    for m in re.finditer(r"uploading (\S+): .*?->\s+(now|\d{1,2}:\d{2} [AP]M)", upload_txt):
        key, when = m.group(1), m.group(2)
        if key in ("main", "replies"):
            continue
        if when == "now":
            at = dt.datetime.now(et) + dt.timedelta(minutes=2)
        else:
            at = dt.datetime.combine(day, dt.datetime.strptime(when, "%I:%M %p").time(), et) + dt.timedelta(minutes=5)
        item = {"at": at.strftime("%Y-%m-%d %H:%M"), "episode": str(Path(ep_path).relative_to(ROOT)), "item": key}
        if not any(i.get("episode") == item["episode"] and i.get("item") == key for i in q):
            q.append(item)
            added.append(item["at"])
    if added:
        q.sort(key=lambda i: (i["at"], 0 if i.get("campaign") else 1))
        qf.write_text(json.dumps(q, indent=1, ensure_ascii=False))
        print("REELS QUEUED (schedule a send_later wake-up running `python -m studio.instagram_upload --queue` at each):",
              ", ".join(sorted(added)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode")
    ap.add_argument("--upload", help="all, or main,short,news,replies,<short id> (owner approval only)")
    ap.add_argument("--now", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--at")
    ap.add_argument("--title", type=int)
    ap.add_argument("--no-es", action="store_true", help="skip the Spanish-voice Shorts")
    ap.add_argument("--tiktok", action="store_true", help="push the Shorts to the tiktok-files branch (main chat)")
    a = ap.parse_args()
    ep_path = (ROOT / a.episode).resolve() if not Path(a.episode).is_absolute() else Path(a.episode)
    ep = json.loads(ep_path.read_text())
    slug = ep["slug"]
    out = ROOT / "output" / slug

    r = run([PY, "-m", "studio.gameplay"])
    print("gameplay:", (r.stdout.strip().splitlines() or ["(nothing new)"])[-1][:120])
    if ep.get("segments") and stale(out / f"{slug}.mp4", ep_path):
        run([PY, "-m", "studio.make_video", str(ep_path)], check=True)
    if (ep.get("short") or ep.get("shorts")) and stale(out / f"{slug}-short.mp4" if ep.get("short") else
                                                        out / f"{slug}-short-{ep['shorts'][0]['id']}.mp4", ep_path):
        run([PY, "-m", "studio.make_video", str(ep_path), "--short"], check=True)
    if not a.no_es and (ep.get("short") or ep.get("shorts")):
        es_first = out / (f"{slug}-short-es.mp4" if ep.get("short") else f"{slug}-short-{ep['shorts'][0]['id']}-es.mp4")
        if stale(es_first, ep_path):
            run([PY, "-m", "studio.make_video", str(ep_path), "--short", "--es"])
    for w in out.glob("work*"):
        run(["rm", "-rf", str(w)])

    videos = sorted(p for p in out.glob("*.mp4") if "preview" not in p.name)
    check_sheet([v for v in videos if not v.name.endswith("-es.mp4")], out / "check.jpg")
    print(f"\nFILES ({out.relative_to(ROOT)}):")
    for v in videos:
        print(f"- {v.name}  {duration(v):.0f}s")
    print(f"CHECK SHEET: {out / 'check.jpg'}  (read it once: captions, headlines, black bars)")
    for t in sorted(out.glob("*.txt")):
        if t.name in ("tags.txt",):
            continue
        lines = t.read_text().splitlines()
        title = lines[1] if len(lines) > 1 else ""
        print(f"TIKTOK {t.stem}: {title.replace('#Shorts', '').strip()}")

    if a.upload:
        cmd = [PY, "-m", "studio.youtube_upload", str(ep_path), "--approve", a.upload]
        for flag, val in (("--date", a.date), ("--at", a.at), ("--title", a.title)):
            if val:
                cmd += [flag, str(val)]
        if a.now:
            cmd.append("--now")
        r = run(cmd)
        txt = r.stdout
        summary = [l for l in txt.splitlines() if any(k in l for k in ('"id"', "scheduled_et", "privacy_returned",
                                                                        "uploading", "COMMENTS", "--comment", "!"))]
        print("\nUPLOAD:\n" + "\n".join(summary))
        if r.returncode:
            print(r.stderr[-1500:])
        queue_reels(ep_path, txt, a.date)

    if a.tiktok:
        shorts = [v for v in videos if "-short" in v.name]
        tmp = ROOT.parent / "_tt"
        run(["rm", "-rf", str(tmp)])
        remote = run(["git", "remote", "get-url", "origin"]).stdout.strip()
        subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", "tiktok-files", remote, str(tmp)])
        subprocess.run(["git", "rm", "-q", "-r", "--ignore-unmatch", "v"], cwd=tmp)
        (tmp / "v").mkdir(exist_ok=True)
        for v in shorts:
            subprocess.run(["cp", str(v), str(tmp / "v" / v.name)])
        subprocess.run(["git", "add", "v"], cwd=tmp)
        subprocess.run(["git", "-c", "user.name=Vice Replay", "-c", "user.email=noreply@anthropic.com", "commit", "-qm",
                        f"TikTok files: {slug} (temporary)"], cwd=tmp)
        subprocess.run(["git", "push", "-q", "origin", "tiktok-files"], cwd=tmp, capture_output=True)
        run(["rm", "-rf", str(tmp)])
        print("TIKTOK: pushed", ", ".join(v.name for v in shorts), "to branch tiktok-files (folder v/)")

    run([PY, "-m", "studio.tidy"])


if __name__ == "__main__":
    main()
