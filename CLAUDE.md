# Vice Replay Studio

Video machine for the YouTube channel **Vice Replay** (@ViceReplayTV-q8s), a GTA 6 fan channel, and builder of
vicereplay.com. Tagline: "GTA's wildest moments. On replay." Brand: neon synthwave, hot pink #FF1F8E + cyan #00E5D2
on deep purple/black, Anton headlines. Start every run with `content/INDEX.md` (map of everything) instead of searching.
Owner runs 3 channels with separate jobs (`content/channels.md`, shared copy in Drive "Creator HQ"): Vice Replay =
GTA 6 channel + makes ALL GTA 6 campaign clips, which are POSTED ON CLIPCIRCUIT (@ClipCircuit-m5f), never on
Vice Replay (owner, Nov 20: reposted clips can mark the main channel an aggregator); ClipCircuit also does every
non-GTA campaign; What If Arena = AI videos.

## How a video gets made
1. **Research** with web search: check `content/learn/scorecard.md`, `ideas.md`, `lessons.md`, `content/performance.md` and the latest
   `content/learn/market-*.md` first and lean toward what works. Use only facts from today/recent days, keep source
   URLs for `sources`, and label rumors/leaks ("reportedly", "according to leaks").
2. **Write** `episodes/<slug>.json` exactly as `content/episode-format.md` says (read it first: segments, hook in the
   first 2-10 s, Shorts that loop, follow badge, pinned comment, Spanish `text_es`, affiliate rules, playlists).
3. **Render + check in one command**: `python -m studio.ship episodes/<slug>.json` (gameplay pull, main video,
   Shorts, Spanish-voice Shorts, `output/<slug>/check.jpg`). Read check.jpg once: captions readable, headline not
   clipped, no black bars/frames; read `output/<slug>/description.txt`. (Manual: `studio.make_video` with
   `--preview`, `--short`, `--short --es`.)
4. Report the output paths and 3 alternative titles (under 60 characters, "GTA 6" first).

## Posting schedule (US Eastern; adjust from analytics)
Weekdays: main Short 9:30 AM, tips Short 12:30 PM, main 3:30 PM, news Short 8:30 PM. Saturday: 10 AM, 12:30, 1:30,
8 PM. Sunday: 10 AM, 12:30, 2:30, 7:30 PM (Nov 21 data: morning Shorts ~21 views/h vs 0.7 for 12-5 PM). Big news: post
as soon as it's ready. Upload early, scheduled.

## Rules for this channel
- **Footage**: everything in `media/` is used as backgrounds. Allowed: official Rockstar screenshots
  (`media/official/`, 176 incl. 38 Ultimate Edition shots of cars/shops/style, named by place/character/car, incl. vintage-* and `leonida-map-poster.jpg`, Rockstar's
  official map: use `magnify`/`zoom` for "where is X" Shorts), silent official clips (`media/trailer/launch-trailer-*`,
  `extended-look-*`: real gameplay from Rockstar's "An Extended Look", and `out-now-*`: 3 short clean shots from the
  Nov 19 "Out Now" video; its club/close-up/logo shots are excluded), and the owner's own gameplay (`media/gameplay/`, pulled from the Drive folder in
  `content/owner.md` by `python -m studio.gameplay`, not committed). Never other creators' videos, never a whole
  trailer, clip audio always dropped; narration adds real commentary. Pick `media` per segment by filename and rotate.
  Keep strip-club or sexualized images out (list of excluded shots in owner.md). New official media:
  rockstargames.com/VI/downloads, add only after viewing each.
