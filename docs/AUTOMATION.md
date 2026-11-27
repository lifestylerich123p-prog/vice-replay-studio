# Scheduled jobs register (owner Phase 10 #5, audited Nov 26, 2026 9 PM ET)

One list of every scheduled job on the account, what it may do, and the rules it depends on. **When a rule changes
(slots, frequency, approvals, voices, budgets, long-form hold), update every job below that mentions it, in the same
session** (`list_triggers` → `update_trigger`), then update this file. Times are America/New_York; recurring jobs use
`CRON_TZ=America/New_York`, one-shots are stored in UTC (all dates below are EST, UTC-5; DST starts Mar 8, 2027).

**Canonical sources (don't restate numbers elsewhere, point here):**
- Publishing slots and caps: `config/channel.json` `auto_publish` (English 8:00 AM + 6:00 PM, max 2) and
  `auto_publish_es` (Spanish 12:30 PM + 7:00 PM, max 2). Owner Phase 10: slots are opportunities, not quotas.
- Gate conditions: `studio/approvals.py`. Mix targets: `config/channel.json` `content_mix` (`studio.mix`).
- Money: `studio.credits` (verified balance) + `studio.everygen_claim` (claim before any paid call).

## Recurring
| Job | When (ET) | Session | May do | Audit Nov 26 |
|---|---|---|---|---|
| trig_019pesiorLpAZ6Nkd8bExXDY nightly prep | daily 2:04 AM | main | fact re-checks + claim ledgers for the next 2 days' slots (both channels), comment replies; **no uploads** | OK |
| trig_01DpEa4hojQ9uFfxLbMLq7xF autonomous publishing | daily 3:45 AM | main | numbers the map series, re-renders stale videos, runs tests if code changed, uploads ONLY gate-approved Shorts (EN + ES) scheduled for their slot, title swap | OK (tonight's first real run; untouched) |
| trig_01AQ4TgsmpD4BDUjmTeJxe1n helper daily run | daily 5:13 AM | helper | research + 2 Shorts on branch `claude/daily-<date>`; never pushes main, posts or spends | OK |
| trig_011QXer4L5s5BHgWLNJwjm7i Spanish director | daily 10:23 AM | main | Spanish research/production 5 days ahead, books `es` slots, gate evaluation | **fixed**: hard-coded old mix → `content_mix`; Phase 10 Spanish priorities, measures, voice + hook recorded, no new paid voice |
| trig_013tmcD9vz8dUNRShCpwjMdk owner report | daily 1:05 PM | main | verify published, calendar, learning, merge helper branch, TikTok files, comments, one owner message | OK |
| trig_01BDJUjM9FysWFCqmPJsfA4s momentum | daily 2:47 PM | fresh | **report-only**: studio.opportunities → message to main chat | **fixed**: removed "owner replies approve" flow |
| trig_01T8agB7rbk9ewL6C1w314Zr comment replies | daily 9:13 PM | fresh | English comment replies only, commits replied.json | **fixed**: dropped the 1:13 PM run (duplicated the 1 PM report's replies) |
| trig_01MTxMGMgd8nF44C6VxmmFHZ breaking news | every 3 h, Nov 17-30 only | fresh | report-only | OK: owner Phase 10 lets it end Nov 30 |
| trig_01Ruh8nL2kasGH91G3capjhk weekly scout | Sun 11:37 AM | fresh | report-only: studio.learn, xplat, studio.competitors, monthly review | OK |
| trig_01XX9xXTp8xfb4i3yYUFP9uF website publish | when poked | main | site files only | **fixed**: removed "owner replies approve to upload" |

## One-shots (pending)
| Job | When (ET) | What | Audit |
|---|---|---|---|
| trig_01F4QYmcmFMh6pZsjZ2up6WC | Fri Nov 27 4:40 AM | cycle check 1: uploads (channel, private + publishAt, titles, duplicates) | OK (tonight's sequence) |
| trig_01PYhhZenEnvS8hLFyykoCiy | Fri Nov 27 6:30 AM | cycle check 2: helper branch, manifest, push | OK |
| trig_01HUshfFyT7iUWuEfeiGJzU3 | Fri Nov 27 8:20 AM | cycle check 3: first public Short, studio.cycle, OPERATIONAL only if all pass | OK |
| trig_01HwqcCiBWsmDf1GXvhrcedE, trig_01Y12eyikzuEkHbm1AWWABPi, trig_01DA4Zoif3McKksZLTW2MtMS, trig_01QBUiWPFjMkMCvh3SFkT61z, trig_01PxX9T56LpC14NtM5xAF7s1 | Fri Nov 27 9:40 AM-3:40 PM | comments via studio.comments + Instagram queue | OK (no affiliate links, never "pinned") |
| trig_01EFwJVu578x8XT6X5HTganb, trig_01PPq42LQyWEMHfkFPyW6vKE | Sat Nov 28 | comment + Reels | OK |
| trig_015mT45FFiKDa4AKJJT6FZdE | Sun Nov 29 4:01 PM | week-one carousel | **fixed**: hub video is on the long-form hold → skip quietly unless it's public |
| trig_01Rox7oBuHUUyMn5REqb1zpx | Mon Nov 30 2:10 PM | Paul Walker Reel | OK |
| trig_01YUGjSYwwnKbKpnPMopZdMC | Tue Dec 1 10:00 AM | ask about Pro mode | **fixed**: plan mode can't change the publishing schedule; content/plans.md updated (it named a deleted job and 3 Shorts/day) |
| trig_01EuQY1hN5ycSRvP1z1FHssQ | Tue Dec 1 3:10 PM | secrets map carousel | OK |
| trig_01KuHzVrZjbVMufPR3rmzKxM | Thu Dec 3 1:41 PM | Spanish one-week review | **fixed**: was going to set `spanish_youtube_paused_until` (pause); now report-only, can't pause |
| trig_01Bq6rDtaQNCaLLSFvH6orAF | Fri Dec 4 2:12 PM | long-form decision | **fixed**: Phase 10 #13 metrics (search impressions/views, CTR, watch time, retention, subs, referrals, costs, demand), whole-life data |
| trig_01DQVQWKrp4LFB2Xcye7HjAa | Sat Dec 5 1:46 PM | 8 AM slot review | **fixed**: compared 8 AM with slots that no longer exist; now 8 AM vs 6 PM, report-only |
| trig_017pWKfYD24hsjkuZvzKyHxE | Sun Dec 6 4:01 PM | Game Awards odds carousel | **fixed**: skip quietly while its long video is on hold |
| trig_01PvFza59EuBJ1Gsm74QXGYM | Tue Dec 8 10:00 AM | Game Awards prep | **fixed**: removed Viral Adam spend + owner-approval ask + 9:30 AM slot; predictions Short only as a gate-passing experiment in a real slot |
| trig_016dqSyTodgJDJEH5he8xubb | Tue Dec 8 10:40 AM | posting-frequency review | **fixed**: was going to edit code/CLAUDE.md for the old 3-a-day plan; now report-only (2 a day vs a 3rd slot, owner decides) |
| trig_01PHr6YJZgTwz5Knn3vo65N5 | Thu Dec 10 11:20 PM | Game Awards results night | **fixed**: posts only if every gate check passes (claims ledger, vice publish, tests, 2+ sources); free voices; Spanish only through its gate; stale quota assumption removed (uploads have their own API bucket) |

Checked for every job: posting frequency, manual-approval wording, Spanish pause, publishing policy (gate), budget
assumptions (no Everygen spend without a claim; Vice Replay zero-credit first), channel references, deprecated commands,
duplicates, timezone, current business objectives. Report-only jobs (Dec 3, Dec 5, Dec 8 frequency, momentum, scout,
breaking news) can never pause a channel or change frequency/slots.

## Aligned after the Nov 27 cycle was verified (8:35 AM ET)
CLAUDE.md, README.md, studio/quota.py (free slots read the gate config), .claude/commands/daily-video.md,
resources/shorts-tiktok-playbook.md, docs/vice-system.md and content/game-awards-2026.md now all point to the one
schedule in config/channel.json (EN 8:00 AM + 6:00 PM, ES 12:30 PM + 7:00 PM, max 2 a day each). The scheduler
(`studio.schedule place`) books new Shorts in free slots and never displaces a numbered map Short or a finished video.
Recurring jobs were renamed "Vice Replay · <time ET> <what it does>" (names only).
