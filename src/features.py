def skill_match_score(candidate):
    """
    Looks at the candidate's skills list and checks how many of the
    JD's core skill categories they actually have.
    Returns a number between 0 and 1 (higher = better match).
    """
    from jd_requirements import CORE_SKILLS

    # Make a simple set of skill names this candidate has, all lowercase
    skill_names = set()
    for skill in candidate.get("skills", []):
        skill_names.add(skill["name"].lower())

    matched_categories = 0
    for category, keywords in CORE_SKILLS.items():
        for kw in keywords:
            if kw in skill_names:
                matched_categories += 1
                break  # found this category, move to the next one

    return matched_categories / len(CORE_SKILLS)

def company_quality_score(candidate):
    """
    If EVERY company in this candidate's career (current + past) is a
    services-only company, that's a flag the JD cares about.
    Returns 1.0 normally, 0.2 if their whole career is services-only.
    """
    from jd_requirements import SERVICES_ONLY_COMPANIES

    companies = {candidate["profile"]["current_company"].lower()}
    for job in candidate.get("career_history", []):
        companies.add(job["company"].lower())

    if companies.issubset(SERVICES_ONLY_COMPANIES):
        return 0.2
    return 1.0

def experience_fit_score(candidate):
    """How close is this candidate to the JD's preferred 5-9 years band?"""
    from jd_requirements import EXPERIENCE_RANGE
    years = candidate["profile"].get("years_of_experience", 0)
    lo, hi = EXPERIENCE_RANGE
    if lo <= years <= hi:
        return 1.0
    distance = min(abs(years - lo), abs(years - hi))
    return max(1.0 - distance * 0.12, 0.2)


def location_fit_score(candidate):
    """Pune/Noida preferred, India good, outside India + not willing to relocate = weak fit."""
    from jd_requirements import PREFERRED_LOCATIONS
    location = candidate["profile"].get("location", "").lower()
    country = candidate["profile"].get("country", "").lower()
    willing = candidate.get("redrob_signals", {}).get("willing_to_relocate", False)

    if any(p in location for p in PREFERRED_LOCATIONS):
        return 1.0
    if country == "india":
        return 0.7
    return 0.5 if willing else 0.3


def title_sanity_score(candidate):
    """
    3 tiers instead of 2:
    - Clearly unrelated (marketing, HR, etc.) -> heavy penalty
    - Genuinely AI/ranking/search relevant -> full credit
    - Generic software engineering (frontend, .NET, cloud, etc.) -> middle score,
      since they're not a red flag, but also not demonstrating real AI focus
    """
    title = candidate["profile"]["current_title"].lower()

    unrelated = ["marketing", "sales", "hr ", "recruiter", "accountant",
                 "customer support", "graphic designer", "civil engineer",
                 "mechanical engineer", "operations manager"]
    if any(t in title for t in unrelated):
        return 0.1

    relevant = ["machine learning", "ml engineer", "ai engineer",
                "recommendation", "search", "ranking", "nlp",
                "data scientist", "applied scientist"]
    if any(t in title for t in relevant):
        return 1.0

    # Generic software/data roles (frontend, backend, .NET, cloud, devops, QA, etc.)
    return 0.5