# The Game Awards 2026: Vice Replay plan (Dec 8-13)

Owner asked Nov 23 ("1,2,4"). Facts checked Nov 23 in 2+ sources each; **re-check everything right before posting**.

## Checked facts
- **Show:** Thursday Dec 10, 7:30 PM ET / 4:30 PM PT, Peacock Theater, Los Angeles. Free on YouTube, Twitch,
  Facebook; Disney+ for the first time (GGRecon, Shacknews, Wikipedia). Game of the Year is the last award (~10:30-11 PM ET).
- **GTA VI: 8 nominations, the most this year** (VGC, Gematsu, Wccftech, Billboard, VICE, TechWiser):
  Game of the Year, Best Game Direction, Best Narrative, Best Art Direction, Best Score and Music, Best Audio
  Design, Best Performance (Manni L. Perez as Lucia Caminos), Best Action/Adventure.
- **GOTY nominees:** 007 First Light, Control Resonant, Grand Theft Auto VI, Phantom Blade Zero, Resident Evil
  Requiem, The Legend of Zelda: Ocarina of Time (remake).
- **Record:** 9 wins in one night, Clair Obscur: Expedition 33 at TGA 2025 (Guinness World Records, VGC, TechRadar).
  Before that, The Last of Us Part II: 7 (2020). So GTA VI (8 nominations) **cannot** break the wins record;
  8 wins would be the 2nd most ever, 7 would tie The Last of Us Part II.
- Players' Voice (fan vote) nominees were due Nov 30: check whether GTA VI is in it before Dec 8 (if yes, the
  pinned comments can say "vote at thegameawards.com").

## Schedule
| When (ET) | What | Status |
|---|---|---|
| Fri Nov 27, 11:00 AM | **8 nominations Short** `gta6-game-awards-8-noms` (Spanish Nov 28 only if the English one wins its first 24 h) | booked |
| Sun Dec 6, 3:30 PM | **Long video** `gta6-game-awards-explained` (3:11, all 8 nominations); 4 PM Game Awards odds carousel on Instagram | booked |
| Mon Dec 8, 10 AM | Fact re-check run (nominees, record, show time, Players' Voice); re-render the predictions Short if anything changed; keep Dec 10 light (see quota) | scheduled |
| Wed Dec 9, 9:30 AM | **Predictions Short** `episodes/gta6-game-awards-record.json` ("GTA 6 can't break the Game Awards record", 18 s, our call 6 of 8). English; Spanish only if it wins its first 24 h (winners-only since Nov 23) | rendered, needs owner approval |
| Thu Dec 10, ~11:15 PM | **Results-night Short** (template A or B below): breaking news, auto-post under the standing breaking-news approval if it passes every rule in `.claude/commands/breaking-news.md` | scheduled run |
| Fri Dec 11, 11:00 AM | **Scorecard Short** (template C): every category won/lost, "our call was 6". Needs owner approval (made on results night, sent with the night report) | made on results night |
| Sun Dec 13, 3:30 PM | Weekly long video: "GTA 6 at The Game Awards: every win and loss, explained" (hub slot) | idea, plan in the Dec 11 daily run |

**Quota:** a results upload needs ~1,750 units (EN) on Dec 10's quota. When booking Dec 10, book at most two
daytime Shorts (leave 12:30 PM free) so ~3,500 units stay open for the night. If the quota is short at night, post the
English Short at 3:05 AM Dec 11 (right after the reset) instead of waiting.

## Templates (lettering cards only, no trailer images; headlines 19 characters or less; 35-55 words)
**A. GTA 6 won Game of the Year** (`gta6-game-awards-goty-win`):
1. kinetic `["GTA 6 WINS", "GAME OF THE YEAR"]`, pink "GAME OF THE YEAR". "GTA 6 just won Game of the Year."
2. headline kicker "THE GAME AWARDS 2026", text "GOTY: GTA VI", ticker = the five nominees it beat, src 2 outlets.
3. meter value = wins tonight, max 8, label "wins tonight", sub "record: 9 (Clair Obscur, 2025)".
4. kinetic `["DID IT", "DESERVE IT?"]`. "Did it deserve it? Tell me, because" (loops to the hook).

**B. GTA 6 lost Game of the Year** (`gta6-game-awards-goty-lost`):
1. kinetic `["GTA 6 LOST", "GAME OF THE YEAR"]`. "GTA 6 just lost Game of the Year to <winner>."
2. versus a `[<winner>, "GOTY"]`, b `["GTA 6", "<X> OF 8"]`, winner "a", src 2 outlets.
3. list of what it did win (max 6 rows), good ["won"].
4. kinetic `["WAS GTA 6", "ROBBED?"]`. "Was GTA 6 robbed? Tell me, because"

**C. Morning scorecard** (`gta6-game-awards-scorecard`): hook kinetic `["GTA 6 WON", "<X> OF 8"]`; list 1 (GOTY,
Direction, Narrative, Art Direction: WON/LOST); list 2 (Score and Music, Audio Design, Performance, Action/Adventure);
meter "our call: 6", value X ("we were right/off by N"); kinetic question. Name who beat GTA 6 in each loss in the
description, not on the cards.

Every template: `text_es` + `chart_es` (Spanish: "GTA seis", numbers as words), `short_es` title in the Spanish
style (one CAPS word + one emoji), pinned comments EN/ES, sources (official thegameawards.com winners list + 2 outlets:
IGN, GameSpot, VGC, Variety, The Verge, Polygon, Kotaku), `#ViceReplayBreaking` at the end of the night Short's
description. No story spoilers.

**Website (Nov 23):** vicereplay.com/guides/gta-6-game-awards/ (+ ES /es/guias/gta-6-premios-game-awards/). Every Game Awards video links it (`guide` key). After the long video goes public (Sun Dec 6), put its id in `site/guides/gta-6-game-awards.json` `video` and republish; on Dec 10 night, add the winners to both guides.
