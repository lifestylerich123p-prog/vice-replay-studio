# Vice Replay system (built Nov 20, 2026)

The research-to-video system from the owner's "Growth & Automation System V1" brief, built on top of the existing
studio (which already rendered, uploaded, learned and posted). New code lives in `studio/vice/`; the brief's folders
map onto the repo like this:

| Brief | Here |
|---|---|
| `config/` | `config/channel.json`, `providers.json`, `budgets.json`, `sources.json` |
| `research/` | `research/competitors/`, `research/campaigns/` (+ cache table in the database) |
| `rights/` | `rights/registry.json` (source of truth, mirrored into the database) |
| `assets/`, footage, music | existing `assets/`, `media/official/`, `media/trailer/`, `media/gameplay/` |
| `src/research-agent` | `studio/vice/research.py` (`discover`), `analytics.py` (`audit`) |
| `src/clip-discovery`, `source-verification` | `studio/vice/discovery.py` (`scan`), `dedupe.py` |
| `src/rights-checker` | `studio/vice/rights.py` |
| `src/clip-ranking` | `studio/vice/scoring.py` |
| `src/story-editor`, `caption-engine`, `renderer` | `studio/vice/editor.py` (clips), `studio/make_video.py` (narrated) |
| `src/quality-inspector` | `studio/vice/qc.py`, `factcheck.py` |
| `src/metadata`, `publisher` | `studio/vice/__main__.py publish`, `channels.py`, existing `studio/ship.py` + `youtube_upload.py` |
| `src/analytics` | `studio/vice/analytics.py`, `report.py`, existing `scorecard.py`, `retention.py` |
| `projects/`, `database/`, `reports/`, `tests/`, `docs/` | same names |

## Commands

`python -m studio.vice <command>` (or `/vice <request>` in chat):

| Command | What it does | Cost |
|---|---|---|
| `audit` | Public stats + YouTube Analytics (views, engaged views = "stayed to watch", % viewed, avg duration, subs, shares, traffic sources) by series; fair 24 h comparisons; flags videos to investigate | free (~5 quota units) |
| `discover` | Seed competitor videos, their channels, latest 50 uploads each, 3 discovery searches; breakouts; title structures (trend only with 3+ channels) | free (~350 units, cached 24 h) |
| `scan` | Authorized stream replays + "moments in circulation" (signals only) + owner gameplay moments; dedupe; rights status; already-used check | free (~800 units, cached 6 h) |
| `clip SRC ...` | Rights -> cut -> transcript -> render (layout, captions from the audio, punch-in, labelled replay, loudness) -> cover -> QC -> draft; resumable | free (local) |
| `rank` / `create` | Episode skeleton with authorized footage; research then `studio.ship` | free |
| `batch` | Next ready ideas from the 14-day calendar | free |
| `analyze VIDEO` | QC report with timestamps and fixes | free (local) |
| `campaigns` | Registry, eligibility, payout math (estimated vs approved vs received) | 1 unit |
| `report` | One page + CSV/JSON exports of every table | free |
| `publish EPISODE` | Publication draft: QC + rights + channel/token check + cover + titles | 1 unit |
| `rights [ASSET --dest D]`, `fingerprint`, `calendar` | registry, published-footage fingerprints, plan | free |

Nothing in `studio.vice` uploads. Publishing stays as CLAUDE.md says: the owner replies "approve" in chat, then
`studio.ship --upload`.

## Guarantees built in

