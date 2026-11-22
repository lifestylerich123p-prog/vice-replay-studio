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
- 2026-11-20 (growth research): Links in Shorts aren't clickable: Amazon buyers come through the bio link, the
  website and long videos set as a Short's "Related video". Amazon pays ~1-2% on games but flat bounties for Prime
  trials (tag them). OneLink covers CA/UK/ES/DE/FR/IT (not Mexico). TikTok Creator Rewards needs 1-min+ videos.
  YPP for new channels doubles on Feb 1, 2027; the expanded tier (500 subs + 3M Shorts views/90 days) is the
  near-term target. FAQ rich results stopped May 2026: use Article/Breadcrumb schema; Discover wants 1200px images
  and max-image-preview:large (added). Facebook Page Reels API: 30/day, needs a Page + pages_manage_posts.
- 2026-11-20: First test of moving gameplay backgrounds: the IShowSpeed Short (official gameplay clips, streamer
  angle) got 167 views in its first 1.3 h (~129/h), while tips Shorts on still screenshots got 3-16 views in ~17 h
  (cheat codes 50 s, "Can't get into GTA 6?", "First 3 settings"). Every Short now uses moving clips, never stills
  as the first frame; today's 12:30 / 6 PM / 8:30 PM Shorts were re-made and swapped (old versions left private).
- 2026-11-20 (audit with real YouTube Analytics, `python -m studio.vice audit`): Shorts are ~97% of views. Campaign
  streamer clips have the best median (1,009 views, 50% stayed to watch) but repeats of a crowded moment got 2-8 views;
  own news Shorts median 572 (818 in 24 h, 43% stayed); tips 248; long videos ~15. Best own Shorts today: streamer news
  (IShowSpeed, ~137 views/h) and "the catch" money hook (~68/h).
- 2026-11-20 (competitors, `studio.vice discover`, 11 channels): "ranking" titles are a confirmed trend (7 channels,
  breakouts 0.7-3.8M); "versus/tested" titles: 0 of 11 channels (an open lane to test, not proven). Videos weren't
  watched (youtube.com is blocked here), so no claims about their editing.
- 2026-11-20 (footage): read signs/HUD at full resolution (a thumbnail read "5/9", the frame said "5/6"); official clips
  have internal cuts and UI moments (blurred weapon wheel at the start of the strip-mall clip): heed the renderer's
  "crosses a shot change" warning. A sourced real-life match ("GameStop closed 1,300+ US stores in two years") makes a
  detail Short stronger.
- 2026-11-20 (system): webcam detection works on real streams by finding the still region around a face (IoU 0.97);
  the repost check needs full-frame AND moving-pixel matches (a streamer's identical webcam room fooled the first
  version); clip loudness uses two-pass loudnorm (one pass left -17.6 LUFS). Everygen downloads are free (YouTube parts
  ~20 s max per call). Instagram insights aren't readable with the current token (needs the insights permission).
- 2026-11-21 (scorecard, 46 Shorts): slot matters more than we thought: Shorts posted before noon ET have a median
  22.8 views/h (n=11) vs 0.7 for 12-5 PM (n=18) and 4.5 for 5-9 PM (n=14). Length too: 16-30 s median 15.2 v/h
  (n=22) vs 60+ s 0.1 (n=8). The "catch" hook gets the most views/h (23.3, n=3) but the lowest % watched (33%);
  "number" hooks keep people best (61.5% watched, n=16). Today's Shorts use a number hook, 20-30 s. Suggest the
  owner test a morning slot for the next streamer Short instead of 6 PM.
- 2026-11-21 (market, 48 h): 7 of the top 10 GTA 6 videos are non-English Shorts (comedy skits, "POV", reactions);
  the English winners are question/curiosity titles ("5 Things You Didn't Know", "How Long Can You Survive 6 Stars",
  "Why Everyone Keeps JUMPING") and ending/spoiler long videos (off-limits for us). Streamer finishes (IShowSpeed
  52 h) are the story of the day in news; no top-50 video covers finish times as a search answer yet.
- 2026-11-21 (main chat, post-launch breakdown of our 33 own Shorts): before launch, news Shorts often hit ~1,000
  views; since Nov 19 noon only streamer stories (IShowSpeed family name 1,179, posted 9:28 AM) and number/catch hooks
  on money or hardware (PS5 vs Pro 1,199; Chapter 1 money 496; $3.79B 185) work. Tips/search-answer Shorts died
  (5-60 views): players have the game now and our trailer footage is old to them. Action: main Short moved to 9:30 AM
  (weekends 10 AM), tutorials go to the website, max 3 own Shorts/day, rotate footage (new: out-now-* clips + the
  official Leonida map poster). The real unlock is owner gameplay (needs a console; GTA 6 cloud play is Xbox-console
  only, no phone/PC browser: Windows Central, GamingBolt).
- 2026-11-21 (fact check): never trust one search summary for a number in a script. Eurogamer 65 h, IGN 115 h, Pure
  Xbox 42 h could not be confirmed and were cut; IShowSpeed's crash hour is reported as 40-43, so "around hour 43";
  quotes from streams are "reportedly". Most coverage of IShowSpeed's reaction to the ending spoils it: use times only.
- 2026-11-21 (early slot check, 1:40 PM ET): IShowSpeed 52 h Short (9:30 AM) 208 views in ~4 h (~50 v/h); Black
  Friday catch Short (11 AM) 69 in ~2.7 h; first GTA 5 vs 6 comparison (1:30 PM) 0 at 10 min. Re-check at 24 h
  (scorecard "24 h views") before moving more slots; so far the morning slot is beating the last two days' afternoons.
