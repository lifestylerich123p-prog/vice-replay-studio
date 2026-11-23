# Vice Replay Studio

The video machine for **Vice Replay** (@ViceReplayTV-q8s), a GTA 6 fan channel, and the builder for
**vicereplay.com**. Claude researches, scripts, renders, learns from YouTube, and (after you approve) uploads.

## Your day (Miami time)
| When | What happens | Your part |
|---|---|---|
| 5:13 AM | Daily run: learns from YouTube, pulls Drive gameplay, makes the day's Shorts on our own graphs of checked numbers (English + Spanish voice), writes the website guide, updates the review page (long video only on Sunday: the weekly recap) | Phone notification |
| Morning | [Review page](https://claude.ai/artifact/DWvVW2BQrHZP9Xfs5Ve17Q): watch, check titles and comment replies | Reply **"approve"** in that chat |
| After approval | Uploads + schedules on Vice Replay AND Vice Replay en Español (Shorts in the daytime slots 9:30 / 11:00 / 12:30; 3:30 / 8:30 PM only for big news or the Sunday recap), posts comment replies, posts pinned comments once live | Pin comments, "Related video" on Shorts, thumbnails B/C |
| 8:23 AM-11:23 PM every 3 h (to Nov 30) | Breaking-news check; auto-posts only big, confirmed news | Nothing |
| 1:13 PM, 9:13 PM | Auto-replies to new comments (skips trolls/spam) | Nothing |
| 2:04 AM | Uses the rest of the day's YouTube quota before the 3 AM reset: uploads approved Shorts early (scheduled for their slots) and answers every comment on both channels (`python -m studio.spend`) | Nothing |
| 2:47 PM | Momentum check: a follow-up Short when one takes off | Approve it in the main chat |
| Sundays | Main video = weekly recap; 11:37 AM upgrade scout (its "reconnect YouTube" line is out of date: the Google app is published, keys no longer expire) | Nothing |
| Up to 4 times a day | Instagram @vice.replaytv: each uploaded Short as a Reel and ~1 carousel or image post a day (max 4 posts/day, ~2.5 h apart; no campaign clips after Meta's Nov 19 ad flag) | Nothing |
| A few times a day | Campaign check (GTA 6 campaigns only; others go to ClipCircuit; Content Rewards budgets, KreekCraft/Lacy footage); campaign clips from Twitch clip links you paste | Post the clip on YouTube, submit within 30 min |
| Anytime | TikTok videos + captions go to the "📱 Vice Replay: TikTok files" chat | Post them by hand |
| Anytime | Ask "how are we doing?" = `python -m studio.status` (one screen of everything); "check all systems" = `studio.doctor` + `studio.status` + tests | Nothing |
| 48 h after each Short | Flop review: `python -m studio.flops` lists public Shorts under 50 views after 48 h; the main chat sets them PRIVATE (never deleted) and logs the pattern in lessons | Nothing |

Commands: `/new-video <topic>`, `/stats` (+ Studio screenshot), `/reply-comments`, `/campaign-clips <name>`,
`/publish-site` (website updates).

## Folders
| Folder | What's in it |
|---|---|
| `studio/` | The machine: `ship.py` (one command: render everything + check sheet + upload), `replies.py` (comment replies), `scorecard.py` (what works, fair 24 h numbers), `moments.py` (which streamer moments are taken), `tidy.py` (automatic cleaner + `content/INDEX.md` map), `make_video.py` (videos, Shorts, `--es` Spanish voice), `youtube_upload.py` (approved uploads, comments, replies), `learn.py`, `radar.py`, `review_page.py`, `gameplay.py`, `clip.py`, `channel_fix.py`, `sound.py`, `brand.py`; `status.py` (one-screen status), `doctor.py` (health), `instagram_upload.py` (Reels/carousels + queue), `ig_cards.py` (carousel cards), `campaign_sources.py` (new footage for approved campaigns), `campaign_inbox.py` (free Drive clip inbox), `twitch_clips.py` (top Twitch clips per campaign streamer), `dashboard.py`, `retention.py`, `title_swap.py`; Nov 22: `charts.py` (our animated graphs: bars, counter, line), `flops.py` (48 h flop review), `retag.py` (search tags on videos already up), `channel_layout.py` (both channels' home pages), `quota.py` (YouTube units + free slots), `youtube_es.py` (Spanish channel) |
| `episodes/` | One script per video (JSON) |
| `studio/vice/` | The research-to-video system (`python -m studio.vice <command>`): audit, discover, scan, clip, rank, create, batch, analyze, campaigns, report, publish, rights. See `docs/vice-system.md` |
| `config/` | `channel.json` (destinations + channel separation), `providers.json` (what's connected), `budgets.json` (spend + quota guard), `sources.json` (authorized footage) |
| `rights/` | `registry.json`: one rights record per source class; anything unmatched is blocked |
| `research/` | `competitors/` (competitor research), `campaigns/` (campaign scans + registry); cached results |
| `projects/` | Clip projects (rights, transcript, captions, QC report, publication draft; media not committed) |
| `database/` | `vice.db` (SQLite): snapshots, candidates, projects, QC, costs, payouts, ideas, fingerprints |
| `reports/` | Audit, scan, report, 14-day calendar (`calendar.md/.csv`); `exports/` CSV/JSON (not committed) |
| `tests/` | `python -m pytest tests -q` |
| `docs/` | `vice-system.md`: how the system works, what's connected, limits |
| `site/` | Website data: `guides/*.json` (guide pages written by the daily run) and `live.json` (launch live updates) |
| `tools/` | `site_guides.py` builds vicereplay.com into the sibling `vicereplay-site` repo; `youtube_auth.py` reconnects YouTube |
| `content/` | The machine's memory: `episode-format.md` (how to write an episode), `owner.md` (settings, links, standing approvals), `launch-plan.md`, `log.md`, `performance.md`, `learn/` (incl. `reels_queue.json`, `status.md`, `health.md`, `uploads.json`), `affiliate.json`, `campaigns/` (one JSON per campaign, `tracker.md`, scans), `carousels/` (Instagram carousel specs); `archive/` holds finished one-off files |
| `media/official/` | 175 official GTA 6 screenshots incl. 37 Ultimate Edition shots (strip-club and weapon-focus shots excluded); `media/gameplay/` is pulled from Drive, not committed |
| `assets/` | Fonts, profile picture; voice model and music are generated/downloaded, not committed |
| `.claude/commands/` | The routines behind each command and the daily run |
| `resources/` | Reference pack: Shorts/TikTok playbook, hooks and titles, topic bank, capture guide, upload checklist, tools (channel rules in CLAUDE.md win) |
| `output/` | Rendered videos, `clips/<campaign>/` campaign clips, `carousels/<slug>/` cards (not committed) |

## Website (vicereplay.com, repo `vicereplay-site`)
GitHub Pages + Cloudflare (DNS, contact@vicereplay.com, Web Analytics) + Google Search Console.
Pages: home, `/gear/` (affiliate), `/guides/` (English guides incl. launch live), `/es/` (Spanish guides), `/links/` (bio link), `/contact/`, `/privacy/` + `/terms/` (Nov 22: needed to publish the shared Google app "Creator HQ").
To change it: edit `site/` or `tools/site_guides.py`, run `python tools/site_guides.py`, push both repos.

## Settings (cloud environment `vice-replay-studio`)
- Network secret for `www.googleapis.com` (read-only YouTube key) and `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (English uploads), `YT_SPANISH_REFRESH_TOKEN` (Vice Replay en Español). Google Cloud project **"Vice Replay"** (ID `what-if-arena`, number 662880770567; renamed Nov 22) with the OAuth app "Creator HQ", client "Vice Replay uploader": published, so keys don't expire after 7 days; `tools/youtube_auth.py` only if a key is revoked. What If Arena has its own project ("What If Arena API") since Nov 22, so the daily YouTube quota is Vice Replay's alone (English + Spanish channels share it). Quota plan: `content/youtube-quota-plan.md`.
- Allowed hosts: Google/YouTube APIs, Google Drive, Hugging Face, Rockstar's site, vicereplay.com, plugin servers.

## How a Short is built now (Nov 22 data; details in `content/episode-format.md`)
- **Original first**: YouTube's Oct 2026 update ranks original Shorts higher and says narration over reused footage
  isn't original. Every Short is built on our own `chart` graphics (bars, counter, line, quote card) of numbers and words we checked, or the
  owner's gameplay; trailer clips only as 1-2 s cutaways. `studio.vice publish` blocks a trailer-only Short.
- **Hook**: the first sentence states the surprising result (3-10 words), never a question (statement openers kept 60%
  of viewers vs 35%); a number in the first headline; 35-55 words (13-20 s), never 76+.
- **Titles**: "GTA 6" + the subject first, 40-45 characters before `#GTA6 #Shorts`, no "#1"-style numbers (YouTube turns
  them into hashtags; the publish check blocks it), 8-15 topic tags.
- **Variety**: don't repeat the same picture order (counter > bars > counter > clip) in a row; the check warns.
- **Spanish**: every chart with words gets a `chart_es` (Spanish label/note); numbers switch to 3.790,5 style.
- **Voice/music**: Kokoro `af_heart` (English) / `em_alex` (Spanish); our synthwave theme by mood.

## Rules that keep the channel safe
No licensed music · official screenshots and your own gameplay only (campaign footage only for approved campaigns) ·
"not affiliated with Rockstar" in every description · no spoilers · nothing uploaded without your approval
(except breaking news that passes every rule) · every video has a real angle. Full rules: `CLAUDE.md`.
