import json
import sys
sys.path.append("src")

from scoring import score_candidate
from honeypot import is_honeypot

with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)

results = []
for candidate in candidates:
    honeypot, reasons = is_honeypot(candidate)
    score, features = score_candidate(candidate)
    results.append({
        "name": candidate["profile"]["anonymized_name"],
        "title": candidate["profile"]["current_title"],
        "company": candidate["profile"]["current_company"],
        "score": score,
        "honeypot": honeypot,
    })

# Sort best to worst
results.sort(key=lambda r: -r["score"])

print("RANK | SCORE | NAME | TITLE | COMPANY | HONEYPOT")
for i, r in enumerate(results, start=1):
    print(f"{i:2} | {r['score']:.3f} | {r['name']} | {r['title']} | {r['company']} | {r['honeypot']}")

from reasoning import build_reasoning
top_candidate = candidates[0]
_, top_features = score_candidate(top_candidate)
print("---")
print(build_reasoning(top_candidate, top_features))