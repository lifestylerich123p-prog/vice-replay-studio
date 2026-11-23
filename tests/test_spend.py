from studio import spend


def test_upload_commands_follow_the_slots():
    same = {"slug": "x", "item": "short", "en": ["2026-11-26", "9:30 AM"], "es": ["2026-11-26", "9:30 AM"]}
    assert spend.commands(same, True, True) == [["python", "-m", "studio.ship", "episodes/x.json", "--upload", "short",
                                                 "--date", "2026-11-26", "--at", "9:30 AM"]]
    split = {"slug": "y", "item": "short", "en": ["2026-11-24", "11:00 AM"], "es": ["2026-11-25", "11:00 AM"]}
    cmds = spend.commands(split, True, True)
    assert cmds[0][-1] == "--no-es-upload" and cmds[1][2] == "studio.youtube_es" and cmds[1][-1] == "11:00 AM"
    only_es = {"slug": "z", "item": "short", "es_only": True, "es": ["2026-11-23", "3:30 PM"]}
    assert spend.commands(only_es, False, True)[0][2] == "studio.youtube_es"


def test_pending_skips_what_is_already_up_and_sorts_by_slot():
    items = spend.pending()
    firsts = [min(x for x in (it.get("en"), it.get("es")) if x) for it, _, _ in items]
    assert all(ne or ns for _, ne, ns in items)
    assert len(firsts) == len(items)
