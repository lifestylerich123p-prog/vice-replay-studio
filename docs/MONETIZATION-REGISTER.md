# Vice Replay monetization register (Phase 6, Nov 26, 2026)

The full data is in `content/monetization/register.json`: 28 programs with eligibility, our real numbers, geo, cost,
disclosure, payment and sources.

**How this was checked:** this session couldn't open support.google.com or affiliate-program.amazon.com (DNS blocked),
so every entry is `search-summary-only`: a search read of the program's own pages, dated 2026-11-26. Anything taken
from third parties is marked unverified in the JSON. Nothing was applied for, signed or bought, and there are no
earnings estimates.

**Where we stand (repo numbers):** English channel 15 subscribers, 63 public videos, 40,140 lifetime views, about 0
long-form watch hours. Spanish channel 0 subscribers, 40 views. Site: 230 search impressions and 6 clicks (Nov 20-23),
no GA4. TikTok: 0 of 24 recent videos are 60 s or longer. Campaign and Amazon earnings: unknown (not recorded).

## Fix first (compliance, us = main chat)
1. Amazon prices still live in two places: the `content/affiliate.json` set `deals` ("about $54 this week", "about
   $110") and the description of the public video S_H61BzbFKA (episodes/gta6-black-friday-deals.json: "$54 (usually $74)").
   Amazon allows prices only from Amazon-served links or API data refreshed within 24 h.
2. After Nov 30, take down the Black Friday "on sale" and "best deal this week" lines (tools/site_guides.py DEALS).
3. Owner decision: 6 Lacy campaign clips (12,422 views) are still public on Vice Replay. The owner's Nov 20 rule says
   campaign clips go on ClipCircuit, and the YPP review judges the whole channel for reused content. Set them private
   (never delete) or keep them; the owner decides.

## Register

| Program | Status | Next step | Who |
|---|---|---|---|
| Amazon Associates (vicereplay-20) | eligible-owner-action (P1) | Check account status, 180-day deadline, sales count, tax interview and payment method in Associates Central; report to main chat | Owner (us: fix the prices above) |
| YPP fan-funding tier, English | not-eligible-yet (P1) | Turn on eligibility alerts in Studio > Earn; track 500 subs + 3M Shorts views/90 d or 3,000 h | Owner (alerts), us (tracking) |
| YPP ad-revenue tier, English | not-eligible-yet (P1) | Plan for the Feb 1, 2027 bar: 1,000 subs + 8,000 h or 20M Shorts views/90 d (confirmed, answer/12843009) | Us |
| Shorts Creator Pool (both channels) | not-eligible-yet (P2) | Only after the ad tier. From Feb 2027 it also needs 10M Shorts views/90 d each month | Us |
| Whop Content Rewards (GTA 6, on ClipCircuit) | active (P2) | Record real earnings in tracker.md; decide on the 6 public Lacy clips | Owner |
| YPP both tiers, Spanish | not-eligible-yet (P3) | Grow per docs/ES-RECOVERY.md; separate application later | Us |
| Best Buy (Impact) | not-eligible-yet (P3) | Reapply once traffic is steady (Impact declined Nov 18) | Owner |
| AdSense (site) | research (P3) | Decide whether to run ads at all, and only on pages without Rockstar map/screenshots | Owner |
| Mediavine Journey | not-eligible-yet (P3) | Create a GA4 property so sessions can be measured (needs 5,000/month from 7 countries, domain 4+ months) | Owner, then us (tag) |
| PlayStation Direct (Partnerize) | research (P4) | Optional application once traffic is steady | Owner |
| Microsoft Store / Xbox | research (P4) | Find the official program page (third-party data only so far) | Us |
| Raptive | not-eligible-yet (P4) | Wait: 25,000 pageviews/month | None now |
| YouTube Shopping affiliate | not-eligible-yet (P4) | Needs YPP | None now |
| YouTube BrandConnect | not-eligible-yet (P4) | Needs the YPP ad tier | None now |
| Direct sponsorships / seeding | research (P4) | Review any inbound offer; media kit from real Studio numbers only | Owner |
| Lurkit | not-eligible-yet (P4) | At 250 YouTube subs; keep TikTok a personal account | Owner |
| TikTok Creator Rewards | not-eligible-yet (P4) | Check the follower count; pays only for 1 min+ videos | Owner |
| Amazon Afiliados MX / ES | research (P5) | Only if Spanish traffic from MX/ES appears | None now |
| GameStop, Green Man Gaming | research (P5) | GameStop has third-party data only; GMG waits for a GTA 6 PC edition (none announced) | None now |
| Ezoic | not-eligible-yet (P5) | Don't apply to the Incubator early (a rejection is permanent) | None now |
| Instagram Gifts | research (P5) | Check eligibility in the Professional Dashboard | Owner |
| Premium site features (tips / ad-free) | research (P5) | Only after map usage is measured; nothing Rockstar-made behind a paywall | Owner decides |
| Original digital products | research (P5) | Free checklist first to test demand; our own work only | Owner decides |
| Grey-market key resellers | rejected-trust-risk | Never | n/a |
| Selling Rockstar's map/assets | rejected-trust-risk | Never | n/a |
| Gambling/crypto/"free money" sponsors | rejected-trust-risk | Never | n/a |

## Affiliate placements allowed today (Amazon account status unknown)
- **vicereplay.com pages:** yes. owner.md says the site is listed in Associates Central. Keep the footer and box
  statement "As an Amazon Associate I earn from qualifying purchases", rel="sponsored", and no typed prices.
- **YouTube long-video descriptions and our own pinned comments:** only if the owner confirms the channel URL is
  listed in Associates Central (Amazon expects established social pages, "in most cases at least 500 followers"; we
  have 15). Until then, link to vicereplay.com/gear instead. Any video that recommends gear says so out loud or on
  screen, early (FTC).
- **Shorts descriptions:** no (links aren't clickable).
- **Spanish channel, Instagram, TikTok:** no (not listed, and amazon.com links pay only on US-store orders).
- **Email/DMs:** only to people who opted in (we have no list). **PDFs, printables, e-books, offline:** never.

## What we will NOT do
- Sell, paywall or put on merch anything Rockstar made: the official map, screenshots, logos, trailer footage, music.
- Use grey-market key resellers (G2A, Kinguin, Eneba, CDKeys and similar).
- Promote gambling, skin/case betting, crypto casinos, "free GTA money", modded accounts, cheats or account sales.
- Type Amazon prices by hand, invent deals, or use fake scarcity ("today only") or stale "on sale" claims.
- Post an affiliate or sponsored link without a disclosure next to it, and in the video when the video recommends it.
- Claim we used or tested a product we didn't.
- Post GTA 6 campaign clips on Vice Replay (they go on ClipCircuit), or repost other creators' videos.
- Publish revenue projections or treat a search summary as a page we read.
- Apply, sign, accept terms, or enter tax or bank details for the owner.
