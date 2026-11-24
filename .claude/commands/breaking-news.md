---
description: Check for big GTA 6 news and auto-post a Short when it's big and confirmed (owner's standing approval)
---
Breaking-news run for Vice Replay. Nobody is watching live. The owner gave STANDING APPROVAL (see
`content/owner.md`) to publish breaking-news Shorts without asking, ONLY under the rules below. Anything that
doesn't pass every rule is NOT auto-posted.

0. **Free radar first (saves usage)**: before reading anything else, run `python -m studio.radar`.
   - Exit code 1 (QUIET): reply only "Nothing big right now (radar: quiet)." and stop. Don't read other files,
     don't search, don't render.
   - Exit code 0 (BIG) or 2 (UNKNOWN): continue below, starting with the stories the radar printed.
1. **Learn**: `python -m studio.learn` (our uploads + what's hot on YouTube right now). From
   `content/learn/channel.json`, list our uploads from the last 24 hours and count how many have
   `#ViceReplayBreaking` in the title or were described as breaking (check titles; when unsure, count it).
2. **Search** the web for GTA 6 news from the last 6 hours: official Rockstar/Take-Two news, launch problems
   (servers, downloads, patches, delays), review scores, sales/player/viewer records, big streamer moments,
   viral moments. Read the actual articles.
3. **Score the best story 0-10** and write the score with one line per point:
   - +3 official or confirmed by 2+ reputable outlets (IGN, GameSpot, Kotaku, Polygon, Forbes, The Verge,
     Eurogamer, Bloomberg, Rockstar Newswire/Support, the streamer's own post); rumors/leaks/single source = stop
   - +2 published in the last 3 hours (+1 if 3-6 hours)
   - +2 huge reach (affects every player, or a top streamer, or a record number)
   - +2 people are searching it now (it, or its topic, shows in today's `market-*.md`, or many outlets cover it)
   - +1 it has a clear number, quote or verdict we can put on a lettering card (or a gameplay highlight)
4. **Auto-post ONLY if all are true**: score >= 8; confirmed by 2+ reputable sources; no story spoilers; not a
   topic we already posted (check the CHANNEL's last 72 h of uploads, not only the registry: a run that can't push
   leaves uploads.json stale, and on Nov 23 two runs posted "39 million PS5 players" twice in 3 hours; the uploader
   now blocks the same story automatically, never pass `--force` to get around it); fewer than 2 breaking auto-posts
   in the last 24 hours; and it isn't about a real person's private life, a tragedy, or anything legal/medical.
   Otherwise: if score >= 6, make the Short anyway and deliver it for approval like daily-video.md step 3
   (no upload); if lower, send a 2-line "nothing big" note and stop.
5. **Make the Short** following CLAUDE.md: episode JSON with `title`, `slug`, `short_title` (end with
   `#GTA6 #Shorts`), `short_description` (facts + sources, end with `#ViceReplayBreaking`), `pinned_comment`,
   `sources`, `short_es` {title, description} and `text_es` on each segment (Spanish), `short` (3-4 segments, 20-40 s, hook in the first 2 seconds, only confirmed facts, say "reportedly"
   for anything not official). Render with `python -m studio.ship episodes/<slug>.json` and read `output/<slug>/check.jpg` once.
6. **Publish**: between 6 AM and 6 PM ET, publish now: `python -m studio.youtube_upload episodes/<slug>.json --approve
   short --now` (public immediately, not made for kids, comment posted). **After 6 PM ET** (Nov 24 data: Shorts posted
   6 PM-6 AM get ~1.9 views/h vs 16 for 6-11 AM), schedule it for **9:30 AM ET the next morning** instead (same
   command without `--now`, plus `--date <tomorrow> --at "9:30 AM"`), unless it's a 10/10 story everyone will cover
   tonight. Either way, add it to `content/learn/uploads.json` in your final message (the main chat registers it if
   you can't push).
7. **Tell the owner** (PushNotification if available, and a short final message): "Auto-posted breaking Short:
   <title> <link>. Score <n>/10 because <one line>. Sources: <links>. Pin the comment; delete it in YouTube
   Studio if you don't want it." Also send the video with SendUserFile so they can repost it on TikTok/Instagram.
8. If anything fails (render, upload), don't retry endlessly: report what happened.

**QC gate (Nov 20):** after rendering and before uploading, run `python -m studio.vice publish episodes/<slug>.json`;
upload only if it reports no blockers (rights, facts, black frames, captions vs speech, channel/token check). If push
to main is refused, also send the episode JSON + the log line to the main chat (fire_trigger trig_01XX9xXTp8xfb4i3yYUFP9uF)
so the repo log stays complete.

**Nov 22-23 (owner): original first, no trailer images.** Build the Short from GTA 6-style lettering cards
(`studio/vicecards.py`): a kinetic hook card, a `headline` card (kicker CONFIRMED / REPORTEDLY), a `meter`/`versus`/`bars`
card with the key checked number and a `src`, then a kinetic verdict/question. No trailer clips or official screenshots at
all (`studio.vice publish` blocks them). Voice: the channel voice in config/channel.json (af_heart). Rules in
content/episode-format.md (headlines of 19 characters or less, prices spoken in dollars and cents).
