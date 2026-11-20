---
description: Make clips for a paid clipping campaign (Whop / Content Rewards etc.) following its rules
argument-hint: <campaign short-name> [source video link or file]
---
Make clips for the campaign `$ARGUMENTS` following CLAUDE.md and `content/campaigns/README.md`.
GTA 6 campaigns only. A non-GTA campaign belongs to ClipCircuit (`content/channels.md`): add it to its Campaign inbox,
tell the owner, and stop. Max 2 campaign clips a day on Vice Replay YouTube, fresh moments only.
**Pick the moment first (free):** `python -m studio.moments <streamer> --hours 12` lists what's already clipped
(TAKEN words) and the winning length; choose a moment NOT on that list. No campaign clips on Instagram (Meta
de-ranks accounts that mostly repost; Nov 19 ad flag).
Two editing engines: **local** (free: `studio/clip.py`) and **everygen** (better edits, but uses the owner's paid
Everygen credits; the ClipCircuit method from the owner's other channel). The campaign file's `"engine"` picks one;
default `local`.

## 0. Fast path that works (Nov 19, Everygen, about 1 credit per clip)
1. Source links: `python -m studio.twitch_clips --campaigns` (top clips of the last 24 h per approved campaign's
   `twitch_login`, risky titles dropped; needs content/twitch-setup.md done), else the owner pastes Twitch clip links
   (twitch.tv/<streamer>/clip/...; "Top - Last 24 hours" = freshest moments).
2. `download_video` each link (free, seconds). `inspect_media` spread 6 on all of them (free) and judge:
   keep animals, cops, crashes, stores, food, funny reactions with the streamer's face reacting; DROP cutscenes,
   nudity/sexual scenes, violence against people/women, "murder", anything that makes the streamer look bad,
   clips under ~8 s. `ask_video` (1 credit/min) only when the words matter for the hook or captions.
3. One `edit_media` per clip: `reframe` 9:16 on the FULL clip first (it stacks the facecam on top; trimming first
   can break the stack), then `trim` (ranges) if needed, `blur_region` x 0.95 y 0.40 w 0.05 h 0.14 (chat-platform
   icons: "no logos" rules), `overlay_text` hook (3-5 words naming the streamer, top, margin 0.375, size m, box, 0-3 s);
   timed caption lines with more `overlay_text` (bottom, margin 0.12) when the clip has no burned-in captions.
   `inspect_media` 4 frames to check (face on top, text not clipped).
4. `curl` the result URL (media.viewmax.io is allowed) to `output/clips/<campaign>/<name>.mp4`, SendUserFile it with
   a title + description (name + required hashtag + "Watch <streamer> live on Twitch"), and queue it for Instagram
   (two campaign clips per slot, `.claude/commands/instagram.md`). YouTube downloads of long VODs time out here:
   use Twitch clips instead. Check `get_credit_balance` before/after a batch and tell the owner the credits used.
   What gets views (307 Lacy Shorts, Nov 19): 8-16 s beats 20-30 s by ~7x views/hour; simple title with the streamer
   first + one emoji ("Lacy Arrested on Day 1 in GTA 6!! 💀"); "firsts" and funny discoveries; fresh moments.
   Source tip: clippers' descriptions sometimes include the original clips.twitch.tv link (YouTube API, free).
5. Owner posts on YouTube and sends the link: log it in tracker.md, schedule the 20-minute submit reminder.
   At ~2,000 views ask for the clip's country-breakdown screenshot (campaign audience rule).

## 1. The campaign (owner approval first)
- Read `content/campaigns/<name>.json`. If it doesn't exist, ask the owner for the campaign page details and create it
  from `_example.json` with `owner_approved: false`. **Stop unless `owner_approved` is true.** Never set it yourself;
  only when the owner approves this specific campaign in chat. Only GTA 6 campaigns that allow clipping the footage.
- When helping the owner choose between campaigns, compare in this order: minimum payout as views needed per clip
  (min payout / rate x 1000), budget left, number of clippers, accepted platforms (want TikTok, Instagram, YouTube),
  rules. Skip pool campaigns with six-figure view minimums. Rules locked until joining: ask for a screenshot and copy
  them word for word into `rules`.

## 2. Footage (both engines)
- Owner's choice (Nov 19, final): Everygen, carefully: at most 1 hour searched and 2 clips finished per batch, balance
  checked before/after and the credits spent reported. The free `local` engine + Drive inbox is the backup.
  YouTube/Twitch can't be downloaded here (blocked): the owner saves the stretch (2-5 min around the moment) to Google
  Drive, shares it "Anyone with the link", and `python -m studio.clip <drive file link> --campaign <name>` fetches it
  into output/campaign_footage/ (never media/).
- Easiest: the owner drops screen recordings into the Drive "Campaign clips folder" (owner.md), subfolder per campaign;
  `python -m studio.campaign_inbox` downloads the new ones and cuts 2 clips each.
- Find new source videos first, free: `python -m studio.campaign_sources` (approved, non-paused campaigns with a
  `youtube_handle`; marks videos not yet used). Put picks in the campaign's `source_queue`, used ones in `used_sources`.
- Only from where the campaign says (`source_footage`), the source given here, else the next `source_queue` item.
  Real source footage only: never AI voice, AI video, generated footage or Vice Replay music on campaign clips; keep
  the original audio. If a host is blocked, say which one and stop.
- Pick moments cheaply: if the owner or the campaign names the moments, cut only those windows. Never run paid
  analysis on a whole long video (Everygen `analyze_video` / `find_clips` on long sources) without the owner's yes.

## 3a. Engine `local` (free)
1. If `facecam_box`/`gameplay_box` aren't set for this streamer: grab one frame, look at it, measure the camera and
   game areas as fractions of the frame, save them in the campaign file.
2. `python -m studio.clip <source> --campaign <name> --top <N>` (N = 2x `max_clips_per_day` so the owner can pick).
   Look at 2 frames of each; drop clips that are boring, cut mid-sentence or break a rule. For the best, re-run with
   `--at <second>` and a `--headline` hook (3-5 words the clip actually supports).

## 3b. Engine `everygen` (paid credits; read the Everygen guide phase "editing" first)
Before spending: `estimate_generation_cost` for the batch, tell the owner in one line ("4 clips, N credits"), and go
only on their yes. Then per clip:
1. `download_video` with from/to (about 50 s windows around known moments). Reframe all clips in ONE `edit_media`
   call (reframe, aspect 9:16, speaker crop). If the window cuts to another person, trim that part off in the same
   call. Check frames with `inspect_media`.
2. One `open_edit` project per clip (9:16), `open_edit_preview` once, `transcribe_edit_clip` with words.
3. One complete idea, setup + payoff, 20-35 s, opening on the strongest line and ending on a full sentence.
   `find_cut_points` on the edges, then `trim_edit` (remove, keep); move voiced edges to the next pause.
4. `caption_edit` style stream-story, yPercent 64, profanity stars, maxDuration 2 (unless the campaign's rules say
   otherwise). Hook card on track 2 for 3 s: 3-5 words the clip supports, white with black stroke, inside the safe zone.
5. Break shots longer than about 7 s at sentence breaks with a gentle alternating zoom.
6. `check_edit` (apply its pause cuts, fix captions crossing cuts; up to 3 rounds), `view_edit_frame` with the
   safe-zone overlay at start/middle/end, proofread captions against the transcript.
7. `export_edit` HD, `get_edit_render`: QA must pass (about -14 LUFS, no black, frozen or silent stretches).
   Hand the file over with `open_edit` on the export + `open_edit_preview` (Download button), plus the direct media
   URL as a backup (open in Safari, Share, Save Video). No comedic sound effects on serious campaigns.

## 4. Deliver, post, submit, track
- Deliver each clip with its caption: hook line, one sentence of context, a question, the creator credit
  (`on_screen_credit`), the campaign link, the required hashtags + 2-3 relevant tags; title = curiosity + the real
  claim + the required hashtag. Say which platforms (same clip to TikTok, Instagram Reels and YouTube Shorts if the
  campaign allows; Instagram tends to pay best).
- At the top, in bold: **submit each clip on the campaign page within 30 minutes of it going live** (CLAUDE.md
  schedules a 25-minute reminder when the owner says they posted one).
- Posting: strongest clip first, at most `max_clips_per_day`, never several clips from one source back to back, and
  only at times the owner can submit right away. The owner posts campaign clips; never upload them.
- Add a row per clip to `content/campaigns/tracker.md` (campaign, clip, engine, platforms, posted/submitted times,
  views, views needed to pay, approved, earned, URLs, Everygen project id/export URL, issues) and remove the used
  `source_queue` item. Never claim a clip is posted, submitted, approved or paid without seeing it.
- Commit and push (if the push is refused, say so).

## What wins (research from ClipCircuit)
Viewers decide in about 1.5-2 s: aim for 70-80% still watching at 3 s. 2-3 caption changes in the first 3 s. Shorter
clips with high completion beat longer ones. One sharp idea that lands without context. Volume wins (no submission
limit), and skip the moment every other clipper will cut: pick the strong one nobody else noticed.
