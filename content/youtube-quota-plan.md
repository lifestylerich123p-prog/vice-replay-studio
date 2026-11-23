# YouTube upload quota: free fixes (Nov 22, 2026)

**Status (Nov 22, night): Fix 1 done.** What If Arena has its own project ("What If Arena API"); the old project was
renamed **"Vice Replay"** (ID what-if-arena, number 662880770567), so its quota is Vice Replay's alone. Fix 2 (the form) is
still open.

**Why (before the fix):** Vice Replay, Vice Replay en Español and What If Arena shared ONE Google Cloud project (named "What If Arena",
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

## Fix 2 (free, slower): ask YouTube for more quota (answers refreshed Nov 23)
**Before you submit (done Nov 23):** the audit checks that the app follows the YouTube API Services Developer
Policies. Two gaps are fixed: `studio.tidy` now deletes other channels' public data (trend research) after 30 days,
and vicereplay.com/privacy/ now says what the tool reads, that it's deleted within 30 days, how to revoke access
(security.google.com/settings/security/permissions) and how to ask for deletion.

Form: https://support.google.com/youtube/contact/yt_api_form (YouTube API Services - Audit and Quota Extension
Form). Submit it from the Google account that owns the **Vice Replay** Cloud project (ID what-if-arena, number
662880770567). There's no published waiting time; YouTube may email follow-up questions (answer them yourself, or
paste the question in the main chat for a draft). Fill in the [brackets] yourself; never share them in chat.

- **Organization / developer name:** [your name or business name]
- **Address / country:** [yours]
- **Website:** https://vicereplay.com/
- **Contact email:** [your email]
- **Google Cloud project number:** 662880770567 (check: Cloud console > the project > Dashboard)
- **Current daily limit:** [Cloud console > APIs & Services > YouTube Data API v3 > Quotas & system limits: "Queries per day"]
- **API client name:** Creator HQ (Vice Replay uploader). Internal tool, not public, no other users.
- **What the client does:** A private command-line tool used only by the channel owner to manage his own two
  YouTube channels, Vice Replay (@ViceReplayTV-q8s) and Vice Replay en Español. It uploads and schedules his own
  original videos (Shorts and one long video a week), adds them to his own playlists, posts one question comment on
  each of his own videos and replies to viewers' comments on his own videos, and reads his own channels' statistics
  to decide what to make next. It also runs a few public searches a day (search.list, videos.list) for popular
  GTA 6 videos to see which topics are trending; that public data stays inside the tool, is never published or
  shared, and is deleted within 30 days. No downloading of YouTube videos, no data sold or shared.
- **Who uses it:** 1 person (the owner), 2 of his own channels.
- **Privacy policy / Terms:** https://vicereplay.com/privacy/ and https://vicereplay.com/terms/ (they link the
  YouTube Terms of Service and the Google Privacy Policy).
- **Quota requested:** 30,000 units per day.
- **Why (our real numbers):** Each upload costs about 1,750 units: videos.insert (1,600) + playlistItems.insert (50)
  + commentThreads.insert (50) + reads (we already stopped uploading caption files on Shorts to save 400 per video).
  A normal day is 3 Shorts in English + 3 in Spanish (about 10,500 units), plus up to ~40 replies to viewers' comments
  (about 2,000), schedule/title updates (about 1,000) and statistics reads (about 1,500): about 15,000 a day. Our
  limit ran out on Nov 21 (9:14 PM ET) and Nov 22 (8:09 PM ET), and on Nov 23 was used up by 10 AM ET, so approved
  videos wait a day and comments go unanswered. Event days (for example The Game Awards on Dec 10) need room for
  news videos on both channels. 30,000 covers a normal day with room for those.
- **Data handling:** Our own channels' data is kept in our private project files to plan content. Other channels'
  public data is used only for trend research and deleted within 30 days. Nothing is shared, sold or shown publicly.
- **If they ask for screenshots/screencast:** a screen recording of the terminal running `python -m studio.status`
  and an upload (`python -m studio.ship ... --upload`) is enough to show what it does; don't show keys or the .env file.
