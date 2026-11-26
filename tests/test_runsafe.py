"""Owner Nov 26 Phase 3 #9: unattended runs save to their own branch with a manifest, retry network errors only,
never retry an auth refusal, and recover unpushed work on the next run (studio/runsafe.py)."""
import json
import subprocess
import types

import pytest

from studio import runsafe as rs


def sh(*a, cwd):
    subprocess.run(list(a), cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repos(tmp_path, monkeypatch):
    remote, work = tmp_path / "remote.git", tmp_path / "work"
    sh("git", "init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp_path)
    sh("git", "clone", "-q", str(remote), str(work), cwd=tmp_path)
    for k, v in (("user.name", "t"), ("user.email", "t@t")):
        sh("git", "config", k, v, cwd=work)
    (work / "a.txt").write_text("a")
    sh("git", "add", "-A", cwd=work)
    sh("git", "commit", "-qm", "init", cwd=work)
    sh("git", "push", "-q", "origin", "main", cwd=work)
    monkeypatch.setattr(rs, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(rs, "today", lambda: "2026-11-27")
    return work


def test_checkpoint_saves_on_its_own_branch_with_manifest(repos):
    (repos / "episodes").mkdir()
    (repos / "episodes" / "x.json").write_text('{"slug": "x"}')
    r = rs.checkpoint("daily", "episode x", step="write", cwd=repos)
    assert r["pushed"] and r["branch"] == "claude/daily-2026-11-27"
    remote_heads = subprocess.run(["git", "ls-remote", "origin"], cwd=repos, capture_output=True, text=True).stdout
    assert "refs/heads/claude/daily-2026-11-27" in remote_heads
    man = json.loads((repos / "content" / "runs" / "daily-2026-11-27.json").read_text())
    assert len(man["files"]["episodes/x.json"]) == 64 and man["checkpoints"][0]["step"] == "write"
    main = subprocess.run(["git", "rev-parse", "origin/main"], cwd=repos, capture_output=True, text=True).stdout
    assert main == subprocess.run(["git", "rev-parse", "main"], cwd=repos, capture_output=True, text=True).stdout  # main untouched


def test_auth_refusal_is_not_retried_and_recover_pushes_later(repos):
    calls = []

    def refused(br):
        calls.append(br)
        return False, "auth", "remote: Permission denied (403)"
    (repos / "b.txt").write_text("b")
    r = rs.checkpoint("daily", "work", cwd=repos, pusher=refused)
    assert not r["pushed"] and r["kind"] == "auth" and len(calls) == 1
    assert json.loads(rs.STATE.read_text())["runs"]["claude/daily-2026-11-27"]["pushed"] is False
    res = rs.recover(cwd=repos)  # next run, GitHub reachable again
    assert res and res[0]["branch"] == "claude/daily-2026-11-27" and res[0]["pushed"]


def test_push_retries_network_errors_only():
    seq = iter([types.SimpleNamespace(returncode=1, stderr="fatal: the remote end hung up unexpectedly", stdout=""),
                types.SimpleNamespace(returncode=0, stderr="", stdout="")])
    assert rs.push("x", waits=(0, 0, 0), runner=lambda: next(seq)) == (True, "ok", "")
    deny = lambda: types.SimpleNamespace(returncode=1, stderr="remote: Write access to repository not granted. 403", stdout="")
    ok, kind, _ = rs.push("x", waits=(0, 0, 0), runner=deny)
    assert not ok and kind == "auth"


def test_inbox_and_verified_merge(repos):
    (repos / "c.txt").write_text("c")
    rs.checkpoint("daily", "c", cwd=repos)
    sh("git", "checkout", "-q", "main", cwd=repos)
    box = rs.inbox(cwd=repos)
    assert box[0]["branch"] == "claude/daily-2026-11-27" and box[0]["files"] >= 1
    assert rs.merge("claude/daily-2026-11-27", cwd=repos)["merged"]
    assert (repos / "c.txt").exists()


def test_preflight_dry_run_changes_nothing(repos):
    res = rs.preflight("daily", repos=[repos])
    assert res[0]["ok"]
    heads = subprocess.run(["git", "ls-remote", "origin"], cwd=repos, capture_output=True, text=True).stdout
    assert "claude/daily" not in heads
