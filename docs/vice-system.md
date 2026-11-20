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
