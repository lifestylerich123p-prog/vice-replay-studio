"""Run this ONCE on your own computer to give the Vice Replay machine permission to upload to your channel.

    python3 youtube_auth.py client_secret_XXXX.json      (the JSON file Google gave you)
    python3 youtube_auth.py CLIENT_ID CLIENT_SECRET       (or the two values)

It opens your browser, you sign in with the Google account that owns the Vice Replay channel and click Allow,
and it prints a REFRESH TOKEN. Put these three values in the Claude environment settings
(vice-replay-studio -> Edit -> Environment variables):

    YT_CLIENT_ID      = the client ID
    YT_CLIENT_SECRET  = the client secret
    YT_REFRESH_TOKEN  = the refresh token this prints

Never paste them into a chat. Uses only Python's standard library.
"""
import http.server
import json
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

SCOPES = ("https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.force-ssl "
          "https://www.googleapis.com/auth/yt-analytics.readonly")


def main():
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        cfg = json.load(open(sys.argv[1]))
        cfg = cfg.get("installed") or cfg.get("web") or cfg
        client_id, client_secret = cfg["client_id"], cfg["client_secret"]
    elif len(sys.argv) == 3:
        client_id, client_secret = sys.argv[1], sys.argv[2]
    else:
        sys.exit(__doc__)
    print("Client ID (put this in YT_CLIENT_ID):\n" + client_id + "\n")
    print("Client secret (put this in YT_CLIENT_SECRET):\n" + client_secret + "\n")
    state = secrets.token_urlsafe(16)
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                result["code"] = q["code"][0]
                msg = "Done! You can close this tab and go back to the terminal."
            else:
                msg = "Something went wrong: " + q.get("error", ["no code"])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(msg.encode())

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{server.server_port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent", "state": state})
    print("Opening your browser. If it doesn't open, copy this link into it:\n\n" + url + "\n")
    webbrowser.open(url)
    t = threading.Thread(target=server.handle_request)
    t.start()
    t.join(timeout=300)
    server.server_close()
    if "code" not in result:
        sys.exit("No permission received (timed out or denied). Run it again.")
    data = urllib.parse.urlencode({"code": result["code"], "client_id": client_id, "client_secret": client_secret,
                                   "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data=data, timeout=30) as r:
        tok = json.load(r)
    if "refresh_token" not in tok:
        sys.exit("Google didn't return a refresh token. Remove the app's access at myaccount.google.com/permissions "
                 "and run this again.")
    print("Success! Put this in the environment settings as YT_REFRESH_TOKEN (don't share it):\n")
    print(tok["refresh_token"])


if __name__ == "__main__":
    main()
