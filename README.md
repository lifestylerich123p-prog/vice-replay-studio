# Vice Replay Studio

The video machine for **Vice Replay** (@ViceReplayTV-q8s), a GTA 6 fan channel, and the builder for
**vicereplay.com**. Claude researches, scripts, renders, learns from YouTube, and (after you approve) uploads.

## Your day (Miami time)
| When | What happens | Your part |
|---|---|---|
| 5:13 AM | Daily run: learns from YouTube, pulls Drive gameplay, makes 1 video + Shorts (English + Spanish voice) + 3 thumbnails, writes the website guide, updates the review page | Phone notification |
| Morning | [Review page](https://claude.ai/artifact/DWvVW2BQrHZP9Xfs5Ve17Q): watch, check titles and comment replies | Reply **"approve"** in that chat |
| After approval | Uploads + schedules (main 3:30 PM, Shorts 6:00 / 8:30 PM weekdays), posts comment replies, posts pinned comments once live | Pin comments, "Related video" on Shorts, thumbnails B/C |
| 8:23 AM-11:23 PM every 3 h (to Nov 30) | Breaking-news check; auto-posts only big, confirmed news | Nothing |
| 1:13 PM, 9:13 PM | Auto-replies to new comments (skips trolls/spam) | Nothing |
| 2:47 PM | Momentum check: a follow-up Short when one takes off | Approve it in the main chat |
| Sundays | Main video = weekly recap; 11:37 AM upgrade scout + YouTube reconnect reminder | Reconnect YouTube |
| Every 1-1.5 h | Instagram @vice.replaytv: each uploaded Short as a Reel, campaign clips two at a time, ~1 carousel a day (tips / fun facts) | Submit campaign Reels within 30 min |
| A few times a day | Campaign check (Content Rewards budgets, KreekCraft/Lacy footage); campaign clips from Twitch clip links you paste | Post the clip on YouTube, submit within 30 min |
| Anytime | TikTok videos + captions go to the "📱 Vice Replay TikTok" chat | Post them by hand |
| Anytime | Ask "how are we doing?" = `python -m studio.status` (one screen of everything) | Nothing |

Commands: `/new-video <topic>`, `/stats` (+ Studio screenshot), `/reply-comments`, `/campaign-clips <name>`,
`/publish-site` (website updates).

## Folders
| Folder | What's in it |
|---|---|
| `studio/` | The machine: `ship.py` (one command: render everything + check sheet + upload), `replies.py` (comment replies), `tidy.py` (automatic cleaner + `content/INDEX.md` map), `make_video.py` (videos, Shorts, `--es` Spanish voice), `youtube_upload.py` (approved uploads, comments, replies), `learn.py`, `radar.py`, `review_page.py`, `gameplay.py`, `clip.py`, `channel_fix.py`, `sound.py`, `brand.py`; `status.py` (one-screen status), `doctor.py` (health), `instagram_upload.py` (Reels/carousels + queue), `ig_cards.py` (carousel cards), `campaign_sources.py` (new footage for approved campaigns), `campaign_inbox.py` (free Drive clip inbox), `twitch_clips.py` (top Twitch clips per campaign streamer), `dashboard.py`, `retention.py`, `title_swap.py` |
| `episodes/` | One script per video (JSON) |
| `site/` | Website data: `guides/*.json` (guide pages written by the daily run) and `live.json` (launch live updates) |
| `tools/` | `site_guides.py` builds vicereplay.com into the sibling `vicereplay-site` repo; `youtube_auth.py` reconnects YouTube |
| `content/` | The machine's memory: `episode-format.md` (how to write an episode), `owner.md` (settings, links, standing approvals), `launch-plan.md`, `log.md`, `performance.md`, `learn/` (incl. `reels_queue.json`, `status.md`, `health.md`, `uploads.json`), `affiliate.json`, `campaigns/` (one JSON per campaign, `tracker.md`, scans), `carousels/` (Instagram carousel specs); `archive/` holds finished one-off files |
| `media/official/` | 137 official GTA 6 screenshots (strip-club shots excluded); `media/gameplay/` is pulled from Drive, not committed |
| `assets/` | Fonts, profile picture; voice model and music are generated/downloaded, not committed |
| `.claude/commands/` | The routines behind each command and the daily run |
| `output/` | Rendered videos, `clips/<campaign>/` campaign clips, `carousels/<slug>/` cards (not committed) |

## Website (vicereplay.com, repo `vicereplay-site`)
GitHub Pages + Cloudflare (DNS, contact@vicereplay.com, Web Analytics) + Google Search Console.
Pages: home, `/gear/` (affiliate), `/guides/` (21 guides incl. launch live), `/es/` (Spanish), `/links/` (bio link), `/contact/`.
To change it: edit `site/` or `tools/site_guides.py`, run `python tools/site_guides.py`, push both repos.

## Settings (cloud environment `vice-replay-studio`)
- Network secret for `www.googleapis.com` (read-only YouTube key) and `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (uploads).
- Allowed hosts: Google/YouTube APIs, Google Drive, Hugging Face, Rockstar's site, vicereplay.com, plugin servers.

## Rules that keep the channel safe
No licensed music · official screenshots and your own gameplay only (campaign footage only for approved campaigns) ·
"not affiliated with Rockstar" in every description · no spoilers · nothing uploaded without your approval
(except breaking news that passes every rule) · every video has a real angle. Full rules: `CLAUDE.md`.
