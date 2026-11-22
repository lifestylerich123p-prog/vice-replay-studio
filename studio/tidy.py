"""Keep the project tidy and write content/INDEX.md, the one small map every run reads first. Free: no AI, no network.

    python -m studio.tidy            # clean + rebuild the index
    python -m studio.tidy --dry-run  # only show what would be removed

What it does:
- output/: removes render work folders; removes videos already uploaded (uploaded.json) after 2 days and any other
  render after 7 days (uploaded.json is always kept, so nothing gets uploaded twice).
- media/gameplay/raw/: removes downloaded recordings older than 14 days (their highlights stay in media/gameplay/).
- content/learn/market-*.md: keeps the newest 14, moves older ones to content/archive/learn/.
- site/live.json: keeps the newest 40 updates.
- __pycache__ folders and stray .DS_Store files.
- Footage: once the owner's own gameplay reaches GAMEPLAY_TARGET highlights in media/gameplay/, retires the stock
  library: trailer clips and screenshots go to media/_retired/ (not committed; re-downloadable from
  rockstargames.com/VI/downloads), except a small core kept for website share cards, thumbnails and news about a
  specific character (anything referenced in tools/ or site/, plus the first shot of each place/character).
- Writes content/INDEX.md: every episode (date, title, YouTube ids), every website guide, the latest learning
  files and where each kind of thing lives, so runs don't spend time searching.
"""
import argparse
import json
import re
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAY = 86400


def age_days(p):
    return (time.time() - p.stat().st_mtime) / DAY


GAMEPLAY_TARGET = 30


def retire_stock(dry, gone):
    gp = ROOT / "media" / "gameplay"
    clips = [p for p in gp.glob("*") if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm", ".m4v"}] if gp.exists() else []
    if len(clips) < GAMEPLAY_TARGET:
        return
    refs = ""
    for f in list((ROOT / "tools").glob("*.py")) + list((ROOT / "site").rglob("*.json")):
        refs += f.read_text(errors="ignore")
    seen, keep = set(), set()
    for p in sorted((ROOT / "media" / "official").glob("*")):
        group = re.sub(r"-\d+$", "", p.stem)
        if p.name in refs or group not in seen:
            keep.add(p.name)
        seen.add(group)
    dest = ROOT / "media" / "_retired"
    stock = [p for p in (ROOT / "media" / "official").glob("*") if p.name not in keep]
    stock += list((ROOT / "media" / "trailer").glob("*")) if (ROOT / "media" / "trailer").exists() else []
    for p in stock:
        gone.append(f"{p.relative_to(ROOT)} -> media/_retired/ (gameplay replaces it)")
        if not dry:
            dest.mkdir(exist_ok=True)
            shutil.move(str(p), dest / p.name)


def queued_files():
    """Files the Instagram queue (content/learn/reels_queue.json) still has to post: never clean these."""
    qf = ROOT / "content" / "learn" / "reels_queue.json"
    keep = set()
    if qf.exists():
        for it in json.loads(qf.read_text()):
            if it.get("posted"):
                continue
            if it.get("video"):
                keep.add((ROOT / it["video"]).resolve())
            elif it.get("episode"):
                slug = Path(it["episode"]).stem
                name = f"{slug}-short" + ("" if it.get("item") in (None, "short") else f"-{it['item']}")
                keep.add((ROOT / "output" / slug / f"{name}.mp4").resolve())
    return keep


def clean(dry):
    gone, freed = [], 0

    def rm(p):
        nonlocal freed
        size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.is_dir() else p.stat().st_size
        freed += size
        gone.append(str(p.relative_to(ROOT)))
        if not dry:
            shutil.rmtree(p) if p.is_dir() else p.unlink()

    out = ROOT / "output"
    keep = queued_files()  # videos still waiting in the Instagram queue
    if out.exists():
        for d in out.iterdir():
            if not d.is_dir():
                if d.suffix == ".mp4" and age_days(d) > 2:
                    rm(d)
                continue
            for w in d.glob("work*"):
                # a render still running writes here: leave folders touched in the last hour alone
                if any(age_days(f) < 1 / 24 for f in [w, *w.rglob("*")]):
                    continue
                rm(w)
            uploaded = (d / "uploaded.json").exists()
            for f in d.rglob("*"):
                if f.is_file() and f.name != "uploaded.json" and f.exists() and f.resolve() not in keep:
                    if age_days(f) > 7 or (uploaded and age_days(f) > 2):
                        rm(f)
            for sub in sorted((p for p in d.rglob("*") if p.is_dir()), reverse=True):
                if sub.exists() and not any(sub.iterdir()) and not dry:
                    sub.rmdir()
    raw = ROOT / "media" / "gameplay" / "raw"
    if raw.exists():
        for f in raw.iterdir():
            if f.is_file() and age_days(f) > 14:
                rm(f)
    learn = ROOT / "content" / "learn"
    markets = sorted(learn.glob("market-*.md"))
    for f in markets[:-14]:
        gone.append(f"{f.relative_to(ROOT)} -> content/archive/learn/")
        if not dry:
            dest = ROOT / "content" / "archive" / "learn"
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), dest / f.name)
    live = ROOT / "site" / "live.json"
    if live.exists():
        items = json.loads(live.read_text())
        if len(items) > 40:
            gone.append(f"site/live.json: {len(items) - 40} old updates")
            if not dry:
                live.write_text(json.dumps(items[:40], ensure_ascii=False, indent=1))
    retire_stock(dry, gone)
    for p in list(ROOT.rglob("__pycache__")) + list(ROOT.rglob(".DS_Store")):
        if ".git" not in p.parts and p.exists():
            rm(p)
    return gone, freed


