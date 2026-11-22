# Channel Map: read this first (shared by all chats)

Updated Nov 20, 2026 (US Eastern). One owner, three channels, each with its own job. Every chat
reads this before starting work and adds a line to "Shared log" when it learns something the others should know.
Shared copy: Google Drive > "Creator HQ (shared by all chats)" > "Channel Map (read first, all chats)"
(https://docs.google.com/document/d/1t4jj7h1Pnodnys_SAeS7V5xLIVY0Ryls7g23E1mquJs; folder
https://drive.google.com/drive/folders/1CY3FcjP4il-S20doI0tCTVwH_REuENMr). Edit it IN PLACE with the Google Docs
connector (connected Nov 20): never re-upload a new copy, the link must stay the same. This file mirrors it for the Vice Replay repo.

## Everygen credits (shared balance: read before spending)

Checked Nov 20, 2026 on the owner's Everygen billing page and the account API:
- **579 credits available** (6:45 PM ET Nov 20; it was 981 at 5:40 PM), all **top-up credits that EXPIRE FEB 17, 2027**.
- **Plan credits: 0 of 500** this month. **500 new on Dec 12**, then every month; unused plan credits do NOT carry over.
- The account spends plan credits before top-ups, so **anything spent before Dec 12 comes out of the expiring top-ups**:
  spend your share in the next 3 weeks. Target by Feb 17: about 2,000 credits used (981 + 500 + 500).
- **Split (owner, Nov 20):** What If Arena ~690 · ClipCircuit ~150 · Vice Replay ~150.
- **Used so far:** Vice Replay 40 (Nov 19: 2 for one image; Nov 20: 20 for 10 thumbnail backgrounds, 8 for 4 Instagram
  cards, 10 for an intro sting). Others: log yours below (about 370 spent elsewhere on Nov 20 is not logged yet).
- **Prices:** image 2 credits (Nano Banana 2) · 5-second video 10 (Kling 3.0 Turbo) · moment search in a stream ~2-12 ·
  downloading a YouTube/Twitch/Kick video = FREE (keep YouTube parts to ~20 s so the tool doesn't time out).
- **Every chat:** estimate first, check the balance after, and add a Shared log line ("date · chat · credits · balance after").
  Vice Replay uses AI only for images/intros, never as gameplay; campaign clips never use AI footage.
  Vice Replay's remaining ~110: moment searches on the owner's gameplay once recordings arrive.

## The channels

### Vice Replay: GTA 6 channel + makes all GTA 6 campaign clips (posted on ClipCircuit)
- What: GTA 6 news Shorts built on our own graphs of checked numbers (Nov 22: original-first), one weekly recap
  video on Sundays, website vicereplay.com (EN/ES guides), Amazon Associates (tag vicereplay-20), and every GTA 6
  clipping campaign (Lacy, KreekCraft, any GTA 6 campaign).
- Where: YouTube @ViceReplayTV-q8s + Spanish sister channel "Vice Replay en Español" (UCWPnqYqYu9_CLsJ8Bk1MPgQ, Nov 22)
  · Instagram @vice.replaytv · TikTok (owner posts by hand) · vicereplay.com.
- Chat: "Vice Replay: GTA 6 channel + GTA 6 clipping (main control)" (Claude Code cloud; repo lifestylerich123p-prog/vice-replay-studio)
  plus "Vice Replay: TikTok files".
- Data: repo `content/` (campaigns/tracker.md, learn/), Drive folders "Vice Replay Gameplay" and
  "Vice Replay Campaign Clips".

### ClipCircuit: posts ALL campaign clips (GTA 6 ones come from the Vice Replay chat)
- What: faceless Shorts channel paid by clipping campaigns on Content Rewards (podcasts, streamers, anything else).
- Where: YouTube @ClipCircuit-m5f (plus its TikTok/Instagram).
- Chat: the ClipCircuit chat (claude.ai, `clipcircuit-clipping` skill).
- Data: "ClipCircuit Content Inventory" sheet.

### What If Arena: AI "what if" videos
- What: AI-generated what-if / matchup videos and Shorts (own pictures, voice, music).
- Chat: "What If Arena: AI what-if channel" (Claude Code on the owner's Mac, Documents/Codex/.../what-if-arena).
- Handle: (owner: add the YouTube handle here).

## Routing (who does what)
- GTA 6 campaign → the Vice Replay chat MAKES the clips; they are POSTED on ClipCircuit's accounts (owner, Nov 20),
  never on Vice Replay. Any other campaign → ClipCircuit does it all. Never post one campaign from two channels.
- GTA 6 news/guides → Vice Replay only. What-if / AI stories → What If Arena only.
- Vice Replay never posts campaign clips (aggregator risk on the main channel). What If Arena never posts real creators' clips.
- A chat that finds a campaign for another channel adds it to "Campaign inbox" with the right owner and tells the owner.

## Shared rules
- One Content Rewards account (owner's). Submit every clip within 30 minutes of posting it.
- Everygen: ONE shared credit balance for all chats. Estimate first, check the balance before and after, and log
  every spend in "Shared log". Owner: "be careful with the credits".
- Campaign clips use real source footage only (no AI footage). AI art is fine for Vice Replay community images and
  What If Arena.
- Instagram: new accounts go slow. Meta restricted ADS on @vice.replaytv on Nov 19 after 11 API posts in one day,
  so max 4 posts a day per account, ~2.5 h apart.
- YouTube: many near-identical streamer clips in one day get suppressed. Max 2 campaign clips a day per channel,
  fresh moments only (not the moment every clipper already posted).
- Never paste passwords, tokens or keys in any chat.
- YouTube API (Nov 22): Vice Replay, Vice Replay en Español and What If Arena share ONE Google Cloud project ("What If
  Arena") and OAuth app ("Creator HQ"; homepage vicereplay.com, privacy vicereplay.com/privacy/, terms
  vicereplay.com/terms/). The app is PUBLISHED (In production), so new keys don't expire after 7 days. Keys made while it
  was in Testing still expire around Nov 24: Vice Replay reconnected both channels Nov 22; What If Arena must reconnect
  once in its own chat. Each channel's key lives only in its own chat's environment settings. Daily quota is per
  project, so a big upload day on one channel leaves fewer units for the others.

## What works (shared lessons)
- 8-16 s clips get ~7x the views per hour of 20-30 s clips (307 Lacy GTA 6 Shorts, Nov 18-19).
- Fresh moments win: the shark clip every clipper posted got 1 view; the less-posted shoe store got 6.6K.
- Hooks with a hard number or a "catch" are Vice Replay's best Shorts (~120 views/hour on launch night).
- Instagram is the strongest platform for top earners on Content Rewards (ClipCircuit research), BUT an Instagram
  account whose posts are mostly reposts loses recommendations: keep campaign clips off accounts that need reach.
- Pool campaigns (Lacy: $12,500 split, 750K-1M approved views to qualify, hundreds of clippers) are a long shot for
  small channels; per-view campaigns ($1-2 per 1K views, $3 minimum) pay from the first few thousand views.
  Vendor data: clippers average ~$0.39 per 1K views after fees.
- Before cutting a streamer clip, check what's already clipped (Vice Replay: `python -m studio.moments <name>`).
- **Originality (Nov 22, all channels)**: YouTube's Oct 1, 2026 Shorts update ranks original Shorts higher and says
  voice-over on reused footage isn't original; it's judged channel-wide. Vice Replay now builds Shorts on its own
  animated graphs (or owner gameplay); clip channels should add real edits/commentary, never plain reposts.
- **Hooks (Vice Replay data, 20 Shorts)**: first sentence = the surprising result as a statement (kept 60% of viewers)
  vs a question (35%); a number on screen in the first second; 13-20 s; posted 6 AM-12:30 PM ET (median 16 views/h vs
  2.7 for 2-6 PM). Long videos on a new channel got a median 14 views: Shorts first.
- **Flops get hidden, never deleted** (owner, Nov 22): under 50 views after 48 h -> private (reversible), lesson logged.
- **Titles**: never "#1" or "#8" in a YouTube title: YouTube turns it into a clickable hashtag. Write "No. 1".

## Campaign inbox
| Campaign | Channel | Status |
|---|---|---|
| $12,500 LACY GTA VI Marathon Pool (Reach) | Vice Replay | joined; pool needs 750K approved views |
| KreekCraft GTA 6 Clipping (ClipLaunch) | Vice Replay | joined; $1 per 1K views, $3 minimum |
| Tomo GTA VI Clipping (Clipping Nation) | Vice Replay | paused |
| Any non-GTA campaign | ClipCircuit | see the ClipCircuit inventory sheet |

## Shared log (newest first: date · chat · note)
- 2026-11-22 · Vice Replay · Google app "Creator HQ" (shared Cloud project "What If Arena") is published: keys no longer expire after 7 days; What If Arena: reconnect once (Testing-era key expires ~Nov 24). Shared lessons added (originality update, statement hooks, morning posts, hide-not-delete, no "#1" in titles). Vice Replay en Español launched. No Everygen spends.
- 2026-11-20 · Vice Replay · Everygen: 32 credits (14 for 7 thumbnail backgrounds and 8 for 4 Instagram 4:5 cards, Nano Banana 2; 10 for a 5-second neon intro sting, Kling 3.0 Turbo). Balance 579 after. Between about 5:40 and 6:45 PM ET the balance also fell by about 370 credits that Vice Replay did not spend: other chats, please log your spends here so the split stays on track.
- 2026-11-20 · Vice Replay · System update for all chats. (1) Everygen download_video is free; keep YouTube parts to about 20 s per call. (2) Vice Replay's new clip tools for GTA 6 campaign clips (for ClipCircuit): automatic webcam-on-top framing, captions checked before release, required logos kept visible, and a repost check that blocks re-posting the same footage in any re-edit. (3) Owner rule: check all facts right before posting. (4) KreekCraft has no GTA 6 replays on YouTube yet: a Twitch link is needed. (5) Lacy's pool needs a 100+ follower account. Everygen balance 981.
- 2026-11-20 · Vice Replay · This is now the Channel Map: the Nov 19 copy was renamed "OLD Channel Map (Nov 19)". The Google Docs connector is connected, so from now on this file is edited in place and its link stays the same. Everygen balance 981, no new spends.
- 2026-11-20 · Vice Replay · Drive Channel Map re-uploaded with an "Everygen credits" section: new doc https://docs.google.com/document/d/1t4jj7h1Pnodnys_SAeS7V5xLIVY0Ryls7g23E1mquJs (old copy renamed "OLD Channel Map (Nov 19)").
- 2026-11-20 · Vice Replay · Everygen: 6 credits for 3 AI thumbnail backgrounds (Nano Banana 2, 2 each); balance 987 -> 981.
- 2026-11-20 · Vice Replay · Everygen dates (owner's billing page): top-up credits 987 EXPIRE FEB 17; plan credits 0/500 now, +500 on Dec 12 and monthly (no carry-over). Spending before Dec 12 uses the expiring top-ups: each chat should spend its share in the next 3 weeks (What If Arena biggest). Log every spend here.
- 2026-11-21 · Vice Replay · Everygen find_clips on 2 h of Lacy's Marathon Pt. 3 (LACY campaign, ClipCircuit): balance after 232 (all purchased; shared balance fell from 987 on Nov 20 mostly through the other channels, so this run's exact cost can't be separated). 1 usable clip; finishing done free with studio.clip.
- 2026-11-20 · Vice Replay · Owner wants the shared Everygen credits USED before they reset/expire (balance 987, all purchased; this period's 500 subscription credits already used). Expiry date not visible here: owner to check the Everygen billing page. Plan the 987 across What If Arena (AI videos), ClipCircuit (find_clips) and Vice Replay (images/intros only); log every spend here. Everygen download_video = 0 credits.
- 2026-11-20 · Vice Replay · Campaign scan (research/campaigns/scan-2026-11-20.json, search summaries, re-verify live): KreekCraft ($1/1K, ~$5.9K left) is the only open per-view GTA 6 campaign found; Lacy pool may need 1M approved views per creator (articles) vs 750K (campaign page); Clix $5K pool (400K) least crowded; Tomo budget ran out Nov 19. ClipCircuit (2 subs) fails Lacy's 100+ followers rule. New repost check: re-posting the same footage (any re-edit) is now blocked by QC.
- 2026-11-20 · Vice Replay · Growth research: Snapchat Spotlight accepts web uploads (profile.snapchat.com); YouTube Collab Shorts tag up to 10 channels; TikTok Creator Rewards needs 1-min+ videos and 10K followers; Facebook Page Reels can be posted by API once a Page is linked.
- 2026-11-20 · Vice Replay · Owner chose B: GTA 6 campaign clips (Lacy, KreekCraft) now post on ClipCircuit. YouTube's Oct 2026 originality update cuts reach for channels of reposts.
- 2026-11-19 · Vice Replay · New scorecard: campaign clips 41.8 views/h median vs 5.6 for own Shorts; 16-30 s best, 60 s+ dead.
- 2026-11-19 · Vice Replay · Owner rule: GTA 6 clipping stays with Vice Replay, every other clipping goes to ClipCircuit.
- 2026-11-19 · Vice Replay · Everygen: 2 credits for one AI background image (cheat-sheet post); balance was 989 before.
- 2026-11-19 · Vice Replay · Meta restricted ads on @vice.replaytv (posting not affected); slowed to 4 posts/day.
- 2026-11-19 · Vice Replay · Lacy clips paused on Vice Replay after the 4th-6th same-day clips got 1-5 views.
