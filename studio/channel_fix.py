"""Apply a channel cleanup plan (content/archive/channel_fixes.json) to the Vice Replay channel. Owner approval required.

    python -m studio.channel_fix content/archive/channel_fixes.json            # apply
    python -m studio.channel_fix content/archive/channel_fixes.json --dry-run  # show what would change

For each listed video: category -> Gaming, adds tags (keeps existing), appends the "not affiliated" line if
missing, adds the Spanish title/description, and adds the video to its playlist (skips if already there).
For the channel: description, keywords, default language, country. Titles and existing text are never removed.
"""
import argparse
import json
import sys
from pathlib import Path

from .youtube_upload import add_to_playlist, req, token

YT = "https://youtube.googleapis.com/youtube/v3/"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text())
    tok = token()
    report = []

    # channel settings
    ch, _ = req("GET", YT + "channels?part=brandingSettings,snippet&mine=true", tok)
    c = ch["items"][0]
    plan.setdefault("channel", {})
    b = c.get("brandingSettings", {"channel": {}})
    b.setdefault("channel", {})
    want = plan["channel"] or {}
    changes = {k: v for k, v in want.items() if b["channel"].get(k) != v}
    if changes and want:
        b["channel"].update(changes)
        report.append(f"channel: {', '.join(changes)}")
        if not a.dry_run:
            req("PUT", YT + "channels?part=brandingSettings", tok, {"id": c["id"], "brandingSettings": b})

    # videos
    ids = [v["id"] for v in plan["videos"]]
    r, _ = req("GET", YT + "videos?part=snippet,localizations&id=" + ",".join(ids), tok)
    current = {v["id"]: v for v in r.get("items", [])}
    line = plan.get("not_affiliated_line", "Vice Replay is a fan channel and is not affiliated with Rockstar Games.")
    for item in plan["videos"]:
        v = current.get(item["id"])
        if not v:
            report.append(f"{item['id']}: not found, skipped")
            continue
        sn = v["snippet"]
        did = []
        body_sn = {"title": sn["title"], "description": sn.get("description", ""), "categoryId": sn.get("categoryId"),
                   "tags": sn.get("tags", []), "defaultLanguage": sn.get("defaultLanguage") or "en"}
        if body_sn["categoryId"] != "20":
            body_sn["categoryId"] = "20"
            did.append("category->Gaming")
        if "not affiliated" not in body_sn["description"].lower():
            body_sn["description"] = (body_sn["description"].rstrip() + "\n\n" + line)[:4900]
            did.append("not-affiliated line")
        from . import affiliate  # Phase 6 #6: no affiliate links while the Associates account is unconfirmed
        if item.get("append") and affiliate.active() and "tag=vicereplay-20" not in body_sn["description"]:
            body_sn["description"] = (body_sn["description"].rstrip() + "\n\n" + item["append"])[:4900]
            did.append("affiliate links")
        tags = list(dict.fromkeys(body_sn["tags"] + plan.get("common_tags", []) + item.get("tags", [])))[:30]
        if tags != body_sn["tags"]:
            body_sn["tags"] = tags
            did.append(f"tags ({len(tags)})")
        loc = v.get("localizations", {})
        parts = "snippet"
        body = {"id": item["id"], "snippet": body_sn}
        if item.get("es") and "es" not in loc:
            loc["es"] = {"title": item["es"]["title"][:100],
                         "description": (item["es"]["description"] + "\n\n" + line)[:4900]}
            body["localizations"] = loc
            parts += ",localizations"
            did.append("Spanish title/description")
        if did and not a.dry_run:
            req("PUT", YT + f"videos?part={parts}", tok, body)
        if item.get("playlist") and not a.dry_run:
            try:
                add_to_playlist(tok, item["id"], item["playlist"])
                did.append(f"playlist '{item['playlist']}'")
            except SystemExit as e:
                did.append(f"playlist failed: {e}")
        report.append(f"{item['id']} ({sn['title'][:40]}): " + (", ".join(did) or "already fine"))
    print(("DRY RUN, nothing changed:\n" if a.dry_run else "Applied:\n") + "\n".join("- " + x for x in report))


if __name__ == "__main__":
    main()
