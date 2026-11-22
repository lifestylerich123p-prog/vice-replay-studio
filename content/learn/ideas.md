# Ideas backlog (newest first; the daily run picks from here when today's plan row is free)

Rules: re-check every fact on the day you use it (2+ sources), label estimates/reports, no story spoilers, no
isolated cutscenes. Mark an idea USED (date + slug) when it ships. Researched by the main chat; sources inline.

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
