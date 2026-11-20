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
