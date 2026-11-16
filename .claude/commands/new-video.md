---
description: Research, script and render a new Vice Replay GTA 6 video (main video + Short + thumbnail)
argument-hint: <topic, or leave empty for Claude to pick a trending one>
---
Make a new Vice Replay video following CLAUDE.md.

Topic: $ARGUMENTS

If no topic was given, search the web for what GTA 6 players are searching for and talking about right now,
suggest 3 video ideas with a one-line reason each, pick the strongest, and say which one you picked.

Then: research it, write the episode JSON, render the preview, check the frames, render the final video,
the Short and the thumbnail, and finish with the output paths, 3 title options and the description text
ready to paste into YouTube Studio. Use media files from `media/` if the user put any there that fit the topic.
