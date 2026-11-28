# Growth plan (owner Nov 28, "Audience growth recovery") — read before writing any Short

Evidence: `python -m studio.growth` (content/learn/growth-audit.md, Nov 28 10 AM ET). Heuristic, our own medians,
small samples marked. Not available via the API: Shorts-feed impressions, Studio's exact viewed-vs-swiped %, returning
viewers, copyright claims (check in Studio when needed). No restrictions found on either channel (all public videos
public, none made-for-kids, region-blocked or rejected): low views are a content/distribution problem, not a ban.

## What the numbers say
**English (15 subs, 41.7k views; last 24 h 1,556 / 7 d 6,912 views; 75% of views from the Shorts feed, 23% search)**
- Launch week carried us: news/fact Shorts had a median of 788 views before Nov 24 and **47 after** (n 11, stayed
  proxy 27%). Post-launch nobody wants GTA 6 news cards: problem **E (demand moved) -> B (swiped) -> A (not shown)**.
- Map/how-to Shorts since Nov 24: median **403** views (n 3: shoe store 1,204, underwater money 403, Paul Walker's
  car 303), % viewed 94. About **10x** the news cards in the same week. Preliminary (n 3), direction is clear.
- Search is real demand: "gta 6 shoe store" + variants brought ~3,900 search views in 28 days. "Where is X" answers win.
- Stayed-to-watch proxy (engaged/views) is **~27-45%** on almost everything: the opening frame loses most of the feed
  audience (**B**). Lettering card on a darkened screenshot is the common factor.
- Subscriber conversion **~0** (0 subs from 14 Shorts since Nov 24): **D**. Nothing yet makes people want the next one.

**Spanish (0 subs, 45 lifetime views, ~10 views/day; Shorts feed only 10% of views, search 71%)**
- Problem **A**: YouTube's feed barely tests the Spanish channel at all. All 12 Shorts 48 h+ are "barely shown".
- Topics were mostly translated streamer/news items (**E**): "IShowSpeed...", "Vice City es TIER B", "dardos".
- The few views come from Spanish searches ("otra noche en miami gta 6", "welcome to vice city bad bunny").
- So the Spanish route in is **search first**: natural Latin American search phrases in the title and first line.

## What changes (future production; booked videos keep their slots)
1. **Topics**: English = where-to-find, how-to, hidden rewards, beginner mistakes, mechanics (a search phrase you can
   answer). No new generic news/fact cards. Spanish = its own research (market-es files): "dónde está/encontrar",
   "cómo conseguir/ganar dinero", "trucos", "secretos", "errores que debes evitar", "cosas que no sabías" + Miami/Latino.
2. **First frame = the payoff** (Format A, map-first): the pin on Rockstar's map zoomed in, or the reward/answer, with
   ONE short line; no intro, logo, greeting or slow empty zoom; never the same opening twice in a row.
3. **Titles**: natural, say what you gain, must mention "GTA 6" (anywhere; the gate now allows it), <= 60 chars,
   max ONE hashtag (#GTA6) or none, no repeated CAPS; Spanish in natural Latin American Spanish ("carros", not
   "coches"), no required CAPS word. Patterns, never claims we can't back: "Where to Sell Stolen Cars in GTA 6",
   "How to Skip Time in GTA 6", "Dónde vender carros robados en GTA 6", "3 lugares secretos de GTA 6".
4. **Formats**: A map-first (now), D mystery -> payoff (now, cards + official map), C visual comparison with
   official screenshots (now), B gameplay demonstration and E quick tutorial need the owner's gameplay (the Drive
   drop zone is empty): until then, tutorials use the official map + route cards, never fake or trailer gameplay.
5. **Subscribe reason**: end on the next numbered spot ("Spot #N next: ...") only when it's true; one-tap comment prompt.
6. **Mix for new content** (hypothesis, per language, adjust from results): 35% tutorials, 25% hidden locations +
   rewards, 20% interactive-map guides, 10% comparisons/discoveries, 10% experiments.

