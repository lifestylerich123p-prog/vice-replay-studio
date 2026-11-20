# Lessons learned (the machine's memory of what works)

Every run adds dated lessons here from real numbers (our channel + what's winning on YouTube). Keep each lesson
short, specific and backed by a number. Remove lessons that later data proves wrong.

- 2026-11-16: Streamer news Short ("Lacy's INSANE GTA 6 Marathon Plan") got ~4,000 views vs 8-158 for every
  other upload. Streamer/creator news is our best format.
- 2026-11-16: Long videos get very few views on a new channel; Shorts drive discovery.
- 2026-11-17: Our two new-system Shorts (24-hour stream: 180 views, 3-days: 91 views) run at ~50 views/hour in
  their first hours vs 0.5-2.7 views/hour for the older non-streamer Shorts. Real screenshots + word captions +
  streamer/launch news is working; keep this format.
- 2026-11-17: Market (top GTA 6 videos, last 48h) is almost all Shorts. Winners are relatable launch moments
  ("Deciding which game to delete for GTA 6", 171K views/hour), streamer marathon content (Kai Cenat marathon,
  160K/h) and performance debates ("30 FPS on PS5", 96K/h). Angles to use: storage/deleting games, 30 vs 60 FPS,
  big streamers' marathons, relatable "every GTA fan right now" moments.
- 2026-11-17 (first private analytics, last 28 days): 97% of our views come from the Shorts feed (SHORTS 1,648 vs
  YouTube search 55, related videos 10). Shorts are how we grow; long videos are a bonus.
- 2026-11-17: Lacy Short is watched 87.9% on average (16 s): a strong hook + streamer name keeps people. The
  "Chaos Is Coming" teaser loses people fast (43.9%, 4 s): vague teasers don't work, specific news does.
- 2026-11-17: Long videos are watched only ~25% (31-60 s of 2-4 min): the first 30 seconds must deliver the
  payoff, and long videos should stay near 2 minutes until retention improves.
- 2026-11-17 (evening): The market's top Shorts are short relatable launch moments ("Xbox gamers can play GTA 6 early",
  47K views/h; "Deciding which game to delete", 141K/h). The New Zealand early-play trick is a proven hungry angle; we cover
  it with risks/PS5-vs-Xbox so it is not a copy of the unlock-time video.
- 2026-11-17: Gameplay pull failed (proxy 403 on the Drive download host); today's run used official screenshots.
- 2026-11-19: Launch-night breaking Shorts are our best ever per hour: cheats "real... but there's a catch" 125.6 views/h,
  Metacritic 99 124.1/h, "7 MILLION watched" 115.2/h, "is OUT: do these 3 things" 98.2/h, NZ "(the catch)" 90.1/h.
  All five lead with a hard number or a "catch"; keep that hook style. Shorts feed still brings ~92% of views (5,245 of ~5,576).
