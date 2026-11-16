# Vice Replay Studio

This folder is the video machine for the YouTube channel **Vice Replay** (@ViceReplayTV-q8s),
a GTA 6 fan channel. Tagline: "GTA's wildest moments. On replay."
Brand: neon synthwave, hot pink #FF1F8E + cyan #00E5D2 on deep purple/black, Anton headlines.

## How a video gets made
1. **Research** the topic with web search. GTA 6 news moves fast, so search before writing and use only facts
   you found from today or recent days. Keep the source URLs for the `sources` list. If something is a
   rumor or leak, the script must say so ("reportedly", "according to leaks").
2. **Write** `episodes/<slug>.json` following `episodes/gta6-3-days.json`:
   - `segments`: 6-9 segments, 25-45 words each, about 2-4 minutes in total. Each has a short `headline`
     (2-4 words, shown on screen), a `chapter` name, the narration `text`, and an optional `media`
     (a clip or screenshot path in `media/`; leave null for a generated neon background).
   - Segment 1 is the hook: state the payoff in the first 10 seconds. No "hey guys, welcome back".
   - The last segment asks a specific question for the comments, then asks people to subscribe.
   - `short`: 3-5 segments, under 55 seconds of narration total, for the vertical Short.
   - `thumbnail`: `line1` (1-2 words, white), `line2` (2-3 words, pink slab), `tag` (2-4 words).
     Thumbnail text must not repeat the title word for word.
   - Write narration for the ear: short sentences, spell numbers the way they should be spoken
     when it matters ("212 gigabytes"), no emoji, no markdown.
3. **Render**:
   - `python -m studio.make_video episodes/<slug>.json --preview` (fast draft, check it)
   - `python -m studio.make_video episodes/<slug>.json` (final 1080p + thumbnail + description)
   - `python -m studio.make_video episodes/<slug>.json --short` (9:16 Short)
4. **Check**: pull 3-4 frames with ffmpeg and look at them (captions readable, headline not clipped),
   and read `output/<slug>/description.txt`. Then report the output paths and the title options.

Also give the user 3 alternative titles (under 60 characters, the main keyword "GTA 6" first).

## Rules for this channel
- Do not use Rockstar trailer footage or other creators' clips in `media/`. Use the owner's own gameplay
  captures or screenshots, or the generated backgrounds. Re-uploaded trailers get Content ID claims.
- Do not make the channel look official: no Rockstar logos, and the description keeps the
  "not affiliated" line.
- Every video needs a real angle (a guide, a list, an opinion, the owner's gameplay). Don't churn out
  near-identical videos: YouTube demonetizes mass-produced, repetitive content.
- Don't spoil story content in titles or thumbnails.
