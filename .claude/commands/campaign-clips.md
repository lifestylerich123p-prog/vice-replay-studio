---
description: Make clips for a paid clipping campaign (Whop Content Rewards etc.) following its rules
argument-hint: <campaign short-name> [source video link or file]
---
Make clips for the campaign `$ARGUMENTS` following CLAUDE.md and `content/campaigns/README.md`.

1. Read `content/campaigns/<name>.json`. If it doesn't exist, ask the owner for the campaign page details
   and create it from `_example.json` with `owner_approved: false`. **Stop unless `owner_approved` is
   true**: the owner must approve every campaign first. Never set it yourself; only when the owner says
   in chat that they approve this specific campaign. Only GTA 6 campaigns that allow clipping the footage.
2. Get the footage: the source given here, else the next item in `source_queue`. Download it only from where
   the campaign says footage comes from. If a host is blocked, say which one and stop.
3. If `facecam_box`/`gameplay_box` aren't set for this streamer yet: grab one frame, look at it, measure the
   camera and game areas as fractions of the frame, and save them in the campaign file.
4. Run `python -m studio.clip <source> --campaign <name> --top <N>` (N = 2x `max_clips_per_day` so the owner
   can pick). Look at 2 frames of each clip; drop clips that are boring, cut mid-sentence, or break a rule.
   For the best ones, re-run with `--at <second>` and a `--headline` hook (3-5 words, from what is said).
5. Deliver with SendUserFile: the clips plus, for each, a caption with the campaign's required hashtags,
   tags and text, and which platform to post on. Put this at the top, in bold: **submit each clip on the
   campaign page within 30 minutes of it going live**. Suggest posting times from the schedule only when
   the owner is likely free to submit right away, and tell them to log posted/submitted times in the tracker.
6. Add a row per delivered clip to `content/campaigns/tracker.md` and remove the used item from
   `source_queue`; commit and push (if the push is refused, say so).
