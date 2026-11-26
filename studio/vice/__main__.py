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
    python -m studio.vice publish episodes/<slug>.json   # publication draft (QC + rights + channel check), every Short
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
    # original first (Nov 22): the hook is our own graphic of a checked number (studio/charts.py)
    segs[0] = {"headline": "HOOK", "headline_es": "", "text": "TODO: the checked number, said as words", "text_es": "",
               "chart": {"type": "counter", "value": 0, "label": "TODO: what the number counts", "seed": 1}}
    segs.append({"headline": "TELL ME BELOW", "headline_es": "", "text": "TODO: loop line ending with 'because'",
                 "text_es": "", "media": f"../media/trailer/{clips[-1].name}"})
    ep = {"title": f"GTA 6: {topic}", "slug": slug, "format": fmt, "series": "B: Rankings" if fmt == "ranking" else "C: Explained",
          "voice": "af_heart", "rate": "+10%", "use_gameplay": True, "short_title": f"GTA 6: {topic} #GTA6 #Shorts",
          "short_title_options": [], "short_description": "TODO", "short_es": {"title": "", "description": ""},
          "pinned_comment": "TODO", "tiktok_hashtags": ["#gta6", "#gtavi", "#gaming"], "sources": [], "short": segs}
    p.write_text(json.dumps(ep, indent=2, ensure_ascii=False) + "\n")
    from . import rights
    rc = rights.check_episode(ep)
    print(f"Wrote {p.relative_to(db.ROOT)} ({fmt}); rights gate: {'OK' if rc['ok'] else 'BLOCKED'}")
    print("Next: research fresh facts (2+ sources), fill every TODO + sources, then `python -m studio.ship " + str(p.relative_to(db.ROOT)) + "`")


# fields that belong to the main video or to one Short; a "shorts" entry's view keeps only its own
SHORT_FIELDS = ("segments", "short", "shorts", "news_short", "tips_short", "thumbnail", "title", "title_options",
                "description", "short_title", "short_title_options", "short_description", "short_es", "pinned_comment")


def _short_units(ep):
    """(id, render name, single-Short episode view) for every Short of a "shorts" episode, the legacy "short" (id
    "short") included. Each view has only that Short's segments, title, description and pinned comment; the main video
    is checked once on its own (_main_checks), so its findings aren't repeated once per Short."""
    slug = ep["slug"]
    base = {k: v for k, v in ep.items() if k not in SHORT_FIELDS}
    units = []
    if ep.get("short"):
        units.append(("short", f"{slug}-short", dict(
            base, short=ep["short"], short_title=ep.get("short_title") or ep.get("title", ""),
            short_title_options=ep.get("short_title_options") or [], short_description=ep.get("short_description"),
            pinned_comment=ep.get("pinned_comment"))))
    for sh in ep["shorts"]:
        view = dict(base, short=sh.get("segments", []), short_title=sh.get("title") or ep.get("title", ""),
                    short_title_options=sh.get("title_options") or [], short_description=sh.get("description"),
                    pinned_comment=sh.get("pinned_comment"))
        if sh.get("format"):
            view["format"] = sh["format"]
        units.append((sh["id"], f"{slug}-short-{sh['id']}", view))
    return units


def _main_checks(ep, dest):
    """Rights + facts for the main video of a "shorts" episode (its segments, title, description, thumbnail), once.
    Text and files only: no render needed. Facts that fail block; warnings are advice; the full list is kept."""
    from . import factcheck, rights
    view = {k: v for k, v in ep.items() if k not in SHORT_FIELDS or k in ("segments", "title", "description", "thumbnail")}
    rc = rights.check_episode(view, dest)
    facts = factcheck.check_episode(view)
    blockers = [f"rights: {c['asset']}: {c['record'] or 'no record'} ({'; '.join(c['reasons'])})"
                for c in rc["checks"] if not c["ok"]]
    blockers += [f"facts: {x['where']}: {x['text'][:140]} ({x['fix']})" for x in facts if x["level"] == "fail"]
    advice = [f"facts: {x['where']}: {x['text'][:140]} ({x['fix']})" for x in facts if x["level"] == "warn"]
    return {"rights": rc["ok"], "blockers": blockers, "advice": advice, "facts": facts}


