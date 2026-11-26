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
as soon as it's ready. Upload early, scheduled. Nov 22 data (21 Shorts since launch, median views/h by ET post time):
6-11 AM 16, 11 AM-2 PM 10, 2-6 PM 2.7, 6 PM-6 AM 1.9: Shorts go in the daytime slots (9:30, 11:00, 12:30); 3:30/8:30 PM
only for big news or long videos (`studio.quota` lists daytime first).
**How many a day** (owner Nov 24: "search online how many videos we should be posting a day and go from there"): no
official YouTube number; 2026 studies say 1-3 Shorts/day (vidIQ, 10.2M channels: growth rises with cadence; Metricool,
~800K videos: monthly Shorts views keep rising with volume, while 35+ Shorts/month drags long-form). Our scorecard's
"Shorts that day" table shows no drop per Short on busy days. So: **3 English Shorts/day** (owner Nov 24 "Do it": **2
map/how-to answers + 1 anchor** a day, Tue GTA 6 vs GTA 5, Wed tier list, Thu quiz; no pure fact Shorts; daily-video.md
rule 8; owner Nov 25 "Start posting the maps videos at least one a day": **every day has at least one map Short**, a
Short with an official-map card; `studio.doctor` warns about any day in the next 7 without one) (9:30, 11:00, 12:30;
weekends 10, 11 or 12:30, 1:30), a 4th only for breaking news; **long videos only for big events** (Game Awards etc.) **and search guides** that tie a Shorts series together
(e.g. episodes/gta6-map-secrets-guide.json: chapters per spot, every map Short's "Related video"; guides keep pulling
search traffic after launch, news recaps don't) until the owner's gameplay arrives
(Nov 24: both recent long videos had 0 views; related/browse traffic is ~0, so long-form isn't being recommended); Spanish channel winners +
max 1 Spanish-only/day; Instagram stays at the owner's cap of 4/day (Mosseri: no magic number). Review Dec 8 (scheduled): if after-launch 3-Short
days get under half the views per Short of 2-Short days and no more total views, go to 2/day.
**Owner Nov 26 "APPROVE ALL"** (details content/owner.md): map/how-to Short titles START with the search phrase
(YouTube autocomplete: "GTA 6 giant crab location + password 🦀"); map Shorts are a numbered series
(`python -m studio.mapseries`: `number` before rendering a new spot, `sync` after uploads keeps the "GTA 6 Map: Where
to Find It" playlist in order, pinned first on the channel home); every map Short also goes to the TikTok files in
Spanish (free Kokoro voice; Viral Adam only for winners while Everygen is low); follow up a taking-off Short the same
day; no new long videos until the ATM and map-secrets guides pull search views.
**Owner Nov 26 "DO IT"** (map cards 46.6 views/h vs versus 4.0, list 0.2): **3 map/how-to Shorts a day**, tier lists and
quizzes stay, no new versus/fact/headline Shorts (parked ones sit in approved_queue.json `paused`); one-tap comment
prompts ("Found it? Reply ✅ — or 😭"; last card "FOUND IT? COMMENT YES"); Spanish YouTube paused until Dec 3
(`spanish_youtube_paused_until`); 8:00 AM slot for each day's first map Short, test week Nov 28-Dec 4 (review Dec 5).

## Rules for this channel
- **Footage**: everything in `media/` is used as backgrounds. Allowed: official Rockstar screenshots
  (`media/official/`, 175 incl. 37 Ultimate Edition shots of cars/shops/style, named by place/character/car, incl. vintage-* and `leonida-map-poster.jpg`, Rockstar's
  official map: use `magnify`/`zoom` for "where is X" Shorts), silent official clips (`media/trailer/launch-trailer-*`,
  `extended-look-*`: real gameplay from Rockstar's "An Extended Look", and `out-now-*`: 3 short clean shots from the
  Nov 19 "Out Now" video; its club/close-up/logo shots are excluded), and the owner's own gameplay (`media/gameplay/`, pulled from the Drive folder in
  `content/owner.md` by `python -m studio.gameplay`, not committed). Never other creators' videos, never a whole
  trailer, clip audio always dropped; narration adds real commentary. Pick `media` per segment by filename and rotate.
  Keep strip-club or sexualized images out (list of excluded shots in owner.md). New official media:
  rockstargames.com/VI/downloads, add only after viewing each. **Exact images first** (owner Nov 24): when a title or
  line names a car, place or character, use THAT official screenshot (`studio.cardphotos.exact`); Rockstar's pack was
  last updated Nov 4, 2026 and is all in media/official; never other people's images. **Map spots** (owner Nov 24): `studio.mappins` pins numbered spots on Rockstar's
  official map by place name or the map's grid ("G7"): `pinned_map` for site pages/thumbnails, carousel `map` pages
  (studio/ig_cards.py), the `map` chart card in Shorts (zoom to a pin); pins live in `site/map-pins.json` (interactive map
  on /guides/gta-6-map-leonida-places/ + /es/guias/mapa-gta-6/; `tools/map_tiles.py`, `tools/map_pictures.py`); only
  labels printed on the map; locations from 2+ guides, disagreements stated.
- **Lettering cards + real pictures** (owner Nov 22-23: "lettering and more modern style", no trailer imaging; Nov 24
  after the views drop, "Approve everything for good of the channel"): Shorts, long videos and Reels are our lettering
  cards (charts, quote, list, tier, versus, quiz) with a strong statement hook, or the owner's gameplay. Since Nov 24
  every card plays on a real GTA 6 picture: an official screenshot from the vetted places/cars pool, exact-name match
  first (`studio/cardphotos.py`, config `card_photos`), slow zoom, darkened under the lettering; map spots use the
  official map (`studio/mappins.py`). Still NOT allowed: trailer CLIPS, bare screenshots without our cards, character
  close-ups, guns, revealing poses (`studio.vice publish` blocks non-card footage segments).
- **Owner gameplay first**: Shorts automatically use the newest gameplay highlights when they exist (`"keep_media":
  true` keeps a segment's own picture; `"use_gameplay": false` turns it off); at 30+ highlights `studio.tidy`
  retires most stock footage (keeps a core for site cards, thumbnails, character news).
- **No official GTA 6 music** (radio, trailer songs, score): Content ID. Game sound only from the owner's gameplay
  recorded with radio/music off. Audio is our generated synthwave theme + SFX (`"music": "none"`, `"sfx": false`).
- **Cheap**: free Kokoro voice (English `af_heart`, grade A, owner Nov 22; set in config/channel.json `voice`); no paid
  APIs unless the owner says so. **Spanish Shorts: Everygen's Viral Adam** (owner Nov 23, ~1 credit per line): when a
  Short is approved, the chat making it generates one line per segment (`generate_voiceover_batch`, voice `viral-adam`, write
  "GTA seis" / numbers as words), saves them to `media/voice/<slug>/es/segN.wav`, sets each segment's `audio_es`,
  re-renders `--short --es` and logs the credits in the Channel Map; Kokoro `em_alex` is only the fallback.
- **Everygen: claim before you spend** (owner Nov 24, after two chats made the same voice twice: "that double
  spending can't happen again, so both chats must work together"): EVERY paid Everygen call (voice, image, video,
  find_clips) starts with `python -m studio.everygen_claim claim <job> --credits N --what "..."` (job e.g.
  `voice:<slug>:es`). It claims the job on GitHub (branch `claude/everygen-ledger`, one winner even if two chats try at
  once) and refuses if the other chat holds it, already did it, or the voice already exists on any branch: then don't
  spend, use theirs. Afterwards `... done <job> --credits N --balance B`; `... list` shows every chat's claims. A hook
  in `.claude/settings.json` blocks paid Everygen calls without a fresh claim (active from each chat's next start).
  Handing a job to another chat = say so in a message and never make it yourself; a redo of a glitched line uses
  `--again "why"`.
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
  the owner to pin comments, set "Related video" on Shorts, add thumbnails B/C (Test & Compare: long videos only, not Shorts). Missing YT_* vars:
  say so and list manual steps.
- **Several chats**: only the main control chat posts (YouTube, Instagram, comments, site); helper chats work on
  their own `claude/...` branch and never post. `git pull --rebase origin main` before every commit. Details and the
  duplicate-post guard (studio/postguard.py): `content/owner.md`.
- **Standing approvals** (details and dates in `content/owner.md`): breaking-news Shorts that pass every rule in
  `.claude/commands/breaking-news.md`; comment auto-replies (`auto-replies.md`, `python -m studio.replies`); any
  time-limited approval written there. Nothing else is posted without asking.
- **Momentum** (`momentum.md`, daily): one follow-up Short with something new when a Short takes off; owner approves
  in the main chat. **Website**: daily guide (+ Spanish) via `site/` + `tools/site_guides.py`, published from the main
  chat (`/publish-site`); scheduled runs can't push, they hand files over with fire_trigger. **Keep the site current** (owner Nov 24: "monitor so this doesn't happen"): a line in `site/live.json` every day, deal prices re-checked every 3 days (`DEALS_CHECKED` in tools/site_guides.py), deal pages carry `expires`; `python -m studio.site_stale` must show 0 stale / 0 old (the site build and `studio.doctor` warn too). **Search traffic**: every Sunday run `python -m studio.search_demand` (Google + Bing autocomplete vs our pages) and turn the top checkable GAPs into guides (2+ sources, no spoilers, no leaks). **YouTube searches that find us**
(`content/learn/search-terms.json`, refreshed by `studio.learn`): any phrase with 50+ views that no Short/guide answers
gets a "where/how" map Short + guide (Nov 24: 'gta 6 shoe store' alone brought ~4,000 views to a clip that never
said where the store is).
- **Instagram** (@vice.replaytv, owner approved Nov 19): every uploaded Short and about one carousel/image a day go
  out through `content/learn/reels_queue.json` (max 4 posts/day; campaign clips paused since Meta's Nov 19 ad flag);
  how: `.claude/commands/instagram.md`.
- **Spanish channel** ("Vice Replay en Español", UCWPnqYqYu9_CLsJ8Bk1MPgQ, connected Nov 22): **winners-only since Nov
  23** (owner "Approve next steps"; `spanish_winners_only` in config/channel.json): a Spanish version of an English Short
  goes up only if the English one did well in its first 24 h (`studio.spend` books it in the next 12:30-1:30 PM Spanish
  slot, or logs it skipped); `studio.youtube_es` refuses the rest unless `--force-es` (owner asks). Spanish-only Shorts
  (`es_only`) are not affected. Before that rule, an owner "approve" for Shorts posted the English AND Spanish versions
  (`studio.ship --upload` runs `studio.youtube_es` too); Spanish titles
  use the Spanish-market style (one CAPS word + one emoji) and `short_pinned_comment_es`; setup steps in `content/owner.md`; channel kit + first uploads in `content/spanish-channel.md`; registry
  `content/learn/uploads-es.json`.
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
  `python -m studio.flops` = 48 h flop review (Shorts under 50 views: main chat sets them private, never deletes).
  `python -m studio.comment_insights` (owner Nov 26 "learn from comments"): themes + questions from the top comments
  on the hottest GTA 6 videos and ours (content/learn/comment-insights-<date>.md; Mon + Thu in the 1 PM checklist).
- **Quota = posting + replies** (owner, Nov 22 night: "every posting credit must be used posting or answering
  comments"): no subtitle files on Shorts (`shorts_subtitles` in config/channel.json), keep reads lean, and every
  night at 2:04 AM ET the main chat runs `python -m studio.spend` (+ `upload`): approved Shorts from
  `content/learn/approved_queue.json` go up early, scheduled for their slots, then every open comment on both
  channels gets an answer (`studio.replies list` / `list --es`). Add each newly approved Short to approved_queue.json.
- **Status**: `python -m studio.status` = one screen (health, YouTube schedule + views, free slots + quota, Instagram
  posted/next, campaigns + clip views); use it for "how are we doing?". `python -m studio.quota`: YouTube units left
  today (learned limit, resets 3 AM ET) and free posting slots for 3 days; fill DAYTIME free slots before extras.
- **Health**: `python -m studio.doctor` (free) checks the YouTube connection (no 7-day expiry since the Google app was
  published Nov 22), missing pinned
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
