"""Per-file source provenance (ported from the owner's starter kit, then extended).

Each registered source records: the local file and its SHA-256, creator, original URL, rights status, proof file
(+ its SHA-256), explicit commercial-use and YouTube flags, owner confirmation, the destinations it may be published
on, attribution and notes. strict_check() fails closed, like the starter:
- owned needs --confirm-owned; permission/licensed need a proof file that still exists and is unchanged;
- campaign needs an owner-approved campaign file and is limited to that campaign's destination (ClipCircuit);
- policy (official Rockstar material) is allowed only where the class registry allows it;
- every source needs explicit commercial + YouTube flags, an unchanged file (hash) and the destination in scope.
Every decision is written to the append-only `rights_audit` table.
"""
import hashlib
import json
from pathlib import Path

from . import db

STATUSES = ("owned", "permission", "licensed", "campaign", "policy", "unknown", "denied")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT NOT NULL, sha256 TEXT NOT NULL, creator TEXT NOT NULL,
  url TEXT NOT NULL, rights_status TEXT NOT NULL, proof_path TEXT NOT NULL DEFAULT '', proof_sha256 TEXT NOT NULL DEFAULT '',
  commercial_allowed INTEGER NOT NULL DEFAULT 0, youtube_allowed INTEGER NOT NULL DEFAULT 0,
  owned_confirmed INTEGER NOT NULL DEFAULT 0, destinations TEXT NOT NULL DEFAULT '[]', campaign TEXT,
  attribution TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rights_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, subject TEXT NOT NULL, destination TEXT, ok INTEGER NOT NULL,
  reasons TEXT NOT NULL, via TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS rights_audit_no_update BEFORE UPDATE ON rights_audit
  BEGIN SELECT RAISE(ABORT, 'rights_audit is append-only'); END;
CREATE TRIGGER IF NOT EXISTS rights_audit_no_delete BEFORE DELETE ON rights_audit
  BEGIN SELECT RAISE(ABORT, 'rights_audit is append-only'); END;
"""


class RightsError(Exception):
    pass


def connect():
    con = db.connect()
    con.executescript(SCHEMA)
    return con


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def audit(con, subject, destination, ok, reasons, via):
    con.execute("INSERT INTO rights_audit (at, subject, destination, ok, reasons, via) VALUES (?,?,?,?,?,?)",
                (db.now(), str(subject), destination, int(ok), json.dumps(reasons), via))
    con.commit()


def add(file_path, creator, url, rights_status, proof_path="", commercial=False, youtube=False, confirm_owned=False,
        destinations=None, campaign=None, attribution="", notes=""):
    if rights_status not in STATUSES:
        raise RightsError(f"rights must be one of {', '.join(STATUSES)}")
    f = Path(file_path).expanduser().resolve()
    if not f.is_file():
        raise RightsError(f"Local media file not found: {f} (URL downloads are not supported)")
    if rights_status == "owned" and not confirm_owned:
        raise RightsError("Own footage requires --confirm-owned.")
    if rights_status in ("permission", "licensed") and not proof_path:
        raise RightsError("Third-party footage requires --proof PATH to the permission/license file.")
    proof, proof_hash = "", ""
    if proof_path:
        pf = Path(proof_path).expanduser().resolve()
        if not pf.is_file():
            raise RightsError(f"Proof file not found: {pf}")
        proof, proof_hash = str(pf), sha256(pf)
    if rights_status == "campaign":
        cf = db.ROOT / "content" / "campaigns" / f"{campaign}.json"
        if not campaign or not cf.is_file():
            raise RightsError("campaign footage needs --campaign <name> matching content/campaigns/<name>.json")
        proof, proof_hash = str(cf), sha256(cf)
        destinations = destinations or ["clipcircuit"]
    con = connect()
    dup = con.execute("SELECT id FROM sources WHERE sha256=?", (sha256(f),)).fetchone()
    if dup:
        raise RightsError(f"This exact file is already registered as source {dup['id']}")
    cur = con.execute(
        "INSERT INTO sources (file_path, sha256, creator, url, rights_status, proof_path, proof_sha256, commercial_allowed,"
        " youtube_allowed, owned_confirmed, destinations, campaign, attribution, notes, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (str(f), sha256(f), creator, url, rights_status, proof, proof_hash, int(commercial), int(youtube),
         int(confirm_owned), json.dumps(destinations or ["vice-replay"]), campaign, attribution, notes, db.now()))
    con.commit()
    sid = cur.lastrowid
    audit(con, f"source:{sid}", None, True, [f"registered as {rights_status}"], "sources.add")
    return sid


def get(con, sid):
    r = con.execute("SELECT * FROM sources WHERE id=?", (sid,)).fetchone()
    if not r:
        raise RightsError(f"No source with ID {sid}")
    return dict(r)


def by_path(con, path):
    p = str(Path(path).expanduser().resolve())
    r = con.execute("SELECT * FROM sources WHERE file_path=?", (p,)).fetchone()
    return dict(r) if r else None


def strict_check(src, destination, ai_voice=False, branding=False, con=None):
    """(ok, reasons) for one registered source and one destination. Fails closed."""
    problems = []
    f = Path(src["file_path"])
    st = src["rights_status"]
    if not f.is_file():
        problems.append(f"source media file missing: {f}")
    elif sha256(f) != src["sha256"]:
        problems.append("source file changed since it was registered (hash mismatch): re-register it")
    if st not in ("owned", "permission", "licensed", "campaign", "policy"):
        problems.append(f"rights status {st!r} is not approved")
    if not src["youtube_allowed"]:
        problems.append("YouTube distribution was not explicitly authorized")
    if not src["commercial_allowed"]:
        problems.append("commercial use was not explicitly authorized")
    if st == "owned" and not src["owned_confirmed"]:
        problems.append("ownership has not been confirmed")
    if st in ("permission", "licensed", "campaign"):
        proof = src["proof_path"]
        if not proof or not Path(proof).is_file():
            problems.append("third-party footage needs its permission/license file stored locally")
        elif sha256(proof) != src["proof_sha256"]:
            problems.append("the permission/license file changed since registration: re-check and re-register")
    if st == "campaign":
        from . import rights
        c = rights.check(f"campaign:{src['campaign']}", destination, ai_voice=ai_voice, branding=branding, log=False,
                         registered=False)
        problems += c["reasons"]
        cf = db.ROOT / "content" / "campaigns" / f"{src['campaign']}.json"
        if cf.is_file() and not json.loads(cf.read_text()).get("owner_approved"):
            problems.append("campaign is not owner-approved")
    if st == "policy":
        from . import rights
        problems += rights.check(src["file_path"], destination, log=False, registered=False)["reasons"]
    if destination not in json.loads(src["destinations"] or "[]"):
        problems.append(f"destination {destination!r} is outside this source's scope {src['destinations']}")
    if con is not None:
        audit(con, f"source:{src['id']}", destination, not problems, problems, "sources.strict_check")
    return not problems, problems
