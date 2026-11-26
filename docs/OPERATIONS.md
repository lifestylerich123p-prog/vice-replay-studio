# Vice Replay operations (publishing, recovery, daily loop)

Since Nov 26, 2026 (owner: directive v2.0 + "Autonomous publishing authorization update"). Read with `CLAUDE.md`.

## The publishing gate (`studio/approvals.py`)
An English Short publishes automatically at its slot only when **all 10 conditions** pass right before upload:

| # | Condition | How it's checked |
|---|---|---|
| 1 | Facts verified | 2+ sources in the episode, and a re-check stamped within 2 days of the slot (`python -m studio.approvals factcheck episodes/<slug>.json --note "..."`, stored in `content/learn/factchecks.json`) |
| 2-5 | Spoilers/safety/copyright, visual/technical defects, narration vs captions, audio | `python -m studio.vice publish` (rights registry, fact flags, QC: black/frozen frames, loudness, captions vs speech, hooks) + 1080x1920, audio stream, 8-60 s |
| 6 | Title + description final | rendered `.txt` title = the episode's title, "GTA 6" first, <= 100 chars, description present |
| 7 | No duplicate | registry (`uploads.json`) by slug/item and exact title; the uploader re-checks every GitHub branch and the channel's own list (`studio/postguard.py`) |
| 8 | Real value / plan | a map card (location guide), a how-to/tutorial, or an episode marked `"experiment": true` |
| 9 | Tests pass | `python -m studio.approvals tests` passed on the current code (hash of `studio/` + `tools/`) within 36 h |
| 10 | Limits | `config/channel.json` `auto_publish.on`, slot in the future and one of `slots` (EN 8:00 AM / 6:00 PM, ES 12:30 PM / 7:00 PM), at most `max_per_day` (2) a day per channel |

States: RESEARCHED → VERIFIED → PRODUCED → RENDERED → QA_PASSED → AUTO_APPROVED → (UPLOADING) → SCHEDULED →
PUBLISHED. BLOCKED = must be fixed; NEEDS_REVIEW = held until a person or the next run decides; FAILED = upload error.
Only the transitions in `ALLOWED` are accepted (nothing jumps from RENDERED to UPLOADING).

The approval is bound to a **content fingerprint** (script, cards, pins, sources, description, pinned comment, series
number, voice-file bytes). Any change after AUTO_APPROVED → NEEDS_REVIEW until evaluated again.

## Phase 3 tools (owner Nov 26, "Data-driven growth and autonomous optimization")
| Need | Command | Notes |
|---|---|---|
| Unattended run saves its work | `python -m studio.runsafe preflight daily` / `checkpoint daily -m ".." --step ..` / `recover` | own branch `claude/daily-<date>`, SHA-256 manifest in content/runs/, retries network errors only; the 5 AM run fires into the helper session "🎬 Vice Replay: daily run" |
| Main chat takes the helper's work | `python -m studio.runsafe inbox` then `merge <branch>` | refuses on a manifest hash mismatch |
| Everygen money | `python -m studio.credits show` / `record --remaining N ...` | VERIFIED only from a provider reading < 24 h old with no spend since; otherwise UNVERIFIED + labelled estimate |
| Follow-ups of winners | `python -m studio.opportunities` | 3x+ matched baseline per platform; candidates in content/learn/map-candidates.json; map intelligence agent rules |
| Cross-platform numbers | `python -m studio.xplat` | each platform vs its own baseline; formats that work on 2+ platforms |
| Content mix vs targets | `python -m studio.mix` | targets in config/channel.json `content_mix` |
| Spanish voice check | `python -m studio.voice_eval` | pace, clipping, pauses, Whisper match, GTA terms; dictionary config/pronounce-es.json |
| Map demo footage | `node tools/record_map_demo.js ../vicereplay-site <page> <search> <pin> media/site/<name>.mp4` | our own site, 1080x1920, slow-motion capture |
| Map styles | map chart `"style"`: zoom / route / steps / area | content/episode-format.md |

Render freshness is per language (`studio/renderdeps.py`, `<video>.inputs.json`): an English-only edit no longer makes the
Spanish video stale; a title/description change only needs `make_video ... --meta-only`. The gate checks the SHA-256 of
the exact file that passed QA right before uploading, and only auto-publishes at the plan's slot times.

