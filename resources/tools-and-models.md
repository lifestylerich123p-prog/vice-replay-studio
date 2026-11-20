# Tools and AI models

What is worth adding to the machine, and what is not. Most rankings online are written by the vendors themselves, so try free tiers on your own footage before paying.

## Voice

The repo already uses Kokoro, which is free and runs on your machine. Change it only if the voice is holding the channel back.

| Option | Cost | Cloning | Notes |
|---|---|---|---|
| Kokoro-82M (current) | Free, local | No, preset voices | Runs on CPU. Good enough for daily output. |
| Chatterbox (Resemble AI) | Free, local | Yes, from a few seconds | MIT licence. Best free route to a signature channel voice. Wants a GPU. |
| CosyVoice2 (Alibaba) | Free, local | Yes | Apache 2.0, many languages. |
| ElevenLabs | Free tier, paid from about $6 a month | Yes | Most often ranked best for quality. Easiest upgrade. |
| Fish Audio | Paid, cheaper | Yes | Budget cloning. |
| Cartesia | Free tier of about 20K credits a month | No | Built for real-time, not needed here. |
| OpenAI TTS | About $15 per million characters | No | Simple and reliable. |
| XTTS v2 (Coqui) | Free, local | Yes | Licence restricts commercial use. Avoid for a monetised channel. |

Only clone a voice you own or have written permission to use.

## Finding moments in your gameplay

| Tool | What it does |
|---|---|
| Eklipse | Scans long recordings, picks highlights, makes vertical clips with captions |
| Medal.tv | Clip capture and AI highlights, strong on gaming |
| Choppity | AI clip maker with gaming presets |
| OpusClip, Vizard | General clippers. Good at reframing and captions, weaker at spotting gameplay moments. |
| Spikes Studio, Subclip | Stream-highlight tools |

Eklipse and Choppity each rank themselves first in their own articles.

## Captions

| Tool | Notes |
|---|---|
| faster-whisper | Free, local. Gives word-level timings for word-by-word captions. See `pipeline-upgrades.md`. |
| CapCut | Free editor with auto-captions, for hand-finishing a Short |
| OpusClip, Vizard | Animated caption styles |

## AI video generation

These cannot make real GTA 6 gameplay. Use them only for intros, transitions or thumbnail art, and never to fake footage of the game.

| Need | Models |
|---|---|
| Clips with sound and lip sync | Veo 3.1, Seedance 2.0 |
| Consistent characters | Kling 3.0, about $0.84 per 10-second 720p clip |
| Lowest cost | Wan 2.7, can be self-hosted |
| Talking presenter | HeyGen (API from about $100 a month), VEED Fabric |
| New audio on existing video | Sync, Magic Hour |

fal.ai and Replicate host many of these with free tiers, so several can be tried from one account.

## Channel research

| Tool | Notes |
|---|---|
| vidIQ | Keywords, trending videos, outliers. Has a Claude connector. |
| YouTube Studio, Research tab | Free. Shows what your own viewers search for. |
| Google Trends | Free. Compare search interest between topics. |
| TikTok Creative Center | Free. Trending hashtags and sounds. |

## Free building blocks

| Need | Tool |
|---|---|
| Recording from a capture card | OBS Studio |
| Editing by hand | DaVinci Resolve, CapCut |
| Thumbnails | Photopea, Canva free tier |
| Music for YouTube | YouTube Audio Library |
