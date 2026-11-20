# Vice Replay resources

Reference pack for the Vice Replay video machine. Researched 16 November 2026.
Prices, limits and programme rules change, so check the provider's own page before paying or applying.

| File | Use it when |
|---|---|
| [shorts-tiktok-playbook.md](shorts-tiktok-playbook.md) | Writing or reviewing any Short or TikTok |
| [hooks-and-titles.md](hooks-and-titles.md) | Writing segment 1, titles, thumbnail text and captions |
| [topic-bank.md](topic-bank.md) | The launch plan has run out, or a day's topic falls through |
| [capture-guide.md](capture-guide.md) | Recording your own gameplay for `media/` |
| [upload-checklist.md](upload-checklist.md) | Posting to YouTube Shorts and TikTok |
| [tools-and-models.md](tools-and-models.md) | Choosing a voice, clipping or video tool |
| [plugins-and-connectors.md](plugins-and-connectors.md) | Adding tools to Claude itself |
| [free-credits.md](free-credits.md) | Applying for free AI credits |
| [pipeline-upgrades.md](pipeline-upgrades.md) | Asking Claude Code to improve `studio/make_video.py` |
| [sources.md](sources.md) | Checking where a claim came from |

## Make Claude use this folder

Claude Code only reads these files if something points it at them. Add this block to the end of `CLAUDE.md`:

```markdown
## Reference pack
Before writing an episode, read `resources/shorts-tiktok-playbook.md` and `resources/hooks-and-titles.md`.
When no topic is planned, pick an angle from `resources/topic-bank.md` and research it fresh.
The channel rules in this file win over anything in `resources/`.
```
