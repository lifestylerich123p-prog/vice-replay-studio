# Vice Replay — Claude Code Starter Kit

A real, local-first Python CLI scaffold for **rights-first GTA 6 Shorts production**. It is a starter for Claude Code, not a complete autonomous video studio. It uses Python's standard library, SQLite, FFmpeg and FFprobe. **No paid APIs** and **no automatic YouTube uploads**.

## Requirements

- Python 3.10+ (`python3 --version`)
- FFmpeg and FFprobe (`ffmpeg -version`, `ffprobe -version`)
- On macOS, install FFmpeg through Homebrew if needed: `brew install ffmpeg`
- Own gameplay or other media for which you have valid written commercial/distribution rights.

## Run on your Mac

```bash
cd vice_replay_starter
python3 -m unittest discover -s tests -v
python3 -m vice_replay --workspace ./workspace init
python3 -m vice_replay --workspace ./workspace status
```

### 1. Add a local recording **you own**

Use your own footage in place of `~/Movies/my-gameplay.mp4`. Explicit flags record your rights confirmation. The tool never downloads external videos.

```bash
python3 -m vice_replay --workspace ./workspace add-source \
  --file ~/Movies/my-gameplay.mp4 \
  --creator "Vice Replay" \
  --url "local://my-original-recording" \
  --rights owned \
  --confirm-owned --commercial-use --youtube-allowed \
  --notes "Original gameplay capture; verify publisher/platform policies"
```

Use `--rights permission --proof /path/to/creator-permission.pdf` or `--rights licensed --proof /path/to/license.pdf` for third-party footage. Confirm the specific permission genuinely covers commercial reuse on YouTube; a text placeholder is not a license. All footage also needs `--commercial-use --youtube-allowed`.

### 2. Register and rank a candidate moment

```bash
python3 -m vice_replay --workspace ./workspace add-candidate \
  --source-id 1 --title "I tried the strangest getaway in GTA" \
  --start 12 --end 29 \
  --curiosity 9 --payoff 9 --context 8 --audio 8 --visuals 9 --originality 9
python3 -m vice_replay --workspace ./workspace rank
```

The score is a transparent *editorial heuristic*, **not a model of predicted views**. A moment with unapproved rights stays blocked no matter its score.

### 3. Create a project and render

```bash
python3 -m vice_replay --workspace ./workspace create-project --candidate-id 1
# Inspect workspace/projects/0001/metadata.json
python3 -m vice_replay --workspace ./workspace render --project-id 1 --layout fit
```

`fit` preserves the entire frame (may leave large letterboxed areas); `fill` crops to vertical. For split-screen clips, Claude should later implement a proper region-aware composition, avoiding the common problem of cropping the webcam or action out of view.

For an optional *accurate*, timecoded subtitle file, put a `.srt` in the project:

```bash
python3 -m vice_replay --workspace ./workspace add-captions \
  --project-id 1 --srt ~/Movies/checked-captions.srt
python3 -m vice_replay --workspace ./workspace render \
  --project-id 1 --layout fit --burn-captions
```

This starter does **not** automatically transcribe audio. Claude can integrate Whisper later and validate its output before adding captions.

### 4. Technical check and prepare a publishing **draft**

```bash
python3 -m vice_replay --workspace ./workspace qc --project-id 1
python3 -m vice_replay --workspace ./workspace package \
  --project-id 1 --description "Original gameplay and commentary" \
  --tags "GTA6,Gaming,Shorts"
```

Look in `workspace/projects/0001/` for `final.mp4`, `qc.json`, `metadata.json`, and `publish_draft.json`. The draft is deliberately marked `upload_ready: false` and **does not upload** to YouTube. Technical QC does not substitute for checking real visual quality, accuracy, and content rights.

## Files included

- `vice_replay/core.py` — database, rights enforcement, ranking, project state, FFmpeg render, technical QC, packaging.
- `vice_replay/cli.py` — commands and human-readable outputs.
- `tests/test_workflow.py` — unit and real FFmpeg integration test.
- `CLAUDE.md` — implementation instructions and authorization for architectural improvements.
- `research/vidiq_snapshot_2026-11-20.json` — historical public audit and competitor examples to guide early decisions.

## Important limitations

- No URL video downloader, scraping, paid APIs, creator impersonation, or YouTube account modification.
- Third-party source footage is blocked without explicit permissions and proof. **No code can establish legal rights merely by setting flags:** verify real licenses.
- No AI clip selection, split-screen detection, automatic narration, Whisper transcripts, cloud services, YouTube Analytics, or publishing yet.
- No promise of copyright clearance, monetization eligibility, or increased views.
- `config.json` contains a **candidate** channel ID from public research; confirm ownership before connecting an account or enabling future uploads.

## Where Claude should start

Read **CLAUDE.md**. Run the tests first. Then prioritize the modular improvements there. Claude can change architecture, languages, libraries, and workflows when an alternative is measurably better, provided it preserves safety and user-approved boundaries.
