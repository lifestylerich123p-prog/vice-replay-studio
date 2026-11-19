# Episode format (read before writing an episode JSON)

Moved out of CLAUDE.md so runs that don't write episodes don't load it. Every rule here still applies.

**Write** `episodes/<slug>.json` following `episodes/gta6-3-days.json`:
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
