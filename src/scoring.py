from datetime import date, datetime
from features import (
    skill_match_score,
    company_quality_score,
    experience_fit_score,
    location_fit_score,
    title_sanity_score,
)

WEIGHTS = {
    "skill_match": 0.35,
    "company_quality": 0.15,
    "experience_fit": 0.20,
    "location_fit": 0.15,
    "title_sanity": 0.15,
}


def behavioral_multiplier(candidate):
    """
    Returns a number around 0.4-1.15 that MULTIPLIES the base score.
    Active, responsive candidates get a boost; inactive/unresponsive
    ones get pulled down -- but never enough to completely override
    a strong skill match.
    """
    sig = candidate.get("redrob_signals", {})

    try:
        last_active = datetime.strptime(sig["last_active_date"], "%Y-%m-%d").date()
        days_inactive = (date.today() - last_active).days
    except (KeyError, ValueError):
        days_inactive = 999

    if days_inactive <= 30:
        recency_factor = 1.0
    elif days_inactive <= 90:
        recency_factor = 0.85
    elif days_inactive <= 180:
        recency_factor = 0.6
    else:
        recency_factor = 0.4

    response_factor = 0.5 + 0.5 * sig.get("recruiter_response_rate", 0.0)
    open_to_work_factor = 1.0 if sig.get("open_to_work_flag") else 0.8

    multiplier = recency_factor * response_factor * open_to_work_factor
    return max(0.4, min(multiplier, 1.15))


def score_candidate(candidate):
    features = {
        "skill_match": skill_match_score(candidate),
        "company_quality": company_quality_score(candidate),
        "experience_fit": experience_fit_score(candidate),
        "location_fit": location_fit_score(candidate),
        "title_sanity": title_sanity_score(candidate),
    }

    base_score = sum(features[k] * WEIGHTS[k] for k in WEIGHTS)
    multiplier = behavioral_multiplier(candidate)
    final_score = round(base_score * multiplier, 4)

    return final_score, features