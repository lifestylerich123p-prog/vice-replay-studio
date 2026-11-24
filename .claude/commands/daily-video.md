---
description: The automated daily run - pick today's topic, make the video + Short + thumbnail, and deliver them for review
---
You are running the daily Vice Replay automation. Nobody is watching live, so don't ask questions:
make sensible choices, finish the whole run, and explain your choices in the final report.

**NOV 23 RULES (owner; these win over anything below that conflicts):**
1. **No trailer clips or official screenshots in ANY video** (Shorts, long videos, Reels). Pictures are our GTA 6-style
   lettering cards (`studio/vicecards.py`: kinetic, countdown, versus, tier, meter, headline, plus charts with
   `"bg": "vice"`; see content/episode-format.md and episodes/gta6-tier-list-critics.json) or the owner's gameplay. The
   publish check blocks footage. Official images stay only for thumbnails, site cards and IG carousels.
2. **Every Short:** a statement hook on a kinetic card (the first frame is the cover), a `src` on the card with the main
   fact, one verdict line ("our take: ..."), a card mix that differs from the last uploads, headlines of 19 characters
   or less, one `seed` per Short, prices spoken as "seventy nine dollars and ninety nine cents". Facts in 2+ sources.
   YouTube (July 2026) doesn't pay "generic, repetitive content easily made with templates": vary formats and angles.
3. **Slots:** 9:30 / 11:00 / 12:30 PM ET on both channels (evenings only for big news). `python -m studio.quota` counts
   the approved queue as booked. Deliver for approval; once the owner approves in the main chat, the Short goes into
   content/learn/approved_queue.json and the daily 3:45 AM run uploads it after the quota reset.
4. **Spanish channel:** at least one Spanish-only angle a day (local prices, Latin American interest, Cuban/Mexican
   style), not only translations; Spanish slots lean 12:30 PM ET (lunch in Mexico, evening in Spain).
5. **Long videos:** only the weekly hub (Sunday, 16:9 lettering cards like episodes/gta6-10-numbers.json); no daily long
   video. The "Wildest Moment" gameplay Short stays when the owner uploads gameplay (segment 1 = a kinetic card).