def episode_rows():
    log = (ROOT / "content" / "log.md").read_text() if (ROOT / "content" / "log.md").exists() else ""
    dates = {}
    for line in log.splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 2 and re.match(r"\d{4}-\d{2}-\d{2}", cells[0]):
            dates.setdefault(cells[1], cells[0])
    rows = []
    for f in sorted((ROOT / "episodes").glob("*.json")):
        try:
            ep = json.loads(f.read_text())
        except ValueError:
            continue
        slug = ep.get("slug", f.stem)
        up = ROOT / "output" / slug / "uploaded.json"
        ids = ""
        if up.exists():
            done = json.loads(up.read_text())
            ids = ", ".join(f"{k}: {v['id']}" for k, v in done.items() if isinstance(v, dict) and v.get("id"))
        kind = "video" if ep.get("segments") else "Short"
        rows.append((dates.get(slug, "?"), slug, kind, ep.get("title", ""), ids or "-"))
    return sorted(rows, reverse=True)


def guide_rows():
    rows = []
    for f in sorted((ROOT / "site" / "guides").glob("*.json")):
        g = json.loads(f.read_text())
        prefix = "es/guias" if g.get("lang") == "es" else "guides"
        rows.append((g.get("date", "?"), f"/{prefix}/{g['slug']}/", g.get("title", "")))
    src = (ROOT / "tools" / "site_guides.py").read_text() if (ROOT / "tools" / "site_guides.py").exists() else ""
    for chunk in src.split('\nguide("')[1:]:
        m = re.match(r'([a-z0-9-]+)", "([^"]+)"', chunk)
        if m:
            es = 'lang="es"' in chunk.split("\nguide(")[0].split("\n# ")[0]
            rows.append(("built-in", f"/{'es/guias' if es else 'guides'}/{m.group(1)}/", m.group(2)))
    return rows


