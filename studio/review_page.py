"""Builds the phone-friendly morning review page for one episode: watch everything, copy every text,
see when to post each upload, tick it off. Output: output/<slug>/review/ (index.html + media files),
ready to publish with the Artifact tool (index.html as the page, the rest via `files`).

    python -m studio.review_page episodes/<slug>.json [--date 2026-11-18]
"""
import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Posting schedule, US Eastern (CLAUDE.md). Index: Monday=0 ... Sunday=6
SCHEDULE = {
    "weekday": ("3:30 PM", "6:00 PM", "8:30 PM"),
    5: ("1:30 PM", "4:00 PM", "8:00 PM"),
    6: ("2:30 PM", "5:00 PM", "7:30 PM"),
}


# Third Short of the day (launch week, owner asked for 3 Shorts a day): lunch-time slot.
EXTRA = {"weekday": "12:30 PM", 5: "11:00 AM", 6: "12:00 PM"}


def times_for(day):
    return SCHEDULE.get(day.weekday(), SCHEDULE["weekday"])


def extra_time(day):
    return EXTRA.get(day.weekday(), EXTRA["weekday"])


def esc(s):
    return html.escape(s or "", quote=True)


def copy_block(label, text, cid):
    return (f'<div class="copy"><div class="copy-head"><span class="label">{esc(label)}</span>'
            f'<button type="button" class="btn" data-copy="{cid}">Copy</button></div>'
            f'<pre id="{cid}">{esc(text)}</pre></div>')


def card(cid, kind, when, title, video, poster, blocks, extra=""):
    vid = (f'<video controls playsinline preload="metadata" src="{esc(video)}"'
           + (f' poster="{esc(poster)}"' if poster else "") + "></video>") if video else ""
    return f"""
<section class="card" id="{cid}">
  <header class="card-head">
    <div><p class="kind">{esc(kind)}</p><h2>{esc(title)}</h2></div>
    <div class="when"><span class="time">{esc(when)}</span><span class="tz">ET</span></div>
  </header>
  {vid}
  {extra}
  {''.join(blocks)}
  <label class="done"><input type="checkbox" id="done-{cid}" data-done="{cid}"> Posted</label>
</section>"""


def read(p):
    return Path(p).read_text() if Path(p).exists() else ""


