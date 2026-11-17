# Vice Replay Studio

The video machine for **Vice Replay** (@ViceReplayTV-q8s), a GTA 6 fan channel.
Claude researches, scripts, renders, learns from YouTube, and (after you approve) uploads.

## Your day
| When (Miami time) | What happens | Your part |
|---|---|---|
| 5:13 AM | Daily run: learns from YouTube, pulls Drive gameplay, makes 1 video + 2 Shorts + 3 thumbnails, updates the review page | Phone notification |
| Morning | [Review page](https://claude.ai/artifact/DWvVW2BQrHZP9Xfs5Ve17Q): watch, check titles | Reply **"approve"** in that session |
| After approval | Uploads + schedules everything (main 3:30 PM, Shorts 6:00 / 8:30 PM weekdays), not made for kids; posts the comments after each goes live | Pin the comments, set "Related video" on Shorts, add thumbnails B/C (Test & Compare) |
| Nov 18-20, 12:23 + 5:23 PM | Launch-week breaking-news check: a Short to post right away, only if big news | Post it |
| Sundays 11:37 AM | Upgrade scout: 3 upgrade ideas + next week's plan | Tell Claude what to build |
| Anytime | Drop gameplay clips in the Drive folder (5 category subfolders) | Record with radio/music at 0, mic off |

Commands in Claude Code: `/new-video <topic>`, `/stats` (+ YouTube Studio screenshot), `/reply-comments`,
`/campaign-clips <name>` (approved campaigns only; you post those and submit within 30 minutes).

## How it's built
| Folder / file | What it does |
|---|---|
| `studio/make_video.py` | Script JSON -> video + Shorts: free Kokoro voice, screenshots/gameplay, word-by-word captions, original music + sound effects, thumbnails A/B/C, description with chapters |
| `studio/learn.py` | Live stats of our uploads + the hottest GTA 6 videos on YouTube -> `content/learn/` |
| `studio/review_page.py` | Builds the phone review page |
| `studio/youtube_upload.py` | Uploads approved videos and schedules them; `--comment` posts comments once public |
| `studio/gameplay.py` | Pulls clips from Google Drive and cuts the best moments into `media/gameplay/` |
| `studio/clip.py` | Highlight clipper for approved clipping campaigns and long recordings |
| `studio/sound.py`, `studio/brand.py` | Original music/SFX and the Vice Replay look |
| `episodes/` | One script per video (JSON) |
| `content/` | Owner settings, content plan, video log, performance + lessons (the machine's memory), campaigns |
| `media/official/` | 51 official GTA 6 screenshots (strip-club shots excluded) |
| `tools/youtube_auth.py` | One-time YouTube upload connection (run on your Mac; redo every 7 days while the Google app is in Testing) |
| `.claude/commands/` | The routines behind each command and the daily run |

## Settings (cloud environment `vice-replay-studio`)
- Network secret for `www.googleapis.com` (`X-Goog-Api-Key`, path `/youtube/v3/`): read-only YouTube key for learning.
- Environment variables `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`: upload permission.
- Allowed hosts: Google/YouTube APIs, Google Drive, Hugging Face (caption model), Rockstar's site (screenshots), plugin servers.

## Rules that keep the channel safe
No licensed music (no GTA radio/trailer songs/score) · official screenshots and your own gameplay only, never
other creators' footage (except approved campaigns) · "not affiliated with Rockstar" line in every description ·
no spoilers in titles/thumbnails · nothing is uploaded without your approval · every video has a real angle.
Full rules: `CLAUDE.md`.
