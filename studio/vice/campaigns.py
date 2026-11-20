"""/vice campaigns: clipping campaign registry, eligibility and payout math (estimates kept apart from real money).

Inputs: content/campaigns/*.json (campaigns the owner joined/approved) + the latest research/campaigns/scan-*.json
(public research; every number there is "re-verify on the live page"). Nothing is joined or submitted here.

Money states, never mixed: estimated (our math on verified views) -> approved (the campaign approved the views)
-> received (the payout arrived). Only the owner records approved/received:
    python -m studio.vice campaigns --record kreekcraft-gta6 --clip <url> --status approved --amount 4.20 --views 4200
"""
import json
from pathlib import Path

from . import db

ROOT = db.ROOT
FEE_ESTIMATE = 0.10  # Content Rewards platform fee (sources disagree who pays it: assume the creator, worst case)
CLIPCIRCUIT = "UCgmVgDyZV-XuHmFl99zDnkw"


def joined():
    out = {}
    for f in sorted((ROOT / "content" / "campaigns").glob("*.json")):
        if f.name.startswith("_"):
            continue
        out[f.stem] = json.loads(f.read_text())
    return out


def latest_scan():
    scans = sorted((ROOT / "research" / "campaigns").glob("scan-*.json"))
    return (json.loads(scans[-1].read_text()), scans[-1].name) if scans else (None, None)


def payout(c, views):
    """Estimated gross and net for one clip with `views` verified views (per-view campaigns only)."""
    rate = c.get("rate_per_1000_views") or c.get("pay_per_1k_views_usd")
    if c.get("pay_type") == "pool" or not isinstance(rate, (int, float)):
        return {"type": "pool or unknown rate", "gross": None, "net": None,
                "note": "pool share depends on everyone's approved views; $0 unless the per-creator minimum is reached"}
    min_views = c.get("min_views_to_pay") or 0
    gross = rate * views / 1000
    note = []
    if views < min_views:
        return {"type": "per-view", "gross": 0.0, "net": 0.0, "note": f"below the {min_views:,}-view minimum"}
    if c.get("min_payout_per_clip") and gross < c["min_payout_per_clip"]:
        return {"type": "per-view", "gross": 0.0, "net": 0.0, "note": f"below the ${c['min_payout_per_clip']} minimum payout"}
    cap = c.get("max_payout_per_clip")
    if cap and gross > cap:
        gross, note = cap, [f"capped at ${cap}"]
    left = c.get("budget_left")
    if isinstance(left, (int, float)) and gross > left:
        gross, note = left, note + ["limited by remaining budget"]
    return {"type": "per-view", "gross": round(gross, 2), "net": round(gross * (1 - FEE_ESTIMATE), 2),
            "note": "; ".join(note + [f"net assumes a {int(FEE_ESTIMATE * 100)}% platform fee"])}


def eligibility(c, channel_stats):
    """Requirements we can check from public data; unknowns are listed, never assumed met."""
    ok, unknown, fail = [], [], []
    rules = " ".join(c.get("rules", [])).lower()
    subs = channel_stats.get("subs", 0)
    if "100+ followers" in rules or "100+" in rules:
        (ok if subs >= 100 else fail).append(f"100+ followers rule: ClipCircuit YouTube has {subs}")
    if "%" in rules and ("us" in rules or "usa" in rules):
        unknown.append("audience country share (check ClipCircuit analytics)")
    if "engagement" in rules:
        unknown.append("engagement-rate minimum (needs per-clip numbers)")
    if c.get("owner_approved"):
        ok.append("owner approved this campaign")
    else:
        fail.append("not owner-approved: no clips until the owner says yes in chat")
    return {"ok": ok, "unknown": unknown, "fail": fail}


def ledger(con):
    rows = db.rows(con, "SELECT campaign, status, SUM(amount_usd) AS usd, SUM(views) AS views, COUNT(*) AS n "
                        "FROM payouts GROUP BY campaign, status")
    return rows


