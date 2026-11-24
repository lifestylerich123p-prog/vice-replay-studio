"""One Everygen job, one chat: claim it on GitHub first, then spend (owner Nov 24: "that double spending can't happen
again, so both chats must work together").

    python -m studio.everygen_claim claim voice:<slug>:es --credits 5 --what "Viral Adam, 5 lines"
    python -m studio.everygen_claim done  voice:<slug>:es --credits 5 --balance 84
    python -m studio.everygen_claim release voice:<slug>:es --reason "owner changed the script"
    python -m studio.everygen_claim list            # open claims + the last spends, from every chat

Why: on Nov 24 the main chat and the Spanish chat made the same Viral Adam voice twice (Ibai, then Bad Bunny in the
same minute): 10 credits lost from a balance of ~94. A rule in CLAUDE.md didn't stop it, so this is mechanical:

* The shared ledger is the branch `claude/everygen-ledger` on GitHub (claims.jsonl). A claim is a commit pushed
  WITHOUT force, so if two chats claim at the same moment GitHub accepts only one push; the other re-reads the ledger,
  sees the claim and stops. Exactly one chat can hold a job.
* Before claiming a voice job it also looks for that voice on every branch (git log --all -- media/voice/<slug>/<lang>)
  and in this checkout, so a voice that already exists is never made again.
* A PreToolUse hook (.claude/settings.json) runs `hook` before every paid Everygen tool call and BLOCKS it unless this
  chat holds a fresh claim (made in the last 60 minutes and not yet marked done). Each chat runs in its own container,
  so the claim file is per chat.
* Redoing a glitched line is allowed on purpose: `claim <job> --again "seg3 glitched"` (logged with the reason).
* Can't reach GitHub = no claim = no spend (fail closed).

Job keys: voice:<slug>:<lang> (Viral Adam lines), image:<slug>:<what>, video:<slug>:<what>, clips:<name>, or any
lowercase key with letters, digits, ':', '-', '_'. Several keys in one claim = one atomic commit (a batch).
"""
import argparse
import datetime as dt
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("EVERYGEN_CLAIM_REPO") or Path(__file__).resolve().parent.parent)
BRANCH = "claude/everygen-ledger"
REMOTE_REF = f"refs/remotes/origin/{BRANCH}"
LEDGER = "claims.jsonl"
LOCAL = ROOT / ".claude" / "everygen-claim.local.json"  # gitignored; what the hook reads
FRESH_MIN = 60          # a claim lets this chat spend for 60 minutes
TAKEOVER_H = 3          # an open claim older than this may be taken over (its chat probably died)
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9:_-]{2,120}$")
KNOWN_CHATS = {  # session id tail -> name shown in messages
    "01CJRsWP9GjYTirqgQXefGyG": "main chat",
    "01CJRsWQE1kt7hsB4ZMNfXcZ": "Spanish chat",
}
PAID = re.compile(r"^mcp__Everygen__(generate_.*|find_clips|change_voice|clone_voice|lip_sync|upscale_.*|clone_swap|"
                  r"compose_.*|render_composition|remove_background|isolate_voice|remove_voice|depth_video|mask_.*)$")


class Refused(Exception):
    pass


def chat_id():
    sid = os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    return re.sub(r"^(cse|session)_", "", sid) or socket.gethostname()


def chat_name(cid):
    return KNOWN_CHATS.get(cid, f"chat {cid}")


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t=None):
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(ts):
    return dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def git(*args, check=True, input=None):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, input=input)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip() or r.stdout.strip()}")
    return r


NET_ERR = re.compile(r"could not resolve|unable to access|connection|timed out|rpc failed|early eof|proxy|"
                     r"remote end hung up|temporarily unavailable|returned error: 5\d\d", re.I)


def net(*args):
    """A git network call with the 4 retries + backoff the repo's rules ask for; raises Refused if GitHub is out."""
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        r = git(*args, check=False)
        if r.returncode == 0 or not NET_ERR.search(r.stderr):
            return r
    raise Refused(f"can't reach GitHub ({r.stderr.strip()[:160]}): NOT claimed, so don't spend. Try again in a minute.")


def fetch_ledger():
    r = net("fetch", "-q", "origin", f"+refs/heads/{BRANCH}:{REMOTE_REF}")
    if r.returncode and "couldn't find remote ref" not in r.stderr.lower():
        raise RuntimeError(r.stderr.strip())
    if r.returncode:  # branch not created yet
        git("update-ref", "-d", REMOTE_REF, check=False)
    head = git("rev-parse", "-q", "--verify", REMOTE_REF, check=False).stdout.strip()
    rows = []
    if head:
        text = git("show", f"{head}:{LEDGER}", check=False).stdout
        for line in text.splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return head, rows


