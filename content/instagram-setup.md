# Instagram Reels auto-posting: one-time setup (about 20 minutes, owner)

Instagram lets apps post Reels for Professional accounts (unlike TikTok). Free. Steps:

1. **Professional account**: Instagram app → Settings → Account type and tools → Switch to professional account →
   Creator (or Business) → category "Gaming video creator".
2. **Meta developer account**: go to developers.facebook.com, log in with Facebook, tap Get Started (free).
3. **Create an app**: My Apps → Create App → use case "Other" → type "Business" → name "Vice Replay Poster".
4. **Add Instagram**: in the app, Add product → Instagram → "API setup with Instagram login".
5. **Add your account**: under "Generate access tokens", Add account → log in to the Vice Replay Instagram → allow.
   (The app stays in development mode; that's fine for posting to your own account.)
6. **Tell Claude it's done** in the main chat. Claude will then:
   - ask you for the **access token** through a secure form (never paste it in chat),
   - ask to allow `graph.instagram.com` for the workspace,
   - set your Instagram user id (shown next to the account in step 5) as `IG_USER_ID`,
   - run `python -m studio.instagram_upload --check` to confirm.
7. From then on, when you approve videos, approved Shorts can also go to Reels automatically (say "post Shorts to
   Reels too" once to switch it on). The token lasts 60 days; Claude reminds you to refresh it.
