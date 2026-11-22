# Channel owner settings

- Time zone: US Eastern (Miami, Florida), America/New_York. Posting times in CLAUDE.md are already local.
- Upload style: owner reviews every video, then uploads and schedules in YouTube Studio
- Gameplay Drive folder: https://drive.google.com/drive/folders/1P6MdlMGA3R6q2jotp9hZ_plpF6Xj_e8w
- Review page (pinned, updated by every run): https://claude.ai/artifact/DWvVW2BQrHZP9Xfs5Ve17Q

## Standing approvals
- 2026-11-17: Breaking-news auto-post. The owner approved publishing breaking-news Shorts WITHOUT asking first,
  only under the rules in `.claude/commands/breaking-news.md` (score 8+/10, 2+ reputable sources, max 2 per day,
  Shorts only, no spoilers, no repeats). Everything else still waits for the owner's "approve". The owner can turn
  this off any time by saying so; then delete this line.
- Business email: contact@vicereplay.com (Cloudflare Email Routing -> owner Gmail); site page /contact/
- Website: https://vicereplay.com (GitHub Pages, repo lifestylerich123p-prog/vicereplay-site; domain on Cloudflare)
- Gear page (affiliate links): https://vicereplay.com/gear/
- Website pages: / (home), /gear/, /guides/ (10 guides+news, built by tools/site_guides.py), /links/ (bio link), /contact/.
  Google Search Console verified + sitemap submitted (Nov 17). Cloudflare Web Analytics on every page.
  Launch live page: add a line to UPDATES in tools/site_guides.py each day of launch week (newest first).
  Spanish guides under /es/guias/ (ALT dict pairs EN<->ES). Each guide gets a share image in /og/ (CARDS) and FAQ (FAQS).
  New guide = add a guide() call in tools/site_guides.py, run it, push vicereplay-site. Scheduled runs can't push: do it in chat. . Use this link in banners, bios and replies; it's listed in Amazon Associates.

- TikTok chat: "📱 Vice Replay: TikTok files" (session_01CJRsWQ4prmRGdfaEyZXz7q). The owner wants every TikTok video sent there with its
  caption and posting time. From the main control session: push the .mp4s to a temporary branch `tiktok-files` (folder v/)
  and send_message that session to fetch them and SendUserFile them. Daily runs can't push: they send_message the captions,
  times and the name of the run's chat where the files are.

- Several Vice Replay chats at once (checked Nov 21, 2026, when the owner opened "YouTube Shorts tools evaluation",
  session_01CJRsWREDSmYU9Rbr46SGyX, next to the main control chat session_01CJRsWP9GjYTirqgQXefGyG). Rules so one chat
  never damages another:
  1. Only the MAIN CONTROL chat posts: YouTube uploads/comments/title swaps, Instagram, website pushes, send_later
     reminders. Helper chats research, test and build; they don't post (even with an "approve" typed there, they hand
     the command to the main chat) and they don't edit the same file the main chat is changing that day.
  2. Helper chats commit to their own `claude/...` branch, never straight to main. The main chat merges a branch
     when the owner says so ("merge it"), after the tests pass. The daily run pushes to main.
  3. Everyone runs `git pull --rebase origin main` before committing, so nobody overwrites anyone.
  4. Safety net (studio/postguard.py): before any YouTube upload the uploader checks the registry on EVERY GitHub
     branch and the channel's real video list (scheduled ones too); the Instagram queue checks the account's latest
     posts and counts today's real posts for the 4-a-day limit. A second chat therefore skips what another posted.
  Each chat has its own container: its files, installs and scratch work don't touch the other chat's copy.

- Impact.com (Best Buy / Walmart / Newegg affiliate): marketplace application DECLINED on Nov 18, 2026 (new site, no traffic
  yet). Site verified with Impact's meta tag (keep it on the home page). Reapply in ~30-60 days once vicereplay.com has
  steady visitors (Cloudflare Web Analytics) and the channel has more subscribers.

