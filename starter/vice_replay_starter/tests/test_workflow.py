"""Run with python -m unittest discover -s tests -v (stdlib only)."""
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vice_replay.core import (
    initialize, connect, source_add, candidate_add, score_candidate, project_create,
    WorkflowError, strict_rights_check, render_project, qc_project, package_project
)

class Workflows(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        initialize(self.root)
        self.db = connect(self.root)
        self.video = self.root / 'source.mp4'
        self.video.write_bytes(b'placeholder')

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def add_source(self, **overrides):
        vals = dict(creator='me', url='local://recording-1', file_path=self.video,
                    rights_status='owned', commercial_allowed=True,
                    youtube_allowed=True, owned_confirmed=True)
        vals.update(overrides)
        return source_add(self.db, **vals)

    def add_candidate(self, source):
        return candidate_add(self.db, source_id=source, title='Original gaming highlight',
            start=0, end=2,
            scores=dict(curiosity=8, payoff=9, context=7, audio=8, visuals=8, originality=10))

    def test_init_idempotent(self):
        cfg = self.root/'config.json'
        before = cfg.read_text()
        initialize(self.root)
        self.assertEqual(cfg.read_text(), before)

    def test_rights_unknown_blocked(self):
        sid = self.add_source(rights_status='unknown')
        ok, reasons = strict_rights_check(self.db.execute('SELECT * FROM sources WHERE id=?', (sid,)).fetchone())
        self.assertFalse(ok)
        self.assertTrue(any('not approved' in r for r in reasons))
        with self.assertRaises(WorkflowError):
            project_create(self.db, self.root, candidate_id=self.add_candidate(sid))

    def test_third_party_needs_proof(self):
        with self.assertRaises(WorkflowError):
            self.add_source(rights_status='permission', owned_confirmed=False)
        proof = self.root/'license.txt'
        proof.write_text('Example demonstration permission - not real rights')
        sid = self.add_source(rights_status='permission', owned_confirmed=False, proof_path=proof)
        ok, _ = strict_rights_check(self.db.execute('SELECT * FROM sources WHERE id=?', (sid,)).fetchone())
        self.assertTrue(ok)
        proof.unlink()
        ok, _ = strict_rights_check(self.db.execute('SELECT * FROM sources WHERE id=?', (sid,)).fetchone())
        self.assertFalse(ok)

    def test_score(self):
        scores = dict(curiosity=10, payoff=10, context=10, audio=10, visuals=10, originality=10)
        self.assertEqual(score_candidate(scores), 100.0)
        scores['payoff'] = 0
        self.assertEqual(score_candidate(scores), 75.0)

    def test_project_creation(self):
        sid = self.add_source()
        pid, path = project_create(self.db, self.root, candidate_id=self.add_candidate(sid))
        meta = json.loads((path / 'metadata.json').read_text())
        self.assertEqual(meta['project_id'], pid)
        self.assertFalse(meta['automated_publishing'])

    def test_no_commercial_use_blocks(self):
        sid = self.add_source(commercial_allowed=False)
        with self.assertRaises(WorkflowError):
            project_create(self.db, self.root, candidate_id=self.add_candidate(sid))

    def test_invalid_candidate_time(self):
        sid = self.add_source()
        with self.assertRaises(WorkflowError):
            candidate_add(self.db, source_id=sid, title='bad', start=9, end=3,
                scores=dict.fromkeys(('curiosity','payoff','context','audio','visuals','originality'),5))

    @unittest.skipUnless(__import__('shutil').which('ffmpeg') and __import__('shutil').which('ffprobe'), 'Needs FFmpeg')
    def test_actual_video_render_and_package(self):
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
            '-f','lavfi','-i','testsrc2=size=320x180:rate=15',
            '-f','lavfi','-i','sine=frequency=440:sample_rate=44100',
            '-t','3','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p',
            '-c:a','aac',str(self.video)], check=True, capture_output=True)
        sid = self.add_source()
        cid = self.add_candidate(sid)
        pid, d = project_create(self.db, self.root, candidate_id=cid)
        output = render_project(self.db, self.root, project_id=pid,
                                layout='fit', width=180, height=320, fps=15)
        self.assertTrue(output.is_file())
        self.assertGreater(output.stat().st_size, 10000)
        # Rendering twice must preserve the first completed output.
        output2 = render_project(self.db, self.root, project_id=pid,
                                 layout='fit', width=180, height=320, fps=15)
        self.assertNotEqual(output, output2)
        self.assertTrue(output.is_file() and output2.is_file())
        report = qc_project(self.db, self.root, pid)
        self.assertTrue(report['passed_technical_checks'], report)
        draft = package_project(self.db, self.root, project_id=pid,
                                description='Example original clip', tags='GTA,Shorts')
        self.assertFalse(json.loads(draft.read_text())['upload_ready'])

if __name__ == '__main__':
    unittest.main()
