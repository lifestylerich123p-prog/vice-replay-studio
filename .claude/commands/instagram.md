---
description: Post Reels and carousels to the Vice Replay Instagram (@vice.replaytv) - queue, captions, campaign pairs
---
Instagram is connected (content/owner.md: IG_USER_ID, Meta System User token for graph.facebook.com as a network
secret, never expires). Owner approval (Nov 19): every approved/auto-posted English Short also goes to Reels, plus
campaign clips, plus about one carousel a day. All posts go through ONE queue: `content/learn/reels_queue.json`.

## Pace (since Nov 19)
Meta restricted ADS on @vice.replaytv on Nov 19 (can't run ads or use audiences; posting is NOT affected) after
11 API posts on the account's first day. Rules from now on: **max 4 posts a day** (`--queue` enforces it:
`IG_MAX_PER_DAY`, default 4; extra items wait for the next day), at least ~2.5 h apart, and no reposted streamer
clips on this account (campaign clips stay held, see owner.md). Don't request an ad review unless the owner wants
to run ads/boosts (a denied review can make it final). If the owner sends another Meta warning that is about
posting/recommendations (Account Status), pause the queue and tell him first.

## How it runs
- `python -m studio.ship ... --upload ...` adds each uploaded Short to the queue 5 min after its YouTube time and
  prints `REELS QUEUED: <times>`. Schedule a send_later wake-up at each time with the message
  "Post the next queued Reel now: cd /home/user/vice-replay-studio && IG_USER_ID=17841454790873754 python -m studio.instagram_upload --queue ..."
- `--queue` posts ONE due item per run (keeps posts ~1-1.5 h apart; a brand-new account posting in bursts looks
  like spam). Campaign clips that share a time go out TOGETHER (owner: "two at the time"), so one submit trip covers both.
- Each Reel gets the episode's `pinned_comment` as its first comment; captions come from the episode
  (title without #Shorts, short_description, tiktok_hashtags, "Follow @vice.replaytv").
- Manual: `--episode episodes/<slug>.json [--item news|tips]`, `--carousel content/carousels/<slug>.json`,
  `<video.mp4> --caption "..."`. Media is hosted for a few minutes on vicereplay.com/r/ (site repo) and removed.

## Queue items
`{"at": "YYYY-MM-DD HH:MM" (ET), "episode": "episodes/x.json", "item": "short|news|tips"}`
`{"at": ..., "video": "output/clips/<campaign>/<file>.mp4", "caption": "...", "campaign": "LACY (Content Rewards)"}`
`{"at": ..., "carousel": "content/carousels/<slug>.json"}`
`{"at": ..., "image": "output/ig-images/<slug>/<file>.jpg", "caption": "...", "comment": "..."}` (single image)

## Campaign clips (LACY etc.)
After a campaign Reel posts (output says CAMPAIGN): send the owner the link(s) at once, schedule ONE send_later
20 minutes later ("Submit <clips> on the <campaign> page now"), add rows to content/campaigns/tracker.md.

## Carousels (about one a day)
Write `content/carousels/<slug>.json` (format in studio/ig_cards.py: cover, 3-6 tips/facts, cta), run
`python -m studio.ig_cards <spec>` and look at `output/carousels/<slug>/sheet.jpg` once (text fits, nothing
overlaps), then queue it. Rotate: tips, fun facts / "by the numbers", news recap, "did you know" Leonida facts.
Only facts we already checked (episodes, site guides), reports labelled as reports, official screenshots as
backgrounds (never the excluded shots). Everygen cover art is OK sparingly (2 credits per image), never fake GTA art.

## Checks
`python -m studio.doctor` shows the Instagram connection, posts used today (limit 100) and overdue queue items;
`python -m studio.status` shows what posted today and what's next.
