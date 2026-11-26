"""Reliable saving for unattended runs (owner Nov 26, Phase 3 #9: "The 5 AM run repeatedly fails to push its work to
GitHub... Do not depend on reconstructing entire files from conversation logs").

Root cause (Nov 26): the daily trigger started a fresh session with no repository attached and no add_repo or
fire_trigger tool, so every push got 403 and the only fallback was file attachments. Fix: the run now fires into a
persistent helper session cloned with this repo (push verified by preflight), and every run saves through this module.

    python -m studio.runsafe preflight daily            # can we read + push? (dry run; no change on GitHub)
    python -m studio.runsafe recover                    # push any earlier run branch that never reached GitHub
    python -m studio.runsafe checkpoint daily -m "..."  # commit everything on claude/daily-<date> + manifest + push
    python -m studio.runsafe inbox                      # main chat: helper run branches not merged into main yet
    python -m studio.runsafe merge claude/daily-2026-11-27   # main chat: merge one after reading its manifest

* Helper runs never touch main: they save to their own branch `claude/<run>-<YYYY-MM-DD>` (CLAUDE.md: helper chats
  work on their own claude/... branch and never post). The main chat merges and publishes.
* Each checkpoint writes `content/runs/<run>-<date>.json` (manifest: files with SHA-256, commit, step, push result),
  so what a run made is on GitHub as files, not in a transcript.
* Pushes retry network errors 4 times with backoff (2, 4, 8, 16 s); a 403 / auth refusal is NOT retried (it needs the
  owner) and is recorded as BLOCKED with the exact step.
* State survives in `.runsafe/state.json` (local) and in the manifests on the run branch; `recover` re-pushes
  unpushed run branches at the start of the next run.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / ".runsafe" / "state.json"
RUNS = ROOT / "content" / "runs"
ET = dt.timezone(dt.timedelta(hours=-5))
NET_ERR = re.compile(r"could not resolve|unable to access|connection|timed out|rpc failed|early eof|hung up|"
                     r"temporarily unavailable|returned error: 5\d\d|sideband", re.I)
AUTH_ERR = re.compile(r"403|401|permission|denied|authenticat|not allowed|forbidden|write access", re.I)
WAITS = (0, 2, 4, 8, 16)


def git(*args, cwd=None, check=False, timeout=120):
    r = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()[:300]}")
    return r


def _load():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {"runs": {}}


def _save(d):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(d, indent=1) + "\n")


def today():
    return dt.datetime.now(ET).date().isoformat()


def branch_for(run, day=None):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", run):
        raise ValueError("run name: lowercase letters, digits and '-'")
    return f"claude/{run}-{day or today()}"


def push(ref_spec, cwd=None, waits=WAITS, runner=None):
    """Push with retries on network errors only. Returns (ok, kind, message): kind = ok | auth | network | other."""
    runner = runner or (lambda: git("push", "-q", "origin", ref_spec, cwd=cwd))
    r = None
    for w in waits:
        time.sleep(w)
        r = runner()
        if r.returncode == 0:
            return True, "ok", ""
        err = (r.stderr or r.stdout).strip()
        if AUTH_ERR.search(err) and not NET_ERR.search(err):
            return False, "auth", err[:300]
        if not NET_ERR.search(err):
            return False, "other", err[:300]
    return False, "network", (r.stderr or r.stdout).strip()[:300]


def preflight(run, repos=None):
    """Read + push permission for each repo, without changing anything on GitHub (git push --dry-run)."""
    repos = repos or [ROOT] + [p for p in (ROOT.parent / "vicereplay-site",) if (p / ".git").exists()]
    out = []
    for repo in repos:
        name = Path(repo).name
        r = git("ls-remote", "origin", "refs/heads/main", cwd=repo, timeout=60)
        if r.returncode:
            out.append({"repo": name, "ok": False, "step": "read (ls-remote)", "error": r.stderr.strip()[:200]})
            continue
        r = git("push", "--dry-run", "origin", f"HEAD:refs/heads/{branch_for(run)}", cwd=repo, timeout=60)
        ok = r.returncode == 0
        out.append({"repo": name, "ok": ok, "step": "push (dry run)",
                    "error": "" if ok else (r.stderr or r.stdout).strip()[:200]})
    d = _load()
    d["runs"].setdefault(branch_for(run), {})["preflight"] = {"at": dt.datetime.now(dt.timezone.utc).isoformat(),
                                                             "results": out}
    _save(d)
    return out


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def checkpoint(run, message, step="", cwd=None, pusher=None):
    """Commit all work on the run branch, write its manifest, push (with retries). Never touches main."""
    repo = Path(cwd or ROOT)
    br = branch_for(run)
    cur = git("rev-parse", "--abbrev-ref", "HEAD", cwd=repo).stdout.strip()
    if cur != br:
        exists = git("rev-parse", "-q", "--verify", f"refs/heads/{br}", cwd=repo).returncode == 0
        git("checkout", "-q", *([br] if exists else ["-b", br]), cwd=repo, check=True)
    git("add", "-A", cwd=repo, check=True)
    changed = [l for l in git("diff", "--cached", "--name-only", cwd=repo).stdout.splitlines() if l]
    manifest_rel = Path("content") / "runs" / f"{br.split('/', 1)[1]}.json"
    mpath = repo / manifest_rel
    mpath.parent.mkdir(parents=True, exist_ok=True)
    try:
        man = json.loads(mpath.read_text())
    except (OSError, ValueError):
        man = {"run": run, "branch": br, "checkpoints": [], "files": {}}
    for f in changed:
        p = repo / f
        man["files"][f] = _sha(p) if p.exists() else "deleted"
    man["checkpoints"].append({"at": dt.datetime.now(dt.timezone.utc).isoformat(), "step": step, "message": message,
                               "files": len(changed)})
    mpath.write_text(json.dumps(man, indent=1) + "\n")
    git("add", str(manifest_rel), cwd=repo, check=True)
    if git("diff", "--cached", "--quiet", cwd=repo).returncode:
        git("-c", "user.name=Vice Replay run", "-c", "user.email=noreply@anthropic.com", "commit", "-qm",
            f"{run} run {today()}: {message}" + (f" [{step}]" if step else ""), cwd=repo, check=True)
    ok, kind, err = pusher(br) if pusher else push(f"{br}:refs/heads/{br}", cwd=repo)
    d = _load()
    rec = d["runs"].setdefault(br, {})
    rec.update(last_checkpoint=man["checkpoints"][-1], pushed=ok, push_error=err, push_kind=kind,
               commit=git("rev-parse", "HEAD", cwd=repo).stdout.strip())
    _save(d)
    return {"branch": br, "pushed": ok, "kind": kind, "error": err, "files": len(changed), "manifest": str(manifest_rel)}


def recover(cwd=None):
    """Push local run branches that are ahead of GitHub (an earlier run that couldn't save)."""
    repo = Path(cwd or ROOT)
    git("fetch", "-q", "origin", cwd=repo, timeout=120)
    out = []
    for br in git("for-each-ref", "--format=%(refname:short)", "refs/heads/claude/", cwd=repo).stdout.split():
        remote = git("rev-parse", "-q", "--verify", f"refs/remotes/origin/{br}", cwd=repo).stdout.strip()
        ahead = git("rev-list", "--count", f"{remote}..{br}" if remote else br, cwd=repo).stdout.strip()
        if remote and ahead == "0":
            continue
        if not remote and git("merge-base", "--is-ancestor", br, "origin/main", cwd=repo).returncode == 0:
            continue  # already merged, nothing to save
        ok, kind, err = push(f"{br}:refs/heads/{br}", cwd=repo)
        out.append({"branch": br, "ahead": ahead, "pushed": ok, "kind": kind, "error": err})
    return out


def inbox(cwd=None):
    """Helper run branches on GitHub with work not yet in main (newest first), with their manifests."""
    repo = Path(cwd or ROOT)
    git("fetch", "-q", "--prune", "origin", cwd=repo, timeout=120)
    out = []
    refs = git("for-each-ref", "--sort=-committerdate", "--format=%(refname:short)",
               "refs/remotes/origin/claude/", cwd=repo).stdout.split()
    for ref in refs:
        br = ref.split("/", 1)[1]
        m = re.fullmatch(r"claude/([a-z0-9-]+)-(\d{4}-\d{2}-\d{2})", br)
        if not m or m.group(1) in ("everygen-ledger", "checkpoint-phase3-start"):
            continue
        ahead = int(git("rev-list", "--count", f"origin/main..{ref}", cwd=repo).stdout.strip() or 0)
        if not ahead:
            continue
        man = git("show", f"{ref}:content/runs/{br.split('/', 1)[1]}.json", cwd=repo).stdout
        try:
            man = json.loads(man)
        except ValueError:
            man = {}
        out.append({"branch": br, "commits": ahead, "files": len(man.get("files", {})),
                    "last": (man.get("checkpoints") or [{}])[-1]})
    return out


def merge(branch, cwd=None):
    """Main chat only: merge a helper run branch into main (no force), after checking its manifest hashes."""
    repo = Path(cwd or ROOT)
    git("fetch", "-q", "origin", branch, "main", cwd=repo, check=True)
    man = json.loads(git("show", f"origin/{branch}:content/runs/{branch.split('/', 1)[1]}.json", cwd=repo,
                         check=True).stdout)
    bad = []
    for f, sha in man.get("files", {}).items():
        if sha == "deleted":
            continue
        blob = subprocess.run(["git", "show", f"origin/{branch}:{f}"], cwd=repo, capture_output=True)
        if blob.returncode or (hashlib.sha256(blob.stdout).hexdigest() != sha and not f.startswith("content/runs/")):
            bad.append(f)
    if bad:
        raise RuntimeError(f"manifest hash mismatch, not merging: {bad[:5]}")
    git("merge", "--no-ff", "-q", "-m", f"Merge {branch} (helper run, manifest verified)", f"origin/{branch}",
        cwd=repo, check=True)
    return {"merged": branch, "files": len(man.get("files", {}))}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.runsafe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("run")
    c = sub.add_parser("checkpoint")
    c.add_argument("run")
    c.add_argument("-m", "--message", required=True)
    c.add_argument("--step", default="")
    sub.add_parser("recover")
    sub.add_parser("inbox")
    m = sub.add_parser("merge")
    m.add_argument("branch")
    a = ap.parse_args(argv)
    if a.cmd == "preflight":
        res = preflight(a.run)
        for r in res:
            print(("OK      " if r["ok"] else "BLOCKED ") + f"{r['repo']}: {r['step']}" + (f": {r['error']}" if r["error"] else ""))
        if not all(r["ok"] for r in res):
            print("PREFLIGHT FAILED: work locally, checkpoint anyway (it keeps a local commit + manifest), tell the main "
                  "chat with send_message, and never try to get around the refusal.")
            sys.exit(2)
    elif a.cmd == "checkpoint":
        r = checkpoint(a.run, a.message, a.step)
        print(json.dumps(r))
        if not r["pushed"]:
            print(f"FAILED PUSH ({r['kind']}): {r['error']}\nThe commit and manifest are saved locally on {r['branch']}; "
                  "`recover` pushes them on the next run. Tell the main chat now (send_message) with this block.")
            sys.exit(3)
    elif a.cmd == "recover":
        res = recover()
        print(json.dumps(res, indent=1) if res else "nothing to recover")
        if any(not r["pushed"] for r in res):
            sys.exit(3)
    elif a.cmd == "inbox":
        res = inbox()
        for r in res:
            print(f"{r['branch']}: {r['commits']} commits, {r['files']} files, last: {r['last'].get('message', '')[:80]}")
        if not res:
            print("inbox empty")
    elif a.cmd == "merge":
        print(json.dumps(merge(a.branch)))


if __name__ == "__main__":
    main()