- 2026-11-21 (voice test): Pocket TTS vs current Kokoro (am_michael), same 3 lines from a Short: Pocket runs 1-3 s longer per line and ~2-3 dB quieter. Kept Kokoro. Pocket's weights are gated on Hugging Face (license not confirmed) and Spanish is untested. Re-test only if the license is confirmed and a need comes up.
- 2026-11-21 (evening, our post-launch Shorts): opening on a moving clip = median 92 views (8 Shorts) vs 18 for a still
  (4). Winners: streamer stories + number verdicts (IShowSpeed family name 1,188; PS5 vs Pro 1,200; money catch 559).
  Dead: plain tips (settings 5, cheat list 8, won't connect 27, dog 32), mostly 79-117 words; anything after 7 PM
  (0-30); every long video (0-25). Real gameplay is the step change: the Lacy campaign clips on this channel on Nov 19
  got 9,393 / 1,863 / 1,011. `studio.vice publish` now enforces a moving first frame and warns on tips/long scripts
  (studio/vice/viewcheck.py).
- 2026-11-22 (YouTube Analytics Nov 13-20, lag 1-2 days): real-gameplay Lacy clips held 86-92% average viewed
  (13-17 s watched); our narrated ~30 s Shorts average ~57% (44-75%), i.e. half the viewers leave. Channel-wide on
  Shorts with 50+ views: 1.4 likes per 100 views, 0.6 subs per 1,000 views, engaged views = 44% of views (most
  viewers swipe in the first seconds). Short real moments get finished; narrated explainers don't.
- 2026-11-22 (web investigation, see content/learn/growth-plan-2026-11-22.md): YouTube's Oct 2026 Shorts originality
  update de-ranks voice-overs that only describe the footage; short (13-20 s) real moments win; never delete flops;
  owner gameplay is the biggest lever. Rules now in the daily run and the views check.

- 2026-11-22 (daily run, channel.json): same topic, different slot: "$1.65 BILLION" (posted 6:56 AM ET) 19.6 v/h vs
  "$3.79 BILLION" (5:30 PM) 5.6 v/h, ~3.5x. Nov 21's Shorts in slot order: IShowSpeed 52 h (9:30 AM, streamer +
  number) 12.9 v/h, Black Friday catch (11 AM) 8.2, first GTA 5 vs 6 comparison (1:30 PM) 5.1. Morning streamer +
  number keeps winning; the comparison format (DO MORE, n=3) has only been tested in the afternoon so far.
- 2026-11-22 (market, 48 h): the top English Short is a money comparison ("$1 v $1,000,000 Car In GTA 6", MrBeast
  Gaming, ~290K v/h); streamer-pair Shorts are next but built on the ending (off-limits). 7 of the top 10 are
  non-English skits/POV. Today: a money comparison with a catch + a streamer ranking built on numbers we checked
  ourselves (YouTube Data API view counts of finished GTA 6 streams: original data, no streamer footage).
- 2026-11-22 (status): the three newest Lacy campaign clips on this channel got 2-8 views vs 1,011-9,439 for the first
  three (Nov 19). Campaign clips aren't automatic wins once a moment is crowded; the owner's Nov 20 rule already
  moves them to ClipCircuit.
- 2026-11-22 (main chat, pre-upload fact check): a YouTube search for "GTA 6" missed CarryMinati's "GTA VI" stream
  (18.1M), so the draft named Mythpat (17.9M) as the biggest non-Speed stream. For any "most-viewed" ranking, search
  "GTA 6", "GTA VI" and "Grand Theft Auto VI" and merge before naming a #1.
- 2026-11-22 (main chat, market scan 48 h, YouTube API): top GTA 6 Shorts are skits (can't do: real actors), streamer
  endings (spoilers) and gameplay stunts (need owner gameplay). The format we CAN do: the fast "every look" montage
  (DjMaRiiO "LOS OUTFITS DE LUCIA EN GTA VI" 4.5M at ~120K v/h, 9 s; "todos los cortes de pelo" 2.2M). Built
  gta6-lucia-outfits on it: 8 numbered outfits, ~1.4 s per cut, 5-outfit flash in the first 1.75 s, recap flash at
  the end that loops, the catch (#8 Vintage Vice City Pack, only with copies bought before Nov 20). Renderer: segment
  `pad` 0.1 + `hard_cut` (the default 0.45 s pad + fade to black between segments made v1 feel slow: 23 s -> 19 s).
  Title words people search: "Lucia" and "outfits" (not "looks").
- 2026-11-22 (main chat): every Short rendered before today has a ~0.1 s black flash at each cut (segment fade out +
  fade in) plus a 0.45 s pause after each line. New default for Shorts: 0.2 s pause + hard cuts (same Dexter script:
  20.4 s -> 19.3 s, 3 black flashes -> 0). Long videos keep the soft dip.
- 2026-11-22 (main chat, owner "something is not working, check online"): YouTube's Oct 1, 2026 Shorts update ranks
  original videos higher; YouTube's Creator Liaison reportedly said voice-over on reused footage doesn't make a clip
  original (Mark Studios, OutlierKit, Relevant Audience). Our narrated trailer-footage Shorts: median 366 views; real
  gameplay moments (the LACY clips): 1K-9.4K. Fixes: studio/charts.py (our own animated leaderboards/counters as the main
  picture, trailer as cutaways); owner gameplay is still the biggest missing lever.