- Excluded official screenshots (strip club / sexualized; never add to media/): boobie-ike-02/03/04, drequan-priest-01/02,
  jason-and-lucia-10/14, real-dimez-02, port-gellhorn-04/05/07, vice-city-02/06/07/18/23/25 (Rockstar pack names).
  Launch Trailer shots skipped: logos/end cards and the shower/club shots.

- 2026-11-18: STANDING APPROVAL for comment auto-replies. The owner (on Max) approved replying to new YouTube comments
  automatically twice a day (~1:13 PM and ~9:13 PM ET) via `.claude/commands/auto-replies.md` / `python -m studio.replies`,
  skipping spam, hate, trolls and anything unsafe. Also approved: Opus for the daily run, 3 Shorts a day in launch week.

- 2026-11-18 ~10 PM ET: TONIGHT-ONLY approval (GTA 6 launch night). The owner said: "For tonight approve all and if
  need make new video without my approval." Valid until 9:00 AM ET on 2026-11-19: the main chat may upload anything
  that is ready (including the launch-day morning episode when it arrives) and make + post new launch-night videos
  without asking, still following every channel rule (facts sourced, no spoilers, no licensed music, not affiliated).
  After 9:00 AM ET the normal approval rules apply again.

- 2026-11-18: STANDING APPROVAL for title swaps ("All" to the upgrade list). Once per video, 24-96 h after posting, an
  upload with views/hour below 40% of our recent median (and under 1,000 views) gets its title changed to title
  option 2 (`python -m studio.title_swap`, run in the daily momentum check). Nothing else about the video changes.

- Dashboard: https://claude.ai/artifact/UZSJWSBJbXBByZvWcxrxiF (refresh with /dashboard in the main chat after uploads).

