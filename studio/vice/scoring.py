"""Clip opportunity score (production priority, NOT a view prediction) + the separate, mandatory rights gate.

Editorial inputs are 0-10 judgments made by the editor (person or Claude) after looking at the moment:
curiosity, payoff, context, audio, visual, contribution. Weights from the brief, total 100.
A candidate whose rights check fails is BLOCKED whatever its score.
"""
from . import rights

WEIGHTS = {"curiosity": 25, "payoff": 25, "context": 15, "audio": 15, "visual": 10, "contribution": 10}
LABELS = {"curiosity": "Curiosity", "payoff": "Entertainment payoff", "context": "Immediate context",
          "audio": "Audio clarity", "visual": "Visual interest", "contribution": "Original editorial contribution"}


def total(scores):
    missing = [k for k in WEIGHTS if k not in scores]
    if missing:
        raise ValueError(f"missing editorial scores: {', '.join(missing)}")
    for k, v in scores.items():
        if k in WEIGHTS and not 0 <= float(v) <= 10:
            raise ValueError(f"{k} must be 0-10, got {v}")
    return int(sum(WEIGHTS[k] * float(scores[k]) / 10 for k in WEIGHTS) + 0.5)  # round half up


def evaluate(candidate, destination, ai_voice=False, branding=False, already_used=False):
    """Score + gate. Returns {"total", "gate", "reasons", "conditions"}; gate is OK or BLOCKED."""
    t = total(candidate["scores"])
    chk = rights.check(candidate.get("rights_source") or candidate.get("source_url") or "", destination,
                       ai_voice=ai_voice, branding=branding)
    reasons = list(chk["reasons"])
    if already_used:
        reasons.append("already used (same footage or same event): reposting gets suppressed and breaks campaign rules")
    return {"total": t, "gate": "OK" if not reasons else "BLOCKED", "reasons": reasons,
            "conditions": chk["conditions"], "rights_record": chk["record"]}
