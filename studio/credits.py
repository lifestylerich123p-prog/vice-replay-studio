"""Everygen credit accounting: provider-verified balances reconciled against the claim ledger (owner Nov 26, Phase 3:
"An estimate is not sufficient for automated financial management... never report an estimate as an exact balance").

Two sources, never mixed up:
* VERIFIED balance: what Everygen itself reports (the MCP tool `get_credit_balance`), recorded with the time it was
  read: `python -m studio.credits record --remaining 74 --purchased 74 --sub-remaining 0 --sub-used 500 --sub-max 500`
  (content/learn/credits.jsonl). A reading older than VERIFIED_H hours is shown as UNVERIFIED.
* LEDGER spends: every paid call is claimed and closed in studio.everygen_claim (branch claude/everygen-ledger), with
  the credits each request used. That gives per-request, per-episode, daily and monthly spending, plus pending
  (claimed, not closed) and failed/released requests.

Reconciliation: between two verified readings the balance should drop by the ledger's spends. A bigger drop is
"spent outside this ledger" (the account is shared with What If Arena and ClipCircuit) and is reported, not guessed.

    python -m studio.credits show            # balance (verified or not), spends, pending, reconciliation
    python -m studio.credits record --remaining N [--purchased N --sub-remaining N --sub-used N --sub-max N]
"""
import argparse
import datetime as dt
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPS = ROOT / "content" / "learn" / "credits.jsonl"
VERIFIED_H = 24


def _now():
    return dt.datetime.now(dt.timezone.utc)


def _ts(s):
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def snapshots(path=None):
    p = Path(path or SNAPS)
    out = []
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return sorted(out, key=lambda r: r["t"])


def record(remaining, purchased=None, sub_remaining=None, sub_used=None, sub_max=None, note="", path=None, t=None):
    """Store one provider-reported reading (call only with numbers Everygen returned)."""
    row = {"t": (t or _now()).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "everygen get_credit_balance",
           "remaining": int(remaining)}
    for k, v in (("purchased_remaining", purchased), ("subscription_remaining", sub_remaining),
                 ("subscription_used", sub_used), ("subscription_max", sub_max)):
        if v is not None:
            row[k] = int(v)
    if note:
        row["note"] = note
    p = Path(path or SNAPS)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def _slug(job):
    parts = job.split(":")
    return parts[1] if len(parts) > 2 or (len(parts) == 2 and parts[0] in ("voice", "image", "video")) else job


def ledger_summary(rows, now=None):
    """Spends (done), pending (open claims) and failed/released requests from the claim ledger rows."""
    now = now or _now()
    open_claims, spends, failed = {}, [], []
    for r in rows:
        job, act = r.get("job", ""), r.get("act")
        if act == "claim":
            open_claims[job] = r
        elif act == "done":
            c = open_claims.pop(job, {})
            spends.append({"t": r["t"], "job": job, "credits": int(r.get("credits") or c.get("credits") or 0),
                           "chat": r.get("chat"), "what": c.get("what", ""),
                           "balance_reported": None if str(r.get("balance", "?")) in ("?", "", "None")
                           else r.get("balance")})
        elif act in ("release", "failed"):
            c = open_claims.pop(job, {})
            failed.append({"t": r["t"], "job": job, "act": act, "reason": r.get("reason", ""),
                           "credits_claimed": int(c.get("credits") or 0)})
    spends = [s for s in spends if s["credits"] > 0 or s["job"].startswith(("voice:", "image:", "video:", "clips:"))]
    day, month, episode = defaultdict(int), defaultdict(int), defaultdict(int)
    for s in spends:
        t = _ts(s["t"])
        day[t.strftime("%Y-%m-%d")] += s["credits"]
        month[t.strftime("%Y-%m")] += s["credits"]
        episode[_slug(s["job"])] += s["credits"]
    pending = [{"job": j, "credits": int(c.get("credits") or 0), "since": c["t"], "chat": c.get("chat"),
                "stale": (now - _ts(c["t"])).total_seconds() > 3 * 3600} for j, c in open_claims.items()
               if not j.startswith("setup:")]
    return {"spends": spends, "pending": pending, "failed": failed, "per_day": dict(day), "per_month": dict(month),
            "per_episode": dict(episode)}


