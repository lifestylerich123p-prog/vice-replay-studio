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
   - `short`: 3-5 segments, under 55 seconds of narration total: the Short cut from this video. Also set
     `short_title` (under 60 chars, ends with #GTA6 #Shorts) and `short_description` (1-2 sentences).
   - `shorts`: extra standalone Shorts, a list of `{"id", "title", "description", "hashtags", "segments"}`
     (same segment format, 2-4 segments, 20-45 seconds). The daily run adds one news Short here.
   - Shorts get far more views than long videos on this channel. Short segment 1 must hook in the first
     2 seconds (a number, a name, a surprise), and its `headline` doubles as the Short's cover text.
   - `thumbnail`: `line1` (1-2 words, white), `line2` (2-3 words, pink slab), `tag` (2-4 words).
     Thumbnail text must not repeat the title word for word.
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

## Rules for this channel
- Footage library: everything in `media/` is used automatically as segment backgrounds (segments with no
  `media` rotate through it). Allowed there: official Rockstar screenshots, short clips cut from official
  GTA 6 trailers, and the owner's own gameplay. Never other creators' videos, never a whole trailer.
  Clip audio is always dropped (trailer music is what triggers Content ID claims); the narration must
  add real commentary on top. Pick a matching file per segment when the filename makes that possible
  (e.g. `media/beach-sunset.jpg` for a segment about beaches).
- Keep it cheap: the voice is the free Kokoro voice unless the owner says otherwise. Don't add paid APIs.
- Do not make the channel look official: no Rockstar logos, and the description keeps the
  "not affiliated" line.
- Every video needs a real angle (a guide, a list, an opinion, the owner's gameplay). Don't churn out
  near-identical videos: YouTube demonetizes mass-produced, repetitive content.
- Don't spoil story content in titles or thumbnails.
- Streamer/creator news (e.g. what big streamers are planning or doing in GTA 6) performs best on this
  channel. Cover it as news in our own format: our voice, our graphics, our footage library. Never use a
  streamer's stream or video footage, and don't put words in their mouths: only report what reliable
  sources say they said or did.
