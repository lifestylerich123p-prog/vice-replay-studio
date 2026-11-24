# Ideas backlog (newest first; the daily run picks from here when today's plan row is free)

Rules: re-check every fact on the day you use it (2+ sources), label estimates/reports, no story spoilers, no
isolated cutscenes. Mark an idea USED (date + slug) when it ships. Researched by the main chat; sources inline.

## Week of Nov 30 (main chat, Nov 23; plan in content/week-2026-11-30.md)
Made and waiting for approval: gta6-top-3-rides (remade as cards), gta6-vs-red-dead-2 (VS), gta-tier-list-sales
(Tier List #2), gta-cities-quiz (Quiz #3). For the daily run: Fri countdown "old GTA brands back in GTA 6" (Sprunk,
eCola, Fleeca, Gruppe Sechs: Kotaku's extended-look details; find a 2nd source each), Sat Spanish special (top
Spanish-speaking streamers, only if Streams Charts numbers agree in 2 sources; IlloJuan "562K" conflicted Nov 23),
Sun Dec 6 long video "GTA 6 at The Game Awards 2026: all 8 nominations explained".

## From the Nov 23 investigation (content/learn/market-2026-11-23.md)
1. BUILT: `gta6-5-things` (facts-only "5 things you didn't know", the week's #1 breakout format). Next: a Part 2 with 5
   NEW checked facts, and with owner gameplay a "hidden details" version.
2. **"GTA 6 has 61 cheats, but there's a catch"** (validated: a 31-subscriber channel got 30.8K with it). Re-check the
   count and the catch (cheats unlock after the story?) with 2+ sources; list card of the catch.
3. **IG carousel "Goodbye GTA 5: 13 years in numbers"** (rides the farewell-to-GTA-5 trend) next to the 13-years Short.
4. Titles: lead with "GTA 6 vs GTA 5" wherever the Short is a comparison.

## Graph Shorts to make next (Nov 22, afternoon; numbers NOT checked yet: research each on the day, 2+ sources)
Built on today's rules: statement hook with the number, 35-55 words, our own chart, vary the layout (see the chart
column), English + Spanish (`chart_es`). Used so far: money (counter VS + bars), 99 club (counter + bars), trailer
views (counter + bars), inflation (counter + LINE).
1. **"Only 1 in 5 finished Chapter 1"**: counter (18%) then bars per tracker (Exophase, Leonida Verse...). Open on
   the counter, no clip until the end. Say "according to trophy trackers"; numbers move daily.
2. **GTA 6 is X hours longer than GTA 5**: bars (GTA 5, RDR2, GTA 6 main story, HowLongToBeat). The long video on
   this (rHaMTePDRUQ) got 0 views; the same fact as a 15 s graph Short is the fair test. Open on BARS this time.
3. **Trailer 1's record, day by day**: line chart of Trailer 1 milestones (24 h record, 1 week, 1 year, today) from
   news reports of each milestone + the API count today. Layout: line first, counter last.
4. **IShowSpeed's record vs every GTA 6 streamer**: bars of peak live viewers (Streams Charts; label it "peak
   viewers", not views). Streamer stories are our best format with zero flops.
5. **212 GB: GTA 6 vs the biggest games**: bars of download sizes (PlayStation Store pages). Ties into the storage
   guide (affiliate) on the website, not in the Short.
6. **Spanish first: top 3 streamers hispanos** (IlloJuan, Rubius, AuronPlay) once Streams Charts confirms: bars,
   Spanish-only like gta6-money-chart-es.

## New leads (Nov 22, 6:30 PM ET; from the news radar: verify each on the day, 2+ sources)
1. **Rockstar interviews (IGN, Nov 22)**: Jason's personality comes from Steve McQueen and real veterans; darts were
   cut because Rockstar didn't have "unlimited money or time" to make them feel right. Quote-card Shorts (new
   `quote` chart): the exact line, who said it, one sentence of our take. No spoilers; check the quote in the original.
2. **Randy's Wish List vehicle locations** (IGN guide, Push Square, Insider Gaming): a collect-them-all car list is a
   search magnet. Website guide first (EN + ES); a Short only with a number ("X cars, here's the rarest").
3. **YouTube image carousels in the Shorts feed** (Made on YouTube, Sep 2026; rolling out): our Instagram carousels
   (4:5 cards) could also go out as YouTube image posts, 100% original. No API for it: the owner posts from the phone.
4. **Shorts series** (seasons/episodes with sequential playback): YouTube Partner Program channels only, so not yet.
   When we're in YPP: group the graph Shorts as a series ("GTA 6 by the numbers").

## Upgrades found online, Nov 22 night (ranked; owner action marked)
1. **Quota is the bottleneck** (ran out at ~7 PM Nov 22 after 6 uploads; Vice Replay, the Spanish channel and What If
   Arena share ONE Google Cloud project = one daily quota). Built: no Spanish subtitle track on English Shorts
   (saves 400 units per Short). OWNER: give What If Arena its own Google Cloud project (own 10,000+ units a day), and/or
   send YouTube's free "Audit and Quota Extension Form" (support.google.com/youtube/contact/yt_api_form; needs a
   compliance audit; no published timeline).
