# Vice Replay Studio

Turns Claude Code into a video machine for the Vice Replay GTA 6 channel.
You give it a topic, and it researches it, writes the script, then makes the voiceover, branded visuals,
captions, a 16:9 video, a 9:16 Short, a thumbnail and a YouTube description with chapters.

## One-time setup (on your computer)
1. Install Python 3.10+, ffmpeg and Claude Code.
   - Mac: `brew install python ffmpeg`
   - Windows: `winget install Python.Python.3.12 Gyan.FFmpeg`
2. In this folder: `pip install -r requirements.txt`

## Make a video
Open Claude Code in this folder and type:

    /new-video GTA 6 best early-game money tips

or just `/new-video` and Claude picks a trending topic.

Output goes to `output/<slug>/`: the .mp4, the -short.mp4, thumbnail.jpg, description.txt, tags.txt.

## Make it look better
- **Your gameplay**: put clips or screenshots in `media/`, and Claude uses them as segment backgrounds
  instead of the generated neon city. Your own gameplay is what makes videos stand out (and is safe from
  copyright claims).
- **Music**: drop a royalty-free .mp3 into `assets/music/` (YouTube Audio Library is free). It's mixed in quietly.
- **Voice**: default is `en-US-AndrewNeural`. Others: `en-US-ChristopherNeural`, `en-US-GuyNeural`,
  `en-US-BrianNeural`. Set `"voice"` in the episode file. List all with `edge-tts --list-voices`.

## Run it by hand
    python -m studio.make_video episodes/gta6-3-days.json --preview
    python -m studio.make_video episodes/gta6-3-days.json
    python -m studio.make_video episodes/gta6-3-days.json --short
