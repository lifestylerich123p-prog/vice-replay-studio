"""Owner, Nov 26: "learn from comments" -> studio.comment_insights sorts comments into themes and finds questions."""
from studio.comment_insights import analyse, is_question, themes_of


def test_themes_and_questions():
    assert "performance (FPS, graphics, PS5 Pro)" in themes_of("30fps on a PS5 Pro is a joke")
    assert "where is it / map" in themes_of("Where do I find the shoe store?")
    assert "PC version" in themes_of("waiting for the PC release")
    assert themes_of("¿Dónde está el mapa?") and "where is it / map" in themes_of("¿Dónde está el mapa?")
    assert is_question("Where is the alligator in GTA 6?")
    assert is_question("how do you lose the cops?")
    assert not is_question("This game is amazing")
    assert not is_question("I know where it is")


def test_analyse_weights_by_likes():
    res = analyse([{"text": "where is the UFO?", "likes": 50, "replies": 3},
                   {"text": "30 fps again", "likes": 2, "replies": 0},
                   {"text": "nice", "likes": 0, "replies": 0}])
    assert res["total"] == 3
    assert res["by_likes"]["where is it / map"] == 51
    assert res["questions"][0]["text"] == "where is the UFO?"


def test_spam_is_dropped():
    res = analyse([{"text": "Which one is better? Subscribe to my channel!", "likes": 300, "replies": 5},
                   {"text": "where is the portal?", "likes": 4, "replies": 1}])
    assert res["total"] == 1 and res["questions"][0]["text"] == "where is the portal?"

