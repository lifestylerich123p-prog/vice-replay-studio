# Your starter kit, merged

This folder is your original starter kit, unchanged (its 8 tests still pass:
`cd starter/vice_replay_starter && python -m unittest discover -s tests`).

Its ideas now run inside the main system with the same command names:
`python -m studio.vice add-source | add-candidate | rank | create-project | render | qc | package | status`.
What changed and why is in `docs/vice-system.md` ("Stage 2"). In short: the same fail-closed rights rules plus file
hashes, destination scope and an append-only audit log; renders go through the framing engine (webcam on top /
tracked crop / blur fill instead of empty bars); captions are transcribed locally and reviewed before release; QC is
the full inspector; and a local dashboard runs the jobs.