def write_index():
    learn = ROOT / "content" / "learn"
    markets = sorted(learn.glob("market-*.md"))
    lines = ["# Vice Replay index (auto-generated by `python -m studio.tidy`; don't edit by hand)", "",
             "Read this first instead of searching the repo.", "",
             "## Where things live",
             "- Rules: `CLAUDE.md` · settings, links, approvals, chats: `content/owner.md` · plan: `content/launch-plan.md`",
             "- What was made: `content/log.md` · numbers: `content/performance.md`, `content/learn/channel.json`, "
             "`content/learn/analytics.json` · lessons: `content/learn/lessons.md`, `content/learn/patterns.md`",
             f"- Latest market report: `{markets[-1].relative_to(ROOT)}`" if markets else "- Latest market report: none yet",
             "- Routines: `.claude/commands/` · code: `studio/` · website: `site/` + `tools/site_guides.py` (repo vicereplay-site)",
             "- Screenshots: `media/official/` (names = place/character/car) · gameplay: `media/gameplay/` (+ processed.json)",
             "- Renders: `output/<slug>/` (videos auto-deleted 2 days after upload; `uploaded.json` kept)",
             "- Live status: `content/learn/status.md` (`python -m studio.status`) · health: `content/learn/health.md`",
             "- Instagram: queue `content/learn/reels_queue.json`, carousels `content/carousels/`, how-to "
             "`.claude/commands/instagram.md`",
             "- Campaigns: `content/campaigns/<name>.json` (approved = owner_approved), `tracker.md`, latest scan "
             "`content/campaigns/scan-*.md`, how-to `.claude/commands/campaign-clips.md`",
             "- Channels (Vice Replay / ClipCircuit / What If Arena, who does what): `content/channels.md` (Drive copy: Creator HQ)",
             "- Learning: `content/learn/scorecard.md` (fair 24 h numbers, DO MORE / DO LESS), `content/learn/ideas.md` (researched next topics), "
             "`history.jsonl` (view snapshots) · fresh streamer moments: `python -m studio.moments <name>`",
             "- How a Short is built (Nov 22): own `chart` graphics (`studio/charts.py`: bars, counter, line, quote) or owner gameplay, "
             "statement hook, 35-55 words: `content/episode-format.md` · hook data `content/learn/hooks-2026-11-22.md` · "
             "pre-upload check `python -m studio.vice publish` · 48 h flop review `python -m studio.flops`",
             "- Spanish channel (Vice Replay en Español): `content/spanish-channel.md`, registry `content/learn/uploads-es.json`, "
             "`studio/youtube_es.py` · both home pages: `python -m studio.channel_layout` · tags on old videos: `python -m studio.retag`",
             "- Reference pack (playbooks, hooks, topic bank): `resources/README.md` (channel rules win over it)",
             "- Finished one-off files: `content/archive/`", "",
             "## Episodes (newest first)", "| Date | Slug | Kind | Title | YouTube ids |", "|---|---|---|---|---|"]
    lines += [f"| {d} | {s} | {k} | {t} | {i} |" for d, s, k, t, i in episode_rows()]
    ch = learn / "channel.json"
    if ch.exists():
        d = json.loads(ch.read_text())
        vids = d.get("videos") or d.get("uploads") or []
        lines += ["", f"## Channel uploads (from the last learn run{', ' + d['updated'] if d.get('updated') else ''})",
                  "| YouTube id | Title | Views |", "|---|---|---|"]
        lines += [f"| {v.get('id')} | {v.get('title', '')} | {v.get('views', '')} |" for v in vids]
    lines += ["", "## Website guides", "| Date | Page | Title |", "|---|---|---|"]
    lines += [f"| {d} | {p} | {t} |" for d, p, t in guide_rows()]
    shots = sorted({re.sub(r"-\d+$", "", p.stem) for p in (ROOT / "media" / "official").glob("*.jpg")})
    lines += ["", "## Screenshot groups in media/official/", ", ".join(shots), ""]
    (ROOT / "content" / "INDEX.md").write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    gone, freed = clean(a.dry_run)
    if not a.dry_run:
        write_index()
    verb = "Would remove" if a.dry_run else "Removed"
    print(f"{verb} {len(gone)} item(s), {freed / 1e6:.1f} MB" + ("" if a.dry_run else "; content/INDEX.md updated"))
    for g in gone[:30]:
        print("  -", g)


if __name__ == "__main__":
    main()
