"""SQLite store for the Vice Replay system (database/vice.db): rights, candidates, projects, metrics, research cache.

Design rules:
- Metrics are append-only snapshots (never overwrite an earlier observation).
- Research results are cached with a timestamp and a time-to-live, so the same research isn't run twice.
- Projects keep a status and a list of finished steps, so an interrupted job resumes where it stopped.
- Every paid or quota-using call is logged in `costs`.
"""
import datetime as dt
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "vice.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS rights (
  id TEXT PRIMARY KEY, asset_class TEXT, match TEXT, owner TEXT, permission TEXT, license_url TEXT,
  commercial_use TEXT, creator_restrictions TEXT, music_rights TEXT, campaign TEXT, attribution TEXT,
  expires TEXT, content_id_risk TEXT, platforms_allowed TEXT, destinations_allowed TEXT,
  status TEXT CHECK (status IN ('cleared','conditional','blocked')), notes TEXT, recorded_at TEXT);
CREATE TABLE IF NOT EXISTS candidates (
  id TEXT PRIMARY KEY, creator TEXT, source_url TEXT, published TEXT, ts_start REAL, ts_end REAL,
  description TEXT, views INTEGER, duration REAL, category TEXT, rights_id TEXT, rights_status TEXT,
  restrictions TEXT, used INTEGER DEFAULT 0, used_in TEXT, event_key TEXT, phash TEXT, scores TEXT,
  total INTEGER, gate TEXT, origin TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY, kind TEXT, title TEXT, series TEXT, status TEXT, destination TEXT, rights_ids TEXT,
  files TEXT, steps TEXT, error TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS qc_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT, video TEXT, passed INTEGER, report TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS metric_snapshots (
  video_id TEXT, taken_at TEXT, published TEXT, age_hours REAL, title TEXT, kind TEXT, series TEXT,
  views INTEGER, likes INTEGER, comments INTEGER, engaged_views INTEGER, avg_pct REAL, avg_sec REAL,
  subs_gained INTEGER, shares INTEGER, source TEXT, PRIMARY KEY (video_id, taken_at));
CREATE TABLE IF NOT EXISTS channel_snapshots (
  channel_id TEXT, taken_at TEXT, subs INTEGER, views INTEGER, videos INTEGER, PRIMARY KEY (channel_id, taken_at));
CREATE TABLE IF NOT EXISTS competitor_channels (
  channel_id TEXT, fetched_at TEXT, title TEXT, handle TEXT, subs INTEGER, views INTEGER, videos INTEGER,
  created TEXT, stats TEXT, PRIMARY KEY (channel_id, fetched_at));
CREATE TABLE IF NOT EXISTS competitor_videos (
  video_id TEXT, fetched_at TEXT, channel_id TEXT, title TEXT, published TEXT, seconds INTEGER, views INTEGER,
  likes INTEGER, comments INTEGER, PRIMARY KEY (video_id, fetched_at));
CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, fetched_at TEXT, ttl_hours REAL, value TEXT);
CREATE TABLE IF NOT EXISTS campaigns (id TEXT, checked_at TEXT, data TEXT, PRIMARY KEY (id, checked_at));
CREATE TABLE IF NOT EXISTS payouts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, campaign TEXT, clip TEXT, status TEXT
  CHECK (status IN ('estimated','approved','received')), views INTEGER, amount_usd REAL, recorded_at TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS costs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, provider TEXT, units REAL, unit TEXT, usd REAL, purpose TEXT,
  project TEXT);
CREATE TABLE IF NOT EXISTS ideas (
  id TEXT PRIMARY KEY, day INTEGER, date TEXT, slot TEXT, series TEXT, topic TEXT, data TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS used_footage (
  phash TEXT, source TEXT, video_id TEXT, project TEXT, at TEXT, msig TEXT);
"""


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect(path=None):
    p = Path(path or DB_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    cols = {r[1] for r in con.execute("PRAGMA table_info(used_footage)")}
    if "msig" not in cols:  # migration (Nov 20): motion signature for repost checks
        con.execute("ALTER TABLE used_footage ADD COLUMN msig TEXT")
        con.commit()
    return con


def rows(con, sql, *args):
    return [dict(r) for r in con.execute(sql, args).fetchall()]


# ---------- cache ----------

def cache_get(con, key):
    r = con.execute("SELECT fetched_at, ttl_hours, value FROM cache WHERE key=?", (key,)).fetchone()
    if not r:
        return None
    age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(r["fetched_at"].replace("Z", "+00:00")))
    if age.total_seconds() / 3600 > r["ttl_hours"]:
        return None
    return json.loads(r["value"])


def cache_put(con, key, value, ttl_hours):
    con.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?,?)", (key, now(), ttl_hours, json.dumps(value)))
    con.commit()


# ---------- costs ----------

def log_cost(con, provider, units, unit, purpose, usd=0.0, project=None):
    con.execute("INSERT INTO costs (at, provider, units, unit, usd, purpose, project) VALUES (?,?,?,?,?,?,?)",
                (now(), provider, units, unit, usd, purpose, project))
    con.commit()


# ---------- projects (resumable jobs) ----------

def project_get(con, pid):
    r = con.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    d = dict(r)
    for k in ("rights_ids", "files", "steps"):
        d[k] = json.loads(d[k] or ("[]" if k != "files" else "{}"))
    return d


def project_save(con, p):
    p = dict(p)
    p.setdefault("created_at", now())
    p["updated_at"] = now()
    con.execute("INSERT OR REPLACE INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (p["id"], p.get("kind"), p.get("title"), p.get("series"), p.get("status", "draft"),
                 p.get("destination"), json.dumps(p.get("rights_ids", [])), json.dumps(p.get("files", {})),
                 json.dumps(p.get("steps", [])), p.get("error"), p["created_at"], p["updated_at"]))
    con.commit()
    return p


def step_done(con, p, step, **files):
    """Mark a project step finished (and remember its output files) so a re-run skips it."""
    if step not in p["steps"]:
        p["steps"].append(step)
    p["files"].update({k: str(v) for k, v in files.items()})
    p["error"] = None
    return project_save(con, p)
