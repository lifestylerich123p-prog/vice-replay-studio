"""/vice report: one page of channel performance, production queue, rights, campaigns and costs, plus CSV/JSON
exports of every table (reports/exports/<date>/). Reads the latest audit/discover/scan outputs; free."""
import csv
import json
from pathlib import Path

from . import db

ROOT = db.ROOT
TABLES = ["channel_snapshots", "metric_snapshots", "competitor_channels", "competitor_videos", "candidates",
          "projects", "qc_reports", "rights", "campaigns", "payouts", "costs", "ideas", "used_footage"]


def latest(pattern):
    files = sorted(ROOT.glob(pattern))
    return json.loads(files[-1].read_text()) if files else None


def export(con, day):
    out = ROOT / "reports" / "exports" / day
    out.mkdir(parents=True, exist_ok=True)
    for t in TABLES:
        rows = db.rows(con, f"SELECT * FROM {t}")
        (out / f"{t}.json").write_text(json.dumps(rows, indent=0, default=str))
        with (out / f"{t}.csv").open("w", newline="") as f:
            if rows:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
    return out


def run():
    con = db.connect()
    day = db.now()[:10]
    audit = latest("reports/audit-*.json")
    comp = latest("research/competitors/competitors-*.json")
    L = [f"# Vice Replay report ({db.now()})", ""]
    snaps = db.rows(con, "SELECT * FROM channel_snapshots ORDER BY taken_at")
    if snaps:
        f, l = snaps[0], snaps[-1]
        L += ["## Channel growth (public counters, append-only snapshots)", "",
              f"{f['taken_at'][:16]}: {f['subs']} subs, {f['views']:,} views, {f['videos']} videos -> "
              f"{l['taken_at'][:16]}: {l['subs']} subs, {l['views']:,} views, {l['videos']} videos ({len(snaps)} snapshots)", ""]
    if audit:
        daily = audit.get("daily") or []
        if daily:
            L += ["Daily (YouTube Analytics): " + ", ".join(f"{d['day'][5:]} {d['views']}v +{d['subscribersGained']}s"
                                                       for d in daily[-8:]), ""]
        L += ["## Series performance (from the latest audit)", "", "| Type | Series | Videos | Median views | Median 24 h | Engaged % |",
              "|---|---|---|---|---|---|"]
        L += [f"| {g['type']} | {g['series']} | {g['n']} | {g['median_views']} | {g['median_views_24h'] or '-'} | {g['median_engaged_rate'] or '-'} |"
              for g in audit["groups"]]
        L += ["", "## Videos needing investigation", ""] + [f"- {x['title']}: {'; '.join(x['why'])}" for x in audit["flags"][:8]]
    if comp:
        top = sorted(comp["profiles"], key=lambda p: -(p["median_views"] or 0))[:5]
        L += ["", "## Competitor research (latest)", ""] + [
            f"- {p['title']}: {p['subs']:,} subs, median {p['median_views']:,} views, {p['uploads_per_day_7d']}/day, "
            f"median {p['median_seconds']} s" for p in top]
        trends = [k for k, t in comp["title_trends"].items() if t["trend"]]
        L.append(f"- Title structures used by 3+ channels: {', '.join(trends)}")
    ideas = db.rows(con, "SELECT * FROM ideas ORDER BY day, slot")
    if ideas:
        L += ["", "## Upcoming ideas (14-day calendar)", "", "| Day | Date | Series | Topic | Rights | Status |", "|---|---|---|---|---|---|"]
        for i in ideas[:10]:
            d = json.loads(i["data"])
            L.append(f"| {i['day']} | {i['date']} | {i['series']} | {i['topic']} | {d['rights_status'][:40]} | {i['status']} |")
    projects = db.rows(con, "SELECT id, kind, series, status, destination, rights_ids, error FROM projects ORDER BY updated_at DESC")
    L += ["", "## Production queue and publishing status", "", "| Project | Kind | Destination | Rights | Status |", "|---|---|---|---|---|"]
    L += [f"| {p['id']} | {p['kind']} | {p['destination']} | {', '.join(json.loads(p['rights_ids'] or '[]')) or '-'} | {p['status']} |"
          for p in projects] or ["| - | | | | |"]
    qcs = db.rows(con, "SELECT video, passed, created_at FROM qc_reports ORDER BY id DESC LIMIT 6")
    L += ["", "QC (latest): " + "; ".join(f"{Path(q['video']).name} {'PASS' if q['passed'] else 'FAIL'}" for q in qcs)]
    rights = db.rows(con, "SELECT id, status, destinations_allowed FROM rights")
    L += ["", "## Rights registry", ""] + [f"- {r['id']}: {r['status']} for {r['destinations_allowed']}" for r in rights]
    tracker = (ROOT / "content" / "campaigns" / "tracker.md").read_text().splitlines()
    pending = [l for l in tracker if l.startswith("| 2026") and l.split("|")[7].strip() == ""]
    L += ["", "## Campaigns", "", f"Pending submissions in tracker.md (no 'Submitted at'): {len(pending)}",
          "Verified payouts: " + (", ".join(f"{r['campaign']} {r['status']} ${r['usd']:.2f}" for r in db.rows(
              con, "SELECT campaign, status, SUM(amount_usd) usd FROM payouts GROUP BY campaign, status")) or "none recorded ($0 received)")]
    costs = db.rows(con, "SELECT provider, unit, SUM(units) units, SUM(usd) usd, COUNT(*) n FROM costs GROUP BY provider, unit")
    L += ["", "## Costs (logged)", ""] + [f"- {c['provider']}: {c['units']:g} {c['unit']} over {c['n']} calls, ${c['usd']:.2f}" for c in costs]
    L += ["- Rendering: local ffmpeg/Kokoro/faster-whisper, $0 (time only). Everygen credits: none spent by this system."]
    exp = export(con, day)
    L += ["", f"Exports (CSV + JSON of every table): `{exp.relative_to(ROOT)}/`"]
    out = ROOT / "reports" / f"report-{day}.md"
    out.write_text("\n".join(L) + "\n")
    return out