2. **Instagram Trial Reels through the API** (`trial_params`, graduation MANUAL or SS_PERFORMANCE, since Dec 2025):
   shows a Reel to non-followers first. Eligibility reportedly needs a professional account with 200-1,000+
   followers (we have 14): add when eligible.
3. **TikTok Content Posting API**: unaudited apps can only post PRIVATE videos (max 5 users/day), so automatic
   TikTok posting needs TikTok's app audit; the owner keeps posting by hand (or a paid audited tool).
4. **Quiz / trivia Shorts**: vendors say quiz channels grow fast, with no hard data; our own test is the history quiz
   (Thu Nov 26) vs the facts-only Shorts.

## System ideas not built yet (Nov 22; ranked by views per effort)
1. **Owner gameplay** stays the biggest lever (originality + "demand moved to gameplay"): 15-30 s moments recorded
   with the radio off; `studio.gameplay` already pulls them and Shorts use them first.
2. **First-hour check**: 90 min after a Short goes public, compare its views with our median at 90 min; if it's in the
   bottom quarter, swap to title option 2 (`studio.title_swap` exists; wire it to a send_later after each upload).
3. BUILT Nov 22 (viewcheck.stale_charts): the publish check warns when a chart `note` says a date 3+ days before the
   upload day (trailer views says "Nov 22" and posts Nov 25: re-read the counts, update the note, re-render).
4. **Count-up from a head start**: a counter starts at 0, so the very first frame shows "$0". Try `"from": 0.7` (start at
   70% of the value) on one Short and compare viewed-vs-swiped with a 0-start one.
5. **Comment-picked topics**: the pinned questions' answers (YES/NO, 1-2-3) are free data; tally them in the daily run
   and turn the winner into the next graph ("72% of you said...") once a Short gets 20+ answers.

## Spanish channel (researched Nov 22, 2026)
1. **IlloJuan borró GTA 6 por error en directo** (~500K viewers, launch night in Spain; AuronPlay reacted). Only
   ClaroSports so far (clarosports.com/us/tendencias-us/illojuan-ya-dejo-uno-de-los-clips-del-ano-borro-gta-6-por-error-ante-medio-millon-de-espectadores/):
   needs a 2nd reliable source before use. Our voice + official footage only.
2. **IlloJuan's 233,520-viewer record** was the Aug 2026 GTA VI presentation (Streams Charts via LevelUp), not launch.
3. **Rubius played early via a New Zealand region switch** (Azteca Jalisco only; another report says base PS5 and
   Notebookcheck says he only watched gameplay at Rockstar North): conflicting, don't use until 2 outlets agree.
4. Spanish-speaking launch rankings: IlloJuan, Rubius and AuronPlay were the biggest Spanish streams of the first
   24 h (streamer.guide, one source): a "top 3 streamers hispanos" Short once Streams Charts confirms the numbers.

## Researched Nov 21, 2026 (main chat: formats that need no gameplay)
1. **Quiz: guess the GTA 6 place from the official map** (`quiz`). Magnify a map label area with the name blurred
   or cropped out, then reveal: Key Lento, Lake Leonida, Mount Kalaga National Park, Port Gellhorn, Vice Beach. Map:
   media/official/leonida-map-poster.jpg (Rockstar's free poster). Template: episodes/gta6-guess-the-ride.json.
2. **Quiz: guess the shop** (Rideout Customs, Sara's Unisex Salon, Stock 305, One-Eyed Willie's) from one detail of
   the official Ultimate Edition screenshots (names on rockstargames.com/VI/ultimate-edition).
3. **"Only 1 in 5 players finished Chapter 1"**: trophy trackers (Exophase ~18% of 54K tracked, Leonida Verse 5.6%
   on Nov 21; both under 20%). Re-check both on the day (numbers move daily); say "according to trophy trackers".
4. **Streamer records**: IShowSpeed's GTA 6 stream peaked around 372-392K viewers, a channel record (Streams Charts,
   passionategeekz); 7.9M peak viewers across platforms on launch day (Streams Charts). Re-verify the day you use it.
5. **"GTA 6 has 61 cheats... but you have to finish the story"** (TweakTown, Player.One, Esquire India). Only after
   3+ days without a cheats Short (we've posted 3; don't repeat the "catch" angle as-is).
6. **Ranking: the 5 best Ultimate Edition rides** from Rockstar's own list (Cheetah, Dominator Buggy, Squalo, Dinka
   Enduro, Ganado retro build), our own picks with one reason each.

