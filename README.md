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
| Anytime | TikTok videos + captions go to the "📱 Vice Replay TikTok" chat | Post them by hand |

Commands: `/new-video <topic>`, `/stats` (+ Studio screenshot), `/reply-comments`, `/campaign-clips <name>`,
`/publish-site` (website updates).

## Folders
| Folder | What's in it |
|---|---|
| `studio/` | The machine: `tidy.py` (automatic cleaner + `content/INDEX.md` map), `make_video.py` (videos, Shorts, `--es` Spanish voice), `youtube_upload.py` (approved uploads, comments, replies), `learn.py`, `radar.py`, `review_page.py`, `gameplay.py`, `clip.py`, `channel_fix.py`, `sound.py`, `brand.py` |
| `episodes/` | One script per video (JSON) |
| `site/` | Website data: `guides/*.json` (guide pages written by the daily run) and `live.json` (launch live updates) |
| `tools/` | `site_guides.py` builds vicereplay.com into the sibling `vicereplay-site` repo; `youtube_auth.py` reconnects YouTube |
| `content/` | The machine's memory: `owner.md` (settings, links, standing approvals), `launch-plan.md`, `log.md`, `performance.md`, `learn/`, `affiliate.json`, `campaigns/`; `archive/` holds finished one-off files |
| `media/official/` | 51 official GTA 6 screenshots (strip-club shots excluded); `media/gameplay/` is pulled from Drive, not committed |
| `assets/` | Fonts, profile picture; voice model and music are generated/downloaded, not committed |
| `.claude/commands/` | The routines behind each command and the daily run |
| `output/` | Rendered videos (not committed) |

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