- **Rights gate, default deny.** No rights record = blocked. Campaign footage only for its campaign's destination
  (ClipCircuit, per the owner's Nov 20 rule), never with AI voice or logos when the campaign bans them. A high
  opportunity score never overrides the gate.
- **Channel separation.** `config/channel.json` lists what each channel accepts; drafts are refused for the wrong
  channel, and for API uploads the token's channel ID must match the destination.
- **No reposts.** Every published file we still have is fingerprinted (one frame per second, 64-bit dHash).
  A video sharing 70%+ of its frames with a published one fails QC; 35-70% is a stock-reuse warning.
  Calibrated on our clips: a re-captioned, punched-in, replay-extended re-edit matched its original 100%; different
  clips matched 0-27%.
- **Facts.** Numbers, records, "confirmed"/"official" sentences need sources; rumor wording next to "confirmed"
  fails; spoilers, sexual content and leaks in a title fail.
- **Append-only metrics** and timestamped research cache; every quota/paid call is logged in `costs`.
- **Low memory** (MacBook Air 16 GB): one render at a time; clip renders run in passes (a single concat graph and
  zoompan both ran away and were OOM-killed during testing; replaced).

## What is connected (Nov 20) and what is missing

Works: YouTube Data API, YouTube Analytics (owner OAuth, Vice Replay only), YouTube upload, Kokoro voice,
faster-whisper (local), ffmpeg, Everygen via MCP (paid; owner's yes required), Instagram Graph, Content Rewards pages
via search.

Missing / blocked:
- **vidIQ**: no vidIQ tool in this session; the owner's vidIQ login authorizes What If Arena only. Competitor and
  outlier research uses the free YouTube API instead.
- **Twitch API**: no TWITCH_CLIENT_ID/SECRET, and twitch.tv is not on the network allowlist.
- **youtube.com / kick.com / whop.com pages**: blocked by the network policy, so stream VODs can't be downloaded here
  and competitor videos can't be watched (no claims about their editing).
- **Owner gameplay**: the Drive gameplay folders are empty; 10 of the 28 calendar ideas wait for recordings.
- **Copyright claims, CTR/impressions, revenue**: no API access for this channel (check YouTube Studio).
- **Remotion**: not used; ffmpeg covers the effects with less memory.

## Sample tests (Nov 20)

1. **Streamer reaction** (`projects/test1-lacy-car-key/`): authorized Lacy campaign footage, re-edited with
   transcript captions, punch-in at the payoff and a labelled 0.75x replay. Rendered in 28 s locally, $0.
   **Blocked by design**: QC found it is the same footage as the Nov 19 post (9QNojUuqHtc) and the visual review found
   double captions (the only Lacy footage on disk is an already-captioned clip). A publishable streamer clip needs a
   fresh moment from the raw stream (Everygen ~2-12 credits with the owner's yes, or the free Drive inbox).
2. **Original gameplay analysis** (`episodes/gta6-race-hud-details.json`): "Vice Replay Details", the race HUD in
   Rockstar's gameplay read frame by frame (5/6 -> 3/6, PROGRESS %, LAP 1/2, 10/12). Magnifier freeze frames,
   callout rings, honest slow motion, Kokoro narration, Spanish version. Rendered in ~3 min, $0. QC passed
   (1 warning: 53% of its shots also appear in earlier Shorts). Awaiting the owner's approval.

## Stage 2 (Nov 20, evening): starter kit merged + next-stage features

**Architecture decision.** The owner's starter kit (`starter/vice_replay_starter/`, kept unchanged with its 8 passing
tests) is a clean, standard-library scaffold: per-file rights with proof files, explicit commercial/YouTube flags,
candidate scoring, fit/fill render, QC, draft packages. The main repo already had far more (narrated renders, Spanish
voice, uploads with approval, learning, Instagram, the rights gate and QC from stage 1). Running two systems would split
data and rules, so the starter's model was ported INTO `studio.vice` and extended, and its command names work there:

| Starter | Now | Why it's better |
|---|---|---|
| `sources` table, proof file, flags | `studio/vice/sources.py`: same fail-closed rules + SHA-256 of the file and the proof (a swapped or edited file is blocked), a destination scope per source, `campaign`/`policy` statuses tied to the campaign files and the class registry | provenance you can audit; channel separation enforced per file |
| (none) | `rights_audit`: every rights decision, append-only (SQLite triggers refuse UPDATE/DELETE) | "auditable rights source" success criterion |
| `render --layout fit/fill` | `studio/vice/framing.py`: `stack` (webcam on top, gameplay below, webcam kept out of the gameplay panel), `pip`, `fill` (crop that follows the action, smoothed), `blur` (whole frame over a blurred fill: no empty bars), `auto` (detects the webcam) | facecam and action both visible; `fit` left half the screen empty |
| manual crop coordinates | `--cam/--game x y w h` first; otherwise YuNet face detection (OpenCV, MIT model, 232 KB) on 12 frames: a face that stays put = the webcam, then its borders are found as edges present in EVERY frame | measured on mock streams: IoU 0.98 and 0.96 with the true webcam box; no false webcam on plain gameplay |
| (none) | `keep` boxes: a campaign's required overlay (e.g. KreekCraft's logo) stays visible: the crop slides a little to include it, else it's composited back as an inset | campaign compliance by construction |
| `add-captions` (manual SRT) | local faster-whisper transcript -> `captions.srt` (editable) + `captions_review.md` listing words under 60% confidence; the publication draft stays BLOCKED until `approve-captions` (which rebuilds the captions from the edited SRT) | accurate, editable, reviewed before release |
| QC (vertical? duration?) | full inspector (black/frozen/bars/silence/loudness/decode/caption WER/repost fingerprints/rights/facts) | catches what actually breaks videos |
| `package` | `package` / `publish`: draft with channel + token check | never uploads; destination verified by channel ID |
| status (JSON) | `status` + the local control dashboard | one place to run and watch jobs |

**Narrated Shorts (studio/make_video.py).**
- Captions are timed to the real speech: faster-whisper word timestamps on the narration, matched to the script with
  difflib; unmatched words are interpolated; weak matches fall back to the old estimate. Measured on the race-HUD Short:
  the old character-count timing was off by 0.23 s on average and up to 0.86 s; aligned captions follow the voice.
  Works for the Spanish voice too.
- Pacing: a segment can list `shots` (media/start/speed/focus/dur) and the background cuts between them.
- Scene-cut guard: a warning when a segment's background runs past a shot change inside its source clip (that's how
  the ranking Short briefly showed a man on a porch over "the airboat" before the fix).
