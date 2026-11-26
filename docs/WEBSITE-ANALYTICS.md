# Website measurement: what we can see today (Phase 6 #9, checked Nov 26, 2026)

| Source | Status | What it gives | Access needed (minimum) |
|---|---|---|---|
| Google Search Console | **AVAILABLE** (Windsor.ai, read-only, `sc-domain:vicereplay.com`) | clicks, impressions, position by page and query (`content/learn/searchconsole-<date>.json`) | none more |
| Cloudflare Web Analytics | beacon on every page (cookieless); **API not readable** | page views by path, incl. the `/v/<slug>/` short links = clicks from our videos | owner: one API token, Account → Account Analytics → **Read** only, saved as a network secret for `api.cloudflare.com` (environment settings) |
| Short-link pages `/v/<slug>/` | live for every location/map Short (EN + ES) | one path per Short, counted by Cloudflare once the token exists; UTM kept on the target page | same token |
| Google Analytics 4 | not set up | sessions, sources, engagement; needed later for ad networks (Mediavine asks for GA4) | owner: create a GA4 property (we add the tag + update /privacy/); optional |
| Bing Webmaster Tools | not connected (Windsor has a connector) | Bing clicks/impressions | owner: connect in Windsor (read-only); optional |
| Hosting logs | none we can read (static hosting) | — | — |

Rules: read-only scopes only, never account-wide admin; until a source is readable the daily report says
"not measurable yet" (never an estimate).

## First real numbers (Search Console, last 7 days to Nov 25)
8 clicks, 341 impressions. Homepage 7 clicks / 73 impressions. Most impressions: /guides/gta-6-ps5-pro-worth-it/
(126, avg position 11.3; query "is ps5 pro worth it for gta 6" 26 impressions at 8.3) -> updated Nov 26 with two FAQ
answers for the queries people actually type ("60 FPS patch", "do you need a PS5 Pro") and Rockstar's Nov 18 statement.
Then /guides/gta-6-characters/ (46, pos 7.9), gift guide (39), unlock time (24). The new map/location guides have no
impressions yet (days old): re-check weekly before building more pages of the same kind.

# Long-form: assessment (Phase 6 #11)
- Evidence so far: long videos got ~0 related/browse traffic (Nov 24); the owner's Nov 26 rule holds new long videos
  until the ATM guide (public Nov 26) and the map-secrets guide (public Nov 27) pull search views.
- Candidate when that happens: **"GTA 6 shopping map: every store type and the first one you can reach"** (clothing,
  barber, tattoo, shoes, mod shops, gun-free): original structure (route from the start area, what each store unlocks,
  money tips, the interactive map walkthrough recorded from vicereplay.com), chapters per store, every location Short's
  "Related video". Not a concatenation of Shorts: new route segments, explanations and map demonstrations.
- Decision point: Fri Dec 4 (7 days of search data on both guides). Make it only if either guide shows search traffic
  (YouTube search views > 0 and growing) and the assets cover it without trailer clips.

## Cloudflare token: exact minimum (owner action, Phase 7 #11)
Cloudflare dashboard -> My Profile -> API Tokens -> Create Token -> Create Custom Token:
- Permissions: **Account | Account Analytics | Read** (nothing else: no Zone, DNS, Workers or Edit rights)
- Account Resources: Include -> the Vice Replay account only; optional: Client IP filtering off, TTL as you like
- Save it as a network secret in this environment's settings: host `api.cloudflare.com`, header `Authorization`,
  value `Bearer <token>` (never paste it in chat). Also add the account ID (not secret) to the environment variables as
  `CF_ACCOUNT_ID`. We then read Web Analytics (GraphQL `rumPageloadEventsAdaptiveGroups`: page views by path, incl. the
  `/v/<slug>/` video short links, referrers, countries) read-only.
