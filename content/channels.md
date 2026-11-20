# Channel Map: read this first (shared by all chats)

Updated Nov 19, 2026 (owner: Javier, US Eastern). One owner, three channels, each with its own job. Every chat
reads this before starting work and adds a line to "Shared log" when it learns something the others should know.
Shared copy: Google Drive > "Creator HQ (shared by all chats)" > "Channel Map"
(https://drive.google.com/drive/folders/1CY3FcjP4il-S20doI0tCTVwH_REuENMr). This file mirrors it for the Vice Replay repo.

## The channels

### Vice Replay: GTA 6 channel + makes all GTA 6 campaign clips (posted on ClipCircuit)
- What: GTA 6 news, guides and tips (Shorts + long videos), website vicereplay.com (EN/ES guides), Amazon
  Associates (tag vicereplay-20), and every GTA 6 clipping campaign (Lacy, KreekCraft, any GTA 6 campaign).
- Where: YouTube @ViceReplayTV-q8s · Instagram @vice.replaytv · TikTok (owner posts by hand) · vicereplay.com.
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

## Campaign inbox
| Campaign | Channel | Status |
|---|---|---|
| $12,500 LACY GTA VI Marathon Pool (Reach) | Vice Replay | joined; pool needs 750K approved views |
| KreekCraft GTA 6 Clipping (ClipLaunch) | Vice Replay | joined; $1 per 1K views, $3 minimum |
| Tomo GTA VI Clipping (Clipping Nation) | Vice Replay | paused |
| Any non-GTA campaign | ClipCircuit | see the ClipCircuit inventory sheet |

## Shared log (newest first: date · chat · note)
- 2026-11-20 · Vice Replay · Everygen dates (owner's billing page): top-up credits 987 EXPIRE FEB 17; plan credits 0/500 now, +500 on Dec 12 and monthly (no carry-over). Spending before Dec 12 uses the expiring top-ups: each chat should spend its share in the next 3 weeks (What If Arena biggest). Log every spend here.
- 2026-11-20 · Vice Replay · Owner wants the shared Everygen credits USED before they reset/expire (balance 987, all purchased; this period's 500 subscription credits already used). Expiry date not visible here: owner to check the Everygen billing page. Plan the 987 across What If Arena (AI videos), ClipCircuit (find_clips) and Vice Replay (images/intros only); log every spend here. Everygen download_video = 0 credits.
- 2026-11-20 · Vice Replay · Campaign scan (research/campaigns/scan-2026-11-20.json, search summaries, re-verify live): KreekCraft ($1/1K, ~$5.9K left) is the only open per-view GTA 6 campaign found; Lacy pool may need 1M approved views per creator (articles) vs 750K (campaign page); Clix $5K pool (400K) least crowded; Tomo budget ran out Nov 19. ClipCircuit (2 subs) fails Lacy's 100+ followers rule. New repost check: re-posting the same footage (any re-edit) is now blocked by QC.
- 2026-11-20 · Vice Replay · Growth research: Snapchat Spotlight accepts web uploads (profile.snapchat.com); YouTube Collab Shorts tag up to 10 channels; TikTok Creator Rewards needs 1-min+ videos and 10K followers; Facebook Page Reels can be posted by API once a Page is linked.
- 2026-11-20 · Vice Replay · Owner chose B: GTA 6 campaign clips (Lacy, KreekCraft) now post on ClipCircuit. YouTube's Oct 2026 originality update cuts reach for channels of reposts.
- 2026-11-19 · Vice Replay · New scorecard: campaign clips 41.8 views/h median vs 5.6 for own Shorts; 16-30 s best, 60 s+ dead.
- 2026-11-19 · Vice Replay · Owner rule: GTA 6 clipping stays with Vice Replay, every other clipping goes to ClipCircuit.
- 2026-11-19 · Vice Replay · Everygen: 2 credits for one AI background image (cheat-sheet post); balance was 989 before.
- 2026-11-19 · Vice Replay · Meta restricted ads on @vice.replaytv (posting not affected); slowed to 4 posts/day.
- 2026-11-19 · Vice Replay · Lacy clips paused on Vice Replay after the 4th-6th same-day clips got 1-5 views.
