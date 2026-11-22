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
   - +1 we have a strong visual for it (official screenshot or gameplay highlight)
4. **Auto-post ONLY if all are true**: score >= 8; confirmed by 2+ reputable sources; no story spoilers; not a
   topic we already posted (check our uploads' titles and `content/log.md`); fewer than 2 breaking auto-posts
   in the last 24 hours; and it isn't about a real person's private life, a tragedy, or anything legal/medical.
   Otherwise: if score >= 6, make the Short anyway and deliver it for approval like daily-video.md step 3
   (no upload); if lower, send a 2-line "nothing big" note and stop.
5. **Make the Short** following CLAUDE.md: episode JSON with `title`, `slug`, `short_title` (end with
   `#GTA6 #Shorts`), `short_description` (facts + sources, end with `#ViceReplayBreaking`), `pinned_comment`,
   `sources`, `short_es` {title, description} and `text_es` on each segment (Spanish), `short` (3-4 segments, 20-40 s, hook in the first 2 seconds, only confirmed facts, say "reportedly"
   for anything not official). Render with `python -m studio.ship episodes/<slug>.json` and read `output/<slug>/check.jpg` once.
6. **Publish now**: `python -m studio.youtube_upload episodes/<slug>.json --approve short --now`. It goes public
   immediately, not made for kids, with the comment posted.
7. **Tell the owner** (PushNotification if available, and a short final message): "Auto-posted breaking Short:
   <title> <link>. Score <n>/10 because <one line>. Sources: <links>. Pin the comment; delete it in YouTube
   Studio if you don't want it." Also send the video with SendUserFile so they can repost it on TikTok/Instagram.
8. If anything fails (render, upload), don't retry endlessly: report what happened.

**QC gate (Nov 20):** after rendering and before uploading, run `python -m studio.vice publish episodes/<slug>.json`;
upload only if it reports no blockers (rights, facts, black frames, captions vs speech, channel/token check). If push
to main is refused, also send the episode JSON + the log line to the main chat (fire_trigger trig_01XX9xXTp8xfb4i3yYUFP9uF)
so the repo log stays complete.

**Nov 22 (owner): original first.** Even breaking news needs at least one `chart` segment with the key checked number
(e.g. a `counter` of the record, a `bars` leaderboard) — `studio.vice publish` blocks trailer-only narration. Voice: the
channel voice in config/channel.json (af_heart). Trailer clips only as 1-2 s cutaways.
