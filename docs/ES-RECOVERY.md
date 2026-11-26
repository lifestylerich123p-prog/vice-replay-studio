# Vice Replay en Español: recovery plan (Nov 26, 2026)

Owner, Nov 26: Vice Replay en Español becomes its own autonomous GTA 6 channel for Spanish speakers (Latin America,
US, Spain), not a translated copy; publishing through the gate without per-video approval; Vice Replay's budget rules.

## Diagnosis: 12 videos, 40 views, 0 likes (Nov 22-26)
| Problem | Evidence | Fix |
|---|---|---|
| Wrong topics | 9 of 12 were streamer news / plain facts, 4 about IShowSpeed (an English-speaking streamer); 0-8 views each | Spanish-first secrets, easter eggs, "dónde está" guides, Latino/Miami angles |
| The winning format never tried | 0 map / secret Shorts on the Spanish channel; English map Shorts are 46.6 views/h vs 0.7 for news; Spanish TikToks do 100-600 views | the Spanish line-up is map/secret Shorts adapted to Spanish |
| Only Latino angle won | Bad Bunny / Miami: 19 views, the best of the 12 | Little Cuba, Vice City vs real Miami, more Miami/Latino angles |
| Titles | mostly news phrasing ("IShowSpeed terminó...", "GTA 6 hizo 5 VECES...") | discovery phrasing that works in Spanish GTA Shorts: SECRETO, TRUCO, EXISTEN, "así se entra", "dónde está" |
| Voice | Kokoro em_alex (free) on early videos: Whisper heard "GTA 6" as "que te ases" | free local Piper es_MX voice (heard "GTA 6" right, 0.71 vs 0.65 word match); Viral Adam only for winners |
| No gameplay | every successful Spanish info Short shows gameplay | owner gameplay is the top request; until then cards + Rockstar's official map |
| Brand-new channel | 0 subscribers, no seed audience | consistent format and 2 a day max; reply to every Spanish comment; channel trailer = best video |
| Retention unknown | the Spanish channel's Analytics (retention) isn't pulled yet | add Spanish Analytics to `studio.learn` (next) |

Not the problem: publishing volume. More videos of the same kind would not have helped.

## Market (content/learn/market-es-2026-11-26.md, 27 Spanish videos)
Gameplay creators and comedy skits dominate; info Shorts that win are discoveries ("TRUCO SECRETO", "SE HA
RESUELTO EL EASTER EGG", "DETALLES ALUCINANTES", "¿Qué pasa si...?"), 30-60 s, CAPS word + emoji.

## Plan (Nov 27 - Dec 6, then decide from data)
- 2 Spanish Shorts a day at 12:30 PM and 7:00 PM ET (11:30 / 18:00 Mexico City), both test slots.
- Line-up: Ninja Turtles, Silent Hill (clave 955214), Backrooms, Little Cuba, ghost ship, Vice City vs Miami, mask,
  shoe store, tattoo shops, official map, giant crab, white fox, jewelry fence, Bigfoot, Vercetti portal, panther,
  UFO, "sin doblaje", alligators (content/learn/approved_queue.json `es` slots).
- Titles start with "GTA 6" (Nov 26: the gate held Silent Hill and Backrooms for "El SECRETO..." / "Los BACKROOMS...";
  9 line-up titles fixed).
- Nov 26: 27 old Spanish slots (news, versus, tier, quiz items, 9:30 AM-1:30 PM) moved to `es_parked` in the queue;
  only the line-up keeps an `es` slot, and the gate only auto-publishes at 12:30 PM / 7:00 PM.
- Every one passes the gate on platform `youtube-es` (Spanish render + title, facts re-checked within 2 days, QA,
  duplicates, destination channel).
- Director: `.claude/agents/vice-replay-es-director.md`; daily Spanish production run (scheduled task).

## Results (fill in at 24 h / 72 h / 7 days)
| Video | Slot | Views 24 h | Views 7 d | Notes |
|---|---|---|---|---|

## Distribution diagnosis (Phase 8, Nov 26; YouTube Analytics, 28 days, both channels' own data)
| | English | Spanish |
|---|---|---|
| views | 38,441 | 31 |
| engaged views | 16,647 (43%) | 10 (32%) |
| from the Shorts feed | 28,965 (75%) | 4 (13%) |
| from YouTube search | 8,812 (23%) | 23 (74%) |
| subscribers gained | 25 | 0 |

Finding (measured): the Spanish Shorts are barely being shown in the Shorts feed; almost every view comes from
someone searching (top terms: "otra noche en miami gta 6", "dardos gta 5", "windpress gta6"). Retention can't be judged
until the feed shows the videos to real audiences. Not measurable via the API: viewed vs swiped away, feed
impressions, unique/returning viewers (Studio only), countries (withheld below YouTube's threshold).
Hypotheses (unproven, to test): new channel with 0 subscribers and irregular uploads (paused Nov 24-26) gets little
feed testing; titles don't match what Spanish speakers search. Tests: (1) steady 2 Spanish Shorts/day from Nov 27 (queue
booked through Dec 9); (2) titles that start with real Spanish search phrases (competitors-2026-11-26.md); (3) track
feed vs search share weekly in content/learn/distribution-<date>.json. Decision rule: if after 14 days of steady posting
the feed share is still under 25%, test Spanish search-guide Shorts as the main format.
