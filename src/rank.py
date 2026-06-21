import csv
import json
import time

from scoring import score_candidate
from honeypot import is_honeypot
from reasoning import build_reasoning


def load_candidates(path):
    """Reads the big file one line at a time, so it doesn't eat all your RAM."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main():
    start_time = time.time()

    scored_candidates = []
    honeypot_count = 0

    for candidate in load_candidates("../data/candidates.jsonl"):
        honeypot, reasons = is_honeypot(candidate)
        if honeypot:
            honeypot_count += 1
            continue  # skip honeypots entirely, never include them

        score, features = score_candidate(candidate)
        scored_candidates.append((candidate, score, features))

    # Sort best to worst. If scores tie, sort by candidate_id so it's consistent.
    scored_candidates.sort(key=lambda x: (-x[1], x[0]["candidate_id"]))
    top_100 = scored_candidates[:100]

    with open("../submission.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, (candidate, score, features) in enumerate(top_100, start=1):
            reasoning = build_reasoning(candidate, features)
            writer.writerow([candidate["candidate_id"], rank, score, reasoning])

    elapsed = time.time() - start_time
    print(f"Done in {elapsed:.1f} seconds.")
    print(f"Honeypots filtered out: {honeypot_count}")
    print(f"Top 100 saved to submission.csv")


if __name__ == "__main__":
    main()