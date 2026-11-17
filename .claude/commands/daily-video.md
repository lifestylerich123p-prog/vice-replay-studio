---
description: The automated daily run - pick today's topic, make the video + Short + thumbnail, and deliver them for review
---
You are running the daily Vice Replay automation. Nobody is watching live, so don't ask questions:
make sensible choices, finish the whole run, and explain your choices in the final report.

0. **Gameplay**: if `content/owner.md` has a Google Drive folder link, run `python -m studio.gameplay` to pull
   new recordings and cut highlights into `media/gameplay/` (used as backgrounds automatically; prefer
   them over screenshots). If there's a great highlight (high score, something wild happens), make one
   of today's Shorts a "wildest moment" Short around it: our voice explaining what happened, game sound
   under it (set that segment's `media` to the clip). `media/gameplay/processed.json` gives each clip's
   `category` from the Drive subfolder it was dropped in (Wildest moments, Chases & crashes, Funny & fails,
   Glitches, Scenery & cars): use it for the Short's angle, e.g. a "funniest fail of the day" Short.
0b. **Learn first**: run `python -m studio.learn` (YouTube Data API; if it fails because there is no API key,
   say so in the report and continue). Then read `content/learn/channel.json` (our uploads with views/hour),
   today's `content/learn/market-<date>.md` (the hottest GTA 6 videos and Shorts on YouTube right now),
   `content/learn/patterns.md` and `content/learn/lessons.md`. Write 1-3 new dated lessons to `lessons.md`:
   which of OUR topic kinds, hooks, title styles and posting times got the most views per hour, and what the
   market's winners have in common (topics, title wording, length, Shorts vs long). Only claim what the
   numbers show. Use the lessons in every choice below: topic, hook, title options, thumbnail text, length.
   Learn from winning videos' patterns; never copy their titles, footage or thumbnails.
1. **Pick the topic.** Today's date is in your context. Read `content/launch-plan.md` and use today's row.
   If there is no row for today, search the web for what GTA 6 players are searching for and talking about
   right now and pick the strongest topic. Check `content/log.md` and `episodes/` so you never repeat a
   topic that was already made. If a market winner shows a GTA 6 story or angle people are hungry for that we
   haven't covered, prefer it (with our own research and angle).
2. **Make it** following CLAUDE.md: research with web search (facts from the last few days, keep source
   URLs), write `episodes/<slug>.json` with `segments`, `short` (cut from this video) and `shorts` holding
   ONE standalone news Short (id `news`). For that news Short, prefer what big streamers and creators are
   doing with GTA 6 right now (launch marathons, records, viral moments, reactions), else the most-talked-
   about GTA 6 news of the day; it must be a different story from the main video. Render the `--preview`,
   check 3-4 frames, then render the final video and `--short` (renders both Shorts).
3. **Deliver for review**:
   - Put `title_options` (3 titles, best first) and `pinned_comment` in the episode JSON, then run
     `python -m studio.review_page episodes/<slug>.json`. It builds `output/<slug>/review/` (index.html plus
     the videos and thumbnails, with posting times for today's weekday).
   - Update the owner's pinned review page (URL in `content/owner.md`) with the Artifact tool: first
     `action: "read"` on that URL and `action: "list", scope: "files"` on it, then publish
     `output/<slug>/review/index.html` with that `url`, passing every other file in the review folder via
     `files`, and `null` for each old file listed that isn't in today's set. Each file must be under 15 MB
     (re-encode with a higher `-crf` if not). If updating the URL fails, publish a new page and give its link.
   - Also send the main .mp4, every Short .mp4 and thumbnail-a/b/c.jpg with SendUserFile (status
     `proactive`) so the owner can save them to upload.
   - Final message: the review page link, the posting plan (times from the page), the recommended title, and
     anything to double-check (e.g. a fact that was still developing). Remind them to set Test & Compare with
     the 3 thumbnails and "Related video" on the Shorts.
4. **Save the record**: add a line to `content/log.md` (date, slug, title, topic choice reason), then
   commit `episodes/<slug>.json` and `content/log.md` and push to `main`. Videos are not committed.
   If the push is refused, try once to attach the repo with push access (add_repo), push again, and if it is
   still refused don't keep trying: send the episode JSON with SendUserFile and say the log wasn't saved.
5. **Campaign clips**: only for campaigns the owner approved (`owner_approved: true`); never start or join one
   yourself. For each `content/campaigns/*.json` with `owner_approved` true, `status` `active` and something in
   `source_queue`, follow `.claude/commands/campaign-clips.md` and deliver up to `max_clips_per_day` clips
   in the same report, with a posting time from the schedule and the reminder to submit each clip on the
   campaign page within 30 minutes of it going live.
6. If something fails (render error, no reliable news), still report what happened and what you made.
