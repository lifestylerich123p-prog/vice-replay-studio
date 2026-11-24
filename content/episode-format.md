# Episode format (read before writing an episode JSON)

Moved out of CLAUDE.md so runs that don't write episodes don't load it. Every rule here still applies.

**Write** `episodes/<slug>.json` following `episodes/gta6-3-days.json`:
   - `segments`: 6-9 segments, 25-45 words each, about 2-4 minutes in total. Each has a short `headline`
     (2-4 words, shown on screen), a `chapter` name, the narration `text`, and an optional `media`
     (a clip or screenshot path in `media/`; leave null for a generated neon background).
   - Segment 1 is the hook: state the payoff in the first 10 seconds. No "hey guys, welcome back".
   - The last segment asks a specific question for the comments, then asks people to subscribe.
   - Title options for automatic swaps: `title_options` (3, main video), `short_title_options` (2-3, main Short) and
     `title_options` (2-3) inside each `shorts` item. Option 1 is posted; option 2 is swapped in if it underperforms.
   - `short`: 3-5 segments, under 55 seconds of narration total: the Short cut from this video. Also set
     `short_title` (under 60 chars, ends with #GTA6 #Shorts) and `short_description` (1-2 sentences).
   - `shorts`: extra standalone Shorts, a list of `{"id", "title", "description", "hashtags", "segments"}`
     (same segment format, 2-4 segments, 20-45 seconds). The daily run adds one news Short here.
   - Shorts get far more views than long videos on this channel. Short segment 1 must hook in the first
     2 seconds (a number, a name, a surprise), and its `headline` doubles as the Short's cover text.
   - `thumbnail`: `line1` (1-2 words, white), `line2` (2-3 words, pink slab), `tag` (2-4 words), `image`
     (the best screenshot for it). The render makes thumbnail-a/b/c.jpg with different pictures for
     YouTube Studio's Test & Compare (up to 3 thumbnails per video).
     Nov 23: add `"variants": [{line1, line2, tag, image}, {...}]` so B and C test different IDEAS (a big number,
     a contrast) instead of the same words on new pictures; `"image": "vice:2"` = our Vice City set. Rebuild only the
     thumbnails with `python -m studio.thumbs episodes/<slug>.json`.
     Thumbnail text must not repeat the title word for word.
   - Every Short's last segment automatically shows a "FOLLOW FOR DAILY GTA 6" badge (Spanish: "SÍGUENOS: GTA 6 A
     DIARIO"); subscribers are the channel's bottleneck for monetization. Set `"follow_cta": false` to turn it off; `"cta"` / `"cta_es"` replace its text with a promise (series parts: "PART 2 TOMORROW: FOLLOW" / "PARTE 2 MAÑANA: SÍGUENOS"; keep it under ~26 characters).
   - Hook (Nov 22 data): the FIRST sentence is a statement of the surprising result, 3-10 words, never a question
     (questions first kept 35% of viewers vs 60%); templates in resources/hooks-and-titles.md. `studio.vice publish`
     blocks a question opener.
   - **Payoff in the first frame** (Nov 24 independent review: our openings held a static card ~3 s before the answer
     showed): when segment 1 is a `kinetic` hook and segment 2 is a map / tier / list / versus / bars / counter / meter
     card, the renderer opens on segment 2's FINISHED picture (the pinned map, the filled board) with the hook lettering
     slammed on top, no captions or tag repeating it; segment 2 then starts close to the pin instead of zooming out to
     the whole state. So: write the hook as 2 short lines (≤ 8 words) and make segment 2 the answer card. Turn it off
     with `"payoff": false` on segment 1 (or `"payoff_hook": false` on the episode), e.g. for a quiz.
   - One text layer per idea: a tag that repeats the card's own lettering is dropped, and hook captions are dropped
     when half the spoken words are already on the hook card. Keep `sub` lines for something NEW (they're now white,
     bigger, on a plate). Before writing a new topic, search `content/learn/uploads.json` titles + `episodes/` for it
     (Nov 24: cheats, mission replay and Dog Island had been drafted again by mistake).
   - Make Shorts loop: the last line should flow back into the first (e.g. ends "...and that's why" while
     the hook starts with the reason), so replays count as extra watch time.
   - `pinned_comment`: one question for the comments that's easy to answer (pick-one or a number), posted and
     pinned by the owner right after upload.
   - Spanish channel (Vice Replay en Español, Nov 22): `short_es.title` / each Short's `es.title` in the Spanish-market
     style (one key word in CAPS + one emoji, e.g. "El PRIMERO en terminar GTA 6 NO fue IShowSpeed 😳 #GTA6 #Shorts"),
     plus `short_pinned_comment_es` (and `pinned_comment_es` inside `shorts` items): an easy Spanish question.
     For Spanish streamer stories (IlloJuan, Rubius, TheGrefg, Ibai...) see content/learn/market-es-*.md.
   - Titles and tags (Nov 22, owner: "check titles and tags are perfect"): the title leads with the words people
     search ("GTA 6" + the subject: "GTA 6: Lucia's 8 outfits...", a streamer's name first for streamer stories),
     under 60 characters before "#GTA6 #Shorts". `tags`: 8-15 search phrases for THIS topic, most specific first
     ("GTA 6 Lucia", "GTA 6 outfits", "Vintage Vice City Pack"), on the episode or per item in `shorts`; Spanish ones
     in `short_es.tags` / each Short's `es.tags` ("outfits de Lucia", "GTA 6 español"). The uploaders add the channel
     basics themselves (studio.youtube_upload.clean_tags, 500-character limit). Before Nov 22, Short-only episodes
     uploaded with NO tags; `python -m studio.retag` fixes videos already up (content/learn/retag.json).
   - Spanish (free extra audience): every segment (main and Shorts) also gets `text_es` (natural Latin American
     Spanish, same meaning, similar length; keep names like GTA 6, Vice City, Kai Cenat as they are). Add `es`
     {`title`, `description`} for the main video, `short_es` for the main Short, and `es` inside each `shorts`
     item. The uploader adds them as YouTube's Spanish title/description and Spanish subtitles.
   - Affiliate links (Amazon, `content/affiliate.json`) are added to the main video's description automatically with
     the required disclosure. Set `affiliate` to pick sets: ["storage","game"] (default; downloads, launch, news),
     ["storage","gear"] (guides, tips, gameplay), or [] for none (e.g. sensitive news). Never claim we used or
     reviewed a product, and never put affiliate links in a way that hides the disclosure.
   - The gear page is https://vicereplay.com/gear/ (repo vicereplay-site). Mention "vicereplay.com/gear" in Short
     descriptions and pinned comments when the topic is storage or gear.
   - Links in Shorts descriptions aren't clickable, so Shorts send people to the long video: end the main Short's
     `short_description` with "Full video on the channel ⬇️" and remind the owner to set "Related video". The long
     video carries the affiliate links (description + pinned comment, added automatically).
   - On download/storage/gear/launch topics, the long video's last or second-to-last segment may add ONE natural line
     like "If you're short on space, I put storage links in the description." Never more than once, never pushy.
   - Playlists are automatic (main -> "GTA 6 News & Guides", Short -> "GTA 6 Shorts", news Short -> "GTA 6
     Streamer & Breaking News"); set `playlist` on an item only to override.
   - Write narration for the ear: short sentences, spell numbers the way they should be spoken
     when it matters ("212 gigabytes"), no emoji, no markdown.

## Formats and editing tools (added Nov 20)

Formats that work (scorecard + competitor research): `"format"` = `news`, `tips/discovery`, `comparison` (GTA 5 vs 6),
`search-answer` (answer a question people search), `details` (a detail read off official/owner footage, magnified),
`ranking` (our own countdown of things shown in authorized footage: rankings are a confirmed trend on 7 of 11
competitor channels), `quiz` (guess from a magnified detail, then reveal; answers from Rockstar's pages; see
episodes/gta6-guess-the-ride.json) and map comparisons (`comparison` on the official Leonida map, see
episodes/gta6-map-is-florida.json). Add `"series"` ("A: Moments", "B: Rankings", "C: Details"/"C: Tested",
"Explained", "Quiz") for the scorecard.

Per-segment keys (all optional) in `short` / `segments`:
- `media_start` (s) and `keep_media: true` (keep this picture even when owner gameplay exists); `"use_gameplay": false`
  on the episode keeps every chosen picture.
- `focus`: 0 (left) .. 1 (right), or [x, y]: which part of a 16:9 clip the vertical crop keeps.
- `speed`: 0.5-0.8 honest slow motion for short clips.
- `freeze`: {"at": s} plays to that point (seconds after media_start, before speed) and holds the frame.
- `magnify`: {"box": [x0, y0, x1, y1], "width": 0.6-0.86, "y": 0.30-0.34} shows that box of the full-resolution frame
  large over the blurred shot (HUD, signs, small details). Keep it between the headline (top 30%) and captions (62%+).
- `callout`: {"x", "y", "r", "at", "label"?} a pink/cyan ring on screen (output coordinates 0-1).
- `zoom`: {"x", "y", "to": 1.3-1.6, "at", "dur"} smooth punch-in toward a point.
- `shots`: [{"media", "start", "speed"?, "focus"?, "dur"?}, ...] cuts between several clips inside one segment (pacing).
- `map` chart (Nov 24, owner approved the official map in videos): `{"type": "map", "at": "Cottonmouth Lake", "label":
  "Skunk Ape · night", "n": 2}` zooms Rockstar's official map from the whole state to that spot and pulses a pin
  (`at` = a place printed on the map, see studio/mappins.PLACES, or a grid cell; `dx`/`dy` nudge it). For "where is X"
  Shorts; the spot must be in site/map-pins.json (2+ guides). Example: episodes/gta6-ufo-where.json.
- `chart` (Nov 22): our own animated graphic as the segment's picture (studio/charts.py), e.g.
  `{"type": "bars", "items": [["IShowSpeed, launch", 68.7], ["CarryMinati", 18.1]], "unit": "M", "highlight": 0,
  "note": "YouTube view counts, Nov 22"}` (a leaderboard that grows, max 6 rows) or `{"type": "counter", "value": 3.79,
  "prefix": "$", "unit": "B", "label": "...", "vs": {...}}` (a number that counts up, optionally VS a second one).
  YouTube's Oct 2026 update ranks ORIGINAL Shorts higher and says narration over reused footage isn't original:
  build the Short around our charts/data and use trailer footage as 1-2 s cutaways, not the whole video.
  Write the number the way the chart shows it ("sixty eight point seven million" for 68.7M).
  `{"type": "line", "items": [["GTA 3\n2001", 95], ["GTA 5\n2013", 86], ["GTA 6\n2026", 80]], "prefix": "$",
  "floor": 70, "note": "...; axis starts at $70"}` (Nov 22): a trend that draws itself left to right, max 8 points, a
  second label line (year) after "\n"; use it for anything over time (prices, views per day, player counts).
  `floor` starts the bars/axis above 0: say so in the `note`. Long notes shrink to fit.
  `{"type": "quote", "text": "exact words, short", "pink": ["key words"], "who": "Rockstar, to IGN (Nov 22)"}`
  (Nov 22): a quote card. The words appear one by one, `pink` words light up, then who said it. Use it for Rockstar
  interviews and streamer stories (what a streamer SAID, from a reliable source), where there are no numbers to chart
  and the streamer's footage is off-limits. Quote exactly and briefly (one or two sentences); name the outlet.
  - **FACTS ONLY (owner, Nov 22 evening: "not the ones with footage, facts with a strong hook")**: a Short is built
    only from our own cards; no trailer clips or official screenshots, not even as cutaways (`studio.vice publish`
    blocks them; owner gameplay is fine; since Nov 23 no waivers and no trailer images in long videos either). Cards:
    `bars`, `counter`, `line`, `quote`, plus `{"type": "text", "text": "Darts, or a better game?", "pink": [...],
    "sub": "..."}` (a big statement: the hook or the closing question), `{"type": "list", "title": "IN GTA 6?",
    "items": [["Pool", "IN"], ["Darts", "CUT"]]}` (a checklist; IN/YES/SÍ/REAL tags cyan, the rest pink) and
    `{"type": "quiz", "tag": "1/3", "q": "Who voiced Tommy Vercetti?", "options": ["Al Pacino", "Ray Liotta", "Robert De
    Niro"], "answer": 1}` (the question with a countdown; repeat it with `"reveal": true` in the next segment for the
    answer). Formats: fun facts, GTA history, "how much do you know" quizzes (see episodes/gta-history-quiz.json),
    numbers, Rockstar/streamer quotes. Quiz rules: every answer checked in 2+ sources, wrong options plausible but
    invented, never a real alternative title; vary which letter is right.
  - **GTA 6-style lettering cards** (owner Nov 23: "lettering and more modern style ... GTA 6 style";
    studio/vicecards.py): they play on our animated Vice City set (sunset sky, striped sun, palm silhouettes, a neon
    grid floor that scrolls), with neon chrome lettering that punches in. Lead new Shorts with these:
    `{"type": "kinetic", "lines": ["VICE CITY", "IS B TIER"], "pink": ["B TIER"], "sub": "..."}` (1-4 big lines, one at a
    time: the hook and the closing question), `{"type": "countdown", "n": 2, "of": 4, "label": "Bigfoot is real",
    "sub": "..."}` (listicle items: "4 secrets", "5 things"), `{"type": "versus", "a": ["GTA 5", "32 HOURS"], "b":
    ["GTA 6", "80 HOURS"], "winner": "b"}` (VS / this-or-that; the winner lights up at 60%), `{"type": "tier", "title":
    "...", "rows": [["S", ["GTA 6 · 99"]], ["A", []]], "static": ["B"]}` (fill one row per segment; `static` rows were
    filled earlier), `{"type": "meter", "value": 99, "max": 100, "label": "Metacritic", "sub": "..."}` (a gauge
    that fills while the number counts up: scores, percentages) and `{"type": "headline", "kicker": "PLAYERS REPORT", "text": "...", "ticker": "..."}` (news; put
    REPORTEDLY / LEAK in the kicker for anything unconfirmed). Use one `seed` per Short (same sky in every segment).
    Any older chart can add `"bg": "vice"`. Research behind it (Nov 23): animate only the key words, change the card
    every 2-4 s, tier lists / countdown listicles / quizzes / VS drive comments (examples: episodes/
    gta6-tier-list-critics.json, gta6-4-secrets.json).
  - **Spanish chart text** (Nov 22): a chart with a `label`, `note` or VS label needs `chart_es` on the same segment (the
    same chart with Spanish words); Spanish renders switch numbers to 3.790,5 style by themselves. Without it the
    Spanish Short shows English words (the publish check warns).
  - **Vary the layout** (Nov 22): the first four graph Shorts were all counter > bars > counter > clip. Mix the order
    (open on bars or a line, a clip cutaway in the middle); the publish check warns when a Short repeats the picture
    order of one of the last 4 uploads.

Footage rules learned Nov 20: read every sign/number/HUD value at FULL resolution before writing it (a thumbnail showed
"5/9" where the frame said "5/6"); official clips contain internal cuts and UI moments (the strip-mall clip opens on a
blurred weapon wheel), so the renderer warns "crosses a shot change": fix it with media_start/speed/freeze/shots.
A "real life matches" line is welcome when it's sourced (2+ reliable sources, exact wording: "in two years", not a
looser "in the last two years"). Captions are timed to the narration automatically (speech-aligned). Caption style "animated" (owner approved
Nov 21; config/channel.json `caption_style`): groups of 3 words pop in, the spoken word bounces in cyan, and English
number words show as pink digits ("fifty two hours" -> 52 HOURS, "ninety eight percent" -> 98%), so keep writing
numbers as words for the voice. Spanish captions keep their words as written.
Before delivering or uploading: `python -m studio.vice publish episodes/<slug>.json` must show no blockers.
With `"shorts"` it gates every Short (and a legacy `"short"`) on its own render and text in one run, plus one
rights/facts check of the main video, with blockers prefixed by the Short id or `main` (`news: ...`, `main: ...`);
no temporary single-Short episodes needed.

AI graphics (Everygen, cleared in `rights/registry.json` as `ai-backgrounds`, Vice Replay only, never on campaign clips):
- `assets/ai-backgrounds/*.jpg` (16:9): thumbnail/card backgrounds by theme: news-skyline, rankings-podium, money-cash,
  racing-night-street, police-wanted, tested-lab, details-magnifier, deals-gear, swamp-nature, night-streets. Use them
  as a thumbnail `image` or a segment `media` only for graphics (lists, prices, rankings), never as "gameplay".
- `assets/ai-backgrounds/ig/*-4x5.jpg` (1080x1350): Instagram carousel/image post backgrounds.
- `assets/intro/sting.mp4`: the long video's 3-second intro (neon flythrough + wordmark + title, made automatically;
  falls back to the still card if the file is missing). Shorts have no intro: they open on the hook.
- vicereplay.com uses them too (built by `tools/site_guides.py`): homepage hero = the sting (plays once, then holds;
  skipped for reduced-motion/data-saver), banners on /guides/ (news-skyline), /es/ (swamp-nature), /links/
  (night-streets) and /gear/ (deals-gear), and picture cards from each guide's share image (og/t/).
