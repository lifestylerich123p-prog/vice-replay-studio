"""14-day plan (content/vice-calendar.json): 28 distinct ideas, synced into the database, rendered as Markdown + CSV.

    python -m studio.vice calendar    # reports/calendar.md + reports/calendar.csv
    python -m studio.vice batch       # the next ideas that can be made now (rights clear, no recording needed)

Nothing is generated or published automatically; each idea still goes research -> episode -> ship -> QC -> approval.
"""
import csv
import json

from . import db

ROOT = db.ROOT
CAL = ROOT / "content" / "vice-calendar.json"
COLS = ["id", "date", "slot_et", "series", "topic", "payoff", "footage", "rights_status", "format", "editing",
        "effort", "cost", "research", "status"]


def load():
    return json.loads(CAL.read_text())


def sync(con=None):
    con = con or db.connect()
    for i in load():
        con.execute("INSERT OR REPLACE INTO ideas VALUES (?,?,?,?,?,?,?,?)",
                    (i["id"], i["day"], i["date"], i["slot_et"], i["series"], i["topic"], json.dumps(i), i["status"]))
    con.commit()


def ready(i):
    return not i["rights_status"].startswith("BLOCKED") and i["status"].startswith(("idea", "rendered"))


def run():
    sync()
    items = load()
    md = ROOT / "reports" / "calendar.md"
    L = ["# 14-day plan: 28 distinct Shorts (Nov 22 - Dec 5)", "",
         "Two quality-checked Shorts a day, each a different format. 'BLOCKED until recorded' ideas need the owner's own "
         "gameplay (Drive shot list); swap in a ready idea if it isn't recorded in time. Times are US Eastern.", "",
         "| # | Date | Time | Series | Topic | Payoff | Rights | Effort | Status |", "|---|---|---|---|---|---|---|---|---|"]
    for i in items:
        L.append(f"| {i['id']} | {i['date'][5:]} | {i['slot_et']} | {i['series']} | {i['topic']} | {i['payoff']} | "
                 f"{i['rights_status'].split(':')[0]} | {i['effort']} | {i['status']} |")
    by = {}
    for i in items:
        by.setdefault(i["series"], 0)
        by[i["series"]] += 1
    L += ["", "Mix: " + ", ".join(f"{k} {v}" for k, v in by.items()),
          f"Ready to make now: {sum(ready(i) for i in items)}; waiting for owner recordings: "
          f"{sum(i['rights_status'].startswith('BLOCKED') for i in items)}.", "",
          "Full fields (footage, format, editing, research, cost) are in content/vice-calendar.json and reports/calendar.csv."]
    md.write_text("\n".join(L) + "\n")
    with (ROOT / "reports" / "calendar.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(items)
    return md


def batch(n=4):
    sync()
    nxt = [i for i in load() if ready(i) and not i["status"].startswith("rendered")][:n]
    for i in nxt:
        print(f"{i['id']} {i['date']} {i['slot_et']} [{i['series']}] {i['topic']}\n   research: {i['research']}\n"
              f"   then: python -m studio.vice create \"{i['topic']}\"  (or rank) -> fill sources -> python -m studio.ship")
    return nxt