- **Owner gameplay first**: Shorts automatically use the newest gameplay highlights when they exist (`"keep_media":
  true` keeps a segment's own picture; `"use_gameplay": false` turns it off); at 30+ highlights `studio.tidy`
  retires most stock footage (keeps a core for site cards, thumbnails, character news).
- **No official GTA 6 music** (radio, trailer songs, score): Content ID. Game sound only from the owner's gameplay
  recorded with radio/music off. Audio is our generated synthwave theme + SFX (`"music": "none"`, `"sfx": false`).
- **Cheap**: free Kokoro voice (English `am_michael`, Spanish `em_alex`); no paid APIs unless the owner says so.
- **Footage law** (details: `content/legal.md`): Rockstar's fan policy allows posting the owner's gameplay with real
  commentary; monetization is tolerated, not licensed. Never post isolated cutscenes, endings/big story moments,
  standalone in-game TV/comedy shows, or anything from leaked copies. YouTube ads: no graphic violence in the first
  7 seconds (make_video keeps openings calm automatically) and no violence/gore montages as the focus.
- **Not official**: no Rockstar logos; descriptions keep the "not affiliated" line. No story spoilers in titles or
  thumbnails. Every video needs a real angle; no near-identical/mass-produced videos (demonetization).
- **Uploading needs the owner's approval in chat** ("approve", "approve the Shorts", "approve, use title 2"...): run
  `python -m studio.ship episodes/<slug>.json --upload <all|main,short,news,tips,replies> [--title N]` (or
  `studio.youtube_upload` directly). Never upload campaign clips. Apply requested changes first. Scheduled videos are
  private until their time, so schedule the printed "COMMENTS TO POST" command with send_later for 10 minutes after
  each time ("Post today's pinned comments now: <command>") and run it when it fires. Commit `content/learn/uploads.json` (the upload registry) and refresh the
  dashboard (`/dashboard`) after uploading. Report links and times; remind
  the owner to pin comments, set "Related video" on Shorts, add thumbnails B/C (Test & Compare). Missing YT_* vars:
  say so and list manual steps.
- **Several chats**: only the main control chat posts (YouTube, Instagram, comments, site); helper chats work on
  their own `claude/...` branch and never post. `git pull --rebase origin main` before every commit. Details and the
  duplicate-post guard (studio/postguard.py): `content/owner.md`.
- **Standing approvals** (details and dates in `content/owner.md`): breaking-news Shorts that pass every rule in
  `.claude/commands/breaking-news.md`; comment auto-replies (`auto-replies.md`, `python -m studio.replies`); any
  time-limited approval written there. Nothing else is posted without asking.
- **Momentum** (`momentum.md`, daily): one follow-up Short with something new when a Short takes off; owner approves
  in the main chat. **Website**: daily guide (+ Spanish) via `site/` + `tools/site_guides.py`, published from the main
  chat (`/publish-site`); scheduled runs can't push, they hand files over with fire_trigger.
- **Instagram** (@vice.replaytv, owner approved Nov 19): every uploaded Short and about one carousel/image a day go
  out through `content/learn/reels_queue.json` (max 4 posts/day; campaign clips paused since Meta's Nov 19 ad flag);
  how: `.claude/commands/instagram.md`.
- **TikTok**: the owner posts by hand; Shorts go to the "📱 Vice Replay: TikTok files" chat (see owner.md;
  `studio.ship --tiktok` pushes them to the `tiktok-files` branch).
- **Campaigns** (Whop/Content Rewards): only campaigns with `owner_approved: true` (set only when the owner approves
  in chat), only GTA 6 (any other campaign goes to ClipCircuit: add it to the Campaign inbox in content/channels.md), only footage from where the campaign says, every rule in `content/campaigns/<name>.json`
  (length, credit, hashtags, platforms), original audio, no Vice Replay music, `max_clips_per_day`. Tools:
  `studio/clip.py` (free) or Everygen (paid; spend credits only after a cost estimate and the owner's yes). Every
  delivery says: submit each clip within 30 minutes of posting. When the owner says they posted one, schedule a
  send_later reminder 20 minutes later, since reminders can arrive late ("Submit <clip> on the <campaign> page
  now: about 10 minutes left in the 30-minute window") and log it in `content/campaigns/tracker.md`.
- **Streamer/creator news** performs best: our voice, graphics and footage; never a streamer's footage (outside
  approved campaigns); only what reliable sources say they said or did.
- **Learning**: `python -m studio.learn` (our numbers + hottest GTA 6 videos; YouTube API key in the environment);
  lessons in `content/learn/lessons.md`. `/stats` logs Studio screenshots into `content/performance.md`.
- **Status**: `python -m studio.status` = one screen (health, YouTube schedule + views, Instagram posted/next,
  campaigns + clip views); use it for "how are we doing?".
- **Health**: `python -m studio.doctor` (free) checks the YouTube connection and its 7-day expiry, missing pinned
  comments (`--fix` posts approved ones), the website and disk. After reconnecting YouTube, write today's date to
  `content/learn/youtube_connected.txt`.
- **Lean runs**: `python -m studio.radar` (free) first in breaking-news runs (QUIET = stop). Don't re-read big files
  or re-render without a reason. End every run that changed anything with `python -m studio.tidy`. New files go where
  the README's table says; finished one-off files go to `content/archive/`.

## System upgrades (Nov 20; details in docs/vice-system.md)
- `python -m studio.vice <audit|discover|scan|publish|...>`: rights gate (default deny, `rights/registry.json`), QC
  (black/frozen frames, loudness, captions vs speech, repost fingerprints, facts), channel/token check, 14-day plan
  (`content/vice-calendar.json`). **Run `studio.vice publish episodes/<slug>.json` before any upload; it must show no
  blockers.** Owner rule: check all facts right before posting.
- New formats/effects (details, ranking, magnifier, callouts, zoom, freeze, shots) are in `content/episode-format.md`.
- Shared Channel Map (all chats): https://docs.google.com/document/d/1t4jj7h1Pnodnys_SAeS7V5xLIVY0Ryls7g23E1mquJs
  edited in place (Google Docs connector). Everygen: 981 top-up credits expire Feb 17; 500 plan credits reset monthly
  (next Dec 12); split What If Arena ~690 / ClipCircuit ~150 / Vice Replay ~150; log every spend there.

## Reference pack
Before writing an episode, read `resources/shorts-tiktok-playbook.md` and `resources/hooks-and-titles.md`.
When no topic is planned, pick an angle from `resources/topic-bank.md` and research it fresh.
The channel rules in this file win over anything in `resources/`.