## 7-day creative experiment (Nov 30 - Dec 6) — content/learn/experiments.json
One variable per channel, alternating slots so time of day doesn't decide it; the other slot is the control.
- **English: opening frame.** Variant = map-first opening (segment 1 is the map card on the spot, headline = the
  answer). Applied by the 2:04 AM run to the experiment slot's Short when it is a location Short (otherwise "n/a").
- **Spanish: title.** Variant = natural Latin American search-phrase title (no CAPS word, one hashtag max).
- Measure at matched ages (24 h, 72 h, 7 d views; stayed proxy; % viewed; subs per 1,000) with studio.growth.
  Preliminary until 5+ per arm; never declare a winner on 1-2 videos; never re-upload near-identical copies.

## Website (ties in)
Each verified location Short -> map pin + guide section (2+ sources), linked both ways; search terms that bring
YouTube views become guide FAQs. Clickable routes to the site: channel profile links, the map-secrets long guide
(related video), Instagram profile link; Shorts descriptions/comments are not clickable.

## Update Nov 28 afternoon (owner: "growth optimization")
**The winning formula, from our own best post** (TikTok shoe store: 17,445 views, 7 followers, 18.8% full watch;
YouTube copy 1,204 views, 118% viewed = rewatched): a real search question ("gta 6 shoe store" was our #1 YouTube
search term); ~12 s in 4 beats; line 1 = the answer with the place name ("...is in Key Lento"); beat 2 = the map card
on the spot; beat 3 = one useful extra step ("open the map, pick Style, then Footwear"); beat 4 ends mid-sentence so
it loops; caption = answer + "Save this for when you play 📌". Weaker TikTok posts were 25-40 s news cards with
0-8% full watch. Mask location (16 s, same pattern) got 416 views in ~4 h. Rule for new location Shorts: 10-18 s,
answer in the first line, map by second 3, one useful extra, loop ending; no padding segments. Original every time:
same structure, new verified place; never re-post the same video.

**Mix for future uncommitted production** (config/channel.json content_mix, studio.mix): 40% location + interactive
map guides (location 30 + map_tutorial 5 + map_scale 5) / 25% gameplay tutorials ("how to") / 15% secrets / 10%
comparisons + rankings (maps tier list: 337 views in 3 h) / 10% experiments. Booked Shorts stay where they are.

**Internal retention targets** (not platform benchmarks): stayed-to-watch PROXY (engaged views / views, from the API)
above 45% (now ~38%); average % viewed above 75% (now ~65%); subs per 1,000 engaged views above 0. The proxy is NOT
Studio's "stayed to watch" number; that one needs a Studio screenshot (/stats). Levers in order: answer first, map pin
in the first 2 s, 10-18 s length, faster beats, satisfying loop ending. One variable per test (experiments.json).

**Spanish website (no /es/ impressions in 28 days)**: technical checks pass (30 Spanish URLs in the sitemap, robots
allow, html lang=es, reciprocal hreflang, index,follow, linked from the English home). So it's discovery/ranking, not
a block. Unknown without Search Console's Pages report: whether Google has indexed them (owner can check Indexing >
Pages, filter /es/, and request indexing for /es/ and /es/guias/mapa-gta-6/). Next: Spanish pages only where Spanish
searches exist (search_demand + autocomplete), Spanish YouTube descriptions/profile pointing to /es/, no translated
doorway pages.

**PS5 Pro guide (176 impressions/7 d, ~position 8-12, 0 clicks)**: queries are "is ps5 pro worth it for gta 6" and
"gta 6 fps ps5 pro"; title/description already match. Added a sourced "Is GTA 6 PS5 Pro Enhanced?" FAQ (EN + ES;
4K claims marked as leaks). Re-check its position next week before changing more.

**Gameplay footage (free, legal)**: the only clean source for real demonstrations is the owner's own capture
(PS5 Create button -> Drive "Gameplay Drop Zone", radio/music off; studio.gameplay pulls it; provenance in
rights/). Official Rockstar media stays as already allowed (screenshots, official map). Other creators only with
written permission recorded in rights/registry.json. Never AI footage presented as gameplay, never downloaded clips.
