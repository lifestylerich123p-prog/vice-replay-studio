"""Local production control dashboard: python -m studio.vice dashboard  ->  http://127.0.0.1:8765

One page: channel numbers, the 14-day queue, episodes (render / QC + draft), clip projects (resume / approve
captions), jobs with logs, rights decisions, campaigns, costs. Buttons start ALLOWLISTED local jobs only (render,
QC, drafts, research); there is no upload or publish button: publishing stays "approve" in chat (CLAUDE.md).

Jobs run one at a time in a background worker (16 GB MacBook: one render at a time), are stored in the `jobs`
table with a log file, and a job that was running when the server stopped is re-queued at the next start (every
job here is resumable: studio.ship skips finished outputs, clip projects skip finished steps).
Bound to 127.0.0.1; POSTs need the per-session token printed in the page, so other sites can't trigger jobs.
"""
import html
import json
import secrets
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import db

ROOT = db.ROOT
TOKEN = secrets.token_hex(12)
JOBS_SQL = """CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, target TEXT,
  cmd TEXT, status TEXT, created_at TEXT, started_at TEXT, finished_at TEXT, returncode INTEGER, log TEXT)"""

PY = sys.executable
ACTIONS = {  # action -> (label, argv builder). Nothing here uploads or posts.
    "render": ("Render", lambda t: [PY, "-m", "studio.ship", f"episodes/{t}.json"]),
    "publish-draft": ("QC + draft", lambda t: [PY, "-m", "studio.vice", "publish", f"episodes/{t}.json"]),
    "resume-project": ("Resume", lambda t: [PY, "-m", "studio.vice", "render", "--project-id", t]),
    "approve-captions": ("Approve captions", lambda t: [PY, "-m", "studio.vice", "approve-captions", t]),
    "create-idea": ("Create episode", lambda t: [PY, "-m", "studio.vice", "create", t]),
    "audit": ("Audit", lambda t: [PY, "-m", "studio.vice", "audit"]),
    "scan": ("Scan moments", lambda t: [PY, "-m", "studio.vice", "scan"]),
    "report": ("Report", lambda t: [PY, "-m", "studio.vice", "report"]),
    "tests": ("Run tests", lambda t: [PY, "-m", "pytest", "tests", "-q"]),
}


def con():
    c = db.connect()
    c.execute(JOBS_SQL)
    return c


def enqueue(action, target=""):
    if action not in ACTIONS:
        raise ValueError(f"action not allowed: {action}")
    if any(ch in target for ch in "/\\\n\r") or len(target) > 160:
        raise ValueError("bad target")
    c = con()
    cmd = ACTIONS[action][1](target)
    cur = c.execute("INSERT INTO jobs (action, target, cmd, status, created_at) VALUES (?,?,?,?,?)",
                    (action, target, json.dumps(cmd), "queued", db.now()))
    c.commit()
    return cur.lastrowid


def worker(stop):
    while not stop.is_set():
        c = con()
        job = c.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY id LIMIT 1").fetchone()
        if not job:
            time.sleep(1)
            continue
        logf = ROOT / "reports" / "jobs" / f"job-{job['id']}.log"
        logf.parent.mkdir(parents=True, exist_ok=True)
        c.execute("UPDATE jobs SET status='running', started_at=?, log=? WHERE id=?", (db.now(), str(logf), job["id"]))
        c.commit()
        with logf.open("w") as lf:
            rc = subprocess.run(json.loads(job["cmd"]), cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT).returncode
        c.execute("UPDATE jobs SET status=?, finished_at=?, returncode=? WHERE id=?",
                  ("done" if rc == 0 else "failed", db.now(), rc, job["id"]))
        c.commit()


def recover():
    """Jobs left 'running' by a crash or restart go back to the queue (all actions are resumable)."""
    c = con()
    n = c.execute("UPDATE jobs SET status='queued', started_at=NULL WHERE status='running'").rowcount
    c.commit()
    return n


def latest_json(pattern):
    files = sorted(ROOT.glob(pattern))
    return json.loads(files[-1].read_text()) if files else None


def esc(x):
    return html.escape(str(x if x is not None else ""))


def button(action, target, label=None):
    return (f"<form method=post action=/run style=display:inline><input type=hidden name=token value={TOKEN}>"
            f"<input type=hidden name=action value={esc(action)}><input type=hidden name=target value=\"{esc(target)}\">"
            f"<button>{esc(label or ACTIONS[action][0])}</button></form>")


def table(headers, rows):
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) or f"<tr><td colspan={len(headers)}>none</td></tr>"
    return f"<div class=scroll><table><tr>{h}</tr>{b}</table></div>"


def media_link(path):
    p = Path(path)
    if not p.exists():
        return "-"
    rel = p.resolve().relative_to(ROOT)
    return f"<a href='/file?p={urllib.parse.quote(str(rel))}' target=_blank>{esc(p.name)}</a>"


