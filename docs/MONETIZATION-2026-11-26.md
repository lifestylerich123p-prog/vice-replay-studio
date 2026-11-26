# Monetization research, Nov 26, 2026 (vice-replay-monetization agent; official pages read via search, unverified items marked)

Done the same day: fixed Amazon product prices removed from the site (Associates policy). Never project earnings.

**Vice Replay monetization report.** Report only: I changed, applied for and spent nothing. Sources were read Nov 26, 2026. This session can't load support.google.com or youtube.com directly, so those official facts come from search reads of the pages. Third-party claims are marked "unverified". There are no earnings projections.

**Fix first: an Amazon compliance risk.** Four site pages show fixed Amazon prices: /, /links/, /guides/gta-6-deals/ and /guides/gta-6-black-friday/ ("PS5 DualSense controller: $54.99", "Pulse Elite ~$110"). We re-check them every 3 days. Amazon's Program Policies (affiliate-program.amazon.com/help/operating/policies) allow prices only through Amazon-served links or API data cached for at most 24 h. As it stands, this could close the Associates account, our only live revenue.

**1) YouTube**
- **Lower (fan-funding) tier:** 500 subs, 3 public uploads in 90 days, and either 3,000 watch hours in 365 days or 3M Shorts views in 90 days. It does NOT change in Feb 2027 (support.google.com/youtube/answer/72851, /12843009).
- **Ad revenue:** today 1,000 subs plus 4,000 h or 10M Shorts views in 90 days. From **Feb 1, 2027**, new applicants need **8,000 h or 20M Shorts views**; existing partners are not affected (answer/12843009; blog.youtube "youtube-partner-program-updates-2027").
- **How Shorts ads pay:** Shorts-feed ad revenue is pooled monthly, minus music costs. Each creator gets a share by engaged views and keeps 45% of it (answer/12504220). From Feb 2027 the pool pays only channels with **10M Shorts views in the last 90 days**. The Shorts bonus program is invite-only (answer/18336041).
- **Where we stand:** ~15 subs and a median Short of ~63 views at 24 h, so every tier is far off. The Spanish channel (31 views in 28 days) is nowhere near.

**2) TikTok.** Creator Rewards (US terms, tiktok.com/legal/page/global/creator-rewards-program-us/en) needs:
- 18+ and a personal account
- 10K followers and 100K views in 30 days
- videos of **at least 1 minute**, with 1,000 qualified For You views each
- tax info, with a $50 minimum payout

**Our Shorts-length videos don't qualify.** Subscriptions and TikTok One also need 10K followers (support.tiktok.com, newsroom.tiktok.com). Our best video got 7,863 views and most get 100-600. Follower count is unchecked.

**3) Instagram/Facebook**
- **Instagram Gifts:** professional account, 18+, 500 followers (help.instagram.com/738469380549477). Meta's 2023 post said 5,000; the dashboard decides.
- **Facebook Content Monetization:** invite-only, with an interest form in Professional Dashboard (creators.facebook.com/tools/facebook-content-monetization).
- **Creator Fast Track:** needs 20K followers elsewhere and 30K views in 60 days (about.fb.com, Mar 2026).
- **Where we stand:** median 8 likes per Reel, plus Meta's Nov 19 flag on our campaign clips. Nothing pays yet.

**4) Website ads.** We have 6 clicks and 230 impressions in week one, and only Cloudflare analytics, no Google Analytics.
- **AdSense:** 18+, original content, HTML access, policy compliance, no traffic minimum (support.google.com/adsense/answer/9724). Its policies bar ads on copyrighted content; our Rockstar screenshots and map may draw a rejection (my inference).
- **Mediavine Journey:** 5,000 sessions a month from US/UK/CA/AU/DE/FR/NL, a domain 4+ months old, checked through Google Analytics (mediavine.com/application-requirements/, updated Nov 17, 2026).
- **Raptive:** 25,000 monthly pageviews, 50% from US/CA/UK/AU/NZ (help.raptive.com).
- **Ezoic:** 250,000 monthly users for new sites since Feb 2026; smaller sites get its Incubator (support.ezoic.com).

**5) Affiliate**
- **Amazon (we have the tag):**
  - The statement "As an Amazon Associate I earn from qualifying purchases" must be prominent and tied to the social account.
  - We need 3 qualifying sales in the first 180 days, or the application is rejected.
  - Rates: digital games 2%, physical games/consoles 1% (Associates help: Operating Agreement and commission table).
- **FTC** (ftc.gov "Endorsement Guides: What People Are Asking"): a description-only disclosure isn't enough when the video itself recommends products. Say it in the video, early.
- **Best Buy Creator/Affiliate (Impact):** rates by category (shown in the dashboard), 7-day cookie, paid ~60 days after month end (bestbuy.com affiliate pages). Fits consoles and accessories.
- **Green Man Gaming:** "up to 5%" on an old page. Poor fit: GTA 6 has no announced PC version. Avoid gray-market key resellers.

**6) Sponsorships/campaigns**
- **Whop Content Rewards** (already used; GTA 6 clips go on ClipCircuit): the brand sets a rate per 1,000 verified views and pays after it approves the clip (docs.whop.com).
- **Lurkit:** 250 YouTube/Twitch subs to join. Its TikTok option needs a Business account, which clashes with Creator Rewards. Its games are mostly off-niche (support.lurkit.com).
- **YouTube BrandConnect:** 25K US subs at launch (older blog.youtube post). Direct deals need a media kit with real numbers later.

**7) Digital products / premium.** Rockstar's fan policy counts it as commercial use when you make money from its material or use it to promote a product (support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz). So never paywall the official-map layer or sell anything with Rockstar art.
- **A:** a free "Leonida completion checklist" built from our own text and pins, saved in the browser, with an honest "notify me" email signup. It tests demand. Demand risk: large free map sites already exist (unverified).
- **B (later):** an optional ad-free or supporter tier on our own tools only, once map usage is measurable. Uptake is unlikely at today's traffic.

**Ranked next steps**

NOW (us)
1. Remove the exact prices from Amazon items: the DEALS list in tools/site_guides.py and the two guides. The main chat publishes.
2. Disclose affiliate links on screen or aloud in any long video that recommends gear. Add the Amazon statement to the channel About page.
3. Keep the subscriber-first plan, and track progress against 500 subs and 3M Shorts views per 90 days in studio.status.
4. Build checklist A.

OWNER
1. Associates Central: confirm account status (3 sales in 180 days), finish the tax interview, add a payment method.
2. Create a GA4 property; we add the tag. Mediavine and Raptive need it to apply.
3. Optional: apply for AdSense (identity, tax, bank). The same account later links to YPP.
4. Optional: apply to Best Buy via Impact, and fill in Facebook's interest form.
5. Check TikTok and Instagram follower counts, and keep TikTok a personal account.

WAIT
1. 500 subs plus 3M Shorts views or 3,000 h: the lower YouTube tier.
2. 1,000 subs plus 8,000 h or 20M Shorts views (from Feb 1, 2027): ad revenue. Shorts ad pay then also needs 10M views in 90 days.
3. TikTok 10K followers plus 100K views in 30 days. Then make 60 s+ cuts.
4. Instagram Gifts: 500 followers.
5. Lurkit: 250 subs, GTA-adjacent games only.
6. Mediavine Journey: 5,000 qualifying sessions and a 4-month-old domain. Then Raptive, then Ezoic.