- Already present and kept: sidechain ducking of music under the voice, -14 LUFS loudness.

**Control dashboard.** `python -m studio.vice dashboard` -> http://127.0.0.1:8765 (localhost only). Channel numbers,
the 14-day queue (Create buttons for ready ideas), episodes (Render, QC + draft), clip projects (Resume, Approve
captions), jobs with logs, rights decisions, campaigns, costs. Jobs run one at a time from an allowlist; a per-session
token blocks other websites from triggering jobs; interrupted jobs are re-queued on restart. No upload button.

**New tests:** `tests/test_next_stage.py` (framing accuracy, webcam exclusion, no empty bars, provenance + hash
tampering, proof changes, append-only audit, the starter workflow end to end on the new engine, caption alignment,
dashboard allowlist + recovery). Run everything: `python -m pytest tests -q` and
`cd starter/vice_replay_starter && python -m unittest discover -s tests`.

**Researched, not adopted:** WhisperX (heavy torch install; faster-whisper alignment is enough for our own narration),
stable-ts (archived May 2026), ctc-forced-aligner (default model non-commercial), Ultralytics webcam models (AGPL),
pyautoflip default face model (InsightFace weights non-commercial), arnndn denoise models (GitHub download blocked here).
YouTube facts that matter: custom Shorts thumbnails are only for Partner Program channels (so the first frame stays the
cover); "Related video" has no API field; since Oct 1 2026 Shorts recommendations favour originals over re-uploads.

### Tested on real stream footage (Nov 20, late)

- **Everygen downloads are free**: three download calls, balance 987 credits before and after. A YouTube part of up
  to ~20 s comes back within the tool's 60 s limit (a 60 s part takes ~2 min and times out, though it isn't charged).
  Campaign footage is saved in `media/campaign/<campaign>/` (git-ignored) and registered with `add-source --rights campaign`.
