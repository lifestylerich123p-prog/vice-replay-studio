# Clipping campaigns (Whop Content Rewards and similar)

Streamers and brands pay per 1,000 views for clips of their streams. Because the streamer gives permission,
campaign footage is the ONE case where Vice Replay may use a streamer's own video and audio.

## Join a campaign
1. Pick GTA 6 campaigns only (they fit the channel and its audience).
2. Copy `_example.json` to `<short-name>.json` (e.g. `lacy-gta6.json`) and fill it in:
   - `rules`: paste every rule from the campaign page word for word (length, platforms, required tags,
     watermark/credit, banned content, posting deadlines).
   - `facecam_box` / `gameplay_box`: where the streamer's camera and the game sit in their stream, as
     fractions of the frame `[x, y, width, height]` (Claude can measure this from one frame of a VOD).
   - `layout`: `stacked` (camera on top, game below), `blur` (whole frame centred) or `full` (centre crop).
   - `status`: `active` while you're clipping it, `ended` after.
3. Add source footage to `source_queue` (VOD links or file paths the campaign allows you to use).

## Make clips
- In Claude Code: `/campaign-clips <short-name>` (or the daily run does it for active campaigns).
- By hand: `python -m studio.clip SOURCE.mp4 --campaign <short-name> --top 6`

## Track
Every posted clip goes in `tracker.md` with its link, so you can submit it and see what pays.