def state(rows):
    """Last word per job: {job: row} (claim / done / release)."""
    last = {}
    for r in rows:
        last[r["job"]] = r
    return last


def voice_exists(key):
    """voice:<slug>:<lang> -> where it already exists (a commit on any branch, or files here), else None."""
    parts = key.split(":")
    if parts[0] != "voice" or len(parts) < 2:
        return None
    slug, lang = parts[1], (parts[2] if len(parts) > 2 else "en")
    rel = f"media/voice/{slug}/{lang}" if lang != "en" else f"media/voice/{slug}"
    files = sorted(p.name for p in (ROOT / rel).glob("*.wav"))
    if files:
        return f"{len(files)} file(s) already in this checkout ({rel}/)"
    net("fetch", "-q", "origin")  # every branch: the other chat may have made it on its own branch
    log = git("log", "--all", "-1", "--format=%h %cr: %s", "--", rel, check=False).stdout.strip()
    return f"commit {log}" if log else None


def check_free(key, last, again, take_over, me):
    row = last.get(key)
    if not row or row["act"] == "release":
        return
    who = chat_name(row["chat"]) + ("" if row["chat"] != me else " (this chat)")
    age_h = (now() - parse(row["t"])).total_seconds() / 3600
    if row["act"] == "done" and not again:
        raise Refused(f"{key} was already DONE by {who} {age_h:.1f} h ago ({row.get('credits', '?')} credits). "
                      f"Use theirs. Only for a real redo (a glitched line): claim {key} --again \"why\".")
    if row["act"] == "claim" and row["chat"] != me:
        if take_over and age_h >= TAKEOVER_H:
            return
        raise Refused(f"{key} is CLAIMED by {who} {age_h * 60:.0f} min ago (\"{row.get('what', '')}\"). Don't spend: "
                      f"message that chat or wait for it. (--take-over works only after {TAKEOVER_H} h.)")


def push_rows(new_rows, check):
    """Append rows to the ledger atomically: build a commit on the ledger head, push without force, retry on a race."""
    for _ in range(8):
        head, rows = fetch_ledger()
        check(state(rows))
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows + new_rows)
        blob = git("hash-object", "-w", "--stdin", input=text).stdout.strip()
        tree = git("mktree", input=f"100644 blob {blob}\t{LEDGER}\n").stdout.strip()
        msg = f"{new_rows[0]['act']} {', '.join(r['job'] for r in new_rows)} ({chat_name(new_rows[0]['chat'])})"
        commit = git("commit-tree", tree, *(["-p", head] if head else []), "-m", msg).stdout.strip()
        r = net("push", "--porcelain", "origin", f"{commit}:refs/heads/{BRANCH}")
        if r.returncode == 0:
            git("update-ref", REMOTE_REF, commit, check=False)
            return commit
        if not re.search(r"rejected|non-fast-forward|fetch first|stale info|already exists", r.stdout + r.stderr):
            raise Refused(f"push refused ({(r.stderr or r.stdout).strip()[:200]}): NOT claimed, don't spend.")
        time.sleep(0.5)  # someone else pushed first: re-read and re-check
    raise Refused("the ledger kept changing under us: NOT claimed, try again.")


def write_local(data):
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL.write_text(json.dumps(data, indent=1))


def read_local():
    try:
        return json.loads(LOCAL.read_text())
    except (OSError, ValueError):
        return None


def cmd_claim(a):
    me, keys = chat_id(), [k.lower() for k in a.jobs]
    for k in keys:
        if not KEY_RE.match(k):
            raise Refused(f"bad job key {k!r}: use e.g. voice:<slug>:es")
    if not a.again:
        for k in keys:
            where = voice_exists(k)
            if where:
                raise Refused(f"{k}: the voice already exists ({where}). Use it. A real redo needs --again \"why\".")
    rows = [{"t": iso(), "job": k, "act": "claim", "chat": me, "credits": a.credits, "what": a.what,
             **({"again": a.again} if a.again else {})} for k in keys]
    push_rows(rows, lambda last: [check_free(k, last, a.again, a.take_over, me) for k in keys])
    local = read_local() or {}
    jobs = {j: v for j, v in (local.get("jobs") or {}).items()
            if (now() - parse(v)).total_seconds() < FRESH_MIN * 60}
    jobs.update({k: iso() for k in keys})
    write_local({"chat": me, "jobs": jobs})
    print(f"CLAIMED by {chat_name(me)}: {', '.join(keys)} (~{a.credits} credits). You may spend for the next "
          f"{FRESH_MIN} min. After: python -m studio.everygen_claim done {' '.join(keys)} --credits N --balance B")


