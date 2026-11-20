# Recording your own gameplay

Your own clips are what `media/` is for. They make the videos stand out and keep the channel clear of Content ID claims.
Console menu names and limits below are from memory of the current system software, so confirm them on your console.

## Before you record

| Setting | Set it to | Why |
|---|---|---|
| In-game radio | Off | Licensed songs get clips muted or claimed |
| HDR in captures | Off, or record in SDR | HDR clips look grey and washed out after editing |
| Capture format | MP4 if offered | Works everywhere, including ffmpeg and both apps |
| Capture resolution | 1080p or higher | The Short crops the middle third, so resolution matters |
| Microphone and party audio | Excluded from captures | Keeps other people's voices out of your videos |
| HUD and minimap | Reduced if the game allows it | Cleaner frame for vertical crops |

## PS5

- Press the Create button to save recent gameplay or start a new recording.
- Captures and Broadcasts settings control the clip length for "save recent gameplay", the file type and the resolution.
- Move clips off the console with a USB drive (Media Gallery, then Copy to USB) or through the PS App auto-upload, which handles short clips only.

## Xbox Series X and S

- Press the Share button to save a clip. Capture settings set length and resolution.
- Internal storage only allows short clips. Recording to an external USB drive formatted for captures allows much longer ones.
- Move clips with the USB drive, or upload from the console to OneDrive.

## Longer or higher-quality recording

A capture card plus OBS Studio (free) on a computer removes the length limits and records straight to the machine that runs this repo.

## Getting clips into the machine

1. Put the files in `media/`. The folder is ignored by git on purpose, because the files are large.
2. Name them so Claude can match them to a topic:

       media/2026-11-20_driving_ocean-drive_sunset.mp4
       media/2026-11-20_police-chase_4-stars.mp4
       media/2026-11-21_screenshot_safehouse.jpg

3. Trim long recordings before use. This keeps a 20-second piece starting at 1 minute 30 without re-encoding:

       ffmpeg -ss 00:01:30 -i long.mp4 -t 20 -c copy media/clip.mp4

4. In the episode file, set a segment's `"media"` to the path, for example `"media/clip.mp4"`.

## What makes a clip usable

- 8 to 20 seconds of continuous action with no menus or loading screens
- The subject in the centre of the frame, so it survives the vertical crop
- No story cutscenes
- No other players' names or voices