def _gate(episode, ep, video, dest, key, gameplay, val, cover):
    """Every pre-publish check on one rendered Short. `ep` is the single-Short episode it was rendered from; `val` the
    channel check. Returns the QC report path, blockers, advice and rights result."""
    from . import qc, quizcheck, rights, viewcheck
    freezes = []
    tf = video.with_suffix(".timings.json")
    if tf.exists():
        for t, s in zip(json.loads(tf.read_text()), ep.get("short", [])):
            if s.get("freeze"):
                freezes.append(t["start"] + s["freeze"]["at"] / s.get("speed", 1))
    rep = qc.check(video, episode=ep, dest=dest, intended_freezes=freezes)
    md = qc.write(rep, video.parent, ep["slug"])
    blockers = [f"QC {c['check']}: {c['detail']}" for c in rep["checks"] if c["status"] == "fail"] + val["problems"]
    blockers += quizcheck.problems(ep, episode, video, tf)  # quiz Shorts: the zoomed "guess" must not show its own answer
    # rules from our own post-launch Shorts (moving first frame, short scripts, no plain tips)
    vb, advice = viewcheck.check_short(ep, key, ep.get("short_title") or ep.get("title", ""), ep.get("short", []),
                                       gameplay_available=gameplay)
    blockers += vb
    if tf.exists() and len(ep.get("short", [])) > 1:  # cover = the payoff segment's middle frame
        t = json.loads(tf.read_text())[1]
        import subprocess
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{(t['start'] + t['end']) / 2 + 1:.2f}", "-i",
                        str(video), "-frames:v", "1", "-q:v", "3", str(cover)])
    return {"qc_report": md, "blockers": blockers, "advice": advice, "rights": rights.check_episode(ep, dest)["ok"]}


