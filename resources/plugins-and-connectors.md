# Claude plugins and connectors

Found in the Claude plugin directory and connector directory on 16 November 2026. None are installed yet.
Plugins from community publishers are reviewed for the directory but are not made by Anthropic, and several need a paid account with the service behind them.

## Most useful for this channel

| Name | Type | What it adds | Needs |
|---|---|---|---|
| vidIQ | Connector | YouTube keyword research, trending videos, outlier videos, channel stats | vidIQ account |
| watch-video | Plugin | Claude watches a local recording: pulls keyframes, transcribes, reports where the good moments are | ffmpeg, local Whisper or an API key |
| AudioPod | Plugin | Noise removal, transcription with speaker labels, stem splitting, format conversion | AudioPod account |
| Token Shield | Plugin | Advice and measurement tools for cutting Claude token use on the daily run | Nothing extra |
| token-saver | Plugin | Compact output and session snapshots to reduce tokens in long sessions | Nothing extra |

## Video makers

| Name | Type | What it adds | Needs |
|---|---|---|---|
| AI Video Editor & Timeline (ManyMotions) | Plugin | Multi-track timeline, trims, transitions, burned-in captions, MP4 export | ManyMotions account and credits |
| AI Avatar Presenter (ManyMotions) | Plugin | AI presenter speaking a script to camera | ManyMotions account and credits |
| Abracadabrax AI Video Generator | Plugin | Short generated clips using Kling, Seedance, Sora or Veo | Abracadabrax credits |
| video-shotcraft | Plugin | Motion-graphics videos built in code with Remotion | Node.js |
| HyperFrames by HeyGen | Connector | Animated slides and motion graphics rendered from HTML | HeyGen account |
| Tella | Connector | Editing and polishing recordings already in Tella | Tella account |

This repo already renders with ffmpeg and Pillow, so the video makers overlap with what exists. Add one only for something the repo cannot do, such as an animated intro.

## Voice

| Name | Type | What it adds | Needs |
|---|---|---|---|
| ElevenLabs | Connector | Manages ElevenLabs voice agents | ElevenLabs account |
| Speko | Connector | Narrates text, transcribes audio | Speko account |

## Keeping the daily run cheap

- Keep `CLAUDE.md` short. It is loaded on every run.
- Have the daily command read only the files it needs from this folder, not all of them.
- Run the daily task on a smaller Claude model if the scripts stay good enough.
- Install only the plugins you use. Every installed plugin and connector adds to what Claude loads.
