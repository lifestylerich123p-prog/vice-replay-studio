"""Phase 3 #11-12 (owner Nov 26): leak words are judged by context (precision, not a weaker check), and sensitive
topics carry a labelled claim status (studio/vice/factcheck.py)."""
from studio.vice import factcheck as fc

SRC = ["VGTimes - x: https://vgtimes.com/a", "Complex - y: https://www.complex.com/b"]


def fails(ep):
    return [x for x in fc.check_episode(ep) if x["level"] == "fail"]


def ep_with(text, **kw):
    return {"short": [{"text": text}], "sources": SRC, **kw}


# --- leaks -------------------------------------------------------------------------------------------------------
def test_liquid_leak_is_not_a_game_leak():
    assert fc.classify_leak("Go at night: green ooze leaks through a crack under a staircase.") == "physical"
    assert not fails(ep_with("Go at night: green ooze leaks through a crack under a staircase.", claim_status="community-found"))


def test_water_leak_is_not_a_game_leak():
    for t in ("The roof leaks when it rains in Vice City.", "The boat springs a leak if you hit the reef.",
              "Water is leaking from the pipe in the motel bathroom."):
        assert fc.classify_leak(t) == "physical", t


def test_fictional_dialogue_is_not_a_game_leak():
    assert fc.classify_leak('On the radio, the host says "whoever leaked my number owes me".') == "fiction"
    assert fc.classify_leak('In-game parody ad: "Leak-free diapers for Florida men".') in ("fiction", "physical")


def test_real_game_information_leaks_still_fail():
    for t in ("Leaked footage shows the GTA 6 map.", "A leaker says GTA 6 Online launches in March.",
              "The leak reveals the PC release date."):
        assert fc.classify_leak(t) == "info", t
        assert any("leak" in x["fix"] for x in fails(ep_with(t))), t


def test_unknown_context_fails_closed():
    assert fc.classify_leak("It leaked yesterday.") == "info"


def test_leaks_allowed_only_when_the_owner_marked_the_episode():
    ep = ep_with("According to leaks, the PC version comes in 2027.", leaks_ok=True, claim_status="theory")
    assert not [x for x in fails(ep) if "leak" in x["fix"]]


# --- rumours, official announcements, satire ----------------------------------------------------------------------
def test_unverified_rumor_cannot_be_called_confirmed():
    ep = ep_with("Insiders say the PC version is confirmed for March.")
    assert any("rumor/leak wording next to 'confirmed'" in x["fix"] for x in fails(ep))


def test_confirmed_official_announcement_passes_with_an_official_source():
    ep = ep_with("Rockstar confirmed a patch for 30 fps stutter on its support page.", claim_status="confirmed",
                 sources=["Rockstar Support - patch notes: https://support.rockstargames.com/articles/1",
                          "IGN - patch: https://www.ign.com/x"])
    assert not fails(ep)
    ep["sources"] = SRC  # "confirmed" without an official source
    assert any("official" in x["text"] for x in fails(ep))


def test_satire_is_labelled_fiction_not_fact():
    ep = ep_with('The Weazel News parody says "Florida man finds Bigfoot".', claim_status="fiction")
    assert not fails(ep)
    assert any(x["where"] == "claim_status" for x in fails(ep_with('The Weazel News parody says "Florida man finds Bigfoot".')))


# --- sensitive topics need a claim status ---------------------------------------------------------------------------
def test_bigfoot_needs_a_claim_status_and_two_sites():
    ep = ep_with("Bigfoot is real in GTA 6: here is where players found him.")
    assert any(x["where"] == "claim_status" for x in fails(ep))
    ep["claim_status"] = "community-found"
    assert not fails(ep)
    ep["sources"] = ["A: https://vgtimes.com/a", "B: https://vgtimes.com/b"]  # one site twice
    assert any("different sites" in x["text"] for x in fails(ep))


def test_theory_and_hypothetical_need_their_wording():
    assert any("theory wording" in x["text"] for x in fails(ep_with("The UFO is in the swamp.", claim_status="theory")))
    assert not fails(ep_with("Players think the UFO might be in the swamp.", claim_status="theory"))
    bad = ep_with("A secret mission is confirmed for Lucia.", claim_status="hypothetical")
    assert any("what-if" in x["text"] for x in fails(bad))
    assert not fails(ep_with("What if a secret mission let Lucia fly?", claim_status="hypothetical"))


def test_ai_visuals_must_be_labelled():
    ep = ep_with("Bigfoot is real in GTA 6.", claim_status="community-found")
    ep["short"][0]["media"] = "media/ai/bigfoot.png"
    assert any("AI-generated" in x["text"] for x in fails(ep))
    ep["ai_visuals_labelled"] = True
    assert not fails(ep)


def test_plain_location_guide_needs_no_claim_status():
    assert not fails(ep_with("The shoe store is in Key Lento, by the beach."))


# --- caption check precision (Phase 3, Nov 26: Spanish QA now runs on the Spanish render) --------------------------
def test_caption_check_tolerates_whisper_spelling_but_not_garbles():
    from studio.vice import qc
    script = qc.norm_words("GTA seis escondió tortugas ninja bebé en un desagüe junto a Millport")
    near = qc.norm_words("gta seis escondió tortubas ninja bebé en un desabue junto a Milport")
    garbled = qc.norm_words("que te haces con diotortubas ni en JVB en un desabue junto a mi port")
    assert qc.wer(script, near) <= 0.12
    assert qc.wer(script, garbled) > 0.25
    assert not qc.same_word("mask", "mass") and qc.same_word("tallaloko", "tallaloco")
