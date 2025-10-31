import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import random

# ------------------------------
# Page setup
# ------------------------------
st.set_page_config(page_title="Prakriti Self-Assessment App v3", page_icon="🧬", layout="wide")

# ------------------------------
# Load data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("prakruti_score.csv", encoding="latin1")
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'Sl.\nNo.': 'SlNo',
        'Dosha dominance': 'Dosha',
        'Question/statement': 'Question',
        'Guna': 'Guna',
        'Is your answer  the following?': 'Expected_Answer',
        'Scores to be allotted if your answer is the one that is mentioned in the previous column': 'Score'
    })
    df['Question'] = df['Question'].fillna("Question missing – please verify source.")
    df['Expected_Answer'] = df['Expected_Answer'].fillna("Yes")
    df['Dosha'] = df['Dosha'].fillna("Kapha")
    df['Score'] = df['Score'].fillna(0)
    return df

df = load_data()

# ------------------------------
# Shuffle once per session
# ------------------------------
if "shuffled_index" not in st.session_state:
    st.session_state.shuffled_index = list(df.index)
    random.shuffle(st.session_state.shuffled_index)

# ------------------------------
# Initialize session state
# ------------------------------
if "scores" not in st.session_state:
    st.session_state.scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# ------------------------------
# Title
# ------------------------------
st.title("🧬 Prakriti Self-Assessment App v3 (Shuffled)")
st.caption("Developed by Dr Prasanna Kulkarni – Atharva AyurTech")
st.write("Answer each question with **Yes/No**, then rate how strongly it applies to you (1 = mild, 5 = very strong).")

# ------------------------------
# Progress + Live Chart
# ------------------------------
max_scores = {"Vata": 960, "Pitta": 600, "Kapha": 1440}
total_q = len(df)
current_q = st.session_state.current_q
progress = current_q / total_q
st.progress(progress, text=f"Progress – {int(progress*100)} % completed")

percent_live = {d: (st.session_state.scores[d] / max_scores[d]) * 100 for d in st.session_state.scores}
fig = go.Figure(go.Bar(
    x=list(percent_live.values()),
    y=list(percent_live.keys()),
    orientation='h',
    text=[f"{v:.1f}%" for v in percent_live.values()],
    textposition="auto",
    marker_color=['#87CEEB', '#F7B267', '#88C999']
))
fig.update_layout(height=250, margin=dict(l=50, r=30, t=20, b=20),
                  xaxis_title="Percentage (%)", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Questionnaire
# ------------------------------
if current_q < total_q:
    row = df.iloc[st.session_state.shuffled_index[current_q]]
    st.subheader(f"Q{current_q + 1}: {row['Question']}")
    answer = st.radio("Choose your answer:", ["Yes", "No"], key=f"q{current_q}")

    rating = 0
    if answer == row["Expected_Answer"]:
        rating = st.slider("How strongly does this apply to you? (1 = mild, 5 = very strong)",
                           1, 5, 3, key=f"r{current_q}")

    if st.button("Next ➡️"):
        if answer == row["Expected_Answer"]:
            weighted = row["Score"] * (rating / 5)
            st.session_state.scores[row["Dosha"]] += weighted
        st.session_state.current_q += 1
        st.rerun()

else:
    # ------------------------------
    # Final Result
    # ------------------------------
    percentages = {d: round((st.session_state.scores[d] / max_scores[d]) * 100, 2)
                   for d in st.session_state.scores}
    st.subheader("✅ Assessment Complete!")
    st.write("### Your Dosha Distribution (%)")
    st.write(percentages)

    dominant = max(percentages, key=percentages.get)
    st.success(f"🌿 Your dominant Prakriti is **{dominant}**")

    # Pie chart
    fig, ax = plt.subplots()
    ax.pie(percentages.values(), labels=percentages.keys(),
           autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    explanations = {
        "Vata": "💨 **Vata Prakriti** – creative, active, variable energy; needs warmth and regular meals.",
        "Pitta": "🔥 **Pitta Prakriti** – sharp intellect; benefits from cooling foods and calmness.",
        "Kapha": "💧 **Kapha Prakriti** – steady and compassionate; needs light diet and activity."
    }
    st.markdown("---")
    st.subheader("🩵 Interpretation")
    st.write(explanations[dominant])

    st.markdown("---")
    st.markdown(
        """
        **Source Credit:** Questionnaire and scoring pattern adapted from *Kishor Patwardhan et al., Institute of Medical Sciences, BHU.*  
        **App Concept & Development:** Dr Prasanna Kulkarni (Atharva AyurTech)
        """,
        unsafe_allow_html=True
    )

    if st.button("🔁 Restart Assessment"):
        st.session_state.scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}
        st.session_state.current_q = 0
        random.shuffle(st.session_state.shuffled_index)
        st.rerun()
