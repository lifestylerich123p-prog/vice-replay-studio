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
    from . import quizcheck  # quiz Shorts: the zoomed "guess" must not show its own answer
    blockers += quizcheck.problems(ep, episode, video, tf)
    from . import viewcheck  # rules from our own post-launch Shorts (moving first frame, short scripts, no plain tips)
    gp = any((db.ROOT / "media" / "gameplay").glob("*.mp4"))
    vb, advice = viewcheck.check(ep, gameplay_available=gp)
    blockers += vb
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
             "status": "BLOCKED" if blockers else "awaiting owner approval", "blockers": blockers, "advice": advice,
             "upload_command_after_approval": f"python -m studio.ship {episode} --upload short --title N"}
    (out / "draft.json").write_text(json.dumps(draft, indent=1, ensure_ascii=False))
    print(json.dumps(draft, indent=1, ensure_ascii=False))


def _workflow(x, workflow, srcmod):
    """Starter-kit commands. Returns True when handled."""
    from . import editor
    if x.cmd == "add-source":
        sid = srcmod.add(x.file, x.creator, x.url, x.rights, proof_path=x.proof, commercial=x.commercial_use,
                         youtube=x.youtube_allowed, confirm_owned=x.confirm_owned, destinations=x.dest,
                         campaign=x.campaign, attribution=x.attribution, notes=x.notes)
        print(f"Source ID: {sid}. Registration is not a publishing approval; `rank` shows the rights result.")
    elif x.cmd == "add-candidate":
        cid, total = workflow.add_candidate(x.source_id, x.title, x.start, x.end,
                                            {k: getattr(x, k) for k in ("curiosity", "payoff", "context", "audio",
                                                                        "visuals", "originality")})
        print(f"Candidate ID: {cid}, editorial score {total}/100 (a production priority, not a view prediction)")
    elif x.cmd == "rank" and not x.topic:  # no topic: rank the scored candidates (starter behaviour)
        print(json.dumps(workflow.rank(), indent=1))
    elif x.cmd == "create-project":
        pid = workflow.create_project(x.candidate_id, headline=x.headline, destination=x.dest)
        print(f"Project ID: {pid}\nFolder: projects/{pid}/")
    elif x.cmd == "render":
        p, params = workflow.project_params(x.project_id)
        for k in ("layout", "cam", "game", "keep", "punch", "replay", "headline"):
            if getattr(x, k) is not None:
                params[k] = getattr(x, k)
        p = editor.build(x.project_id, params, rerun=("render", "cover", "qc", "draft"))
        print(f"{x.project_id}: {p['status']}  video: projects/{x.project_id}/{x.project_id}.mp4")
    elif x.cmd == "qc":
        print((db.ROOT / "projects" / x.project_id / f"{x.project_id}.qc.md").read_text())
    elif x.cmd == "package":
        print((db.ROOT / "projects" / x.project_id / "draft.json").read_text())
    elif x.cmd == "approve-captions":
        p = workflow.approve_captions(x.project_id)
        print(f"{x.project_id}: captions approved, re-rendered; status {p['status']}")
    elif x.cmd == "status":
        print(json.dumps(workflow.status(), indent=1, default=str))
    elif x.cmd == "frame":
        from . import framing
        out = x.out or str(Path(x.file).with_suffix("")) + f".{x.layout}.mp4"
        print(json.dumps(framing.render(x.file, out, layout=x.layout), indent=1, default=float))
    elif x.cmd == "dashboard":
        from . import control
        control.serve(x.port)
    else:
        return False
    return True


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
        s.add_argument("topic", nargs="?" if name == "rank" else None)
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
    s = sub.add_parser("add-source", help="register a LOCAL file and its rights (starter workflow)")
    s.add_argument("--file", required=True)
    s.add_argument("--creator", required=True)
    s.add_argument("--url", required=True)
    s.add_argument("--rights", required=True, choices=("owned", "permission", "licensed", "campaign", "policy", "unknown", "denied"))
    s.add_argument("--proof", default="")
    s.add_argument("--campaign")
    s.add_argument("--dest", action="append", help="allowed destination (repeatable); default vice-replay")
    s.add_argument("--commercial-use", action="store_true")
    s.add_argument("--youtube-allowed", action="store_true")
    s.add_argument("--confirm-owned", action="store_true")
    s.add_argument("--attribution", default="")
    s.add_argument("--notes", default="")
    s = sub.add_parser("add-candidate")
    s.add_argument("--source-id", type=int, required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--start", type=float, required=True)
    s.add_argument("--end", type=float, required=True)
    for f in ("curiosity", "payoff", "context", "audio", "visuals", "originality"):
        s.add_argument("--" + f, type=int, required=True)
    s = sub.add_parser("create-project")
    s.add_argument("--candidate-id", required=True)
    s.add_argument("--headline")
    s.add_argument("--dest")
    s = sub.add_parser("render")
    s.add_argument("--project-id", required=True)
    s.add_argument("--layout", choices=("auto", "stack", "pip", "fill", "blur"))
    s.add_argument("--cam", type=float, nargs=4, metavar=("X", "Y", "W", "H"))
    s.add_argument("--game", type=float, nargs=4, metavar=("X", "Y", "W", "H"))
    s.add_argument("--keep", type=float, nargs=4, action="append", metavar=("X", "Y", "W", "H"))
    s.add_argument("--punch", type=float)
    s.add_argument("--replay", type=float, nargs=2)
    s.add_argument("--headline")
    for name in ("qc", "package"):
        s = sub.add_parser(name)
        s.add_argument("--project-id", required=True)
    s = sub.add_parser("approve-captions")
    s.add_argument("project_id")
    sub.add_parser("status")
    s = sub.add_parser("frame", help="preview the framing engine on a local 16:9 file")
    s.add_argument("file")
    s.add_argument("--layout", default="auto", choices=("auto", "stack", "pip", "fill", "blur"))
    s.add_argument("--out", default=None)
    s = sub.add_parser("dashboard", help="local control dashboard on http://127.0.0.1:8765")
    s.add_argument("--port", type=int, default=8765)
    x = ap.parse_args()
    from . import workflow, sources as srcmod
    try:
        if _workflow(x, workflow, srcmod):
            return
    except srcmod.RightsError as e:
        sys.exit(f"ERROR: {e}")

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
