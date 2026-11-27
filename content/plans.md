# Plan modes (switch with one message: "switch to Pro mode" / "switch to Max mode")

The owner is on Claude **Max** for GTA 6 launch month (Nov 2026). When they go back to a smaller plan, apply **Pro mode**
in one go from the main chat (update the scheduled tasks below with update_trigger; the owner's message is the request).

| Setting | Max mode (now) | Pro mode (cheaper) |
|---|---|---|
| Publishing schedule | NOT part of plan mode (owner Phase 10, Nov 26): English 8:00 AM + 6:00 PM ET, Spanish 12:30 PM + 7:00 PM ET, max 2 routine Shorts per channel per day, only through the publishing gate (config/channel.json `auto_publish` / `auto_publish_es`) | same |
| Helper daily run (trig_01AQ4TgsmpD4BDUjmTeJxe1n, 5:13 AM) model | session default | claude-sonnet-5-5 |
| Spanish director run (trig_011QXer4L5s5BHgWLNJwjm7i, 10:23 AM) | daily | every other day (keep the 5-day line-up) |
| Breaking news (trig_01MTxMGMgd8nF44C6VxmmFHZ) | report-only, ends Nov 30 (owner Phase 10) | ended |
| Momentum check (trig_01BDJUjM9FysWFCqmPJsfA4s) | daily 2:47 PM, report-only | Mon/Wed/Fri only, or off |
| Comment auto-replies (trig_01T8agB7rbk9ewL6C1w314Zr) | 9:13 PM (+ the 1 PM report and the 2:04 AM run) | same |
| Website guide | EN + ES daily | EN daily, ES only for big topics |
| Weekly scout + competitor learning | Sundays | Sundays (keep: it's one run) |

Always cheap regardless of plan: studio.radar (stops quiet news runs for free), studio.ship (one command per video,
one check image), studio.tidy + content/INDEX.md (no searching), slim CLAUDE.md (episode details only loaded when
writing), episodes/backlog/ (ready-made scripts).