## Researched Nov 19, 2026 (night)
1. USED 2026-11-20 (gta6-beginner-tips-nobody-tells-you, main Short) **GTA 6 has no mission replay (save like this)**. Hook: "No mission replay. 15 save slots." 15 manual slots +
   1 autosave; loading an old save overwrites the autosave.
   gtaboom.com/gta-6-has-a-new-save-system-and-will-not-let-you-replay-story-missions-fa48 ·
   gamerfuzion.com/gta-6-how-to-save-manual-save-slots-mission-replay/
2. USED 2026-11-20 (gta6-beginner-tips-nobody-tells-you, tip 2) **Never carry over $20,000**. Hook: "Die once, lose $20,000." Pocket cash caps at $20K and is lost when wasted or
   busted; ATMs come with the "Buck Me" mission (guides disagree on how safe banked cash is: say so).
   gamesradar.com/games/grand-theft-auto/gta-6-atm/ · vicecityhustle.com/guides/gta-6-wasted-busted-what-you-lose
3. USED 2026-11-20 (gta6-beginner-tips-nobody-tells-you, news Short) **A lifeguard dog on a jet ski**. Hook: "Swim too far. A dog comes." Kotaku + all.gg (gta-6-players-discover-a-
   dog-that-rescues-you-at-sea). Wholesome, shareable, no spoilers.
4. **The literal Easter egg**. Hook: "Climb 7 minutes. Throw one egg." GameSpot (gta-6-has-a-hilarious-riff-on-
   easter-eggs) + IBTimes. Screenshots/owner gameplay only, never the gag cutscene itself.
5. **IShowSpeed cried at "Watkins Auto Parts"**. Hook: "His family name is in GTA 6?" Sportskeeda; Rockstar hasn't
   confirmed a nod, so "he says". (Streamer news = our best format.)
6. **Base PS5 dips to 23 FPS** (Digital Foundry, reported second-hand by altchar): Pro is steadiest. Ties into the
   PS5 Pro guide (affiliate). Verify with a 2nd outlet first.
7. **19 million copies on day one?** Sensor Tower ESTIMATE: 19.1M copies, ~$1.84B (Globe and Mail, Men's Journal).
   Take-Two's official numbers are expected by Nov 23: make it a breaking-news Short when they land.

## GTA 6-style lettering Shorts (owner Nov 23: no trailer images; "lettering and more modern style")
Research (Nov 23, web: FluxNote, Influencers-Time, AIR Media-Tech, YouTube's own blog on tier lists): text-on-screen is
the standard for faceless Shorts; animate only the key words; change the picture every 2-4 s (8-12 scenes per 30 s);
tier lists (a gaming-born format, S = "super"), countdown listicles (4-6 s per item), quizzes with a timer and VS /
"this or that" drive comments. Our own data: statement hooks beat questions; "catch" and "vs GTA 5" work.
Next ideas on the new cards (facts checked before writing):
1. **Tier list: every GTA by critics** (built: gta6-tier-list-critics, "Vice City is only B tier").
2. **4 secrets as a countdown** (re-made Nov 23 in the new style; awaiting approval).
3. **VS: GTA 6 vs GTA 5 in 4 numbers** (price $80 vs $60, 80 h vs 32 h, $3.79B vs $800M day one, 99 vs 97): one VS
   card per number, the winner lights up.
4. **Tier list: GTA 6 radio stations by what the comments pick** (needs our comment data first).
5. **Breaking-news card** for any confirmed update/patch (kicker CONFIRMED / REPORTEDLY).

## Weekly card series (owner approved Nov 23, "all")
Mon news card · Tue VS · Wed tier list · Thu quiz · Fri countdown · Sat Spanish special · Sun long hub (3:30 PM) +
meter Short. Details in .claude/commands/daily-video.md rule 7. Number each series in the description ("Vice Replay
Tier List #2") so returning viewers recognize it.

## Nov 24 investigation (market + search)
- **"GTA 5 vs GTA 6: <one feature>" series** (comparison = our #2 format, 6.0 v/h; the day's hottest GTA 6 Shorts were
  "GTA 5 vs GTA 6 Cops" 12.5M and "GTA 6 vs RDR2 gun strap" 8.9M). Versus card first, 1 verified difference per Short.
  First one booked: gta6-cops-remember (Thu Nov 26). Next ideas: wanted stars, map size, phone, swimming/diving,
  weather, radio. Every claim about GTA 6 in 2+ sources; GTA 5 side only what's well documented.
- **Tier lists keep winning** ("Vice City is only B tier": 506 views in 3 h, 613 in 24 h vs 431 footage median).
  Booked: protagonists (Thu), money (Fri), maps (Sat). Keep one a week at least.
- **Search gaps filled**: "gta 6 how to lower criminal profile" -> guide EN+ES live + Short draft gta6-criminal-profile.
  Skipped: impound (guides disagree, tied to a story mission), "gta 6 netflix" (August's Extended Look, not news),
  hurricane "how to trigger" (hurricanes confirmed by Game Informer; no source shows a trigger: clickbait).
- **Already posted, don't redo**: cheats (3 Shorts), no mission replay, Dog Island. Check uploads.json first.
