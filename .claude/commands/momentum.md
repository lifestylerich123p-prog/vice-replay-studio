---
description: Afternoon momentum check - spot a Short that is taking off and prepare a follow-up while the topic is hot
---
Momentum run for Vice Replay. Nobody is watching live: don't ask questions. Read `content/INDEX.md` first.

1. Run `python -m studio.learn --mine` (our uploads with views per hour). From `content/learn/channel.json`, take our
   Shorts published in the last 48 hours and compute views per hour. A Short has MOMENTUM when its views/hour is at
   least 2x the median of our Shorts from the last 7 days AND it has 500+ views.
2. No momentum: reply in 2 lines (best Short today + its views/hour) and stop. Don't search, don't render.
3. Momentum: search the web for what's NEW on that exact topic in the last 12 hours (reputable outlets only; label
   rumors). Write ONE follow-up Short in `episodes/<slug>-followup.json` (CLAUDE.md format, 3-4 segments, 20-40 s,
   hook in 2 seconds, `short_es` + `text_es`, `sources`, `pinned_comment`). It must add something new: the next fact,
   the answer to the top comment's question, or "part 2". Never a re-cut of the same video (mass-produced content
   gets demonetized). Run `python -m studio.gameplay` first, then render `--short` and `--short --es`, check 3 frames.
4. Hand it to the main chat (it can upload; this run can't): call `fire_trigger` with trigger_id
   `trig_01XX9xXTp8xfb4i3yYUFP9uF` and `text` = "FILES:" then `episodes/<slug>-followup.json` and its full contents,
   plus a first line "MOMENTUM: <original Short title> is at <n> views/hour; follow-up ready, owner approves in main chat."
   Also send the .mp4 files with SendUserFile and finish with: **Reply "approve" in the main chat to post the follow-up.**
5. Don't upload anything, don't push, don't make more than one follow-up per run.
