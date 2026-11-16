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
3. **Deliver for review** with SendUserFile (status `proactive`): the main .mp4, the -short.mp4 and
   thumbnail.jpg from `output/<slug>/`. Then post one message containing, ready to paste into YouTube Studio:
   3 title options (best first), the full description.txt, the tags from tags.txt, and a title + 2-3
   hashtags for the Short. Point out anything the owner should double-check (e.g. a fact that was still
   developing).
4. **Save the record**: add a line to `content/log.md` (date, slug, title, topic choice reason), then
   commit `episodes/<slug>.json` and `content/log.md` and push to `main`. Videos are not committed.
5. If something fails (render error, no reliable news), still report what happened and what you made.