- **KreekCraft**: no GTA 6 stream replays on his YouTube channel (last 50 uploads and recent streams are Roblox); his
  GTA 6 streams are presumably on Twitch, which this environment can't list. No KreekCraft clip possible from here yet.
- **Webcam detection on a real Lacy stream** first failed (the box snapped to his head: he barely moves, so his outline
  looked like a border; the real webcam touches the frame edges). New primary method: a webcam is a region that stays
  still while gameplay changes (pixel std 2.4 inside vs 40.7 outside); grow from the face while the strip outside is
  still. Result: IoU 0.97 with the hand-measured webcam; mock streams still 0.98 / 0.96 (edge method as fallback).
- **Repost check**: on real clips, full-frame fingerprints called every Lacy clip "the same footage" because his
  webcam room fills the top of every frame. Now a repost needs BOTH full-frame match AND a match of the moving pixels
  only (static pixels ignored): the re-edited car-key clip is still blocked, a new moment from another minute is not.
- **Loudness**: clip renders now use two-pass loudnorm (one pass left a stream clip at -17.6 LUFS; now -14.8).
- **Known gap**: the full-height action-tracking crop centres on the frame when the whole picture moves (camera moving),
  which can cut off a third-person character standing left of centre. OpenCV 5 dropped its built-in person detector;
  `auto` therefore prefers the webcam-on-top layout, which handled this footage well.

## Stage 3 (Nov 22): original-first Shorts and the views check

Why: YouTube's Oct 1, 2026 Shorts update ranks original Shorts higher and says narration over reused footage isn't
original; our own data (content/learn/hooks-2026-11-22.md) showed which hooks, lengths and slots work.

- **Our own graphics** (`studio/charts.py`): `chart` segments render bars (a leaderboard that grows), counters (one
  number or two with VS), lines (a trend that draws itself) and quote cards (exact words, word by word, then who
  said them), each on its own gradient so chart videos don't
  fingerprint alike. `chart_es` gives the Spanish render Spanish words; Spanish renders format numbers 3.790,5.
- **Views check** (`studio/vice/viewcheck.py`, part of `publish`). Blocks: a Short that is narration over trailer
  footage only (no chart, no owner gameplay, no owner-approved `originality` note); a question as the first sentence;
  76+ words; a still first picture with no motion; "#" + a number in any title (YouTube makes it a hashtag). Warns: no
  number in the first headline, a title core over 45 characters, an opener over 14 words, 56-75 words, a plain tip, no
  tags (EN/ES), English chart words in the Spanish version, the same picture order as one of the last 4 uploads, and a
  chart note dated 3+ days ago.
- **Repost check and our charts**: frames from our own chart segments count as "never a match", so a graph Short is
  never called a repost of an old title card (`dedupe.overlap(..., own=...)`); retired uploads aren't compared.
- **Scorecard** (`studio/scorecard.py`): Shorts are also grouped by picture (graph / owner gameplay / trailer and
  screenshots, read from the episode file via content/learn/uploads.json) and by opener (statement / question), so the
  graph-Short switch is measured with the same DO MORE / DO LESS rule (3+ Shorts per group).
- **Flop review** (`python -m studio.flops`): public Shorts under 50 views 48 h after going public; `--apply` (main chat)
  sets them private (never deleted), marks uploads.json `hidden` and logs their pattern in lessons.md. Campaign clips,
  website embeds and the Spanish channel are never touched.
- **Schedule** (`studio/quota.py` reads the gate's slots from config/channel.json): English 8:00 AM + 6:00 PM, Spanish 12:30 PM + 7:00 PM ET, max 2 a day each (owner Phase 10).
- **Tags** (`studio/youtube_upload.clean_tags`, `studio/retag.py`): 8-15 topic tags per upload within YouTube's 500
  characters; `retag` fixes videos already up.
- **Both channels** (`studio/youtube_es.py`, `studio/channel_layout.py`): every approved Short also posts on Vice Replay
  en Español; each channel's home page links the other.
