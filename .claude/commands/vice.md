---
description: Vice Replay system - audit, discover, scan, clip, rank, create, batch, analyze, campaigns, report, publish
---
Run the Vice Replay research-to-video system for: $ARGUMENTS

Map the request to one command (`python -m studio.vice <command>`, details in `docs/vice-system.md`):
- audit -> `audit` (real YouTube Data + Analytics numbers by series; flags are signals, not verdicts)
- discover -> `discover` (competitors, cached 24 h; never claim editing details: videos aren't watched)
- scan -> `scan` (authorized sources only; "moment signals" are never footage)
- clip [source] -> `clip SRC --start --end --campaign <name> --headline ... [--punch t] [--replay a b]`
  (campaign clips -> ClipCircuit, hand-off only; source must be the raw stream, not a finished clip)
- rank/create [topic] -> skeleton, then research 2+ sources, fill every TODO, `python -m studio.ship episodes/<slug>.json`
- batch -> next ready calendar ideas (content/vice-calendar.json)
- analyze [video] -> `analyze VIDEO --episode E`
- campaigns -> `campaigns` (estimates vs approved vs received kept apart; never join/submit)
- report -> `report` (+ CSV/JSON exports)
- publish -> `publish episodes/<slug>.json` builds the draft (QC + rights + channel check). Uploading still needs
  the owner's "approve" in chat, then `python -m studio.ship ... --upload` per CLAUDE.md.
Rules: CLAUDE.md wins. Never spend Everygen credits without an estimate and the owner's yes. Report what ran,
the files written, and any blocker in plain words.
