# Gameplay footage: legal sources (Phase 4, Nov 26)

Every file we use has a record in rights/registry.json; `python -m studio.provenance --check` lists each file's source,
owner, license, restrictions, attribution and episodes (rights/provenance.json). Unregistered = not usable.

| Source | Usable? | Conditions | Status |
|---|---|---|---|
| Owner's own gameplay (Drive "Vice Replay Gameplay" -> `python -m studio.gameplay`) | yes, best option | Rockstar's fan-content policy (registry `rockstar-official-gameplay` / `owner-gameplay`): real commentary, radio/music off, no cutscenes/endings, nothing from leaked copies | waiting for recordings |
| Rockstar official media (Newswire screenshots, "An Extended Look", trailers) | screenshots yes; clips only as allowed by the owner's style rule | Rockstar policy: fan use with commentary, monetization tolerated not licensed; owner rule since Nov 23: no trailer CLIPS in our videos | 175 screenshots + 32 silent clips registered |
| Creator footage | only with written permission | a registry record per creator: scope (clips, platforms, monetization), attribution text, date, proof link; revocable | none yet |
| Viewer submissions | only with an explicit license grant | a submission form whose terms grant us use + credit; checked like creator footage | not built (would need a form + storage) |
| Stock libraries | no GTA footage exists under stock licenses | - | - |
| Our website map recordings (`tools/record_map_demo.js`) | yes | our UI + Rockstar's official map (credited on screen) | 6 demos (media/site/) |
| Original animations (map styles, cards) | yes | our own work | in use |
| AI-generated scenes | never as gameplay | must be labelled on screen (`ai_visuals_labelled`) | not used in Vice Replay Shorts |

Until gameplay exists, its 15% of the content mix goes to map tutorials and location guides (config/channel.json
`content_mix`). When the owner's recordings arrive, set it back.