def page():
    c = con()
    parts = []
    audit = latest_json("reports/audit-*.json")
    if audit:
        ch = audit["channel"]
        parts.append(f"<section><h2>Channel</h2><p class=big>{ch['subs']} subscribers · {ch['views']:,} views · "
                     f"{ch['videos']} videos <span class=muted>(audit {esc(audit['taken'][:16])})</span> {button('audit', '', 'Refresh audit')}</p>")
        parts.append(table(["Type", "Series", "Videos", "Median views", "Median 24 h", "Engaged %"],
                           [[esc(g["type"]), esc(g["series"]), g["n"], g["median_views"], g["median_views_24h"] or "-",
                             g["median_engaged_rate"] or "-"] for g in audit["groups"]]))
        if audit["flags"]:
            parts.append("<details><summary>Videos needing investigation</summary><ul>" + "".join(
                f"<li>{esc(f['title'])}: {esc('; '.join(f['why']))}</li>" for f in audit["flags"]) + "</ul></details>")
        parts.append("</section>")
    cal = json.loads((ROOT / "content" / "vice-calendar.json").read_text())
    rows = []
    for i in cal:
        blocked = i["rights_status"].startswith("BLOCKED")
        act = "" if blocked or i["status"].startswith("rendered") else button("create-idea", i["topic"][:150], "Create")
        rows.append([esc(i["id"]), esc(i["date"][5:]) + " " + esc(i["slot_et"]), esc(i["series"]), esc(i["topic"]),
                     f"<span class={'bad' if blocked else 'ok'}>{esc(i['rights_status'].split(':')[0])}</span>",
                     esc(i["status"]), act])
    parts.append("<section><h2>14-day queue</h2>" + table(["#", "When (ET)", "Series", "Topic", "Rights", "Status", ""], rows) + "</section>")
    eps = sorted((ROOT / "episodes").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:12]
    rows = []
    for e in eps:
        slug = e.stem
        out = ROOT / "output" / slug
        short = out / f"{slug}-short.mp4"
        qcj = out / f"{slug}-short.qc.json"
        qc = json.loads(qcj.read_text()) if qcj.exists() else None
        draft = json.loads((out / "draft.json").read_text()) if (out / "draft.json").exists() else None
        rows.append([esc(slug), media_link(short), media_link(out / "cover.jpg"),
                     "-" if not qc else f"<span class={'ok' if qc['passed'] else 'bad'}>{'PASS' if qc['passed'] else 'FAIL'}</span> "
                                        f"{qc['fails']}f/{qc['warns']}w",
                     esc(draft["status"]) if draft else "-", button("render", slug) + button("publish-draft", slug)])
    parts.append("<section><h2>Episodes (newest 12)</h2>" + table(["Episode", "Short", "Cover", "QC", "Draft", ""], rows) + "</section>")
    rows = []
    for p in db.rows(c, "SELECT * FROM projects ORDER BY updated_at DESC LIMIT 12"):
        pdir = ROOT / "projects" / p["id"]
        rows.append([esc(p["id"]), esc(p["destination"]), esc(p["status"]), esc(", ".join(json.loads(p["steps"] or "[]"))),
                     media_link(pdir / f"{p['id']}.mp4"), media_link(pdir / "captions_review.md"),
                     button("resume-project", p["id"]) + ("" if (pdir / "captions.approved").exists() else button("approve-captions", p["id"]))])
    parts.append("<section><h2>Clip projects</h2>" + table(["Project", "Destination", "Status", "Steps done", "Video", "Caption review", ""], rows) + "</section>")
    rows = [[j["id"], esc(j["action"]), esc(j["target"][:40]), f"<span class={'ok' if j['status'] == 'done' else 'bad' if j['status'] == 'failed' else ''}>{esc(j['status'])}</span>",
             esc((j["started_at"] or "")[11:19]), esc((j["finished_at"] or "")[11:19]), media_link(j["log"]) if j["log"] else "-"]
            for j in db.rows(c, "SELECT * FROM jobs ORDER BY id DESC LIMIT 10")]
    parts.append("<section><h2>Jobs</h2>" + button("scan", "", "Scan moments") + button("report", "") + button("tests", "") +
                 table(["#", "Action", "Target", "Status", "Started", "Finished", "Log"], rows) + "</section>")
    try:
        aud = db.rows(c, "SELECT at, subject, destination, ok, reasons FROM rights_audit ORDER BY id DESC LIMIT 8")
    except Exception:
        aud = []
    reg = json.loads((ROOT / "rights" / "registry.json").read_text())
    parts.append("<section><h2>Rights</h2>" + table(["Record", "Status", "Destinations"], [[esc(r["id"]), esc(r["status"]), esc(", ".join(r["destinations_allowed"]) or "nowhere")] for r in reg])
                 + "<h3>Latest decisions (append-only log)</h3>" + table(["At", "Subject", "Destination", "OK", "Reasons"],
                 [[esc(a["at"][11:19]), esc(a["subject"][-48:]), esc(a["destination"]), "yes" if a["ok"] else "<span class=bad>no</span>", esc("; ".join(json.loads(a["reasons"]))[:120])] for a in aud]) + "</section>")
    camps = [json.loads(f.read_text()) for f in sorted((ROOT / "content" / "campaigns").glob("*.json")) if not f.name.startswith("_")]
    pay = db.rows(c, "SELECT campaign, status, SUM(amount_usd) usd FROM payouts GROUP BY campaign, status")
    parts.append("<section><h2>Campaigns (posted on ClipCircuit)</h2>" + table(["Campaign", "Status", "Pay", "Budget left"],
                 [[esc(x["name"]), esc(str(x.get("status", ""))[:40]), esc(x.get("rate_per_1000_views") and f"${x['rate_per_1000_views']}/1K" or (x.get("pool") and f"pool ${x['pool']:,}") or "?"), esc(x.get("budget_left", "-"))] for x in camps])
                 + "<p>Money recorded: " + esc(", ".join("{} {} ${:.2f}".format(p["campaign"], p["status"], p["usd"]) for p in pay)
                                                or "none ($0 received)") + "</p></section>")
    costs = db.rows(c, "SELECT provider, unit, SUM(units) u FROM costs GROUP BY provider, unit")
    parts.append("<section><h2>Costs</h2><p>" + esc(", ".join(f"{x['provider']}: {x['u']:g} {x['unit']}" for x in costs) or "none")
                 + ". Paid credits spent by this system: 0.</p></section>")
    return f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Vice Replay Control</title><style>