- 2026-11-19: Market (last 48h): "ps5"/"pro" are among the top title words and the 30 FPS debate fills our own comments
  (3 of the latest 8 mention 30fps). Players now want "what am I actually getting" performance/settings answers, plus
  relatable POV launch moments and first-time gameplay (which we can't make until owner gameplay arrives).
- 2026-11-19: Campaign clips: a Lacy moment many clippers already posted (the shark) got 1 view on YouTube with no claim (duplicate-content suppression), while less-posted moments (shoe store 4K+, alligator 1.6K) took off. Pick fresh moments (Twitch clips Top · Last 24 h) over the most-reposted ones.
- 2026-11-19: 307 Lacy GTA 6 Shorts (Nov 18-19): the top 20% by views/hour have a median length of 14 s (rest 24 s) and get ~1,350 views/h vs ~190. Winners are short "firsts" with a simple title, name first: "Lacy Arrested on Day 1 in GTA 6!! 💀", "Lacy meets a dog in GTA VI 🥹", "Lacy's first crash out in GTA 6". ALL-CAPS titles, #core tags and credit lines made no difference. Our best (shoe store, 15 s) fits this. Keep campaign clips 8-16 s, post fast after the moment, avoid moments 5+ accounts already posted.
- 2026-11-19: After 3 Lacy clips took off on Vice Replay (5.2K/1.7K/1K), the next 3 posted the same day got 1-3 views each (no claims): likely YouTube repetitive-content limiting from 6 near-identical streamer clips in one day. Campaign clips belong on a separate clips channel, not the main channel.
- 2026-11-19: Instagram: a day-one account posting 11 times through the API got its ADS restricted by Meta (posting
  still fine). New accounts go slow: max 4 posts a day (`studio.instagram_upload` enforces it), ~2.5 h apart.
- 2026-11-19: Give every Short its own pinned comment that matches what the Short says (the 6 PM "Can't get into
  GTA 6?" Short reused the episode's 30 FPS question, which didn't fit).
- 2026-11-19: Text/codes on AI images: AI garbles letters and arrows, so generate the background with NO text
  (Everygen Nano Banana 2, 2 credits, 4:5) and draw the exact text ourselves (cheat-sheet post). DejaVu Sans Bold
  draws even ←↑→↓; Anton/Montserrat arrows are uneven.
- 2026-11-19: Black Friday: Amazon's Black Friday Week runs Nov 19-30. GTA 6 and its controller aren't discounted;
  the regular DualSense ($54) is the deal that sends clicks. Lead with "the catch", link the live deals page.
- 2026-11-19 (night): Clipping math. Lacy is a POOL ($12,500 split by approved views; 750K-1M approved views needed
  to share). Our 7 Lacy clips have ~10K views total, while 226 Lacy Shorts went up in 9 hours on Day 2 and 67
  clippers had 18.9M views by Nov 18 (Reach). Pools are a long shot for a small channel; per-view campaigns
  (KreekCraft $1/1K, $3 min; Tomo $1.50/1K) pay from the first few thousand views. Vendor data: clippers average
  ~$0.39 per 1K views after fees. Use `studio.moments` before every clip; skip TAKEN moments.
- 2026-11-19 (night): First scorecard (studio.scorecard): campaign clips median 41.8 v/h vs 5.6 for our own Shorts;
  16-30 s Shorts win, 60+ s Shorts are dead (0.2 v/h); morning posts beat afternoon (launch-week data, so re-check
  as the 24 h numbers fill in). Instagram: accounts whose posts are mostly reposts lose recommendations.
- 2026-11-20: Scorecard: "catch" hooks are our best own-Short hook so far (median 39.1 v/h and 1,236 first-24 h views,
  n=2) against 4.8 v/h for number and statement hooks. Morning posts (before noon ET) have a median of 44.6 v/h against
  1.0 for 12-5 PM (n=16), so the afternoon main/tips slots are our weakest. Shorts of 16-30 s have a median of 25.1 v/h
  against 4.9 for 31-60 s. Keep Shorts under 30 s with a catch or hard-number hook.
- 2026-11-20: Retention: Shorts that open with a number are watched 58.1% on average against 52.2% without one (6 vs 3 Shorts).
- 2026-11-20: Market (last 48 h): winners moved from launch news to in-game discoveries and "do this first" help:
  a rescue-dog Short (335K views/h, 21 s), "What happens if you reach the N" (115K/h), "Stealing a jet" (148K/h),
  "Five things you NEED to do first" (32K/h, main). Discoveries plus beginner tips are the hungry angles now. Without
  owner gameplay we cover them with our own research and official screenshots, never other creators' clips.
- 2026-11-20: Official gameplay clips (extended-look-*) make Shorts look like real gameplay. Review every new clip at
  full size: a 'city drive' thumbnail hid a drive-by with guns (removed). Never show a storefront while naming a different shop.
- 2026-11-20 (market + research): Top 432 GTA 6 Shorts of 72 h: 127 came from channels under 20K subs with 500K-10M
  views, so size isn't the limit; format is. Typical views by format: GTA 5 vs GTA 6 comparison ~940K, streamer
  moments ~760K, real gameplay ~520K, memes/POV ~400K, news/facts ~290K (our main format). Duval Desk (started Nov 16,
  faceless, 5-6 Shorts/day): baseline 1-12K, breakout 606K with "7 Things GTA 6 Lets You Do That GTA 5 Never Did".
  Winning titles create curiosity ("...Will Shock You", "Still Think It's Small?"), not headlines.
- 2026-11-20 (YouTube policy): Oct 1, 2026 "Prioritizing original content on Shorts" cuts reach for reused footage
  with narration that only describes it; July 2026 "generic or repetitive" (same template across uploads) loses
  monetization; frequency is not a ranking factor (YouTube). Official trailer/Extended Look footage has been seen by
  31M+ (weak swipe-stop). Fixes: owner gameplay first, narration that adds facts/opinion, fewer and more varied
  Shorts, and keep reposted streamer clips a small share of the main channel (aggregator risk). vidIQ: 300-1,300
  views is normal for a channel's first weeks; the best of a new channel's first 10 Shorts has a median of ~1.9K.
