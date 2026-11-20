# Pipeline upgrades

Ideas for `studio/make_video.py`, ordered by how much they should help Shorts and TikTok. None are built yet.
Each has a prompt you can paste into Claude Code inside the repo.

## 1. Word-by-word captions

Short-form viewers expect captions that light up word by word. The narration text is already known, so only the timing is missing.

> Add word-level caption timing to the Short. Use faster-whisper on each segment's voiceover to get word timestamps, align them to the segment text, and write an ASS caption file that shows 3 to 4 words at a time with the current word in pink #FF1F8E. Keep the existing captions for the 16:9 video.

## 2. A TikTok cut over one minute

TikTok's Creator Rewards has only paid on videos longer than one minute, and the `short` block is under 55 seconds.

> Add an optional `tiktok` block to the episode format, 5 to 7 segments and 65 to 90 seconds of narration, and a `--tiktok` flag that renders it at 1080x1920 to `output/<slug>/<slug>-tiktok.mp4`. Update CLAUDE.md to describe the block.

## 3. Hook frame before the intro card

The first frame decides the swipe. A Short should open on gameplay or the headline, not a title card.

> For `--short`, skip the intro card and start directly on segment 1 with its headline on screen from frame one.

## 4. Smart vertical crop

A centre crop of 16:9 gameplay often cuts off the action.

> Add an optional `"focus"` value per segment (0.0 left to 1.0 right, default 0.5) that sets where the 9:16 crop is taken from a 16:9 clip.

## 5. Find highlights in long recordings

> Add `studio/find_moments.py`. Given a long gameplay recording, use ffmpeg scene-change detection and audio loudness peaks to list the 10 most likely highlight moments with timestamps, and export each as a 15-second clip into `media/`.

## 6. Separate captions per platform

> In addition to description.txt, write `shorts-title.txt` and `tiktok-caption.txt` to the output folder, following resources/hooks-and-titles.md.

## 7. Safe zones

> Draw captions and headlines for `--short` inside a safe area that leaves the bottom 20% and the right 12% of the frame clear, and add a `--safezone` debug flag that overlays the blocked areas on a preview frame.

## 8. Performance log

> Add columns to content/log.md for YouTube and TikTok views and average percentage viewed at 48 hours, and have /daily-video read the last 7 rows and state which hook type did best before choosing today's hook.

## 9. Signature voice

> Add Chatterbox as a third voice engine alongside Kokoro and edge-tts, selected by `"voice": "clone:<name>"`, reading a reference clip from `assets/voice/<name>.wav`.

Use only a reference recording of your own voice, or one you have written permission to use.
