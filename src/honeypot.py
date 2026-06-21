def is_honeypot(candidate):
    """
    Returns (True, reasons) if this profile has facts that don't add up.
    Otherwise returns (False, []).
    """
    reasons = []

    # Check 1: total time in career_history vs stated years_of_experience
    total_months = sum(job.get("duration_months", 0) for job in candidate.get("career_history", []))
    stated_years = candidate["profile"].get("years_of_experience", 0)
    if total_months > 0 and abs((total_months / 12) - stated_years) > 3:
        reasons.append("career history duration doesn't match stated years of experience")

    # Check 2: "expert" at a skill they've used for under 3 months
    for skill in candidate.get("skills", []):
        if skill.get("proficiency") == "expert" and skill.get("duration_months", 999) < 3:
            reasons.append(f"expert in {skill['name']} with under 3 months usage")

    # Check 3: education end year before start year
    for edu in candidate.get("education", []):
        if edu.get("end_year") and edu.get("start_year") and edu["end_year"] < edu["start_year"]:
            reasons.append("education end year before start year")

    return len(reasons) > 0, reasons