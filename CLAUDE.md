# Vice Replay Studio

This folder is the video machine for the YouTube channel **Vice Replay** (@ViceReplayTV-q8s),
a GTA 6 fan channel. Tagline: "GTA's wildest moments. On replay."
Brand: neon synthwave, hot pink #FF1F8E + cyan #00E5D2 on deep purple/black, Anton headlines.

## How a video gets made
1. **Research** the topic with web search. Check `content/learn/lessons.md`, `content/performance.md` and the
   latest `content/learn/market-*.md` first, and lean toward what the numbers say works. GTA 6 news moves fast, so search before writing and use only facts
   you found from today or recent days. Keep the source URLs for the `sources` list. If something is a
   rumor or leak, the script must say so ("reportedly", "according to leaks").
2. **Write** `episodes/<slug>.json` following `episodes/gta6-3-days.json`:
   - `segments`: 6-9 segments, 25-45 words each, about 2-4 minutes in total. Each has a short `headline`
     (2-4 words, shown on screen), a `chapter` name, the narration `text`, and an optional `media`
     (a clip or screenshot path in `media/`; leave null for a generated neon background).
   - Segment 1 is the hook: state the payoff in the first 10 seconds. No "hey guys, welcome back".
   - The last segment asks a specific question for the comments, then asks people to subscribe.
   - `short`: 3-5 segments, under 55 seconds of narration total: the Short cut from this video. Also set
     `short_title` (under 60 chars, ends with #GTA6 #Shorts) and `short_description` (1-2 sentences).
   - `shorts`: extra standalone Shorts, a list of `{"id", "title", "description", "hashtags", "segments"}`
     (same segment format, 2-4 segments, 20-45 seconds). The daily run adds one news Short here.
   - Shorts get far more views than long videos on this channel. Short segment 1 must hook in the first
     2 seconds (a number, a name, a surprise), and its `headline` doubles as the Short's cover text.
   - `thumbnail`: `line1` (1-2 words, white), `line2` (2-3 words, pink slab), `tag` (2-4 words), `image`
     (the best screenshot for it). The render makes thumbnail-a/b/c.jpg with different pictures for
     YouTube Studio's Test & Compare (up to 3 thumbnails per video).
     Thumbnail text must not repeat the title word for word.
   - Every Short's last segment automatically shows a "FOLLOW FOR DAILY GTA 6" badge (Spanish: "SÍGUENOS: GTA 6 A
     DIARIO"); subscribers are the channel's bottleneck for monetization. Set `"follow_cta": false` to turn it off.
   - Make Shorts loop: the last line should flow back into the first (e.g. ends "...and that's why" while
     the hook starts with the reason), so replays count as extra watch time.
   - `pinned_comment`: one question for the comments that's easy to answer (pick-one or a number), posted and
     pinned by the owner right after upload.
   - Spanish (free extra audience): every segment (main and Shorts) also gets `text_es` (natural Latin American
     Spanish, same meaning, similar length; keep names like GTA 6, Vice City, Kai Cenat as they are). Add `es`
     {`title`, `description`} for the main video, `short_es` for the main Short, and `es` inside each `shorts`
     item. The uploader adds them as YouTube's Spanish title/description and Spanish subtitles.
   - Affiliate links (Amazon, `content/affiliate.json`) are added to the main video's description automatically with
     the required disclosure. Set `affiliate` to pick sets: ["storage","game"] (default; downloads, launch, news),
     ["storage","gear"] (guides, tips, gameplay), or [] for none (e.g. sensitive news). Never claim we used or
     reviewed a product, and never put affiliate links in a way that hides the disclosure.
   - The gear page is https://vicereplay.com/gear/ (repo vicereplay-site). Mention "vicereplay.com/gear" in Short
     descriptions and pinned comments when the topic is storage or gear.
   - Links in Shorts descriptions aren't clickable, so Shorts send people to the long video: end the main Short's
     `short_description` with "Full video on the channel ⬇️" and remind the owner to set "Related video". The long
     video carries the affiliate links (description + pinned comment, added automatically).
   - On download/storage/gear/launch topics, the long video's last or second-to-last segment may add ONE natural line
     like "If you're short on space, I put storage links in the description." Never more than once, never pushy.
   - Playlists are automatic (main -> "GTA 6 News & Guides", Short -> "GTA 6 Shorts", news Short -> "GTA 6
     Streamer & Breaking News"); set `playlist` on an item only to override.
   - Write narration for the ear: short sentences, spell numbers the way they should be spoken
     when it matters ("212 gigabytes"), no emoji, no markdown.
3. **Render**:
   - `python -m studio.make_video episodes/<slug>.json --preview` (fast draft, check it)
   - `python -m studio.make_video episodes/<slug>.json` (final 1080p + thumbnail + description)
   - `python -m studio.make_video episodes/<slug>.json --short` (all 9:16 Shorts; each gets a .txt with
     its title, description and hashtags)
4. **Check**: pull 3-4 frames with ffmpeg and look at them (captions readable, headline not clipped),
   and read `output/<slug>/description.txt`. Then report the output paths and the title options.

Also give the user 3 alternative titles (under 60 characters, the main keyword "GTA 6" first).

## Posting schedule (US Eastern time; starting point, adjust from YouTube Studio analytics)
- Weekdays: main video 3-4 PM, Short cut from it 6 PM, news Short 8-9 PM.
- Saturday: main video 1-2 PM, Shorts 4 PM and 8 PM. Sunday: like weekdays, 1 hour earlier.
- Big news breaks: post the Short as soon as it's ready; freshness beats the schedule.
- Upload everything in the morning and use YouTube Studio's Schedule option, so posting happens on time.

## Rules for this channel
- Footage library: everything in `media/` is used automatically as segment backgrounds (segments with no
  `media` rotate through it). Allowed there: official Rockstar screenshots, short clips cut from official
  GTA 6 trailers, and the owner's own gameplay. Never other creators' videos, never a whole trailer.
  Clip audio is always dropped (trailer music is what triggers Content ID claims); the narration must
  add real commentary on top. Pick a matching file per segment when the filename makes that possible
  (e.g. `media/beach-sunset.jpg` for a segment about beaches). `media/official/` holds 137 official Rockstar
  screenshots named by place, character or car (vice-city-*, leonida-keys-*, grassrivers-*, port-gellhorn-*,
  mount-kalaga-*, ambrosia-*, jason-duval-*, lucia-caminos-*, jason-and-lucia-*, car-*, vintage-* (Vintage Vice City
  pack), and supporting characters: cal-hampton-*, boobie-ike-*, drequan-priest-*, real-dimez-*, raul-bautista-*,
  brian-heder-*). `media/trailer/` holds 11 silent 2-6 s clips from the official Launch Trailer (launch-trailer-*:
  motorbike, beach-plane, heist-explosion, helicopter-city, marina-aerial, ...) for moving backgrounds. Source for
  new official media: rockstargames.com/VI/downloads (screenshot and video packs); add new ones after viewing each. Set `media` per segment to the best match; rotate so one video doesn't repeat a shot.
  Keep strip-club or sexualized images out of the library (they get videos age-restricted/limited ads).
- Owner gameplay comes from the Google Drive folder in `content/owner.md`: `python -m studio.gameplay` downloads
  new recordings and cuts highlights into `media/gameplay/` (not committed; pulled fresh each run).
- No official GTA 6 music: the radio stations, trailer songs and the Justice score are licensed music that
  Content ID claims. Don't download or use them. Game sound (engines, city ambience, gunfire) is fine
  only from the owner's own gameplay recorded with the in-game radio and music turned off.
- Audio is automatic: an original synthwave theme (`studio/sound.py`, generated, no licensing) ducks under the
  voice, with a whoosh on every cut and an impact on the hook. Captions highlight each word as it's spoken.
  Set `"music": "none"` or `"sfx": false` in an episode to turn them off.
- Keep it cheap: the voice is the free Kokoro voice unless the owner says otherwise. Don't add paid APIs.
- Do not make the channel look official: no Rockstar logos, and the description keeps the
  "not affiliated" line.
- Every video needs a real angle (a guide, a list, an opinion, the owner's gameplay). Don't churn out
  near-identical videos: YouTube demonetizes mass-produced, repetitive content.
- Don't spoil story content in titles or thumbnails.
- Auto-posting to YouTube (after approval only): when the owner replies in a delivery session with an approval
  ("approve", "approve all", "approve the Shorts", "approve, use title 2", ...), run
  `python -m studio.youtube_upload episodes/<slug>.json --approve <all|main,short,news,replies> [--title N]` ("all" also posts the approved comment replies). It uploads and
  schedules each approved upload for its posting time. Never upload without an explicit approval message from the
  owner in chat, never upload campaign clips (the owner posts those), and apply any changes the owner asks for
  (titles, which items) before uploading. Scheduled videos are private until their time and YouTube refuses
  comments on private videos, so the uploader prints a "COMMENTS TO POST AFTER <time>" command: right after
  uploading, schedule it with send_later for 10 minutes after that time, with the message "Post today's pinned
  comments now: <the command>", and run the command when it arrives. Report each video link and its scheduled
  time, and remind the owner to pin the comments (after they're posted), set "Related video" on the Shorts and add
  thumbnails B and C in Test & Compare.
  If the YT_* variables are missing, say so and list the manual upload steps instead.
- Exception, breaking news: the owner gave standing approval (`content/owner.md`) to auto-publish breaking-news
  Shorts that pass every rule in `.claude/commands/breaking-news.md`. Only those; nothing else is auto-posted.
- Campaigns need the owner's approval first: only clip campaigns whose file has `owner_approved: true`, which
  is set only when the owner approves that campaign in chat. Each campaign clip must be submitted on the
  campaign page within 30 minutes of being posted; every delivery says so.
- Campaign 30-minute reminder: when the owner says they posted a campaign clip (e.g. "posted lacy clip 2"),
  immediately schedule a reminder with send_later for 25 minutes later: "Submit <clip> on the <campaign> page
  now: 5 minutes left in the 30-minute window", and log the posted time in `content/campaigns/tracker.md`.
  When the reminder fires, send it as a push notification if that tool is available.
- Learning loop: `python -m studio.learn` pulls our channel's live numbers and the hottest GTA 6 videos on
  YouTube (free YouTube Data API; key in the environment's settings as the `YOUTUBE_API_KEY` variable or a
  network secret for www.googleapis.com). Lessons live in `content/learn/lessons.md`; every run adds to them.
- Stay organized (free, no AI): start every run by reading `content/INDEX.md` (map of where everything is, every
  episode, YouTube id and website guide) instead of searching the repo, and end every run that made or changed
  anything with `python -m studio.tidy` (deletes old renders and caches, archives old reports, rebuilds the index).
  New files go in the folder the README's table says; finished one-off files go to `content/archive/`.
- Saving usage: `python -m studio.radar` (free, no AI) checks Google News; breaking-news runs stop right away when
  it says QUIET. Keep runs lean: don't re-read big files or re-run renders without a reason.
- Helpers: `/stats` logs YouTube Studio screenshots into `content/performance.md` (the daily run favors what
  works there); `/reply-comments` writes comment replies; `/campaign-clips` makes campaign clips.
- Paid clipping campaigns (Whop Content Rewards etc.): the one exception where a streamer's own footage and
  voice may be used, because the campaign grants permission. Only GTA 6 campaigns, only footage from where
  the campaign says, and follow every rule in `content/campaigns/<name>.json` exactly (length, credit,
  hashtags, platforms). Tools: `studio/clip.py` (free) or Everygen (the owner's paid editor, ClipCircuit method; spend
  credits only after a cost estimate and the owner's yes); command: `/campaign-clips`. No Vice Replay music on these:
  keep the original audio. Keep campaign clips to `max_clips_per_day` so the channel stays Vice Replay.
- Streamer/creator news (e.g. what big streamers are planning or doing in GTA 6) performs best on this
  channel. Cover it as news in our own format: our voice, our graphics, our footage library. Never use a
  streamer's stream or video footage, and don't put words in their mouths: only report what reliable
  sources say they said or did.
