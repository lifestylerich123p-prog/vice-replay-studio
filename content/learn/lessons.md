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
- 2026-11-22 (flop review, all videos 36 h+ old): long videos median 14 views (7/9 under 50) -> no daily long video,
  only Sunday's recap; tips/how-to Shorts median 237 (3/7 under 50) -> website only; catch 1,174, number/verdict 928,
  streamer 638 (0 flops); Shorts at 6-11 AM median 1,084 vs 2-6 PM 199; 76+ word scripts median 404 vs 56-75 words 836
  (block now at 76). 9 flops set private (not deleted).
- 2026-11-22 (hook research): our 20 Shorts with retention data: question as the first sentence 35% viewed (median 130
  views, n=4) vs statement 60% (858, n=16). Best: the surprising result at once ("Eighteen hours early." 82%, "GTA 6
  cheats are real, but there's a catch nobody expected." 75%, "GTA 6 just got a ninety nine on Metacritic." 66%).
  Worst: questions ("Can't get into GTA 6?" 25%, "GTA 6 looking blurry?" 26%) and setups ("Rockstar's boss almost
  never speaks in public." 47%). Outside research (vendor blogs, inconsistent numbers) agrees: claim first, no intro,
  curiosity gap + fast payoff. Now enforced: studio.vice publish blocks a question opener.
- 2026-11-22 (hook investigation, content/learn/hooks-2026-11-22.md): a number in the first on-screen headline kept 65%
  vs 49%; real gameplay moments 89% vs 58% narrated; top market Shorts with titles of 40 characters or less 95K v/h vs
  70K; "when..."/POV titles 2x (needs gameplay). "#8" in a title became a hashtag (caught in the Lucia title, now blocked).

## 2026-11-22 (evening): YouTube Partner Program bar doubles on Feb 1, 2027
- YouTube's help page "Changes to the YouTube Partner Program" (support.google.com/youtube/answer/12843009) plus
  Search Engine Journal, Basic Tutorials and others: from Feb 1, 2027, NEW channels need 1,000 subscribers AND 8,000
  watch hours in 365 days OR 20 million Shorts views in 90 days (today: 4,000 hours or 10 million). Channels already
  in YPP keep their status (activity rules apply). Vice Replay is at 15 subscribers and ~36K lifetime views (Nov 22),
  so joining before Feb 1 is a long shot; plan for the new bar. What follows: subscribers are the first gate either
  way (follow badge, pinned questions, a series viewers want to binge), and Shorts views are the realistic path (our
  long videos get a median of 14 views).


## Nov 23, 2026: Everygen voices for Spanish (Cuban Short)
- Everygen voiceovers cost about 1 credit per line (up to ~70 characters): cheap for voices Kokoro lacks.
- In Spanish, **Viral Adam** sounds native and passes the caption check (Whisper hears the script); **Pham** has a
  foreign accent (51% word error: "GTS es esta leno"). Owner picked Viral Adam. Test any new voice with the caption
  check before using it.
- Put per-segment voice files in `media/voice/<slug>/` and point `audio_es` (or `audio`) at them; the renderer uses them
  instead of Kokoro and the rights gate checks them (`everygen-voice` in rights/registry.json).

## Nov 23, 2026: lettering Shorts, captions and layout
- Captions read "seventy nine ninety nine" like a year and showed "7,999"; the voice reads "$79.99" as "1 dollar 79 99".
  Say prices as "seventy nine dollars and ninety nine cents" (captions: "79 dollars and 99 cents"). The publish check
  now warns on any spoken number that becomes a 4-digit non-year.
- Two-line captions reach up to ~60% of a Short's height: on vertical Shorts the source line sits ABOVE the card;
  keep card text out of the bottom ~8% of the card area.
- 16:9 long videos: the VS card goes side by side; size lettering by the short side of the frame.
- Headlines over 19 characters wrap and hit the lettering (warned). One `seed` per Short keeps the same sky.
- Captions turned spoken decimals into nonsense ("one point eight four billion" -> "one point 12,000,000,000";
  "sixty eight point seven million" -> "68 point 7,000,000"), on every video before Nov 23. Fixed in
  make_video.display_tokens: decimals show as "1.84 billion" / "68.7 million", round numbers as "800 million".

## 2026-11-23 afternoon (main chat): first lettering Shorts, first results
- **Tier list took off**: "GTA 6 tier list: Vice City is only B tier" (tier cards, 18 s, statement hook that picks a
  fight) had 506 views ~2.5 h after its 12:30 PM slot, about 2x our best Short at the same age (258 at 3 h). Same day,
  same style: darts quote card 16 views at ~5 h, patch-notes news card 8 at ~6 h. Lesson: rankings with a contrarian
  verdict beat plain news/quote cards; follow up with Tier List #2 (sales) while it's hot.
- **Spanish channel gets ~0 distribution so far** (0 subscribers; the Spanish tier list had 0 views at 2.5 h while the
  English one had 506). Same video, so it's the channel, not the format: keep Spanish uploads lean until it has a base.
- **News ages fast**: the 9 AM "zero patch notes" Short was outdated by the afternoon (Rockstar published notes for
  1.002.002). For "no news yet" angles, re-check right before the slot, and prefer framings that stay true ("3 updates
  in 10 days") over "zero X".
- **Spanish channel diagnosis (Nov 23 evening)**: settings are right (channel + every video: language es, audio es,
  Gaming, not made for kids, 12-15 tags), yet 0 total views after 9 videos. Likely causes: a 1-day-old channel with
  0 subscribers, and Shorts that repeat the English cards (same layout and order, Spanish text) from a second channel
  of the same owner, which YouTube can treat as repeated content. Response: winners-only (fewer, proven Spanish
  versions) + Spanish-only originals (Cuba, prices by country, no dubbing). If a Spanish version goes up, change its
  hook card (a Spanish-specific opener) so it isn't a 1:1 copy of the English Short.

## 2026-11-24 (daily run): what the numbers say this morning
- **Rankings with a verdict are still our best card**: "Vice City is only B tier" is at 612 views (36 v/h vs a 2 v/h
  channel median); the darts quote card from the same weekend sits at 23. Same lettering style, so the difference is
  the angle (a ranking that picks a fight) not the picture. Today's VS rounds end on a verdict for the same reason.
- **Streamer + "wasn't IShowSpeed" angle keeps paying**: "The first person to finish GTA 6 wasn't IShowSpeed" is at 616
  (14 v/h, still climbing on day 3). Today's main Short reuses the shape with new numbers ("Speed won by 580,000 hours",
  a VTuber at #2) instead of repeating the topic.
- **Market (last 48 h)**: the top GTA 6 Shorts are short and simple: "GTA 5 vs GTA 6 Cops" 11.3M in 9 s, "GTA 6 Hidden
  Facts" 12.1M in 42 s, "Map of all GTA 6 Players" 5.8M in 11 s. VS and "hidden facts/secrets" are the formats we can
  make legally (our cards, no their footage); the easter-egg Short today is our "hidden facts" test. Statement openers
  still beat questions on our channel (6.4 vs 1.6 v/h median, n=26 vs 3).

## 2026-11-24 (owner: "check why views are falling"): diagnosis + what changes
- **The launch spike was borrowed views.** Channel views: Nov 19 16,579 (5,903 from search) -> Nov 20 3,612 -> Nov 21
  899 (pre-launch Nov 14-16 was 1,600-2,300/day). About 11,000 of the Nov 17-21 views were LACY campaign clips, which
  now post on ClipCircuit (owner rule Nov 20), and launch-day search ("NZ trick", "already out", "$1.65 billion")
  faded within 48 h. Part of the drop is the whole niche cooling after launch, not us.
- **What we control: picture + angle + volume.** Footage Shorts (27, now retired): median 431 views at 24 h, 63.6%
  watched. Lettering cards so far: one hit (tier list, 612) and the rest 2-80 views; the 7 fixes Short had 2 views
  in its first hour = people swipe past text-only cards unless the angle picks a fight (rankings with a verdict).
  Volume fell from 6-7 public Shorts/day (Nov 17-20) to 3 (Nov 22-23), and 22 of 66 uploads are private.
- **Market check:** the biggest GTA 6 Shorts this week are gameplay moments and streamer reactions (Spanish market:
  Sergio Encinas 10.8M, Rubius easter egg 3.7M); search demand is gameplay help (money, key cloner, radio, easter
  eggs). Our cards can match the topics, but the visuals people stop for are gameplay.
- **Changes made Nov 24:** (1) uploader blocks the same story twice (studio/postguard.same_story: two breaking runs
  posted "39 million PS5 players" 3 h apart because the first couldn't push the registry); (2) doctor warns about
  uploads missing from the registry; (3) breaking news after 6 PM ET waits for 9:30 AM next day (6 PM-6 AM = 1.9
  views/h vs 16 for 6-11 AM); (4) status shows 🧊 for Shorts under 15 views after 2-12 h, next to the 🔥 ones.
- **Do next:** rankings/versus/"catch" angles over plain number trivia; how-to angles from studio.search_demand
  (money, key cloner, easter eggs) as cards; keep 4-6 Shorts/day in morning slots; and the biggest lever is the
  owner's own gameplay (`media/gameplay/` via the Drive folder, radio off): Rockstar's policy allows it and it's
  what the top Shorts show.

## Nov 24 investigation (owner: "continue to investigate and act")
- Traffic, Oct 27-Nov 24 (YouTube Analytics): Shorts feed 27,574 views, **YouTube search 8,072 (22%)**, related videos 22,
  browse/other 366. Search is our second engine: titles must start with the exact phrase people type ("GTA 6 ..." +
  "where to find" / "how to" / the thing's name), and the first line of the description repeats it.
- Both recent long videos (how long to beat, launch week recap) had **0 views** after 2-3 days; related-video traffic
  is ~0. Long videos now only for big events until the owner's own gameplay exists (CLAUDE.md posting rule).
- Scorecard: tips/discovery Shorts lead (6.3 v/h, 715 views in 24 h, 72% watched); "catch" headlines next (7.7 v/h).
  The map series ("where to find X" on the official map) is built on both; each has a catch-style title as option 2
  for the automatic swap.
- Hook v2 (same day): photo cards were too dark and static in the first second; now brighter 4K pictures, a punch-in
  in the first 0.45 s, no repeated hook text, bright hook pictures only (luminance 85+).
- Slug reuse bug: a new Short reused an old private Short's slug, so the uploader would have skipped it; studio.doctor
  now flags it.
- Instagram (Nov 24, `studio.ig_stats`; views need the instagram_manage_insights permission, so likes/comments only):
  practical tip Reels win by far: "First 3 settings to change" 119 likes, "Don't grind money in Chapter 1 (here's
  the catch)" 68, "cheat codes that actually work (screenshot this)" 41, "no mission replay (save like this)" 37.
  Carousels: median 0 likes over 5 (they mostly reach our 15 followers). Facts/number Reels ~0. So: tips and
  where-to-find first, a "save this" nudge on them, carousels only when they're genuinely save-worthy.
- Retention (Nov 24 refresh): average Short is watched 68% (many rewatch). Viewers don't leave; YouTube shows us to
  too few people. The fix is the first frame + topic (search phrases, tips), not shorter Shorts.
- Opening review (Nov 24, independent reviewer on 4 booked Shorts, scores 4-7/10): all four opened on a static
  two-line card until ~3 s; the payoff (pin, board) came at 3.3-3.9 s, after the swipe decision. Fixed in the renderer
  for every Short: payoff picture in frame one, lettering slam in the first 300 ms, no duplicate tags/captions, bigger
  tier board, follow badge moved above YouTube's title overlay, map zooms kept inside the printed map and off the
  "LEONIDA" title art. Facts: the egg tower's region isn't settled (Bluegrass vs South Vice-Dale; IBTimes: not
  independently established), so always say "guides point to".
- Competitor details (Nov 24; 68 top GTA 6 Shorts of the week + metadata of the top 50 via the API): median views/h
  with an emoji in the title 133K vs 99K; "vs" comparisons 207K vs 104K; "?" in the title 69K vs 108K; 20 s or less
  151K vs 98K (our own data doesn't show that: our 31-60 s did better in launch week, keep 13-20 s). Most top Shorts
  have EMPTY descriptions and no tags (metadata isn't the lever; the first frame and topic are). Their like rate ~1.65%
  = ours 1.58%, but our comment rate is ~19x theirs (0.26% vs 0.014%): the pinned question works, keep it. Smaller
  channels (under ~120K subs) that won: comparisons, "5 things you didn't know", exact money ("Fastest $40,000"),
  "(Most People Miss This)" tags, details/NPC behaviour. Applied: one topic emoji on every booked English title.
- 2026-11-25 (first TikTok numbers, via Windsor.ai; raw: content/learn/tiktok-2026-11-25.json): all 19 TikToks were
  posted Nov 17-19 and none since, so the tiktok-files hand-off has stalled. They were the old 30-35 s Shorts: viewers
  watched a median 5.9 s, only 3.9% watched to the end, 0 followers gained from any video. Best: "GTA 6 NZ trick: 18
  hours early?" 914 views (a catch/trick hook, like on YouTube). Spanish versions on the same account did as well or
  better (median 177 vs 152 views; "$1.65 MILLONES" 587 vs the English 114). So on TikTok: post the new 13-25 s
  payoff-first Shorts, post the Spanish version too, lead with the catch.
- 2026-11-25 (daily run; studio.status 5:15 AM ET + market-2026-11-25.md): the critics tier list ("Vice City is only
  B tier", jQbv5GPR3dk) is still the only fresh Short taking off (616 views, 15/h vs our 1/h median), while the four
  most recent number/fact Shorts sit at 19-63 views (sales tier list 63, cheapest-GTA 47, Metacritic 99 club 28, patch
  notes 19). Same lesson as Nov 24, now with more data: a contrarian ranking beats a plain number even when both use
  the same Metacritic facts. Follow-up made with NEW games (RDR1/RDR2/Bully/Max Payne 3), not a re-cut.
- 2026-11-25 (market): the 48 h top 25 GTA 6 Shorts are mostly skits/relatable humour (we can't make those without
  gameplay), but the money how-to lane is wide open in long form: "How to make $100k from ATM robberies" (9:45,
  676K views, 24.7K/h) and "Fastest $40,000" (Short, 3.9M). Our search-guide long video today copies the TOPIC (ATM
  robberies, with the catch players hit: marked bills), not the footage.
- 2026-11-25 (process): this cloud session had a Python 3.13 `pip` on PATH while `python` is 3.11, so
  `pip install -r requirements.txt` installed nothing usable (requests/Pillow missing). Use
  `python -m pip install -r requirements.txt`.

- 2026-11-26 flop review: "Rockstar: even we don't have unlimited time (GTA 6) #GTA6 #Shorts" had 30 views at 56 h (news/facts, graph (older charts), opener statement, title hook statement, 16-30 s, posted morning <12); set private (not deleted).
- 2026-11-26 flop review: "68 MILLION views on ONE GTA 6 stream #GTA6 #Shorts" had 36 views at 72 h (news/facts, trailer/screenshots, opener question, title hook number, 16-30 s, posted evening 17-21); set private (not deleted).
- 2026-11-26 (mid-week verdict, owner Nov 22 "continue to monitor": facts-only vs footage): the planned head-to-head
  can't be run as booked: 4 of the 5 footage Shorts (Dexter, 60 FPS, rides, Lucia outfits) stayed PRIVATE after the
  Nov 23 switch to lettering cards. By picture type (scorecard, all 39 Shorts): trailer/screenshots (retired) median
  431 views at 24 h, 4.6 v/h, 62% watched; lettering cards 67 at 24 h, 2.9 v/h, 67%; older graph charts 28, 1.6 v/h,
  32%. The pure facts Shorts named in the test: darts 28, 99 club 28, inflation 63 views at 24 h (darts set private
  by the flop rule today); Spanish facts Shorts 0-5 views. So the plain-fact format lost by ~7-15x to the old
  screenshot Shorts, and the owner's Nov 24 "no pure fact Shorts" rule was right. What wins on the new cards: tier
  lists (median 270 views at 3 h) and map "where is X" Shorts: the Paul Walker car map Short (ChmiOLulOvo, posted
  Nov 25 3:45 PM, an afternoon slot) had 171 views after ~4 h (~40 v/h vs our 2 v/h median), and the shoe-store map
  TikTok reached 2,653 views (18% watched to the end). Next: map + tier first, one map Short every day (owner Nov 25).
- 2026-11-26 (comments, owner "learn from comments"; `python -m studio.comment_insights`, 1,254 top comments on the 15
  hottest GTA 6 videos + ours, content/learn/comment-insights-2026-11-26.md): what players talk about most is REALISM
  and COMPARISONS: NPCs/physics/details (88 comments, ~8,000 likes) and GTA 6 vs GTA 5 / RDR2 (92 comments). Secrets with
  an exact spot get the biggest single reactions (6,600 likes on the Vice City portal easter egg). Florida-man humour
  lands (an "alligator blood" joke: 1,274 likes). In Spanish, Jason & Lucia's relationship is a question people ask
  ("¿son novios?", 748 likes). Story, Online, bugs and streamers barely come up in the top comments. On OUR channel the
  few comments are about 30 FPS and waiting for the PC version. Questions under viral entertainment videos are mostly
  jokes: use YouTube search terms (search-terms.json) for "where is X" demand, comments for themes and tone.