## The daily loop (scheduled runs)
| ET | Run | What it does |
|---|---|---|
| 2:04 AM | Nightly prep (trig_019pesiorLpAZ6Nkd8bExXDY) | fact re-checks for tomorrow's two Shorts (stamp only if 2+ sources still agree), comment replies on both channels; uploads nothing |
| 3:45 AM | Publishing run (trig_01DpEa4hojQ9uFfxLbMLq7xF) | `python -m studio.spend upload`: numbers the map series, re-renders stale videos, runs the tests if the code changed, evaluates each Short, uploads AUTO_APPROVED ones scheduled for 8 AM / 6 PM; reports holds |
| 5:13 AM | Daily video (trig_018e2bAmbskJfRQUY5DkEmDD) | research + a new candidate (hands files to the main chat) |
| 1:05 PM | Daily report (trig_013tmcD9vz8dUNRShCpwjMdk) | `approvals verify` (public on YouTube? → PUBLISHED), pinned comments, TikTok files (EN + ES), numbers, one message to the owner |
| 2:47 PM | Momentum (trig_01BDJUjM9FysWFCqmPJsfA4s) | a taking-off Short → a follow-up candidate |
| 8/11/2/5/8/11 | Breaking news (trig_01MTxMGMgd8nF44C6VxmmFHZ, to Nov 30) | report only |

## Recovery
- **Upload error / timeout**: the record goes to FAILED. The next run asks YouTube first (postguard): found → SCHEDULED
  with that id; not found → AUTO_APPROVED again and sent once. Never re-upload blindly.
- **Two failures in a row**: auto-publishing pauses itself (`approvals status` shows why). Fix, then
  `python -m studio.approvals resume`.
- **Emergency stop**: `python -m studio.approvals pause "why"`.
- **Missed slot**: never posted automatically; move the item to a new slot in `content/learn/approved_queue.json`.
- **Held video**: `python -m studio.approvals status` lists every BLOCKED/NEEDS_REVIEW reason; fix the cause (re-render,
  re-check facts, change format), it is evaluated again at the next run.
- **Never run two `studio.ship` at once**: each ends by deleting its work folders and running `studio.tidy`.

## Platforms
- English YouTube: automatic through the gate.
- Spanish YouTube: not auto-published; paused until Dec 3 (`spanish_youtube_paused_until`), review then.
- TikTok: the owner posts by hand from the `tiktok-files` branch (English + Spanish files, 1 PM report).
- Instagram: existing queue (`content/learn/reels_queue.json`, max 4/day), Reels only of uploaded Shorts + about one
  carousel a day.

## Quota
`videos.insert` is billed to its own uploads bucket (1 unit, 100 uploads/day per project) per the 2026 quota docs as
summarised by several API guides (Google's own page could not be opened from the cloud session; confirm in Google
Cloud Console → APIs → YouTube Data API v3 → Quotas). The general 10,000-unit pool now only pays for playlists,
comments, thumbnails, reads and searches. `studio/quota.py` and `studio/spend.py` were updated Nov 26.

## Phase 7 operational settings: where each one lives (no duplicate config files)
| Area (owner Phase 7 #33) | Where it is set |
|---|---|
| channels, autonomous publishing, slots, caps, emergency stop | config/channel.json `auto_publish`, `auto_publish_es` (`python -m studio.approvals pause/resume`) |
| fact / rights / identity / hash-bound authorization / duplicates / calendar | studio/approvals.py (10 conditions), studio/sources.py (`claims_required_from`), studio.calcheck |
| affiliate marketing (account, properties, tracking ID, disclosures, compat, rules) | content/affiliate.json + studio/affiliate.py |
| comments | studio/comments.py, ledger content/learn/our-comments.json |
| website | tools/site_guides.py, site/*.json, studio/sitelinks.py |
| credits (fresh balance, reservations, buffer 5, no purchases) | studio/credits.py, studio/everygen_claim.py |
| analytics (separate channels/platforms, review ages 1/24/72/168/672 h) | studio/xplat.py, studio/learn.py, content/learn/searchconsole-*.json |
| security (no secrets in git, least privilege) | .gitignore, environment network secrets, docs/WEBSITE-ANALYTICS.md token scopes |
| business monitoring | python -m studio.cycle, studio.status, studio.doctor, 1 PM report |