def build(ep_path, day):
    ep = json.loads(Path(ep_path).read_text())
    slug = ep.get("slug")
    out = ROOT / "output" / slug
    rv = out / "review"
    if rv.exists():
        shutil.rmtree(rv)
    rv.mkdir(parents=True)
    t_main, t_short, t_news = times_for(day)
    cards, n = [], 0

    def take(src):
        src = Path(src)
        if src.exists():
            shutil.copy(src, rv / src.name)
            return src.name
        return None

    # main video
    main = take(out / f"{slug}.mp4")
    if main:
        thumbs = [take(out / f"thumbnail-{k}.jpg") for k in "abc"]
        thumbs = [t for t in thumbs if t]
        titles = ep.get("title_options") or [ep["title"]]
        thumbs_html = ('<div class="thumbs">' + "".join(f'<figure><img src="{t}" alt="Thumbnail {t[-5].upper()}">'
                       f'<figcaption>{t[-5].upper()}</figcaption></figure>' for t in thumbs) + "</div>"
                       '<p class="hint">Upload all three with Test &amp; Compare (under Thumbnail).</p>') if thumbs else ""
        blocks = [copy_block(f"Title option {i + 1}" + (" (best)" if i == 0 else ""), t, f"main-title-{i}")
                  for i, t in enumerate(titles)]
        blocks += [copy_block("Description", read(out / "description.txt"), "main-desc"),
                   copy_block("Tags", read(out / "tags.txt"), "main-tags")]
        if ep.get("pinned_comment"):
            blocks.append(copy_block("Pinned comment", ep["pinned_comment"], "main-pin"))
        cards.append(card("main", "Main video", t_main, titles[0], main, thumbs[0] if thumbs else None, blocks, thumbs_html))
        n += 1
    # shorts
    shorts = ([{"id": "", "title": ep.get("short_title"), "pinned_comment": ep.get("pinned_comment")}] if ep.get("short") else []) \
        + ep.get("shorts", [])
    for k, sh in enumerate(shorts):
        name = f"{slug}-short" + (f"-{sh['id']}" if sh.get("id") else "")
        vid = take(out / f"{name}.mp4")
        if not vid:
            continue
        txt = read(out / f"{name}.txt")
        title = sh.get("title") or (txt.split("\n")[1] if txt.count("\n") > 1 else ep["title"])
        desc = txt.split("DESCRIPTION\n", 1)[-1].strip() if "DESCRIPTION" in txt else ""
        blocks = [copy_block("Title", title, f"s{k}-title"), copy_block("Description", desc, f"s{k}-desc")]
        # TikTok / Instagram Reels: same video, one caption (no #Shorts), hashtags people search on TikTok
        social = re.sub(r"\s*#\w+", "", title).strip()
        tags = " ".join(sh.get("tiktok_hashtags") or ["#GTA6", "#GTAVI", "#ViceCity", "#gaming", "#gta6news"])
        blocks.append(copy_block("TikTok / Reels caption", f"{social} {tags}", f"s{k}-tiktok"))
        if sh.get("pinned_comment"):
            blocks.append(copy_block("Pinned comment", sh["pinned_comment"], f"s{k}-pin"))
        when = t_short if k == 0 else t_news if k == 1 else extra_time(day)
        kind = "Short" if not sh.get("id") else f"Short: {sh['id']}"
        extra = '<p class="hint">Set "Related video" to the main video.</p>' if main else ""
        cards.append(card(f"short{k}", kind, when, title, vid, None, blocks, extra))
        n += 1

    # suggested replies to new comments (from content/learn/comments.json, written into the episode by the daily run)
    replies = ep.get("comment_replies") or []
    if replies:
        blocks = []
        for i, r in enumerate(replies):
            blocks.append(f'<p class="hint"><b>{esc(r.get("author", ""))}</b>: {esc(r.get("comment", ""))} '
                          f'<a href="{esc(r.get("url", ""))}" style="color:var(--cyan)">open</a></p>')
            blocks.append(copy_block(f"Reply {i + 1}", r.get("reply", ""), f"reply-{i}"))
        cards.append(card("replies", "Reply to comments", "ASAP", f"{len(replies)} new comments", None, None, blocks))
        n += 1

    page = TEMPLATE.replace("{{DATE}}", day.strftime("%A, %B %-d")) \
        .replace("{{COUNT}}", str(n)) \
        .replace("{{TOPIC}}", esc(ep["title"])) \
        .replace("{{KEY}}", esc(f"vr-{slug}-{day.isoformat()}")) \
        .replace("{{CARDS}}", "\n".join(cards))
    (rv / "index.html").write_text(page)
    print(rv / "index.html")
    for f in sorted(rv.iterdir()):
        print(f"  {f.name}  {f.stat().st_size / 1e6:.1f} MB")
    return rv