def cmd_close(a, act):
    me, keys = chat_id(), [k.lower() for k in a.jobs]

    def mine(last):
        for k in keys:
            row = last.get(k)
            if not row or row["act"] != "claim":
                raise Refused(f"{k} has no open claim to mark {act}")
            if row["chat"] != me:
                raise Refused(f"{k} is claimed by {chat_name(row['chat'])}, not this chat")

    extra = {"credits": a.credits, "balance": a.balance} if act == "done" else {"reason": a.reason}
    push_rows([{"t": iso(), "job": k, "act": act, "chat": me, **extra} for k in keys], mine)
    local = read_local() or {}
    jobs = {j: v for j, v in (local.get("jobs") or {}).items() if j not in keys}
    if jobs:
        write_local({**local, "jobs": jobs})
    else:
        LOCAL.unlink(missing_ok=True)
    print(f"{act.upper()}: {', '.join(keys)}" + (f" ({a.credits} credits, balance {a.balance})" if act == "done" else ""))
    if act == "done":
        print("Log it in the Channel Map's Shared log and content/channels.md: "
              f"\"{dt.date.today()} · Vice Replay ({chat_name(me)}) · Everygen: {a.credits} credits for "
              f"{', '.join(keys)}. Balance after: {a.balance}.\"")


def cmd_list(_a):
    _, rows = fetch_ledger()
    last = state(rows)
    open_ = [r for r in last.values() if r["act"] == "claim"]
    print(f"Open claims ({len(open_)}):" if open_ else "Open claims: none")
    for r in open_:
        print(f"  {r['job']}  {chat_name(r['chat'])}  since {r['t']}  ~{r.get('credits', '?')} cr  {r.get('what', '')}")
    print("Last 10 done:")
    for r in [r for r in rows if r["act"] == "done"][-10:]:
        print(f"  {r['t']}  {r['job']}  {chat_name(r['chat'])}  {r.get('credits', '?')} cr  balance {r.get('balance', '?')}")


def cmd_hook(_a):
    """PreToolUse hook: exit 0 = allow, exit 2 = block (stderr goes back to the model)."""
    try:
        tool = json.load(sys.stdin).get("tool_name", "")
    except ValueError:
        tool = ""
    if tool and not PAID.match(tool):
        return 0
    local, me = read_local(), chat_id()
    fresh = []
    if local and local.get("chat") == me:
        fresh = [j for j, t in (local.get("jobs") or {}).items() if (now() - parse(t)).total_seconds() < FRESH_MIN * 60]
    if fresh:
        return 0
    sys.stderr.write(
        f"BLOCKED: {tool or 'this Everygen call'} spends shared credits and this chat holds no claim. All chats share one "
        "Everygen balance, and on Nov 24 two chats made the same voice twice. First run:\n"
        "  python -m studio.everygen_claim claim voice:<slug>:es --credits <n> --what \"<what>\"\n"
        "If it says CLAIMED BY another chat or ALREADY DONE: don't spend, use theirs or message that chat. "
        "After spending: python -m studio.everygen_claim done <job> --credits <n> --balance <b>.\n")
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("claim")
    c.add_argument("jobs", nargs="+")
    c.add_argument("--credits", type=int, required=True, help="estimated credits")
    c.add_argument("--what", required=True)
    c.add_argument("--again", default="", help="reason for a real redo of a job that is already done")
    c.add_argument("--take-over", action="store_true", help=f"take an open claim older than {TAKEOVER_H} h")
    d = sub.add_parser("done")
    d.add_argument("jobs", nargs="+")
    d.add_argument("--credits", type=int, required=True)
    d.add_argument("--balance", default="?")
    r = sub.add_parser("release")
    r.add_argument("jobs", nargs="+")
    r.add_argument("--reason", required=True)
    sub.add_parser("list")
    sub.add_parser("hook")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "hook":
            return cmd_hook(a)
        {"claim": cmd_claim, "list": cmd_list,
         "done": lambda x: cmd_close(x, "done"), "release": lambda x: cmd_close(x, "release")}[a.cmd](a)
    except Refused as e:
        print(f"NOT CLAIMED: {e}" if a.cmd == "claim" else f"REFUSED: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
