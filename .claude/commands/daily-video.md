---
description: The automated daily run - pick today's topic, make the video + Short + thumbnail, and deliver them for review
---
You are running the daily Vice Replay automation. Nobody is watching live, so don't ask questions:
make sensible choices, finish the whole run, and explain your choices in the final report.

0. **Gameplay**: if `content/owner.md` has a Google Drive folder link, run `python -m studio.gameplay` to pull
   new recordings and cut highlights into `media/gameplay/` (used as backgrounds automatically; prefer
   them over screenshots). If there's a great highlight (high score, something wild happens), make one
   of today's Shorts a "wildest moment" Short around it: our voice explaining what happened, game sound
   under it (set that segment's `media` to the clip).
1. **Pick the topic.** Today's date is in your context. Read `content/launch-plan.md` and use today's row.
   If there is no row for today, search the web for what GTA 6 players are searching for and talking about
   right now and pick the strongest topic. Check `content/log.md` and `episodes/` so you never repeat a
   topic that was already made.
2. **Make it** following CLAUDE.md: research with web search (facts from the last few days, keep source
   URLs), write `episodes/<slug>.json` with `segments`, `short` (cut from this video) and `shorts` holding
   ONE standalone news Short (id `news`). For that news Short, prefer what big streamers and creators are
   doing with GTA 6 right now (launch marathons, records, viral moments, reactions), else the most-talked-
   about GTA 6 news of the day; it must be a different story from the main video. Render the `--preview`,
   check 3-4 frames, then render the final video and `--short` (renders both Shorts).
3. **Deliver for review** with SendUserFile (status `proactive`): the main .mp4, the -short.mp4 and
   thumbnail-a/b/c.jpg from `output/<slug>/`, plus the second Short (`-short-news.mp4`). Then post one message containing, ready to paste into YouTube Studio:
   3 title options (best first), the full description.txt, the tags from tags.txt, and for each Short
   the contents of its .txt file. Add a **posting plan**: the exact time to schedule each
   upload today, from the posting schedule in CLAUDE.md for today's weekday (Eastern time, plus the
   owner's local time if `content/owner.md` gives a time zone), and the `pinned_comment` to pin on each.
   Remind them to add thumbnail-a/b/c with Test & Compare on the main video and to link the main video
   as the Shorts' "Related video". Point out anything the owner should double-check (e.g. a fact that was still
   developing). Only if SendUserFile is not available: publish a private review page with the Artifact tool
   holding the videos, thumbnail and that text instead.
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
