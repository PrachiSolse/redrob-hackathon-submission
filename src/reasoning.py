def build_reasoning(candidate, features):
    """
    Builds a short, honest explanation using ONLY facts that exist in
    this candidate's own data. No generic phrases, no guessing.
    """
    p = candidate["profile"]
    sig = candidate.get("redrob_signals", {})

    parts = [f"{p['current_title']} with {p['years_of_experience']} yrs experience"]

    if features["skill_match"] >= 0.5:
        parts.append("strong overlap with core retrieval/ranking skills")
    elif features["skill_match"] > 0:
        parts.append("partial overlap with core skills")
    else:
        parts.append("little direct overlap with core skills")

    if features["company_quality"] < 0.5:
        parts.append("career has been services-firm only")

    if features["location_fit"] < 0.5:
        parts.append(f"based in {p['location']}, outside preferred locations")

    notice = sig.get("notice_period_days")
    if notice is not None:
        parts.append(f"{notice}-day notice period")

    response_rate = sig.get("recruiter_response_rate")
    if response_rate is not None:
        parts.append(f"recruiter response rate {response_rate:.2f}")

    return "; ".join(parts) + "."