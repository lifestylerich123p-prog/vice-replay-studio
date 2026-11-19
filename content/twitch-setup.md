# Twitch clip finder: one-time setup (about 10 minutes, owner)

Lets Claude pull Lacy's / KreekCraft's top Twitch clips automatically (`python -m studio.twitch_clips --campaigns`)
instead of you copying links. Free.

1. **Make the app**: go to **dev.twitch.tv/console** → log in with Twitch → **Register Your Application**.
   Name `Vice Replay Clips` · OAuth Redirect URL `http://localhost` · Category **Other** · Client type
   **Confidential** → **Create**. Open it → copy the **Client ID** → **New Secret** → copy the secret.
2. **Make the token** (on your Mac, Terminal app), replacing the two values (keep the quotes):
   ```
   curl -s -X POST https://id.twitch.tv/oauth2/token -d "client_id=YOUR_CLIENT_ID" -d "client_secret=YOUR_SECRET" -d "grant_type=client_credentials"
   ```
   It prints `{"access_token":"...","expires_in":...}`. Copy only the long access_token value.
3. **Tell Claude "twitch ready"** in the main chat and send the **Client ID** (not secret). Claude then:
   - opens a secure form for the access token (host api.twitch.tv); never paste the token or secret in chat,
   - saves the Client ID as the `TWITCH_CLIENT_ID` environment variable,
   - runs `python -m studio.twitch_clips lacy` to test.
4. The token lasts about 60 days. When the finder says it expired, repeat step 2 and the secure form.
