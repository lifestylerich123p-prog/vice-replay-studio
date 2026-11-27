# Experiments (hypotheses, results, decisions)

Rules (directive v2.0): compare matched cohorts (same format and topic type, same observation window: 3 h, 24 h,
72 h, 7 days; search-driven vs feed-driven kept apart), use medians, never decide on one video. A 50% lift in the
24-hour median is a target, not proof. Data: `python -m studio.learn --mine` (scorecard.md, history.jsonl).

Baseline (Nov 26): after-launch Shorts median ~28 views at 24 h; map cards 46.6 views/h median (n=3), tier 6.2,
versus 4.0, headline 0.7, list 0.2; ~0.5% likes; ~0 viewer comments; 15 subscribers.

| ID | Question | Variants | Status | Started | Read on | Result |
|---|---|---|---|---|---|---|
| S1 | Best slot for the day's best map Short | 8:00 AM vs 6:00 PM (2/day plan, Nov 27-Dec 10); old 8 AM test week folded in | running | Nov 27 | Dec 5 (reminder set), Dec 10 | - |
| D1 | Comment prompt | open question vs one-tap ("Found it? Reply ✅ / 😭", last card "FOUND IT? COMMENT YES") | running | Nov 27 | Dec 5 | - |
| D2 | End-card promise | "SPOT #N+1 NEXT: FOLLOW" pill vs default "FOLLOW FOR DAILY GTA 6" | planned (needs a no-number control week) | - | - | - |
| A1 | Voice | Kokoro AI voice vs owner's recorded voice vs no narration (music + text) | waiting: owner voice recordings | - | - | - |
| B1 | Visual | screenshot + map pin vs animated website map vs owner gameplay + map overlay | waiting: owner gameplay | - | - | - |
| C1 | Hook | location revealed at frame 1 vs short location question vs problem → answer | planned: next 6 map Shorts alternate hook types (mark `"hook_type"` in the episode) | - | - | - |
| A2 | Spanish voice | Piper es_MX claude (default) vs Kokoro em_alex at -8% vs recorded Everygen Viral Adam | running: em_alex on tattoo shops (Dec 1) + easter-egg filter (Dec 3); Viral Adam on shoe store (Dec 1) + official map (Dec 2); Piper on checklist (Dec 2) + jewelry (Dec 3). Voice is recorded per upload (uploads-es.json), % viewed per voice in studio.xplat. Nov 26 checks: Piper claude 0.81 Whisper-small match vs es_MX-ald 0.68 (ald dropped); Piper peak limit fixed clipping | Nov 26 | Dec 6 (72 h after the last), then 7 days | - |
| M1 | Content mix | 40 location / 25 secrets / 15 gameplay / 10 map tutorial / 10 experimental (`python -m studio.mix`) | running | Nov 27 | weekly | - |
| H1 | Hook structure | location-reveal / result-first / benefit / myth-check / curiosity / warning (episode "hook_type"; studio.xplat hook table) across distinct comparable Shorts, never near-identical re-uploads | running | Nov 27 | weekly (n >= 5 per type) | - |
| L1 | Script length | 35-55 words vs 25-45 words (directive) | planned: new Shorts from Nov 27 at 25-45 | - | - | - |

## Decisions log
- 2026-11-26 (Phase 3): cross-platform table (`studio.xplat`): map/location 13.6x the YouTube baseline (n=3) and 57x on
  TikTok (n=1, the shoe store); tier lists 6.6x on YouTube (n=2) but 0.1x on Instagram; news/facts ~0.4-1.0 everywhere.
  Tier lists are NOT dropped (directive: never on one video): they stay in the 10% experimental share.
- 2026-11-26: versus / plain-fact / headline / list Shorts parked (map 46.6 v/h vs versus 4.0, list 0.2); tier lists
  parked from the plan (6.2) but kept as a later experiment option.
- 2026-11-26: Spanish YouTube paused to Dec 3 (37 views in 12 videos); Spanish goes to TikTok (100-600 views each).

## H2: Spanish hook structures (Phase 6 #3, started Nov 26)
- Question: which opening structure keeps Spanish viewers watching? Structures: immediate-answer, visual-reveal,
  question, comparison, myth-reality, location-info, before-you-buy (episode `hook_type_es`, else classified from the
  first Spanish line by studio.xplat; `first_frame` records what the first frame shows).
- Baseline (18 Spanish uploads before Nov 27): all statement/result openers over footage or text cards; median 5.9%
  viewed (studio.xplat, 28-day Analytics). No contrast yet, so no conclusion.
- First arms: Balsero (question, answer pin on screen), Sahara Arena ES (comparison), Little Cuba (immediate-answer,
  map pin). Then rotate the 7 structures across the Spanish slots.
- Decision rule: compare median % viewed and views at 72 h per structure with n >= 5 each, similar topics (map/location
  vs news), and the same voice where possible; until then every result is preliminary. A question opener stays a test
  (gate warning, not a blocker) only when tagged and the first frame shows the answer.

## H3: numbered titles vs single-spot titles (Phase 9, started Nov 26)
- Evidence to test: competitor learning (studio.competitors, Nov 26) EN numbered titles 2.42x their channel median vs
  0.89x (n=43/234, 8 channels); ES numbered 0.77x (insufficient) and ES 'secreto' titles 0.5x (n=23, 7 channels).
  Correlation only; earlier single-channel FAZZGTA example is NOT evidence.
- Arms: EN "GTA 6 map: 3 hidden Spanish words" (gta6-map-spanish-words) vs that week's single-spot EN map Shorts;
  ES "GTA 6: 3 lugares SECRETOS que quizás no viste" (gta6-3-lugares-secretos-es, Wed Dec 9 7 PM) vs single-spot ES map
  Shorts of the same week. Same card style, comparable length (20-26 s).
- Measure: views at 24 h / 72 h / 7 d, % viewed, Shorts-feed vs search share, subscribers. Decision after n >= 5 per arm.

## H4: map-scale visuals vs single-pin location cards (Phase 9, started Nov 26)
- Evidence to test: competitor map-scale Shorts 25x (EN, n=4) and 13x (ES, n=6) their channel medians: insufficient n,
  strong signal. Arm: "GTA 6 map size: how big Leonida really is" (gta6-map-size-scale, EN + ES; steps across the state,
  area pulse on Vice City, route over the Keys; every size figure attributed, no fan square-mile number shown as fact).
- Measure as H3; also website referrals to /guides/gta-6-map-size/ (Cloudflare once the token exists).