:root{{--bg:#0f0a1e;--card:#1a1233;--ink:#f3eefe;--muted:#a99cc9;--pink:#ff1f8e;--cyan:#00e5d2;--line:#2e2452}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{padding:14px 16px;border-bottom:2px solid var(--pink);display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}}
h1{{margin:0;font-size:20px;letter-spacing:.5px}} h1 b{{color:var(--pink)}} h1 i{{color:var(--cyan);font-style:normal}}
main{{padding:8px 16px 40px;max-width:1200px;margin:auto}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:14px 0}}
h2{{font-size:15px;margin:4px 0 10px;color:var(--cyan)}} h3{{font-size:13px;color:var(--muted)}} .big{{font-size:16px}}
.scroll{{overflow-x:auto}} table{{border-collapse:collapse;width:100%}} th,td{{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--muted);font-weight:600;font-size:12px}} a{{color:var(--cyan)}} .muted{{color:var(--muted)}} .ok{{color:var(--cyan)}} .bad{{color:var(--pink)}}
button{{background:transparent;color:var(--ink);border:1px solid var(--pink);border-radius:6px;padding:3px 8px;margin:2px;cursor:pointer}} button:hover{{background:var(--pink)}}
</style></head><body><header><h1><b>VICE</b> <i>REPLAY</i> control</h1><span class=muted>local only · jobs run one at a time · no upload button (approve in chat)</span></header>
<main>{''.join(parts)}</main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            return self.send(200, page())
        if u.path == "/jobs.json":
            return self.send(200, json.dumps(db.rows(con(), "SELECT * FROM jobs ORDER BY id DESC LIMIT 50")), "application/json")
        if u.path == "/file":
            rel = urllib.parse.parse_qs(u.query).get("p", [""])[0]
            f = (ROOT / rel).resolve()
            allowed = any(f.is_relative_to(ROOT / d) for d in ("output", "projects", "reports"))
            if not allowed or not f.is_file():
                return self.send(404, "not found")
            ctype = {".mp4": "video/mp4", ".jpg": "image/jpeg", ".png": "image/png", ".md": "text/plain; charset=utf-8",
                     ".log": "text/plain; charset=utf-8", ".json": "application/json"}.get(f.suffix, "application/octet-stream")
            return self.send(200, f.read_bytes(), ctype)
        return self.send(404, "not found")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        form = urllib.parse.parse_qs(self.rfile.read(n).decode())
        if form.get("token", [""])[0] != TOKEN:
            return self.send(403, "bad token")
        try:
            enqueue(form.get("action", [""])[0], form.get("target", [""])[0])
        except ValueError as e:
            return self.send(400, str(e))
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


def serve(port=8765, host="127.0.0.1"):
    n = recover()
    stop = threading.Event()
    threading.Thread(target=worker, args=(stop,), daemon=True).start()
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"Vice Replay control: http://{host}:{port}  ({n} interrupted job(s) re-queued; Ctrl+C to stop)")
    try:
        srv.serve_forever()
    finally:
        stop.set()