TEMPLATE = """<title>Vice Replay Review</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@500;700;800&display=swap">
<style>
/* Layout: one column of upload cards, each = what to post + when + everything to copy. Single dark neon look (the channel's brand). */
:root {
  --bg: #0d0717; --panel: #170d26; --panel-2: #21123a; --line: #3a2357;
  --fg: #f4eefc; --muted: #b7a9cf; --pink: #ff1f8e; --cyan: #00e5d2; --ok: #3ddc97;
  --display: "Anton", "Impact", "Arial Narrow", sans-serif;
  --body: "Montserrat", system-ui, -apple-system, "Segoe UI", sans-serif;
  color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 15px; line-height: 1.5; }
.wrap { max-width: 680px; margin: 0 auto; padding-block: 20px 48px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 18px; }
.top { display: grid; gap: 6px; }
.brand { font-family: var(--display); font-size: 22px; letter-spacing: .02em; }
.brand b { color: var(--cyan); font-weight: 400; }
h1 { font-family: var(--display); font-weight: 400; font-size: clamp(30px, 8vw, 44px); line-height: 1; margin: 0;
  text-wrap: balance; }
h1 span { background: var(--pink); padding: 0 .18em; box-decoration-break: clone; -webkit-box-decoration-break: clone; }
.sub { color: var(--muted); margin: 0; }
.progress { display: flex; align-items: center; gap: 10px; font-weight: 700; font-variant-numeric: tabular-nums; }
.bar { flex: 1; height: 8px; border-radius: 99px; background: var(--panel-2); overflow: hidden; }
.bar i { display: block; height: 100%; width: 0; background: linear-gradient(90deg, var(--pink), var(--cyan)); transition: width .3s; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 16px; display: grid; gap: 12px; min-width: 0; }
.card.is-done { border-color: var(--ok); opacity: .72; }
.card-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.card-head > div:first-child { min-width: 0; }
.kind { margin: 0; text-transform: uppercase; letter-spacing: .1em; font-size: 12px; font-weight: 800; color: var(--cyan); }
h2 { margin: 2px 0 0; font-size: 17px; line-height: 1.3; text-wrap: balance; }
.when { text-align: right; flex-shrink: 0; }
.time { display: block; font-family: var(--display); font-size: 26px; line-height: 1; color: var(--pink); font-variant-numeric: tabular-nums; }
.tz { font-size: 11px; letter-spacing: .1em; color: var(--muted); font-weight: 700; }
video { width: 100%; max-height: 70vh; border-radius: 10px; background: #000; }
.thumbs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.thumbs figure { margin: 0; position: relative; }
.thumbs img { border-radius: 6px; display: block; width: 100%; aspect-ratio: 16/9; object-fit: cover; }
.thumbs figcaption { position: absolute; bottom: 4px; right: 4px; background: var(--bg); color: var(--fg); font-weight: 800;
  font-size: 11px; padding: 1px 6px; border-radius: 4px; }
.hint { margin: 0; font-size: 13px; color: var(--muted); }
.copy { background: var(--panel-2); border-radius: 10px; padding: 10px 12px; display: grid; gap: 6px; min-width: 0; }
.copy-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.label { text-transform: uppercase; letter-spacing: .08em; font-size: 11px; font-weight: 800; color: var(--muted); }
pre { margin: 0; white-space: pre-wrap; word-break: break-word; font-family: var(--body); font-size: 14px; max-height: 9.5em; overflow: auto; }
.btn { font: 800 13px var(--body); color: var(--bg); background: var(--cyan); border: 0; border-radius: 99px; padding: 6px 14px; cursor: pointer; }
.btn.ok { background: var(--ok); }
.btn:focus-visible, input:focus-visible { outline: 3px solid var(--pink); outline-offset: 2px; }
.done { display: flex; align-items: center; gap: 10px; font-weight: 800; padding-top: 4px; cursor: pointer; }
.done input { width: 22px; height: 22px; accent-color: var(--ok); }
.foot { color: var(--muted); font-size: 13px; text-align: center; }
@media (prefers-reduced-motion: reduce) { .bar i { transition: none; } }
</style>
<main class="wrap">
  <header class="top">
    <div class="brand">VICE <b>REPLAY</b></div>
    <h1><span>{{DATE}}</span></h1>
    <p class="sub">{{TOPIC}} · {{COUNT}} uploads. Upload each in YouTube Studio, set the time with Schedule, then tick it off.</p>
    <div class="progress"><div class="bar"><i id="bar"></i></div><span id="count">0/{{COUNT}}</span></div>
  </header>
  {{CARDS}}
  <p class="foot">Video files to upload come with the daily message in Claude. Times are US Eastern (Miami).</p>
</main>
<script>
(function () {
  var KEY = "{{KEY}}";
  var store = {};
  try { store = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { store = {}; }
  var boxes = Array.prototype.slice.call(document.querySelectorAll("[data-done]"));
  function paint() {
    var done = 0;
    boxes.forEach(function (b) {
      var c = document.getElementById(b.getAttribute("data-done"));
      if (b.checked) done++;
      if (c) c.classList.toggle("is-done", b.checked);
    });
    document.getElementById("count").textContent = done + "/" + boxes.length;
    document.getElementById("bar").style.width = (boxes.length ? done / boxes.length * 100 : 0) + "%";
  }
  boxes.forEach(function (b) {
    b.checked = !!store[b.id];
    b.addEventListener("change", function () {
      store[b.id] = b.checked;
      try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {}
      paint();
    });
  });
  paint();
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-copy]");
    if (!btn) return;
    var pre = document.getElementById(btn.getAttribute("data-copy"));
    var text = pre ? pre.textContent : "";
    function flash(msg) { btn.textContent = msg; btn.classList.add("ok"); setTimeout(function () { btn.textContent = "Copy"; btn.classList.remove("ok"); }, 1600); }
    function selectIt() { var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); flash("Selected"); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { flash("Copied"); }, selectIt);
    } else { selectIt(); }
  });
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode")
    ap.add_argument("--date", help="posting date YYYY-MM-DD (default: today, US Eastern)")
    a = ap.parse_args()
    if a.date:
        day = dt.date.fromisoformat(a.date)
    else:
        from zoneinfo import ZoneInfo
        day = dt.datetime.now(ZoneInfo("America/New_York")).date()
    build(a.episode, day)


if __name__ == "__main__":
    main()
