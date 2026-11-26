"""Verified affiliate revenue from official Associates Central exports (owner Phase 8 #11: "Accept official reporting
exports. Validate report dates. Prevent duplicate imports. Separate orders from shipped items. Account for returns.
Record verified commissions. Separate tracking IDs where available. Preserve financial privacy. Avoid storing
unnecessary account information... Do not invent revenue numbers.").

The owner downloads a report in Associates Central (Reports -> Download Reports: Earnings, Orders or Tracking ID
summary, CSV) and drops the file anywhere in the checkout; then:

    python -m studio.revenue import <report.csv>     # validate + add (refuses the same file or rows twice)
    python -m studio.revenue summary                  # verified totals; "unavailable" when nothing was imported

Only daily aggregates per tracking ID (+ product ASIN/category for "best products") are kept, in
content/revenue/ledger.json. The raw report is never copied or committed. Earnings = Amazon's "Ad Fees" on SHIPPED
items minus returns (that is the verified commission); orders are only orders (they can still be cancelled/returned).
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "content" / "revenue" / "ledger.json"
OUR_TAGS = {"vicereplay-20"}


def _num(x):
    x = re.sub(r"[^0-9.\-]", "", str(x or ""))
    return float(x) if x not in ("", "-", ".") else 0.0


def _date(x):
    x = str(x or "").strip()
    for cand in (x, x[:10], x[:19]):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d %H:%M:%S", "%B %d, %Y"):
            try:
                return dt.datetime.strptime(cand, fmt).date()
            except ValueError:
                continue
    return None


def _col(row, *names):
    low = {k.strip().lower(): v for k, v in row.items() if k}
    for n in names:
        for k, v in low.items():
            if k.startswith(n):
                return v
    return None


def parse(text):
    """(kind, rows, (from, to)) from an Associates Central CSV export (title line(s) optional)."""
    lines = text.splitlines()
    rng = None
    m = re.search(r"from (\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}-\d{2}-\d{2}) to (\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}-\d{2}-\d{2})",
                  " ".join(lines[:3]), re.I)
    if m:
        rng = (_date(m.group(1)), _date(m.group(2)))
    start = next((i for i, l in enumerate(lines) if re.search(r"tracking id|tag|asin", l, re.I) and "," in l), None)
    if start is None:
        raise ValueError("not an Associates Central report (no header with Tracking ID / ASIN)")
    rows = list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))
    head = " ".join(h.lower() for h in rows[0].keys()) if rows else lines[start].lower()
    kind = ("earnings" if "ad fees" in head or "items shipped" in head else
            "tracking" if "clicks" in head else "orders" if "qty" in head or "ordered" in head else None)
    if not kind:
        raise ValueError(f"unknown report type (columns: {head[:120]})")
    return kind, rows, rng


def normalize(kind, rows, rng=None, today=None):
    """Aggregated records + problems. Each record: kind, date, tag, asin, category, clicks, ordered, shipped,
    returned, sales, earnings (USD)."""
    today = today or dt.date.today()
    out, probs = [], []
    for i, r in enumerate(rows, 1):
        tag = (_col(r, "tracking id", "tag") or "").strip()
        d = _date(_col(r, "date shipped", "date") or "") if kind != "tracking" else (rng[1] if rng else None)
        if kind != "tracking" and not d:
            probs.append(f"row {i}: no valid date")
            continue
        if d and d > today:
            probs.append(f"row {i}: date {d} is in the future")
            continue
        if rng and d and not (rng[0] <= d <= rng[1]):
            probs.append(f"row {i}: date {d} outside the report's range {rng[0]}..{rng[1]}")
            continue
        rec = {"kind": kind, "date": d.isoformat() if d else None, "tag": tag,
               "asin": (_col(r, "asin") or "").strip() or None, "category": (_col(r, "category") or "").strip() or None,
               "clicks": int(_num(_col(r, "clicks"))) if kind == "tracking" else 0,
               "ordered": int(_num(_col(r, "items ordered", "qty"))) if kind in ("orders", "tracking") else 0,
               "shipped": int(_num(_col(r, "items shipped"))) if kind in ("earnings", "tracking") else 0,
               "returned": int(_num(_col(r, "returns"))) if kind in ("earnings", "tracking") else 0,
               "sales": round(_num(_col(r, "revenue", "price")), 2) if kind != "orders" else 0.0,
               "earnings": round(_num(_col(r, "ad fees", "earnings")), 2) if kind in ("earnings", "tracking") else 0.0}
        if tag and tag not in OUR_TAGS:
            probs.append(f"row {i}: tracking ID {tag!r} isn't ours ({', '.join(sorted(OUR_TAGS))}): kept separate")
        out.append(rec)
    return out, probs


def _key(rec):
    return hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:20]


def load():
    try:
        return json.loads(LEDGER.read_text())
    except (OSError, ValueError):
        return {"imports": {}, "records": {}}


def import_file(path, ledger=None, today=None, write=True):
    raw = Path(path).read_bytes()
    fh = hashlib.sha256(raw).hexdigest()
    led = ledger if ledger is not None else load()
    if fh in led["imports"]:
        raise ValueError(f"this exact report was already imported on {led['imports'][fh]['at']}")
    kind, rows, rng = parse(raw.decode("utf-8-sig", errors="replace"))
    recs, probs = normalize(kind, rows, rng, today)
    added = dup = 0
    for r in recs:
        k = _key(r)
        if k in led["records"]:
            dup += 1
            continue
        led["records"][k] = r
        added += 1
    led["imports"][fh] = {"at": dt.datetime.now(dt.timezone.utc).isoformat()[:19], "kind": kind,
                          "range": [str(rng[0]), str(rng[1])] if rng else None, "rows": len(rows), "added": added,
                          "duplicates": dup, "problems": probs[:20]}
    if write:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(led, indent=1) + "\n")
    return {"kind": kind, "added": added, "duplicates": dup, "problems": probs}


def summary(ledger=None):
    led = ledger if ledger is not None else load()
    recs = [r for r in led.get("records", {}).values() if not r.get("tag") or r["tag"] in OUR_TAGS]
    if not recs:
        return None
    s = {"clicks": sum(r["clicks"] for r in recs), "ordered": sum(r["ordered"] for r in recs),
         "shipped": sum(r["shipped"] for r in recs), "returned": sum(r["returned"] for r in recs),
         "verified_earnings_usd": round(sum(r["earnings"] for r in recs if r["kind"] in ("earnings", "tracking")), 2),
         "dates": [min(r["date"] for r in recs if r["date"]), max(r["date"] for r in recs if r["date"])]
         if any(r["date"] for r in recs) else None}
    by = {}
    for r in recs:
        if r["asin"] and r["kind"] == "earnings":
            b = by.setdefault(r["asin"], {"category": r["category"], "shipped": 0, "earnings": 0.0})
            b["shipped"] += r["shipped"] - r["returned"]
            b["earnings"] = round(b["earnings"] + r["earnings"], 2)
    s["top_products"] = sorted(by.items(), key=lambda kv: -kv[1]["earnings"])[:5]
    s["conversion"] = round(s["ordered"] / s["clicks"], 4) if s["clicks"] else None
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.revenue")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("import")
    p.add_argument("file")
    sub.add_parser("summary")
    a = ap.parse_args(argv)
    if a.cmd == "import":
        try:
            r = import_file(a.file)
        except ValueError as e:
            print(f"NOT IMPORTED: {e}")
            sys.exit(1)
        print(f"imported {r['kind']} report: {r['added']} new rows, {r['duplicates']} already in the ledger")
        for pr in r["problems"][:10]:
            print("  ! " + pr)
        return
    s = summary()
    if not s:
        print("affiliate revenue: unavailable (no Associates Central report imported yet)")
        return
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
