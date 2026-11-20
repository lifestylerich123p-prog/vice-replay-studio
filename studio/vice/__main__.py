"""Vice Replay system CLI: research -> rights-checked projects -> QC -> publication drafts.

    python -m studio.vice audit                     # channel performance by series (YouTube Data + Analytics)
    python -m studio.vice discover                  # competitor research (cached 24 h)
    python -m studio.vice scan                      # candidate moments from authorized sources, deduped
    python -m studio.vice clip SRC --start 0 --end 14 --campaign lacy-gta6 --headline "..." [--punch 3.4] [--replay 2 5.8]
    python -m studio.vice rank "topic"              # ranking episode skeleton from authorized footage
    python -m studio.vice create "topic"            # narrated episode skeleton (then research + studio.ship)
    python -m studio.vice batch                     # next ready ideas from the 14-day calendar
    python -m studio.vice analyze VIDEO [--episode E] [--dest vice-replay]
    python -m studio.vice campaigns                 # registry, eligibility, payout math
    python -m studio.vice report                    # one-page report + CSV/JSON exports
    python -m studio.vice publish episodes/<slug>.json   # publication draft (QC + rights + channel check)
    python -m studio.vice rights [ASSET --dest D] | fingerprint | calendar

Nothing here uploads. Publishing stays: owner says "approve" in chat -> studio.ship --upload (CLAUDE.md).
"""
import argparse
import json
import re
import sys
from pathlib import Path

from . import db


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]


def skeleton(topic, fmt):
    slug = "gta6-" + slugify(topic.replace("GTA 6", "").replace("gta 6", ""))
    p = db.ROOT / "episodes" / f"{slug}.json"
    if p.exists():
        sys.exit(f"{p} already exists")
    clips = sorted((db.ROOT / "media" / "trailer").glob("extended-look-*.mp4"))
    n = 5 if fmt == "ranking" else 4
    heads = ["NUMBER 3", "NUMBER 2", "NUMBER 1"] if fmt == "ranking" else ["HOOK", "POINT 1", "POINT 2"]
    segs = [{"headline": h, "headline_es": "", "text": "TODO: one sourced sentence", "text_es": "",
             "media": f"../media/trailer/{clips[i % len(clips)].name}"} for i, h in enumerate(["HOOK"] + heads[:n - 2])]
    segs.append({"headline": "TELL ME BELOW", "headline_es": "", "text": "TODO: loop line ending with 'because'",
                 "text_es": "", "media": f"../media/trailer/{clips[-1].name}"})
    ep = {"title": f"GTA 6: {topic}", "slug": slug, "format": fmt, "series": "B: Rankings" if fmt == "ranking" else "C: Explained",
          "voice": "am_michael", "rate": "+10%", "use_gameplay": True, "short_title": f"GTA 6: {topic} #GTA6 #Shorts",
          "short_title_options": [], "short_description": "TODO", "short_es": {"title": "", "description": ""},
          "pinned_comment": "TODO", "tiktok_hashtags": ["#gta6", "#gtavi", "#gaming"], "sources": [], "short": segs}
    p.write_text(json.dumps(ep, indent=2, ensure_ascii=False) + "\n")
    from . import rights
    rc = rights.check_episode(ep)
    print(f"Wrote {p.relative_to(db.ROOT)} ({fmt}); rights gate: {'OK' if rc['ok'] else 'BLOCKED'}")
    print("Next: research fresh facts (2+ sources), fill every TODO + sources, then `python -m studio.ship " + str(p.relative_to(db.ROOT)) + "`")


