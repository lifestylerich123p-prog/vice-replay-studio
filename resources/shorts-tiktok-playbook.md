# Shorts and TikTok playbook

How the `short` block of an episode should be written and posted. Rewritten Nov 22, 2026 with our own numbers
(content/learn/hooks-2026-11-22.md, scorecard.md, lessons.md). `CLAUDE.md` and `content/episode-format.md` win.

## Shape of a good Short

| Part | Time | What it does |
|---|---|---|
| Hook | 0 to 2 s | States the surprising result as a statement, with the number on screen. The viewer decides here. |
| Proof | 2 to 15 s | Our own graph of the checked numbers (bars, counter, line), one fact per segment, 2 to 4 segments. |
| Turn | last 2 to 4 s | A pick-one question ("YES or NO", "1, 2 or 3") that loops back into the first line, then the follow badge. |

- **35 to 55 words, 13 to 20 seconds.** Our real-moment Shorts held 86-92% at 13-17 s; ~30 s explainers held ~57%.
  Scripts of 76+ words got a median 404 views vs 836 for 56-75 (the publish check blocks 76+).
- One idea per Short. If the main video has seven points, the Short takes the single strongest one.
- The first `headline` is on screen during the hook, so it must make sense with the sound off. Put the number in it
  (65% kept vs 49% without).
- End on a line that loops back into the opening ("Tell me, because" -> "GTA 6 is the cheapest GTA ever").

## Writing rules

- **Open on the result, never a question.** Statement openers kept 60% of viewers, question openers 35% (median 13.3
  views/hour vs 1.8). Good: "GTA 6 is the cheapest GTA ever, after inflation." "Eighteen hours early." Bad: "Did you
  know GTA 6 is cheap?" A question belongs at the END (the comment prompt).
- 3 to 10 words for the first sentence. Say "GTA 6" in it so search and auto-captions pick it up.
- Short sentences, one breath each. Spell numbers the way the chart shows them ("sixty eight point seven million").
- Label rumours out loud: "reportedly", "according to leaks". Estimates: "an estimate from Sensor Tower".
- No story spoilers in the first segment, the headline, the title or the caption.

## Visuals

- **Facts only** (owner, Nov 22 evening): no game footage in Shorts at all. Our cards carry the whole Short: charts,
  quote, list, text and quiz cards (content/episode-format.md). Owner gameplay is the one exception.
- **Original first** (YouTube's Oct 1, 2026 Shorts update ranks original videos higher; narration over reused footage
  isn't original). Build the Short on our own cards or the owner's gameplay. The publish check blocks a
  trailer-only Short unless the owner approved an `originality` note.
- Vary the layout: don't post three Shorts in a row that go counter > bars > counter > clip. Use a `line` chart for
  anything over time, open on bars sometimes, put a clip cutaway in the middle.
- Hard cuts on the beat (Shorts default: 0.2 s after each line, no fade to black).
- Keep important action in the middle; the 9:16 crop cuts the left and right thirds of a 16:9 clip.
- Leave the bottom fifth and the right edge clear (captions, buttons, progress bar).
- Captions: groups of 3 words, the spoken word in cyan, numbers as pink digits (automatic).

## Titles and tags

- "GTA 6" + the subject first (a streamer's name first for streamer stories), 40-45 characters before
  `#GTA6 #Shorts` (market titles of 40 or less: 95K views/h vs 70K for longer).
- Never "#1", "#8"... in a title: YouTube turns it into a hashtag. Write "No. 1" or reword (the check blocks it).
- 8 to 15 topic tags, most specific first; Spanish tags for the Spanish version.

## Posting

- Daytime slots: 9:30, 11:00, 12:30 ET (6-11 AM median 16 views/h, 11 AM-2 PM 10, 2-6 PM 2.7, evening 1.9).
  3:30 / 8:30 PM only for big news or the Sunday recap.
- Every Short goes up in English and in Spanish (Vice Replay en Español), Spanish title in the Spanish-market style
  (one CAPS word + one emoji), chart words in `chart_es`.
- Post the same Short to TikTok and Instagram from the clean file (never a download with another app's watermark).
- Our own pinned question is posted 10 minutes after the Short goes public; the owner pins it.

## What to measure

`python -m studio.learn` refreshes the numbers; `content/learn/scorecard.md` compares groups automatically (format,
picture = graph / gameplay / trailer, opener = statement / question, title hook, length, slot) and writes DO MORE /
DO LESS lines once a group has 3+ Shorts. Also check in YouTube Studio after 48 hours:

| Number | What it tells you |
|---|---|
| Viewed vs swiped away (Studio only) | Whether the hook works (aim for 70%+ viewed) |
| Average percentage viewed | Whether the middle drags. Over 100% means people rewatch. |
| Where the retention graph drops | Which segment to cut next time |
| Comments per 1,000 views | Whether the closing question works |

**Flop review**: `python -m studio.flops` lists public Shorts under 50 views 48 h after going public; the main chat
sets them PRIVATE (never deleted) and logs their pattern in content/learn/lessons.md.

## Rules that protect the channel

- YouTube limits or removes monetisation for mass-produced, near-identical videos. Every Short needs its own angle
  and its own data; vary the layout.
- Campaign clips never go on Vice Replay (they post on ClipCircuit): reposted clips can mark the channel an aggregator.
- No official GTA 6 music (radio, trailer songs, score). Our synthwave theme only; record gameplay with the radio off.
- Never other creators' footage.
