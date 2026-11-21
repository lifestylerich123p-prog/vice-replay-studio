"""The gameplay drop zone lister must skip Google Docs (the shot list) and walk subfolders (Nov 21 fix)."""
from studio import gameplay

ROOT_HTML = '''<div class="flip-entry" id="entry-F1"><a href="https://drive.google.com/drive/folders/F1">
<div class="flip-entry-title">1 - Wildest moments</div></a></div>
<div class="flip-entry" id="entry-D1"><a href="https://docs.google.com/document/d/D1/edit">
<div class="flip-entry-title">01 - SHOT LIST: what to record</div></a></div>
<div class="flip-entry" id="entry-P1"><a href="https://drive.google.com/file/d/P1/view?usp=drive_web">
<div class="flip-entry-title">00 - READ ME.png</div></a></div>'''
SUB_HTML = '''<div class="flip-entry" id="entry-V1"><a href="https://drive.google.com/file/d/V1/view?usp=drive_web">
<div class="flip-entry-title">jet ski fail.mp4</div></a></div>'''


class R:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_list_folder_walks_subfolders_and_skips_docs(monkeypatch):
    import requests
    monkeypatch.setattr(requests, "get", lambda url, timeout=60: R(SUB_HTML if "id=F1" in url else ROOT_HTML))
    got = gameplay.list_folder("ROOT")
    assert ("V1", "1 - Wildest moments/jet ski fail.mp4") in got
    assert ("P1", "00 - READ ME.png") in got
    assert all(fid != "D1" for fid, _ in got)