6. Instagram captions say "AI narration" automatically; remind the owner to switch on TikTok's AI label.
7. **Weekly card series** (owner Nov 23; one recognizable format per weekday, different card mix every day, so
   YouTube sees variety, not a template): **Mon** news card (`headline` + kinetic: the week's biggest confirmed update);
   **Tue** VS day (`versus`: GTA 6 vs GTA 5, edition vs edition, record vs record); **Wed** tier list (`tier`: rank
   something with checked numbers or owner/comment votes; **Nov 23: tier lists won big (506 views in 3 h vs a
   219 median), so a 2nd tier list every Saturday 10 AM in English**, data-backed or a clearly labeled opinion ranking
   with a contrarian hook, e.g. "CJ isn't S tier"); **Thu** quiz (`quiz` cards with a timer, "only real fans get
   3/3"); **Fri** countdown ("N things", `countdown` cards); **Sat** Spanish special (a Spanish-only angle on the Spanish
   channel: local prices, Latin American interest, regional slang/style); **Sun** the long hub video (16:9 lettering,
   episodes/gta6-10-numbers.json style) at 3:30 PM + a meter/kinetic Short. Series name in each description, e.g.
   "Vice Replay Tier List #2". The other daily Shorts stay free-form (news, catches, streamers).

00. **Health first (free)**: `python -m studio.doctor --fix`. If it reports 🔴 (YouTube connection failing or about to
   expire, website down), put that in bold at the very top of the final message with the fix.
0. **Gameplay + "Wildest Moment of the Day"**: run `python -m studio.gameplay` (pulls the owner's new recordings from
   Drive and cuts highlights into `media/gameplay/`; `processed.json` lists each clip with its score and `category`
   from the Drive subfolder: Wildest moments, Chases & crashes, Funny & fails, Glitches, Scenery & cars).
   If it printed NEW highlight clips today, the `tips` Short becomes **"Wildest Moment of the Day"** (id `wild`, same
   12:30 PM slot): pick the best new highlight (highest score; Funny & fails / Glitches / Wildest moments first), look
   at 3 frames of it, and write 3-4 segments that tell what happens in the owner's own words-style ("watch what
   happens when..."), with a hook in 2 seconds, a payoff, and the follow badge. Set `"keep_media": true` and that
   clip as `media` on segments 2-4 (with `media_start` offsets so it plays through), but keep segment 1 calm (no
   shooting/gore in the first 7 seconds: use a calm clip or a kinetic lettering card). Title like "Wildest GTA 6 moment
   today: <what happened> #GTA6 #Shorts". Never a cutscene, ending or story moment; no in-game radio. Series name in
   the description: "Wildest Moment of the Day #<n>" (count previous `wild` Shorts in content/learn/uploads.json + 1).
0b. **Learn first**: run `python -m studio.learn` and `python -m studio.retention` (free; read `content/learn/retention.md`:
   which hooks/lengths/topics keep viewers, and write hooks like the best ones), (YouTube Data API; if it fails because there is no API key,
   say so in the report and continue). Then read `content/learn/channel.json` (our uploads with views/hour),
   today's `content/learn/market-<date>.md` (the hottest GTA 6 videos and Shorts on YouTube right now),
   `content/learn/scorecard.md` (fair first-24 h numbers per hook/length/slot/kind + DO MORE / DO LESS: follow it),
   `content/learn/patterns.md`, `content/learn/lessons.md`, and if present `content/learn/analytics.json`
   (private numbers: % of each video watched, seconds watched, subscribers gained, where views come from;
   these beat view counts for judging hooks and length) and `content/learn/comments.json`. Write 1-3 new dated lessons to `lessons.md`:
   which of OUR topic kinds, hooks, title styles and posting times got the most views per hour, and what the
   market's winners have in common (topics, title wording, length, Shorts vs long). Only claim what the
   numbers show. Use the lessons in every choice below: topic, hook, title options, thumbnail text, length.
   Learn from winning videos' patterns; never copy their titles, footage or thumbnails.
**NOV 22 RESEARCH PLAN (owner: "full investigation"; overrides the plans below where they differ; sources in
content/learn/growth-plan-2026-11-22.md).** YouTube's Oct 1, 2026 Shorts update cuts reach for footage that only gets
"VO descriptions of what's happening on screen" (YouTube's Creator Liaison), which is close to our trailer-narration style,
and our numbers agree (narrated Shorts ~57% viewed, 40% stayed to watch; real moments 86-92%). So:
- **Max 2 narrated Shorts a day** until owner gameplay exists (more volume of the same template looks mass-produced).
- **13-20 s, one fact** (35-55 words; `studio.vice publish` blocks over ~30 s). Concrete number or catch in the FIRST line
  and on screen (our best openers: "30 FPS EVERYWHERE", "$1.65 BILLION": 50-55% stayed; vague teasers: 29%).
- **Commentary, not description**: every Short needs a claim, a verdict or a test ("it works / it doesn't / here's the
  catch"). Never narrate what the picture shows. Prefer our own graphics (magnifier, map, numbers, comparisons) over
  plain trailer clips.
- **Formats, in order**: streamer news with a number (Spanish channel: Spanish-speaking streamers, 2 sources); "how to
  find it" for this week's community discoveries told on the official map (never their footage); quiz/map; big
  confirmed news. Evergreen how-tos go to the website guides (Shorts fade after ~30 days).
- **Never delete a flop** (YouTube: deleting cuts the audience link); unlist at most, and make a new angle instead.
- Judge each Short against our own median in content/learn/retention.md ("Stayed to watch"), not a magic number.

**NOV 22 FLOP REVIEW (owner: "hide the videos that don't get views and learn from it"; overrides older plans).**
9 videos under 50 views after 36 h+ were set PRIVATE (not deleted; list in content/owner.md). What the numbers say
(all our videos 36 h+ old): long videos median 14 views (7 of 9 under 50); tips/how-to Shorts median 237 (3 of 7 under
50); catch 1,174, number/verdict 928, streamer 638 with zero flops; Shorts posted 6-11 AM median 1,084 vs 2-6 PM 199;
scripts of 76+ words median 404 vs 56-75 words 836. So:
- **No daily long video.** The only long video is Sunday's weekly recap; every other day is Shorts only (saves ~2,500
  YouTube units a day for Shorts). Long guides belong on the website.
- **No tips/how-to Shorts at all** (settings, fixes, cheat lists, beginner tips, "do this first"): website guides only.
- **Every Short is a catch, a number/verdict or a streamer story**, built on a `chart` (or owner gameplay), 56-75 words
  max (`studio.vice publish` blocks 76+), posted 9:30 / 11:00 / 12:30.
- Hide (private, never delete) any Short under 50 views after 48 h, and add its pattern to content/learn/lessons.md:
  run `python -m studio.flops` (lists them; changes nothing) and put its list in the report; the main chat runs
  `--apply`. Before picking today's layout, read the scorecard's "By picture" / "By opener" tables.
- **FACTS ONLY** (owner, Nov 22 evening): no game footage in Shorts; cards only (charts, quote, list, text, quiz).
  Rotate the day's Shorts between numbers, quotes, fun facts / GTA history and a "how much do you know" quiz; queue an
  Instagram quiz carousel about once a week (content/carousels/gta-quiz-5.json is the template).
- **Vary the graph layout** (Nov 22): bars, counter and `line` charts in a different order than the last uploads
  (the publish check warns on a repeat); every chart with words gets `chart_es` for the Spanish version.
- **Hook**: first sentence = the surprising result as a statement (3-10 words), never a question (35% vs 60% of
  viewers kept); templates with our numbers in resources/hooks-and-titles.md.

**NOV 22 BLUEPRINT RULES (owner: "match the energy", "titles and tags perfect"; apply to every Short).**
- **Market scan first**: YouTube API search (`order=viewCount`, last 48 h, `videoDuration=short`) for "GTA 6" AND "GTA VI"
  AND "Grand Theft Auto VI", merged (a "GTA 6"-only search missed CarryMinati's 18.1M "GTA VI" stream). Copy the
  winning FORMAT we can legally make (e.g. the "every look" montage), never their footage, skits or endings.
- **Energy**: Shorts now default to 0.2 s gaps and hard cuts (no dip to black). Segment 1 = `shots` with 3-5 quick cuts
  (0.25-0.3 s each) that show the payoff in the first 2 s, then the hook clip; a cut every ~1-1.5 s; end on a
  0.3 s-per-shot recap flash that loops into the first line. Examples: episodes/gta6-lucia-outfits.json,
  episodes/gta6-top-3-rides.json.
- **Look at every picture at FULL resolution** before using it: thumbnails hid a pistol (lucia-caminos-08) and a
  revolver (an Ultimate shot, now removed). No weapons in hand, nothing revealing, no near-black frames (brighten a
  dark still with the shot key `"gamma": 1.3`).
- **No two picks of the same thing** in a list/montage (two Ultimate shots were the same outfit).
- **Titles**: the words people search first ("GTA 6" + subject: "Lucia", "outfits", a streamer's name), under 60
  characters before "#GTA6 #Shorts". **Tags**: `tags` (8-15 phrases for THIS Short) and `short_es.tags` / `es.tags` in
  Spanish; the views check warns when they're missing.
- **Don't repeat a topic** we posted in the last 4 days (the $3.79B was made 3 times: the 3rd went Spanish-only).
- **Original first** (Oct 2026 YouTube update: narration over reused footage isn't original, and that was most of our
  Shorts): every narrated Short has at least one `chart` segment (leaderboard / counter / VS) built from numbers WE
  checked (YouTube API counts, official figures), and trailer clips are cutaways. Demo: the chart segments in
  content/episode-format.md. Best fits: streamer leaderboards, money/records, "X vs Y" comparisons, our quiz scores.

**NOV 21 PLAN (owner: "use data to find a plan of action and implement"; overrides the slots and mix below).**
Since launch, people play the game themselves and our trailer-footage Shorts mostly die (Nov 19 noon to Nov 20:
tips/search-answer Shorts got 5-60 views; settings 7, cheat list 5, no-mission-replay 53). What still works:
streamer stories (IShowSpeed family name: 1,179 views, posted 9:28 AM), number/catch hooks on money and hardware
(PS5 vs Pro 1,199; Chapter 1 money catch 496; $3.79B 185), 16-30 s, and MORNING posts (before noon median 21 v/h,
12-5 PM 0.7 v/h). So, every day:
- **9:30 AM (weekends 10 AM): the day's best Short** = streamer/finisher news or a hard-number fact with a catch
  ("The first person to finish GTA 6 wasn't IShowSpeed", "Only 1 in 5 players finished Chapter 1 (trackers)", "61
  cheats unlock after the credits"). Facts from people who finished: only times, records, trophy-tracker %,
  what unlocks after the credits. NEVER the ending, who lives/dies, reactions to the ending (most coverage of
  IShowSpeed's reaction spoils it), late chapters or story beats.
- **12:30 PM: one comparison or money/"catch" Short** (GTA 6 vs 5, prices, records). No plain tips Shorts.
- **8:30 PM: only big confirmed news.** Max 3 own Shorts a day; one strong Short beats three weak ones.
- **Tutorials / how-to / "where is X" go to the WEBSITE guide** (Google search demand: saving, bank account,
  money, lose the cops, easy mode, settings) and to the long video, not to Shorts, until owner gameplay exists
  (a tutorial needs the real menus and map). Use `media/official/leonida-map-poster.jpg` with `magnify`/`zoom`
  for map answers.
- **Formats that need no gameplay (Nov 21, owner: "get views without the live videos")**: YouTube's Oct 2026
  originality update favors Shorts that ADD something, not narration over reused clips. Rotate:
  1. **Quiz** (`"format": "quiz"`, e.g. episodes/gta6-guess-the-ride.json): "Only real GTA 6 fans get 4/4": a
     `magnify` detail of an official screenshot, then the reveal with the name as headline; 4 items, loop ending
     "Tell me your score below, because". Answers only from Rockstar's own pages (vehicle/place names).
  2. **Map vs real life** (`"format": "comparison"`, e.g. episodes/gta6-map-is-florida.json): Rockstar's official
     map (`media/official/leonida-map-poster.jpg`) with `magnify` boxes on labels + a sourced real-place match, and
     one twist (e.g. Florida's highest point is 345 ft, so Mount Kalaga is invented).
  3. **Streamer/finisher news** and **money catches** (above), and **rankings** of things in official media.
  Check every magnify box by cropping it from the image first (labels must be inside the box). For quizzes,
  `studio.vice publish` OCR-reads each guess (zoomed crop + rendered frame) and BLOCKS if the answer is readable
  (Nov 21: the Cheetah badge and the blurred 'Squalo' lettering); still look at the frames yourself.
- **Both channels** (Nov 22): every Short gets Spanish-market `es` titles + `short_pinned_comment_es`; the owner's
  "approve" posts English and Spanish (`studio.ship --upload` also runs `studio.youtube_es`). Mention the Spanish
  titles in the delivery so the owner approves both at once.
- **Views check** (`studio.vice publish`, Nov 21): BLOCKS a Short whose first segment is a still with no zoom/magnify
  (moving first frame: median 92 views vs 18 since launch) and warns on plain tips and scripts over 85 words. Fix the
  Short instead of overriding: segment 1 = a media/trailer clip or `shots`, payoff in line two, 75 words or fewer.
- **Footage**: QC warns when 50%+ of shots repeat recent Shorts. Rotate: least-used clips first (launch-trailer-*
  calm shots, out-now-*, extended-look-convertible-overpass/van-residential/sunset-skyline), and the map poster.
  Owner gameplay (Drive drop zone) beats everything: when it exists, build the Short around it.

**NEW FORMAT MIX (owner approved Nov 20: "let's start right now"; overrides the old main video + 3 Shorts plan).**
Our news/facts Shorts get 300-1,300 views while launch-week winners from tiny channels get 500K-10M. YouTube's
Oct 2026 update favors ORIGINAL Shorts and cuts reach for reused footage + narration that only describes it, and
its "generic or repetitive" rule hits same-template channels. So, every day:
- **11:00 AM: one GTA 6 vs GTA 5 comparison Short** (best format this week: ~940K typical among the top Shorts).
  Angles: things GTA 6 removed / added, cops, car theft, physics, water, map, money. Use `python -m studio.compare
  gta5.mp4 gta6.mp4 -o media/compare/<name>.mp4` for a split screen when owner footage of BOTH games exists;
  otherwise official gameplay clips (`media/trailer/extended-look-*`) with clear GTA 5 vs GTA 6 headlines.
- **6:00 PM: one streamer-moment OR search-answer Short.** Streamer news told in our voice with our footage
  (never theirs), or an answer to what people are searching TODAY (Google Trends / "how old is Jason", "is Niko in
  GTA 6"...), with a specific in-game answer.
- **8:30 PM: only for big confirmed news** (e.g. Take-Two's official sales). No filler.
- **No daily long main video** (ours get ~0 views); the website guide stays (Google + Amazon).
- **Title = curiosity or comparison, never a plain headline**: "GTA 6 took away 4 things GTA 5 gave you", "...Will
  Shock You", "Still think it's small?". 15-30 s. First frame = MOTION (a clip, not a still) + the payoff as text.
- **Narration must add something** (a fact, a comparison, an opinion), never just describe the picture.
- **Owner gameplay first**: when `media/gameplay/` has highlights, build the Short around the best one.
- **Demand check first (free):** web-search what GTA 6 players are asking TODAY (Google Trends "GTA 6" related
  queries, top questions on news sites); prefer topics with clear search demand. The owner checks YouTube Studio
  Research / Ask Studio on his phone and may send topics: those win.
- **Website guide: only when there's a real search question** (editions/price, money, cheats, map regions, PC status,
  "how old is Jason"...), and each guide must add something original (a checked comparison table, our own take,
  sources). No filler pages: Google's Aug 2026 spam update targets scaled automated content. Skip the guide on days
  with nothing new.
- **Goal:** YouTube's expanded Partner tier (500 subscribers + 3M Shorts views in 90 days) during the launch window;
  from Feb 1, 2027 the full-YPP bar for new channels doubles (20M Shorts views or 8,000 hours).
- Set `"format"` in each episode (comparison / streamer / search-answer / discovery / news) so the scorecard
  compares formats. Check `content/learn/scorecard.md` "By format" and drop formats that keep losing.

1. **Pick the topic.** If today's plan row or a slow news day matches a ready-made file in `episodes/backlog/`
   (see its README), use it: refresh the facts, then render. It saves research. On Sundays the main video is the weekly recap, "GTA 6 This Week: <the week's biggest story>":
   the 5-7 biggest confirmed stories of the past 7 days (use `content/log.md`, our Shorts and fresh searches), one segment
   each, with our take; the Short is the week's single biggest moment. (A plan row for that Sunday overrides this.)
   Otherwise: Today's date is in your context. Read `content/launch-plan.md` and use today's row.
   **Shorts (Nov 22 - Dec 5):** use today's two rows in `content/vice-calendar.json` (`python -m studio.vice batch`); a
   row marked "BLOCKED until recorded" needs owner gameplay: if `media/gameplay/` has none, take the next ready row.
   Before delivering, run `python -m studio.vice publish episodes/<slug>.json` and include its QC result.
   If there is no row for today, take the best unused idea from `content/learn/ideas.md` (freshest research; re-check its facts;
   mark it USED), then `resources/topic-bank.md` (older angles, Nov 16), or search the web for what GTA 6 players are searching for and talking about
   right now and pick the strongest topic. Check `content/log.md` and `episodes/` so you never repeat a
   topic that was already made. If a market winner shows a GTA 6 story or angle people are hungry for that we
   haven't covered, prefer it (with our own research and angle).
2. **Make it** following CLAUDE.md: research with web search (facts from the last few days, keep source
   URLs), write `episodes/<slug>.json` with `segments`, `short` (cut from this video) and `shorts` holding
   TWO standalone Shorts (owner asked for 3 Shorts a day in launch week): id `news` (posted 8:30 PM) and id `tips`
   (posted 12:30 PM: one quick, useful GTA 6 tip or fact players are searching today, different from the main video).
   **First run `python -m studio.status`**: any slot already shown with ⏰ today is TAKEN (the main chat may have
   scheduled a Short there); leave that Short out of `shorts` and don't upload into a taken slot. Its "Free slot"
   lines (from `python -m studio.quota`) list the open slots for 3 days and how many uploads today's YouTube quota
   still fits: propose DAYTIME free slots only (9:30/10 AM first, then 12:30 PM; evening slots only for big confirmed
   news: since launch, posts after 7 PM got 0-30 views). More narrated Shorts in bad slots don't add views and make
   the channel look mass-produced; owner gameplay or a real angle does. Also skip topics
   those scheduled videos already cover (e.g. Fri Nov 20 12:30 PM = "Don't grind money in Chapter 1"). For that news Short, prefer what big streamers and creators are
   doing with GTA 6 right now (launch marathons, records, viral moments, reactions), else the most-talked-
   about GTA 6 news of the day; it must be a different story from the main video. Then ONE command renders
   everything (gameplay pull, main video, all Shorts, Spanish-voice Shorts, check sheet): `python -m studio.ship
   episodes/<slug>.json`. Read `output/<slug>/check.jpg` once (captions readable, headlines not clipped, no black
   frames); fix the episode and re-run only if something is wrong.
3. **Deliver for review**:
   - Put `title_options` (3 titles, best first) and `pinned_comment` in the episode JSON. From
     `content/learn/comments.json`, take up to 8 recent comments without a reply (skip spam/hate) and add
     `comment_replies`: [{`author`, `comment`, `url`, `reply`}] with replies in the Vice Replay voice (short,
     friendly, hyped, a question when it helps; Spanish reply to a Spanish comment). Then run
     `python -m studio.review_page episodes/<slug>.json`. It builds `output/<slug>/review/` (index.html plus
     the videos and thumbnails, with posting times for today's weekday).
   - Update the owner's pinned review page (URL in `content/owner.md`) with the Artifact tool: first
     `action: "read"` on that URL and `action: "list", scope: "files"` on it, then publish
     `output/<slug>/review/index.html` with that `url`, passing every other file in the review folder via
     `files`, and `null` for each old file listed that isn't in today's set. Each file must be under 15 MB
     (re-encode with a higher `-crf` if not). If updating the URL fails, publish a new page and give its link.
   - The review page also shows a "TikTok / Reels caption" for each Short (the owner reposts Shorts on TikTok and
     Instagram by hand; TikTok keeps API posts from unaudited apps private). Optionally set `tiktok_hashtags`
     per Short (3-5 hashtags people search on TikTok right now).
   - Also send the main .mp4, every Short .mp4 and thumbnail-a/b/c.jpg with SendUserFile (status
     `proactive`) so the owner can save them to upload.
   - "approve" / "approve all" also posts the `comment_replies` (the uploader's `replies` item); "approve the Shorts"
     doesn't. Show the replies on the review page so the owner can change or drop any before approving.
   - Final message starts with: **Reply "approve" in the main chat ("🎬 Vice Replay Studio (main control)") to schedule
     everything on YouTube** (this scheduled chat can't upload) (or
     "approve the Shorts", "approve, use title 2", or ask for changes first). Then: the review page link, the posting plan (times from the page), the recommended title, and
     anything to double-check (e.g. a fact that was still developing). Remind them to set Test & Compare with
     the 3 thumbnails and "Related video" on the Shorts.
3b. **Website** (vicereplay.com): write a guide for today's main video as `site/guides/<slug>.json` (format at the top of the
   loader in `tools/site_guides.py`: slug, lang "en", title (60-70 chars, keyword first), desc, date, video (YouTube id once
   uploaded, else null), card [line1, line2, screenshot from media/official], lede, 3-6 sections [heading, short HTML
   paragraphs/lists] rewritten from the script for reading, 1-3 faq, gear ["game","storage"] when it fits, sources).
   Also write the Spanish version as `site/guides/<slug>-es.json` (lang "es", natural Latin American Spanish, same facts,
   Spanish slug in `slug`, e.g. "gta-6-trucos-de-dinero"). Also prepend 1-2 dated lines to `site/live.json` with today's biggest confirmed news (launch week; link our guide).
   Same facts and rules as the video: sourced, rumors labeled, no spoilers. First try to save directly: if the repos were attached with push access and `git push` works, commit +
   push these files yourself and publish the site per publish-site.md. If push is refused (403), don't retry:
   publish by calling `fire_trigger` with trigger_id `trig_01XX9xXTp8xfb4i3yYUFP9uF` (it wakes the owner's main control session,
   which can push) and `text` = "FILES:" then each file path on its own line followed by its full contents. ALWAYS
   include `episodes/<slug>.json` and the new `content/log.md` line too: the main chat saves them, and because this
   scheduled chat can't upload, the owner approves in the main chat ("🎬 Vice Replay Studio (main control)"), which
   re-renders from the episode file and uploads. Say that in the final message: "Reply approve in the main chat". If
   fire_trigger isn't available or fails, say the website update is waiting and attach the JSON files with SendUserFile.
3d. **TikTok chat**: `send_message` session `session_01CJRsWQ4prmRGdfaEyZXz7q` ("📱 Vice Replay: TikTok files") with, for every Short
   (English and Spanish): its TikTok caption + hashtags and a posting time (after the YouTube version), and say the
   files are in today's daily-run chat. Treat it as a hand-off; don't wait for a reply.
3c. **Spanish voice Shorts** are made by studio.ship (files end in `-es.mp4`). Send them with SendUserFile too, labeled
   for TikTok/Instagram in Spanish. They are NOT uploaded to the main YouTube channel.

4. **Save the record**: add a line to `content/log.md` (date, slug, title, topic choice reason), run
   `python -m studio.tidy`, then commit `episodes/<slug>.json`, `content/log.md` and `content/INDEX.md` and push to `main`. Videos are not committed.
   If push is refused (403), don't retry: send the episode JSON with SendUserFile and say the log wasn't saved.
5. **Campaign clips**: only for campaigns the owner approved (`owner_approved: true`); never start or join one
   yourself. For each `content/campaigns/*.json` with `owner_approved` true, `status` `active` and something in
   `source_queue`, follow `.claude/commands/campaign-clips.md` and deliver up to `max_clips_per_day` clips
   in the same report, with a posting time from the schedule and the reminder to submit each clip on the
   campaign page within 30 minutes of it going live.
6. If something fails (render error, no reliable news), still report what happened and what you made.

**New tools (Nov 20):** formats `details` / `ranking` / `search-answer` and the editing keys (focus, speed, freeze,
magnify, callout, zoom, shots) are in `content/episode-format.md`. Read footage at full resolution before writing any
on-screen fact; fix every "crosses a shot change" warning; run `python -m studio.vice publish` and report its QC line
with the delivery. `python -m studio.vice dashboard` is the owner's local control panel (no upload button).
