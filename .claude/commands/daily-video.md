---
description: The automated daily run - pick today's topic, make the video + Short + thumbnail, and deliver them for review
---
You are running the daily Vice Replay automation. Nobody is watching live, so don't ask questions:
make sensible choices, finish the whole run, and explain your choices in the final report.

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
   shooting/gore in the first 7 seconds: use a calm clip or official picture). Title like "Wildest GTA 6 moment
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
- Set `"format"` in each episode (comparison / streamer / search-answer / discovery / news) so the scorecard
  compares formats. Check `content/learn/scorecard.md` "By format" and drop formats that keep losing.

1. **Pick the topic.** If today's plan row or a slow news day matches a ready-made file in `episodes/backlog/`
   (see its README), use it: refresh the facts, then render. It saves research. On Sundays the main video is the weekly recap, "GTA 6 This Week: <the week's biggest story>":
   the 5-7 biggest confirmed stories of the past 7 days (use `content/log.md`, our Shorts and fresh searches), one segment
   each, with our take; the Short is the week's single biggest moment. (A plan row for that Sunday overrides this.)
   Otherwise: Today's date is in your context. Read `content/launch-plan.md` and use today's row.
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
   scheduled a Short there); leave that Short out of `shorts` and don't upload into a taken slot. Also skip topics
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
