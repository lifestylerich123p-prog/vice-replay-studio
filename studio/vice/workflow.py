"""The starter kit's command workflow, running on the main system (same names, same fail-closed rules):

    python -m studio.vice add-source --file F --creator C --url U --rights owned --confirm-owned --commercial-use --youtube-allowed
    python -m studio.vice add-candidate --source-id 1 --title T --start 12 --end 29 --curiosity 9 --payoff 9 --context 8 \
        --audio 8 --visuals 9 --originality 9
    python -m studio.vice rank
    python -m studio.vice create-project --candidate-id <id> [--headline ...]
    python -m studio.vice render --project-id <id> [--layout auto|stack|pip|fill|blur] [--cam x y w h] [--keep x y w h]
    python -m studio.vice qc --project-id <id>         # full QC report
    python -m studio.vice package --project-id <id>    # publication draft (never uploads)
    python -m studio.vice approve-captions <id>        # after reviewing captions.srt (edits are used)
    python -m studio.vice status

Differences from the starter, on purpose: renders go through the framing engine (webcam on top / tracked crop /
blur fill instead of empty bars), captions are transcribed locally with a review gate, QC is the full inspector,
sources carry SHA-256 provenance and a destination scope, and every rights decision is audited.
"""
import hashlib
import json
import re
from pathlib import Path

from . import db, editor, scoring, sources

SCORE_MAP = {"curiosity": "curiosity", "payoff": "payoff", "context": "context", "audio": "audio",
             "visuals": "visual", "originality": "contribution"}


def add_candidate(source_id, title, start, end, scores):
    con = sources.connect()
    src = sources.get(con, source_id)
    if not (0 <= start < end):
        raise sources.RightsError("Clip start must be >= 0 and end must be > start.")
    if end - start > 180:
        raise sources.RightsError("Clips over 180 s belong in the long-form pipeline (make_video main videos).")
    sc = {SCORE_MAP[k]: int(v) for k, v in scores.items()}
    total = scoring.total(sc)
    cid = "m" + hashlib.sha1(f"{source_id}|{start}|{end}".encode()).hexdigest()[:10]
    con.execute("INSERT OR REPLACE INTO candidates (id, creator, source_url, published, ts_start, ts_end, description, views,"
                " duration, category, rights_id, rights_status, restrictions, used, event_key, scores, total, origin, created_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid, src["creator"], src["file_path"], None, start, end, title, None, end - start, "manual",
                 f"source:{source_id}", None, src["notes"], 0, None, json.dumps(sc), total, f"source:{source_id}", db.now()))
    con.commit()
    return cid, total


def rank(destination=None):
    con = sources.connect()
    out = []
    for c in db.rows(con, "SELECT * FROM candidates WHERE origin LIKE 'source:%' OR scores IS NOT NULL"):
        sid = int(c["origin"].split(":")[1]) if (c["origin"] or "").startswith("source:") else None
        if sid is None:
            continue
        src = sources.get(con, sid)
        dest = destination or json.loads(src["destinations"])[0]
        ok, reasons = sources.strict_check(src, dest, con=con)
        out.append({"candidate_id": c["id"], "score": c["total"], "title": c["description"], "destination": dest,
                    "rights_approved": ok, "rights_issues": reasons})
    return sorted(out, key=lambda x: (not x["rights_approved"], -(x["score"] or 0)))


def create_project(candidate_id, headline=None, destination=None):
    con = sources.connect()
    c = con.execute("SELECT * FROM candidates WHERE id=?", (candidate_id,)).fetchone()
    if not c:
        raise sources.RightsError(f"No candidate {candidate_id}")
    sid = int(c["origin"].split(":")[1])
    src = sources.get(con, sid)
    dest = destination or json.loads(src["destinations"])[0]
    ok, reasons = sources.strict_check(src, dest, con=con)
    if not ok:
        raise sources.RightsError("Cannot create project:\n- " + "\n- ".join(reasons))
    pid = re.sub(r"[^a-z0-9]+", "-", c["description"].lower()).strip("-")[:40] + f"-{c['id'][-4:]}"
    editor.new_project(pid, src["file_path"], c["ts_start"], c["ts_end"], campaign=src["campaign"], dest=dest,
                       headline=headline or "")
    return pid


def project_params(pid):
    p = db.project_get(db.connect(), pid)
    if not p:
        raise sources.RightsError(f"No project {pid}")
    pj = db.ROOT / "projects" / pid / "project.json"
    params = json.loads(pj.read_text()) if pj.exists() else {}
    params.pop("id", None)
    stored = json.loads(db.connect().execute("SELECT files FROM projects WHERE id=?", (pid,)).fetchone()["files"] or "{}")
    return p, params or stored.get("params", {})


def approve_captions(pid):
    """The reviewer checked (and maybe edited) captions.srt: rebuild the styled captions from it and re-render."""
    out = db.ROOT / "projects" / pid
    srt = out / "captions.srt"
    if not srt.exists():
        raise sources.RightsError("no captions.srt in this project")
    words = []
    for block in srt.read_text().strip().split("\n\n"):
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        a, b = [x.strip() for x in lines[1].split("-->")]

        def secs(t):
            h, m, s = t.replace(",", ".").split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        toks = " ".join(lines[2:]).split()
        t0, t1 = secs(a), secs(b)
        for i, w in enumerate(toks):  # spread a reviewed line's words evenly across its time
            words.append({"w": w, "s": round(t0 + (t1 - t0) * i / len(toks), 2),
                          "e": round(t0 + (t1 - t0) * (i + 1) / len(toks), 2), "p": 1.0})
    editor.write_ass(words, out / "captions.ass")
    (out / "captions.approved").write_text(json.dumps({"at": db.now(), "words": len(words)}) + "\n")
    p, params = project_params(pid)
    return editor.build(pid, params, rerun=("render", "cover", "qc", "draft"))


def status():
    con = sources.connect()
    return {"sources": db.rows(con, "SELECT id, creator, rights_status, destinations, file_path FROM sources ORDER BY id"),
            "projects": db.rows(con, "SELECT id, kind, status, destination, updated_at FROM projects ORDER BY updated_at DESC"),
            "recent_rights_decisions": db.rows(con, "SELECT at, subject, destination, ok, reasons FROM rights_audit "
                                                    "ORDER BY id DESC LIMIT 8")}
