---
description: The automated daily run - pick today's topic, make the video + Short + thumbnail, and deliver them for review
---
You are running the daily Vice Replay automation. Nobody is watching live, so don't ask questions:
make sensible choices, finish the whole run, and explain your choices in the final report.

1. **Pick the topic.** Today's date is in your context. Read `content/launch-plan.md` and use today's row.
   If there is no row for today, search the web for what GTA 6 players are searching for and talking about
   right now and pick the strongest topic. Check `content/log.md` and `episodes/` so you never repeat a
   topic that was already made.
2. **Make it** following CLAUDE.md: research with web search (facts from the last few days, keep source
   URLs), write `episodes/<slug>.json` with both `segments` and `short`, render the `--preview`, check 3-4
   frames, then render the final video and the `--short`.
3. **Deliver for review** as a private review page, published with the Artifact tool (load the
   artifact-design skill first if you have it). Put these in one folder and publish `index.html` with the
   other files passed through `files`:
   - the main .mp4, the -short.mp4 and thumbnail.jpg from `output/<slug>/` (each must be under 15 MB:
     if one isn't, re-encode it with ffmpeg at a higher `-crf`, e.g. 26, until it fits);
   - `index.html`: page title "Vice Replay: <short topic>". Show the thumbnail, a `<video controls>` player
     for each video, each with a download link, and copy buttons for: 3 title options (best first), the
     full description.txt, the tags from tags.txt, and a title + 2-3 hashtags for the Short. Dark
     background, pink #FF1F8E / cyan #00E5D2 accents, readable on a phone.
   Also send the files with SendUserFile (status `proactive`) if that tool is available.
   End the run with a short message: the review page link, the recommended title, and anything the
   owner should double-check (e.g. a fact that was still developing).
4. **Save the record**: add a line to `content/log.md` (date, slug, title, topic choice reason), then
   commit `episodes/<slug>.json` and `content/log.md` and push to `main`. Videos are not committed.
5. If something fails (render error, no reliable news), still report what happened and what you made.
