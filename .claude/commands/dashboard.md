---
description: Refresh the Vice Replay Dashboard artifact with the latest channel numbers (main chat)
---
Dashboard: https://claude.ai/artifact/UZSJWSBJbXBByZvWcxrxiF (Data artifact type; datasets channel, uploads, schedule,
campaigns are attached JSON files; the page in its store `files/index.html` follows the one-writer rule).

1. `python -m studio.dashboard` -> output/dashboard/{channel,uploads,schedule,campaigns}.json (YouTube API, free).
2. Upload each file to the artifact: Artifact publish with `url` above, `file_path` the file, `asset: true` (one call
   per JSON file). Note each new `/_blob/<id>`.
3. ArtifactData `get` each `datasets/<id>` for its version, then one `batch` of `update`s pinned with `if_version`:
   `source.url` = the new /_blob url, `updated` = {at: now UTC ISO, by: "Claude (studio.dashboard)"}.
4. Delete the old blobs (Artifact `delete` with `url` and `path` = the old 32-char id) so they don't pile up.
5. Read `data/users/me` `check`/`runs` if present; fix only what they show. Don't change the page unless asked.
Run it after each upload batch in the main chat, and when the owner asks "how are we doing".