def publish_draft(episode, dest):
    from . import channels, qc, rights
    ep = json.loads(Path(episode).read_text())
    slug = ep["slug"]
    out = db.ROOT / "output" / slug
    video = out / f"{slug}-short.mp4"
    if not video.exists():
        sys.exit(f"Render first: python -m studio.ship {episode}")
    freezes = []
    tf = video.with_suffix(".timings.json")
    if tf.exists():
        for t, s in zip(json.loads(tf.read_text()), ep.get("short", [])):
            if s.get("freeze"):
                freezes.append(t["start"] + s["freeze"]["at"] / s.get("speed", 1))
    rep = qc.check(video, episode=episode, dest=dest, intended_freezes=freezes)
    md = qc.write(rep, out, slug)
    ctype = "official-footage-commentary" if ep.get("use_gameplay") is False else "original-narrated"
    val = channels.validate(dest, ctype)
    blockers = [f"QC {c['check']}: {c['detail']}" for c in rep["checks"] if c["status"] == "fail"] + val["problems"]
    cover = out / "cover.jpg"
    if tf.exists() and len(ep.get("short", [])) > 1:  # cover = the payoff segment's middle frame
        t = json.loads(tf.read_text())[1]
        import subprocess
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{(t['start'] + t['end']) / 2 + 1:.2f}", "-i",
                        str(video), "-frames:v", "1", "-q:v", "3", str(cover)])
    draft = {"episode": episode, "destination": dest, "channel_check": val, "video": str(video.relative_to(db.ROOT)),
             "spanish_video": f"output/{slug}/{slug}-short-es.mp4", "cover": str(cover.relative_to(db.ROOT)),
             "title_options": ep.get("short_title_options") or [ep.get("short_title")],
             "description": ep.get("short_description"), "pinned_comment": ep.get("pinned_comment"),
             "qc_report": str(md.relative_to(db.ROOT)), "rights": rights.check_episode(ep, dest)["ok"],
             "status": "BLOCKED" if blockers else "awaiting owner approval", "blockers": blockers,
             "upload_command_after_approval": f"python -m studio.ship {episode} --upload short --title N"}
    (out / "draft.json").write_text(json.dumps(draft, indent=1, ensure_ascii=False))
    print(json.dumps(draft, indent=1, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("audit", "discover", "scan", "batch", "report", "fingerprint", "calendar"):
        sub.add_parser(c)
    c = sub.add_parser("clip")
    c.add_argument("source")
    c.add_argument("--start", type=float, required=True)
    c.add_argument("--end", type=float, required=True)
    c.add_argument("--campaign")
    c.add_argument("--dest", default=None)
    c.add_argument("--headline", default="")
    c.add_argument("--punch", type=float)
    c.add_argument("--replay", type=float, nargs=2)
    c.add_argument("--id")
    c.add_argument("--caption", default="")
    c.add_argument("--title", action="append", default=[])
    for name in ("rank", "create"):
        s = sub.add_parser(name)
        s.add_argument("topic")
    a = sub.add_parser("analyze")
    a.add_argument("video")
    a.add_argument("--episode")
    a.add_argument("--dest", default="vice-replay")
    a.add_argument("--no-whisper", action="store_true")
    cp = sub.add_parser("campaigns")
    cp.add_argument("--record", nargs=5, metavar=("CAMPAIGN", "CLIP", "STATUS", "USD", "VIEWS"))
    pb = sub.add_parser("publish")
    pb.add_argument("episode")
    pb.add_argument("--dest", default="vice-replay")
    r = sub.add_parser("rights")
    r.add_argument("asset", nargs="?")
    r.add_argument("--dest", default="vice-replay")
    x = ap.parse_args()

    if x.cmd == "audit":
        from . import analytics
        rep, (md, _) = analytics.run()
        print(md.read_text())
    elif x.cmd == "discover":
        from . import research
        rep, (md, _) = research.run()
        print(md.read_text())
    elif x.cmd == "scan":
        from . import discovery, rights
        rights.sync()
        cands, md = discovery.run()
        print(f"{len(cands)} candidates -> {md.relative_to(db.ROOT)}")
    elif x.cmd == "clip":
        from . import editor
        dest = x.dest or ("clipcircuit" if x.campaign else "vice-replay")
        pid = x.id or slugify(f"{Path(x.source).stem}-{int(x.start)}")
        params = {"source": x.source, "start": x.start, "end": x.end, "campaign": x.campaign, "headline": x.headline,
                  "punch": x.punch, "replay": x.replay, "title_options": x.title, "caption": x.caption}
        editor.new_project(pid, x.source, x.start, x.end, x.campaign, dest, x.headline)
        p = editor.build(pid, params)
        print(f"{pid}: {p['status']} {p.get('error') or ''}\nfiles: projects/{pid}/")
    elif x.cmd in ("rank", "create"):
        skeleton(x.topic, "ranking" if x.cmd == "rank" else "explained")
    elif x.cmd == "analyze":
        from . import qc
        rep = qc.check(x.video, episode=x.episode, dest=x.dest, use_whisper=not x.no_whisper)
        print(qc.write(rep).read_text())
    elif x.cmd == "campaigns":
        from . import campaigns
        if x.record:
            camp, clip, status, usd, views = x.record
            campaigns.record(camp, clip, status, float(usd), int(views))
        print(campaigns.run().read_text())
    elif x.cmd == "report":
        from . import report
        print(report.run().read_text())
    elif x.cmd == "publish":
        publish_draft(x.episode, x.dest)
    elif x.cmd == "rights":
        from . import rights
        rights.sync()
        if x.asset:
            print(json.dumps(rights.check(x.asset, x.dest), indent=1))
        else:
            for r in rights.load():
                print(f"{r['status']:12} {r['id']:30} -> {', '.join(r['destinations_allowed']) or 'nowhere'}")
    elif x.cmd == "fingerprint":
        from . import registry
        print(registry.fingerprint_all(), "new fingerprints")
    elif x.cmd in ("calendar", "batch"):
        from . import calendar
        if x.cmd == "calendar":
            print(calendar.run().read_text())
        else:
            calendar.batch()


if __name__ == "__main__":
    main()