- Instagram: @vice.replaytv (https://www.instagram.com/vice.replaytv/), professional Creator account created Nov 18.
  Reels auto-posting not connected yet (content/archive/instagram-setup-2026-11-19.md); until then the owner reposts Shorts by hand.
- 2026-11-18 11:55 PM ET: owner extended it: "Just continue to monitor thru the night post if needed without my
  approval." Overnight checks at 12:10 (comment), 1:15, 2:45, 4:45 and 6:45 AM; each may post one strong, confirmed
  (2+ reputable sources), uncovered story as a Short. Ends 9:00 AM ET Nov 19.
- 2026-11-19: Owner said "If anything use something else not Everygen": campaign clips use the free local engine (studio/clip.py) with footage the owner puts in Google Drive. Don't use Everygen unless the owner asks again.
- Campaign clips folder: https://drive.google.com/drive/folders/1kuRRXtAaLCs28N3w8tnlEW_Q5gQ6ZIpv (subfolders Lacy, KreekCraft; owner shares it once as 'Anyone with the link can view'; `python -m studio.campaign_inbox` cuts new recordings)
- 2026-11-19 (later): Owner: "Ok just use Everygen but be careful with the credits": Everygen is back for campaign clips. Search at most 1 hour of a stream per batch, finish at most 2 clips, check the balance before/after and report the credits spent.
- 2026-11-20: Owner: "remember we have to use all everygen credits before it restarts or we lose them". Account
  (Nov 20 22:40 UTC): plan pro_l_yearly, period ends 2027-11-13; subscription allowance 500/500 already USED (0 left);
  the 987 remaining are PURCHASED credits. Everygen's expiry rule for purchased credits isn't public/visible from here
  (everygen.ai is blocked; searches found nothing): get the real expiry date from the Everygen billing page and plan
  spend to finish before it. Still: estimate first, check balance before/after, log every spend in content/channels.md.
  Downloads (download_video) cost 0 credits (tested 3x Nov 20). Prices: image 2, 5-s Kling 3.0 Turbo video 10,
  find_clips on a stream ~2-12. Vice Replay may use AI only for images/intros, never as gameplay footage.
  Owner's billing page (screenshot, Nov 20): Pro plan renews Nov 13 2027; plan credits 0/500, RESET Dec 12 (monthly,
  unused don't carry over); top-up credits 987, NEXT EXPIRY FEB 17. The account spent plan credits before top-ups, so:
  every credit spent before Dec 12 comes from the expiring 987. Target: use most of the 987 by Dec 12, then each month's
  500 plan credits within that month, and whatever top-up is left before Feb 17 (~2,000 credits total by Feb 17).
- 2026-11-19: Instagram connected for Reels posting: @vice.replaytv (IG_USER_ID 17841454790873754, env var), Meta System User token for graph.facebook.com saved as a network secret (never expires; permissions instagram_basic, instagram_content_publish, instagram_manage_comments). Reels posting ON: owner said "ok aprove all post and add the ones in youtube or new ones" (Nov 19): every approved/auto-posted English Short also goes to Instagram Reels, plus campaign clips (LACY), spaced about 1-1.5 h apart via content/learn/reels_queue.json.
- 2026-11-19: Owner: LACY (campaign) Reels go out two at a time, at times Claude picks, so one submit trip covers both.

- 2026-11-19 5:49 PM: Meta emailed "Your professional ad account is restricted from advertising" for vice.replaytv
  (can't create/run ads, can't use audiences; posting unaffected). Response: Instagram slowed to max 4 posts/day
  (enforced in studio.instagram_upload), tonight's 3 Reels moved to Fri/Sat. No ad review requested (we run no ads).

- 2026-11-20: Added silent clips `media/trailer/extended-look-*` (10 kept) (6 s, 1080p) cut from Rockstar's official
  "GTA VI: An Extended Look" (rockstargames.com/VI/downloads), each reviewed second by second: driving, skyline, swamp
  airboat, skydive, night drive. Left out: shootings/robbery/heist, drug lab, swimsuit/club shots, a bloody close-up,
  the VI logo. "GTA VI Out Now" skipped (logos and club shots). Gameplay Drive pull fixed: files now download
  through drive.usercontent.google.com (the doc-*.googleusercontent hosts are blocked by the cloud proxy).
- 2026-11-20: Removed extended-look-city-drive-sedan: a full-size check showed two people leaning out of the car
  with guns (getaway scene). Lesson: review new clips at full size (360 px+), not thumbnails.
- 2026-11-20: Added 8 more official gameplay clips from "An Extended Look" (18 total): convertible-overpass,
  convertible-waterfront, downtown-highway, van-residential, aerial-bay, dirt-bike-trail (2.8 s), night-street-race
  (2.8 s), sunset-skyline (2 s). Each checked first/middle/last frame at full size and trimmed off the next scene
  (club, gym, the bloody close-up, Rockstar title card). Rotate clips so no two Shorts in a day open the same way.
- 2026-11-20: Google Docs connector connected: the shared Channel Map
  (https://docs.google.com/document/d/1t4jj7h1Pnodnys_SAeS7V5xLIVY0Ryls7g23E1mquJs) is edited IN PLACE from now on;
  the Nov 19 copy is renamed "OLD Channel Map (Nov 19)". Never re-upload a new copy.
- 2026-11-20: Owner asked "check all facts before posting" (applies to every video): verify each claim against 2+
  reliable sources (or read it off the footage at full size) right before upload, and fix loose wording.
- 2026-11-21: New official media (rockstargames.com/VI/media, each viewed first): 3 clean shots from the Nov 19
  "Out Now" video (`media/trailer/out-now-marina-ferris-wheel`, `-yacht-bay`, `-night-drive-ocean-drive`; left out: Rockstar
  and GTA logos, "Play/Out Now" cards, club dancing, a close-up of a woman's body, a pink-lit room, character close-ups),
  the official Leonida map poster (`media/official/leonida-map-poster.jpg`) and 38 Ultimate Edition screenshots (cars,
  boats, Rideout Customs, Sara's Salon, Stock 305, Wyman car collection, Vice City style). EXCLUDED Ultimate Edition
  shots: both revolver shots, weapon variants, the PTT store (man holding a gun), two Electric Fang tattoo-parlor
  shots (balaclava pose, bat/pipe), the Squalo swimwear shot, Stock 305 #4 and Vice City Style #3/#5 (revealing poses).
  Nov 22: `jason-and-lucia-ultimate-02.jpg` (Lucia on the green car holding a revolver at her hip) had slipped into
  media/official; removed (found while checking the Lucia outfits Short at full resolution).
- 2026-11-21: Channel profile improved (owner: "continue to do improvement to the channel"): new description and
  keywords (daily morning news, streamer stories, quizzes, map comparisons; not-affiliated line kept; old text in
  content/archive/channel-profile-before-2026-11-21.json), homepage sections added (Streamer & Breaking News, Shorts,
  Popular uploads, News & Guides), searchable playlist descriptions; title swaps run on 3 underperformers.
- 2026-11-21 (5:50 PM ET): channel trailer for non-subscribers set to the how-long video rHaMTePDRUQ ("GTA 6 Is Almost
  Twice as Long as GTA 5 (No Spoilers)"); there was none before. Swap it for a better long video when one exists.
- Spanish channel (ready to switch on, Nov 21): every Short already gets a Spanish-voice version (`<name>-es.mp4`)
  that was never posted. To start "Vice Replay en Español": (1) YouTube -> your profile -> Settings -> Add or manage
  channels -> Create a channel (name it "Vice Replay en Español"); (2) on the Mac run tools/youtube_auth.py and pick
  the NEW channel on Google's screen; (3) save the printed refresh token as YT_ES_REFRESH_TOKEN in the environment
  settings; (4) tell the main chat "Spanish channel connected": it runs `python -m studio.youtube_es whoami`, puts the
  id in config/channel.json, then posts approved Shorts with `python -m studio.youtube_es episodes/<slug>.json
  --approve short,news`. It refuses to post if the token belongs to the English channel.
- 2026-11-21 (night): owner created "Vice Replay en Español" and saved YT_ES_REFRESH_TOKEN in the vice-replay-studio
  environment (sign-in script with --es; first try hit invalid_client from a pasted client ID, fixed by putting the
  ID in the command). Next: `studio.youtube_es whoami` -> channel_id in config, then the Day 1 Spanish Shorts.
- 2026-11-22 approval (owner, 12:20 AM ET: "ok do it start making the channel but the spanish one started it will all
  the new upgrades just the best not the old"): post the 7 Spanish launch Shorts in content/spanish-channel.md
  ("Launch lineup") on Vice Replay en Español, re-rendered with animated captions, 2-3 a day in the morning slots,
  Nov 22-24. Anything else on that channel still needs an "approve".
- 2026-11-22 (owner: "do it now"): the main chat started helper session_01CJRsWNc23ARSJyE58DXbiL "🇪🇸 Vice Replay en
  Español: launch" because only a new session sees YT_ES_REFRESH_TOKEN. Exception to "helpers never post": it may
  post ONLY the 7 approved Spanish launch Shorts + their pinned questions on the Spanish channel, commits to
  claude/spanish-launch, and reports back. Once the main chat's container reloads, Spanish posting returns here.
- 2026-11-22 (owner: "continue to monitor and manage both channels with all the upgrades"): Vice Replay en Español
  (UCWPnqYqYu9_CLsJ8Bk1MPgQ) is connected. From now on an owner "approve" for an episode's Shorts also posts their
  Spanish versions on the Spanish channel, same slots (`studio.ship --upload` does it; `--no-es-upload` skips).
  Long videos stay English-only. Spanish key: YT_SPANISH_REFRESH_TOKEN (wins) or YT_ES_REFRESH_TOKEN.
- 2026-11-22 (1 AM ET): the saved keys were swapped (YT_REFRESH_TOKEN = Spanish channel, YT_ES_REFRESH_TOKEN =
  English, YT_SPANISH_REFRESH_TOKEN = Spanish). Since commit 7434d93 every tool picks the key by the channel it
  belongs to, so it works anyway; the health check shows a 🟡 until the settings are tidied (owner, when awake:
  English key in YT_REFRESH_TOKEN, Spanish key in YT_SPANISH_REFRESH_TOKEN, delete YT_ES_REFRESH_TOKEN).
- 2026-11-22 (8 AM ET, owner "Ok" to the schedule review): (1) Lucia outfits Short moves up from Wed 9:30 AM to
  **Mon Nov 23 12:30 PM (English)** and **Mon 8:30 PM (Spanish**: the Spanish 12:30 slot has the map Short); (2) the
  39 s ranking Short QzFhpT4dNVQ is unscheduled (private, kept) and its IG Reel skipped; the re-cut
  `episodes/gta6-top-3-rides.json` (~17 s, top 3) takes **Wed Nov 25 9:30 AM** (EN + ES); (3) the GTA 5 money Short
  (gta6-this-week-launch `tips`, `es_only` in the episode) goes to the **Spanish channel only**, Mon 3:30 PM. The
  Mon 3:12 / 3:20 AM reminders were written before this: follow this entry. The Mon 12:40 PM ranking-comment
  reminder is void (that video won't be public).
- 2026-11-22 (8:40 AM ET, owner "find upgrades"): races Short sP1fq11WMmw moved from Sun 5 PM to **Thu Nov 26 11:00 AM**
  (2-6 PM posts: median 2.7 views/h vs 16 for 6-11 AM); its IG Reel moved to Thu 11:05; Sun 5:10 PM comment reminder void.
- 2026-11-22 (9:15 AM ET, owner: "I want to try making videos like that from now on... graph, real evidence based.
  Start taking off the ones not going to get views and changing them for this"): from now on Shorts are built on
  our own graphs of checked numbers (studio/charts.py), trailer footage only as cutaways. Unscheduled (private, kept):
  M7oKevOPY08 "hidden EASY MODE" (Tue 12:30) and sP1fq11WMmw "races" (Thu 11 AM); their IG Reels and comment
  reminders are void. Replacements: `gta6-99-club` (Metacritic graph) **Tue Nov 24 12:30 PM EN / 11:00 AM ES**;
  `gta6-trailer-views` (Rockstar trailer view counts) **Wed Nov 25 12:30 PM EN + ES**; the Spanish money Short is now
  `gta6-money-chart-es` (es_only, Mon 3:30 PM ES) and gta6-this-week-launch `tips` is `replaced_by` it. Uploads: Mon
  3:07 AM (money ES) and Tue 3:10 AM (99 club + trailers), after each day's quota reset.
- 2026-11-22 (10 AM ET, owner: "change the video for the ones that will have more views and start changing the system
  to match"; "use the best voice rated"): voice -> Kokoro af_heart (grade A) in config/channel.json for every new
  render (Spanish stays em_alex); Lucia, top-3 rides, 99 club and trailer views re-rendered with it. The 33 s map Short
  9ZmygQdJRBA (Tue 11 AM) is unscheduled and replaced by `gta6-cheapest-gta-inflation` (GTA 6 is the cheapest GTA after
  inflation, our BLS CPI math): **Tue Nov 24 11:00 AM EN, Wed Nov 25 11:00 AM ES** (upload Tue 3:20 AM). System:
  studio/vice/viewcheck.py now BLOCKS a Short that is narration over trailer footage only (needs a `chart` or owner
  gameplay; an owner-approved `originality` note waives it, e.g. Lucia montage, top-3 rides).
- 2026-11-20 open owner items: ~~publish the Google OAuth app + reconnect YouTube before ~Nov 24~~ (DONE Nov 22 for Vice
  Replay EN + ES; What If Arena still to reconnect in its own chat); add both repos to the
  routines (claude.ai/connect-github) so breaking-news/daily runs can push; decide AI-voice label on/off; approve the
  next Everygen batch ("make the rest", ~64 credits); KreekCraft GTA 6 Twitch link for a campaign clip; record gameplay.
- 2026-11-22 (11 AM ET, owner: "start deleting videos that don't have the needed views and learn from it" -> "OK do it as
  you say, don't delete"): set PRIVATE (not deleted, reversible in Studio): 3T1de9Fnygg (Is Out: Do This Before You
  Play, 0), PJgR2lmq_Nc (Beginner Tips long, 2), RmONg7-uN4w (Physical Edition long, 8), MIvka1jBpJ0 (Not Enough Space
  long, 25), 6QbWET74cQs (settings, 5), acNIOalmWzM (money cheat, 9), RAs1Sx_7Zh8 (won't connect, 28), LHTxGyakWyI
  (dog, 33), 2MOr9zSDyfM (Chaos Is Coming, 43). Kept public on purpose: the 3 LACY campaign clips under 50 views
  (submitted to the campaign) and 3 long videos the website embeds (vJDnv7_7Hcs launch checklist, YqnShunG7WY best
  settings, GjhaJdjHR4Q map size). Lessons -> .claude/commands/daily-video.md "NOV 22 FLOP REVIEW".

- 2026-11-22 (owner): the shared Google Cloud project "What If Arena" (OAuth app, renamed "Creator HQ"; Branding uses
  vicereplay.com/, /privacy/ and /terms/) is now PUBLISHED ("In production"): new refresh tokens no longer expire after
  7 days. Keys made while it was in Testing still expire (~Nov 24): reconnect Vice Replay (English + Spanish) and What
  If Arena once, then write the date to content/learn/youtube_connected.txt.
- 2026-11-22 (afternoon, owner: "update all our info with the ideas we came up with today and continue to think of how to
  improve them"): (1) the new keys are loaded in the main chat (YT_REFRESH_TOKEN = English, YT_SPANISH_REFRESH_TOKEN =
  Spanish; YT_ES_REFRESH_TOKEN is gone); both verified. (2) Title fixes, no other change: top-3 rides is now "GTA 6 top 3
  rides: No. 1 isn't the convertible" and trailer views "GTA 6's first trailer STILL wins (309M views)" / ES "El PRIMER
  tráiler de GTA 6 sigue ganando (309 M) 🎬": their "#1" would have become a hashtag and the publish check would have
  stopped Monday's and Tuesday's uploads. (3) The inflation Short's middle chart is now a LINE (GTA 3 2001 -> GTA 6 2026,
  same numbers, axis from $70 stated), so the four graph Shorts don't share one layout; re-rendered EN + ES. (4) Spanish
  versions of 99 club, trailer views and inflation now show Spanish chart words (`chart_es`); re-rendered. (5) New:
  `python -m studio.flops` (48 h flop review, list first; `--apply` in the main chat), scorecard groups by picture and
  opener, publish-check warnings for repeated layouts, English chart words in Spanish versions and chart dates 3+ days
  old. Docs updated: README, INDEX, episode-format, playbook, topic bank, ideas (next graph Shorts + unbuilt ideas),
  docs/vice-system.md, Channel Map.
- 2026-11-22 (6:30 PM ET, owner: "check for updates or new system upgrades or anything new that could help"): found
  (1) YouTube Partner Program entry bar doubles for new channels on Feb 1, 2027 (1,000 subs + 8,000 h or 20M Shorts
  views in 90 days; details in content/learn/lessons.md), shared in the Channel Map for all 3 channels; (2) Shorts
  series (YPP only) and image carousels in the Shorts feed (owner posts from the phone); (3) news leads: Rockstar
  interviews (IGN) and Randy's Wish List car locations (content/learn/ideas.md). Built: `quote` chart type (animated
  quote card) so interview and streamer-quote Shorts are original without footage. No unmerged work on other branches.
- 2026-11-22 (6:45 PM ET, owner "do what you think" to my option 1 for the darts Short): `gta6-no-darts` (quote cards:
  Rob Nelson / Rockstar North to VGC, darts and bowling cut, pool in) uploads Mon 3:40 AM for **Mon Nov 23 11:00 AM
  EN + ES**; the quiz Short I2VEKQUia8w moved from Mon 11:00 to **Wed Nov 25 11:00 AM** (its Mon 11:10 comment reminder
  is void; new one Wed 11:10). Website: /guides/gta-6-darts/ and /es/guias/dardos-gta-6/ published. Randy's Wish
  List guide held until sources agree on the car count (16-22). Uploader: the key check now retries brief network
  errors (2 of 6 checks had failed with "no saved key belongs to channel").

