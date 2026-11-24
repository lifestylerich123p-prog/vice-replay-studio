"""Channel separation: validate the destination of every publication draft.

Vice Replay, ClipCircuit and What If Arena share tools, never destinations, branding, analytics or history.
validate() refuses a draft when the content type isn't accepted by the destination, when the destination is
uploaded by hand (we only prepare a hand-off), or when the upload token belongs to a different channel.
"""
import json
import urllib.error
import urllib.request

from . import db

CONFIG = db.ROOT / "config" / "channel.json"


def config():
    return json.loads(CONFIG.read_text())


def authenticated_channel_id(env=None):
    """Channel the upload token belongs to (1 quota unit). None if the token can't be used.
    env: the token's environment variable (the Spanish channel uses its own token, see studio/youtube_es.py)."""
    try:
        from ..youtube_upload import token
        tok = token(env) if env else token()
        req = urllib.request.Request("https://youtube.googleapis.com/youtube/v3/channels?part=id&mine=true",
                                     headers={"Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            items = json.load(r).get("items", [])
        return items[0]["id"] if items else None
    except urllib.error.HTTPError as e:  # Nov 22: a used-up quota was reported as "token expired"
        body = e.read().decode(errors="ignore")
        return "quota" if e.code == 403 and ("quotaExceeded" in body or "dailyLimitExceeded" in body) else None
    except SystemExit as e:
        return "quota" if "QUOTA" in str(e) else None
    except Exception:
        return None


def validate(destination, content_type, check_token=True, token_channel=None):
    cfg = config()["channels"]
    problems, notes = [], []
    ch = cfg.get(destination)
    if not ch:
        return {"ok": False, "problems": [f"unknown destination '{destination}'"], "notes": [], "mode": None}
    if content_type in ch.get("refuses", []) or content_type not in ch.get("accepts", []):
        problems.append(f"{ch['name']} does not take '{content_type}' content (accepts: {', '.join(ch['accepts'])})")
        owner_of = [k for k, c in cfg.items() if content_type in c.get("accepts", [])]
        if owner_of:
            notes.append(f"'{content_type}' belongs on: {', '.join(cfg[k]['name'] for k in owner_of)}")
    mode = ch.get("upload")
    if mode == "api" and check_token:
        env = None
        if destination == "vice-replay-es":  # Nov 24: check the Spanish token, not the English one
            from ..youtube_es import ENV as env
        tok_ch = token_channel if token_channel is not None else (authenticated_channel_id(env) if env else authenticated_channel_id())
        if tok_ch == "quota":
            problems.append("YouTube daily quota used up (resets 3 AM ET): the connection is "
                            "fine and nothing else is wrong; run publish again after the reset")
        elif tok_ch is None:
            problems.append("upload token unavailable or expired: reconnect YouTube (tools/youtube_auth.py)")
        elif tok_ch != ch["channel_id"]:
            problems.append(f"upload token belongs to {tok_ch}, not {ch['name']} ({ch['channel_id']})")
    elif mode != "api":
        notes.append(f"{ch['name']} is posted by the owner ({mode}): we prepare a hand-off package, never upload")
    return {"ok": not problems, "problems": problems, "notes": notes, "mode": mode, "channel": ch["name"]}