def publish_draft(episode, dest, lang="en"):
    """Publication draft: QC + rights + channel + views + facts on the rendered Short(s), written to draft.json.
    An episode with "shorts" is gated once per Short, plus one rights/facts check of its main video ("main"), and gets
    one combined result (blockers/advice prefixed with the Short id or "main"); a single-"short" episode gets the
    one-Short draft."""
    from . import channels, viewcheck
    ep = json.loads(Path(episode).read_text())
    slug = ep["slug"]
    out = db.ROOT / "output" / slug
    rel = lambda p: str(p.relative_to(db.ROOT))  # noqa: E731
    gameplay = any((db.ROOT / "media" / "gameplay").glob("*.mp4"))
    vals = {}

    def channel_check(view):  # once per content type (it costs a YouTube token call), not once per Short
        ctype = "official-footage-commentary" if view.get("use_gameplay") is False else "original-narrated"
        if ctype not in vals:
            vals[ctype] = channels.validate(dest, ctype)
        return vals[ctype]

    if ep.get("segments") and not ep.get("short") and not ep.get("shorts"):
        # a long video with no Short (Nov 23: the Sunday hub, e.g. gta6-10-numbers)
        from . import qc
        video = out / f"{slug}.mp4"
        if not video.exists():
            sys.exit(f"Render first: python -m studio.make_video {episode}")
        val, main = channel_check(ep), _main_checks(ep, dest)
        rep = qc.check(video, episode=ep, dest=dest)
        qc_md = qc.write(rep, out, slug)
        vb, vw = viewcheck.check(ep, recent=[])
        blockers = ([f"QC {c['check']}: {c['detail']}" for c in rep["checks"] if c["status"] == "fail"] + val["problems"]
                    + [f"main: {b}" for b in main["blockers"]] + vb)
        advice = [f"main: {a}" for a in main["advice"]] + vw
        draft = {"episode": episode, "destination": dest, "channel_check": val, "video": rel(video),
                 "thumbnail": rel(out / "thumbnail.jpg"), "title_options": ep.get("title_options") or [ep.get("title")],
                 "description": ep.get("description"), "pinned_comment": ep.get("pinned_comment"), "qc_report": rel(qc_md),
                 "rights": main["rights"], "status": "BLOCKED" if blockers else "awaiting owner approval",
                 "blockers": blockers, "advice": advice,
                 "upload_command_after_approval": f"python -m studio.ship {episode} --upload main --title N"}
    elif not ep.get("shorts"):
        # es_only, or --lang es (Phase 3: the Spanish channel's QA runs on the Spanish render, never needs the English one)
        video = out / (f"{slug}-short-es.mp4" if ep.get("es_only") or lang == "es" else f"{slug}-short.mp4")
        if not video.exists():
            sys.exit(f"Render first: python -m studio.make_video {episode} --short" + (" --es" if lang == "es" else ""))
        val, cover = channel_check(ep), out / "cover.jpg"
        g = _gate(episode, ep, video, dest, "short", gameplay, val, cover)
        g["advice"] += viewcheck.check_tags(ep)  # same advice as viewcheck.check(ep)
        draft = {"episode": episode, "destination": dest, "channel_check": val, "video": rel(video),
                 "spanish_video": f"output/{slug}/{slug}-short-es.mp4", "cover": rel(cover),
                 "title_options": ep.get("short_title_options") or [ep.get("short_title")],
                 "description": ep.get("short_description"), "pinned_comment": ep.get("pinned_comment"),
                 "qc_report": rel(g["qc_report"]), "rights": g["rights"],
                 "status": "BLOCKED" if g["blockers"] else "awaiting owner approval", "blockers": g["blockers"],
                 "advice": g["advice"], "upload_command_after_approval": f"python -m studio.ship {episode} --upload short --title N"}
    else:
        units = _short_units(ep)
        missing = [(sid, name) for sid, name, _ in units if not (out / f"{name}.mp4").exists()]
        if missing:
            sys.exit("Render first: " + "; ".join(f"Short '{sid}' has no output/{slug}/{name}.mp4" for sid, name in missing)
                     + f". Run: python -m studio.ship {episode}")
        shorts, blockers, advice = [], [], []
        main = _main_checks(ep, dest) if ep.get("segments") else None
        if main:
            blockers += [f"main: {b}" for b in main["blockers"]]
            advice += [f"main: {a}" for a in main["advice"]]
        for sid, name, view in units:
            video, val = out / f"{name}.mp4", channel_check(view)
            cover = out / ("cover.jpg" if sid == "short" else f"cover-{sid}.jpg")
            g = _gate(episode, view, video, dest, sid, gameplay, val, cover)
            blockers += [f"{sid}: {b}" for b in g["blockers"]]
            advice += [f"{sid}: {a}" for a in g["advice"]]
            shorts.append({"id": sid, "channel_check": val, "video": rel(video), "spanish_video": f"output/{slug}/{name}-es.mp4",
                           "cover": rel(cover), "title_options": view.get("short_title_options") or [view.get("short_title")],
                           "description": view.get("short_description"), "pinned_comment": view.get("pinned_comment"),
                           "qc_report": rel(g["qc_report"]), "rights": g["rights"],
                           "status": "BLOCKED" if g["blockers"] else "awaiting owner approval",
                           "blockers": g["blockers"], "advice": g["advice"],
                           "upload_command_after_approval": f"python -m studio.ship {episode} --upload {sid} --title N"})
        advice += [f"episode: {w}" for w in viewcheck.check_tags(ep)]  # titles/tags: once for the whole episode
        draft = {"episode": episode, "destination": dest,
                 "rights": all(s["rights"] for s in shorts) and (main is None or main["rights"]),
                 "status": "BLOCKED" if blockers else "awaiting owner approval", "blockers": blockers, "advice": advice,
                 **({"main": main} if main else {}), "shorts": shorts,
                 "upload_command_after_approval": f"python -m studio.ship {episode} --upload {','.join(s['id'] for s in shorts)}"}
    (out / ("draft-es.json" if lang == "es" else "draft.json")).write_text(json.dumps(draft, indent=1, ensure_ascii=False))
    print(json.dumps(draft, indent=1, ensure_ascii=False))
    return draft


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
    pb.add_argument("--lang", choices=("en", "es"), default="en", help="es: QA the Spanish render (-short-es.mp4)")
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
        publish_draft(x.episode, x.dest, x.lang)
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
