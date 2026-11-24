---
description: Afternoon momentum check - spot a Short that is taking off and prepare a follow-up while the topic is hot
---
Momentum run for Vice Replay. Nobody is watching live: don't ask questions. Read `content/INDEX.md` first.

0. Run `python -m studio.title_swap` (owner's standing approval: swaps the title of uploads that underperform after
   24-96 h to their option 2, once). Report any swap in the final message.
1. Run `python -m studio.learn --mine` (our uploads with views per hour). From `content/learn/channel.json`, take our
   Shorts published in the last 48 hours and compute views per hour. A Short has MOMENTUM when its views/hour is at
   least 2x the median of our Shorts from the last 7 days AND it has 500+ views.
2. No momentum: reply in 2 lines (best Short today + its views/hour) and stop. Don't search, don't render.
3. Momentum: search the web for what's NEW on that exact topic in the last 12 hours (reputable outlets only; label
   rumors). Write ONE follow-up Short in `episodes/<slug>-followup.json` (CLAUDE.md format, 3-4 segments, 20-40 s,
   hook in 2 seconds, `short_es` + `text_es`, `sources`, `pinned_comment`). It must add something new: the next fact,
   the answer to the top comment's question, or "part 2". Never a re-cut of the same video (mass-produced content
   gets demonetized). Render with `python -m studio.ship episodes/<slug>-followup.json` (gameplay + EN/ES Shorts) and read `output/<slug>-followup/check.jpg` once.
4. Hand it to the main chat (it can upload; this run can't): call `fire_trigger` with trigger_id
   `trig_01XX9xXTp8xfb4i3yYUFP9uF` and `text` = "FILES:" then `episodes/<slug>-followup.json` and its full contents,
   plus a first line "MOMENTUM: <original Short title> is at <n> views/hour; follow-up ready, owner approves in main chat."
   Also send the .mp4 files with SendUserFile and finish with: **Reply "approve" in the main chat to post the follow-up.**
5. Don't upload anything, don't push, don't make more than one follow-up per run.

**Nov 22-23 (owner): original first, no trailer images.** A follow-up Short is built from GTA 6-style lettering
cards (`studio/vicecards.py`) around new checked numbers with a `src` on screen, or the owner's gameplay; trailer clips
and official screenshots are blocked by `studio.vice publish`.