def reconcile(snaps, spends):
    """For each pair of verified readings: drop in balance vs credits the ledger says were spent in between."""
    out = []
    for a, b in zip(snaps, snaps[1:]):
        ta, tb = _ts(a["t"]), _ts(b["t"])
        logged = sum(s["credits"] for s in spends if ta < _ts(s["t"]) <= tb)
        drop = a["remaining"] - b["remaining"]
        out.append({"from": a["t"], "to": b["t"], "balance_drop": drop, "ledger_spent": logged,
                    "unexplained": drop - logged,
                    "note": ("matches the ledger" if drop == logged else
                             "balance went UP (top-up or monthly plan credits)" if drop < 0 else
                             f"{drop - logged} credits spent outside this ledger (What If Arena / ClipCircuit share "
                             "the account) or not logged" if drop > logged else
                             f"ledger says {logged - drop} more than the balance dropped (a refund or a failed request "
                             "logged as done)")})
    return out


def summary(rows=None, snaps=None, now=None):
    now = now or _now()
    if rows is None:
        from . import everygen_claim
        try:
            _, rows = everygen_claim.fetch_ledger()
        except Exception as e:  # GitHub out: say so, never guess
            rows, err = [], str(e)
        else:
            err = ""
    else:
        err = ""
    snaps = snapshots() if snaps is None else snaps
    led = ledger_summary(rows, now)
    last = snaps[-1] if snaps else None
    bal = {"verified": False, "remaining": None, "read_at": None, "spent_since": 0, "estimate": None}
    if last:
        age_h = (now - _ts(last["t"])).total_seconds() / 3600
        since = sum(s["credits"] for s in led["spends"] if _ts(s["t"]) > _ts(last["t"]))
        bal.update(read_at=last["t"], age_h=round(age_h, 1), spent_since=since,
                   subscription=last.get("subscription_remaining"), purchased=last.get("purchased_remaining"))
        if age_h <= VERIFIED_H and since == 0:
            bal.update(verified=True, remaining=last["remaining"])
        else:
            bal["estimate"] = last["remaining"] - since
    return {"balance": bal, "ledger": led, "reconcile": reconcile(snaps, led["spends"]), "ledger_error": err}


def lines(s):
    b, led = s["balance"], s["ledger"]
    out = []
    if b["verified"]:
        out.append(f"Everygen: {b['remaining']} credits VERIFIED (provider reading {b['read_at']}, "
                   f"{b.get('purchased')} purchased + {b.get('subscription')} plan)")
    elif b["read_at"]:
        out.append(f"Everygen: UNVERIFIED. Last provider reading {b['read_at']} ({b['age_h']} h ago); ledger spends since "
                   f"then {b['spent_since']} -> ESTIMATE {b['estimate']} (read get_credit_balance and record it)")
    else:
        out.append("Everygen: UNVERIFIED, no provider reading recorded (python -m studio.credits record ...)")
    month = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m")
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    out.append(f"  Vice Replay ledger: today {led['per_day'].get(today, 0)}, this month {led['per_month'].get(month, 0)} "
               f"credits; {len(led['spends'])} paid requests logged")
    if led["per_episode"]:
        top = sorted(led["per_episode"].items(), key=lambda x: -x[1])[:5]
        out.append("  per episode: " + ", ".join(f"{k} {v}" for k, v in top))
    for p in led["pending"]:
        out.append(f"  PENDING claim {p['job']} ({p['credits']} cr) since {p['since']}" + (" (stale: check it)" if p["stale"] else ""))
    for f in led["failed"][-3:]:
        out.append(f"  released/failed {f['job']} ({f['reason'][:60]})")
    for r in s["reconcile"][-2:]:
        out.append(f"  reconcile {r['from'][:16]} -> {r['to'][:16]}: balance -{r['balance_drop']}, ledger "
                   f"{r['ledger_spent']}: {r['note']}")
    if s["ledger_error"]:
        out.append(f"  ledger unreachable: {s['ledger_error'][:100]}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.credits")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="store a reading Everygen's get_credit_balance returned")
    r.add_argument("--remaining", type=int, required=True)
    r.add_argument("--purchased", type=int)
    r.add_argument("--sub-remaining", type=int)
    r.add_argument("--sub-used", type=int)
    r.add_argument("--sub-max", type=int)
    r.add_argument("--note", default="")
    s = sub.add_parser("show")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "record":
        print(json.dumps(record(a.remaining, a.purchased, a.sub_remaining, a.sub_used, a.sub_max, a.note)))
        return
    res = summary()
    print(json.dumps(res, indent=1) if a.json else "\n".join(lines(res)))


if __name__ == "__main__":
    main()