def record(campaign, clip, status, amount, views, note=""):
    con = db.connect()
    con.execute("INSERT INTO payouts (campaign, clip, status, views, amount_usd, recorded_at, note) VALUES (?,?,?,?,?,?,?)",
                (campaign, clip, status, views, amount, db.now(), note))
    con.commit()


def run():
    from .. import learn
    con = db.connect()
    st = learn.call("channels", part="statistics", id=CLIPCIRCUIT)["items"][0]["statistics"]
    stats = {"subs": int(st.get("subscriberCount", 0)), "views": int(st.get("viewCount", 0)),
             "videos": int(st.get("videoCount", 0))}
    db.log_cost(con, "youtube_data_api", 1, "quota units", "campaigns: ClipCircuit stats")
    mine = joined()
    scan, scan_name = latest_scan()
    for k, c in mine.items():
        con.execute("INSERT OR REPLACE INTO campaigns VALUES (?,?,?)", (k, db.now(), json.dumps(c)))
    con.commit()
    L = [f"# Clipping campaigns ({db.now()})", "",
         f"Clips are posted on ClipCircuit (YouTube {stats['subs']} subscribers, {stats['videos']} videos), never on Vice Replay.",
         "Estimates are our math on verified views, not money. Nothing here was joined or submitted.", "",
         "## Campaigns we joined", "",
         "| Campaign | Status | Pay | Min | Max/clip | Budget left | Platforms | Eligibility | 3K views | 10K views | 50K views |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, c in mine.items():
        el = eligibility(c, stats)
        pay = f"${c['rate_per_1000_views']}/1K" if c.get("rate_per_1000_views") else (f"pool ${c.get('pool'):,}" if c.get("pool") else "?")
        cells = []
        for v in (3000, 10000, 50000):
            p = payout(c, v)
            cells.append("pool" if p["gross"] is None else f"${p['gross']} (net ~${p['net']})")
        elig = "; ".join([f"FAIL {x}" for x in el["fail"]] + [f"? {x}" for x in el["unknown"]]) or "ok"
        L.append(f"| {c['name']} | {str(c.get('status', ''))[:30]} | {pay} | {c.get('min_views_to_pay') or c.get('pool_rule', '')[:40]} | "
                 f"{c.get('max_payout_per_clip') or '-'} | {c.get('budget_left', '-')} | {', '.join(c.get('platforms', []))} | {elig} | "
                 + " | ".join(cells) + " |")
    if scan:
        L += ["", f"## Other campaigns found ({scan_name}; numbers from search summaries, re-verify on the live page)", "",
              "| Campaign | Open? | Pay | Minimum | Platforms | Footage permission | Fit |", "|---|---|---|---|---|---|---|"]
        best = " ".join(json.dumps(scan.get("best_fit", ""))).lower()
        for c in scan["campaigns"]:
            op = c["open"]["value"] if isinstance(c.get("open"), dict) else c.get("open")
            fit = "best fit" if c["name"].split()[0].lower() in best else ""
            perm = c.get("grants_footage_permission")
            perm = perm.get("value") if isinstance(perm, dict) else perm
            L.append(f"| {c['name']} | {str(op)[:28]} | {c.get('pay_per_1k_views_usd') or '-'} | "
                     f"{str(c.get('min_qualifying_views') or '-')[:45]} | {', '.join(c.get('permitted_platforms') or [])} | "
                     f"{str(perm)[:40]} | {fit} |")
        L += ["", "Platform terms: " + json.dumps(scan.get("platform_terms", {}))[:600]]
    led = ledger(con)
    L += ["", "## Money (recorded by the owner)", ""]
    if led:
        L += ["| Campaign | Status | Clips | Views | USD |", "|---|---|---|---|---|"]
        L += [f"| {r['campaign']} | {r['status']} | {r['n']} | {r['views'] or 0:,} | ${r['usd'] or 0:.2f} |" for r in led]
    else:
        L.append("No approved or received payouts recorded yet. Estimated earnings so far: $0 (no clip has reached a paying minimum on record).")
    out = ROOT / "research" / "campaigns" / f"campaigns-{db.now()[:10]}.md"
    out.write_text("\n".join(L) + "\n")
    return out
