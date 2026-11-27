# End-of-night checkpoint: Thu Nov 26, 2026 (~9:30 PM ET)

Recovery point: git tag `checkpoint-2026-11-26-night` on vice-replay-studio and vicereplay-site (main). Rendered
videos (`output/`) are not in git: if this container is lost, the 3:45 AM run re-renders any missing or stale video
from its episode file before the gate (studio/spend.py `renders_needed`), and the gate re-checks it.

## Verified tonight (evidence: commands run, results in this session)
- `studio.doctor`: all green except "no claude/daily-2026-11-26 branch" (expected: the new helper run starts 5:13 AM Nov 27).
- Test suite: passed on the current code (`approvals.tests_ok()` = True; no studio/ or tools/ code changed tonight).
- `studio.cycle --date 2026-11-27`: PASS (queue, fact re-checks, renders current, right channel, right time, main
  pushed, no duplicates, analytics, cost) / WAIT (uploads at 3:45 AM, public at slot, helper run). Not OPERATIONAL yet.
- Map series: 26 booked spots (#5-#30) renumbered after reschedules, re-rendered, numbers + next-spot promises +
  descriptions checked against the schedule (`studio.mapseries show`: no stale numbers). Published videos untouched.
- Gate (AUTO_APPROVED, bound to the final file's SHA-256): Fri mask EN 8:00 AM, barber EN 6:00 PM, ninja ES 7:00 PM;
  Sat backrooms EN 8:00 AM + ES 7:00 PM, silent hill ES 12:30 PM, clothing stores EN 6:00 PM.
- Website: Xbox storage guide EN + ES live (200), canonical + hreflang correct, in the sitemap, no horizontal scroll at
  390 px, one tagged link (vicereplay-20) with the disclosure above it, linked from both SSD guides; IndexNow 200;
  `studio.site_stale`: 0 stale.
- Spending: 0 Everygen credits today; month: Vice Replay 10, What If Arena 10 (ledger reconciled with the provider
  balance; last verified balance 64, shared account). No purchases, subscriptions or ads.
- Affiliate: links only on vicereplay.com (listed); YouTube EN/ES + Instagram OFF until listed in Associates Central.

## Scheduled, NOT happened yet (no result until it runs)
| ET (Fri Nov 27) | Job | Expected |
|---|---|---|
| 2:04 AM | nightly prep (trig_019pesiorLpAZ6Nkd8bExXDY, CRON_TZ America/New_York) | fact re-checks + ledgers for the next 2 days, comment replies, no uploads |
| 3:45 AM | autonomous publishing (trig_01DpEa4hojQ9uFfxLbMLq7xF, CRON_TZ) | uploads only gate-approved Shorts, scheduled private with publishAt |
| 4:40 AM | cycle check 1 (trig_01F4QYmcmFMh6pZsjZ2up6WC, one-shot 09:40 UTC) | channel, privacy, publishAt, titles, duplicates |
| 5:13 AM | helper daily run (trig_01AQ4TgsmpD4BDUjmTeJxe1n, CRON_TZ) | branch claude/daily-2026-11-27 pushed |
| 6:30 AM | cycle check 2 (trig_01PYhhZenEnvS8hLFyykoCiy, one-shot 11:30 UTC) | helper branch, manifest, push |
| 8:00 AM | mask Short goes public (YouTube publishAt, set at 3:45 AM) | public on Vice Replay |
| 8:20 AM | cycle check 3 (trig_01HUshfFyT7iUWuEfeiGJzU3, one-shot 13:20 UTC) | OPERATIONAL only if every real check passes |

All one-shots are stored in UTC and were computed for EST (UTC-5); recurring jobs use CRON_TZ=America/New_York.
Full job list and tonight's 13 corrections: docs/AUTOMATION.md.

## Protections in place (unchanged tonight)
- One uploader for routine Shorts (3:45 AM run) through the gate; duplicate guard on every branch + YouTube; approval
  void if the episode or file changes; 2 upload failures in a row pause publishing; anything uncertain is held.
- Review/recommendation jobs (Dec 3, Dec 5, Dec 8, momentum, scout, breaking news) are report-only: they can't pause
  a channel or change slots/frequency.
- Paid Everygen calls need a fresh claim (hook in .claude/settings.json); Vice Replay produces with free voices.

## Sidebar organized (owner request, ~9:10 PM ET)
- Active sessions renamed "<emoji> <Project> · <role>" and tagged by project: 🎮 Vice Replay · Main control,
  🎬 Vice Replay · Daily helper run (5:13 AM), 📱 Vice Replay · TikTok files (tag vice-replay); 🧪 What If Arena · Shorts
  look + pipeline (what-if-arena); 💼 Business Portfolio · Autonomous income system (business-portfolio);
  🖥️ Mac + Claude cleanup (mac-setup). Titles/tags only: nothing in those sessions was changed.
- Archived (restorable with unarchive): the finished Spanish launch helper (its commits were already on GitHub, its
  TikTok files already sent) and the latest finished runs of breaking news, momentum, the Nov 26 1:13 PM
  comment-replies run and the Nov 22 scout (each checked: nothing pending for the owner). Older scheduled-run sessions can't be
  listed from here; archive them in the app (right-click a chat → Archive).
- Recurring jobs renamed "Vice Replay · <time ET> <what it does>" (names only; schedules and instructions unchanged).
- Repo folders already match README's folder map; tidy runs after every render. One-off files referenced by code
  were left in place (moving them would change code right before the first automatic run).

## Known, not blocking tonight
- Spanish Shorts carry the English series number ("LUGAR #N") and a line pointing to the English playlist: fix after
  the 8:20 AM verification (Phase 10 #4, with regression tests).
- Tattoo (EN Sun 6 PM) and Vice City (ES Mon 12:30 PM) wait for their nightly fact re-check (Sat/Sun 2:04 AM) before
  the gate can approve them; Vice City ES also needs its claims ledger (required from Nov 30).
- Old gate records for Little Cuba ES and mask ES say BLOCKED (from before earlier re-renders); both videos are current
  now and are re-evaluated when due.
- Cloudflare analytics: not measurable until the owner adds a read-only token (Account Analytics: Read).

## After the 8:20 AM verification passes (Phase 10, conditional)
1. CLAUDE.md + related files: EN 8:00 AM / 6:00 PM, ES 12:30 PM / 7:00 PM, max 2 each (list in docs/AUTOMATION.md).
2. Independent Spanish series numbering + no English playlist line in Spanish descriptions + regression tests.
3. Content mix 35 location / 25 numbered secrets / 20 map tutorials / 10 map-scale / 10 experiments.
4. Full Phase 10 report. If the verification fails: diagnose and fix that component first.
