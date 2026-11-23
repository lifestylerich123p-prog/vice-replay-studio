# YouTube upload quota: free fixes (Nov 22, 2026)

**Why:** Vice Replay, Vice Replay en Español and What If Arena share ONE Google Cloud project (named "What If Arena",
OAuth app "Creator HQ"), so they share one daily YouTube quota. On Nov 22 it ran out at 7:02 PM ET after 6 uploads.
A Short costs about 2,000-2,500 units (upload 1,600 + subtitles 400 + playlist, comment, thumbnail ~150). Already
done (free): English Shorts no longer upload a Spanish subtitle track (saves 400 per Short).

## Fix 1 (free, ~15 minutes, biggest): give What If Arena its own Google Cloud project: DONE Nov 22 (night)
Each project gets its own daily quota (10,000 units by default). Moving What If Arena OUT keeps Vice Replay's keys as
they are (no reconnect for the two Vice Replay channels). Do this on the computer where the What If Arena chat runs.

1. Go to console.cloud.google.com, click the project name at the top, then **New project**. Name: `What If Arena API`.
   Create, then make sure the new project is selected at the top.
2. **APIs & Services > Library**: search **YouTube Data API v3**, open it, click **Enable**.
3. **Google Auth Platform** (left menu): **Get started**. App name `What If Arena`, your support email, Audience
   **External**, your contact email, agree, **Create**.
4. **Branding**: App home page `https://vicereplay.com/`, Privacy policy `https://vicereplay.com/privacy/`, Terms
   `https://vicereplay.com/terms/` (these pages already cover What If Arena). Authorized domain `vicereplay.com`. Save.
5. **Audience**: click **Publish app** and confirm, so it shows **In production** (keys then don't expire after 7 days).
6. **Clients > Create client**: type **Desktop app**, name `What If Arena uploader`, Create. Download the JSON.
7. In the **What If Arena chat**: tell it "use the new Google Cloud project for YouTube" and give it the downloaded
   file the way it asks (a file on your Mac, never pasted into chat). It reconnects the What If Arena channel once.
8. Optional, once What If Arena works on its new project: in the old project, rename it to `Vice Replay` (top project
   menu > the project > Settings). The name is only a label; nothing for Vice Replay changes.

## Fix 2 (free, slower): ask YouTube for more quota
Form: https://support.google.com/youtube/contact/yt_api_form (YouTube API Services - Audit and Quota Extension Form).
YouTube first checks that the app follows its API rules; there's no published waiting time. Use the old project
(Vice Replay's) for this. Draft answers below; fill in the parts in [brackets] yourself (never share them in chat).

- **Organization / developer name:** [your name or business name]
- **Website:** https://vicereplay.com/
- **Contact email:** [your email]
- **Google Cloud project number:** [Cloud console > the project > Dashboard > "Project number"]
- **API client name:** Creator HQ (Vice Replay uploader)
- **What the client does:** A private tool used only by the channel owner to upload and schedule his own YouTube
  Shorts to his own two channels (Vice Replay, @ViceReplayTV-q8s, and Vice Replay en Español), add them to his own
  playlists, upload his own subtitle files, post his own pinned question comments and read his own channels' public
  statistics to decide what to make next. No other users, no data sold or shared, no downloading of YouTube videos.
- **Who uses it:** 1 person (the owner), 2 of his own channels.
- **Privacy policy / Terms:** https://vicereplay.com/privacy/ and https://vicereplay.com/terms/ (link to the YouTube
  Terms of Service and the Google Privacy Policy).
- **Quota requested:** 30,000 units per day.
- **Why:** About 10 Shorts a day across both channels (English + Spanish version of each). Each upload is
  videos.insert (1,600) + captions.insert (400) + playlistItems.insert (50) + commentThreads.insert (50) + reads,
  about 2,150 units, so ~21,500 a day plus ~1,500 for reading our own statistics. Our current limit ran out on
  Nov 22, 2026 after 6 uploads.
- **Data handling:** Only our own channels' data; stored in our private project files to plan content; not shared.
