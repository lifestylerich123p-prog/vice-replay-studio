"""Standard-library project management, rights controls, ranking and media operations.

Nothing in this package downloads protected videos, claims license rights, spends credits,
or publishes a video. These operations require explicit extension and authorization.
"""

from __future__ import annotations

import json
import sqlite3
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CONFIG = {
    "channel_name": "Vice Replay",
    "channel_id": "UCzk9Wts3WFynOHZQJRWOQIw",
    "channel_id_needs_owner_verification": True,
    "youtube_publish_enabled": False,
    "paid_provider_spend_limit_usd": 0,
    "default_width": 1080,
    "default_height": 1920,
    "default_fps": 30,
    "note": "Confirm channel ownership before any eventual OAuth/publishing integration.",
}

SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator TEXT NOT NULL,
  url TEXT NOT NULL,
  file_path TEXT NOT NULL,
  rights_status TEXT NOT NULL CHECK(rights_status IN ('owned','permission','licensed','unknown','denied')),
  proof_path TEXT NOT NULL DEFAULT '',
  commercial_allowed INTEGER NOT NULL DEFAULT 0,
  youtube_allowed INTEGER NOT NULL DEFAULT 0,
  owned_confirmed INTEGER NOT NULL DEFAULT 0,
  attribution TEXT NOT NULL DEFAULT '',
  notes TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL REFERENCES sources(id),
  title TEXT NOT NULL,
  start_seconds REAL NOT NULL CHECK(start_seconds >= 0),
  end_seconds REAL NOT NULL CHECK(end_seconds > start_seconds),
  curiosity INTEGER NOT NULL CHECK(curiosity BETWEEN 0 AND 10),
  payoff INTEGER NOT NULL CHECK(payoff BETWEEN 0 AND 10),
  context INTEGER NOT NULL CHECK(context BETWEEN 0 AND 10),
  audio INTEGER NOT NULL CHECK(audio BETWEEN 0 AND 10),
  visuals INTEGER NOT NULL CHECK(visuals BETWEEN 0 AND 10),
  originality INTEGER NOT NULL CHECK(originality BETWEEN 0 AND 10),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id INTEGER NOT NULL REFERENCES candidates(id),
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  output_path TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
"""


class WorkflowError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def initialize(workspace: Path):
    workspace.mkdir(parents=True, exist_ok=True)
    for name in ('projects', 'assets', 'reports', 'research', 'rights'):
        (workspace / name).mkdir(exist_ok=True)
    config_path = workspace / 'config.json'
    if not config_path.exists():
        config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + '\n', encoding='utf-8')
    # First initialization creates the DB file; connect() enforces existence later.
    db = sqlite3.connect(workspace / "vice_replay.sqlite3")
    db.executescript(SQL)
    db.close()
    return config_path


def connect(workspace: Path):
    dbfile = workspace / 'vice_replay.sqlite3'
    if not dbfile.is_file():
        raise WorkflowError(f'Workspace not initialized: {workspace}. Run init first.')
    c = sqlite3.connect(dbfile)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON;')
    return c


def getrow(db, tab: str, id_: int):
    if tab not in {'sources', 'candidates', 'projects'}:
        raise WorkflowError('Invalid table')
    r = db.execute(f'SELECT * FROM {tab} WHERE id=?', (id_,)).fetchone()
    if r is None:
        raise WorkflowError(f'No {tab} with ID {id_}')
    return r


def strict_rights_check(source):
    """Return (allowed, reasons), with fail-closed source-asset approval."""
    problems = []
    status = source['rights_status']
    filepath = Path(source['file_path'])
    if not filepath.is_file():
        problems.append(f'Source media file missing: {filepath}')
    if status not in {'owned', 'licensed', 'permission'}:
        problems.append(f'Rights status {status!r} is not approved')
    if not source['youtube_allowed']:
        problems.append('YouTube distribution was not explicitly authorized')
    if not source['commercial_allowed']:
        problems.append('Commercial use was not explicitly authorized')
    if status == 'owned' and not source['owned_confirmed']:
        problems.append('Ownership has not been confirmed')
    if status in {'licensed', 'permission'}:
        proof = source['proof_path']
        if not proof or not Path(proof).is_file():
            problems.append('Third-party footage needs a locally stored license/permission file')
    return not problems, problems


def score_candidate(row):
    # Weighted points: 25 + 25 + 15 + 15 + 10 + 10 = 100.
    weights = {'curiosity': 25, 'payoff': 25, 'context': 15,
               'audio': 15, 'visuals': 10, 'originality': 10}
    return round(sum((int(row[k]) / 10.0) * w for k, w in weights.items()), 2)


def source_add(db, *, creator, url, file_path, rights_status, proof_path='',
               commercial_allowed=False, youtube_allowed=False, owned_confirmed=False,
               attribution='', notes=''):
    file = Path(file_path).expanduser().resolve()
    if not file.is_file():
        raise WorkflowError(f'Local media file not found: {file}')
    if rights_status == 'owned' and not owned_confirmed:
        raise WorkflowError('Own footage requires --confirm-owned.')
    if rights_status in {'permission', 'licensed'} and not proof_path:
        raise WorkflowError('Third-party footage requires --proof PATH to the permission/license file.')
    proof = str(Path(proof_path).expanduser().resolve()) if proof_path else ''
    if proof and not Path(proof).is_file():
        raise WorkflowError(f'Proof file not found: {proof}')
    with db:
        cur = db.execute('''INSERT INTO sources (creator,url,file_path,rights_status,proof_path,
            commercial_allowed,youtube_allowed,owned_confirmed,attribution,notes,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (creator, url, str(file), rights_status, proof, int(commercial_allowed),
             int(youtube_allowed), int(owned_confirmed), attribution, notes, now()))
    return cur.lastrowid


def candidate_add(db, *, source_id, title, start, end, scores):
    getrow(db, 'sources', source_id)
    if not (0 <= start < end):
        raise WorkflowError('Clip start must be >= 0 and end must be > start.')
    if end - start > 180:
        raise WorkflowError('Clips >180 seconds need a different long-form pipeline.')
    for k, v in scores.items():
        if not isinstance(v, int) or not (0 <= v <= 10):
            raise WorkflowError(f'{k} must be an integer from 0 to 10.')
    with db:
        cur = db.execute('''INSERT INTO candidates (source_id,title,start_seconds,end_seconds,
        curiosity,payoff,context,audio,visuals,originality,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
        (source_id, title, start, end, *(scores[k] for k in
         ('curiosity', 'payoff', 'context', 'audio', 'visuals', 'originality')), now()))
    return cur.lastrowid


def project_create(db, workspace, *, candidate_id):
    cand = getrow(db, 'candidates', candidate_id)
    source = getrow(db, 'sources', cand['source_id'])
    allowed, reasons = strict_rights_check(source)
    if not allowed:
        raise WorkflowError('Cannot create project:\n- ' + '\n- '.join(reasons))
    ts = now()
    with db:
        cur = db.execute('''INSERT INTO projects (candidate_id,title,created_at,updated_at)
                            VALUES (?,?,?,?)''', (candidate_id, cand['title'], ts, ts))
    id_ = cur.lastrowid
    p = workspace / 'projects' / f'{id_:04d}'
    p.mkdir(exist_ok=True)
    (p / 'metadata.json').write_text(json.dumps({
       'project_id': id_, 'candidate_id': candidate_id,
       'title': cand['title'], 'attribution': source['attribution'],
       'source_url': source['url'], 'rights_status': source['rights_status'],
       'rights_proof': source['proof_path'], 'start_seconds': cand['start_seconds'],
       'end_seconds': cand['end_seconds'], 'requires_manual_review': True,
       'automated_publishing': False,
    }, indent=2) + '\n', encoding='utf-8')
    (p / 'README.txt').write_text(
       'Project must be reviewed manually before any upload.\n'
       'Put an accurate, timed captions.srt in this folder if desired.\n'
       'Never misrepresent gameplay or source authenticity.\n', encoding='utf-8')
    return id_, p


def probe(media: Path):
    if not shutil.which('ffprobe'):
        raise WorkflowError('ffprobe not found on PATH; install FFmpeg first.')
    cp = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                         '-of', 'json', str(media)], capture_output=True, text=True)
    if cp.returncode:
        raise WorkflowError('ffprobe failed: ' + cp.stderr.strip())
    return json.loads(cp.stdout)


def has_stream(info, stream_type):
    return any(x.get('codec_type') == stream_type for x in info.get('streams', []))


def duration(info):
    try:
        return float(info['format']['duration'])
    except (KeyError, ValueError, TypeError):
        raise WorkflowError('Duration unavailable; unsupported input.')


def render_project(db, workspace, *, project_id, layout='fit', width=1080,
                   height=1920, fps=30, focus_x=0.5, focus_y=0.5,
                   burn_captions=False, preview=False):
    if not shutil.which('ffmpeg'):
        raise WorkflowError('ffmpeg not found on PATH; install FFmpeg first.')
    if width % 2 or height % 2 or width < 2 or height < 2:
        raise WorkflowError('Dimensions must be even positive integers.')
    if not (0 <= focus_x <= 1 and 0 <= focus_y <= 1):
        raise WorkflowError('Focus positions must be between 0 and 1.')
    if not (1 <= fps <= 60):
        raise WorkflowError('FPS must be between 1 and 60.')
    project = getrow(db, 'projects', project_id)
    cand = getrow(db, 'candidates', project['candidate_id'])
    source = getrow(db, 'sources', cand['source_id'])
    allowed, reasons = strict_rights_check(source)
    if not allowed:
        raise WorkflowError('Render blocked:\n- ' + '\n- '.join(reasons))
    pdir = workspace / 'projects' / f'{project_id:04d}'
    info = probe(Path(source['file_path']))
    if not has_stream(info, 'video'):
        raise WorkflowError('Input file contains no video stream.')
    start, end = float(cand['start_seconds']), float(cand['end_seconds'])
    if end > duration(info) + 0.2:
        raise WorkflowError(f'Clip end {end}s exceeds input duration {duration(info):.2f}s.')
    if layout == 'fit':
        vf = (f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
              f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2')
    elif layout == 'fill':
        vf = (f'scale={width}:{height}:force_original_aspect_ratio=increase,'
              f'crop={width}:{height}:(iw-ow)*{focus_x}:(ih-oh)*{focus_y}')
    else:
        raise WorkflowError('Layout must be fit or fill.')
    vf += ',setsar=1,format=yuv420p'
    srt = pdir / 'captions.srt'
    if burn_captions:
        if not srt.is_file():
            raise WorkflowError('No captions.srt in project folder. Use add-captions first.')
        # Use relative filename and run ffmpeg from the project dir to avoid
        # unsafe filtergraph escaping of user-supplied paths.
        vf += ',subtitles=captions.srt'
    stem = 'preview' if preview else 'final'
    out = pdir / f'{stem}.mp4'
    version = 2
    while out.exists():
        out = pdir / f'{stem}_v{version}.mp4'
        version += 1
    arguments = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
        '-ss', str(start), '-i', source['file_path'],
        '-t', str(end - start), '-map', '0:v:0', '-map', '0:a:0?',
        '-vf', vf, '-r', str(fps), '-c:v', 'libx264', '-preset', 'veryfast',
        '-crf', '24' if preview else '20', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart',
        str(out),
    ]
    cp = subprocess.run(arguments, cwd=pdir, capture_output=True, text=True)
    if cp.returncode != 0:
        raise WorkflowError('FFmpeg render failed:\n' + cp.stderr[-4000:])
    if not preview:
        with db:
            db.execute('UPDATE projects SET status=?,output_path=?,updated_at=? WHERE id=?',
                       ('rendered', str(out.resolve()), now(), project_id))
    return out


def qc_project(db, workspace, project_id):
    proj = getrow(db, 'projects', project_id)
    c = getrow(db, 'candidates', proj['candidate_id'])
    src = getrow(db, 'sources', c['source_id'])
    video = Path(proj['output_path']) if proj['output_path'] else None
    errors, warnings = [], []
    ok, reasons = strict_rights_check(src)
    if not ok:
        errors.extend(reasons)
    if not video or not video.is_file():
        errors.append('No final rendered file exists')
    else:
        info = probe(video)
        if not has_stream(info, 'video'):
            errors.append('Missing video stream')
        if not has_stream(info, 'audio'):
            warnings.append('No audio stream: review whether deliberate')
        streams = [s for s in info['streams'] if s['codec_type'] == 'video']
        if streams:
            width, height = int(streams[0]['width']), int(streams[0]['height'])
            if width >= height:
                errors.append(f'Not vertical video: {width}x{height}')
        actual = duration(info)
        target = c['end_seconds'] - c['start_seconds']
        if abs(actual - target) > max(0.75, target * 0.05):
            warnings.append(f'Duration differs from requested {target:.2f}s: got {actual:.2f}s')
        if video.stat().st_size < 10_000:
            warnings.append('Very small output file; inspect playback')
    pdir = workspace / 'projects' / f'{project_id:04d}'
    if not (pdir / 'captions.srt').is_file():
        warnings.append('No sidecar captions.srt; add accurate captions before publishing')
    warnings.append('Automated QC cannot confirm narrative quality, visual continuity, factual accuracy or YouTube monetization eligibility. Human review required.')
    report = {'project_id': project_id, 'passed_technical_checks': not errors,
              'errors': errors, 'warnings': warnings, 'requires_manual_approval': True,
              'checked_at': now()}
    (pdir / 'qc.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def package_project(db, workspace, *, project_id, description, tags):
    p = getrow(db, 'projects', project_id)
    if p['status'] != 'rendered':
        raise WorkflowError('Render project before creating a publication package.')
    report = qc_project(db, workspace, project_id)
    if not report['passed_technical_checks']:
        raise WorkflowError('QC failed; package blocked: ' + str(report['errors']))
    cand = getrow(db, 'candidates', p['candidate_id'])
    src = getrow(db, 'sources', cand['source_id'])
    folder = workspace / 'projects' / f'{project_id:04d}'
    payload = {
        'title': p['title'], 'description': description,
        'source': src['url'], 'credit': src['attribution'],
        'tags': [t.strip() for t in tags.split(',') if t.strip()],
        'file': p['output_path'], 'channel_id': json.loads((workspace/'config.json').read_text())['channel_id'],
        'visibility': 'private', 'upload_ready': False,
        'human_review_required': True,
        'notes': 'Draft only; no YouTube API call is performed.'
    }
    (folder / 'publish_draft.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    return folder / 'publish_draft.json'
