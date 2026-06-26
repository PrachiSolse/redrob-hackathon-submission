import streamlit as st
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from scoring import score_candidate
from honeypot import is_honeypot
from reasoning import build_reasoning

st.set_page_config(page_title="Redrob Ranker", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

.app-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-size: 0.75rem;
    color: #C6FF3D;
    margin-bottom: 0.25rem;
}
.app-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.4rem;
    line-height: 1.1;
    background: linear-gradient(90deg, #8B5CF6, #FF2E88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.app-subtitle { color: #8B8B9E; font-size: 0.95rem; margin-bottom: 1.5rem; }

.podium { display: flex; gap: 12px; margin: 1.5rem 0 2rem 0; }
.podium-card {
    flex: 1; background: #15151F; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1.1rem 1rem;
}
.podium-card.rank-1 {
    border: 1px solid #C6FF3D;
    box-shadow: 0 0 24px rgba(198,255,61,0.15);
    transform: translateY(-8px);
}
.podium-medal { font-size: 1.5rem; }
.podium-name { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.95rem; color: #F5F3FF; margin: 0.3rem 0 0.1rem 0; }
.podium-score { font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; color: #C6FF3D; }
.vibe-track { width: 100%; height: 6px; background: rgba(255,255,255,0.06); border-radius: 99px; margin-top: 8px; overflow: hidden; }
.vibe-fill { height: 100%; background: linear-gradient(90deg, #8B5CF6, #FF2E88); border-radius: 99px; }

.row-card { display: flex; align-items: center; gap: 14px; background: #15151F; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 0.7rem 1rem; margin-bottom: 8px; }
.row-rank { font-family: 'JetBrains Mono', monospace; color: #8B8B9E; width: 28px; }
.row-main { flex: 1; min-width: 0; }
.row-id { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #F5F3FF; }
.row-reason { color: #8B8B9E; font-size: 0.78rem; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-score { font-family: 'JetBrains Mono', monospace; color: #C6FF3D; font-weight: 600; width: 55px; text-align: right; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-eyebrow">REDROB · CANDIDATE INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title">Who actually fits the role</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Drop a candidates JSON file. Scoring, honeypot filtering, and ranking run instantly, on-device, no external calls.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload candidates JSON", type="json", label_visibility="collapsed")

if uploaded_file is not None:
    candidates = json.load(uploaded_file)

    rows = []
    honeypot_count = 0
    for candidate in candidates:
        honeypot, reasons = is_honeypot(candidate)
        if honeypot:
            honeypot_count += 1
            continue
        score, features = score_candidate(candidate)
        reasoning = build_reasoning(candidate, features)
        rows.append({"candidate_id": candidate["candidate_id"], "score": score, "reasoning": reasoning})

    rows.sort(key=lambda r: -r["score"])
    max_score = rows[0]["score"] if rows else 1

    st.caption(f"🚀 {len(candidates)} loaded   ·   🛑 {honeypot_count} honeypots filtered   ·   ✅ {len(rows)} ranked")

    # Podium for top 3
    medals = ["🥇", "🥈", "🥉"]
    top3 = rows[:3]
    podium_html = '<div class="podium">'
    for i, r in enumerate(top3):
        rank_class = "rank-1" if i == 0 else ""
        fill_pct = int((r["score"] / max_score) * 100) if max_score else 0
        podium_html += f"""
        <div class="podium-card {rank_class}">
            <div class="podium-medal">{medals[i]}</div>
            <div class="podium-name">{r['candidate_id']}</div>
            <div class="podium-score">{r['score']:.3f}</div>
            <div class="vibe-track"><div class="vibe-fill" style="width:{fill_pct}%"></div></div>
        </div>"""
    podium_html += "</div>"
    st.markdown(podium_html, unsafe_allow_html=True)

    # Rest of the list as styled rows
    rest_html = ""
    for i, r in enumerate(rows[3:100], start=4):
        fill_pct = int((r["score"] / max_score) * 100) if max_score else 0
        rest_html += f"""
        <div class="row-card">
            <div class="row-rank">#{i}</div>
            <div class="row-main">
                <div class="row-id">{r['candidate_id']}</div>
                <div class="row-reason">{r['reasoning']}</div>
                <div class="vibe-track"><div class="vibe-fill" style="width:{fill_pct}%"></div></div>
            </div>
            <div class="row-score">{r['score']:.3f}</div>
        </div>"""
    st.markdown(rest_html, unsafe_allow_html=True)

    import pandas as pd
    df = pd.DataFrame(rows)
    df.insert(0, "rank", range(1, len(df) + 1))
    st.download_button("⬇ Download ranked CSV", df.to_csv(index=False), "ranked_results.csv")
else:
    st.info("No file uploaded yet — try sample_candidates.json from your data folder.")