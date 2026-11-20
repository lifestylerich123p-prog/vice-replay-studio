"""Command-line interface for Vice Replay's local video workflow."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .core import (
    WorkflowError, initialize, connect, getrow, source_add, candidate_add,
    score_candidate, project_create, render_project, qc_project, package_project,
    strict_rights_check,
)

SCORE_FIELDS = ('curiosity', 'payoff', 'context', 'audio', 'visuals', 'originality')


def parser():
    p = argparse.ArgumentParser(prog='vice', description='Vice Replay: rights-first GTA Shorts production toolkit')
    p.add_argument('--workspace', default='./vice_workspace', help='Local project workspace')
    cmd = p.add_subparsers(dest='command', required=True)
    cmd.add_parser('init', help='Initialize a local workspace without overwriting existing config')
    s = cmd.add_parser('add-source', help='Register a LOCAL video and its rights/permissions')
    s.add_argument('--file', required=True, help='Existing local media file; URL downloads not supported')
    s.add_argument('--creator', required=True)
    s.add_argument('--url', required=True, help='Original source URL or a local recording identifier')
    s.add_argument('--rights', required=True, choices=('owned', 'licensed', 'permission', 'unknown', 'denied'))
    s.add_argument('--proof', default='', help='Local license/permission evidence, required for third-party')
    s.add_argument('--commercial-use', action='store_true', help='Explicitly confirm commercial use rights')
    s.add_argument('--youtube-allowed', action='store_true', help='Explicitly confirm YouTube distribution rights')
    s.add_argument('--confirm-owned', action='store_true', help='Confirm you own the recorded media')
    s.add_argument('--attribution', default='')
    s.add_argument('--notes', default='')
    s = cmd.add_parser('add-candidate', help='Describe and score an authorized source moment (0-10 per criterion)')
    s.add_argument('--source-id', type=int, required=True)
    s.add_argument('--title', required=True)
    s.add_argument('--start', type=float, required=True)
    s.add_argument('--end', type=float, required=True)
    for field in SCORE_FIELDS:
        s.add_argument('--' + field, type=int, required=True)
    cmd.add_parser('rank', help='Rank saved candidate moments; rights-ineligible items marked BLOCKED')
    s = cmd.add_parser('rights', help='Verify current rights for one local source')
    s.add_argument('--source-id', type=int, required=True)
    s = cmd.add_parser('create-project', help='Create a video project from an approved candidate')
    s.add_argument('--candidate-id', type=int, required=True)
    s = cmd.add_parser('add-captions', help='Copy a human-checked SRT into a project')
    s.add_argument('--project-id', type=int, required=True)
    s.add_argument('--srt', required=True)
    s = cmd.add_parser('render', help='Cut and frame a candidate using local FFmpeg')
    s.add_argument('--project-id', type=int, required=True)
    s.add_argument('--layout', choices=('fit', 'fill'), default='fit',
                   help='fit preserves whole frame; fill crops to vertical')
    s.add_argument('--focus-x', type=float, default=0.5)
    s.add_argument('--focus-y', type=float, default=0.5)
    s.add_argument('--width', type=int, default=1080)
    s.add_argument('--height', type=int, default=1920)
    s.add_argument('--fps', type=int, default=30)
    s.add_argument('--burn-captions', action='store_true', help='Requires captions.srt in project dir')
    s.add_argument('--preview', action='store_true', help='Preview export; does not update project state')
    s = cmd.add_parser('qc', help='Check output media characteristics and rights; human approval still mandatory')
    s.add_argument('--project-id', type=int, required=True)
    s = cmd.add_parser('package', help='Create a publishing DRAFT. Never uploads or publishes.')
    s.add_argument('--project-id', type=int, required=True)
    s.add_argument('--description', default='')
    s.add_argument('--tags', default='GTA6,GTA,Shorts')
    cmd.add_parser('status', help='Show projects and permissions')
    return p


def execute(args):
    w = Path(args.workspace).expanduser().resolve()
    if args.command == 'init':
        print(f'Initialized workspace: {w}\nConfiguration: {initialize(w)}')
        return
    with connect(w) as db:
        if args.command == 'add-source':
            id_ = source_add(db, creator=args.creator, url=args.url, file_path=args.file,
                rights_status=args.rights, proof_path=args.proof,
                commercial_allowed=args.commercial_use, youtube_allowed=args.youtube_allowed,
                owned_confirmed=args.confirm_owned, attribution=args.attribution, notes=args.notes)
            print(f'Source ID: {id_}. Registration does not guarantee publishing eligibility; run rights.')
        elif args.command == 'add-candidate':
            scorevals = {f: getattr(args, f) for f in SCORE_FIELDS}
            id_ = candidate_add(db, source_id=args.source_id, title=args.title,
                start=args.start, end=args.end, scores=scorevals)
            print(f'Candidate ID: {id_}, editorial score: {score_candidate(scorevals)}/100')
        elif args.command == 'rank':
            rows = db.execute('''SELECT c.*, s.rights_status FROM candidates c
                        JOIN sources s ON s.id=c.source_id ORDER BY c.id''').fetchall()
            results = []
            for c in rows:
                source = getrow(db, 'sources', c['source_id'])
                allowed, reasons = strict_rights_check(source)
                results.append({'candidate_id': c['id'], 'score': score_candidate(c),
                                'rights_approved': allowed, 'title': c['title'],
                                'rights_issues': reasons})
            print(json.dumps(sorted(results, key=lambda x: (not x['rights_approved'], -x['score'])), indent=2))
        elif args.command == 'rights':
            src = getrow(db, 'sources', args.source_id)
            ok, issues = strict_rights_check(src)
            print(json.dumps({'source_id': args.source_id, 'rights_approved': ok, 'issues': issues}, indent=2))
        elif args.command == 'create-project':
            id_, folder = project_create(db, w, candidate_id=args.candidate_id)
            print(f'Project ID: {id_}\nFolder: {folder}')
        elif args.command == 'add-captions':
            getrow(db, 'projects', args.project_id)
            original = Path(args.srt).expanduser().resolve()
            if not original.is_file() or original.suffix.lower() != '.srt':
                raise WorkflowError('Specify an existing .srt file.')
            dest = w / 'projects' / f'{args.project_id:04d}' / 'captions.srt'
            if original != dest.resolve():
                shutil.copy2(original, dest)
            print(f'Copied subtitles: {dest}. Review text/timing before burning.')
        elif args.command == 'render':
            out = render_project(db, w, project_id=args.project_id, layout=args.layout,
                 width=args.width, height=args.height, fps=args.fps,
                 focus_x=args.focus_x, focus_y=args.focus_y,
                 burn_captions=args.burn_captions, preview=args.preview)
            print(f'Rendered: {out}')
        elif args.command == 'qc':
            print(json.dumps(qc_project(db, w, args.project_id), indent=2))
        elif args.command == 'package':
            print(f'Publish draft (NOT uploaded): {package_project(db, w, project_id=args.project_id, description=args.description, tags=args.tags)}')
        elif args.command == 'status':
            projects = [dict(r) for r in db.execute('SELECT * FROM projects ORDER BY id DESC').fetchall()]
            sources = [dict(r) for r in db.execute('SELECT id,creator,url,rights_status,commercial_allowed,youtube_allowed FROM sources ORDER BY id').fetchall()]
            print(json.dumps({'projects': projects, 'sources': sources}, indent=2))


def main():
    args = parser().parse_args()
    try:
        execute(args)
    except (WorkflowError, OSError, ValueError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
