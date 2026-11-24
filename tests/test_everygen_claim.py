"""studio/everygen_claim.py: two chats can never both hold (and spend on) the same Everygen job.

Runs against a local bare repo standing in for GitHub, so nothing touches the real remote."""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

MOD = Path(__file__).resolve().parent.parent / "studio" / "everygen_claim.py"
MAIN, SPANISH = "cse_01CJRsWP9GjYTirqgQXefGyG", "cse_01CJRsWQE1kt7hsB4ZMNfXcZ"


def sh(*args, cwd=None):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def chats(tmp_path):
    """A bare 'GitHub' with a main branch and two clones: the main chat and the Spanish chat."""
    origin = tmp_path / "origin.git"
    sh("git", "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    sh("git", "clone", "-q", str(origin), str(seed))
    for k, v in (("user.name", "t"), ("user.email", "t@t")):
        sh("git", "config", k, v, cwd=seed)
    (seed / "README").write_text("x")
    sh("git", "add", "README", cwd=seed)
    sh("git", "commit", "-qm", "seed", cwd=seed)
    sh("git", "push", "-q", "origin", "main", cwd=seed)
    out = {}
    for name in ("main", "es"):
        c = tmp_path / name
        sh("git", "clone", "-q", str(origin), str(c))
        for k, v in (("user.name", name), ("user.email", f"{name}@t")):
            sh("git", "config", k, v, cwd=c)
        out[name] = c
    out["seed"] = seed
    return out


def run(clone, session, *args, stdin=None):
    env = {**os.environ, "EVERYGEN_CLAIM_REPO": str(clone), "CLAUDE_CODE_REMOTE_SESSION_ID": session}
    r = subprocess.run([sys.executable, str(MOD), *args], env=env, capture_output=True, text=True, input=stdin)
    return r.returncode, r.stdout + r.stderr


def hook(clone, session, tool="mcp__Everygen__generate_voiceover_batch"):
    return run(clone, session, "hook", stdin=json.dumps({"tool_name": tool, "tool_input": {}}))[0]


def test_second_chat_is_refused(chats):
    code, out = run(chats["main"], MAIN, "claim", "voice:gta6-x:es", "--credits", "5", "--what", "5 lines")
    assert code == 0, out
    code, out = run(chats["es"], SPANISH, "claim", "voice:gta6-x:es", "--credits", "5", "--what", "5 lines")
    assert code == 1 and "CLAIMED by main chat" in out


def test_race_exactly_one_wins(chats):
    for i in range(4):
        job = f"voice:race-{i}:es"
        with ThreadPoolExecutor(2) as ex:
            a = ex.submit(run, chats["main"], MAIN, "claim", job, "--credits", "5", "--what", "race")
            b = ex.submit(run, chats["es"], SPANISH, "claim", job, "--credits", "5", "--what", "race")
            codes = sorted([a.result()[0], b.result()[0]])
        assert codes == [0, 1], (a.result(), b.result())


def test_existing_voice_on_another_branch_blocks(chats):
    seed = chats["seed"]
    sh("git", "checkout", "-qb", "claude/spanish-launch", cwd=seed)
    d = seed / "media/voice/gta6-bb/es"
    d.mkdir(parents=True)
    (d / "seg1.wav").write_bytes(b"RIFF")
    sh("git", "add", "-A", cwd=seed)
    sh("git", "commit", "-qm", "voice", cwd=seed)
    sh("git", "push", "-q", "origin", "claude/spanish-launch", cwd=seed)
    code, out = run(chats["main"], MAIN, "claim", "voice:gta6-bb:es", "--credits", "5", "--what", "x")
    assert code == 1 and "already exists" in out
    code, out = run(chats["main"], MAIN, "claim", "voice:gta6-bb:es", "--credits", "1", "--what", "x",
                    "--again", "seg3 glitched")
    assert code == 0, out


def test_done_blocks_repeat_and_release_frees(chats):
    assert run(chats["es"], SPANISH, "claim", "image:thumb-a", "--credits", "2", "--what", "thumb")[0] == 0
    assert run(chats["es"], SPANISH, "done", "image:thumb-a", "--credits", "2", "--balance", "82")[0] == 0
    code, out = run(chats["main"], MAIN, "claim", "image:thumb-a", "--credits", "2", "--what", "thumb")
    assert code == 1 and "already DONE by Spanish chat" in out
    assert run(chats["main"], MAIN, "claim", "image:thumb-b", "--credits", "2", "--what", "b")[0] == 0
    code, out = run(chats["es"], SPANISH, "release", "image:thumb-b", "--reason", "not mine")
    assert code == 1 and "claimed by main chat" in out
    assert run(chats["main"], MAIN, "release", "image:thumb-b", "--reason", "script changed")[0] == 0
    assert run(chats["es"], SPANISH, "claim", "image:thumb-b", "--credits", "2", "--what", "b")[0] == 0


def test_hook_needs_a_fresh_claim_from_this_chat(chats):
    assert hook(chats["main"], MAIN) == 2                      # no claim: blocked
    assert hook(chats["main"], MAIN, "mcp__Everygen__download_video") == 0  # free tool: not gated
    assert run(chats["main"], MAIN, "claim", "voice:hk:es", "--credits", "5", "--what", "x")[0] == 0
    assert hook(chats["main"], MAIN) == 0                      # claimed: allowed
    assert hook(chats["main"], SPANISH) == 2                   # another chat's claim file doesn't count
    local = chats["main"] / ".claude" / "everygen-claim.local.json"
    data = json.loads(local.read_text())
    data["jobs"] = {k: "2026-01-01T00:00:00Z" for k in data["jobs"]}
    local.write_text(json.dumps(data))
    assert hook(chats["main"], MAIN) == 2                      # stale: blocked
    assert run(chats["main"], MAIN, "claim", "voice:hk:es", "--credits", "5", "--what", "x")[0] == 0  # own re-claim
    assert run(chats["main"], MAIN, "done", "voice:hk:es", "--credits", "5", "--balance", "79")[0] == 0
    assert hook(chats["main"], MAIN) == 2                      # done: the next spend needs a new claim


def test_list_shows_both_chats(chats):
    run(chats["main"], MAIN, "claim", "voice:l1:es", "--credits", "5", "--what", "one")
    run(chats["es"], SPANISH, "claim", "voice:l2:es", "--credits", "4", "--what", "two")
    code, out = run(chats["main"], MAIN, "list")
    assert code == 0 and "voice:l1:es" in out and "voice:l2:es" in out and "Spanish chat" in out


def test_settings_hook_gates_the_same_tools():
    """The hook's matcher in .claude/settings.json and the module's PAID list must stay identical."""
    import re
    root = MOD.parent.parent
    hook_cfg = json.loads((root / ".claude" / "settings.json").read_text())["hooks"]["PreToolUse"]
    matcher = next(h["matcher"] for h in hook_cfg if "everygen_claim" in h["hooks"][0]["command"])
    src = MOD.read_text()
    paid = "".join(re.findall(r'r"([^"]*)"', src[src.index("PAID = re.compile("):src.index(")$\")") + 5]))
    assert matcher == paid
